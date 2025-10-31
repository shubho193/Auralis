from audio_mixer import StemMixer


def example_basic_mix():
    mixer = StemMixer(sample_rate=44100)
    
    stems = {
        'drums': 'stems/drums.wav',
        'bass': 'stems/bass.wav',
        'synth': 'stems/synth.wav',
        'vocals': 'stems/vocals.wav',
    }
    
    gains = {
        'drums': 0.0,     # No change
        'bass': -1.0,     # -1 dB
        'synth': -2.0,    # -2 dB
        'vocals': 1.0,    # +1 dB (vocals a bit louder)
    }
    
    print("Creating mix...")
    mixed_audio = mixer.mix_stems(stems, gains=gains)
    
    mixer.save_audio(mixed_audio, 'output/basic_mix.wav')


def example_advanced_mix():
    mixer = StemMixer(sample_rate=44100)
    
    stems = {
        'drums': 'stems/drums.wav',
        'bass': 'stems/bass.wav',
        'synth': 'stems/synth.wav',
        'vocals': 'stems/vocals.wav',
    }
    
    # Gain settings
    gains = {
        'drums': -1.0,
        'bass': -0.5,
        'synth': -1.5,
        'vocals': 0.0,
    }
    
    # Panning (-1 = left, 0 = center, 1 = right)
    pans = {
        'drums': 0.0,    # Center
        'bass': 0.0,     # Center
        'synth': 0.3,    # Slightly right
        'vocals': 0.0,   # Center
    }
    
    # EQ filters (in Hz)
    high_pass = {
        'vocals': 80.0,   # Remove low frequencies from vocals
        'synth': 60.0,    # Remove very low frequencies from synth
    }
    
    low_pass = {
        'drums': 8000.0,  # Reduce high frequencies in drums
    }
    
    # Mix with all effects
    print("Creating advanced mix...")
    mixed_audio = mixer.mix_stems(
        stems=stems,
        gains=gains,
        pans=pans,
        high_pass_cutoffs=high_pass,
        low_pass_cutoffs=low_pass
    )
    
    mixer.save_audio(mixed_audio, 'output/advanced_mix.wav')


def example_custom_stems():
    
    mixer = StemMixer(sample_rate=48000) 
    stems = {
        'kick': 'my_stems/kick_drum.wav',
        'snare': 'my_stems/snare.wav',
        'bass_guitar': 'my_stems/bass.wav',
        'lead_vocal': 'my_stems/lead_vocals.wav',
        'backing_vocals': 'my_stems/backing_vocals.wav',
    }
    
    gains = {
        'kick': 0.0,
        'snare': 0.5,
        'bass_guitar': -1.0,
        'lead_vocal': 1.5,
        'backing_vocals': -2.0,
    }
    
    print("Creating custom mix...")
    mixed_audio = mixer.mix_stems(stems, gains=gains)
    
    mixer.save_audio(mixed_audio, 'output/custom_mix.wav')


if __name__ == "__main__":
    # Run the examples (make sure you have stem files first!)
    print("Stem Mixer Examples")
    print("=" * 50)
    
    
    print("\nNote: Make sure to create a 'stems' directory with your audio files")
    print("or modify the paths in the examples to point to your stem files.")

