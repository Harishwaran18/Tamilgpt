"""Knowledge-base integrity checks.

Run with ``python -m tamilgpt.knowledge.validate``. CI fails if any record is
missing a bilingual field, a source URL, or a valid sector.
"""

from __future__ import annotations

import sys

from tamilgpt.knowledge.loader import build_knowledge_base
from tamilgpt.sectors import SECTORS, Sector


def validate_knowledge() -> list[str]:
    errors: list[str] = []
    try:
        kb = build_knowledge_base()
    except Exception as exc:
        return [f"failed to load knowledge base: {exc}"]

    if len(kb.documents) < 40:
        errors.append(f"expected at least 40 documents, found {len(kb.documents)}")

    covered = {doc.sector for doc in kb.documents}
    required = set(SECTORS) - {Sector.GENERAL}
    missing = required - covered
    if missing:
        errors.append(f"sectors without documents: {sorted(s.value for s in missing)}")

    for doc in kb.documents:
        if not doc.title_ta.strip() or not doc.body_ta.strip():
            errors.append(f"{doc.id}: Tamil title/body is empty")
        if not doc.title_en.strip() or not doc.body_en.strip():
            errors.append(f"{doc.id}: English title/body is empty")
        if doc.source_url and not doc.source_url.startswith("http"):
            errors.append(f"{doc.id}: source_url is not an http(s) URL")

    for scheme in kb.schemes:
        if not scheme.source_url:
            errors.append(f"{scheme.id}: scheme needs a source_url")
        if not scheme.documents:
            errors.append(f"{scheme.id}: scheme needs at least one document")
        if scheme.min_age and scheme.max_age and scheme.min_age > scheme.max_age:
            errors.append(f"{scheme.id}: min_age is greater than max_age")

    for topic in kb.health_topics:
        if not topic.red_flags_ta or not topic.red_flags_en:
            errors.append(f"{topic.id}: health topic needs red flags in both languages")

    for service in kb.services:
        if not service.overpass_tags:
            errors.append(f"{service.id}: service needs at least one OSM tag")

    numbers = [line.number for line in kb.helplines]
    if len(numbers) != len(set(numbers)):
        errors.append("helpline numbers must be unique")

    return errors


def main() -> int:
    errors = validate_knowledge()
    if errors:
        print("Knowledge base validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    kb = build_knowledge_base()
    stats = kb.stats()
    print("Knowledge base OK")
    print(f"  documents : {stats.documents}")
    print(f"  schemes   : {stats.schemes}")
    print(f"  careers   : {stats.careers}")
    print(f"  health    : {stats.health_topics}")
    print(f"  services  : {stats.services}")
    print(f"  helplines : {stats.helplines}")
    print(f"  sectors   : {', '.join(stats.sectors)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
