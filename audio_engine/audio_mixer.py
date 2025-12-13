import numpy as np
import soundfile as sf
from typing import Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

try:
    from .gain_predictor import GainPredictor, CNNGainPredictor
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
    
    def mix_stems(
        self,
        stems: Dict[str, str],
        gains: Optional[Dict[str, float]] = None,
        pans: Optional[Dict[str, float]] = None,
        normalize_output: bool = True,
        auto_gain: bool = False,
        use_cnn: bool = False
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        gains = gains or {}
        pans = pans or {}
        
        if auto_gain and HAS_PREDICTOR:
            print("\n=== AUTOMATIC GAIN PREDICTION ENABLED ===")
            return self._mix_with_auto_gain(
                stems, pans, normalize_output, use_cnn, gains
            )
        
        stem_data = {}
        max_length = 0
        
        for name, file_path in stems.items():
            print(f"Loading {name} from {file_path}...")
            audio, sr = self.load_audio(file_path)
            audio = self.resample_audio(audio, sr, self.sample_rate)
            stem_data[name] = audio
            max_length = max(max_length, len(audio))
        
        mixed_audio = None
        final_gains = {}
        
        for name, audio in stem_data.items():
            print(f"Processing {name}...")
            
            audio = self.normalize_length(audio, max_length)
            
            gain = gains.get(name, 0.0)
            final_gains[name] = gain
            if gain != 0.0:
                audio = self.apply_gain(audio, gain)
                print(f"  Applied gain: {gain} dB")
            
            pan = pans.get(name, 0.0)
            if pan != 0.0:
                audio = self.apply_pan(audio, pan)
                print(f"  Applied pan: {pan} (Shape: {audio.shape})")
            
            if mixed_audio is None:
                mixed_audio = audio
            else:
                mixed_audio = mixed_audio + audio
        
        if normalize_output and mixed_audio is not None:
            max_val = np.abs(mixed_audio).max()
            if max_val > 1.0:
                print(f"Normalizing output (max value: {max_val:.3f})")
                mixed_audio = mixed_audio / max_val
        
        return mixed_audio, final_gains
    
    def _create_smart_mix_stems(self, stems: Dict[str, str], use_cnn: bool) -> Tuple[np.ndarray, Dict[str, float]]:
        stem_data = {}
        max_length = 0
        
        for name, file_path in stems.items():
            print(f"Loading {name} from {file_path}...")
            audio, sr = self.load_audio(file_path)
            audio = self.resample_audio(audio, sr, self.sample_rate)
            stem_data[name] = audio
            max_length = max(max_length, len(audio))
            
        if use_cnn:
            predictor = CNNGainPredictor()
        else:
            predictor = GainPredictor()
        predictor.sr = self.sample_rate
        
        if use_cnn:
             predicted_gains = predictor.predict_gains_cnn(stem_data)
        else:
             predicted_gains = predictor.predict_gains(stem_data)
             
        return None, predicted_gains


    def _mix_with_auto_gain(
        self,
        stems: Dict[str, str],
        pans: Dict[str, float],
        normalize_output: bool,
        use_cnn: bool,
        manual_gains: Dict[str, float]
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        
        _, predicted_gains = self._create_smart_mix_stems(stems, use_cnn)
        
        print("\n=== PREDICTED GAIN SUMMARY ===")
        for name, gain in predicted_gains.items():
            print(f"  {name}: {gain:.2f} dB")
            
        return self.mix_stems(
            stems=stems,
            gains=predicted_gains,
            pans=pans,
            normalize_output=normalize_output,
            auto_gain=False, 
            use_cnn=False
        )
    
    def save_audio(self, audio: np.ndarray, output_path: str):
        print(f"Saving audio with shape: {audio.shape}")
        sf.write(output_path, audio, self.sample_rate)
        print(f"Saved mixed audio to {output_path}")
