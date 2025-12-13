# Audio Stem Mixer

A Python program that takes multiple audio stems (drums, vocals, synth, bass, etc.) and mixes them together with adjustable parameters like gain, panning, and EQ.

## Features

- **Individual Gain Control**: Adjust volume for each stem in decibels
- **AI-Powered Auto-Gain**: CNN-based automatic gain prediction for optimal balance
- **Panning**: Control left/right stereo position for each stem
- **EQ Filtering**: Apply high-pass and low-pass filters to individual stems
- **Automatic Sample Rate Conversion**: Handles different sample rates automatically
- **Mono to Stereo Conversion**: Converts mono audio to stereo automatically
- **Length Normalization**: Automatically handles stems of different lengths
- **Output Normalization**: Prevents clipping in the final mix

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `stems` folder and add your audio files (drums.wav, bass.wav, etc.)

Required packages:
- `numpy` - Array operations
- `soundfile` - Reading and writing audio files
- `librosa` - Audio processing and resampling
- `scipy` - Signal processing (for filters)
- `tensorflow` - Neural network for auto-gain (optional but recommended)
- `kivy` - GUI framework (for graphical interface)
- `kivymd` - Material Design components (optional)

## Quick Start

### Basic Mixing

The easiest way to get started is using the quick start script:

```bash
python quick_start.py
```

This will automatically:
- Look for stem files in the `stems` folder
- Apply balanced gain settings
- Save the output to `output/quick_mix.wav`

### AI-Powered Auto-Gain Mixing

For automatic gain adjustment powered by AI:

```bash
python quick_start_auto_gain.py
```

This will:
- Analyze each stem using audio features
- Automatically predict optimal gain values
- Create an intelligent mix with no manual tuning needed

### Graphical User Interface (GUI)

Launch the beautiful Kivy-based GUI:

```bash
python audio_mixer_gui.py
```

Features:
- 🎨 Modern, intuitive interface with animations
- 🎵 Easy drag-and-drop stem management
- 🤖 Toggle AI auto-gain on/off
- 📊 Real-time progress visualization
- ✅ Live status updates

See [GUI_README.md](GUI_README.md) for detailed GUI documentation.

## Usage

### Command Line

```bash
python audio_mixer.py <stems_directory> [output_file]
```

Example:
```bash
python audio_mixer.py ./stems mixed_output.wav
```

The program will look for files named `drums.wav`, `bass.wav`, `synth.wav`, and `vocals.wav` in the stems directory.

### Python API

```python
from audio_mixer import StemMixer

# Create mixer
mixer = StemMixer(sample_rate=44100)

# Define stems
stems = {
    'drums': 'stems/drums.wav',
    'bass': 'stems/bass.wav',
    'vocals': 'stems/vocals.wav',
}

# Define gain settings (in dB)
gains = {
    'drums': 0.0,     # No change
    'bass': -1.0,     # -1 dB
    'vocals': 1.0,    # +1 dB
}

# Mix
mixed_audio = mixer.mix_stems(stems, gains=gains)

# Save
mixer.save_audio(mixed_audio, 'output.wav')
```

### Advanced Usage with Panning and EQ

```python
from audio_mixer import StemMixer

mixer = StemMixer(sample_rate=44100)

stems = {
    'drums': 'stems/drums.wav',
    'synth': 'stems/synth.wav',
    'vocals': 'stems/vocals.wav',
}

gains = {
    'drums': -1.0,
    'synth': -2.0,
    'vocals': 1.0,
}

# Panning (-1 = left, 0 = center, 1 = right)
pans = {
    'drums': 0.0,
    'synth': 0.3,
    'vocals': 0.0,
}

# EQ filters
high_pass = {
    'vocals': 80.0,   # Remove frequencies below 80 Hz
}

low_pass = {
    'drums': 8000.0,  # Remove frequencies above 8000 Hz
}

# Mix with all effects
mixed_audio = mixer.mix_stems(
    stems=stems,
    gains=gains,
    pans=pans,
    high_pass_cutoffs=high_pass,
    low_pass_cutoffs=low_pass
)

mixer.save_audio(mixed_audio, 'mixed_output.wav')
```

### AI-Powered Automatic Gain Control

