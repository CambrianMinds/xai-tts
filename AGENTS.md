# AI Agent Guidelines

Please observe the following rules:

## Architecture

- The application uses `textual` for the UI, located in `xai_tts/ui/`. Panels are in `panels.py`, modals in `screens.py`, and the main layout in `app.py`.
- All background tasks and async calls must use `httpx` (in `xai_tts/api.py`). Do not use `requests` or `urllib`.
- Audio playback prefers `pygame` instead of platform-specific OS processes.
- Configuration and history are stored in `~/.xai_tts/` (managed by `xai_tts/config.py`).
- Do not introduce Textual threads (`@work(thread=True)`); use pure async instead (`@work(exclusive=True)`).

## Editing Guidelines

- When adding new speech tags, update both `xai_tts/tags.py` and the test suite in `tests/test_tags.py`.
- Ensure changes are tested with `pytest tests/`.
- Maintain the 3-panel UI design. Do not radically alter the Textual layout composition without explicit user consent.

## Futures
Do not implement the following without explicit direction:
- Full file browser widgets
- Streaming TTS
- Custom voice cloning UI
- Major visual redesign of the GitHub Pages site
- Adding many new speech tags
