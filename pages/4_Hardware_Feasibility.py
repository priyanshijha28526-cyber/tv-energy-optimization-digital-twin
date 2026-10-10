
import streamlit as st
import pandas as pd
import plotly.express as px


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Hardware Feasibility | TV Energy Digital Twin",
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
        <h1>Hardware Feasibility</h1>
        <p>
            Proposed hardware architecture, integration
            requirements and engineering considerations
            for real-world TV energy optimization.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

with st.expander("Scope of this feasibility study"):
    st.write(
        """
        This page presents a conceptual implementation pathway
        for translating the software digital twin into a physical
        smart-TV control system.

        The current project models power consumption and controller
        behaviour in software. It does not demonstrate a completed
        hardware integration or measured power savings on a physical TV.

        Actual feasibility depends on access to the TV's firmware,
        LED-driver interface, processor resources and hardware design.
        """ 
    )


# --------------------------------------------------
# FEASIBILITY OVERVIEW
# --------------------------------------------------

st.markdown(
    '<div class="section-label">Feasibility Overview</div>',
    unsafe_allow_html=True
)

c1, c2, c3 = st.columns(3)

c1.metric(
    "Potential Sensor Addition",
    "BH1750",
    help="Candidate ambient-light sensor for a physical prototype."
)

c2.metric(
    "Control Software",
    "Modification",
    help="Controller integration would need to be implemented and tested."
)

c3.metric(
    "PCB Redesign",
    "To Be Assessed",
    help="Depends on available interfaces, power and physical integration."
)


st.info(
    """
    Feasibility status: conceptual proposal. The component choices
    and implementation pathway require validation against the
    specifications and interfaces of a target television.
    """
)


# --------------------------------------------------
# SYSTEM ARCHITECTURE
# --------------------------------------------------

st.markdown("---")

st.markdown(
    '<div class="section-label">System Design</div>',
    unsafe_allow_html=True
)

st.subheader("System Architecture")

try:
    st.image(
        "Assets/architecture.png",
        use_container_width=True
    )

    st.caption(
        "Conceptual digital twin architecture for smart-TV "
        "backlight optimization."
    )

except Exception:
    st.warning(
        "The architecture image could not be loaded. "
        "Check that Assets/architecture.png exists in the "
        "repository and that its capitalization matches exactly."
    )

with st.expander("Architecture explanation"):
    st.write(
        """
        1. Ambient-light input represents the brightness of the room.
        2. Content-brightness estimation represents the brightness
           of the displayed video content.
        3. The controller combines these inputs to recommend a
           backlight level.
        4. A compatible TV control interface would translate the
           recommendation into a command for the LED backlight driver.
        5. The resulting power consumption would need to be measured
           to validate the software model.
        """
    )


# --------------------------------------------------
# HARDWARE REQUIREMENTS
# --------------------------------------------------

st.markdown("---")
st.subheader("Required Hardware and Interfaces")

hardware = pd.DataFrame({
    "Component": [
        "Ambient Light Sensor",
        "TV Main SoC",
        "LED Driver",
        "SMPS",
        "Backlight LEDs"
    ],
    "Purpose": [
        "Measure surrounding illumination",
        "Run control software and process available inputs",
        "Regulate backlight current and brightness",
        "Convert input power into required DC rails",
        "Provide display illumination"
    ],
    "Candidate Device / Type": [
        "BH1750 digital sensor",
        "Existing TV processor, if accessible",
        "Compatible programmable LED driver",
        "Existing TV power supply",
        "Existing white LED array"
    ],
    "Potential Modification": [
        "Sensor interface and placement",
        "Firmware or software integration",
        "Control-interface integration",
        "Assess existing supply capacity",
        "Validate brightness-control compatibility"
    ]
})

st.dataframe(
    hardware.set_index("Component"),
    use_container_width=True
)

st.caption(
    "These are candidate components and integration requirements. "
    "Exact compatibility must be confirmed against the selected "
    "television's schematics and component datasheets."
)


