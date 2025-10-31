"""
Example using automatic gain prediction with CNN
"""

from audio_mixer import StemMixer


def example_auto_gain_basic():
    """Example using automatic gain prediction (rule-based)"""
    
    mixer = StemMixer(sample_rate=44100)
    
    stems = {
        'drums': 'stems/drums.wav',
        'bass': 'stems/bass.wav',
        'synth': 'stems/synth.wav',
        'vocals': 'stems/vocals.wav',
    }
    
    print("Using automatic gain prediction (rule-based)...")
    mixed_audio = mixer.mix_stems(
        stems,
        auto_gain=True,
        use_cnn=False
    )
    
    mixer.save_audio(mixed_audio, 'output/auto_gain_mix.wav')


def example_auto_gain_cnn():
    """Example using automatic gain prediction (CNN-based)"""
    
    mixer = StemMixer(sample_rate=44100)
    
    stems = {
        'drums': 'stems/drums.wav',
        'bass': 'stems/bass.wav',
        'synth': 'stems/synth.wav',
        'vocals': 'stems/vocals.wav',
    }
    
    print("Using automatic gain prediction (CNN-based)...")
    mixed_audio = mixer.mix_stems(
        stems,
        auto_gain=True,
        use_cnn=True
    )
    
    mixer.save_audio(mixed_audio, 'output/auto_gain_cnn_mix.wav')


def example_hybrid_approach():
    """Example using auto-gain with manual EQ adjustments"""
    
    mixer = StemMixer(sample_rate=44100)
    
    stems = {
        'drums': 'stems/drums.wav',
        'bass': 'stems/bass.wav',
        'vocals': 'stems/vocals.wav',
    }
    
    # Use auto-gain for basic levels, but apply manual EQ
    high_pass = {
        'vocals': 80.0,
        'bass': 30.0,
    }
    
    low_pass = {
        'drums': 8000.0,
    }
    
    # Note: pan and low_pass can still be used with auto_gain
    mixed_audio = mixer.mix_stems(
        stems,
        auto_gain=True,
        high_pass_cutoffs=high_pass,
        low_pass_cutoffs=low_pass
    )
    
    mixer.save_audio(mixed_audio, 'output/hybrid_mix.wav')


if __name__ == "__main__":
    print("Auto-Gain Mixing Examples")
    print("=" * 60)
    
    # Uncomment the example you want to run:
    
    # example_auto_gain_basic()
    # example_auto_gain_cnn()
    # example_hybrid_approach()
    
    print("\nNote: Make sure you have your stem files in the 'stems' directory")
    print("The auto-gain feature will analyze each stem and suggest optimal gain levels.")

