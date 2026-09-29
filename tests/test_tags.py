import pytest
from xai_tts.tags import get_all_tags

def test_get_all_tags():
    tags = get_all_tags()
    assert "inline" in tags
    assert "wrap" in tags
    assert "Pauses" in tags["inline"]
    assert "pause" in tags["inline"]["Pauses"]
    assert "Volume & Intensity" in tags["wrap"]
    assert "whisper" in tags["wrap"]["Volume & Intensity"]
