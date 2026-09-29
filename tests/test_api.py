import pytest
from xai_tts.api import XAITTSAPI

@pytest.mark.asyncio
async def test_fetch_voices_fallback():
    # If we provide an invalid API key, it should fallback
    api = XAITTSAPI(api_key="invalid")
    voices = await api.fetch_voices()
    await api.close()
    
    assert len(voices) >= 4
    voice_ids = [v["voice_id"] for v in voices]
    assert "rex" in voice_ids
    assert "eve" in voice_ids
