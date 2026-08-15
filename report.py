import datetime
from fpdf import FPDF

class SentinelReport(FPDF):
    def header(self):
        # Top branding bar
        self.set_fill_color(30, 41, 59)  # Dark slate gray matching your dashboard theme
        self.rect(0, 0, 210, 30, 'F')
        
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'SENTINEL AI - ASSET DIAGNOSTIC REPORT', ln=True, align='L')
        
        self.set_font('Helvetica', 'I', 9)
        self.cell(0, 5, 'Automated Predictive Maintenance & Prognostics Engine', ln=True, align='L')
        self.ln(12) 

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()} | Confidential Industrial IoT Analytics', align='C')

def generate_pdf_report(latest_metrics, prognostics_results):
    """
    Generates a structured PDF byte-stream from the latest machine metrics.
    """
    pdf = SentinelReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- Metadata Section ---
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "1. System Metadata", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(95, 6, f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=False)
    pdf.cell(95, 6, f"Target Asset: Rexnord ZA-2115 Bearing (IMS Test 3)", ln=True)
    pdf.ln(5)
    
    # --- Health Status Alert Banner ---
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "2. Operational Health Status", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    
    status = latest_metrics["Status"]
    health_score = latest_metrics["HealthScore"]
    
    # Set colors dynamically based on alert level
    if status == "Healthy":
        pdf.set_fill_color(220, 252, 231)  # Light green
        pdf.set_text_color(21, 128, 61)    # Dark green
    elif status == "Warning":
        pdf.set_fill_color(254, 243, 199)  # Light amber
        pdf.set_text_color(180, 83, 9)     # Dark amber
    else:
        pdf.set_fill_color(254, 226, 226)  # Light red
        pdf.set_text_color(185, 28, 28)    # Dark red
        
    pdf.cell(0, 12, f"  CRITICAL METRIC STATUS: {status.upper()} ({health_score}% Health Score)", ln=True, fill=True)
    pdf.ln(5)
    
    # --- Extracted Signal Features Table ---
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "3. Key Telemetry Feature Dimensions", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    
    # Table Header
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(63, 7, " Feature Metric", border=1, fill=True)
    pdf.cell(63, 7, " Extracted Value", border=1, fill=True)
    pdf.cell(64, 7, " Baseline Reference", border=1, fill=True)
    pdf.ln()
    
    # Table Rows
    pdf.set_font('Helvetica', '', 10)
    features_to_print = [
        ("RMS_mean (Continuous Energy)", f"{latest_metrics['RMS_mean']:.4f} g", "< 0.0800 g"),
        ("RMS_max (Peak Shock Energy)", f"{latest_metrics['RMS_max']:.4f} g", "< 0.1200 g"),
        ("Kurtosis_mean (Signal Spikiness)", f"{latest_metrics['Kurtosis_mean']:.4f}", "< 1.0000"),
        ("PeakFreq_mean (Dominant Freq)", f"{latest_metrics['PeakFreq_mean']:.0f} Hz", "1000 Hz"),
        ("PeakMag_max (FFT Peak Magnitude)", f"{latest_metrics['PeakMag_max']:.2f}", "< 400.00")
    ]
    
    for feat, val, base in features_to_print:
        pdf.cell(63, 7, f" {feat}", border=1)
        pdf.cell(63, 7, f" {val}", border=1)
        pdf.cell(64, 7, f" {base}", border=1)
        pdf.ln()
    pdf.ln(5)
    
   # --- Prognostics Forecast ---
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "4. Predictive Prognostics (Linear Trend Forecast)", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    
    pdf.set_font('Helvetica', '', 10)
    
    # 1. CRITICAL LEVEL: Health is extremely low (Breached severe thresholds)
    if health_score < 35:
        pdf.multi_cell(0, 6, f"CRITICAL SHUTDOWN ALERT: Sentinel AI has flagged an extreme operational hazard.\n"
                             f"- Current Health Score: {health_score}% ({status.upper()})\n"
                             f"- Notice: Structural failure is imminent. The asset has breached critical safety tolerances.\n"
                             f"Action Required: Emergency structural intervention required immediately. Halt machine operations.")

    # 2. SEVERE LEVEL: Health is highly degraded, overriding a flat slope plateau
    elif health_score <= 50:
        pdf.multi_cell(0, 6, f"SEVERE ALERT: Sentinel AI has flagged an operational risk override.\n"
                             f"- Current Health Score: {health_score}% ({status.upper()})\n"
                             f"- Notice: Although the immediate degradation trend line has flattened out, the "
                             f"absolute vibration amplitude remains at an unsafe, highly degraded plateau.\n"
                             f"Action Required: Immediate maintenance or manual shutdown is required. Do not rely on countdown timers.")
                             
    # 3. WARNING LEVEL: Degrading trend detected with an active slope countdown
    elif health_score < 80 and prognostics_results.get("status") == "degrading":
        pdf.multi_cell(0, 6, f"WARNING: Sentinel AI regression analytics identified a progressive acceleration pattern in vibration amplitudes.\n"
                             f"- Calculated Degradation Rate: {prognostics_results['degradation_rate_per_hour']:.4f} g/hour.\n"
                             f"- Estimated Time to Shutdown: {prognostics_results['minutes_remaining']:.1f} minutes.\n"
                             f"Action Required: Schedule inspection immediately before failure threshold is breached.")
                             
    # 4. DEFAULT LEVEL: Stable background operations
    else:
        pdf.multi_cell(0, 6, f"SYSTEM STATUS: Stable.\n"
                             f"The structural degradation trend line is flat or negative within this observation window. "
                             f"No proactive maintenance intervention required at this time.")
        
    return pdf.output()