# --------------------------------------------------
# AMBIENT LIGHT SENSOR
# --------------------------------------------------

st.markdown("---")
st.subheader("Sensor Requirements")

sensor_col, sensor_info_col = st.columns([1, 1])

with sensor_col:
    st.markdown("#### Candidate sensor options")

    sensors = pd.DataFrame({
        "Sensor": [
            "BH1750",
            "TEMT6000",
            "LDR circuit"
        ],
        "Interface / Output": [
            "Digital I²C",
            "Analog output",
            "Resistance-based circuit"
        ],
        "Potential Use": [
            "Digital lux measurement",
            "Basic light-level sensing",
            "Low-cost experimental prototype"
        ]
    })

    st.dataframe(
        sensors.set_index("Sensor"),
        use_container_width=True
    )

with sensor_info_col:
    st.markdown("#### Integration considerations")

    st.write(
        """
        **BH1750:** A candidate digital ambient-light sensor
        with an I²C interface and lux-oriented output.

        **TEMT6000:** A phototransistor-based option whose output
        requires suitable measurement circuitry and calibration.

        **LDR:** A low-cost option for a prototype, but its
        resistance-to-light relationship requires calibration.
        """
    )

    st.warning(
        """
        Sensor selection should consider measurement range,
        placement, display light leakage, electrical interface
        and compatibility with the target TV processor.
        """ 
    )


# --------------------------------------------------
# SOFTWARE REQUIREMENTS
# --------------------------------------------------

st.markdown("---")
st.subheader("Software and Firmware Requirements")

software = pd.DataFrame({
    "Function": [
        "Ambient-light acquisition",
        "Content-brightness estimation",
        "Optimization controller",
        "Backlight control",
        "Power monitoring",
        "Safety and user controls"
    ],
    "Implementation Consideration": [
        "Read and calibrate sensor measurements",
        "Access decoded video frames or available brightness metadata",
        "Execute the control algorithm",
        "Use a supported LED-driver interface",
        "Measure actual power or validate against model estimates",
        "Preserve user settings and safe operating limits"
    ]
})

st.dataframe(
    software.set_index("Function"),
    use_container_width=True
)

st.info(
    """
    Content brightness estimation may be possible in software
    without adding a dedicated sensor, but it is not automatically
    accessible to third-party applications. Access to decoded
    frames, processor APIs and firmware may be required.
    """ 
)


# --------------------------------------------------
# IMPLEMENTATION FLOW
# --------------------------------------------------

st.markdown("---")
st.markdown(
    '<div class="section-label">Implementation Pathway</div>',
    unsafe_allow_html=True
)

st.subheader("Proposed Implementation Flow")

steps = [
    (
        "01",
        "Read ambient light",
        "Acquire and calibrate the ambient-light measurement."
    ),
    (
        "02",
        "Estimate content brightness",
        "Obtain a suitable frame-brightness measure or metadata."
    ),
    (
        "03",
        "Run the controller",
        "Combine the input signals using the optimization algorithm."
    ),
    (
        "04",
        "Calculate backlight command",
        "Generate a recommendation within supported brightness limits."
    ),
    (
        "05",
        "Interface with LED driver",
        "Apply the command through a compatible hardware or firmware interface."
    ),
    (
        "06",
        "Measure power consumption",
        "Compare actual input power against a conventional baseline."
    ),
    (
        "07",
        "Validate performance",
        "Assess energy savings, picture quality and brightness stability."
    )
]

for i in range(0, len(steps), 2):
    columns = st.columns(2)

    for j, column in enumerate(columns):
        index = i + j

        if index < len(steps):
            number, title, description = steps[index]

            with column:
                with st.container(border=True):
                    st.markdown(
                        f"**{number} | {title}**"
                    )
                    st.write(description)


# --------------------------------------------------
# POWER DISTRIBUTION
# --------------------------------------------------

