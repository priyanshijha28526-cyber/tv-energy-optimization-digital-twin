
import streamlit as st
import pandas as pd
import plotly.express as px

from power_model import wall_power
from controller import recommended_backlight


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Annual Impact | TV Energy Digital Twin",
    page_icon=None,
    layout="wide"
)


# --------------------------------------------------
# TARIFF ASSUMPTIONS
# --------------------------------------------------
# Indicative residential rates for scenario modelling.
# These are NOT guaranteed official tariffs for every
# DISCOM, consumption slab or subsidy category.
#
# Rates should be reviewed against current tariff orders
# before being presented as verified official data.
#
# Some values are representative assumptions where a
# sufficiently clear comparable rate was not available.
# Users can adjust the selected rate in the dashboard.

TARIFFS = {
    "Andhra Pradesh": 4.50,
    "Arunachal Pradesh": 4.00,
    "Assam": 5.50,
    "Bihar": 5.25,
    "Chhattisgarh": 5.00,
    "Goa": 4.50,
    "Gujarat": 4.50,
    "Haryana": 5.50,
    "Himachal Pradesh": 5.00,
    "Jharkhand": 7.00,
    "Karnataka": 5.90,
    "Kerala": 5.50,
    "Madhya Pradesh": 5.50,
    "Maharashtra": 8.00,
    "Manipur": 5.00,
    "Meghalaya": 4.50,
    "Mizoram": 4.00,
    "Nagaland": 4.50,
    "Odisha": 4.50,
    "Punjab": 5.50,
    "Rajasthan": 6.00,
    "Sikkim": 4.00,
    "Tamil Nadu": 5.00,
    "Telangana": 5.50,
    "Tripura": 4.50,
    "Uttar Pradesh": 5.50,
    "Uttarakhand": 5.00,
    "West Bengal": 5.50,
    "Andaman and Nicobar Islands": 4.00,
    "Chandigarh": 4.00,
    "Dadra and Nagar Haveli and Daman and Diu": 4.50,
    "Delhi": 5.50,
    "Jammu and Kashmir": 4.00,
    "Ladakh": 4.00,
    "Lakshadweep": 4.00,
    "Puducherry": 4.50
}

