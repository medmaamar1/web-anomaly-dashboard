import time
from datetime import datetime, timedelta
from typing import List, Tuple

import numpy as np
import pandas as pd
import streamlit as st


# -----------------------------
# Utilities (placeholders/mock)
# -----------------------------
def generate_time_series(
    start: datetime,
    periods: int,
    freq_minutes: int,
    baseline: float,
    noise: float,
) -> pd.DataFrame:
    timestamps = [start + timedelta(minutes=i * freq_minutes) for i in range(periods)]
    values = np.clip(
        baseline
        + np.sin(np.linspace(0, 4 * np.pi, periods)) * baseline * 0.1
        + np.random.randn(periods) * noise,
        a_min=0,
        a_max=None,
    )
    return pd.DataFrame({"timestamp": timestamps, "value": values})


def generate_mock_events(num_rows: int) -> pd.DataFrame:
    np.random.seed(42)
    status = np.random.choice(["OK", "WARN", "ALERT"], size=num_rows, p=[0.7, 0.2, 0.1])
    sources = np.random.choice(["nginx", "waf", "cdn", "app"], size=num_rows)
    latency_ms = np.random.gamma(shape=2.0, scale=80.0, size=num_rows).astype(int)
    scores = np.clip(np.random.beta(2, 5, size=num_rows) * 100, 0, 100)
    now = datetime.utcnow()
    ts = [now - timedelta(seconds=i * np.random.randint(3, 30)) for i in range(num_rows)]
    return pd.DataFrame(
        {
            "time": ts,
            "status": status,
            "source": sources,
            "latency_ms": latency_ms,
            "risk_score": np.round(scores, 2),
            "ip": [f"192.168.0.{i%255}" for i in range(num_rows)],
            "path": np.random.choice(["/", "/login", "/api", "/checkout", "/search"], size=num_rows),
        }
    ).sort_values("time", ascending=False)


def generate_mock_incidents(num_rows: int) -> pd.DataFrame:
    severities = ["low", "medium", "high", "critical"]
    types = ["bot", "ddos", "credential_stuffing", "scraping"]
    now = datetime.utcnow()
    data = []
    for i in range(num_rows):
        started = now - timedelta(hours=np.random.uniform(1, 120))
        duration_min = int(np.random.uniform(5, 240))
        data.append(
            {
                "id": f"INC-{1000+i}",
                "started": started,
                "duration_min": duration_min,
                "type": np.random.choice(types),
                "severity": np.random.choice(severities, p=[0.4, 0.35, 0.2, 0.05]),
                "status": np.random.choice(["open", "investigating", "mitigated", "closed"], p=[0.2, 0.3, 0.3, 0.2]),
                "notes": "Placeholder incident details.",
            }
        )
    df = pd.DataFrame(data).sort_values(["severity", "started"], ascending=[False, False])
    return df


# -----------------------------
# Sidebar controls (placeholders)
# -----------------------------
def sidebar_controls() -> Tuple[Tuple[datetime, datetime], str, float, int, bool]:
    st.sidebar.header("Controls")
    today = datetime.utcnow().date()
    start_default = datetime.combine(today - timedelta(days=1), datetime.min.time())
    end_default = datetime.combine(today, datetime.max.time())

    date_range = st.sidebar.date_input(
        "Date range",
        value=(start_default.date(), end_default.date()),
    )

    model = st.sidebar.selectbox(
        "Detection model",
        options=["Heuristic v1", "ML Baseline", "XGBoost v2", "Transformer v1"],
        index=2,
    )

    threshold = st.sidebar.slider("Alert threshold", min_value=0.0, max_value=1.0, value=0.65, step=0.01)

    refresh_seconds = st.sidebar.select_slider(
        "Auto-refresh (s)",
        options=[0, 5, 10, 15, 30, 60],
        value=10,
    )

    dark = st.sidebar.toggle("Dark mode", value=True)

    st.sidebar.divider()
    st.sidebar.caption("These are placeholders; no backend is connected yet.")

    # Normalize date_range into datetimes
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_dt = datetime.combine(date_range[0], datetime.min.time())
        end_dt = datetime.combine(date_range[1], datetime.max.time())
    else:
        start_dt, end_dt = start_default, end_default

    return (start_dt, end_dt), model, threshold, int(refresh_seconds), bool(dark)


# -----------------------------
# Top KPI cards
# -----------------------------
def kpi_row():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Requests/min", value="12.6k", delta="+4.2%")
    with col2:
        st.metric("Blocked/min", value="380", delta="+1.8%")
    with col3:
        st.metric("Median latency", value="124 ms", delta="-6 ms")
    with col4:
        st.metric("Anomaly rate", value="1.7%", delta="-0.2%")


