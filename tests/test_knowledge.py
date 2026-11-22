from __future__ import annotations

import pytest

from tamilgpt.knowledge import get_knowledge_base, reset_knowledge_base
from tamilgpt.knowledge.loader import build_knowledge_base
from tamilgpt.knowledge.retriever import BM25Index, SearchHit, index_tokens
from tamilgpt.knowledge.validate import main, validate_knowledge
from tamilgpt.sectors import Sector


def test_knowledge_base_loading(kb) -> None:
    stats = kb.stats()
    assert stats.documents == 50
    assert stats.schemes == 23
    assert stats.careers == 16
    assert stats.health_topics >= 10
    assert stats.services >= 10
    assert stats.helplines >= 10
    assert "schemes" in stats.sectors

    assert kb.scheme_by_id("pm-kisan") is not None
    assert kb.scheme_by_id("missing") is None
    assert kb.service_by_id("hospital") is not None
    assert kb.service_by_id("missing") is None


def test_knowledge_search(kb) -> None:
    documents = kb.search_documents("education loan", sector=Sector.EDUCATION, top_k=3)
    assert documents
    assert all(hit.item.sector is Sector.EDUCATION for hit in documents)

    schemes = kb.search_schemes("farmer crop", top_k=3)
    assert schemes

    careers = kb.search_careers("nurse", top_k=3)
    assert careers

    topics = kb.search_health("fever", top_k=3)
    assert topics
    assert topics[0].item.id in {"fever", "child-fever"}

    services = kb.search_services("hospital", top_k=3)
    assert services
    assert services[0].item.id == "hospital"


def test_helplines_and_cache_reset(kb) -> None:
    emergency = kb.helplines_for("emergency")
    assert emergency
    assert all(line.category == "emergency" for line in emergency)
    assert kb.helplines_for() == kb.helplines

    reset_knowledge_base()
    rebuilt = get_knowledge_base()
    assert rebuilt.stats().documents == 50
    assert rebuilt is not kb


def test_build_knowledge_base() -> None:
    fresh = build_knowledge_base()
    assert fresh.stats().schemes == 23
    assert fresh.search_schemes("pension")


def test_validation() -> None:
    assert validate_knowledge() == []
    assert main() == 0


def test_bm25_index() -> None:
    items = [
        "Tamil education loan for students",
        "Farmer crop loan and agriculture subsidy",
        "Government hospital emergency services",
    ]
    index = BM25Index(items, lambda item: item, title_getter=lambda item: item)
    assert len(index) == 3

    hits = index.search("education loan", top_k=2)
    assert hits
    assert hits[0].item == items[0]
    assert hits[0].score > 0
    assert hits[0].matched_terms
    assert "score" in hits[0].to_dict()

    filtered = index.search("loan", filter_fn=lambda item: "Farmer" in item)
    assert filtered
    assert all("Farmer" in hit.item for hit in filtered)

    assert index.search("loan", min_score=10_000) == []
    assert index.search("") == []
    assert BM25Index([], lambda item: item).search("anything") == []


def test_search_hit_serialisation() -> None:
    hit = SearchHit(item="x", score=1.23456, matched_terms=("x",))
    assert hit.to_dict() == {"score": 1.2346, "matched_terms": ["x"]}


def test_index_tokens_expands_phonetics() -> None:
    tokens = index_tokens("கல்வி கடன்")
    assert tokens
    assert all(len(token) > 1 for token in tokens)


def test_missing_data_directory(monkeypatch) -> None:
    from pathlib import Path

    import tamilgpt.knowledge.loader as loader

    monkeypatch.setattr(loader, "DATA_DIR", Path("/tmp/does-not-exist"))
    with pytest.raises(FileNotFoundError):
        loader.build_knowledge_base()
