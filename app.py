
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import joblib

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Smart Traffic Intelligence System",
    layout="wide"
)

# ==========================================
# LOAD DATA
# ==========================================
df = pd.read_csv("data/events.csv")

model = joblib.load(
    "models/severity_model.pkl"
)

# ==========================================
# TITLE
# ==========================================
st.title("🚦 Smart Traffic Intelligence System")

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Module",
    [
        "Dashboard",
        "Hotspots",
        "Live Map",
        "AI Predictor",
        "Resource Recommendation"
    ]
)

# ===================================================
# DASHBOARD
# ===================================================
if page == "Dashboard":

    st.header("📊 Traffic Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "🚦 Total Events",
        len(df)
    )

    col2.metric(
        "🟢 Active Events",
        (df["status"] == "active").sum()
    )

    col3.metric(
        "✅ Closed Events",
        (df["status"] == "closed").sum()
    )

    col4.metric(
        "🔴 High Priority",
        (df["priority"] == 1).sum()
    )

    st.markdown("---")

    st.subheader("Top Event Causes")

    fig1 = px.bar(
        x=df["event_cause"].value_counts().head(10).index,
        y=df["event_cause"].value_counts().head(10).values,
        title="Top Event Causes"
    )

    fig1.update_layout(
        xaxis_title="Cause",
        yaxis_title="Count"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    st.markdown("---")

    st.subheader("Corridor Distribution")

    fig2 = px.pie(
        values=df["corridor"].value_counts().head(10).values,
        names=df["corridor"].value_counts().head(10).index,
        title="Corridor Distribution"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# ===================================================
# HOTSPOTS
# ===================================================
elif page == "Hotspots":

    st.header("🔥 Traffic Hotspots")

    hotspot_df = (
        df[df["cluster"] != -1]
        .groupby("cluster")
        .size()
        .reset_index(name="events")
        .sort_values(
            by="events",
            ascending=False
        )
    )

    st.subheader("Hotspot Table")

    st.dataframe(hotspot_df)

    st.markdown("---")

    fig_hot = px.bar(
        hotspot_df,
        x="cluster",
        y="events",
        title="Events per Cluster"
    )

    fig_hot.update_layout(
        xaxis_title="Cluster ID",
        yaxis_title="Number of Events"
    )

    st.plotly_chart(
        fig_hot,
        use_container_width=True
    )

# ===================================================
# LIVE MAP
# ===================================================
elif page == "Live Map":

    st.header("🗺 Live Traffic Map")

    m = folium.Map(
        location=[
            df["latitude"].mean(),
            df["longitude"].mean()
        ],
        zoom_start=11
    )

    sample_df = df.sample(
        min(1000, len(df)),
        random_state=42
    )

    for _, row in sample_df.iterrows():

        color = (
            "red"
            if row["priority"] == 1
            else "green"
        )

        folium.CircleMarker(
            location=[
                row["latitude"],
                row["longitude"]
            ],
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=f"""
Cause : {row['event_cause']}
Priority : {row['priority']}
"""
        ).add_to(m)

    st_folium(
        m,
        width=1200,
        height=700
    )

# ===================================================
# AI PREDICTOR
# ===================================================
elif page == "AI Predictor":

    st.header("🤖 AI Severity Predictor")

    priority = st.selectbox(
        "Priority",
        [1, 0],
        format_func=lambda x:
        "High" if x == 1 else "Low"
    )

    road_closure = st.selectbox(
        "Road Closure",
        [True, False]
    )

    morning_peak = st.selectbox(
        "Morning Peak",
        [1, 0]
    )

    evening_peak = st.selectbox(
        "Evening Peak",
        [1, 0]
    )

    if st.button("Predict Severity"):

        severity = 1

        if priority == 1:
            severity += 1

        if road_closure:
            severity += 1

        if morning_peak == 1 or evening_peak == 1:
            severity += 1

        severity = min(severity, 4)

        if severity == 1:
            st.success("🟢 Low Severity")

        elif severity == 2:
            st.warning("🟡 Medium Severity")

        elif severity == 3:
            st.warning("🟠 High Severity")

        else:
            st.error("🔴 Critical Severity")

# ===================================================
# RESOURCE RECOMMENDATION
# ===================================================
elif page == "Resource Recommendation":

    st.header("🚓 Smart Resource Recommendation")

    severity = st.selectbox(
        "Severity Level",
        [1, 2, 3, 4]
    )

    road_closure = st.selectbox(
        "Road Closure",
        [False, True]
    )

    if severity == 1:
        police = 1
        barricades = 2
        ambulance = "No"
        tow_truck = "No"

    elif severity == 2:
        police = 2
        barricades = 4
        ambulance = "No"
        tow_truck = "Yes"

    elif severity == 3:
        police = 3
        barricades = 6
        ambulance = "Yes"
        tow_truck = "Yes"

    else:
        police = 4
        barricades = 8
        ambulance = "Yes"
        tow_truck = "Yes"

    diversion = (
        "Yes"
        if road_closure
        else "No"
    )

    st.success(f"🚓 Police Units : {police}")
    st.success(f"🚧 Barricades : {barricades}")
    st.success(f"🚑 Ambulance Required : {ambulance}")
    st.success(f"🚚 Tow Truck Required : {tow_truck}")
    st.success(f"🔀 Diversion Required : {diversion}")

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")

st.caption(
    "🚦 Smart Traffic Intelligence System | Flipkart GRIDLOCK 2.0 Hackathon"
)
