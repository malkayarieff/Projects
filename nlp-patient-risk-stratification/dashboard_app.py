"""
Long-Term Care Patient Risk Dashboard
DS399 Capstone Project
Built with Streamlit (Python)

To run:
    pip install streamlit pandas plotly
    streamlit run dashboard_app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="Patient Risk Dashboard",
    page_icon="🏥",
    layout="wide"
)

# ── CUSTOM STYLING ───────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0d1117; }
    .block-container { padding: 1.5rem 2rem; }
    h1, h2, h3 { color: #e6edf3; }
    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .risk-high     { color: #ff4444; font-size: 2rem; font-weight: bold; }
    .risk-elevated { color: #ff8c00; font-size: 2rem; font-weight: bold; }
    .risk-monitor  { color: #3b82f6; font-size: 2rem; font-weight: bold; }
    .risk-stable   { color: #22c55e; font-size: 2rem; font-weight: bold; }
    .stSelectbox label { color: #e6edf3; }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("patient_risk_scores_full.csv")
    df["date_of_target"] = pd.to_datetime(df["date_of_target"])
    df["diagnoses"]      = df["diagnoses"].fillna("No diagnosis on record")
    df["risk_keywords"]  = df["risk_keywords"].fillna("none")
    df["medications_list"] = df["medications_list"].fillna("No medication on record")
    return df

df = load_data()

# Get latest assessment per patient for summary stats
latest = df.sort_values("date_of_target").groupby("resident_id").last().reset_index()

# ── HEADER ───────────────────────────────────────────────────
st.title("🏥 Long-Term Care Patient Risk Dashboard")
st.caption("DS-399 Capstone · NLP-Driven Risk Stratification · 2019 Dataset")
st.divider()

# ── SUMMARY CARDS ────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    n = (latest["final_risk_category"] == "HIGH RISK").sum()
    st.metric("🔴 High Risk", n)

with col2:
    n = (latest["final_risk_category"] == "ELEVATED").sum()
    st.metric("🟠 Elevated", n)

with col3:
    n = (latest["final_risk_category"] == "MONITOR").sum()
    st.metric("🔵 Monitor", n)

with col4:
    n = (latest["final_risk_category"] == "STABLE").sum()
    st.metric("🟢 Stable", n)

with col5:
    n = (latest["trend"] == "WORSENING").sum()
    st.metric("📈 Worsening", n)

st.divider()

# ── TWO COLUMN LAYOUT ────────────────────────────────────────
left_col, right_col = st.columns([1, 2])

# ── LEFT: CHARTS ─────────────────────────────────────────────
with left_col:
    st.subheader("Overview")

    # Risk category distribution
    cat_counts = latest["final_risk_category"].value_counts().reset_index()
    cat_counts.columns = ["Category", "Count"]
    color_map = {
        "HIGH RISK": "#ff4444",
        "ELEVATED":  "#ff8c00",
        "MONITOR":   "#3b82f6",
        "STABLE":    "#22c55e"
    }
    fig_cat = px.bar(
        cat_counts, x="Count", y="Category", orientation="h",
        color="Category", color_discrete_map=color_map,
        title="Risk Category Distribution"
    )
    fig_cat.update_layout(
        plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
        font_color="#e6edf3", showlegend=False,
        height=250, margin=dict(l=0, r=0, t=40, b=0)
    )
    st.plotly_chart(fig_cat, use_container_width=True)

    # Trend distribution
    trend_counts = latest["trend"].value_counts().reset_index()
    trend_counts.columns = ["Trend", "Count"]
    trend_colors = {
        "WORSENING": "#ff4444",
        "STABLE": "#7d8590",
        "IMPROVING": "#22c55e",
        "INSUFFICIENT DATA": "#30363d"
    }
    fig_trend = px.pie(
        trend_counts, values="Count", names="Trend",
        color="Trend", color_discrete_map=trend_colors,
        title="Patient Trend Distribution"
    )
    fig_trend.update_layout(
        plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
        font_color="#e6edf3", height=280,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # Average risk score over time
    monthly = df.copy()
    monthly["month"] = monthly["date_of_target"].dt.to_period("M").astype(str)
    monthly_avg = monthly.groupby("month")["final_risk_score"].mean().reset_index()
    monthly_avg.columns = ["Month", "Avg Risk Score"]

    fig_time = px.line(
        monthly_avg, x="Month", y="Avg Risk Score",
        title="Avg Risk Score Over Time",
        markers=True
    )
    fig_time.update_traces(line_color="#58a6ff")
    fig_time.update_layout(
        plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
        font_color="#e6edf3", height=250,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    st.plotly_chart(fig_time, use_container_width=True)

# ── RIGHT: PATIENT LOOKUP ────────────────────────────────────
with right_col:
    st.subheader("Patient Lookup")

    # Filters
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        category_filter = st.selectbox(
            "Filter by Risk Category",
            ["ALL", "HIGH RISK", "ELEVATED", "MONITOR", "STABLE"]
        )
    with filter_col2:
        trend_filter = st.selectbox(
            "Filter by Trend",
            ["ALL", "WORSENING", "STABLE", "IMPROVING", "INSUFFICIENT DATA"]
        )
    with filter_col3:
        search_id = st.text_input("Search Patient ID", placeholder="e.g. 528")

    # Apply filters
    filtered = latest.copy()
    if category_filter != "ALL":
        filtered = filtered[filtered["final_risk_category"] == category_filter]
    if trend_filter != "ALL":
        filtered = filtered[filtered["trend"] == trend_filter]
    if search_id:
        filtered = filtered[filtered["resident_id"].astype(str).str.contains(search_id)]

    filtered_sorted = filtered.sort_values("final_risk_score", ascending=False)

    st.caption(f"{len(filtered_sorted)} patients found")

    # Patient selector
    if len(filtered_sorted) == 0:
        st.warning("No patients match your filters.")
    else:
        patient_options = [
            f"Patient #{int(row['resident_id'])} — {row['final_risk_category']} (Score: {int(row['final_risk_score'])})"
            for _, row in filtered_sorted.head(100).iterrows()
        ]

        selected_label = st.selectbox("Select a patient", patient_options)
        selected_id = int(selected_label.split("#")[1].split(" ")[0])

        # Get patient data
        patient_latest = latest[latest["resident_id"] == selected_id].iloc[0]
        patient_history = df[df["resident_id"] == selected_id].sort_values("date_of_target")

        st.divider()

        # Patient header
        cat = patient_latest["final_risk_category"]
        score = int(patient_latest["final_risk_score"])
        trend = patient_latest["trend"]

        cat_color = color_map.get(cat, "#ffffff")
        st.markdown(f"### Patient #{selected_id}")

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Risk Category", cat)
        p2.metric("Risk Score", score)
        p3.metric("Trend", trend)
        p4.metric("Assessments", len(patient_history))

        # Keywords
        keywords = patient_latest["risk_keywords"]
        if keywords and keywords != "none":
            st.markdown("**Risk Keywords (Latest):**")
            kw_tags = " · ".join([f"`{k.strip()}`" for k in keywords.split(",")])
            st.markdown(kw_tags)

        # Medications
        meds = patient_latest["medications_list"]
        if meds and meds != "No medication on record":
            with st.expander(f"💊 Medications ({int(patient_latest['num_medications'])} classes) {'— ⚠️ Polypharmacy' if patient_latest['polypharmacy_flag'] == 1 else ''}"):
                for m in meds.split("|"):
                    st.write(f"• {m.strip()}")

        # Diagnoses
        diag = patient_latest["diagnoses"]
        if diag and diag != "No diagnosis on record":
            with st.expander("🩺 Diagnoses on Record"):
                for d in diag.split("|"):
                    st.write(f"• {d.strip()}")

        # Risk score timeline
        st.markdown("**Risk Score Timeline**")
        fig_timeline = go.Figure()

        fig_timeline.add_trace(go.Scatter(
            x=patient_history["date_of_target"],
            y=patient_history["final_risk_score"],
            mode="lines+markers",
            line=dict(color="#58a6ff", width=2),
            marker=dict(
                size=10,
                color=[color_map.get(c, "#ffffff") for c in patient_history["final_risk_category"]],
                line=dict(color="#ffffff", width=1)
            ),
            hovertemplate="<b>%{x}</b><br>Score: %{y}<br><extra></extra>"
        ))

        fig_timeline.add_hline(y=6, line_dash="dash", line_color="#ff4444",
                               annotation_text="High Risk", annotation_position="right")
        fig_timeline.add_hline(y=3, line_dash="dash", line_color="#ff8c00",
                               annotation_text="Elevated", annotation_position="right")

        fig_timeline.update_layout(
            plot_bgcolor="#0d1117", paper_bgcolor="#161b22",
            font_color="#e6edf3",
            xaxis_title="Assessment Date",
            yaxis_title="Risk Score",
            height=300,
            margin=dict(l=0, r=60, t=20, b=0)
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

        # Assessment history table
        with st.expander("📋 Full Assessment History"):
            history_display = patient_history[[
                "date_of_target", "final_risk_score",
                "final_risk_category", "risk_keywords"
            ]].copy()
            history_display.columns = ["Date", "Score", "Category", "Keywords"]
            history_display["Date"] = history_display["Date"].dt.strftime("%Y-%m-%d")
            st.dataframe(history_display, use_container_width=True, hide_index=True)

        # Latest note preview
        latest_note = patient_history.iloc[-1]["full_note"]
        if pd.notna(latest_note) and str(latest_note).strip():
            with st.expander("📝 Latest Nurse Note Preview"):
                st.write(str(latest_note)[:500] + ("..." if len(str(latest_note)) > 500 else ""))
