import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from power_model import wall_power
from controller import recommended_backlight


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="TV Energy Digital Twin | Live Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
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

    [data-testid="stSidebar"] input {
        color: #111827;
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
# HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1> TV Energy Optimization Digital Twin</h1>
        <p>
            Live simulation of intelligent backlight control,
            power consumption and estimated energy savings.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

with st.expander("Project objective and modelling approach"):
    st.write(
        """
        This digital twin estimates the power consumption of a
        smart television under different operating conditions.

        The controller recommends a backlight level using ambient
        light and content brightness inputs. The power model
        estimates subsystem loads and accounts for LED-driver
        and SMPS conversion efficiencies.

        The conventional case uses a fixed 100% backlight
        brightness as its comparison baseline.

        The results are model-based estimates, not measurements
        from a physical television prototype.
        """
    )


# --------------------------------------------------
# OPERATING MODE PRESETS
# --------------------------------------------------

PRESETS = {
    "Custom": {
        "ambient": 50,
        "content": 50,
        "volume": 50
    },
    "Movie Night": {
        "ambient": 20,
        "content": 20,
        "volume": 30
    },
    "Living Room": {
        "ambient": 50,
        "content": 40,
        "volume": 40
    },
    "Gaming": {
        "ambient": 80,
        "content": 80,
        "volume": 60
    },
    "Sports": {
        "ambient": 90,
        "content": 90,
        "volume": 70
    },
    "Streaming": {
        "ambient": 60,
        "content": 70,
        "volume": 40
    }
}


def apply_preset():
    """Update input sliders when the operating mode changes."""
    selected_mode = st.session_state["mode"]
    selected_preset = PRESETS[selected_mode]

    st.session_state["ambient"] = selected_preset["ambient"]
    st.session_state["content"] = selected_preset["content"]
    st.session_state["volume"] = selected_preset["volume"]


# Initialize widget state before rendering widgets.
st.session_state.setdefault("mode", "Custom")
st.session_state.setdefault("ambient", 50)
st.session_state.setdefault("content", 50)
st.session_state.setdefault("volume", 50)


# --------------------------------------------------
# SIDEBAR INPUTS
# --------------------------------------------------

st.sidebar.markdown("## Simulation Controls")
st.sidebar.caption("Adjust the inputs to explore TV power consumption.")

st.sidebar.selectbox(
    "Operating Mode",
    options=list(PRESETS.keys()),
    key="mode",
    on_change=apply_preset
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Environment")

ambient = st.sidebar.slider(
    "Ambient Light (%)",
    min_value=0,
    max_value=100,
    key="ambient",
    help="Represents the ambient-light input to the controller."
)

content = st.sidebar.slider(
    "Content Brightness (%)",
    min_value=0,
    max_value=100,
    key="content",
    help="Represents the video-content brightness input."
)

st.sidebar.markdown("### TV Settings")

volume = st.sidebar.slider(
    "Volume (%)",
    min_value=0,
    max_value=100,
    key="volume",
    help="Used by the subsystem power model."
)

wifi = st.sidebar.checkbox(
    "Wi-Fi Enabled",
    value=True
)

eco = st.sidebar.checkbox(
    "Eco Mode",
    value=False
)


# --------------------------------------------------
# INPUT INTERPRETATION
# --------------------------------------------------

if ambient < 30:
    ambient_status = "Dark room"
elif ambient <= 60:
    ambient_status = "Moderately lit room"
else:
    ambient_status = "Bright room"

if content < 30:
    content_status = "Dark content"
elif content <= 60:
    content_status = "Medium-brightness content"
else:
    content_status = "Bright content"


st.sidebar.markdown("---")
st.sidebar.markdown("### Current Inputs")

st.sidebar.caption(
    f"""
    **Mode:** {st.session_state["mode"]}

    **Ambient light:** {ambient}% — {ambient_status}

    **Content brightness:** {content}% — {content_status}

    **Volume:** {volume}%

    **Wi-Fi:** {"On" if wifi else "Off"}

    **Eco Mode:** {"On" if eco else "Off"}
    """
)


# --------------------------------------------------
# DIGITAL TWIN CALCULATIONS
# --------------------------------------------------

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

conventional_power = conventional["WallPower"]
optimized_power = optimized["WallPower"]

power_saved = conventional_power - optimized_power

if conventional_power > 0:
    saving = (power_saved / conventional_power) * 100
else:
    saving = 0.0


# --------------------------------------------------
# TOP-LEVEL PERFORMANCE METRICS
# --------------------------------------------------

st.markdown(
    '<div class="section-label">Performance Overview</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Conventional Power",
    f"{conventional_power:.2f} W"
)

c2.metric(
    "Optimized Power",
    f"{optimized_power:.2f} W",
    delta=f"{optimized_power - conventional_power:+.2f} W",
    delta_color="inverse"
)

c3.metric(
    "Estimated Power Savings",
    f"{saving:.2f}%",
    delta=f"{power_saved:.2f} W saved"
)

c4.metric(
    "Recommended Backlight",
    f"{recommended:.1f}%"
)


# --------------------------------------------------
# SAVINGS STATUS
# --------------------------------------------------

if saving >= 30:
    st.success(
        f"High estimated savings: {saving:.1f}% "
        f"({power_saved:.2f} W relative to the baseline)."
    )
elif saving >= 15:
    st.info(
        f"Moderate estimated savings: {saving:.1f}% "
        f"({power_saved:.2f} W relative to the baseline)."
    )
elif saving > 0:
    st.warning(
        f"Limited estimated savings: {saving:.1f}% "
        f"({power_saved:.2f} W relative to the baseline)."
    )
elif saving == 0:
    st.info(
        "No estimated power reduction relative to the baseline."
    )
else:
    st.warning(
        f"The optimized case consumes {-power_saved:.2f} W more "
        "than the conventional baseline. Review the model inputs "
        "and conversion-efficiency assumptions."
    )


# --------------------------------------------------
# ENERGY SAVINGS GAUGE
# --------------------------------------------------

st.markdown(
    '<div class="section-label">Energy Analysis</div>',
    unsafe_allow_html=True
)

gauge_max = max(
    40,
    int((max(saving, 0) + 9) // 10) * 10
)

gauge = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=saving,
        number={
            "suffix": "%",
            "valueformat": ".1f"
        },
        title={
            "text": "Estimated Power Reduction"
        },
        gauge={
            "axis": {
                "range": [min(0, saving), gauge_max]
            },
            "bar": {
                "color": "#0F766E"
            },
            "bgcolor": "white",
            "borderwidth": 1,
            "bordercolor": "#E2E8F0",
            "steps": [
                {
                    "range": [0, gauge_max * 0.375],
                    "color": "#FCE8E6"
                },
                {
                    "range": [
                        gauge_max * 0.375,
                        gauge_max * 0.75
                    ],
                    "color": "#FEF3C7"
                },
                {
                    "range": [
                        gauge_max * 0.75,
                        gauge_max
                    ],
                    "color": "#D1FAE5"
                }
            ]
        }
    )
)

gauge.update_layout(
    height=300,
    margin=dict(l=25, r=25, t=65, b=20),
    paper_bgcolor="white",
    font=dict(
        family="Arial",
        color="#172033"
    )
)

st.plotly_chart(
    gauge,
    use_container_width=True,
    key="energy_gauge"
)


# --------------------------------------------------
# RECOMMENDED BACKLIGHT
# --------------------------------------------------

st.subheader("Recommended Backlight Level")

left, right = st.columns([2, 1])

with left:
    st.progress(
        max(0, min(100, int(round(recommended))))
    )

    st.caption(
        f"Controller recommendation: {recommended:.1f}% brightness"
    )

with right:
    st.metric(
        "Estimated PWM Duty Cycle",
        f"{recommended:.1f}%"
    )

st.caption(
    "PWM duty cycle is shown as equivalent to the recommended "
    "brightness percentage for this model. Actual LED-driver "
    "behaviour may differ in physical hardware."
)


# --------------------------------------------------
# POWER CONVERSION PERFORMANCE
# --------------------------------------------------

st.subheader("Power Conversion Performance")

eff1, eff2 = st.columns(2)

eff1.metric(
    "LED Driver Efficiency",
    f"{optimized['LED_Eff'] * 100:.1f}%"
)

eff2.metric(
    "SMPS Efficiency",
    f"{optimized['SMPS_Eff'] * 100:.1f}%"
)

st.caption(
    "Efficiency values are obtained from the power model "
    "for the current optimized operating point."
)


# --------------------------------------------------
# SUBSYSTEM LOAD DISTRIBUTION
# --------------------------------------------------

st.markdown("---")
st.subheader("Subsystem Load Distribution")

subs = optimized["Subsystems"]

subsystem_names = [
    "Backlight",
    "Audio",
    "MainBoard",
    "Misc"
]

subsystem_values = [
    subs["Backlight"],
    subs["Audio"],
    subs["MainBoard"],
    subs["Misc"]
]

subsystem_df = pd.DataFrame({
    "Subsystem": subsystem_names,
    "Power (W)": subsystem_values
})

chart_col, explanation_col = st.columns([1.4, 1])

with chart_col:
    donut = px.pie(
        subsystem_df,
        values="Power (W)",
        names="Subsystem",
        hole=0.58,
        title="Estimated Subsystem Load Distribution"
    )

    donut.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Subsystem load: %{value:.2f} W<br>"
            "Share: %{percent}<extra></extra>"
        )
    )

    donut.update_layout(
        showlegend=False,
        height=370,
        margin=dict(l=20, r=20, t=65, b=20),
        paper_bgcolor="white",
        font=dict(
            family="Arial",
            color="#172033"
        )
    )

    st.plotly_chart(
        donut,
        use_container_width=True,
        key="subsystem_donut"
    )

