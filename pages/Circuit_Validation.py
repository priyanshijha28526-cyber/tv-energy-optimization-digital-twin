```python
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from scipy.interpolate import PchipInterpolator

from controller import recommended_backlight
from power_model import (
    wall_power,
    led_duty,
    led_eff,
    smps_load,
    smps_eff,
)

st.set_page_config(
    page_title="Circuit Validation",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# PROFESSIONAL NAVY AND WHITE THEME
# ---------------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background-color: #F5F7FB;
        color: #172B4D;
    }

    [data-testid="stHeader"] {
        background-color: rgba(245,247,251,0.95);
    }

    [data-testid="stSidebar"] {
        background-color: #EAF0F8;
    }

    h1, h2, h3 {
        color: #142D4E !important;
    }

    p, li, label {
        color: #344563;
    }

    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #D9E2EF;
        border-radius: 10px;
        padding: 16px;
    }

    [data-testid="stMetricLabel"] {
        color: #526581;
    }

    [data-testid="stMetricValue"] {
        color: #142D4E;
    }

    div[data-testid="stAlert"] {
        border-radius: 8px;
    }

    .hero {
        background: linear-gradient(115deg, #142D4E, #254F78);
        padding: 28px 32px;
        border-radius: 14px;
        color: white;
        margin-bottom: 22px;
    }

    .hero h1 {
        color: white !important;
        margin-bottom: 8px;
        font-size: 2rem;
    }

    .hero p {
        color: #E5EDF7 !important;
        font-size: 1rem;
        margin-bottom: 0;
    }

    .section-note {
        background: #FFFFFF;
        border-left: 4px solid #315F91;
        padding: 14px 18px;
        border-radius: 5px;
        margin: 10px 0 18px 0;
    }

    .small-note {
        color: #64748B;
        font-size: 0.88rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>Circuit Validation</h1>
        <p>
            Analytical validation of the LED backlight controller,
            conversion-efficiency models and television power estimates.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    This page examines the engineering relationships used by the Digital Twin.
    The analysis progresses from the PWM control principle to the predicted
    wall-power response and subsystem-level power balance.
    """
)

st.info(
    "Scope: This is a software-based analytical validation. "
    "The curves and power estimates are model outputs, not measurements "
    "from a physical television or a completed transistor-level circuit simulation."
)

# ---------------------------------------------------------
# VALIDATION OVERVIEW
# ---------------------------------------------------------

st.subheader("Validation Overview")

overview = [
    ("01", "PWM and LED current"),
    ("02", "LED driver efficiency"),
    ("03", "SMPS efficiency"),
    ("04", "Controller response"),
    ("05", "Wall-power response"),
    ("06", "Operating-point comparison"),
    ("07", "Engineering validation flow"),
    ("08", "Subsystem power balance"),
]

cols = st.columns(4)

for i, (number, label) in enumerate(overview):
    with cols[i % 4]:
        st.markdown(
            f"""
            <div style="
                background:#FFFFFF;
                border:1px solid #D9E2EF;
                border-radius:10px;
                padding:15px;
                margin-bottom:12px;
                min-height:88px;">
                <div style="
                    color:#52749A;
                    font-size:0.8rem;
                    font-weight:600;">SECTION {number}</div>
                <div style="
                    color:#142D4E;
                    font-weight:600;
                    margin-top:6px;">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Consistent plotting defaults
plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#CBD5E1",
        "axes.labelcolor": "#344563",
        "xtick.color": "#526581",
        "ytick.color": "#526581",
        "text.color": "#142D4E",
        "axes.titleweight": "semibold",
        "font.size": 10,
    }
)

NAVY = "#214B75"
BLUE = "#477DB3"
GREEN = "#31866B"
ORANGE = "#D18A35"
RED = "#C45151"


def finish_plot(fig):
    """Apply consistent styling and display a Matplotlib figure."""
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def get_subsystem_total(result):
    """Sum the modeled subsystem loads returned by power_model.py."""
    subsystems = result["Subsystems"]
    return sum(
        subsystems[key]
        for key in ["Backlight", "Audio", "MainBoard", "Misc"]
    )


# ---------------------------------------------------------
# SECTION 1: PWM DUTY CYCLE VS LED CURRENT
# ---------------------------------------------------------

st.divider()
st.header("01. PWM Duty Cycle vs LED Current")

st.markdown(
    """
    Pulse Width Modulation (PWM) regulates average LED output by changing
    the fraction of each switching period during which the LEDs are driven.

    For a fixed LED current during the ON interval, average current is
    approximately proportional to duty cycle. Actual behaviour depends on
    the driver topology and its control circuitry.
    """
)

duty_points = np.array([0, 5, 10, 20, 40, 60, 80, 100], dtype=float)

current_points = np.array(
    [0, 7, 15, 31, 61, 91, 121, 150],
    dtype=float,
)

# Shape-preserving interpolation avoids cubic overshoot.
current_curve = PchipInterpolator(duty_points, current_points)

duty = np.linspace(0, 100, 300)
current = current_curve(duty)

fig, ax = plt.subplots(figsize=(9, 4.5))

ax.plot(
    duty,
    current,
    color=NAVY,
    linewidth=2.8,
    label="Illustrative LED-current relationship",
)

ax.scatter(
    duty_points,
    current_points,
    color=BLUE,
    s=32,
    zorder=3,
    label="Model data points",
)

ax.axvline(
    100,
    color=RED,
    linestyle="--",
    linewidth=1.6,
    label="Full-brightness reference",
)

ax.set_xlabel("PWM Duty Cycle (%)")
ax.set_ylabel("LED Current (mA)")
ax.set_title("PWM Duty Cycle and Average LED Current")
ax.set_xlim(0, 100)
ax.set_ylim(bottom=0)
ax.grid(True, alpha=0.2)
ax.legend(frameon=False)

finish_plot(fig)

st.markdown(
    """
    <div class="section-note">
    <b>Engineering interpretation</b><br>
    Reducing PWM duty cycle can reduce average LED current and backlight
    power. The plotted current values are illustrative model inputs;
    they are not measured values for a specific LED driver.
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# SECTION 2: LED DRIVER EFFICIENCY
# ---------------------------------------------------------

st.divider()
st.header("02. LED Driver Efficiency")

st.markdown(
    """
    The LED driver converts its input power into power delivered to the
    backlight. Its efficiency can vary with operating point, so the
    efficiency curve used by the Digital Twin affects its wall-power estimate.
    """
)

fig, ax = plt.subplots(figsize=(9, 4.5))

ax.plot(
    np.asarray(led_duty) * 100,
    np.asarray(led_eff) * 100,
    color=BLUE,
    linewidth=2.5,
    marker="o",
    markersize=4,
    label="Model efficiency curve",
)

ax.set_xlabel("PWM Duty Cycle (%)")
ax.set_ylabel("LED Driver Efficiency (%)")
ax.set_title("LED Driver Efficiency vs PWM Duty Cycle")
ax.grid(True, alpha=0.2)
ax.legend(frameon=False)

finish_plot(fig)

st.caption(
    "Interpret the curve according to the efficiency data encoded in "
    "power_model.py. Its physical accuracy depends on the source and "
    "validity of those data."
)

# ---------------------------------------------------------
# SECTION 3: SMPS EFFICIENCY
# ---------------------------------------------------------

st.divider()
st.header("03. SMPS Efficiency Curve")

st.markdown(
    """
    The switched-mode power supply (SMPS) converts mains-derived input
    power into the DC power required by the television subsystems.
    Its efficiency generally varies with load and converter design.
    """
)

fig, ax = plt.subplots(figsize=(9, 4.5))

ax.plot(
    np.asarray(smps_load) * 100,
    np.asarray(smps_eff) * 100,
    color=ORANGE,
    linewidth=2.5,
    marker="o",
    markersize=4,
    label="Model efficiency curve",
)

ax.set_xlabel("SMPS Load (%)")
ax.set_ylabel("SMPS Efficiency (%)")
ax.set_title("SMPS Efficiency vs Load")
ax.grid(True, alpha=0.2)
ax.legend(frameon=False)

finish_plot(fig)

st.info(
    "The model uses load-dependent SMPS efficiency to estimate conversion "
    "losses. This page does not assume a fixed rated-load value to infer "
    "the operating point; the actual load definition is implemented in "
    "power_model.py."
)

# ---------------------------------------------------------
# SECTION 4: CONTROLLER RESPONSE
# ---------------------------------------------------------

st.divider()
st.header("04. Controller Response")

st.markdown(
    """
    The controller combines ambient illumination and displayed-content
    brightness to calculate a recommended backlight setting. This section
    visualizes how its output changes as ambient illumination varies.
    """
)

ambient_values = np.arange(0, 101)
content_levels = [10, 30, 50, 70, 90]

fig, ax = plt.subplots(figsize=(9, 4.8))

for content_level in content_levels:
    brightness_values = [
        recommended_backlight(
            ambient_light=int(ambient),
            content_brightness=content_level,
            eco_mode=False,
        )
        for ambient in ambient_values
    ]

    ax.plot(
        ambient_values,
        brightness_values,
        linewidth=2,
        label=f"Content brightness = {content_level}%",
    )

ax.set_xlabel("Ambient Light Input (%)")
ax.set_ylabel("Recommended Backlight (%)")
ax.set_title("Controller Output Across Ambient-Light Conditions")
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.grid(True, alpha=0.2)
ax.legend(frameon=False, ncol=2)

finish_plot(fig)

st.markdown(
    """
    <div class="section-note">
    <b>Engineering interpretation</b><br>
    The graph displays the behaviour of the implemented control rule.
    It does not establish that the selected brightness is perceptually
    optimal; that would require display-performance and user-comfort testing.
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# SECTION 5: WALL POWER VS BACKLIGHT BRIGHTNESS
# ---------------------------------------------------------

st.divider()
st.header("05. Wall Power vs Backlight Brightness")

st.markdown(
    """
    This sweep varies backlight brightness while keeping volume and Wi-Fi
    settings fixed. It isolates the effect of the backlight input within
    the assumptions of the current power model.
    """
)

brightness_values = np.arange(10, 101)
wall_power_values = []

for brightness_pct in brightness_values:
    result = wall_power(
        brightness_pct=int(brightness_pct),
        volume_pct=40,
        wifi_on=True,
    )
    wall_power_values.append(result["WallPower"])

fig, ax = plt.subplots(figsize=(9, 4.5))

ax.plot(
    brightness_values,
    wall_power_values,
    color=GREEN,
    linewidth=2.8,
)

ax.set_xlabel("Backlight Brightness (%)")
ax.set_ylabel("Estimated Wall Power (W)")
ax.set_title("Estimated Wall Power vs Backlight Brightness")
ax.set_xlim(10, 100)
ax.set_ylim(bottom=0)
ax.grid(True, alpha=0.2)

finish_plot(fig)

st.caption(
    "These values are generated by the analytical model. The shape and "
    "magnitude of the curve depend on the subsystem-power assumptions and "
    "the LED-driver and SMPS efficiency curves."
)

# ---------------------------------------------------------
# SECTION 6: LIVE DIGITAL TWIN VALIDATION
# ---------------------------------------------------------

st.divider()
st.header("06. Digital Twin Operating-Point Comparison")

st.markdown(
    """
    Adjust the operating inputs below to compare a full-brightness reference
    with the controller-recommended setting. Both cases use the same volume
    and Wi-Fi settings, allowing the modeled difference to be attributed
    primarily to the backlight-control change.
    """
)

c1, c2, c3 = st.columns(3)

with c1:
    ambient_input = st.slider(
        "Ambient light (%)",
        min_value=0,
        max_value=100,
        value=50,
        key="validation_ambient",
    )

with c2:
    content_input = st.slider(
        "Content brightness (%)",
        min_value=0,
        max_value=100,
        value=40,
        key="validation_content",
    )

with c3:
    volume_input = st.slider(
        "Volume (%)",
        min_value=0,
        max_value=100,
        value=40,
        key="validation_volume",
    )

eco_mode = st.toggle(
    "Enable Eco Mode",
    value=False,
    key="validation_eco",
)

wifi_on = st.toggle(
    "Wi-Fi Enabled",
    value=True,
    key="validation_wifi",
)

recommended = recommended_backlight(
    ambient_light=ambient_input,
    content_brightness=content_input,
    eco_mode=eco_mode,
)

optimized_result = wall_power(
    brightness_pct=recommended,
    volume_pct=volume_input,
    wifi_on=wifi_on,
)

conventional_result = wall_power(
    brightness_pct=100,
    volume_pct=volume_input,
    wifi_on=wifi_on,
)

conventional_power = conventional_result["WallPower"]
optimized_power = optimized_result["WallPower"]

power_saved = conventional_power - optimized_power

saving_pct = (
    power_saved / conventional_power * 100
    if conventional_power > 0
    else 0
)

st.markdown("#### Operating conditions")

st.write(
    f"Ambient light: **{ambient_input}%** · "
    f"Content brightness: **{content_input}%** · "
    f"Volume: **{volume_input}%** · "
    f"Eco Mode: **{'On' if eco_mode else 'Off'}** · "
    f"Wi-Fi: **{'On' if wifi_on else 'Off'}**"
)

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Recommended Backlight",
    f"{recommended:.1f}%",
)

m2.metric(
    "Full-Brightness Reference",
    f"{conventional_power:.2f} W",
)

m3.metric(
    "Controller Setting",
    f"{optimized_power:.2f} W",
    delta=f"{optimized_power - conventional_power:+.2f} W",
    delta_color="inverse",
)

m4.metric(
    "Predicted Power Reduction",
    f"{saving_pct:.2f}%",
)

comparison_df = pd.DataFrame(
    {
        "Operating Case": [
            "Full-brightness reference",
            "Controller-recommended setting",
        ],
        "Backlight (%)": [
            100,
            recommended,
        ],
        "Estimated Wall Power (W)": [
            conventional_power,
            optimized_power,
        ],
    }
)

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True,
)

fig, ax = plt.subplots(figsize=(8, 4))

bars = ax.bar(
    ["Full-brightness\nreference", "Controller-\nrecommended"],
    [conventional_power, optimized_power],
    color=[BLUE, GREEN],
    width=0.55,
)

ax.set_ylabel("Estimated Wall Power (W)")
ax.set_title("Comparison of Predicted Operating Points")
ax.set_ylim(
    0,
    max(conventional_power, optimized_power) * 1.2
    if max(conventional_power, optimized_power) > 0
    else 1,
)
ax.grid(axis="y", alpha=0.2)

for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{height:.2f} W",
        ha="center",
        va="bottom",
        fontsize=9,
    )

finish_plot(fig)

st.caption(
    "The full-brightness reference is a modeled baseline, not a measured "
    "conventional television. The percentage reduction is conditional on "
    "the implemented controller and power-model assumptions."
)

# ---------------------------------------------------------
# SECTION 7: ENGINEERING VALIDATION FLOW
# ---------------------------------------------------------

st.divider()
st.header("07. Engineering Validation Flow")

st.markdown(
    """
    The model links a control decision to an estimated electrical outcome
    through the following sequence:
    """
)

flow_cols = st.columns(5)

flow_steps = [
    ("01", "Input conditions", "Ambient light and content brightness"),
    ("02", "Controller", "Recommended backlight level"),
    ("03", "LED subsystem", "Estimated backlight demand"),
    ("04", "Conversion stages", "LED-driver and SMPS losses"),
    ("05", "Power estimate", "Predicted wall power"),
]

for col, (number, title, description) in zip(flow_cols, flow_steps):
    with col:
        st.markdown(
            f"""
            <div style="
                background:#FFFFFF;
                border:1px solid #D9E2EF;
                border-radius:10px;
                padding:15px;
                min-height:145px;">
                <div style="color:#52749A;font-weight:700;">
                    {number}
                </div>
                <div style="
                    color:#142D4E;
                    font-weight:700;
                    margin:8px 0;">{title}</div>
                <div style="color:#526581;font-size:0.9rem;">
                    {description}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("")

st.success(
    "The implementation connects controller output, subsystem-power "
    "estimates and conversion-efficiency curves to calculate predicted "
    "wall power. This demonstrates internal consistency of the software model."
)

st.warning(
    "Internal consistency is not the same as experimental validation. "
    "Measured hardware power, calibrated efficiency data or independent "
    "circuit simulation would be needed to quantify real-world accuracy."
)

# ---------------------------------------------------------
# SECTION 8: SUBSYSTEM POWER BALANCE
# ---------------------------------------------------------

st.divider()
st.header("08. Subsystem Power Balance Verification")

st.markdown(
    """
    The following representative scenarios compare the estimated power
    assigned to each subsystem with the model's overall wall-power output.
    Scenario inputs are illustrative operating conditions.
    """
)

scenarios = [
    ("Movie Night", 20, 20, 30),
    ("Living Room", 50, 40, 40),
    ("Streaming", 60, 70, 40),
    ("Gaming", 80, 80, 60),
    ("Sports", 90, 90, 70),
]

rows = []

for name, ambient, content, volume in scenarios:
    brightness_pct = recommended_backlight(
        ambient_light=ambient,
        content_brightness=content,
        eco_mode=False,
    )

    result = wall_power(
        brightness_pct=brightness_pct,
        volume_pct=volume,
        wifi_on=True,
    )

    subsystems = result["Subsystems"]
    subsystem_total = get_subsystem_total(result)

    rows.append(
        {
            "Scenario": name,
            "Ambient (%)": ambient,
            "Content (%)": content,
            "Volume (%)": volume,
            "Brightness (%)": round(float(brightness_pct), 2),
            "Backlight (W)": round(subsystems["Backlight"], 2),
            "Audio (W)": round(subsystems["Audio"], 2),
            "Mainboard (W)": round(subsystems["MainBoard"], 2),
            "Misc (W)": round(subsystems["Misc"], 2),
            "Subsystem Total (W)": round(subsystem_total, 2),
            "Estimated Wall Power (W)": round(result["WallPower"], 2),
        }
    )

df = pd.DataFrame(rows)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
)

st.markdown("#### Subsystem power distribution")

fig = go.Figure()

subsystem_columns = [
    ("Backlight (W)", "Backlight"),
    ("Audio (W)", "Audio"),
    ("Mainboard (W)", "Mainboard"),
    ("Misc (W)", "Miscellaneous"),
]

for column, label in subsystem_columns:
    fig.add_bar(
        name=label,
        x=df["Scenario"],
        y=df[column],
    )

fig.update_layout(
    barmode="stack",
    title="Estimated Subsystem Power Across Viewing Scenarios",
    xaxis_title="Viewing Scenario",
    yaxis_title="Estimated Subsystem Power (W)",
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(color="#142D4E"),
    legend_title="Subsystem",
    margin=dict(l=20, r=20, t=60, b=20),
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

# Compare the model's own subsystem and wall-power outputs.
df["Conversion Difference (W)"] = (
    df["Estimated Wall Power (W)"] - df["Subsystem Total (W)"]
).round(2)

st.markdown("#### Power balance comparison")

st.dataframe(
    df[
        [
            "Scenario",
            "Subsystem Total (W)",
            "Estimated Wall Power (W)",
            "Conversion Difference (W)",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

st.info(
    "The conversion difference is calculated from the two outputs returned "
    "by the current model. It should not automatically be interpreted as "
    "a separately measured conversion loss. Its exact meaning depends on "
    "the equations implemented in power_model.py."
)

st.markdown(
    """
    **Interpretation:** The subsystem chart shows how the model allocates
    power among the backlight, audio, mainboard and miscellaneous loads.
    Comparing the subsystem sum with estimated wall power provides a useful
    consistency check, but does not independently verify the accuracy of
    the underlying load or efficiency assumptions.
    """
)

# ---------------------------------------------------------
# FINAL CONCLUSION
# ---------------------------------------------------------

st.divider()
st.header("Conclusion")

st.markdown(
    """
    The Circuit Validation page examines the relationships connecting
    adaptive backlight control to estimated television power consumption.

    The analysis covers the PWM-current relationship, LED-driver efficiency,
    SMPS efficiency, controller response, wall-power variation and subsystem
    power balance. Together, these checks show how the implemented software
    model produces its power-saving estimates.
    """
)

st.markdown(
    """
    <div class="section-note">
    <b>Validation status</b><br>
    The current implementation demonstrates analytical model behaviour and
    internal consistency. Quantitative claims about a real television's
    efficiency or energy savings require comparison against measured power
    data or an independently validated electrical simulation.
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Digital Twin project · Analytical power modelling · Adaptive LED backlight control"
)
```
