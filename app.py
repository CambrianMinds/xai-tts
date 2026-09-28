import os
import sys
import contextlib
import io
import requests

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Button, Select, Input, Checkbox, Log, Label, TextArea
from textual import work

class XAITTSApp(App):
    CSS = """
    Screen {
        layout: horizontal;
    }
    #left-panel {
        width: 25%;
        height: 100%;
        border-right: solid $primary;
        padding: 1;
    }
    #center-panel {
        width: 55%;
        height: 100%;
        padding: 1;
    }
    #right-panel {
        width: 20%;
        height: 100%;
        border-left: solid $primary;
        padding: 1;
    }
    .field {
        margin-bottom: 1;
    }
    #text-editor {
        height: 1fr;
        margin-bottom: 1;
    }
    Log {
        border: solid gray;
        height: 10;
    }
    .tag-category {
        margin-top: 1;
        text-style: bold;
        color: yellow;
    }
    .tag-btn {
        width: 100%;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode")
    ]

    INLINE_TAGS = {
        "Pauses": ["pause", "long-pause", "hum-tune"],
        "Laughter & Crying": ["laugh", "chuckle", "giggle", "cry"],
        "Mouth Sounds": ["tsk", "tongue-click", "lip-smack"],
        "Breathing": ["breath", "inhale", "exhale", "sigh"]
    }
    
    WRAP_TAGS = {
        "Volume & Intensity": ["soft", "whisper", "loud", "build-intensity", "decrease-intensity"],
        "Pitch & Speed": ["higher-pitch", "lower-pitch", "slow", "fast"],
        "Vocal Style": ["sing-song", "singing", "emphasis"]
    }

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Horizontal():
            # Left Panel: Settings
            with Vertical(id="left-panel"):
                yield Label("API Key", classes="field")
                self.api_input = Input(placeholder="xAI API Key", password=True, classes="field")
                yield self.api_input
                
                yield Label("Output File Path", classes="field")
                self.output_input = Input(value="output.mp3", classes="field")
                yield self.output_input
                
                yield Label("Voice Gender Filter", classes="field")
                self.gender_filter = Select(
                    [("All", "all"), ("Male", "male"), ("Female", "female")],
                    value="all",
                    classes="field"
                )
                yield self.gender_filter
                
                yield Label("Voice ID", classes="field")
                self.voice_select = Select([], prompt="Loading voices...", classes="field")
                self.voice_select.disabled = True
                yield self.voice_select
                
                yield Label("Format & Language", classes="field")
                with Horizontal():
                    self.format_select = Select([("MP3", "mp3"), ("WAV", "wav"), ("FLAC", "flac")], value="mp3", classes="field")
                    self.lang_select = Select([("English", "en"), ("Spanish", "es"), ("French", "fr")], value="en", classes="field")
                    yield self.format_select
                    yield self.lang_select

                yield Label("Speed Multiplier", classes="field")
                self.speed_input = Input(value="1.0", placeholder="1.0", classes="field")
                yield self.speed_input
                
                self.dry_run_checkbox = Checkbox("Dry Run (Simulate API)", value=True, classes="field")
                yield self.dry_run_checkbox
                
                self.play_checkbox = Checkbox("Auto-play Output", value=True, classes="field")
                yield self.play_checkbox
                
                self.synth_button = Button("Synthesize Audio", variant="success", id="btn-synthesize")
                yield self.synth_button

            # Center Panel: Text and Logs
            with Vertical(id="center-panel"):
                yield Label("Text to Synthesize:")
                self.text_editor = TextArea("Hello! [pause] This is a <whisper>general purpose</whisper> TTS studio.", id="text-editor")
                yield self.text_editor
                
                self.char_count = Label("Characters: 73", id="char-count")
                yield self.char_count
                
                yield Label("Output Logs:")
                self.log_widget = Log(id="log")
                yield self.log_widget

            # Right Panel: Speech Tags (Dedicated Auto-insert panel)
            with VerticalScroll(id="right-panel"):
                yield Label("Tag Library")
                yield Label("Highlight text to wrap, or click to insert at cursor.", classes="field")
                
                for category, tags in self.INLINE_TAGS.items():
                    yield Label(category, classes="tag-category")
                    for tag in tags:
                        yield Button(f"\\[{tag}\\]", id=f"tag-inline-{tag}", classes="tag-btn")
                        
                for category, tags in self.WRAP_TAGS.items():
                    yield Label(category, classes="tag-category")
                    for tag in tags:
                        yield Button(f"<{tag}>", id=f"tag-wrap-{tag}", classes="tag-btn")

        yield Footer()

    def on_mount(self) -> None:
        self.title = "xAI TTS Studio - General Purpose"
        self.log_widget.write_line("Welcome to the standalone xAI TTS Studio.")
        
        # Try to load API key from environment or Windows Registry
        api_key = os.environ.get("XAI_API_KEY")
        if not api_key and sys.platform == "win32":
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as env_key:
                    val, _ = winreg.QueryValueEx(env_key, "XAI_API_KEY")
                    if val:
                        api_key = val
            except Exception:
                pass
                
        if api_key:
            self.api_input.value = api_key
            self.log_widget.write_line("Loaded API Key from system environment.")
            
        self.fetch_voices(api_key)

    @work(thread=True)
    def fetch_voices(self, api_key: str) -> None:
        if not api_key:
            self.app.call_from_thread(self.log_widget.write_line, "No API key found. Using fallback voices.")
            self.app.call_from_thread(self.fallback_voices)
            return
            
        try:
            self.app.call_from_thread(self.log_widget.write_line, "Fetching voices from xAI API...")
            response = requests.get(
                "https://api.x.ai/v1/tts/voices",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5
            )
            response.raise_for_status()
            voices = response.json().get("voices", [])
            
            for default_v in [
                {"voice_id": "orion", "name": "Orion", "gender": "male"},
                {"voice_id": "aria", "name": "Aria", "gender": "female"},
                {"voice_id": "eve", "name": "Eve", "gender": "female"},
                {"voice_id": "rex", "name": "Rex", "gender": "male"}
            ]:
                if not any(v.get('voice_id') == default_v['voice_id'] for v in voices):
                    voices.insert(0, default_v)
                
            self.app.call_from_thread(self.update_voice_select, voices)
        except Exception as e:
            self.app.call_from_thread(self.log_widget.write_line, f"Failed to fetch voices: {e}")
            self.app.call_from_thread(self.fallback_voices)

    def fallback_voices(self) -> None:
        voices = [
            {"voice_id": "rex", "name": "Rex", "gender": "male"},
            {"voice_id": "eve", "name": "Eve", "gender": "female"},
            {"voice_id": "aria", "name": "Aria", "gender": "female"},
            {"voice_id": "orion", "name": "Orion", "gender": "male"}
        ]
        self.update_voice_select(voices)

    def update_voice_select(self, voices_data: list) -> None:
        self.all_voices_data = voices_data
        self.apply_voice_filter()

    def apply_voice_filter(self) -> None:
        if not hasattr(self, "all_voices_data"):
            return
            
        filter_val = self.gender_filter.value
        
        # Known gender mappings for xAI default voices
        known_male = {"rex", "orion"}
        known_female = {"eve", "aria"}
        
        filtered_options = []
        for voice in self.all_voices_data:
            vid = voice.get("voice_id", "").lower()
            
            gender = voice.get("gender", voice.get("labels", {}).get("gender", "")).lower()
            
            is_male = gender == "male" or vid in known_male
            is_female = gender == "female" or vid in known_female
            
            if filter_val == "male" and not is_male:
                continue
            if filter_val == "female" and not is_female:
                continue
                
            name = voice.get("name", voice.get("voice_id"))
            filtered_options.append((f"{name} ({voice.get('voice_id')})", voice.get("voice_id")))
            
        self.voice_select.set_options(filtered_options)
        self.voice_select.disabled = False
        
        current_val = self.voice_select.value
        if current_val and any(val == current_val for _, val in filtered_options):
            pass # Keep it
        elif any(val == "rex" for _, val in filtered_options):
            self.voice_select.value = "rex"
        elif any(val == "eve" for _, val in filtered_options):
            self.voice_select.value = "eve"
        elif filtered_options:
            self.voice_select.value = filtered_options[0][1]
            
        self.log_widget.write_line("Voices ready.")

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select == self.gender_filter:
            self.apply_voice_filter()

    def on_text_area_changed(self, event) -> None:
        if event.text_area.id == "text-editor" and hasattr(self, "char_count"):
            self.char_count.update(f"Characters: {len(event.text_area.text)}")

    def on_input_changed(self, event: Input.Changed) -> None:
        # Re-fetch voices if API key changes and we haven't fetched real ones yet
        if event.input == self.api_input and len(event.input.value) > 20:
            if not getattr(self, "all_voices_data", []) or len(self.all_voices_data) <= 4:
                self.fetch_voices(event.input.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-synthesize":
            self.start_synthesis()
        elif event.button.id and event.button.id.startswith("tag-"):
            # Format: tag-inline-laugh or tag-wrap-whisper
            parts = event.button.id.split("-")
            tag_type = parts[1]
            tag_name = "-".join(parts[2:])
            
            try:
                if tag_type == "inline":
                    text_to_insert = f"[{tag_name}]"
                    self.text_editor.replace(
                        text_to_insert,
                        self.text_editor.selection.start,
                        self.text_editor.selection.end
                    )
                elif tag_type == "wrap":
                    selected_text = self.text_editor.selected_text
                    text_to_insert = f"<{tag_name}>{selected_text}</{tag_name}>"
                    self.text_editor.replace(
                        text_to_insert,
                        self.text_editor.selection.start,
                        self.text_editor.selection.end
                    )
                self.text_editor.focus()
            except Exception as e:
                self.log_widget.write_line(f"Error inserting tag: {e}")

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def start_synthesis(self) -> None:
        text = self.text_editor.text
        if not text.strip():
            self.log_widget.write_line("Please enter some text to synthesize.")
            return

        api_key = self.api_input.value
        if not api_key:
            self.log_widget.write_line("Error: API Key is required.")
            return

        out_path = self.output_input.value
        if not out_path:
            self.log_widget.write_line("Error: Output path is required.")
            return

        voice = self.voice_select.value or "rex"
        try:
            speed = float(self.speed_input.value)
            speed = max(0.25, min(4.0, speed))
            self.speed_input.value = str(speed)
        except ValueError:
            speed = 1.0
        
        fmt = getattr(self, "format_select", None)
        lang = getattr(self, "lang_select", None)
        out_fmt = fmt.value if fmt else "mp3"
        out_lang = lang.value if lang else "en"
        
        dry_run = self.dry_run_checkbox.value
        auto_play = getattr(self, "play_checkbox", None)
        should_play = auto_play.value if auto_play else False
        
        self.log_widget.write_line("-" * 40)
        self.log_widget.write_line(f"Starting synthesis (chars: {len(text)})...")
        self.log_widget.write_line(f"Output: {out_path} | Voice: {voice} | Speed: {speed}")
        
        self.synth_button.disabled = True
        
        self.run_tts_worker(api_key, text, out_path, voice, speed, dry_run, out_fmt, out_lang, should_play)

    @work(thread=True)
    def run_tts_worker(self, api_key: str, text: str, out_path: str, voice: str, speed: float, dry_run: bool, out_fmt: str = "mp3", out_lang: str = "en", should_play: bool = False) -> None:
        class LogRedirector(io.StringIO):
            def __init__(self, app_ref):
                super().__init__()
                self.app_ref = app_ref
            def write(self, s):
                for line in s.splitlines():
                    if line.strip():
                        self.app_ref.call_from_thread(self.app_ref.log_widget.write_line, line.strip())

        redirector = LogRedirector(self.app)
        
        with contextlib.redirect_stdout(redirector), contextlib.redirect_stderr(redirector):
            try:
                # Resolve output directory
                out_dir = os.path.dirname(os.path.abspath(out_path))
                if out_dir and not os.path.exists(out_dir):
                    os.makedirs(out_dir, exist_ok=True)
                    print(f"Created directory: {out_dir}")

                if dry_run:
                    import time
                    time.sleep(0.5)
                    print(f"[DRY RUN] Would send {len(text)} characters to xAI API.")
                    print(f"[DRY RUN] Voice: {voice}, Speed: {speed}")
                    print(f"[DRY RUN] Would save audio to: {os.path.abspath(out_path)}")
                    print("[DRY RUN] Success! (Simulated)")
                else:
                    url = "https://api.x.ai/v1/tts"
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "text": text,
                        "voice_id": voice,
                        "language": out_lang,
                        "output_format": {
                            "codec": out_fmt,
                            "sample_rate": 44100,
                            "bit_rate": 192000
                        },
                        "speed": speed
                    }

                    print("Sending POST request to xAI TTS API...")
                    response = requests.post(url, headers=headers, json=payload)
                    
                    if not response.ok:
                        print(f"API Error {response.status_code}: {response.text}")
                    else:
                        with open(out_path, "wb") as f:
                            f.write(response.content)
                        print(f"Successfully saved {len(response.content):,} bytes to {os.path.abspath(out_path)}")
                        if should_play:
                            print(f"Playing audio: {out_path}")
                            import subprocess, sys
                            if sys.platform == "win32":
                                os.startfile(out_path)
                            elif sys.platform == "darwin":
                                subprocess.Popen(["open", out_path])
                            else:
                                subprocess.Popen(["xdg-open", out_path])
            except Exception as e:
                print(f"Exception during synthesis: {e}")

        self.app.call_from_thread(self.log_widget.write_line, "Task complete.")
        self.app.call_from_thread(self.enable_synth_button)

    def enable_synth_button(self) -> None:
        self.synth_button.disabled = False

if __name__ == "__main__":
    app = XAITTSApp()
    app.run()
