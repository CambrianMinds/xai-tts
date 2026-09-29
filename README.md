# 🎙️ xAI TTS Studio

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Textual](https://img.shields.io/badge/built%20with-Textual-da59dc.svg)](https://textual.textualize.io/)
[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-00d2ff.svg)](https://cambrianminds.github.io/xai-tts/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A modern, terminal-native user interface (TUI) studio for synthesizing expressive audio with the **xAI Text-to-Speech API**. Features dedicated one-click speech tag insertion, dynamic voice discovery, gender filtering, live console logs, and dry-run simulation.

🔗 **Live Documentation & Interactive Playground:** [https://cambrianminds.github.io/xai-tts/](https://cambrianminds.github.io/xai-tts/)

---

## ⚡ Highlights

- **🖥️ 3-Panel Terminal Interface**: Clean, responsive layout built on [Textual](https://textual.textualize.io/) with dark mode support.
- **🏷️ Interactive Speech Tag Palette**:
  - **Inline insertion**: One-click cursor placement for `[pause]`, `[laugh]`, `[sigh]`, `[lip-smack]`, etc.
  - **Selected text wrapping**: Highlight text and click to wrap with `<whisper>`, `<soft>`, `<singing>`, `<emphasis>`, `<slow>`, etc.
- **🔑 Zero-Friction Auth**: Auto-detects `XAI_API_KEY` from system environment variables or the Windows Registry (`HKCU\Environment`).
- **👥 Voice Discovery & Filtering**: Automatically fetches available voices from xAI API (`/v1/tts/voices`) with instant gender filtering (Male / Female / All) and built-in fallbacks (`rex`, `eve`, `aria`, `orion`).
- **🛡️ Dry Run Mode**: Validate formatting, check speed parameters, and simulate requests without spending API credits.
- **🧵 Asynchronous Background Worker**: Synthesis runs in a non-blocking `async` worker via Textual and `httpx`, keeping the UI perfectly responsive.
- **🎛️ Audio Export**: Direct export to high-quality MP3 (44.1 kHz, 192 kbps) with auto-creation of missing destination directories.
- **📁 History & Projects**:
  - Press `h` to browse past synthesizations and restore them.
  - `ctrl+e` / `ctrl+o` to save/load full project state as JSON.

---

## 📐 Layout Overview

```
+----------------------------------------------------------------------------------------------------+
| 🎙️  xAI TTS Studio - General Purpose                                                     12:00:00  |
+--------------------------+-------------------------------------------------+-----------------------+
|  CONFIG & CONTROLS       |  TEXT EDITOR & LOGS                             |  SPEECH TAGS PALETTE  |
|                          |                                                 |                       |
|  API Key: [••••••••••••] |  Text to Synthesize:                            |  Pauses:              |
|                          |  +-------------------------------------------+  |  [[pause]]            |
|  Output: [output.mp3   ] |  | Hello! [pause] This is a <whisper>general  |  |  [[long-pause]]       |
|                          |  | purpose</whisper> TTS studio.             |  |  [[hum-tune]]         |
|  Gender: [ All       v ] |  |                                           |  |                       |
|                          |  +-------------------------------------------+  |  Laughter & Crying:   |
|  Voice:  [ Eve (eve) v ] |                                                 |  [[laugh]] [[chuckle]]|
|                          |  Output Logs:                                   |                       |
|  Speed:  [ 1.0         ] |  +-------------------------------------------+  |  Volume & Intensity:  |
|                          |  | [12:00:01] Loaded API Key from system     |  |  [<whisper>] [<soft>] |
|  [X] Dry Run (Simulate)  |  | [12:00:02] Fetching voices from xAI...    |  |  [<loud>]             |
|                          |  | [12:00:03] Voices ready.                  |  |                       |
|  [ Synthesize Audio ]    |  +-------------------------------------------+  |  ... (18+ tags)       |
|                          |  [🔍 Preview Selected Text]                     |                       |
+--------------------------+-------------------------------------------------+-----------------------+
| q Quit | d Dark Mode | ctrl+s Synthesize | p Pause | h History | ctrl+o Load | ctrl+e Save       |
+----------------------------------------------------------------------------------------------------+
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10 or higher
- An active [xAI API Key](https://console.x.ai/)

### 2. Installation

**One-line installation (Windows PowerShell):**
```powershell
irm https://raw.githubusercontent.com/cambrianminds/xai-tts/main/install.ps1 | iex
```

**Or install manually:**

Clone this repository:
```bash
git clone https://github.com/cambrianminds/xai-tts.git
cd xai-tts
```

Create and activate a virtual environment:
```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Set Your API Key (Optional)

The application will read your API key automatically if exported to your environment:

```bash
# Linux / macOS
export XAI_API_KEY="xai-your-api-key-here"

# Windows (PowerShell)
$env:XAI_API_KEY="xai-your-api-key-here"

# Windows (Permanent User Env Var)
setx XAI_API_KEY "xai-your-api-key-here"
```

*Note: You can also paste or edit your API key directly into the TUI input field anytime.*

### 4. Launch the Studio

```bash
python app.py
```

---

## 🏷️ Speech Tags Reference

xAI's TTS model understands contextual vocal gestures and modulation tags embedded in text:

### 1. Inline Tags
Insert these directly at cursor position to trigger vocal sound effects and pauses:

| Tag | Category | Description | Example |
|---|---|---|---|
| `[pause]` | Pauses | Standard natural conversational pause | `"Wait for it... [pause] Done!"` |
| `[long-pause]` | Pauses | Extended dramatic or structural pause | `"Chapter One. [long-pause] The awakening."` |
| `[hum-tune]` | Pauses | Melodic humming gesture | `"Hmm [hum-tune], that's interesting."` |
| `[laugh]` | Laughter | Audible burst of laughter | `"That makes no sense! [laugh]"` |
| `[chuckle]` | Laughter | Subtle, warm chuckle | `"Oh, I remember that. [chuckle]"` |
| `[giggle]` | Laughter | Light, playful giggle | `"Stop it! [giggle]"` |
| `[cry]` | Crying | Emotional sob or weeping tone | `"I didn't mean to... [cry]"` |
| `[tsk]` | Mouth Sounds | Disapproval or clicking sound | `"Tsk [tsk], always making excuses."` |
| `[tongue-click]`| Mouth Sounds | Distinct alveolar click | `"And just like that, [tongue-click] gone."`|
| `[lip-smack]` | Mouth Sounds | Conversational pre-speech lip smack | `"[lip-smack] Alright, let's get started."` |
| `[breath]` | Breathing | Noticeable audible breath intake | `"Phew! [breath] That was close."` |
| `[inhale]` | Breathing | Sharp intake of air | `"[inhale] I have an announcement."` |
| `[exhale]` | Breathing | Audible release of air | `"Finally finished. [exhale]"` |
| `[sigh]` | Breathing | Weary or relieved sigh | `"[sigh] Another Monday morning."` |

### 2. Wrap Tags
Highlight text in the editor and click the button to wrap phrases in prosody tags:

| Tag | Category | Description | Example |
|---|---|---|---|
| `<whisper>` | Volume | Conspiratorial or quiet whisper | `"Don't let them hear you: <whisper>the code is 4021</whisper>."` |
| `<soft>` | Volume | Gentle, soothing delivery | `"<soft>Close your eyes and breathe deeply.</soft>"` |
| `<loud>` | Volume | Heightened projection and energy | `"<loud>Attention all personnel!</loud>"` |
| `<build-intensity>` | Volume | Dynamic crescendo across the phrase | `"<build-intensity>Three, two, one, liftoff!</build-intensity>"` |
| `<decrease-intensity>` | Volume | Decrescendo trailing off | `"<decrease-intensity>Fading into the distance...</decrease-intensity>"` |
| `<higher-pitch>` | Pitch | Raised vocal register | `"<higher-pitch>Is someone there?</higher-pitch>"` |
| `<lower-pitch>` | Pitch | Deepened, authoritative register | `"<lower-pitch>I am the architect.</lower-pitch>"` |
| `<slow>` | Speed | Deliberate, slower pace | `"<slow>Listen very carefully.</slow>"` |
| `<fast>` | Speed | Rapid, urgent tempo | `"<fast>Quick, get inside before it shuts!</fast>"` |
| `<sing-song>` | Vocal Style | Rhythmic, playful cadence | `"<sing-song>Guess who just arrived?</sing-song>"` |
| `<singing>` | Vocal Style | Melodic, sung delivery | `"<singing>Happy birthday to you</singing>"` |
| `<emphasis>` | Vocal Style | Heavy stress on the phrase | `"<emphasis>Never</emphasis> touch that lever."` |

---

## 🎙️ Default Voices

| Voice ID | Display Name | Gender | Character Profile |
|---|---|---|---|
| `eve` | Eve | Female | Balanced, clear, warm narration |
| `aria` | Aria | Female | Expressive, lively, engaging dialogue |
| `rex` | Rex | Male | Confident, articulate, modern delivery |
| `orion` | Orion | Male | Deep, resonant, cinematic presence |

*Additional custom or newly released voices attached to your xAI organization are fetched automatically when launching with an active API key.*

---

## ⌨️ Keybindings

| Key | Action |
|---|---|
| `q` | Quit application |
| `d` | Toggle dark / light mode |
| `ctrl+s` | Synthesize Audio |
| `p` | Insert [pause] tag at cursor |
| `h` | View Synthesis History |
| `ctrl+o` | Load Project (.json) |
| `ctrl+e` | Save Project (.json) |
| `Tab` / `Shift+Tab` | Navigate between panels and controls |
| `Enter` | Activate selected button or focus input |

---

## 📡 Direct API Reference (cURL)

The TUI generates requests matching the official xAI REST schema:

```bash
curl -X POST https://api.x.ai/v1/tts \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Welcome! [pause] This is synthesized using <whisper>xAI Speech Studio</whisper>.",
    "voice_id": "eve",
    "language": "en",
    "output_format": {
      "codec": "mp3",
      "sample_rate": 44100,
      "bit_rate": 192000
    },
    "speed": 1.0
  }' \
  --output output.mp3
```

---

## 🛠️ Architecture

- **`xai_tts/ui/app.py`**:
  - `XAITTSApp(App)`: Core Textual application class.
  - `compose()`: Declarative UI tree importing `SettingsPanel`, `EditorPanel`, `TagsPanel`.
  - `fetch_voices()`: Async worker fetching voices using `httpx`.
  - `run_tts_task()`: Background HTTP worker running via `@work(exclusive=True)`.
- **`xai_tts/api.py`**: Clean, async `httpx` wrapper for the xAI API.
- **`xai_tts/config.py`**: Manages app state, auto-saving to `~/.xai_tts/config.yaml`, and tracking synthesis history.
- **`xai_tts/tags.py`**: Dictionary of all supported tags and their insertion logic.

---

## 📄 License

Distributed under the [MIT License](LICENSE).

---

## 🤝 Contributing

Contributions, feedback, and speech tag enhancements are welcome! Feel free to open an issue or pull request.
