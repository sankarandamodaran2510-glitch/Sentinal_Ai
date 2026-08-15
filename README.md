# Sentinel AI

## Bearing Health Monitoring System

Sentinel AI is an AI-powered predictive maintenance system designed to monitor the health of rotating machinery using vibration sensor data.

The system processes raw multi-channel bearing vibration signals, extracts meaningful time-domain and frequency-domain features, detects anomalous operating behavior using Isolation Forest, calculates a degradation score and machine health score, and presents the results through an interactive Streamlit dashboard.

---

## Project Overview

Industrial bearings generate vibration signals during operation. Changes in these signals can indicate abnormal behavior or progressive degradation.

Sentinel AI converts raw vibration measurements into meaningful features that can be analyzed by machine learning models.

The overall pipeline is:

Raw Vibration Signals
        ↓
Signal Processing & Feature Extraction
        ↓
7 Engineered Bearing Features
        ↓
StandardScaler
        ↓
Isolation Forest
        ↓
Anomaly Detection

Selected Degradation Features
        ↓
MinMaxScaler
        ↓
Degradation Score
        ↓
Health Score
        ↓
Streamlit Dashboard

---

## Features

- Multi-channel vibration signal processing
- Time-domain feature extraction
- Frequency-domain analysis using FFT
- Four-channel sensor aggregation
- Isolation Forest based anomaly detection
- Degradation score calculation
- Machine health score calculation
- Health trend visualization
- Multiple raw vibration file upload
- Interactive Streamlit dashboard

---

## Feature Extraction

Each raw vibration file contains four sensor channels.

The system extracts features from each channel and then aggregates them into machine-level features.

The final feature set contains:

- RMS_mean
- RMS_max
- Variance_mean
- Kurtosis_mean
- PeakFreq_mean
- PeakMag_mean
- PeakMag_max

### Time-domain features

RMS represents the overall vibration energy of the signal.

Variance measures the variation in the vibration signal.

Kurtosis helps identify impulsive or highly peaked vibration behavior.

### Frequency-domain features

FFT is used to transform the vibration signal from the time domain into the frequency domain.

Peak frequency represents the dominant frequency component.

Peak magnitude represents the magnitude of the dominant frequency component.

---

## Machine Learning

Sentinel AI uses Isolation Forest for anomaly detection.

Isolation Forest was selected because the vibration dataset does not provide a straightforward labelled healthy/fault classification for every observation.

The model learns the structure of the feature space and identifies observations that differ significantly from the learned operating pattern.

### Model pipeline

7 engineered features
        ↓
StandardScaler
        ↓
Isolation Forest

The trained objects are saved using Joblib:

- `scaler.pkl` — StandardScaler used before Isolation Forest prediction
- `iso_model.pkl` — trained Isolation Forest model

---

## Health Score

Anomaly detection and health scoring serve different purposes.

The Isolation Forest determines whether a vibration observation is anomalous.

The HealthScore provides a continuous indication of machine condition.

Selected degradation-related features are normalized using a separate MinMaxScaler:

- RMS_max
- Variance_mean
- Kurtosis_mean
- PeakMag_max

The normalized values are combined to calculate the DegradationScore.

The HealthScore is then calculated as:

HealthScore = 100 × (1 − DegradationScore)

The health preprocessing object is saved as:

`health_scaler.pkl`

This allows the same transformation to be applied to new vibration data in the dashboard.

---

## Deployment

The project separates model development from deployment.

### Development

The `SentinelAI.ipynb` notebook was used for:

- Exploring the raw vibration signals
- Visualizing vibration behavior
- Performing FFT analysis
- Extracting features
- Creating the processed bearing feature dataset
- Developing the anomaly detection pipeline
- Developing the health scoring approach
- Training and saving the required preprocessing objects and model

### Deployment

The Streamlit dashboard accepts new raw vibration files.

The dashboard does not retrain the model.

Instead, each uploaded raw file follows the same feature extraction process used during development:

New Raw Vibration File
        ↓
feature_extraction.py
        ↓
7 Engineered Features
        ↓
scaler.pkl
        ↓
iso_model.pkl
        ↓
Anomaly Prediction

The health features are separately processed using `health_scaler.pkl`.

---

## Why Feature Extraction Is Repeated in the Dashboard

The trained Isolation Forest does not operate directly on raw vibration samples.

It was trained using the seven engineered features.

Therefore, when a new raw vibration file is uploaded, the dashboard must convert that raw signal into the same seven features before passing it to the trained model.

`feature_extraction.py` contains the reusable feature extraction functions.

This allows the same processing pipeline to be used for new vibration data during inference.

---

## Project Structure

```text
Sentinel-AI/
│
├── dashboard.py
├── feature_extraction.py
│
├── models/
│   ├── scaler.pkl
│   ├── health_scaler.pkl
│   └── iso_model.pkl
│
├── notebooks/
│   └── SentinelAI.ipynb
│
├── data/
│   └── README.md
│
├── screenshots/
│   └── dashboard.png
│
├── requirements.txt
├── .gitignore
└── README.md
