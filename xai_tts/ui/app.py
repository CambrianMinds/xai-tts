from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Header, Footer, Button, Select
from textual import work
from datetime import datetime
import asyncio
import os
import sys

from xai_tts.config import AppConfig, SynthesisHistoryItem, add_history, calculate_cost
from xai_tts.api import XAITTSAPI
from xai_tts.ui.panels import SettingsPanel, EditorPanel, TagsPanel
from xai_tts.ui.messages import APICredentialsUpdated

class XAITTSApp(App):
    CSS = """
    Screen { layout: horizontal; }
    #left-panel { width: 25%; height: 100%; border-right: solid $primary; padding: 1; }
    #center-panel { width: 55%; height: 100%; padding: 1; }
    #right-panel { width: 20%; height: 100%; border-left: solid $primary; padding: 1; }
    .field { margin-bottom: 1; }
    #text-editor { height: 1fr; margin-bottom: 1; }
    Log { border: solid gray; height: 10; }
    .tag-category { margin-top: 1; text-style: bold; color: yellow; }
    .tag-btn { width: 100%; margin-bottom: 1; }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
        ("ctrl+s", "synthesize", "Synthesize"),
        ("p", "insert_pause", "Insert Pause"),
    ]

    def __init__(self):
        super().__init__()
        self.config = AppConfig.load()
        self.api = None
        self.all_voices_data = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            self.settings_panel = SettingsPanel(self.config, id="left-panel")
            yield self.settings_panel
            self.editor_panel = EditorPanel(id="center-panel")
            yield self.editor_panel
            self.tags_panel = TagsPanel(id="right-panel")
            yield self.tags_panel
        yield Footer()

    async def on_mount(self) -> None:
        self.title = "xAI TTS Studio"
        self.dark = self.config.theme == "textual-dark"
        self.log_msg("Welcome to xAI TTS Studio.")
        
        # Load API key
        api_key = self.config.api_key or os.environ.get("XAI_API_KEY")
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
            self.settings_panel.api_input.value = api_key
            self.config.api_key = api_key
            self.log_msg("Loaded API Key.")
            self.setup_api(api_key)

    def log_msg(self, message: str) -> None:
        self.editor_panel.log_widget.write_line(message)

    def setup_api(self, api_key: str):
        if self.api:
            asyncio.create_task(self.api.close())
        self.api = XAITTSAPI(api_key)
        self.fetch_voices()

    async def on_a_p_i_credentials_updated(self, message: APICredentialsUpdated):
        self.setup_api(message.api_key)
        self.config.save()

    @work(exclusive=True)
    async def fetch_voices(self):
        if not self.api:
            return
        
        self.log_msg("Fetching voices...")
        try:
            voices = await self.api.fetch_voices()
            self.all_voices_data = voices
            self.apply_voice_filter()
            self.log_msg("Voices ready.")
        except Exception as e:
            self.log_msg(f"Error fetching voices: {e}")

    def on_select_changed(self, event: Select.Changed) -> None:
        if getattr(event.select, "id", None) == self.settings_panel.gender_filter.id or event.select == self.settings_panel.gender_filter:
            self.apply_voice_filter()

    def apply_voice_filter(self) -> None:
        if not self.all_voices_data:
            return
            
        filter_val = self.settings_panel.gender_filter.value
        
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
            
        self.settings_panel.voice_select.set_options(filtered_options)
        self.settings_panel.voice_select.disabled = False
        
        if filtered_options:
            if not self.settings_panel.voice_select.value:
                self.settings_panel.voice_select.value = filtered_options[0][1]

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-synthesize":
            self.action_synthesize()
        elif event.button.id == "btn-preview":
            self.action_synthesize(preview=True)
        elif event.button.id and event.button.id.startswith("tag-"):
            parts = event.button.id.split("-")
            tag_type = parts[1]
            tag_name = "-".join(parts[2:])
            editor = self.editor_panel.text_editor
            
            try:
                if tag_type == "inline":
                    text_to_insert = f"[{tag_name}]"
                    editor.replace(text_to_insert, editor.selection.start, editor.selection.end)
                elif tag_type == "wrap":
                    selected_text = editor.selected_text
                    text_to_insert = f"<{tag_name}>{selected_text}</{tag_name}>"
                    editor.replace(text_to_insert, editor.selection.start, editor.selection.end)
                editor.focus()
            except Exception as e:
                self.log_msg(f"Error inserting tag: {e}")

    def action_insert_pause(self) -> None:
        editor = self.editor_panel.text_editor
        editor.replace("[pause]", editor.selection.start, editor.selection.end)
        editor.focus()

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark
        self.config.theme = "textual-dark" if self.dark else "textual-light"
        self.config.save()

    def action_synthesize(self, preview=False) -> None:
        text = self.editor_panel.text_editor.selected_text if preview else self.editor_panel.text_editor.text
        if not text.strip():
            self.log_msg("No text to synthesize.")
            return

        if not self.api:
            self.log_msg("API key not set.")
            return

        out_path = self.settings_panel.output_input.value
        voice = self.settings_panel.voice_select.value or "rex"
        try:
            speed = float(self.settings_panel.speed_input.value)
        except ValueError:
            speed = 1.0
            
        out_fmt = self.settings_panel.format_select.value
        out_lang = self.settings_panel.lang_select.value
        dry_run = self.settings_panel.dry_run_checkbox.value
        should_play = self.settings_panel.play_checkbox.value
        
        self.log_msg("-" * 40)
        self.log_msg(f"Starting {'preview ' if preview else ''}synthesis...")
        self.settings_panel.synth_button.disabled = True
        
        self.run_tts_task(text, out_path, voice, speed, dry_run, out_fmt, out_lang, should_play, preview)

    @work(exclusive=True)
    async def run_tts_task(self, text, out_path, voice, speed, dry_run, out_fmt, out_lang, should_play, preview):
        if preview:
            # Modify output path for preview
            base, ext = os.path.splitext(out_path)
            out_path = f"{base}_preview{ext}"
            
        try:
            out_dir = os.path.dirname(os.path.abspath(out_path))
            if out_dir and not os.path.exists(out_dir):
                os.makedirs(out_dir, exist_ok=True)
                
            if dry_run:
                await asyncio.sleep(0.5)
                self.log_msg(f"[DRY RUN] Would send {len(text)} chars.")
                self.log_msg(f"[DRY RUN] Voice: {voice}, Speed: {speed}")
                self.log_msg(f"[DRY RUN] Would save to {out_path}")
            else:
                self.log_msg("Requesting audio from API...")
                audio_data = await self.api.synthesize(text, voice, speed, out_fmt, out_lang)
                with open(out_path, "wb") as f:
                    f.write(audio_data)
                self.log_msg(f"Saved {len(audio_data):,} bytes to {out_path}")
                
                # Save history
                cost = calculate_cost(text)
                add_history(SynthesisHistoryItem(
                    text=text, voice=voice, speed=speed, 
                    output_path=out_path, cost=cost, 
                    timestamp=datetime.now().isoformat()
                ))

                if should_play:
                    self.play_audio(out_path)
                    
        except Exception as e:
            # Enhanced error messages
            if hasattr(e, "response") and e.response is not None:
                self.log_msg(f"Synthesis failed (API Error {e.response.status_code}): {e.response.text}")
            else:
                self.log_msg(f"Synthesis failed: {e}")
            
        self.settings_panel.synth_button.disabled = False

    def play_audio(self, path):
        self.log_msg(f"Playing {path}")
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except ImportError:
            # Fallback
            import subprocess
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            self.log_msg(f"Could not play audio: {e}")

def main():
    app = XAITTSApp()
    app.run()

if __name__ == "__main__":
    main()
