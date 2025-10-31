import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

try:
    from gain_predictor import GainPredictor, CNNGainPredictor, create_smart_mix_stems
    HAS_PREDICTOR = True
except ImportError:
    HAS_PREDICTOR = False


class StemMixer:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        data, sr = sf.read(file_path)
        
        if len(data.shape) == 1:
            data = np.column_stack([data, data])
        
        return data, sr
    
    def resample_audio(self, audio: np.ndarray, sr_original: int, sr_target: int) -> np.ndarray:
        import librosa
        
        if sr_original == sr_target:
            return audio
        
        resampled = np.zeros((int(len(audio) * sr_target / sr_original), audio.shape[1]))
        for ch in range(audio.shape[1]):
            resampled[:, ch] = librosa.resample(
                audio[:, ch], 
                orig_sr=sr_original, 
                target_sr=sr_target
            )
        
        return resampled
    
    def normalize_length(self, audio: np.ndarray, target_length: int) -> np.ndarray:
        current_length = len(audio)
        
        if current_length > target_length:
            return audio[:target_length]
        elif current_length < target_length:
            padding = np.zeros((target_length - current_length, audio.shape[1]))
            return np.vstack([audio, padding])
        else:
            return audio
    
    def apply_gain(self, audio: np.ndarray, gain_db: float) -> np.ndarray:
        gain_linear = 10 ** (gain_db / 20.0)
        return audio * gain_linear
    
    def apply_pan(self, audio: np.ndarray, pan: float) -> np.ndarray:
        if audio.shape[1] != 2:
            return audio
        
        left_gain = np.cos((pan + 1) * np.pi / 4)
        right_gain = np.sin((pan + 1) * np.pi / 4)
        
        audio[:, 0] *= left_gain
        audio[:, 1] *= right_gain
        
        return audio
    
    def apply_high_pass(self, audio: np.ndarray, cutoff: float, sample_rate: int) -> np.ndarray:
        from scipy import signal
        
        nyquist = sample_rate / 2
        normalized_cutoff = cutoff / nyquist
        b, a = signal.butter(4, normalized_cutoff, btype='high')
        
        filtered = np.copy(audio)
        for ch in range(audio.shape[1]):
            filtered[:, ch] = signal.filtfilt(b, a, audio[:, ch])
        
        return filtered
    
    def apply_low_pass(self, audio: np.ndarray, cutoff: float, sample_rate: int) -> np.ndarray:
        from scipy import signal
        
        nyquist = sample_rate / 2
        normalized_cutoff = cutoff / nyquist
        b, a = signal.butter(4, normalized_cutoff, btype='low')
        
        filtered = np.copy(audio)
        for ch in range(audio.shape[1]):
            filtered[:, ch] = signal.filtfilt(b, a, audio[:, ch])
        
        return filtered
    
    def mix_stems(
        self,
        stems: Dict[str, str],
        gains: Optional[Dict[str, float]] = None,
        pans: Optional[Dict[str, float]] = None,
        high_pass_cutoffs: Optional[Dict[str, float]] = None,
        low_pass_cutoffs: Optional[Dict[str, float]] = None,
        normalize_output: bool = True,
        auto_gain: bool = False,
        use_cnn: bool = False
    ) -> np.ndarray:
        gains = gains or {}
        pans = pans or {}
        high_pass_cutoffs = high_pass_cutoffs or {}
        low_pass_cutoffs = low_pass_cutoffs or {}
        
        # Auto-gain prediction if requested
        if auto_gain and HAS_PREDICTOR:
            print("\n=== AUTOMATIC GAIN PREDICTION ENABLED ===")
            return self._mix_with_auto_gain(
                stems, pans, high_pass_cutoffs, low_pass_cutoffs, 
                normalize_output, use_cnn, gains
            )
        
        stem_data = {}
        max_length = 0
        
        for name, file_path in stems.items():
            print(f"Loading {name} from {file_path}...")
            audio, sr = self.load_audio(file_path)
            audio = self.resample_audio(audio, sr, self.sample_rate)
            stem_data[name] = audio
            max_length = max(max_length, len(audio))
        
        # Process each stem
        mixed_audio = None
        
        for name, audio in stem_data.items():
            print(f"Processing {name}...")
            
            # Normalize length
            audio = self.normalize_length(audio, max_length)
            
            # Apply gain
            gain = gains.get(name, 0.0)
            if gain != 0.0:
                audio = self.apply_gain(audio, gain)
                print(f"  Applied gain: {gain} dB")
            
            # Apply panning
            pan = pans.get(name, 0.0)
            if pan != 0.0:
                audio = self.apply_pan(audio, pan)
                print(f"  Applied pan: {pan}")
            
            # Apply high-pass filter
            hp_cutoff = high_pass_cutoffs.get(name)
            if hp_cutoff:
                audio = self.apply_high_pass(audio, hp_cutoff, self.sample_rate)
                print(f"  Applied high-pass filter: {hp_cutoff} Hz")
            
            # Apply low-pass filter
            lp_cutoff = low_pass_cutoffs.get(name)
            if lp_cutoff:
                audio = self.apply_low_pass(audio, lp_cutoff, self.sample_rate)
                print(f"  Applied low-pass filter: {lp_cutoff} Hz")
            
            # Mix with other stems
            if mixed_audio is None:
                mixed_audio = audio
            else:
                mixed_audio = mixed_audio + audio
        
        # Normalize output to prevent clipping
        if normalize_output and mixed_audio is not None:
            max_val = np.abs(mixed_audio).max()
            if max_val > 1.0:
                print(f"Normalizing output (max value: {max_val:.3f})")
                mixed_audio = mixed_audio / max_val
        
        return mixed_audio
    
    def _mix_with_auto_gain(
        self,
        stems: Dict[str, str],
        pans: Dict[str, float],
        high_pass_cutoffs: Dict[str, float],
        low_pass_cutoffs: Dict[str, float],
        normalize_output: bool,
        use_cnn: bool,
        manual_gains: Dict[str, float]
    ) -> np.ndarray:
        """Mix stems with automatic gain prediction."""
        if use_cnn:
            mixed_audio, predicted_gains = create_smart_mix_stems(
                stems, self, use_cnn=True, sample_rate=self.sample_rate
            )
        else:
            mixed_audio, predicted_gains = create_smart_mix_stems(
                stems, self, use_cnn=False, sample_rate=self.sample_rate
            )
        
        print("\n=== PREDICTED GAIN SUMMARY ===")
        for name, gain in predicted_gains.items():
            print(f"  {name}: {gain:.2f} dB")
        
        return mixed_audio
    
    def save_audio(self, audio: np.ndarray, output_path: str):
        sf.write(output_path, audio, self.sample_rate)
        print(f"Saved mixed audio to {output_path}")


