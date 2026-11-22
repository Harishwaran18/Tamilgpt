"""Curated bilingual knowledge base and hybrid retrieval."""

from tamilgpt.knowledge.loader import KnowledgeBase, get_knowledge_base, reset_knowledge_base
from tamilgpt.knowledge.models import Career, HealthTopic, Helpline, KnowledgeDoc, Scheme, Service
from tamilgpt.knowledge.retriever import BM25Index, SearchHit

__all__ = [
    "BM25Index",
    "Career",
    "HealthTopic",
    "Helpline",
    "KnowledgeBase",
    "KnowledgeDoc",
    "Scheme",
    "SearchHit",
    "Service",
    "get_knowledge_base",
    "reset_knowledge_base",
]
