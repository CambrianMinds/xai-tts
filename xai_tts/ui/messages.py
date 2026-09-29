from textual.message import Message
from typing import Dict, Any, List

class APICredentialsUpdated(Message):
    def __init__(self, api_key: str):
        self.api_key = api_key
        super().__init__()

class SynthesisRequested(Message):
    def __init__(self, text: str, is_preview: bool = False):
        self.text = text
        self.is_preview = is_preview
        super().__init__()

class VoiceListUpdated(Message):
    def __init__(self, voices: List[Dict[str, Any]]):
        self.voices = voices
        super().__init__()
