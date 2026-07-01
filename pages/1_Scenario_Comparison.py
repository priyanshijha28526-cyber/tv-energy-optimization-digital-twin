import streamlit as st
import pandas as pd
import plotly.express as px
from controller import recommended_backlight
from power_model import wall_power

st.title(" Scenario Comparison")

st.write("""
Compare TV power consumption across common viewing scenarios.
""")

# Scenario data from your simulation

scenarios = [
    ("Movie Night",20,20,30),
    ("Living Room",50,40,40),
    ("Gaming",80,80,60),
    ("Sports",90,90,70),
    ("Streaming",60,70,40)
]

rows = []

for name,ambient,content,volume in scenarios:

    brightness = recommended_backlight(
        ambient,
        content,
        False
    )

    conventional = wall_power(
        100,
        volume,
        True
    )

    optimized = wall_power(
        brightness,
        volume,
        True
    )

    saving = (
        (
            conventional["WallPower"]
            -
            optimized["WallPower"]
        )
        /
        conventional["WallPower"]
    )*100

    rows.append({

        "Scenario":name,

        "Recommended Brightness (%)":round(brightness,1),

        "Conventional Power (W)":round(
            conventional["WallPower"],2
        ),

        "Optimized Power (W)":round(
            optimized["WallPower"],2
        ),

        "Savings (%)":round(
            saving,
            1
        )

    })

df = pd.DataFrame(rows)


# ==========================
# Table
# ==========================

st.subheader("Scenario Data")

st.dataframe(
    df.set_index("Scenario"),
    use_container_width=True
)

avg_saving = df["Savings (%)"].mean()
avg_power_saved = (
    df["Conventional Power (W)"]
    -
    df["Optimized Power (W)"]
).mean()

c1,c2 = st.columns(2)

c1.metric(
    "Average Saving",
    f"{avg_saving:.1f}%"
)

c2.metric(
    "Average Power Saved",
    f"{avg_power_saved:.1f} W"
)

# ==========================
# Savings Chart
# ==========================

st.subheader("Energy Savings by Scenario")

fig1 = px.bar(
    df,
    x="Scenario",
    y="Savings (%)",
    text="Savings (%)",
    title="Percentage Energy Savings"
)
colors = []

for s in df["Savings (%)"]:

    if s>30:

        colors.append("green")

    elif s>15:

        colors.append("orange")

    else:

        colors.append("red")


fig1.update_traces(
    marker_color=colors
)

fig1.update_traces(
    texttemplate='%{text:.1f}%',
    textposition='outside'
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# ==========================
# Power Comparison
# ==========================

st.subheader("Conventional vs Optimized Power")

power_df = pd.DataFrame({
    "Scenario": df["Scenario"].tolist()*2,
    "Power (W)": (
        df["Conventional Power (W)"].tolist()
        +
        df["Optimized Power (W)"].tolist()
    ),
    "Type": (
        ["Conventional"]*len(df)
        +
        ["Optimized"]*len(df)
    )
})

fig2 = px.bar(
    power_df,
    x="Scenario",
    y="Power (W)",
    color="Type",
    barmode="group",
    title="Wall Power Comparison"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# ==========================
# Brightness Comparison
# ==========================

st.subheader("Recommended Brightness")

fig3 = px.bar(
    df,
    x="Scenario",
    y="Recommended Brightness (%)",
    text="Recommended Brightness (%)",
    title="Recommended Backlight Brightness"
)

fig3.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)
fig4 = px.scatter(
    df,
    x="Recommended Brightness (%)",
    y="Savings (%)",
    text="Scenario",
    size="Savings (%)",
    title="Relationship Between Recommended Brightness and Energy Savings"
)

fig4.update_traces(
    textposition="top center"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

           


# ==========================
# Insights
# ==========================

st.subheader("Observations")

st.success("""
Observations

• A clear inverse relationship exists between recommended backlight brightness and energy savings.

• Lower controller-selected brightness levels correspond to higher energy savings.

• The plotted scenarios follow a consistent downward trend, 
           indicating that increasing brightness requirements reduce the achievable energy savings.
""")
st.subheader("Research Findings")

st.info("""
Movie Night and Living Room conditions provide the highest energy savings because lower ambient light allows substantial backlight reduction.

Gaming and Sports require higher brightness for visibility and image quality, therefore energy savings are lower.

The controller adapts brightness dynamically instead of simply minimizing power, resulting in a better balance between efficiency and viewing quality.
""")
