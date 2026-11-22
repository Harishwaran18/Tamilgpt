"""Nearby public services using OpenStreetMap's Overpass API.

Overpass needs no key and is free. The service degrades gracefully: if the live
lookup fails, the caller still gets the official directory link and helpline, so
a citizen is never left without a next step.
"""

from __future__ import annotations

import math
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

import httpx

from tamilgpt.core.cache import TTLCache
from tamilgpt.core.errors import ValidationFailed
from tamilgpt.core.logging import get_logger
from tamilgpt.knowledge import KnowledgeBase, Service, get_knowledge_base

logger = get_logger(__name__)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
_CACHE: TTLCache[str, list[Place]] = TTLCache(maxsize=256, ttl_seconds=300)
_Fetcher = Callable[[str], Awaitable[dict[str, Any]]]


@dataclass(slots=True)
class Place:
    name: str
    latitude: float
    longitude: float
    distance_km: float
    kind: str = ""
    address: str | None = None
    phone: str | None = None
    website: str | None = None
    opening_hours: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "distance_km": round(self.distance_km, 2),
            "kind": self.kind,
            "address": self.address,
            "phone": self.phone,
            "website": self.website,
            "opening_hours": self.opening_hours,
        }


@dataclass(slots=True)
class NearbyResult:
    service: Service
    places: list[Place] = field(default_factory=list)
    live: bool = True
    note_ta: str = ""
    note_en: str = ""
    map_url: str | None = None

    def to_dict(self, language: str = "ta") -> dict[str, object]:
        is_ta = language == "ta"
        return {
            "service": {
                "id": self.service.id,
                "type": self.service.type,
                "name": self.service.name_ta if is_ta else self.service.name_en,
                "icon": self.service.icon,
                "description": (
                    self.service.description_ta if is_ta else self.service.description_en
                ),
                "helpline": self.service.helpline,
                "website": self.service.website,
            },
            "places": [place.to_dict() for place in self.places],
            "live": self.live,
            "note": self.note_ta if is_ta else self.note_en,
            "map_url": self.map_url,
        }


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def build_overpass_query(tags: tuple[str, ...], lat: float, lon: float, radius_m: int) -> str:
    clauses = []
    for tag in tags:
        if "=" not in tag:
            continue
        key, value = tag.split("=", 1)
        clauses.append(f'nwr["{key}"="{value}"](around:{radius_m},{lat},{lon});')
    if not clauses:
        raise ValidationFailed("service has no usable OpenStreetMap tags")
    return f"[out:json][timeout:20];({''.join(clauses)});out center 20;"


def parse_overpass(payload: dict[str, Any], lat: float, lon: float) -> list[Place]:
    places: list[Place] = []
    seen: set[tuple[str, float, float]] = set()
    for element in payload.get("elements", []) or []:
        tags = element.get("tags") or {}
        center = element.get("center") or {}
        element_lat = element.get("lat", center.get("lat"))
        element_lon = element.get("lon", center.get("lon"))
        if element_lat is None or element_lon is None:
            continue
        name = (
            tags.get("name:ta")
            or tags.get("name")
            or tags.get("name:en")
            or tags.get("operator")
            or "Unnamed service"
        )
        key = (name, round(float(element_lat), 4), round(float(element_lon), 4))
        if key in seen:
            continue
        seen.add(key)
        address = tags.get("addr:full") or ", ".join(
            part
            for part in (
                tags.get("addr:housenumber"),
                tags.get("addr:street"),
                tags.get("addr:city"),
                tags.get("addr:postcode"),
            )
            if part
        )
        kind = (
            tags.get("amenity")
            or tags.get("healthcare")
            or tags.get("office")
            or tags.get("shop")
            or ""
        )
        places.append(
            Place(
                name=name,
                latitude=float(element_lat),
                longitude=float(element_lon),
                distance_km=haversine_km(lat, lon, float(element_lat), float(element_lon)),
                kind=kind,
                address=address or None,
                phone=tags.get("phone") or tags.get("contact:phone"),
                website=tags.get("website") or tags.get("contact:website"),
                opening_hours=tags.get("opening_hours"),
            )
        )
    places.sort(key=lambda place: place.distance_km)
    return places


async def _default_fetcher(query: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=25.0, headers={"User-Agent": "TamilGPT/2.0"}) as client:
        response = await client.post(OVERPASS_URL, data={"data": query})
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {}


def _resolve_service(service_type: str, kb: KnowledgeBase) -> Service | None:
    service = kb.service_by_id(service_type)
    if service is not None:
        return service
    for candidate in kb.services:
        if candidate.type == service_type:
            return candidate
    hits = kb.search_services(service_type, top_k=1)
    return hits[0].item if hits else None


async def find_nearby(
    lat: float,
    lon: float,
    service_type: str,
    *,
    radius_m: int = 3000,
    kb: KnowledgeBase | None = None,
    fetcher: _Fetcher | None = None,
) -> NearbyResult:
    if not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise ValidationFailed("latitude/longitude out of range")
    if not 100 <= radius_m <= 10_000:
        raise ValidationFailed("radius_m must be between 100 and 10000")

    base = kb or get_knowledge_base()
    service = _resolve_service(service_type, base)
    if service is None:
        raise ValidationFailed(f"unknown service type '{service_type}'")

    cache_key = f"{round(lat, 3)}:{round(lon, 3)}:{service.id}:{radius_m}"
    cached = _CACHE.get(cache_key)
    if cached is not None:
        return NearbyResult(service=service, places=cached, live=True)

    query = build_overpass_query(service.overpass_tags, lat, lon, radius_m)
    map_url = (
        f"https://www.openstreetmap.org/#map=15/{lat}/{lon}"
    )
    try:
        payload = await (fetcher or _default_fetcher)(query)
        places = parse_overpass(payload, lat, lon)
    except (TimeoutError, httpx.HTTPError, ValueError, KeyError) as exc:
        logger.warning("overpass_lookup_failed", extra={"error": str(exc), "service": service.id})
        return NearbyResult(
            service=service,
            places=[],
            live=False,
            note_ta=(
                "நேரடி வரைபடத் தேடல் இப்போது கிடைக்கவில்லை. கீழே உள்ள அதிகாரப்பூர்வ இணையதளம் "
                "அல்லது உதவி எண்ணைப் பயன்படுத்தி அருகிலுள்ள மையத்தைக் கண்டறியுங்கள்."
            ),
            note_en=(
                "Live map lookup is unavailable right now. Use the official website or helpline "
                "below to find the nearest centre."
            ),
            map_url=map_url,
        )

    _CACHE.set(cache_key, places)
    return NearbyResult(
        service=service,
        places=places,
        live=True,
        note_ta=(
            "தூரம் உங்கள் இருப்பிடத்திலிருந்து நேர் கோட்டில் கணக்கிடப்பட்டது. "
            "செல்லும் முன் தொலைபேசி எண்ணை உறுதிப்படுத்துங்கள்."
        ),
        note_en=(
            "Distances are straight-line from your location. Confirm the phone number "
            "before travelling."
        ),
        map_url=map_url,
    )
