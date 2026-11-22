from __future__ import annotations

from fastapi.testclient import TestClient

from tamilgpt.api.main import create_app
from tamilgpt.core.config import Settings
from tamilgpt.services import nearby as nearby_service


def test_health_and_metadata(client: TestClient) -> None:
    assert client.get("/healthz").json() == {"status": "ok"}
    ready = client.get("/readyz")
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"

    meta = client.get("/api/v1/meta").json()
    assert meta["version"] == "2.0.0"
    assert meta["languages"] == ["ta", "en", "tanglish"]
    assert meta["knowledge"]["schemes"] > 0
    assert len(meta["knowledge"]["sectors"]) == 10


def test_static_ui(client: TestClient) -> None:
    index = client.get("/")
    assert index.status_code == 200
    assert "TamilGPT 2.0" in index.text
    assert "app.js" in index.text
    assert client.get("/static/styles.css").status_code == 200
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/fonts/noto-sans-tamil.woff2").status_code == 200
    assert client.get("/static/favicon.svg").status_code == 200


def test_sectors(client: TestClient) -> None:
    sectors = client.get("/api/v1/sectors?language=en").json()
    assert len(sectors) == 10
    assert {item["id"] for item in sectors} >= {"schemes", "employment", "healthcare"}
    tamil = client.get("/api/v1/sectors?language=ta").json()
    assert tamil[0]["name"] == tamil[0]["name_ta"]


def test_scheme_endpoints(client: TestClient) -> None:
    listing = client.get("/api/v1/schemes?limit=5").json()
    assert len(listing) == 5
    assert {"id", "name", "documents", "source_url"} <= set(listing[0])

    search = client.get("/api/v1/schemes?q=farmer&limit=5").json()
    assert search

    category = client.get("/api/v1/schemes?category=agriculture").json()
    assert all(item["category"] == "agriculture" for item in category)

    scheme = client.get("/api/v1/schemes/pm-kisan").json()
    assert scheme["id"] == "pm-kisan"
    assert client.get("/api/v1/schemes/not-a-scheme").status_code == 404

    matches = client.post(
        "/api/v1/schemes/match",
        json={
            "age": 45,
            "gender": "male",
            "occupation": "farmer",
            "monthly_income": 15000,
            "land_acres": 2,
            "limit": 5,
            "eligible_only": True,
        },
    ).json()
    assert matches
    assert all(item["eligible"] for item in matches)
    assert any(item["id"] == "pm-kisan" for item in matches)


def test_career_endpoints(client: TestClient) -> None:
    careers = client.get("/api/v1/careers?limit=3&language=en").json()
    assert len(careers) == 3
    assert {"id", "title", "salary_min", "salary_max"} <= set(careers[0])
    matches = client.post(
        "/api/v1/careers/match",
        json={"education": "Degree", "interests": ["technology"], "limit": 3},
    ).json()
    assert matches
    assert all("reasons" in item for item in matches)


def test_finance_endpoints(client: TestClient) -> None:
    emi = client.post(
        "/api/v1/finance/emi",
        json={"principal": 500_000, "annual_rate": 10, "months": 60},
    ).json()
    assert 10_000 < emi["monthly_emi"] < 11_000
    assert emi["total_payment"] > emi["principal"]

    affordable = client.post(
        "/api/v1/finance/affordability",
        json={"monthly_income": 40_000, "existing_emi": 0, "annual_rate": 9, "months": 60},
    ).json()
    assert affordable["safe_emi"] > 0
    assert affordable["max_loan"] > 0

    savings = client.post(
        "/api/v1/finance/savings",
        json={"target": 100_000, "months": 12, "annual_return": 6},
    ).json()
    assert savings["monthly_contribution"] > 0

    comparison = client.post(
        "/api/v1/finance/compare-loans",
        json={
            "principal": 500_000,
            "offers": [
                {"name": "Bank A", "annual_rate": 9, "months": 60, "processing_fee": 5000},
                {"name": "Bank B", "annual_rate": 10, "months": 60, "processing_fee": 0},
            ],
        },
    ).json()
    assert len(comparison) == 2
    assert comparison[0]["total_cost"] <= comparison[1]["total_cost"]
    assert "name" in comparison[0]


def test_finance_validation(client: TestClient) -> None:
    assert client.post("/api/v1/finance/emi", json={"principal": 0, "annual_rate": 10, "months": 12}).status_code == 422
    assert client.post("/api/v1/finance/emi", json={"principal": 1000, "annual_rate": 90, "months": 12}).status_code == 422


def test_health_endpoints(client: TestClient) -> None:
    topics = client.get("/api/v1/health/topics?language=en").json()
    assert len(topics) >= 10
    assert {"id", "title", "symptoms", "red_flags"} <= set(topics[0])

    emergency = client.post(
        "/api/v1/health/triage",
        json={"text": "chest pain and breathing difficulty", "language": "en"},
    ).json()
    assert emergency["emergency"] is True
    assert any("108" in note for note in emergency["notes"])

    urgent = client.post(
        "/api/v1/health/triage",
        json={"text": "fever for 4 days", "language": "en"},
    ).json()
    assert urgent["urgent"] is True


