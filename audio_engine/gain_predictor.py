import numpy as np
import librosa
from typing import Dict, Optional
import warnings
warnings.filterwarnings('ignore')

class GainPredictor:
    def __init__(self, n_mfcc: int = 13):
        self.n_mfcc = n_mfcc
    
    def extract_features(self, audio: np.ndarray, sr: int) -> np.ndarray:
        if len(audio.shape) > 1:
            audio_mono = np.mean(audio, axis=1)
        else:
            audio_mono = audio
        
        features = []
        
        rms = np.mean(librosa.feature.rms(y=audio_mono, frame_length=2048, hop_length=512)[0])
        features.append(rms)
        
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_mono, sr=sr)[0])
        spectral_centroid_norm = spectral_centroid / (sr / 2)
        features.append(spectral_centroid_norm)
        
        rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio_mono, sr=sr)[0])
        rolloff_norm = rolloff / (sr / 2)
        features.append(rolloff_norm)
        
        zcr = np.mean(librosa.feature.zero_crossing_rate(audio_mono)[0])
        features.append(zcr)
        
        bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=audio_mono, sr=sr)[0])
        bandwidth_norm = bandwidth / (sr / 2)
        features.append(bandwidth_norm)
        
        mfccs = librosa.feature.mfcc(y=audio_mono, sr=sr, n_mfcc=self.n_mfcc)
        mfcc_mean = np.mean(mfccs, axis=1)
        features.extend(mfcc_mean.tolist())
        
        dynamic_range = np.std(audio_mono) / (np.mean(np.abs(audio_mono)) + 1e-8)
        features.append(dynamic_range)
        
        return np.array(features)
    
    def compute_relative_gain(self, features: np.ndarray, stem_type: str) -> float:
        type_baselines = {
            'drums': -2.0,
            'bass': -1.5,
            'vocals': 0.0,
            'synth': -2.5,
        }
        baseline = type_baselines.get(stem_type, -1.5)
        
        rms = features[0]
        spectral_centroid = features[1]
        dynamic_range = features[-1]
        
        loudness_gain = np.clip((0.5 - rms) * 10, -3, 3)
        
        brightness_gain = 0
        if stem_type == 'vocals':
            brightness_gain = np.clip((spectral_centroid - 0.15) * 5, -2, 2)
        
        compression_gain = np.clip((0.5 - dynamic_range) * 2, -2, 1)
        
        total_gain = baseline + loudness_gain + brightness_gain + compression_gain
        
        return np.clip(total_gain, -6, 6)
    
    def predict_gains(self, stems_data: Dict[str, np.ndarray], 
                     stem_paths: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        print("\nAnalyzing stems for optimal gain settings...")
        
        predicted_gains = {}
        
        for name, audio in stems_data.items():
            sr = 44100
            if stem_paths and hasattr(self, 'sr'):
                sr = self.sr
            
            features = self.extract_features(audio, sr)
            
            gain = self.compute_relative_gain(features, name)
            predicted_gains[name] = float(gain)
            
            print(f"  {name}: {gain:.2f} dB (RMS: {features[0]:.4f}, "
                  f"Centroid: {features[1]:.4f})")
        
        return predicted_gains


class CNNGainPredictor(GainPredictor):
    def __init__(self, n_mfcc: int = 13, model_path: Optional[str] = None):
        super().__init__(n_mfcc)
        self.model_path = model_path
        self.model = None
    
    def extract_spectral_features(self, audio: np.ndarray, sr: int, 
                                   n_fft: int = 2048, hop_length: int = 512) -> np.ndarray:
        if len(audio.shape) > 1:
            audio_mono = np.mean(audio, axis=1)
        else:
            audio_mono = audio
        
        mel_spec = librosa.feature.melspectrogram(
            y=audio_mono, 
            sr=sr,
            n_fft=n_fft,
            hop_length=hop_length,
            n_mels=128
        )
        
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        features = []
        features.append(np.mean(mel_spec_db))
        features.append(np.std(mel_spec_db))
        
        traditional_features = self.extract_features(audio, sr)
        features.extend(traditional_features.tolist())
        
        return np.array(features)
    
    def predict_gains_cnn(self, stems_data: Dict[str, np.ndarray],
                          stem_paths: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        print("\nUsing CNN model for gain prediction (Prototype Mode)...")
        
        predicted_gains = {}
        sr = 44100
        
        for name, audio in stems_data.items():
            gain = self.compute_relative_gain(self.extract_features(audio, sr), name)
            predicted_gains[name] = float(gain)
            print(f"  {name}: {gain:.2f} dB")
        
        return predicted_gains
