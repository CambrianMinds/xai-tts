import httpx
from typing import Dict, Any, List, Optional
import os

BASE_URL = "https://api.x.ai/v1/tts"

class XAITTSAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            timeout=60.0
        )

    async def close(self):
        await self.client.aclose()

    async def fetch_voices(self) -> List[Dict[str, Any]]:
        """Fetch available voices, falling back to defaults if API fails."""
        try:
            response = await self.client.get(f"{BASE_URL}/voices")
            response.raise_for_status()
            voices = response.json().get("voices", [])
        except Exception:
            voices = []

        # Ensure defaults exist
        default_voices = [
            {"voice_id": "orion", "name": "Orion", "gender": "male"},
            {"voice_id": "aria", "name": "Aria", "gender": "female"},
            {"voice_id": "eve", "name": "Eve", "gender": "female"},
            {"voice_id": "rex", "name": "Rex", "gender": "male"}
        ]
        
        for default_v in reversed(default_voices):
            if not any(v.get('voice_id') == default_v['voice_id'] for v in voices):
                voices.insert(0, default_v)
                
        return voices

    async def synthesize(self, text: str, voice: str, speed: float, out_fmt: str = "mp3", out_lang: str = "auto") -> bytes:
        payload = {
            "text": text,
            "voice_id": voice,
            "language": out_lang if out_lang != "auto" else None,
            "output_format": {
                "codec": out_fmt,
                "sample_rate": 44100,
                "bit_rate": 192000
            },
            "speed": speed
        }
        # Remove language if auto to let the API detect it (or xAI might require no language field)
        if payload["language"] is None:
            del payload["language"]
        
        response = await self.client.post(BASE_URL, json=payload)
        response.raise_for_status()
        return response.content