with explanation_col:
    st.markdown("#### Subsystem estimates")

    for name, value in zip(
        subsystem_names,
        subsystem_values
    ):
        st.metric(
            name,
            f"{value:.2f} W"
        )

    st.caption(
        "These values describe the modelled subsystem loads. "
        "The donut chart does not separately display the "
        "power lost during LED-driver and SMPS conversion."
    )


# --------------------------------------------------
# CONTROLLER DECISION
# --------------------------------------------------

st.markdown("---")
st.subheader("Controller Decision")

decision_col, inputs_col = st.columns(2)

with decision_col:
    st.markdown("#### Control output")

    st.metric(
        "Recommended Backlight",
        f"{recommended:.1f}%"
    )

    st.write(
        f"""
        The controller receives ambient light of **{ambient}%**
        and content brightness of **{content}%**.

        It recommends a backlight level of **{recommended:.1f}%**.
        """
    )

with inputs_col:
    st.markdown("#### Operating conditions")

    st.write(f"**Ambient environment:** {ambient_status}")
    st.write(f"**Content condition:** {content_status}")
    st.write(f"**Eco Mode:** {'Enabled' if eco else 'Disabled'}")
    st.write(f"**Wi-Fi:** {'Enabled' if wifi else 'Disabled'}")

st.info(
    """
    The controller uses a weighted combination of ambient-light
    and content-brightness inputs. Eco Mode further adjusts the
    recommendation. The final result is evaluated by the power
    model to estimate the corresponding wall power.
    """
)


