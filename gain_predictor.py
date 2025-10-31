import numpy as np
import librosa
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class GainPredictor:
    def __init__(self, n_mfcc: int = 13):
        self.n_mfcc = n_mfcc
        self.feature_weights = self._initialize_weights()
    
    def _initialize_weights(self) -> Dict[str, float]:
        return {
            'rms_energy': 0.30,    
            'spectral_centroid': 0.15, 
            'spectral_rolloff': 0.10,   
            'zero_crossing': 0.05,    
            'spectral_bandwidth': 0.10, 
            'mfcc_mean': 0.20,         
            'dynamic_range': 0.10      
        }
    
    def extract_features(self, audio: np.ndarray, sr: int) -> np.ndarray:
        if len(audio.shape) > 1:
            audio_mono = np.mean(audio, axis=1)
        else:
            audio_mono = audio
        
        features = []
        
        # RMS Energy (loudness indicator)
        rms = np.mean(librosa.feature.rms(y=audio_mono, frame_length=2048, hop_length=512)[0])
        features.append(rms)
        
        # Spectral Centroid (brightness)
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_mono, sr=sr)[0])
        # Normalize by max frequency
        spectral_centroid_norm = spectral_centroid / (sr / 2)
        features.append(spectral_centroid_norm)
        
        # Spectral Rolloff (energy distribution)
        rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio_mono, sr=sr)[0])
        rolloff_norm = rolloff / (sr / 2)
        features.append(rolloff_norm)
        
        # Zero Crossing Rate (texture)
        zcr = np.mean(librosa.feature.zero_crossing_rate(audio_mono)[0])
        features.append(zcr)
        
        # Spectral Bandwidth (frequency spread)
        bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=audio_mono, sr=sr)[0])
        bandwidth_norm = bandwidth / (sr / 2)
        features.append(bandwidth_norm)
        
        # MFCC features (timbral characteristics)
        mfccs = librosa.feature.mfcc(y=audio_mono, sr=sr, n_mfcc=self.n_mfcc)
        mfcc_mean = np.mean(mfccs, axis=1)
        features.extend(mfcc_mean.tolist())
        
        # Dynamic range (consistency)
        dynamic_range = np.std(audio_mono) / (np.mean(np.abs(audio_mono)) + 1e-8)
        features.append(dynamic_range)
        
        return np.array(features)
    
    def compute_relative_gain(self, features: np.ndarray, stem_type: str) -> float:
        """
        Compute gain adjustment based on features and stem type.
        
        This implements a simple rule-based system. In production, this would be
        replaced with a trained neural network.
        
        Args:
            features: Feature vector
            stem_type: Type of stem (drums, bass, vocals, synth)
            
        Returns:
            Suggested gain in dB
        """
        # Stem type specific adjustments
        type_baselines = {
            'drums': -2.0,      # Drums typically need slight attenuation
            'bass': -1.5,       # Bass needs control to avoid mud
            'vocals': 0.0,      # Vocals at reference
            'synth': -2.5,      # Synths often need attenuation
        }
        baseline = type_baselines.get(stem_type, -1.5)
        
        # Feature-based adjustments
        rms = features[0]
        spectral_centroid = features[1]
        dynamic_range = features[-1]
        
        # Loudness adjustment: quieter stems need boost
        loudness_gain = np.clip((0.5 - rms) * 10, -3, 3)
        
        # Brightness adjustment: very bright or very dark need different handling
        brightness_gain = 0
        if stem_type == 'vocals':
            brightness_gain = np.clip((spectral_centroid - 0.15) * 5, -2, 2)
        
        # Dynamic range adjustment: overly compressed tracks need attenuation
        compression_gain = np.clip((0.5 - dynamic_range) * 2, -2, 1)
        
        # Combine adjustments
        total_gain = baseline + loudness_gain + brightness_gain + compression_gain
        
        # Clamp to reasonable range
        return np.clip(total_gain, -6, 6)
    
    def predict_gains(self, stems_data: Dict[str, np.ndarray], 
                     stem_paths: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """
        Predict optimal gain values for multiple stems.
        
        Args:
            stems_data: Dictionary of stem names to audio data
            stem_paths: Optional dictionary of file paths (used for sample rate)
            
        Returns:
            Dictionary of stem names to suggested gain values in dB
        """
        print("\nAnalyzing stems for optimal gain settings...")
        
        predicted_gains = {}
        
        for name, audio in stems_data.items():
            # Get sample rate from paths if available, otherwise use default
            sr = 44100
            if stem_paths and hasattr(self, 'sr'):
                sr = self.sr
            
            # Extract features
            features = self.extract_features(audio, sr)
            
            # Predict gain
            gain = self.compute_relative_gain(features, name)
            predicted_gains[name] = float(gain)
            
            print(f"  {name}: {gain:.2f} dB (RMS: {features[0]:.4f}, "
                  f"Centroid: {features[1]:.4f})")
        
        return predicted_gains


class CNNGainPredictor(GainPredictor):
    """
    CNN-based gain predictor that uses a simple neural network.
    
    This is a prototype implementation. For production use, you would:
    1. Collect training data (stems + expert mixing decisions)
    2. Train a proper CNN on spectrograms or mel-spectrograms
    3. Use the trained model for inference
    """
    
    def __init__(self, n_mfcc: int = 13, model_path: Optional[str] = None):
        """
        Initialize CNN-based predictor.
        
        Args:
            n_mfcc: Number of MFCC coefficients
            model_path: Path to trained model (None uses rule-based fallback)
        """
        super().__init__(n_mfcc)
        self.model_path = model_path
        self.model = None
        
        if model_path:
            self._load_model(model_path)
    
    def _load_model(self, model_path: str):
        """Load a trained model (placeholder for future implementation)."""
        # In production, this would load a saved Keras/TensorFlow model
        pass
    
    def extract_spectral_features(self, audio: np.ndarray, sr: int, 
                                   n_fft: int = 2048, hop_length: int = 512) -> np.ndarray:
        """
        Extract mel-spectrogram features for CNN input.
        
        Args:
            audio: Audio data
            sr: Sample rate
            n_fft: FFT window size
            hop_length: Hop length
            
        Returns:
            Feature array suitable for CNN input
        """
        # Convert to mono
        if len(audio.shape) > 1:
            audio_mono = np.mean(audio, axis=1)
        else:
            audio_mono = audio
        
        # Extract mel-spectrogram
        mel_spec = librosa.feature.melspectrogram(
            y=audio_mono, 
            sr=sr,
            n_fft=n_fft,
            hop_length=hop_length,
            n_mels=128
        )
        
        # Convert to log scale
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        # Flatten and add statistical features
        features = []
        
        # Mean and std of mel-spectrogram
        features.append(np.mean(mel_spec_db))
        features.append(np.std(mel_spec_db))
        
        # Spectral features (reuse from parent)
        traditional_features = self.extract_features(audio, sr)
        features.extend(traditional_features.tolist())
        
        return np.array(features)
    
    def predict_gains_cnn(self, stems_data: Dict[str, np.ndarray],
                          stem_paths: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """
        Predict gains using CNN approach.
        
        Args:
            stems_data: Dictionary of stem names to audio data
            stem_paths: Optional file paths
            
        Returns:
            Dictionary of predicted gains
        """
        if self.model is None:
            # Fallback to rule-based approach
            print("No trained model available, using rule-based prediction...")
            return self.predict_gains(stems_data, stem_paths)
        
        print("\nUsing CNN model for gain prediction...")
        
        predicted_gains = {}
        sr = 44100
        
        for name, audio in stems_data.items():
            # Extract CNN features
            features = self.extract_spectral_features(audio, sr)
            
            # Reshape for model input
            features_reshaped = features.reshape(1, -1)
            
            # Predict (placeholder - would use self.model.predict() in production)
            # For now, use rule-based approach
            gain = self.compute_relative_gain(self.extract_features(audio, sr), name)
            predicted_gains[name] = float(gain)
            
            print(f"  {name}: {gain:.2f} dB")
        
        return predicted_gains


def create_smart_mix_stems(
    stems: Dict[str, str],
    mixer,
    use_cnn: bool = False,
    sample_rate: int = 44100
) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Create a mix using automatic gain prediction.
    
    Args:
        stems: Dictionary of stem names to file paths
        mixer: StemMixer instance
        use_cnn: Whether to use CNN predictor (vs rule-based)
        sample_rate: Sample rate
        
    Returns:
        Tuple of (mixed audio, predicted gains)
    """
    # Load all stems first
    stem_data = {}
    stem_sample_rates = {}
    max_length = 0
    
    for name, file_path in stems.items():
        print(f"Loading {name} from {file_path}...")
        audio, sr = mixer.load_audio(file_path)
        stem_sample_rates[name] = sr
        audio = mixer.resample_audio(audio, sr, sample_rate)
        stem_data[name] = audio
        max_length = max(max_length, len(audio))
    
    # Initialize gain predictor
    if use_cnn:
        predictor = CNNGainPredictor()
    else:
        predictor = GainPredictor()
    
    # Set sample rate for predictor
    predictor.sr = sample_rate
    
    # Predict gains
    predicted_gains = predictor.predict_gains(stem_data)
    
    # Apply predicted gains and mix
    mixed_audio = None
    
    for name, audio in stem_data.items():
        print(f"\nProcessing {name}...")
        
        # Normalize length
        audio = mixer.normalize_length(audio, max_length)
        
        # Apply predicted gain
        gain = predicted_gains[name]
        if gain != 0.0:
            audio = mixer.apply_gain(audio, gain)
            print(f"  Applied gain: {gain:.2f} dB")
        
        # Mix with other stems
        if mixed_audio is None:
            mixed_audio = audio
        else:
            mixed_audio = mixed_audio + audio
    
    # Normalize output
    max_val = np.abs(mixed_audio).max()
    if max_val > 1.0:
        print(f"\nNormalizing output (max value: {max_val:.3f})")
        mixed_audio = mixed_audio / max_val
    
    return mixed_audio, predicted_gains