The most powerful feature is automatic gain prediction using machine learning:

```python
from audio_mixer import StemMixer

mixer = StemMixer(sample_rate=44100)

stems = {
    'drums': 'stems/drums.wav',
    'bass': 'stems/bass.wav',
    'synth': 'stems/synth.wav',
    'vocals': 'stems/vocals.wav',
}

# Let AI determine optimal gain levels
mixed_audio = mixer.mix_stems(
    stems,
    auto_gain=True,      # Enable automatic gain prediction
    use_cnn=False        # Use rule-based or CNN (set True for CNN)
)

mixer.save_audio(mixed_audio, 'auto_mix.wav')
```

The AI analyzes each stem and considers:
- RMS energy (loudness)
- Spectral centroid (brightness)
- Spectral rolloff (energy distribution)
- Zero crossing rate (texture)
- Spectral bandwidth (frequency spread)
- MFCC features (timbre characteristics)

## Parameters

### Gains
- **Type**: Dictionary of stem names to float values
- **Unit**: Decibels (dB)
- **Example**: `{'vocals': 1.0}` increases vocals by 1 dB
- **Note**: 0 dB = no change, positive = louder, negative = quieter

### Panning
- **Type**: Dictionary of stem names to float values
- **Range**: -1.0 (full left) to 1.0 (full right)
- **Example**: `{'synth': 0.3}` pans synth slightly to the right
- **Note**: 0 = center

### High-Pass Filters
- **Type**: Dictionary of stem names to float values
- **Unit**: Hz (frequency)
- **Example**: `{'vocals': 80.0}` removes frequencies below 80 Hz
- **Use case**: Removing low-frequency noise or mud

### Low-Pass Filters
- **Type**: Dictionary of stem names to float values
- **Unit**: Hz (frequency)
- **Example**: `{'drums': 8000.0}` removes frequencies above 8000 Hz
- **Use case**: Softening harsh high frequencies

## Supported Audio Formats

- WAV (recommended)
- FLAC
- OGG
- Any format supported by `soundfile`

## File Structure

```
Audio Processor/
├── audio_mixer.py          # Main mixer class
├── gain_predictor.py       # AI auto-gain predictor
├── audio_mixer_gui.py      # GUI application
├── train_cnn_model.py      # CNN model training script
├── quick_start.py          # Basic quick start
├── quick_start_auto_gain.py # AI quick start
├── example_usage.py        # Usage examples
├── example_auto_gain.py    # Auto-gain examples
├── requirements.txt        # Dependencies
├── README.md              # This file
├── GUI_README.md          # GUI documentation
└── stems/                 # Put your stem files here
    ├── drums.wav
    ├── bass.wav
    ├── synth.wav
    └── vocals.wav
```

## Tips for Best Results

1. **Use high-quality stem files**: Better source material = better mix
2. **Match gain levels**: Start with all stems at 0 dB and adjust from there
3. **Use EQ sparingly**: Small adjustments often sound better than drastic cuts
4. **Keep vocals prominent**: Typically vocals should be the loudest element
5. **Test in stereo**: Use headphones or good speakers to evaluate panning
6. **Prevent clipping**: The mixer normalizes output automatically, but keep individual stems from clipping

## Troubleshooting

**Problem**: "No stem files found!"
- **Solution**: Make sure your stem files are named correctly (`drums.wav`, etc.) and in the correct directory

**Problem**: "Error reading audio file"
- **Solution**: Check that the audio file is not corrupted and is in a supported format

**Problem**: Output sounds distorted
- **Solution**: Reduce gain values or check for clipping in individual stems

**Problem**: Auto-gain not working
- **Solution**: Make sure `gain_predictor.py` is in the same directory as `audio_mixer.py`

**Problem**: TensorFlow import errors
- **Solution**: Install TensorFlow with `pip install tensorflow` (optional, rule-based prediction works without it)

## Advanced: Training Your Own Model

To train a custom CNN model on your own data:

```bash
python train_cnn_model.py
```

This will:
1. Load training data (stems + expert gain decisions)
2. Extract audio features
3. Train a neural network
4. Save the model for future use

In production, train on professionally mixed tracks to learn optimal gain settings.

## License

This project is open source and available for educational and personal use.
