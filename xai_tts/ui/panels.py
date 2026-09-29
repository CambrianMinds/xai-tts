from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll, Horizontal
from textual.widgets import Label, Input, Select, Checkbox, Button, TextArea, Log
from textual.message import Message

from xai_tts.config import AppConfig, calculate_cost
from xai_tts.tags import get_all_tags
from xai_tts.ui.messages import APICredentialsUpdated, SynthesisRequested

class SettingsPanel(Vertical):
    def __init__(self, config: AppConfig, **kwargs):
        self.config = config
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Label("API Key", classes="field")
        self.api_input = Input(value=self.config.api_key, placeholder="xAI API Key", password=True, classes="field")
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
            self.lang_select = Select([
                ("Auto", "auto"), ("English", "en"), ("Spanish", "es"), 
                ("French", "fr"), ("German", "de"), ("Italian", "it"),
                ("Portuguese", "pt"), ("Russian", "ru"), ("Chinese", "zh"),
                ("Japanese", "ja"), ("Korean", "ko"), ("Arabic", "ar"),
                ("Hindi", "hi"), ("Turkish", "tr"), ("Dutch", "nl"), 
                ("Polish", "pl"), ("Swedish", "sv"), ("Indonesian", "id"), 
                ("Vietnamese", "vi"), ("Tagalog", "tl"), ("Ukrainian", "uk"), 
                ("Greek", "el"), ("Czech", "cs"), ("Danish", "da"), 
                ("Finnish", "fi"), ("Romanian", "ro")
            ], value=self.config.default_language, classes="field")
            yield self.format_select
            yield self.lang_select

        yield Label("Speed Multiplier", classes="field")
        self.speed_input = Input(value=str(self.config.default_speed), placeholder="1.0", classes="field")
        yield self.speed_input
        
        self.dry_run_checkbox = Checkbox("Dry Run (Simulate API)", value=False, classes="field")
        yield self.dry_run_checkbox
        
        self.play_checkbox = Checkbox("Auto-play Output", value=self.config.play_after_synthesis, classes="field")
        yield self.play_checkbox
        
        self.synth_button = Button("Synthesize Audio", variant="success", id="btn-synthesize")
        yield self.synth_button

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input == self.api_input:
            self.config.api_key = event.input.value
            self.post_message(APICredentialsUpdated(self.config.api_key))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button == self.synth_button:
            # We want to ask the main app to start synthesis. 
            # We don't have the text here, so we just emit a generic event or let the app handle the button via ID.
            pass  # Handled by App

class EditorPanel(Vertical):
    def compose(self) -> ComposeResult:
        yield Label("Text to Synthesize:")
        
        # Setting language="html" so that <tags> are highlighted properly
        self.text_editor = TextArea("Hello! [pause] This is a <whisper>general purpose</whisper> TTS studio.", id="text-editor", language="html")
        yield self.text_editor
        
        with Horizontal():
            self.char_count = Label("Characters: 73", id="char-count")
            self.cost_est = Label(" | Est. Cost: $0.0011", id="cost-estimate")
            yield self.char_count
            yield self.cost_est
            
        yield Button("Preview Selected Text", id="btn-preview", variant="primary", classes="field")
            
        yield Label("Output Logs:")
        self.log_widget = Log(id="log")
        yield self.log_widget

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self._update_cost()

    def on_text_area_selection_changed(self, event: TextArea.SelectionChanged) -> None:
        self._update_cost()

    def _update_cost(self) -> None:
        selected = self.text_editor.selected_text
        if selected:
            chars = len(selected)
            cost = calculate_cost(selected)
            self.char_count.update(f"Selection: {chars}")
        else:
            text = self.text_editor.text
            chars = len(text)
            cost = calculate_cost(text)
            self.char_count.update(f"Characters: {chars}")
        self.cost_est.update(f" | Est. Cost: ${cost:.5f}")


class TagsPanel(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Label("Tag Library")
        yield Label("Highlight text to wrap, or click to insert.", classes="field")
        
        tags = get_all_tags()
        
        for category, tag_list in tags["inline"].items():
            yield Label(category, classes="tag-category")
            for tag in tag_list:
                yield Button(f"\\[{tag}\\]", id=f"tag-inline-{tag}", classes="tag-btn")
                
        for category, tag_list in tags["wrap"].items():
            yield Label(category, classes="tag-category")
            for tag in tag_list:
                yield Button(f"<{tag}>", id=f"tag-wrap-{tag}", classes="tag-btn")
