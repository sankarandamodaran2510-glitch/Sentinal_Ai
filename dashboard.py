import streamlit as st
import pandas as pd
import numpy as np
import joblib
from scipy.stats import kurtosis
from scipy.fft import fft
from fpdf import FPDF

#feature extraction
from feature_extraction import *

#predicting the shutdown time
from regression import *

#report generation
from report import *


st.set_page_config(
    page_title="Sentinel AI",
    page_icon="⚙️",
    layout="wide"
)

st.title("Sentinel AI")
st.subheader("Bearing Health Monitoring System")


#panel to upload sensor readings files
uploaded_files = st.sidebar.file_uploader(
    "Choose vibration files",
    accept_multiple_files=True
)

#loading models
iso_scaler = joblib.load("scaler.pkl")
iso_model = joblib.load("iso_model.pkl")
health_scaler = joblib.load("health_scaler.pkl")

if uploaded_files:

    all_machine_features = []

    for file in uploaded_files:

        df = pd.read_csv(
            file,
            sep="\t",
            header=None
        )

        channel_features = []

        for channel in range(4):

            signal = df[channel].values

            features = extract_features(signal)

            channel_features.append(features)

        machine_features = aggregate_features(
            channel_features
        )

        all_machine_features.append(
            machine_features
        )


    # Feature DataFrame
    feature_df = pd.DataFrame(
        all_machine_features
    )

    # Health Score Calculation
    health_features = [
    "RMS_max",
    "Variance_mean",
    "Kurtosis_mean",
    "PeakMag_max"
    ]

    health_normalized = health_scaler.transform(
        feature_df[health_features]
    )

    feature_df["DegradationScore"] = (
        health_normalized.mean(axis=1)
    )

    feature_df["HealthScore"] = (
        100 * (
            1 - feature_df["DegradationScore"]
        )
    ).round(2)


    # Isolation Forest
    X_scaled = iso_scaler.transform(
        feature_df.iloc[:, :7]
    )

    feature_df["Anomaly"] = (
        iso_model.predict(X_scaled)
    )

    feature_df["AnomalyScore"] = (
        -iso_model.decision_function(X_scaled)
    )

    # Latest Reading only if freqyency is > 0 bcz dead machine don't have frequency
    
    latest = feature_df.iloc[-1]
    if latest["PeakFreq_mean"] < 10:

        st.error(
            "🚨 Machine Stopped / No Signal"
        )

    else:

        # Health logic

        health = latest["HealthScore"]

        if health > 80:
            status = "Healthy"

        elif health > 50:
            status = "Warning"
        
        elif health > 30:
            status = "Severe"

        else:
            status = "Critical"

       

        # Dashboard layout split into columns for cleaner visual metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Machine Health",
                f"{health:.1f}%"
            )
            st.write(f"### Status : {status}")
            st.write(f"### Peak Frequency : {latest['PeakFreq_mean']:.0f} Hz")

        with col2:
            if latest["Anomaly"] == -1:
                st.error("⚠️ Anomaly Detected")
            else:
                st.success("Anomaly = normal")

        st.subheader("Health Trend")
        st.line_chart(
            feature_df["HealthScore"]
        ) 

        # --- INTEGRATING THE REGRESSION FILE ---
        st.subheader("🔮 Predictive Prognostics (RUL Estimation)")
        
        # Assuming your regression function inside 'regression.py' is named 'estimate_remaining_useful_life'
        # Adjust name here if you called your function something else (e.g., predict_shutdown(feature_df))
        prognostics_results = estimate_remaining_useful_life(feature_df)
        
        # Render the UI based on the output dictionary flags from your regression script
        if prognostics_results["status"] == "degrading":
            st.warning(prognostics_results["message"])
            st.info(f"📈 **Degradation Rate:** {prognostics_results['degradation_rate_per_hour']:.4f} g increase per hour")
        elif prognostics_results["status"] == "stable":
            st.success(prognostics_results["message"])
        elif prognostics_results["status"] == "failed":
            st.error(prognostics_results["message"])
        else:
            st.info(prognostics_results["message"])
       

       

        st.subheader(
            "Extracted Features"
        )

        st.dataframe(
            feature_df
        )

        #automated report generation
        st.subheader("📋 Maintenance Dispatch")
        
        # Assemble the current state metrics into a clean dictionary
        latest_metrics_payload = {
            "Status": status,
            "HealthScore": health,
            "RMS_mean": latest["RMS_mean"],
            "RMS_max": latest["RMS_max"],
            "Kurtosis_mean": latest["Kurtosis_mean"],
            "PeakFreq_mean": latest["PeakFreq_mean"],
            "PeakMag_max": latest["PeakMag_max"]
        }
        
        # Generate the PDF byte data
        pdf_bytes = generate_pdf_report(latest_metrics_payload, prognostics_results)
        
        # Native Streamlit download widget
        st.download_button(
            label="📥 Download Diagnostic PDF Report",
            data=bytes(pdf_bytes),
            file_name=f"Sentinel_AI_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )








