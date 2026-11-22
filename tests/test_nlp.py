from __future__ import annotations

import pytest

from tamilgpt.nlp.entities import extract_entities
from tamilgpt.nlp.intent import Action, Sector, classify, is_crisis, sector_hints
from tamilgpt.nlp.language import Language, detect_language, reply_language
from tamilgpt.nlp.matching import TermMatcher
from tamilgpt.nlp.normalize import (
    expand_abbreviations,
    normalize_for_match,
    normalize_text,
    truncate,
)
from tamilgpt.nlp.script import count_latin, count_tamil, has_tamil
from tamilgpt.nlp.similarity import fuzzy_contains, jaccard, levenshtein, ratio
from tamilgpt.nlp.tokenize import content_tokens, ngrams, stem, tokenize
from tamilgpt.nlp.transliterate import phonetic_key, romanize, skeleton_key, variants


def test_language_detection() -> None:
    assert detect_language("எனக்கு காய்ச்சல்") is Language.TAMIL
    assert detect_language("hello world") is Language.ENGLISH
    assert detect_language("Enaku 35 vayasu penn") is Language.TANGLISH
    assert detect_language("தமிழ் and english") is Language.MIXED
    assert detect_language("12345") is Language.UNKNOWN
    assert detect_language("") is Language.UNKNOWN

    assert reply_language("en", Language.TAMIL) is Language.ENGLISH
    assert reply_language("ta", Language.ENGLISH) is Language.TAMIL
    assert reply_language(None, Language.ENGLISH) is Language.ENGLISH
    assert reply_language("auto", Language.TANGLISH) is Language.TAMIL


def test_normalisation() -> None:
    assert normalize_text("  hello\u200b  world  ") == "hello world"
    assert normalize_text("‘quoted’") == "'quoted'"  # noqa: RUF001
    assert normalize_text("௧௦") == "10"
    assert normalize_for_match("Hello, World!") == "hello, world"
    assert expand_abbreviations("TN govt scheme") == "tamil nadu government scheme"
    assert expand_abbreviations("50 k income") == "50000 income"
    assert truncate("short", 20) == "short"
    assert truncate("a" * 30, 10) == "a" * 9 + "…"


def test_tokenization() -> None:
    tokens = tokenize("I am a farmer, கோயம்புத்தூர்! 2024")
    assert tokens == ["i", "am", "a", "farmer", "கோயம்புத்தூர்", "2024"]
    assert stem("schemes") == "schem"
    assert content_tokens("I am a farmer in Coimbatore") == ["farmer", "coimbatore"]
    assert ngrams(["a", "b", "c"], 2) == [("a", "b"), ("b", "c")]


def test_transliteration() -> None:
    assert romanize("தமிழ்") == "thamizh"
    assert phonetic_key("தமிழ்") == "tamil"
    assert skeleton_key("தமிழ்") == "tml"
    assert "tamil" in variants("தமிழ்")
    assert phonetic_key("vanakkam") == phonetic_key("vanakam")


def test_similarity() -> None:
    assert levenshtein("kitten", "sitting") == 3
    assert levenshtein("abc", "abc") == 0
    assert levenshtein("abc", "xyz", max_distance=1) == 2
    assert ratio("abc", "abc") == 1.0
    assert jaccard({"a", "b"}, {"b", "c"}) == pytest.approx(1 / 3)
    assert fuzzy_contains("government hospital", "govt hospital") is False
    assert fuzzy_contains("government hospital", "government hospital") is True


def test_script_helpers() -> None:
    assert has_tamil("தமிழ்")
    assert not has_tamil("english")
    assert count_tamil("தமிழ் abc") > 0
    assert count_latin("தமிழ் abc") == 1


def test_intent_classification() -> None:
    schemes = classify("Which schemes can I get?")
    assert schemes.sector is Sector.SCHEMES
    assert schemes.action is Action.ELIGIBILITY

    emi = classify("EMI for 5 lakh loan")
    assert emi.action is Action.CALCULATION

    nearby = classify("Nearby hospital")
    assert nearby.sector is Sector.HEALTHCARE
    assert nearby.action is Action.NEARBY

    apply = classify("How to apply for PM Kisan")
    assert apply.action is Action.APPLY

    documents = classify("Documents for PM Kisan")
    assert documents.action is Action.DOCUMENTS

    small_talk = classify("hello")
    assert small_talk.action is Action.SMALL_TALK

    assert is_crisis("I want to die")
    assert is_crisis("தற்கொலை செய்ய நினைக்கிறேன்")
    crisis = classify("I want to die")
    assert crisis.crisis is True
    assert crisis.action is Action.CRISIS

    assert sector_hints(Sector.SCHEMES).en


def test_entities_english_tamil_tanglish() -> None:
    english = extract_entities(
        "I am 35, a woman, earning ₹18,000 a month, living in Coimbatore with 2 acres."
    )
    assert english.age == 35
    assert english.gender == "female"
    assert english.monthly_income == 18_000
    assert english.district == "Coimbatore"
    assert english.land_acres == 2

    tamil = extract_entities(
        "எனக்கு 40 வயது, பெண், மாத வருமானம் ₹12,000, தையல் தொழில், மதுரை"
    )
    assert tamil.age == 40
    assert tamil.gender == "female"
    assert tamil.monthly_income == 12_000
    assert tamil.occupation == "tailor"
    assert tamil.district == "மதுரை"

    tanglish = extract_entities(
        "Enaku 40 vayasu, vidhavai, varumanam 12000, vivasayam, Salem"
    )
    assert tanglish.age == 40
    assert tanglish.gender == "female"
    assert tanglish.marital_status == "widow"
    assert tanglish.monthly_income == 12_000
    assert tanglish.occupation == "farmer"
    assert tanglish.district == "Salem"


def test_entities_education_and_family() -> None:
    entities = extract_entities("I completed B.Com and have a family of 4, 10th standard")
    assert entities.education == "Degree"
    assert entities.family_size == 4


def test_term_matcher() -> None:
    matcher = TermMatcher()
    matcher.add("scheme", 2.0)
    matcher.add("which scheme", 3.0)
    matcher.add_many(["திட்டம்", "thittam"], 1.5)
    assert len(matcher) == 4

    result = matcher.match("Which scheme can I get?")
    assert result.hit
    assert result.score >= 5.0
    assert "which scheme" in result.matched

    tamil = matcher.match("எந்த திட்டம்")
    assert tamil.hit

    assert not matcher.match("").hit
