# Repository notes

## Commands

```bash
pip install -e ".[dev]"
ruff check src tests
mypy src/tamilgpt
pytest
pytest --cov=tamilgpt --cov-report=term-missing --cov-fail-under=70
python -m tamilgpt.knowledge.validate
uvicorn tamilgpt.api.main:app --reload
```

## Conventions

- Python 3.11+, `from __future__ import annotations`, line length 100.
- Bilingual records: every user-facing knowledge field has `_ta` and `_en`.
- Safety-critical text (crisis, health red flags, disclaimers) lives in code, not
  only in data files.
- Scheme eligibility and finance must stay deterministic and explainable.
- The offline composer is the contract; the LLM is optional and must fall back
  cleanly.
- API JSON keys are stable and snake_case. Add fields, do not rename silently.
- Tests live in `tests/` and use the real knowledge base via the `kb` fixture.

## Layout

- `src/tamilgpt/api` — FastAPI app and v1 routes.
- `src/tamilgpt/services` — chat routing, schemes, careers, finance, health,
  nearby, safety, profile, feedback, metrics.
- `src/tamilgpt/nlp` — language, normalisation, entities, intent, matching,
  transliteration, BM25 text.
- `src/tamilgpt/knowledge` — JSON datasets, loader, models, retriever, validation.
- `src/tamilgpt/llm` — optional OpenAI-compatible, Gemini and Ollama adapters.

## Current baseline

- 77 tests passing, 91.64% statement + branch coverage.
- Ruff clean, mypy strict clean (57 source files).
- Knowledge base: 50 documents, 23 schemes, 16 careers, 12 health topics,
  14 services, 16 helplines, 10 sectors.