st.markdown("---")
st.subheader("Illustrative TV Subsystem Power Distribution")

power = pd.DataFrame({
    "Subsystem": [
        "Backlight",
        "Mainboard",
        "Audio",
        "Wi-Fi",
        "Miscellaneous"
    ],
    "Illustrative Share (%)": [
        50,
        20,
        10,
        5,
        15
    ]
})

fig = px.pie(
    power,
    values="Illustrative Share (%)",
    names="Subsystem",
    hole=0.55,
    title="Illustrative Power Distribution"
)

fig.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "Illustrative share: %{value}%<extra></extra>"
    )
)

fig.update_layout(
    height=420,
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(
        family="Arial",
        color="#172033"
    ),
    margin=dict(l=25, r=25, t=65, b=25),
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="hardware_power_distribution"
)

st.caption(
    "The percentages are illustrative assumptions and are not "
    "measured values from the TV under study. Actual power "
    "distribution varies by model, panel size and operating conditions."
)


# --------------------------------------------------
# ADVANTAGES
# --------------------------------------------------

st.markdown("---")
st.subheader("Potential Advantages")

advantages = [
    (
        "Backlight-focused optimization",
        "Targets a subsystem whose power demand can vary with brightness."
    ),
    (
        "Reuse of existing components",
        "May use the existing processor, LED driver and power supply "
        "if their interfaces support the proposed control."
    ),
    (
        "Software-based control",
        "The controller can be evaluated in simulation before hardware integration."
    ),
    (
        "Scalable development pathway",
        "The software model provides a starting point for later prototype testing."
    ),
    (
        "Picture-quality constraints",
        "Brightness limits and user preferences can be incorporated into the controller."
    )
]

for title, description in advantages:
    st.markdown(f"**{title}**")
    st.write(description)


# --------------------------------------------------
# ENGINEERING CHALLENGES
# --------------------------------------------------

st.markdown("---")
st.subheader("Engineering Challenges")

challenges = pd.DataFrame({
    "Challenge": [
        "Backlight response delay",
        "User comfort and perception",
        "Panel-to-panel variation",
        "Brightness fluctuation",
        "Picture quality",
        "Hardware access"
    ],
    "Consideration": [
        "Measure response time and avoid unstable control.",
        "Test brightness transitions under different room conditions.",
        "Calibrate for different display and driver characteristics.",
        "Use filtering, hysteresis or transition limits where appropriate.",
        "Check colour appearance, visibility and HDR behaviour.",
        "Confirm access to firmware and a supported driver interface."
    ]
})

st.dataframe(
    challenges.set_index("Challenge"),
    use_container_width=True
)


# --------------------------------------------------
# FUTURE WORK
# --------------------------------------------------

st.markdown("---")
st.subheader("Future Work")

future_work = [
    "Build a hardware-in-the-loop prototype.",
    "Integrate an ambient-light sensor and validate its readings.",
    "Test the controller with a compatible LED-driver interface.",
    "Measure wall power under controlled viewing conditions.",
    "Evaluate brightness stability and user-perceived picture quality.",
    "Explore adaptive content analysis and user-preference settings.",
    "Compare measured power consumption with digital twin predictions."
]

for item in future_work:
    st.markdown(f"- {item}")


# --------------------------------------------------
# CONCLUSION
# --------------------------------------------------

st.markdown("---")
st.subheader("Conclusion")

st.write(
    """
    The proposed digital twin provides a software foundation for
    investigating intelligent TV backlight optimization. A physical
    implementation could use an ambient-light sensor, an accessible
    processor and a compatible LED-driver control interface.

    The extent of hardware modification cannot be confirmed without
    reviewing the target television's design and interfaces.
    Hardware integration, measured power testing and picture-quality
    validation are the next steps required to establish real-world
    feasibility.
    """
)

st.caption(
    "TV Energy Optimization Digital Twin | Hardware Feasibility"
)