# -----------------------------
# Tabs content (placeholders)
# -----------------------------
def tab_overview():
    st.subheader("Traffic & Detection Overview")
    now = datetime.utcnow()
    ts = generate_time_series(now - timedelta(hours=3), periods=60, freq_minutes=3, baseline=1000, noise=60)
    ts = ts.set_index("timestamp")

    st.line_chart(ts, height=220)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.caption("Requests by endpoint (sampled)")
        endpoints = ["/", "/login", "/api", "/checkout", "/search", "/products"]
        counts = np.random.randint(200, 4000, size=len(endpoints))
        df = pd.DataFrame({"endpoint": endpoints, "requests": counts}).sort_values("requests", ascending=False)
        st.bar_chart(df.set_index("endpoint"))
    with col2:
        st.caption("Status split")
        split = pd.DataFrame(
            {
                "status": ["2xx", "4xx", "5xx"],
                "count": [np.random.randint(8000, 12000), np.random.randint(300, 1200), np.random.randint(50, 400)],
            }
        )
        st.dataframe(split, hide_index=True, use_container_width=True)


def tab_live_monitor(refresh_s: int):
    st.subheader("Live Monitor")
    placeholder = st.empty()
    events_df = generate_mock_events(30)

    with placeholder.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.progress(int(np.random.randint(60, 95)))
            st.caption("System health")
        with col2:
            st.progress(int(np.random.randint(30, 70)))
            st.caption("Mitigation capacity")
        with col3:
            st.progress(int(np.random.randint(10, 40)))
            st.caption("Current risk load")

        st.dataframe(events_df, use_container_width=True, hide_index=True)

    if refresh_s > 0:
        time.sleep(0.1)
        st.caption(f"Auto-refresh every {refresh_s}s (placeholder; manual rerun to refresh).")


def tab_incidents():
    st.subheader("Incidents")
    df = generate_mock_incidents(18)

    col1, col2, col3 = st.columns(3)
    with col1:
        sev = st.selectbox("Filter severity", options=["all", "low", "medium", "high", "critical"], index=0)
    with col2:
        status = st.selectbox("Filter status", options=["all", "open", "investigating", "mitigated", "closed"], index=0)
    with col3:
        itype = st.selectbox("Filter type", options=["all", "bot", "ddos", "credential_stuffing", "scraping"], index=0)

    filtered = df.copy()
    if sev != "all":
        filtered = filtered[filtered["severity"] == sev]
    if status != "all":
        filtered = filtered[filtered["status"] == status]
    if itype != "all":
        filtered = filtered[filtered["type"] == itype]

    st.dataframe(filtered, use_container_width=True, hide_index=True)


def tab_settings(
    date_range: Tuple[datetime, datetime], model: str, threshold: float, refresh_s: int, dark: bool
):
    st.subheader("Settings (Placeholders)")
    st.write(
        {
            "start": date_range[0].isoformat(),
            "end": date_range[1].isoformat(),
            "model": model,
            "threshold": threshold,
            "auto_refresh_seconds": refresh_s,
            "dark_mode": dark,
        }
    )

    st.divider()
    st.caption("These controls are not persisted and do not affect any backend yet.")


def tab_help():
    st.subheader("Help")
    st.markdown(
        """
        This dashboard is a UI placeholder for a real-time web detection system.

        - Use the sidebar to adjust time range, select a model, set thresholds.
        - Explore the tabs for overview charts, live events, and incidents.
        - Data displayed is synthetic and for demonstration only.

        When the backend is ready, these views will connect to live APIs.
        """
    )


# -----------------------------
# App
# -----------------------------
def main():
    st.set_page_config(page_title="Real-Time Web Detection", layout="wide", page_icon="🛰️")
    st.title("🛰️ Real-Time Web Detection")
    st.caption("Placeholder dashboard UI. Not connected to backend yet.")

    # Sidebar controls
    date_range, model, threshold, refresh_s, dark = sidebar_controls()

    # KPI row
    kpi_row()

    # Tabs
    tabs: List[str] = ["Overview", "Live Monitor", "Incidents", "Settings", "Help"]
    tab1, tab2, tab3, tab4, tab5 = st.tabs(tabs)
    with tab1:
        tab_overview()
    with tab2:
        tab_live_monitor(refresh_s=refresh_s)
    with tab3:
        tab_incidents()
    with tab4:
        tab_settings(date_range, model, threshold, refresh_s, dark)
    with tab5:
        tab_help()


if __name__ == "__main__":
    main()


