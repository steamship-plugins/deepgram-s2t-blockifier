import pytest
from steamship import Steamship


@pytest.fixture
def steamship_client() -> Steamship:
    return Steamship(profile="test")


def config(punctuate: bool) -> dict:
    return {
        "detect_language": True,
        "punctuate": punctuate,
        "profanity_filter": True,
        "diarize": True,
        "smart_format": True,
        "paragraphs": True,
        "summarize": True,
        "detect_topics": True,
        "utterances": True,
    }
