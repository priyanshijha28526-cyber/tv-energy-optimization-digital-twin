import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

st.title("Time Series Simulation")

duration = st.slider(
    "Session Duration (minutes)",
    30,
    240,
    120
)

if duration < 60:
    session_text = f"{duration} minute"
elif duration % 60 == 0:
    session_text = f"{duration//60} hour"
else:
    session_text = f"{duration/60:.1f} hour"

st.write(
    f"""
    Simulates TV operation over a **{session_text} viewing session**
    and compares conventional and optimized power consumption.
    """
)

# ==========================================
# SYNTHETIC INPUTS
# ==========================================

np.random.seed(42)

time = np.arange(duration)

ambient = (
    50
    + 25*np.sin(2*np.pi*time/60)
    + np.random.normal(0,5,duration)
)

ambient = np.clip(
    ambient,
    0,
    100
)

content = (
    50
    + 30*np.sin(2*np.pi*time/25)
    + np.random.normal(0,8,duration)
)

content = np.clip(
    content,
    0,
    100
)

# ==========================================
# BRIGHTNESS CONTROLLER
# ==========================================

from controller import recommended_backlight
recommended = np.array([
    recommended_backlight(a, c)
    for a, c in zip(ambient, content)
])



# ==========================================
# POWER MODEL
# ==========================================

from power_model import wall_power

conventional_power = []
optimized_power = []

volume = 50

for b in recommended:

    optimized_power.append(
        wall_power(
            brightness_pct=float(b),
            volume_pct=volume,
            wifi_on=True
        )["WallPower"]
    )

    conventional_power.append(
        wall_power(
            brightness_pct=100,
            volume_pct=volume,
            wifi_on=True
        )["WallPower"]
    )

conventional_power = np.array(conventional_power)
optimized_power = np.array(optimized_power)

# ==========================================
# ENERGY CALCULATIONS
# ==========================================

energy_saved = (
    conventional_power
    - optimized_power
)

cumulative_energy = np.cumsum(
    energy_saved/60
)

# ==========================================
# INPUT GRAPH
# ==========================================

st.subheader(
    "Simulation Inputs"
)

df_inputs = pd.DataFrame(
    {
        "Time":time,
        "Ambient Light":ambient,
        "Content Brightness":content
    }
)

fig1 = px.line(
    df_inputs,
    x="Time",
    y=[
        "Ambient Light",
        "Content Brightness"
    ]
)

st.plotly_chart(
    fig1,
    use_container_width=True
)
st.metric(
    "Average Recommended Brightness",
    f"{recommended.mean():.1f}%"
)

# ==========================================
# POWER GRAPH
# ==========================================

st.subheader(
    "Wall Power During Session"
)

df_power = pd.DataFrame(
    {
        "Time":time,
        "Conventional TV":conventional_power,
        "Optimized TV":optimized_power
    }
)

fig2 = px.line(
    df_power,
    x="Time",
    y=[
        "Conventional TV",
        "Optimized TV"
    ],
    labels={
        "Time":"Time (minutes)",
        "value":"Power (W)"
    }
)

st.plotly_chart(
    fig2,
    use_container_width=True
)
df_inputs = pd.DataFrame({
    "Time": time,
    "Ambient Light": ambient,
    "Content Brightness": content,
    "Recommended Brightness": recommended
})

# ==========================================
# CUMULATIVE SAVINGS
# ==========================================

st.subheader(
    "Cumulative Energy Savings"
)

df_save = pd.DataFrame(
    {
        "Time":time,
        "Energy Saved (Wh)":cumulative_energy
    }
)

fig3 = px.line(
    df_save,
    x="Time",
    y="Energy Saved (Wh)",
    labels={
        "Time":"Time (minutes)",
        "Energy Saved":"Energy Saved (Wh)"
    }
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# ==========================================
# FINAL RESULTS
# ==========================================

total_saved = cumulative_energy[-1]

conventional_energy = (
    conventional_power.sum()/60
)

optimized_energy = (
    optimized_power.sum()/60
)

saving_percent = (
    (
        conventional_energy
        -
        optimized_energy
    )
    /
    conventional_energy
)*100

c1,c2,c3 = st.columns(3)

c1.metric(
    "Conventional Energy",
    f"{conventional_energy:.2f} Wh"
)

c2.metric(
    "Optimized Energy",
    f"{optimized_energy:.2f} Wh"
)

c3.metric(
    "Energy Saved",
    f"{total_saved:.2f} Wh"
)

st.success(
    f"Total Energy Saving = {saving_percent:.1f}%"
)
st.metric(
    "Average Wall Power Reduction",
    f"{(conventional_power.mean()-optimized_power.mean()):.2f} W"
)
st.info(
    """
Note:


Unlike the Scenario Comparison page, this simulation models continuously varying ambient illumination and content brightness over time.

Consequently, the controller dynamically adjusts the recommended backlight at every time step,
 producing realistic variations in wall power and cumulative energy savings.
"""
)