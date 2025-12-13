import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.metrics import dp
from kivy.core.window import Window

import os
import threading
import io
import contextlib
from pathlib import Path
from typing import Dict, Optional

try:
    from audio_mixer import StemMixer
    from gain_predictor import GainPredictor
    HAS_AUDIO_MODULES = True
except ImportError:
    HAS_AUDIO_MODULES = False


Window.size = (900, 500)
Window.clearcolor = (0.02, 0.05, 0.1, 1)  # Deep Navy Background

# Theme Colors
C_BACKGROUND = (0.02, 0.05, 0.1, 1)
C_PRIMARY = (0.0, 0.9, 1.0, 1)      # Cyan
C_SECONDARY = (0.95, 0.95, 1.0, 1)  # White
C_BTN_NORMAL = (0.0, 0.2, 0.3, 1)   # Dark Cyan
C_BTN_ACTIVE = (0.0, 0.4, 0.5, 1)
C_WARNING = (1.0, 0.3, 0.3, 1)
C_TEXT_MAIN = (0.9, 0.95, 1.0, 1)
C_TEXT_DIM = (0.6, 0.7, 0.8, 1)




class AnimatedProgressBar(Widget):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.progress_value = 0.0
        self.bind(size=self._update_canvas, pos=self._update_canvas)
        self._update_canvas()
        self.animation = None
    
    def _update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Background rail
            Color(0.1, 0.2, 0.3, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            # Progress bar
            Color(*C_PRIMARY)
            current_width = self.size[0] * self.progress_value
            self.rect = Rectangle(pos=self.pos, size=(current_width, self.size[1]))
            
            # Glow effect (simple line)
            Color(1, 1, 1, 0.3)
            Line(points=[self.pos[0], self.pos[1] + self.size[1]/2, self.pos[0] + self.size[0], self.pos[1] + self.size[1]/2], width=1)
    
    def animate_progress(self, value, duration=1.0):
        self.progress_value = value
        target_width = self.size[0] * value
        anim = Animation(size=(target_width, self.size[1]), duration=duration)
        anim.start(self.rect)
        self.animation = anim


class StemFileItem(BoxLayout):
    def __init__(self, name, file_path, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(60)
        self.name = name
        self.file_path = file_path
        
        layout = BoxLayout(orientation='horizontal', spacing=dp(10), padding=dp(10))
        
        # Minimalist icon
        icon = Label(text='[wav]', size_hint_x=0.1, font_size=dp(16),  color=C_PRIMARY)
        layout.add_widget(icon)
        
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
        name_label = Label(
            text=name.upper(),
            size_hint_y=0.6,
            font_size=dp(18),
            bold=True,
            
            color=C_TEXT_MAIN,
            halign='left',
            valign='bottom'
        )
        name_label.bind(size=name_label.setter('text_size'))
        
        path_label = Label(
            text=os.path.basename(file_path),
            size_hint_y=0.4,
            font_size=dp(12),
            
            text_size=(None, None),
            halign='left',
            valign='top',
            color=C_TEXT_DIM
        )
        path_label.bind(size=path_label.setter('text_size'))
        
        info_layout.add_widget(name_label)
        info_layout.add_widget(path_label)
        layout.add_widget(info_layout)
        
        remove_btn = Button(
            text='X',
            size_hint_x=0.1,
            font_size=dp(18),
            
            background_color=(0, 0, 0, 0), # Transparent
            color=C_WARNING
        )
        layout.add_widget(remove_btn)
        
        self.add_widget(layout)


class AudioMixerGUI(App):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stems: Dict[str, str] = {}
        self.mixer = None
        self.is_processing = False
    
    def build(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        title = Label(
            text='SONIC INTELLIGENCE',
            size_hint_y=0.1,
            font_size=dp(36),
            bold=True,
            
            color=C_PRIMARY,
            outline_width=1,
            outline_color=C_SECONDARY
        )
        main_layout.add_widget(title)
        
        # Content area
        content = BoxLayout(orientation='horizontal', spacing=dp(20))
        
        # Left panel - Stem management
        left_panel = BoxLayout(orientation='vertical', size_hint_x=0.5, spacing=dp(10))
        
        # Add stems button
        # Add stems button
        add_btn = Button(
            text='+ ADD STEMS',
            size_hint_y=0.1,
            font_size=dp(16),
            
            background_color=C_BTN_NORMAL,
            color=C_SECONDARY,
            on_press=self.show_file_browser
        )
        left_panel.add_widget(add_btn)
        
        # Stems list
        stems_scroll = ScrollView(size_hint_y=0.7)
        self.stems_container = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        self.stems_container.bind(minimum_height=self.stems_container.setter('height'))
        stems_scroll.add_widget(self.stems_container)
        left_panel.add_widget(stems_scroll)
        
        # Mix options
        options_layout = BoxLayout(orientation='vertical', size_hint_y=0.2, spacing=dp(5))
        
        # Auto-gain toggle
        # Auto-gain toggle
        self.auto_gain_btn = Button(
            text='AI AUTO-GAIN: OFF',
            size_hint_y=1.0,
            font_size=dp(14),
            
            background_color=(0.2, 0.2, 0.2, 1),
            color=C_TEXT_DIM,
            on_press=self.toggle_auto_gain
        )
        self.auto_gain_enabled = False
        
        options_layout.add_widget(self.auto_gain_btn)
        left_panel.add_widget(options_layout)
        
        # Right panel - Processing and output
        right_panel = BoxLayout(orientation='vertical', size_hint_x=0.5, spacing=dp(10))
        
        # Mix button
        # Mix button
        self.mix_btn = Button(
            text='INITIALIZE MIX',
            size_hint_y=0.15,
            font_size=dp(20),
            
            bold=True,
            background_color=C_BTN_NORMAL,
            color=C_PRIMARY,
            on_press=self.start_mixing
        )
        right_panel.add_widget(self.mix_btn)
        
        # Progress area
        progress_layout = BoxLayout(orientation='vertical', size_hint_y=0.3, spacing=dp(10))
        
        self.status_label = Label(
            text='SYSTEM READY',
            font_size=dp(14),
            
            color=C_TEXT_MAIN
        )
        progress_layout.add_widget(self.status_label)
        
        self.progress_bar = AnimatedProgressBar(height=dp(40))
        progress_layout.add_widget(self.progress_bar)
        
        right_panel.add_widget(progress_layout)
        
        # Output area
        output_scroll = ScrollView(size_hint_y=0.55)
        self.output_container = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None
        )
        self.output_container.bind(minimum_height=self.output_container.setter('height'))
        output_scroll.add_widget(self.output_container)
        right_panel.add_widget(output_scroll)
        
        content.add_widget(left_panel)
        content.add_widget(right_panel)
        main_layout.add_widget(content)
        
        return main_layout
    
    def show_file_browser(self, instance):
        """Show file browser popup"""
        # Set default path to current project directory
        default_path = os.path.dirname(os.path.abspath(__file__))
        
        filechooser = FileChooserIconView(
            path=default_path,
            filters=['*.wav', '*.flac', '*.mp3', '*.ogg'],
            dirselect=False
        )
        
        select_btn = Button(text='Select')
        cancel_btn = Button(text='Cancel')
        
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=dp(10))
        button_layout.add_widget(select_btn)
        button_layout.add_widget(cancel_btn)
        
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        content.add_widget(filechooser)
        content.add_widget(button_layout)
        
        popup = Popup(
            title='Select Audio File',
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        
        # Set button actions after popup is created
        select_btn.on_press = lambda: [self.add_stem(filechooser.path, filechooser.selection), popup.dismiss()]
        cancel_btn.on_press = lambda: [popup.dismiss()]

        
        popup.open()
    
    def add_stem(self, path, selection):
        """Add selected file as a stem"""
        if not selection:
            return
        
        file_path = selection[0]
        
        # Determine stem name from filename
        filename = os.path.basename(file_path).lower()
        stem_name = None
        
        # Check for common stem names
        for name in ['drums', 'bass', 'vocals', 'synth', 'lead', 'guitar', 'piano', 'strings']:
            if name in filename:
                stem_name = name
                break
        
        # Default name if not found
        if not stem_name:
            stem_name = filename.split('.')[0]
        
        # Add to stems dict
        self.stems[stem_name] = file_path
        self.update_stems_display()
    
    def update_stems_display(self):
        """Update the stems display"""
        self.stems_container.clear_widgets()
        
        for name, path in self.stems.items():
            item = StemFileItem(name, path)
            # Add remove functionality
            remove_btn = item.children[0].children[0]  # Get remove button
            remove_btn.on_press = lambda btn, n=name: self.remove_stem(n)
            self.stems_container.add_widget(item)
    
    def remove_stem(self, name):
        """Remove a stem"""
        if name in self.stems:
            del self.stems[name]
            self.update_stems_display()
    
    def toggle_auto_gain(self, instance):
        """Toggle auto-gain feature"""
        self.auto_gain_enabled = not self.auto_gain_enabled
        
        if self.auto_gain_enabled:
            self.auto_gain_btn.text = 'AI AUTO-GAIN: ON'
            self.auto_gain_btn.background_color = C_PRIMARY
            self.auto_gain_btn.color = C_BACKGROUND
        else:
            self.auto_gain_btn.text = 'AI AUTO-GAIN: OFF'
            self.auto_gain_btn.background_color = (0.2, 0.2, 0.2, 1)
            self.auto_gain_btn.color = C_TEXT_DIM
    
    def start_mixing(self, instance):
        """Start the mixing process"""
        if not self.stems:
            self.show_error("No stems added! Please add at least one audio file.")
            return
        
        if self.is_processing:
            return
        
        self.is_processing = True
        self.mix_btn.disabled = True
        self.mix_btn.text = 'PROCESSING...'
        
        # Clear previous output
        self.output_container.clear_widgets()
        
        # Start mixing in a separate thread
        thread = threading.Thread(target=self.mix_audio)
        thread.daemon = True
        thread.start()
    
    def mix_audio(self):
        """Perform audio mixing in background thread"""
        try:
            if not HAS_AUDIO_MODULES:
                Clock.schedule_once(lambda dt: self.show_error("Audio modules not found!"))
                return
            
            # Update status
            Clock.schedule_once(lambda dt: self.set_status("INITIALIZING MIXER..."))
            Clock.schedule_once(lambda dt: self.update_progress(0.1))
            
            # Create mixer
            self.mixer = StemMixer(sample_rate=44100)
            
            Clock.schedule_once(lambda dt: self.set_status("LOADING STEMS..."))
            Clock.schedule_once(lambda dt: self.update_progress(0.3))
            
            Clock.schedule_once(lambda dt: self.set_status("MIXING AUDIO..."))
            Clock.schedule_once(lambda dt: self.update_progress(0.5))
            
            # Mix with or without auto-gain
            if self.auto_gain_enabled:
                mixed_audio = self.mixer.mix_stems(
                    self.stems,
                    auto_gain=True,
                    use_cnn=False
                )
            else:
                # Use default gains
                mixed_audio = self.mixer.mix_stems(self.stems)
            
            Clock.schedule_once(lambda dt: self.set_status("SAVING OUTPUT..."))
            Clock.schedule_once(lambda dt: self.update_progress(0.9))
            
            # Save output
            os.makedirs('output', exist_ok=True)
            output_path = 'output/stems_mix.wav'
            self.mixer.save_audio(mixed_audio, output_path)
            
            Clock.schedule_once(lambda dt: self.update_progress(1.0))
            Clock.schedule_once(lambda dt: self.set_status("MIX COMPLETE"))
            
            # Show success
            Clock.schedule_once(lambda dt: self.show_success(output_path))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(f"Error: {str(e)}"))
        
        finally:
            self.is_processing = False
            Clock.schedule_once(lambda dt: setattr(self.mix_btn, 'disabled', False))
            Clock.schedule_once(lambda dt: setattr(self.mix_btn, 'text', 'INITIALIZE MIX'))
    
    def set_status(self, text):
        """Update status label"""
        self.status_label.text = text
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.animate_progress(value, duration=0.3)
    
    def show_error(self, message):
        """Show error popup"""
        popup = Popup(
            title='Error',
            content=Label(text=message, padding=dp(20)),
            size_hint=(0.6, 0.3),
            background_color=(0.8, 0.3, 0.3, 1)
        )
        popup.open()
    
    def show_success(self, output_path):
        """Show success message with output"""
        self.output_container.clear_widgets()
        
        success_label = Label(
            text='MIX COMPLETE',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(24),
            color=C_PRIMARY
        )
        self.output_container.add_widget(success_label)
        
        path_label = Label(
            text=f'OUTPUT: {output_path}',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(14),
            text_size=(None, None),
            halign='left',
            color=C_TEXT_MAIN
        )
        self.output_container.add_widget(path_label)
        
        # Show mix information
        info_label = Label(
            text=f'STEMS MIXED: {len(self.stems)}',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(14),
            color=C_TEXT_DIM
        )
        self.output_container.add_widget(info_label)
        
        # Reset progress after delay
        def reset_progress(dt):
            self.update_progress(0.0)
        
        Clock.schedule_once(reset_progress, 2.0)


if __name__ == '__main__':
    AudioMixerGUI().run()

