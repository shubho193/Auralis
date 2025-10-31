from audio_mixer import StemMixer
import os
import sys


def main():
    print("=" * 60)
    print("Audio Stem Mixer - Quick Start")
    print("=" * 60)
    print()
    
    stems_dir = "stems"
    if not os.path.exists(stems_dir):
        print(f"ERROR: '{stems_dir}' directory not found!")
        print()
        print("Please create a 'stems' folder and add your audio files:")
        print("  - drums.wav")
        print("  - bass.wav")
        print("  - synth.wav")
        print("  - vocals.wav")
        print()
        return
    
    expected_stems = {
        'drums': 'drums.wav',
        'bass': 'bass.wav',
        'synth': 'synth.wav',
        'vocals': 'vocals.wav',
    }
    
    available_stems = {}
    for name, filename in expected_stems.items():
        filepath = os.path.join(stems_dir, filename)
        if os.path.exists(filepath):
            available_stems[name] = filepath
        else:
            print(f"Warning: {filename} not found in {stems_dir}")
    
    if not available_stems:
        print(f"\nERROR: No stem files found in '{stems_dir}'!")
        print("\nPlease add at least one of the following files:")
        for filename in expected_stems.values():
            print(f"  - {filename}")
        return
    
    print(f"Found {len(available_stems)} stem(s): {', '.join(available_stems.keys())}")
    print()
    
    print("Creating mixer (sample rate: 44100 Hz)...")
    mixer = StemMixer(sample_rate=44100)
    
    gains = {
        'drums': 0.0,      # Drums at 0 dB
        'bass': -1.0,      # Bass slightly quieter
        'synth': -2.0,     # Synth quieter
        'vocals': 1.0,     # Vocals slightly louder
    }
    
    gains = {k: v for k, v in gains.items() if k in available_stems}
    
    print("\nStarting mix...")
    print("-" * 60)
    
    mixed_audio = mixer.mix_stems(available_stems, gains=gains)
    
    print("-" * 60)
    
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "quick_mix.wav")
    
    mixer.save_audio(mixed_audio, output_file)
    
    print()
    print("=" * 60)
    print("Mix complete!")
    print(f"Output saved to: {output_file}")
    print("=" * 60)
    print()
    print("Tip: Edit this script to adjust gain, panning, and EQ settings")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcess cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nMake sure you have installed all dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)



