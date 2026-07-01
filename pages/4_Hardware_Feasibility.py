import streamlit as st
import pandas as pd
import plotly.express as px

st.title(" Hardware Feasibility")
c1,c2,c3 = st.columns(3)

c1.metric(
    "Additional components",
    "BH1750 Sensor"
)

c2.metric(
    "Firmware Changes",
    "Required"
)

c3.metric(
    "PCB Redesign",
    "Not Required"
)

st.write(
    """
    This page explains how the proposed
    TV Energy Optimization Digital Twin
    could be implemented in a real
    smart television.
    """
)

st.divider()

st.subheader("System Architecture")

st.image(
    "Assets/architecture.png",
    use_container_width=True
)
st.caption(
    """
    Digital Twin Architecture for Smart TV Energy Optimization.
    The controller combines ambient light information and video
    frame brightness estimation to dynamically adjust LED
    backlight intensity and reduce overall power consumption.
    """
)

st.divider()

st.header("Required Hardware")

hardware = pd.DataFrame({

    "Component":[
        "Ambient Light Sensor",
        "TV Main SoC",
        "LED Driver",
        "SMPS",
        "Backlight LEDs"
    ],

    "Purpose":[
        "Measure room brightness",
        "Run optimization algorithm",
        "Control LED brightness",
        "Supply regulated power",
        "Display illumination"
    ],

    "Typical Device":[
        "BH1750",
        "MediaTek / Realtek SoC",
        "LP8551",
        "Flyback SMPS",
        "White LED Array"
    ],

    "Modification Required":[
        "Optional",
        "Software",
        "Firmware",
        "None",
        "None"
    ]

})

st.dataframe(
    hardware.set_index("Component")
)

st.divider()

st.header("Sensor Requirements")

st.info(
    """
    Recommended Sensor Options

• BH1750 Digital Ambient Light Sensor (Preferred)

• TEMT6000 Ambient Light Sensor

• Low-cost LDR Circuit (Prototype)

The BH1750 provides calibrated lux measurements
and communicates via I²C, making it suitable for
integration into modern smart televisions.
    """
)

st.divider()

st.header("Software Requirements")

st.success(
    """
    No additional hardware is required
    for content brightness estimation.

    Average frame brightness can be
    calculated directly from the
    video stream using the TV's
    existing processor.
    """
)

st.divider()

st.header("Implementation Flow")

st.subheader(
    "Implementation Flow"
)

st.markdown(
    """
### Step 1
Read Ambient Light Sensor

### Step 2
Estimate Frame Brightness

### Step 3
Run Optimization Controller

### Step 4
Calculate Recommended Backlight

### Step 5
Update LED Driver PWM Duty Cycle

### Step 6
Reduce Backlight Power Consumption

### Step 7
Monitor Energy Savings
"""
)


st.divider()

st.header("Power Flow in Television")

power = pd.DataFrame({
    "Subsystem":[
        "Backlight",
        "MainBoard",
        "Audio",
        "WiFi",
        "Misc"
    ],
    "Importance":[
        50,
        20,
        10,
        5,
        15
    ]
})

fig = px.pie(
    power,
    values="Importance",
    names="Subsystem",
    title="Typical Power Distribution"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

st.header("Advantages")

st.success(
    """
     *No redesign of TV architecture

     *Uses existing video processing hardware

     * Low implementation cost

     *Improves energy efficiency

     *Can be added through firmware updates

     *Compatible with existing LED TV designs
     *Maintaining color consistency during dynamic dimming
    """
)

st.divider()

st.header("Engineering Challenges")

st.warning(
    """
    • Backlight response delay

    • User comfort and brightness perception

    • Calibration across different panel types

    • Avoiding frequent brightness fluctuations

    • Maintaining picture quality while saving power
    """
)

st.divider()

st.header("Future Work")

st.markdown(
    """
    - Machine Learning based brightness prediction

    - Viewer preference learning

    - Dynamic HDR optimization

    - Cloud analytics integration

    - Smart home energy management integration
    """
)

st.divider()

st.header("Conclusion")

st.success(
    """
    The proposed Digital Twin can be implemented
using commercially available LED television
hardware with only minor firmware and control
algorithm modifications.

The approach therefore represents a practical
energy optimization strategy for future smart
television platforms.
    """
)
st.caption(
    """
    Home-equivalent calculation assumes
    average household consumption of
    approximately 1200 kWh/year.
    """
)


