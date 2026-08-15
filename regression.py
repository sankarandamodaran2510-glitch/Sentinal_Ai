import numpy as np
from sklearn.linear_model import LinearRegression

def estimate_remaining_useful_life(feature_df, minutes_per_file=10, failure_threshold=0.45):
    
    # We need at least 3 historical points to establish a reliable direction/trend
    if len(feature_df) < 3:
        return {
            "status": "insufficient_data",
            "message": "💡 Upload 3 or more historical sequential files to activate Time-to-Shutdown predictions."
        }
        
    # 1. Setup the time axis (X) in minutes based on file sequence
    X = np.arange(len(feature_df)).reshape(-1, 1) * minutes_per_file
    
    # 2. Target vector (y) tracking the maximum vibration energy
    y = feature_df["RMS_max"].values
    
    # 3. Fit the linear model
    lr_model = LinearRegression()
    lr_model.fit(X, y)
    
    # Get the slope (rate of degradation per minute)
    slope = lr_model.coef_[0]
    current_rms = y[-1]
    
    # 4. Evaluate the degradation trend
    if current_rms >= failure_threshold:
        return {
            "status": "failed",
            "message": "🚨 Imminent Failure Level Reached! Shutdown threshold breached."
        }
        
    if slope > 0:
        # Minutes remaining = (Threshold - Current Value) / Slope per minute
        minutes_to_shutdown = (failure_threshold - current_rms) / slope
        
        if minutes_to_shutdown > 0:
            return {
                "status": "degrading",
                "minutes_remaining": minutes_to_shutdown,
                "degradation_rate_per_hour": slope * 60,
                "message": f"⏳ **Estimated Time to Shutdown:** {minutes_to_shutdown:.1f} minutes"
            }
            
    # If slope is negative or zero, the bearing is stable in this time window
    return {
        "status": "stable",
        "message": "✅ **Stable Trend:** No progressive degradation trend detected in this window."
    }