# --------------------------------------------------
# CONVENTIONAL VS OPTIMIZED COMPARISON
# --------------------------------------------------

st.markdown("---")
st.subheader("Conventional vs Optimized Operation")

comparison = pd.DataFrame({
    "Parameter": [
        "Wall Power (W)",
        "Brightness (%)",
        "Power Saved (W)"
    ],
    "Conventional": [
        conventional_power,
        100,
        0
    ],
    "Optimized": [
        optimized_power,
        recommended,
        power_saved
    ]
})

comparison[["Conventional", "Optimized"]] = (
    comparison[["Conventional", "Optimized"]].round(2)
)

st.dataframe(
    comparison.set_index("Parameter"),
    use_container_width=True
)

st.caption(
    "Conventional baseline: 100% backlight brightness with "
    "the same volume and Wi-Fi settings as the optimized case."
)


# --------------------------------------------------
# MODEL SUMMARY
# --------------------------------------------------

st.markdown("---")
st.subheader("About This Digital Twin")

st.write(
    """
    The simulation represents four main subsystem loads:

    - **LED backlight:** modelled as a function of brightness.
    - **Audio system:** modelled as a function of volume.
    - **Mainboard electronics:** includes the modelled board load
      and the Wi-Fi contribution when enabled.
    - **Miscellaneous loads:** represented by a fixed model term.

    LED-driver and SMPS efficiencies are used to estimate
    wall-input power. The controller then allows the optimized
    operating point to be compared with a conventional
    100%-brightness baseline.
    """
)

st.warning(
    """
    **Model limitation:** The dashboard is a software simulation.
    Its savings depend on the assumed subsystem loads, efficiency
    curves and controller logic. Physical measurements and
    viewing-quality tests would be required to validate the
    predicted savings on an actual television.
    """
)

st.caption(
    "TV Energy Optimization Digital Twin | Live Simulator"
)