TARIFF_SOURCE = (
    "https://electricbillcalculate.in/"
    "all-states-electricity-calculators.html"
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
        <h1>Annual Impact Analysis</h1>
        <p>
            Estimate yearly energy savings, electricity-cost
            reduction and potential environmental impact.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

with st.expander("About this analysis and its assumptions"):
    st.write(
        """
        This page estimates the annual impact of TV backlight
        optimization using the project's power model.

        The model compares a conventional TV operating at 100%
        backlight brightness with an optimized operating point
        selected by the controller.

        The electricity-cost estimate uses a representative
        residential rate selected for the chosen state or UT.
        It is not a full household electricity-bill calculation.
        """

    )

    st.markdown(
        f"[Tariff reference: All States Electricity Calculators]({TARIFF_SOURCE})"
    )

    st.warning(
        """
        Actual electricity bills may differ because of monthly
        consumption slabs, the local DISCOM, fixed charges,
        electricity duty, fuel adjustments, meter charges,
        government subsidies and tariff revisions. The rates
        supplied here are indicative modelling assumptions,
        not verified tariff orders for every jurisdiction.
        """
    )


# --------------------------------------------------
# USAGE INPUT
# --------------------------------------------------

st.markdown(
    '<div class="section-label">Usage Assumptions</div>',
    unsafe_allow_html=True
)

daily_hours = st.slider(
    "Average TV Usage (hours per day)",
    min_value=1,
    max_value=12,
    value=4,
    step=1
)

st.caption(
    "Annual usage is calculated using 365 days per year."
)


# --------------------------------------------------
# STATE / UT SELECTION AND TARIFF
# --------------------------------------------------

st.markdown("---")
st.subheader("Electricity Tariff Settings")

state_col, tariff_col = st.columns([1.2, 1])

with state_col:
    state = st.selectbox(
        "Select State or Union Territory",
        options=list(TARIFFS.keys()),
        index=list(TARIFFS.keys()).index("Tamil Nadu")
    )

with tariff_col:
    default_tariff = TARIFFS[state]

    tariff = st.number_input(
        "Indicative residential tariff (₹/kWh)",
        min_value=0.0,
        max_value=50.0,
        value=float(default_tariff),
        step=0.25,
        format="%.2f",
        help=(
            "Editable estimate used for this calculation. "
            "Check the applicable DISCOM tariff and household "
            "slab before treating this as an actual bill rate."
        )
    )

st.caption(
    f"Selected jurisdiction: {state}. "
    f"Rate used in this estimate: ₹{tariff:.2f}/kWh."
)

with st.expander("Tariff source, coverage and limitations"):
    st.markdown(
        f"[Open the tariff reference website]({TARIFF_SOURCE})"
    )

    st.write(
        """
        The reference website presents state-wise electricity
        calculators and approximate residential rates. A single
        representative rate cannot reproduce every household's
        bill.

        The editable value above is a simplified rate for
        estimating the financial value of TV energy savings.
        It does not calculate slab-by-slab household billing.

        Before describing a rate as official, verify the applicable
        tariff order for the consumer's DISCOM, connection category,
        billing period and consumption level.
        """
    )


# --------------------------------------------------
# TV OPERATING CONDITIONS
# --------------------------------------------------

st.markdown("---")
st.subheader("TV Operating Conditions")

control_col, status_col = st.columns([1, 1])

with control_col:
    ambient = st.slider(
        "Representative Ambient Light (%)",
        min_value=0,
        max_value=100,
        value=50,
        help="Used as the representative ambient-light input."
    )

    content = st.slider(
        "Representative Content Brightness (%)",
        min_value=0,
        max_value=100,
        value=50,
        help="Used as the representative content-brightness input."
    )

with status_col:
    volume = st.slider(
        "Representative Volume (%)",
        min_value=0,
        max_value=100,
        value=50
    )

    wifi = st.checkbox(
        "Wi-Fi Enabled",
        value=True
    )

    eco = st.checkbox(
        "Eco Mode Enabled",
        value=False
    )


# --------------------------------------------------
# POWER MODEL CALCULATIONS
# --------------------------------------------------

brightness = recommended_backlight(
    ambient,
    content,
    eco
)

optimized = wall_power(
    brightness_pct=brightness,
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
    saving_percent = (
        power_saved / conventional_power
    ) * 100
else:
    saving_percent = 0.0


# --------------------------------------------------
# ANNUAL ENERGY CALCULATIONS
# --------------------------------------------------

annual_energy_normal = (
    conventional_power * daily_hours * 365
) / 1000

annual_energy_optimized = (
    optimized_power * daily_hours * 365
) / 1000

annual_saved = (
    annual_energy_normal - annual_energy_optimized
)

money_saved = annual_saved * tariff

# Illustrative grid emissions factor.
# Replace with a current, appropriately sourced factor
# if reporting this as an official emissions estimate.
co2_factor = 0.82  # kg CO2 per kWh

co2_saved = annual_saved * co2_factor

# Illustrative equivalence only; not a direct measurement.
tree_equivalence_factor = 21  # kg CO2 per tree-year
trees = co2_saved / tree_equivalence_factor


# --------------------------------------------------
# TOP-LEVEL METRICS
# --------------------------------------------------

st.markdown("---")
st.markdown(
    '<div class="section-label">Annual Impact Overview</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Annual Energy Saved",
    f"{annual_saved:.2f} kWh"
)

c2.metric(
    "Estimated Cost Saved",
    f"₹{money_saved:,.0f}"
)

c3.metric(
    "Estimated CO₂ Avoided",
    f"{co2_saved:.2f} kg"
)

c4.metric(
    "Tree-Year Equivalent",
    f"{trees:.2f}"
)


# --------------------------------------------------
# POWER AND ENERGY SUMMARY
# --------------------------------------------------

st.subheader("Annual Energy Comparison")

energy_df = pd.DataFrame({
    "Operating Condition": [
        "Conventional TV",
        "Optimized TV",
        "Energy Saved"
    ],
    "Annual Energy (kWh)": [
        annual_energy_normal,
        annual_energy_optimized,
        annual_saved
    ]
})

energy_display = energy_df.copy()
energy_display["Annual Energy (kWh)"] = (
    energy_display["Annual Energy (kWh)"].round(2)
)

st.dataframe(
    energy_display.set_index("Operating Condition"),
    use_container_width=True
)


# --------------------------------------------------
# ENERGY DISTRIBUTION CHART
# --------------------------------------------------

st.subheader("Annual Energy Distribution")

energy_chart = pd.DataFrame({
    "Category": [
        "Optimized TV Energy",
        "Energy Saved"
    ],
    "Energy (kWh)": [
        max(annual_energy_optimized, 0),
        max(annual_saved, 0)
    ]
})

fig1 = px.pie(
    energy_chart,
    values="Energy (kWh)",
    names="Category",
    hole=0.55,
    title="Optimized Energy Use vs Energy Saved",
    color_discrete_map={
        "Optimized TV Energy": "#64748B",
        "Energy Saved": "#0F766E"
    }
)

fig1.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "%{value:.2f} kWh/year<br>"
        "%{percent}<extra></extra>"
    )
)

