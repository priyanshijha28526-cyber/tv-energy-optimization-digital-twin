
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

from controller import recommended_backlight
from power_model import wall_power


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Time Series Simulation | TV Energy Digital Twin",
    page_icon=None,
    layout="wide"
)


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background-color: #F5F7FB;
    }

    [data-testid="stSidebar"] {
        background-color: #111827;
    }

    [data-testid="stSidebar"] * {
        color: #F3F4F6;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    .hero {
        padding: 1.5rem 1.7rem;
        border-radius: 16px;
        background: linear-gradient(120deg, #111827, #1E3A5F);
        color: white;
        margin-bottom: 1.4rem;
    }

    .hero h1 {
        color: white;
        font-size: 2rem;
        margin-bottom: 0.4rem;
    }

    .hero p {
        color: #D1D9E6;
        font-size: 1rem;
        margin-bottom: 0;
    }

    .section-label {
        color: #64748B;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.10em;
        text-transform: uppercase;
        margin-top: 0.7rem;
        margin-bottom: 0.35rem;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1rem;
    }

    div[data-testid="stMetricLabel"] {
        color: #64748B;
    }

    div[data-testid="stMetricValue"] {
        color: #111827;
    }

    div[data-testid="stPlotlyChart"] {
        background-color: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 0.5rem;
    }

    h2, h3 {
        color: #172033;
    }

    hr {
        border-color: #E2E8F0;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>Time Series Simulation</h1>
        <p>
            Analyse changing TV operating conditions, wall power
            and cumulative energy savings throughout a viewing session.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

with st.expander("About this simulation"):
    st.write(
        """
        This page simulates TV operation using synthetic ambient-light
        and content-brightness inputs that vary over time.

        At each one-minute time step, the controller calculates a
        recommended backlight level. The power model then estimates
        conventional and optimized wall-input power.

        The two operating cases use the same volume and Wi-Fi settings.
        Eco Mode is not explicitly enabled in this simulation.

        The input signals are generated mathematically and are not
        measurements collected from a physical television or a room.
        """
    )


# --------------------------------------------------
# SESSION CONTROLS
# --------------------------------------------------

st.markdown(
    '<div class="section-label">Simulation Controls</div>',
    unsafe_allow_html=True
)

duration = st.slider(
    "Viewing Session Duration (minutes)",
    min_value=30,
    max_value=240,
    value=120,
    step=10
)

if duration < 60:
    session_text = f"{duration} minutes"
elif duration % 60 == 0:
    hours = duration // 60
    session_text = f"{hours} " + (
        "hour" if hours == 1 else "hours"
    )
else:
    session_text = f"{duration / 60:.1f} hours"

st.caption(
    f"Selected simulation duration: {session_text}"
)


# --------------------------------------------------
# SYNTHETIC INPUT GENERATION
# --------------------------------------------------

# A fixed seed makes the results reproducible.
np.random.seed(42)

time = np.arange(duration)

ambient = (
    50
    + 25 * np.sin(2 * np.pi * time / 60)
    + np.random.normal(0, 5, duration)
)

ambient = np.clip(ambient, 0, 100)

content = (
    50
    + 30 * np.sin(2 * np.pi * time / 25)
    + np.random.normal(0, 8, duration)
)

content = np.clip(content, 0, 100)


# --------------------------------------------------
# BRIGHTNESS CONTROLLER
# --------------------------------------------------

recommended = np.array([
    recommended_backlight(a, c)
    for a, c in zip(ambient, content)
])


# --------------------------------------------------
# POWER MODEL
# --------------------------------------------------

volume = 50
wifi_on = True

conventional_power = []
optimized_power = []

for brightness in recommended:

    optimized_result = wall_power(
        brightness_pct=float(brightness),
        volume_pct=volume,
        wifi_on=wifi_on
    )

    conventional_result = wall_power(
        brightness_pct=100,
        volume_pct=volume,
        wifi_on=wifi_on
    )

    optimized_power.append(
        optimized_result["WallPower"]
    )

    conventional_power.append(
        conventional_result["WallPower"]
    )


conventional_power = np.array(conventional_power)
optimized_power = np.array(optimized_power)


# --------------------------------------------------
# ENERGY CALCULATIONS
# --------------------------------------------------

# Each sample represents one minute of operation.
energy_saved = (
    conventional_power - optimized_power
)

cumulative_energy = np.cumsum(
    energy_saved / 60
)

conventional_energy = (
    conventional_power.sum() / 60
)

optimized_energy = (
    optimized_power.sum() / 60
)

total_saved = cumulative_energy[-1]

if conventional_energy > 0:
    saving_percent = (
        (conventional_energy - optimized_energy)
        / conventional_energy
    ) * 100
else:
    saving_percent = 0.0

average_power_reduction = (
    conventional_power.mean()
    - optimized_power.mean()
)

average_brightness = recommended.mean()


# --------------------------------------------------
# PERFORMANCE OVERVIEW
# --------------------------------------------------

st.markdown(
    '<div class="section-label">Performance Overview</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Average Recommended Brightness",
    f"{average_brightness:.1f}%"
)

c2.metric(
    "Average Power Reduction",
    f"{average_power_reduction:.2f} W"
)

c3.metric(
    "Cumulative Energy Saved",
    f"{total_saved:.2f} Wh"
)

c4.metric(
    "Estimated Energy Savings",
    f"{saving_percent:.1f}%"
)


# --------------------------------------------------
# CHART STYLING HELPER
# --------------------------------------------------

def style_chart(fig, height=380):
    """Apply a consistent visual style to Plotly charts."""

    fig.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Arial",
            color="#172033",
            size=12
        ),
        margin=dict(
            l=35,
            r=25,
            t=65,
            b=45
        ),
        title=dict(
            x=0.03,
            xanchor="left"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor="#E2E8F0"
    )

    fig.update_yaxes(
        gridcolor="#E8EDF4",
        zerolinecolor="#94A3B8"
    )

    return fig


# --------------------------------------------------
# SIMULATION INPUTS
# --------------------------------------------------

st.markdown("---")

st.markdown(
    '<div class="section-label">Input Analysis</div>',
    unsafe_allow_html=True
)

st.subheader("Ambient Light and Content Brightness")

df_inputs = pd.DataFrame({
    "Time (minutes)": time,
    "Ambient Light (%)": ambient,
    "Content Brightness (%)": content
})

fig1 = px.line(
    df_inputs,
    x="Time (minutes)",
    y=[
        "Ambient Light (%)",
        "Content Brightness (%)"
    ],
    labels={
        "value": "Input Level (%)",
        "variable": "Input Signal",
        "Time (minutes)": "Time (minutes)"
    },
    title="Synthetic Input Signals During the Session",
    color_discrete_map={
        "Ambient Light (%)": "#0F766E",
        "Content Brightness (%)": "#D97757"
    }
)

fig1 = style_chart(fig1, 400)

st.plotly_chart(
    fig1,
    use_container_width=True,
    key="timeseries_input_chart"
)

st.caption(
    "The signals are synthetic and use a fixed random seed "
    "so that the simulation can be reproduced."
)


# --------------------------------------------------
# CONTROLLER OUTPUT
# --------------------------------------------------

st.subheader("Recommended Backlight Over Time")

df_brightness = pd.DataFrame({
    "Time (minutes)": time,
    "Recommended Brightness (%)": recommended
})

fig_brightness = px.line(
    df_brightness,
    x="Time (minutes)",
    y="Recommended Brightness (%)",
    title="Controller Output",
    labels={
        "Time (minutes)": "Time (minutes)",
        "Recommended Brightness (%)": "Backlight Brightness (%)"
    }
)

fig_brightness.update_traces(
    line=dict(
        color="#0F766E",
        width=2.5
    )
)

fig_brightness = style_chart(
    fig_brightness,
    360
)

st.plotly_chart(
    fig_brightness,
    use_container_width=True,
    key="timeseries_brightness_chart"
)


# --------------------------------------------------
# WALL POWER COMPARISON
# --------------------------------------------------

st.markdown("---")

st.markdown(
    '<div class="section-label">Power Analysis</div>',
    unsafe_allow_html=True
)

st.subheader("Wall Power During the Viewing Session")

df_power = pd.DataFrame({
    "Time (minutes)": time,
    "Conventional TV": conventional_power,
    "Optimized TV": optimized_power
})

fig2 = px.line(
    df_power,
    x="Time (minutes)",
    y=[
        "Conventional TV",
        "Optimized TV"
    ],
    labels={
        "Time (minutes)": "Time (minutes)",
        "value": "Estimated Wall Power (W)",
        "variable": "Operating Condition"
    },
    title="Conventional vs Optimized Wall Power",
    color_discrete_map={
        "Conventional TV": "#64748B",
        "Optimized TV": "#0F766E"
    }
)

fig2 = style_chart(fig2, 420)

st.plotly_chart(
    fig2,
    use_container_width=True,
    key="timeseries_power_chart"
)


# --------------------------------------------------
# CUMULATIVE ENERGY SAVINGS
# --------------------------------------------------

st.markdown("---")

st.markdown(
    '<div class="section-label">Energy Analysis</div>',
    unsafe_allow_html=True
)

st.subheader("Cumulative Energy Savings")

df_save = pd.DataFrame({
    "Time (minutes)": time,
    "Cumulative Energy Saved (Wh)": cumulative_energy
})

fig3 = px.line(
    df_save,
    x="Time (minutes)",
    y="Cumulative Energy Saved (Wh)",
    title="Accumulated Energy Difference",
    labels={
        "Time (minutes)": "Time (minutes)",
        "Cumulative Energy Saved (Wh)": "Cumulative Energy (Wh)"
    }
)

fig3.update_traces(
    line=dict(
        color="#0F766E",
        width=3
    ),
    fill="tozeroy",
    fillcolor="rgba(15, 118, 110, 0.10)"
)

fig3 = style_chart(fig3, 400)

st.plotly_chart(
    fig3,
    use_container_width=True,
    key="timeseries_energy_chart"
)


# --------------------------------------------------
# FINAL RESULTS
# --------------------------------------------------

st.markdown("---")
st.subheader("Session Energy Summary")

r1, r2, r3 = st.columns(3)

r1.metric(
    "Conventional Energy",
    f"{conventional_energy:.2f} Wh"
)

r2.metric(
    "Optimized Energy",
    f"{optimized_energy:.2f} Wh"
)

r3.metric(
    "Net Energy Saved",
    f"{total_saved:.2f} Wh"
)

if saving_percent > 0:
    st.success(
        f"The model estimates a {saving_percent:.1f}% reduction "
        f"in energy consumption over this {session_text} session."
    )
elif saving_percent == 0:
    st.info(
        "The model estimates no net energy reduction "
        "relative to the conventional baseline."
    )
else:
    st.warning(
        f"The optimized case uses {-total_saved:.2f} Wh more "
        "than the conventional baseline over this session."
    )


# --------------------------------------------------
# METHODOLOGY AND LIMITATIONS
# --------------------------------------------------

st.markdown("---")
st.subheader("Methodology and Limitations")

with st.expander("How are the results calculated?"):

    st.write(
        """
        1. Synthetic ambient-light and content-brightness values
           are generated for each minute of the session.

        2. The brightness controller calculates a recommended
           backlight level for each pair of inputs.

        3. The power model estimates wall-input power for the
           recommended brightness and for a fixed 100% brightness
           baseline.

        4. The difference between the two power estimates is
           accumulated over the session to calculate net energy saved.
        """
    )

    st.write(
        """
        **Assumptions**

        - The simulation uses one-minute time steps.
        - Volume remains fixed at 50%.
        - Wi-Fi remains enabled.
        - Eco Mode is not explicitly enabled.
        - The conventional and optimized cases use the same
          volume and Wi-Fi settings.
        - Ambient-light and content-brightness signals are synthetic.
        """
    )

    st.write(
        """
        **Limitations**

        These results depend on the assumptions, subsystem loads
        and conversion-efficiency curves in the power model.
        The synthetic inputs are not measured environmental data.
        Physical power measurements and viewing-quality tests
        would be needed to validate the estimates on real hardware.
        """
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")

st.caption(
    "TV Energy Optimization Digital Twin | Time Series Simulation"
)
