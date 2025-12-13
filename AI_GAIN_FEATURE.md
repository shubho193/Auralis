# AI-Powered Automatic Gain Prediction

## Overview

The Audio Stem Mixer now includes an **AI-powered automatic gain prediction feature** that analyzes your audio stems and automatically determines optimal gain levels for each one. No manual tuning required!

## How It Works

### Feature Extraction

The AI analyzes each stem and extracts multiple audio features:

1. **RMS Energy** (Loudness) - Overall loudness of the track
2. **Spectral Centroid** (Brightness) - Where the energy is concentrated
3. **Spectral Rolloff** - Energy distribution
4. **Zero Crossing Rate** - Texture and attack
5. **Spectral Bandwidth** - Frequency spread
6. **MFCC Features** (13 coefficients) - Timbre characteristics
7. **Dynamic Range** - Consistency and compression

### Gain Prediction Methods

#### 1. Rule-Based Approach (Default)

- Fast and lightweight
- No machine learning models required
- Uses empirical mixing knowledge
- Analyzes features and applies stem-specific adjustments
- Good for most use cases

**Algorithm:**
- Starts with stem-specific baselines (drums: -2dB, bass: -1.5dB, vocals: 0dB, synth: -2.5dB)
- Adjusts based on loudness (quieter stems get boost, louder get cut)
- Applies brightness corrections for vocals
- Handles over-compression with dynamic range analysis

#### 2. CNN-Based Approach (Experimental)

- More sophisticated neural network
- Can be trained on your own data
- Uses mel-spectrograms and deep learning
- Currently in prototype stage
- Falls back to rule-based if no trained model exists

## Usage

### Quick Start

```bash
python quick_start_auto_gain.py
```

### Python API

#### Basic Auto-Gain

```python
from audio_mixer import StemMixer

mixer = StemMixer(sample_rate=44100)

stems = {
    'drums': 'stems/drums.wav',
    'bass': 'stems/bass.wav',
    'vocals': 'stems/vocals.wav',
    'synth': 'stems/synth.wav',
}

# Automatic gain prediction
mixed_audio = mixer.mix_stems(
    stems,
    auto_gain=True,      # Enable AI
    use_cnn=False        # Use rule-based or CNN
)

mixer.save_audio(mixed_audio, 'auto_mix.wav')
```

#### With Manual EQ Overrides

You can still apply EQ even with auto-gain:

```python
mixed_audio = mixer.mix_stems(
    stems,
    auto_gain=True,
    high_pass_cutoffs={
        'vocals': 80.0,  # Remove low end from vocals
    },
    low_pass_cutoffs={
        'drums': 8000.0,  # Soften high end on drums
    }
)
```

## Example Output

```
Analyzing stems for optimal gain settings...
  drums: -1.00 dB (RMS: 0.0492, Centroid: 0.3343)
  bass: 0.13 dB (RMS: 0.1069, Centroid: 0.0098)
  synth: -1.17 dB (RMS: 0.0475, Centroid: 0.0757)
  vocals: 1.05 dB (RMS: 0.0262, Centroid: 0.1591)

=== PREDICTED GAIN SUMMARY ===
  drums: -1.00 dB
  bass: 0.13 dB
  synth: -1.17 dB
  vocals: 1.05 dB
```

## Training Your Own Model

To train a custom CNN model on your own data:

```bash
python train_cnn_model.py
```

This requires:
1. A dataset of professionally mixed tracks
2. Expert gain decisions (labels)
3. TensorFlow installed

See `train_cnn_model.py` for details on the training pipeline.

## Architecture

### GainPredictor Class

- Extracts audio features using librosa
- Applies rule-based gain prediction
- Stem-type aware adjustments

### CNNGainPredictor Class

- Extends GainPredictor
- Uses mel-spectrograms for CNN input
- Can load trained models
- Falls back to rule-based if no model

### Integration

Seamlessly integrated into `StemMixer` class:

```python
mix_stems(
    ...,
    auto_gain=True,    # Enable auto-gain
    use_cnn=False      # Choose method
)
```

## Advantages

1. **Time Saving** - No manual gain adjustment needed
2. **Consistent Results** - Same stems produce same predictions
3. **Learning-Based** - Can improve with more training data
4. **Flexible** - Works with manual overrides for EQ
5. **Fast** - Rule-based approach is lightweight

## Limitations

1. **Music Genre Agnostic** - Same rules apply to all genres
2. **No Artistic Intent** - Doesn't consider creative decisions
3. **Limited Context** - Analyzes stems independently
4. **No Sidechain** - Doesn't implement sidechain compression
5. **Prototype CNN** - Neural network needs real training data

## Future Improvements

- [ ] Genre-specific models
- [ ] Context-aware prediction (considers other stems)
- [ ] Sidechain compression prediction
- [ ] Panning prediction
- [ ] EQ recommendation system
- [ ] User preference learning
- [ ] A/B comparison tools

## Files

- `gain_predictor.py` - Core prediction classes
- `train_cnn_model.py` - Training script
- `example_auto_gain.py` - Usage examples
- `quick_start_auto_gain.py` - Quick demo

## Dependencies

Required:
- numpy
- soundfile
- librosa
- scipy

Optional (for CNN):
- tensorflow

## References

The system uses traditional audio features combined with machine learning:

- **MFCC**: Mel-Frequency Cepstral Coefficients
- **Spectral Features**: Standard audio analysis
- **Deep Learning**: CNN for complex pattern recognition

## License

Same as main project - open source for educational and personal use.