def create_default_mix(
    stems_dir: str,
    output_path: str = "mixed_output.wav",
    sample_rate: int = 44100
) -> None:
    stems_dir = Path(stems_dir)
    
    # Look for common stem file names
    stem_files = {
        'drums': stems_dir / 'drums.wav',
        'bass': stems_dir / 'bass.wav',
        'synth': stems_dir / 'synth.wav',
        'vocals': stems_dir / 'vocals.wav',
    }
    
    # Only include stems that exist
    existing_stems = {name: str(path) for name, path in stem_files.items() if path.exists()}
    
    if not existing_stems:
        print("No stem files found!")
        return
    
    # Create mixer
    mixer = StemMixer(sample_rate=sample_rate)
    
    # Define mixing parameters
    gains = {
        'drums': 0.0,   # 0 dB
        'bass': -1.0,   # -1 dB
        'synth': -2.0,  # -2 dB
        'vocals': 1.0,  # +1 dB
    }
    
    pans = {
        'drums': 0.0,
        'bass': 0.0,
        'synth': 0.0,
        'vocals': 0.0,
    }
    
    # EQ cuts (optional)
    high_pass = {
        'vocals': 80.0,  # Remove low frequencies from vocals
        'synth': 60.0,
    }
    
    low_pass = {
        'drums': 10000.0,  # Reduce high frequencies in drums
    }
    
    # Mix stems
    print(f"Mixing {len(existing_stems)} stems...")
    mixed = mixer.mix_stems(
        stems=existing_stems,
        gains=gains,
        pans=pans,
        high_pass_cutoffs=high_pass,
        low_pass_cutoffs=low_pass
    )
    
    # Save output
    mixer.save_audio(mixed, output_path)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        stems_dir = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else "mixed_output.wav"
        create_default_mix(stems_dir, output_path)
    else:
        print("Usage: python audio_mixer.py <stems_directory> [output_file]")
        print("\nExample: python audio_mixer.py ./stems mixed_output.wav")

