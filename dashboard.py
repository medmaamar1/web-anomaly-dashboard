import time
import pandas as pd
import streamlit as st

# Import the REAL backend modules
from ingestor import start_ingestor
from preprocessor import preprocess
from features import extract_features
from detector import detect_anomalies
from store import store

# -----------------------------
# Initialize Session State
# -----------------------------
if 'event_handler' not in st.session_state:
    st.session_state.event_handler = start_ingestor()
if 'raw_logs' not in st.session_state:
    st.session_state.raw_logs = pd.DataFrame()
if 'features_df' not in st.session_state:
    st.session_state.features_df = pd.DataFrame()

# -----------------------------
# App Layout
# -----------------------------
st.set_page_config(page_title="Real-Time Web Detection", layout="wide", page_icon="🛰️")
st.title("🛰️ Real-Time Web Detection (Live)")
st.caption("Connected directly to watchdog ingestor and ML pipeline.")

refresh_s = st.sidebar.select_slider("Auto-refresh (s)", options=[0, 2, 5, 10, 30], value=5)

# Fetch new lines from watchdog
new_lines = st.session_state.event_handler.get_lines()

if new_lines:
    try:
        # 1. Preprocess new logs
        new_df = preprocess(new_lines)
        st.session_state.raw_logs = pd.concat([st.session_state.raw_logs, new_df]).tail(10000)
        
        # 2. Extract Features
        # Requires at least some data to group by 5-min intervals
        if not st.session_state.raw_logs.empty:
            f_df = extract_features(st.session_state.raw_logs.copy())
            
            # 3. Detect Anomalies (if enough features exist)
            if len(f_df) > 1:
                detect_anomalies(f_df)  # This modifies f_df in place
                st.session_state.features_df = f_df
                
                # Push anomalies to Supabase
                if 'anomaly' in f_df.columns:
                    anomalies_only = f_df[f_df['anomaly'] == -1]
                    if not anomalies_only.empty:
                        # Only push timestamps we haven't pushed yet
                        if 'last_pushed_ts' not in st.session_state:
                            st.session_state.last_pushed_ts = pd.Timestamp.min.tz_localize(None)
                        
                        # Ensure timezone naive for comparison if needed, or just compare directly
                        new_anomalies = anomalies_only[anomalies_only.index > st.session_state.last_pushed_ts]
                        
                        if not new_anomalies.empty:
                            store.insert_anomalies(new_anomalies)
                            st.session_state.last_pushed_ts = new_anomalies.index.max()
    except Exception as e:
        st.sidebar.error(f"Pipeline Error: {e}")

# KPI Row
col1, col2, col3, col4 = st.columns(4)
total_reqs = len(st.session_state.raw_logs)
anomalies_detected = 0

if not st.session_state.features_df.empty and 'anomaly' in st.session_state.features_df.columns:
    # Anomaly == -1 usually
    anomalies_detected = len(st.session_state.features_df[st.session_state.features_df['anomaly'] == -1])

with col1:
    st.metric("Total Requests Processed", value=f"{total_reqs:,}")
with col2:
    st.metric("Anomaly Spikes Detected", value=anomalies_detected)
with col3:
    if not st.session_state.raw_logs.empty and 'response_size' in st.session_state.raw_logs.columns:
        avg_size = int(st.session_state.raw_logs['response_size'].mean())
        st.metric("Avg Response Size", value=f"{avg_size} bytes")
    else:
        st.metric("Avg Response Size", value="0 bytes")
with col4:
    st.metric("Pipeline Status", value="ACTIVE" if refresh_s > 0 else "PAUSED")

# Main Dashboard
tab1, tab2 = st.tabs(["Anomaly Detection (ML Models)", "Raw Logs (Tailing log.file)"])

with tab1:
    st.subheader("5-Minute Aggregated Behavioral Features & Anomalies")
    if not st.session_state.features_df.empty:
        st.dataframe(st.session_state.features_df.reset_index(), use_container_width=True)
    else:
        st.info("Waiting for enough log data to generate 5-minute behavioral windows...")

with tab2:
    st.subheader("Live Parsed Logs")
    if not st.session_state.raw_logs.empty:
        # Show most recent first
        st.dataframe(st.session_state.raw_logs.sort_values("date", ascending=False), use_container_width=True)
    else:
        st.info("No logs intercepted yet. Append lines to 'log.file' to see them here.")

if refresh_s > 0:
    time.sleep(refresh_s)
    st.rerun()
