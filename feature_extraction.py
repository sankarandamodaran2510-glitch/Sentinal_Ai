import numpy as np
from scipy.stats import kurtosis
from scipy.fft import fft, fftfreq

def extract_features(signal, fs=20480):
    """
    Extracts time and frequency-domain features from a single signal segment/channel.
    Matches the exact mathematical definitions required for the NASA IMS dataset.
    """
    N = len(signal)
    
    # --- Time-Domain Features ---
    rms_val = np.sqrt(np.mean(signal**2))
    variance_val = np.var(signal)
    kurtosis_val = kurtosis(signal)
    
    # --- Frequency-Domain Features (FFT) ---
    fft_raw = fft(signal)
    frequencies = fftfreq(N, 1/fs)
    
    # Keep only the positive half of the frequency spectrum
    positive_indices = frequencies >= 0
    pos_freqs = frequencies[positive_indices]
    magnitudes = np.abs(fft_raw[positive_indices])
    
    # Locate peak magnitude and its matching frequency in Hz
    peak_idx = np.argmax(magnitudes)
    peak_freq_hz = pos_freqs[peak_idx]
    peak_mag_val = magnitudes[peak_idx]
    peak_mag_avg = np.mean(magnitudes)
    
    # Return flat keys expected by the aggregation phase
    return {
        "RMS_mean": rms_val,
        "RMS_max": rms_val,  # Seed value; will be accurately maxed during aggregation
        "Variance_mean": variance_val,
        "Kurtosis_mean": kurtosis_val,
        "PeakFreq_mean": peak_freq_hz,
        "PeakMag_mean": peak_mag_avg,
        "PeakMag_max": peak_mag_val
    }

def aggregate_features(channel_features):
    """
    Aggregates windowed chunk features into global metrics across channels/segments.
    """
    return {
        "RMS_mean": np.mean([f["RMS_mean"] for f in channel_features]),
        "RMS_max": np.max([f["RMS_max"] for f in channel_features]), # True maximum windowed energy
        "Variance_mean": np.mean([f["Variance_mean"] for f in channel_features]),
        "Kurtosis_mean": np.mean([f["Kurtosis_mean"] for f in channel_features]),
        "PeakFreq_mean": np.mean([f["PeakFreq_mean"] for f in channel_features]),
        "PeakMag_mean": np.mean([f["PeakMag_mean"] for f in channel_features]),
        "PeakMag_max": np.max([f["PeakMag_max"] for f in channel_features])
    }