def test_helplines(client: TestClient) -> None:
    lines = client.get("/api/v1/helplines?language=en").json()
    numbers = {line["number"] for line in lines}
    assert {"112", "108", "1098", "181"} <= numbers
    emergency = client.get("/api/v1/helplines?category=emergency&language=en").json()
    assert emergency
    assert all(line["category"] == "emergency" for line in emergency)


def test_nearby_uses_real_parser(client: TestClient, monkeypatch) -> None:
    async def fake_fetcher(query: str) -> dict:
        assert "hospital" in query
        return {
            "elements": [
                {
                    "type": "node",
                    "id": 1,
                    "lat": 11.001,
                    "lon": 76.999,
                    "tags": {
                        "name": "Government Hospital",
                        "amenity": "hospital",
                        "phone": "0422-123456",
                        "website": "https://example.org",
                    },
                }
            ]
        }

    nearby_service._CACHE.clear()
    monkeypatch.setattr(nearby_service, "_default_fetcher", fake_fetcher)
    result = client.get("/api/v1/nearby?lat=11.0&lon=77.0&type=hospital&language=en").json()
    assert result["live"] is True
    assert result["places"][0]["name"] == "Government Hospital"
    assert result["places"][0]["phone"] == "0422-123456"
    assert result["service"]["id"] == "hospital"


def test_nearby_validation(client: TestClient) -> None:
    assert client.get("/api/v1/nearby?lat=200&lon=77&type=hospital").status_code == 422
    assert client.get("/api/v1/nearby?lat=11&lon=77&type=zzzz").status_code == 422


def test_chat_endpoint(client: TestClient) -> None:
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "I am a farmer in Coimbatore. Which schemes can I get?",
            "language": "en",
            "profile": {"age": 45, "gender": "male", "occupation": "farmer", "land_acres": 2},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["reply"]
    assert body["language"] == "en"
    assert body["provider"] == "offline"
    assert body["request_id"]
    assert response.headers["X-Request-ID"] == body["request_id"]
    assert body["intent"]["sector"]

    crisis = client.post(
        "/api/v1/chat",
        json={"message": "I want to end my life", "language": "en"},
    ).json()
    assert crisis["crisis"] is True
    assert crisis["disclaimers"]
    assert "14416" in crisis["reply"] or "Tele-MANAS" in crisis["reply"]


def test_chat_validation(client: TestClient) -> None:
    assert client.post("/api/v1/chat", json={"message": ""}).status_code == 422
    assert client.post("/api/v1/chat", json={"message": "x" * 3000}).status_code == 422
    assert client.post("/api/v1/chat", json={"message": "hi", "language": "fr"}).status_code == 422
    bad = client.post("/api/v1/chat", json={"message": "hi", "extra": 1})
    assert bad.status_code == 422
    assert bad.json()["error"]["code"] == "validation_failed"


def test_feedback_and_metrics(client: TestClient) -> None:
    response = client.post(
        "/api/v1/feedback",
        json={"rating": 5, "comment": "very useful", "sector": "schemes", "language": "en"},
    ).json()
    assert response["ok"] is True
    assert response["summary"]["count"] == 1
    assert response["summary"]["average"] == 5.0

    assert client.post("/api/v1/feedback", json={"rating": 9}).status_code == 422

    summary = client.get("/api/v1/feedback/summary").json()
    assert summary["count"] == 1

    metrics = client.get("/api/v1/metrics").json()
    assert metrics["counters"]["http_requests_total"] >= 1


def test_security_headers_and_request_id(client: TestClient) -> None:
    response = client.get("/", headers={"X-Request-ID": "abc-123"})
    assert response.headers["X-Request-ID"] == "abc-123"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" in response.headers

    invalid = client.get("/", headers={"X-Request-ID": "bad id!"})
    assert invalid.headers["X-Request-ID"] != "bad id!"


def test_cors_preflight(client: TestClient) -> None:
    response = client.options(
        "/api/v1/chat",
        headers={
            "Origin": "https://example.org",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "*"


def test_api_key_protection() -> None:
    settings = Settings(api_key="secret-key", rate_limit_per_minute=1000)
    with TestClient(create_app(settings)) as protected:
        assert protected.get("/api/v1/schemes").status_code == 401
        assert protected.get("/api/v1/meta").status_code == 200
        assert protected.get("/healthz").status_code == 200
        ok = protected.get("/api/v1/schemes", headers={"X-API-Key": "secret-key"})
        assert ok.status_code == 200
        bearer = protected.get(
            "/api/v1/schemes", headers={"Authorization": "Bearer secret-key"}
        )
        assert bearer.status_code == 200


def test_rate_limit_and_body_limit() -> None:
    settings = Settings(rate_limit_per_minute=2, max_body_bytes=1000)
    with TestClient(create_app(settings)) as limited:
        assert limited.get("/api/v1/schemes").status_code == 200
        assert limited.get("/api/v1/schemes").status_code == 200
        blocked = limited.get("/api/v1/schemes")
        assert blocked.status_code == 429
        assert blocked.json()["error"]["code"] == "rate_limited"
        assert "Retry-After" in blocked.headers

        large = limited.post("/api/v1/chat", json={"message": "x" * 1500})
        assert large.status_code == 413
