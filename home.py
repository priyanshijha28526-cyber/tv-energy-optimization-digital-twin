import streamlit as st
from power_model import wall_power
from controller import recommended_backlight
import pandas as pd

st.set_page_config(
    page_title="Live Simulator",
    layout="wide"
)

st.title(
    " TV Energy Optimization Digital Twin"
)
st.info(
    """
Project Objective

Develop a digital twin that dynamically
adjusts TV backlight brightness using
ambient light and video-content analysis
to reduce power consumption while
maintaining viewing quality.
"""
)

st.write(
    """
    This digital twin models
    power consumption of a smart TV
    and dynamically adjusts
    backlight brightness to reduce
    energy usage.
    """
)

# Sidebar

st.sidebar.header("Inputs")
mode = st.sidebar.selectbox(
    "Operating Mode",
    [
        "Custom",
        "Movie Night",
        "Living Room",
        "Gaming",
        "Sports",
        "Streaming"
    ]
)

presets = {
    "Movie Night":{
        "ambient":20,
        "content":20,
        "volume":30
    },

    "Living Room":{
        "ambient":50,
        "content":40,
        "volume":40
    },

    "Gaming":{
        "ambient":80,
        "content":80,
        "volume":60
    },

    "Sports":{
        "ambient":90,
        "content":90,
        "volume":70
    },

    "Streaming":{
        "ambient":60,
        "content":70,
        "volume":40
    },

    "Custom":{
        "ambient":50,
        "content":50,
        "volume":50
    }
}

default_ambient = presets[mode]["ambient"]
default_content = presets[mode]["content"]
default_volume = presets[mode]["volume"]


ambient = st.sidebar.slider(
    "Ambient Light",
    0,
    100,
    default_ambient
)

content = st.sidebar.slider(
    "Content Brightness",
    0,
    100,
    default_content
)

volume = st.sidebar.slider(
    "Volume",
    0,
    100,
    default_volume
)
# Ambient room label
if ambient < 30:
    ambient_status = "🌙 Dark Room"
elif ambient <= 60:
    ambient_status = "🏠 Moderate Room"
else:
    ambient_status = "☀️ Bright Room"

# Content label
if content < 30:
    content_status = "🎬 Dark Scene"
elif content <= 60:
    content_status = "📺 Mid-range"
else:
    content_status = "⚡ Bright Scene"


wifi = st.sidebar.checkbox(
    "WiFi Enabled",
    value=True
)

eco = st.sidebar.checkbox(
    "Eco Mode",
    value=False
)
st.sidebar.info(
    f"""
Current Scenario

Mode: {mode}

Ambient Light: {ambient}% ({ambient_status})

Content Brightness: {content}% ({content_status})

Volume: {volume}%
"""
)

# Controller

recommended = recommended_backlight(
    ambient,
    content,
    eco
)

optimized = wall_power(
    brightness_pct=recommended,
    volume_pct=volume,
    wifi_on=wifi
)

conventional = wall_power(
    brightness_pct=100,
    volume_pct=volume,
    wifi_on=wifi
)
saving = (
    (
        conventional["WallPower"]
        -
        optimized["WallPower"]
    )
    /
    conventional["WallPower"]
) * 100

power_saved = (
    conventional["WallPower"]
    -
    optimized["WallPower"]
)

# Top metrics


c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "Conventional Power",
    f"{conventional['WallPower']:.1f} W"
)

c2.metric(
    "Optimized Power",
    f"{optimized['WallPower']:.1f} W"
)

c3.metric(
    "Saving",
    f"{saving:.1f}%"
)

c4.metric(
    "Recommended Brightness",
    f"{recommended:.1f}%"
)

st.success(
    f"""
Current Operating Mode: {mode}

Energy Saving Achieved: {saving:.1f}%

Recommended Backlight: {recommended:.1f}%
"""
)

# Efficiency Status Badge

if saving > 30:
    st.success("🟢 Excellent Energy Efficiency")

elif saving > 20:
    st.warning("🟡 Moderate Energy Efficiency")

else:
    st.error("🔴 Low Energy Efficiency")

import plotly.graph_objects as go

fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=saving,
        title={"text":"Energy Savings %"},
        gauge={
            "axis":{"range":[0,40]},
            "steps":[
                {"range":[0,15],"color":"#ffcccc"},
                {"range":[15,30],"color":"#fff2cc"},
                {"range":[30,40],"color":"#d9ead3"}
            ]
        }
    )
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="energy_gauge"
)

st.divider()

st.subheader(
    "Recommended Backlight"
)

st.progress(
    int(recommended)
)

st.write(
    f"{recommended:.1f}%"
)
c1, c2, c3 = st.columns(3)

c1.metric(
    "PWM Duty Cycle",
    f"{recommended:.1f}%"
)

c2.metric(
    "LED Driver Efficiency",
    f"{optimized['LED_Eff']*100:.1f}%"
)

c3.metric(
    "SMPS Efficiency",
    f"{optimized['SMPS_Eff']*100:.1f}%"
)

st.subheader(
    "Subsystem Breakdown"
)

subs = optimized["Subsystems"]

df = pd.DataFrame(
    {
        "Subsystem":[
            "Backlight",
            "Audio",
            "MainBoard",
            "Misc"
        ],
        "Power":[
            subs["Backlight"],
            subs["Audio"],
            subs["MainBoard"],
            subs["Misc"]
        ]
    }
)

import plotly.express as px

fig = px.pie(
    df,
    values="Power",
    names="Subsystem",
    title="Power Distribution",
    hole=0.30
)

fig.update_traces(
    textposition="inside",
    textinfo="percent+label"
)

fig.update_layout(
    showlegend=False
)
st.plotly_chart(
    fig,
    use_container_width=True,
     key="subsystem_donut"
)

st.info(
    f"""
Controller Decision

Ambient Light : {ambient}% ({ambient_status})

Content Brightness : {content}% ({content_status})

Recommended Backlight : {recommended:.1f}%

Equivalent PWM Duty Cycle : {recommended:.1f}%

The controller computes the recommended
backlight using weighted ambient-light and
content analysis, balancing viewing quality
and energy efficiency rather than simply
minimizing brightness.

"""
)
comparison = pd.DataFrame({

    "Parameter":[
        "Wall Power (W)",
        "Brightness (%)",
        "Power Saved (W)"
    ],

    "Conventional":[
        conventional["WallPower"],
        100,
        0
    ],

    "Optimized":[
        optimized["WallPower"],
        recommended,
        power_saved
    ]
})

st.subheader(
    "Comparison Table"
)

st.dataframe(
    comparison.set_index("Parameter")
)

st.markdown("---")

st.header(
    "About This Digital Twin"
)

st.write(
    """
    This project develops a digital twin
    for smart television power optimization.

    The framework models:

    • LED Backlight System

    • Audio System

    • Mainboard Electronics

    • SMPS Power Supply

    The controller dynamically adjusts
    backlight brightness using ambient
    light and content brightness inputs
    to minimize energy consumption while
    maintaining viewing quality.
    """
)
st.success(
    """
Key Findings

• Maximum savings occur in dark rooms.

• Bright-content scenarios require higher backlight levels.

• Controller balances user experience and energy savings.

• Dynamic control outperforms fixed-brightness operation.
"""
)
