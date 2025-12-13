from audio_mixer import StemMixer
import os
import sys


def main():
    print("=" * 60)
    print("Audio Stem Mixer - Auto-Gain Quick Start")
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
    
    print("Creating mixer with automatic gain prediction...")
    mixer = StemMixer(sample_rate=44100)
    
    # Optional: Ask user for CNN or rule-based
    print("\nChoose prediction method:")
    print("  1. Rule-based (fast, good for most cases)")
    print("  2. CNN-based (experimental, more advanced)")
    choice = input("Enter choice (1 or 2, default=1): ").strip()
    
    use_cnn = False
    if choice == "2":
        use_cnn = True
        print("\nUsing CNN-based prediction...")
    else:
        print("\nUsing rule-based prediction...")
    
    # Start mixing with auto-gain
    print("\nStarting intelligent mix...")
    print("-" * 60)
    
    mixed_audio = mixer.mix_stems(
        available_stems, 
        auto_gain=True,
        use_cnn=use_cnn
    )
    
    print("-" * 60)
    
    # Save output
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "auto_gain_mix.wav")
    
    mixer.save_audio(mixed_audio, output_file)
    
    print()
    print("=" * 60)
    print("Intelligent mix complete!")
    print(f"Output saved to: {output_file}")
    print("=" * 60)
    print()
    print("The AI analyzed your stems and automatically adjusted gain levels")
    print("for optimal balance. You can still fine-tune with manual settings.")


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
        print("\nAlso ensure gain_predictor.py is in the same directory.")
        sys.exit(1)