fig1.update_layout(
    height=400,
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
    fig1,
    use_container_width=True,
    key="annual_energy_donut"
)


# --------------------------------------------------
# POWER SAVINGS STATUS
# --------------------------------------------------

st.subheader("Model Results")

st.write(
    f"""
    At the selected operating conditions, the controller
    recommends a backlight level of **{brightness:.1f}%**.

    Conventional wall power is estimated at
    **{conventional_power:.2f} W**, compared with
    **{optimized_power:.2f} W** in the optimized case.

    The model estimates **{annual_saved:.2f} kWh** of annual
    energy savings at {daily_hours} hours of TV usage per day.
    """
)

if saving_percent > 0:
    st.success(
        f"The model estimates a {saving_percent:.1f}% reduction "
        "in TV wall power under the selected operating conditions."
    )
elif saving_percent == 0:
    st.info(
        "The selected operating conditions produce no estimated "
        "power reduction against the conventional baseline."
    )
else:
    st.warning(
        "The optimized case consumes more power than the "
        "conventional baseline under the selected conditions."
    )


# --------------------------------------------------
# NATIONAL-SCALE ILLUSTRATION
# --------------------------------------------------

st.markdown("---")
st.subheader("Illustrative National-Scale Impact")

number_of_tvs = st.number_input(
    "Number of TVs adopting the optimization",
    min_value=1,
    max_value=100_000_000,
    value=1_000_000,
    step=100_000
)

grid_energy_saved_mwh = (
    annual_saved * number_of_tvs / 1000
)

grid_energy_saved_gwh = (
    grid_energy_saved_mwh / 1000
)

grid_co2_saved_tonnes = (
    co2_saved * number_of_tvs / 1000
)

# Illustrative annual household electricity consumption.
household_annual_kwh = 1200

equivalent_homes = (
    annual_saved * number_of_tvs / household_annual_kwh
)

n1, n2, n3 = st.columns(3)

n1.metric(
    "Annual Energy Saved",
    f"{grid_energy_saved_gwh:,.3f} GWh"
)

n2.metric(
    "Estimated CO₂ Avoided",
    f"{grid_co2_saved_tonnes:,.1f} tonnes"
)

n3.metric(
    "Household-Energy Equivalent",
    f"{equivalent_homes:,.0f} homes"
)

st.caption(
    "National-scale values are linear extrapolations of the "
    "selected single-TV scenario. They are illustrative, not "
    "a forecast of actual nationwide adoption or realised savings."
)


# --------------------------------------------------
# OBSERVATIONS AND LIMITATIONS
# --------------------------------------------------

st.markdown("---")
st.subheader("Observations and Limitations")

with st.expander("Interpretation of the results", expanded=True):
    st.write(
        """
        Annual energy savings scale with daily TV usage because
        the model assumes the selected operating conditions and
        estimated power difference persist throughout the viewing
        period.

        The rupee estimate is calculated by multiplying annual
        energy saved by the selected representative tariff.

        The CO₂ estimate uses an illustrative grid-emissions factor.
        The tree-year figure is only an equivalence based on the
        stated assumption; it does not represent a measured number
        of trees needed to offset emissions.
        """
    )

    st.warning(
        """
        This dashboard is not a full electricity-bill calculator.
        It does not model the household's existing monthly
        consumption slabs, fixed charges, electricity duty,
        fuel adjustment charges, subsidies or all local DISCOM
        rules. Those components may affect the actual bill impact.

        The savings and environmental impact are software-model
        estimates, not measurements from a physical TV prototype.
        """
    )


# --------------------------------------------------
# SOURCES
# --------------------------------------------------

st.markdown("---")
st.subheader("References")

st.markdown(
    f"""
    - [Electricity Bill Calculator — All States and UTs]({TARIFF_SOURCE})
    """
)

st.caption(
    "Tariff values are editable indicative assumptions. "
    "Check the current tariff order and applicable DISCOM schedule "
    "before using a value as an official residential rate."
)

st.markdown("---")

st.caption(
    "TV Energy Optimization Digital Twin | Annual Impact Analysis"
)
