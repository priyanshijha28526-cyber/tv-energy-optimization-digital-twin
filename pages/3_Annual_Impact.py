import streamlit as st
from power_model import wall_power
from controller import recommended_backlight

st.title("Annual Impact Analysis")

st.write(
    """
    Estimate annual energy savings
    achieved through intelligent
    TV backlight optimization.
    """
)

daily_hours = st.slider(
    "Average TV Usage (hours/day)",
    1,
    12,
    4
)
st.subheader("Electricity Tariff Settings")

state = st.selectbox(
    "Select State",
    [
        "Maharashtra",
        "Karnataka",
        "Delhi",
        "Tamil Nadu",
        "Uttar Pradesh",
        "Gujarat",
        "West Bengal",
        "Rajasthan",
        "Punjab"
    ]
)
if state == "Maharashtra":
    tariff = st.slider(
        "Electricity Tariff (₹/kWh)",
        4.43,
        14.33,
        8.00
    )

elif state == "Karnataka":
    tariff = st.slider(
        "Electricity Tariff (₹/kWh)",
        4.75,
        9.50,
        7.00
    )

elif state == "Delhi":
    tariff = st.slider(
        "Electricity Tariff (₹/kWh)",
        3.00,
        8.00,
        6.00
    )

elif state == "Tamil Nadu":
    tariff = st.slider(
        "Electricity Tariff (₹/kWh)",
        4.95,
        9.95,
        7.00
    )

elif state == "Uttar Pradesh":
    tariff = st.slider(
        "Electricity Tariff (₹/kWh)",
        3.35,
        8.00,
        6.00
    )

elif state == "Gujarat":
    tariff = st.slider(
        "Electricity Tariff (₹/kWh)",
        3.50,
        6.20,
        5.00
    )

elif state == "West Bengal":
    tariff = st.slider(
        "Electricity Tariff (₹/kWh)",
        6.50,
        10.00,
        8.00
    )

elif state == "Rajasthan":
    tariff = st.slider(
        "Electricity Tariff (₹/kWh)",
        4.00,
        7.95,
        6.00
    )

else:
    tariff = st.slider(
        "Electricity Tariff (₹/kWh)",
        3.78,
        7.50,
        5.50
    )

brightness = recommended_backlight(
    ambient_light=50,
    content_brightness=50
)

optimized = wall_power(
    brightness_pct=brightness,
    volume_pct=50,
    wifi_on=True
)

conventional = wall_power(
    brightness_pct=100,
    volume_pct=50,
    wifi_on=True
)

saving_percent = (
    (conventional["WallPower"] - optimized["WallPower"])
    /
    conventional["WallPower"]
) * 100

tv_power = conventional["WallPower"]

annual_energy_normal = (
    tv_power *
    daily_hours *
    365
) / 1000

annual_energy_optimized = (
    annual_energy_normal *
    (1 - saving_percent/100)
)

annual_saved = (
    annual_energy_normal -
    annual_energy_optimized
)


money_saved = (
    annual_saved *
    tariff
)

co2_factor = 0.82

co2_saved = (
    annual_saved *
    co2_factor
)

c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "kWh Saved / Year",
    f"{annual_saved:.1f}"
)

c2.metric(
    "Money Saved / Year",
    f"₹{money_saved:.0f}"
)

c3.metric(
    "CO₂ Reduction",
    f"{co2_saved:.1f} kg"
)
trees = co2_saved / 21
c4.metric(
    "Equivalent Trees",
    f"{trees:.0f}"
)
import plotly.express as px
energy = {
    "Category":[
        "Energy Used",
        "Energy Saved"
    ],
    "Value":[
        annual_energy_optimized,
        annual_saved
    ]
}

fig = px.pie(
    energy,
    values="Value",
    names="Category",
    hole=0.5,
    title="Annual Energy Distribution"
)

st.plotly_chart(
    fig,
    use_container_width=True
)
st.success("""
Observation

Annual energy savings increase linearly with daily TV usage because adaptive backlight optimization is continuously applied throughout the viewing session.

Consequently, households with longer television usage experience proportionally greater reductions in electricity consumption and operating cost.
""")
st.info(
    f"""
Selected State: {state}

Electricity Tariff Used:
₹{tariff:.2f}/kWh
"""
)

st.divider()

homes = annual_saved / 1200
grid_scale_mwh = (
    annual_saved
    * 1_000_000
    / 1000
)
st.success(
    f"""
    One optimized TV saves
    approximately {annual_saved:.1f} kWh/year.

    If 1 million TVs adopt this technology,
    Annual Grid Energy Saved:

      {grid_scale_mwh:.1f} MWh



    Equivalent to powering
    {homes*1000000:.0f} homes for a year.
    """
)
st.info(
    """
   The annual impact calculations are extrapolated from the validated Digital Twin model using representative television operating conditions.
    Actual savings will vary depending on viewing duration, displayed content, ambient illumination and electricity tariff.
    """
)
st.success(
    """
    If adopted by 1 million TVs across India,
    this technology could save approximately
    43.8 GWh annually while preventing
    thousands of tonnes of CO₂ emissions.
    """
)
st.caption(
    """
Tariff values are based on typical
residential electricity tariff ranges
for different Indian states.

Actual savings may vary depending on
consumption slab, DISCOM policies,
fixed charges and subsidies.
"""
)