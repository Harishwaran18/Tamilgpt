"""Load, validate and index every curated dataset exactly once."""

from __future__ import annotations

import json
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path
from typing import Any, TypeVar

from tamilgpt.knowledge.models import (
    Career,
    HealthTopic,
    Helpline,
    KnowledgeDoc,
    KnowledgeStats,
    Scheme,
    Service,
)
from tamilgpt.knowledge.retriever import BM25Index, SearchHit
from tamilgpt.sectors import Sector

DATA_DIR = Path(__file__).parent / "data"
DOCS_DIR = DATA_DIR / "docs"

T = TypeVar("T")


class KnowledgeBase:
    """In-memory repository with one BM25 index per record type."""

    def __init__(
        self,
        documents: list[KnowledgeDoc],
        schemes: list[Scheme],
        careers: list[Career],
        health_topics: list[HealthTopic],
        services: list[Service],
        helplines: list[Helpline],
    ) -> None:
        self.documents = documents
        self.schemes = schemes
        self.careers = careers
        self.health_topics = health_topics
        self.services = services
        self.helplines = helplines

        self._scheme_by_id = {scheme.id: scheme for scheme in schemes}
        self._service_by_id = {service.id: service for service in services}
        self._document_index = BM25Index(
            documents,
            lambda doc: doc.search_text(),
            title_getter=lambda doc: f"{doc.title_ta} {doc.title_en}",
        )
        self._scheme_index = BM25Index(
            schemes,
            lambda scheme: scheme.search_text(),
            title_getter=lambda scheme: f"{scheme.name_ta} {scheme.name_en}",
        )
        self._career_index = BM25Index(
            careers,
            lambda career: career.search_text(),
            title_getter=lambda career: f"{career.title_ta} {career.title_en}",
        )
        self._health_index = BM25Index(
            health_topics,
            lambda topic: topic.search_text(),
            title_getter=lambda topic: f"{topic.title_ta} {topic.title_en}",
        )
        self._service_index = BM25Index(
            services,
            lambda service: " ".join(
                [
                    service.name_ta, service.name_en, service.description_ta,
                    service.description_en, " ".join(service.keywords),
                ]
            ),
            title_getter=lambda service: f"{service.name_ta} {service.name_en}",
        )

    def search_documents(
        self, query: str, *, sector: Sector | None = None, top_k: int = 5
    ) -> list[SearchHit[KnowledgeDoc]]:
        filter_fn: Callable[[KnowledgeDoc], bool] | None = None
        if sector is not None and sector is not Sector.GENERAL:
            def filter_fn(doc: KnowledgeDoc) -> bool:
                return doc.sector is sector
        return self._document_index.search(query, top_k=top_k, filter_fn=filter_fn)

    def search_schemes(self, query: str, *, top_k: int = 5) -> list[SearchHit[Scheme]]:
        return self._scheme_index.search(query, top_k=top_k)

    def search_careers(self, query: str, *, top_k: int = 5) -> list[SearchHit[Career]]:
        return self._career_index.search(query, top_k=top_k)

    def search_health(self, query: str, *, top_k: int = 3) -> list[SearchHit[HealthTopic]]:
        return self._health_index.search(query, top_k=top_k)

    def search_services(self, query: str, *, top_k: int = 5) -> list[SearchHit[Service]]:
        return self._service_index.search(query, top_k=top_k)

    def scheme_by_id(self, scheme_id: str) -> Scheme | None:
        return self._scheme_by_id.get(scheme_id)

    def service_by_id(self, service_id: str) -> Service | None:
        return self._service_by_id.get(service_id)

    def helplines_for(self, category: str | None = None) -> list[Helpline]:
        if category is None:
            return list(self.helplines)
        return [line for line in self.helplines if line.category == category]

    def stats(self) -> KnowledgeStats:
        return KnowledgeStats(
            documents=len(self.documents),
            schemes=len(self.schemes),
            careers=len(self.careers),
            health_topics=len(self.health_topics),
            services=len(self.services),
            helplines=len(self.helplines),
            sectors=tuple(sorted({doc.sector.value for doc in self.documents})),
        )


def _read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _load_list(path: Path, factory: Callable[[dict[str, Any]], T]) -> list[T]:
    data = _read_json(path)
    if not isinstance(data, list):
        raise ValueError(f"{path.name} must contain a JSON array")
    records: list[T] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"{path.name}[{index}] must be an object")
        try:
            records.append(factory(item))
        except ValueError as exc:
            raise ValueError(f"{path.name}[{index}]: {exc}") from exc
    return records


def _load_documents() -> list[KnowledgeDoc]:
    documents: list[KnowledgeDoc] = []
    for path in sorted(DOCS_DIR.glob("*.json")):
        documents.extend(_load_list(path, KnowledgeDoc.from_dict))
    ids = [doc.id for doc in documents]
    duplicates = {doc_id for doc_id in ids if ids.count(doc_id) > 1}
    if duplicates:
        raise ValueError(f"duplicate document ids: {sorted(duplicates)}")
    return documents


def build_knowledge_base() -> KnowledgeBase:
    return KnowledgeBase(
        documents=_load_documents(),
        schemes=_load_list(DATA_DIR / "schemes.json", Scheme.from_dict),
        careers=_load_list(DATA_DIR / "careers.json", Career.from_dict),
        health_topics=_load_list(DATA_DIR / "health_topics.json", HealthTopic.from_dict),
        services=_load_list(DATA_DIR / "services.json", Service.from_dict),
        helplines=_load_list(DATA_DIR / "helplines.json", Helpline.from_dict),
    )


@lru_cache(maxsize=1)
def get_knowledge_base() -> KnowledgeBase:
    """Return the process-wide knowledge base singleton."""
    return build_knowledge_base()


def reset_knowledge_base() -> None:
    get_knowledge_base.cache_clear()
