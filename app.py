import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import math

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Sun-Starved Tracker | Agri-Voltaics Optimizer",
    page_icon="☀️",
    layout="wide"
)

# ============================================================
# CROP DATA
# ============================================================

CROP_DATA = {
    "Tomato": {
        "Germination": 55,
        "Vegetative": 70,
        "Flowering": 80,
        "Fruiting": 75
    },
    "Lettuce": {
        "Germination": 45,
        "Vegetative": 60,
        "Flowering": 50,
        "Fruiting": 50
    },
    "Wheat": {
        "Germination": 55,
        "Vegetative": 75,
        "Flowering": 85,
        "Fruiting": 80
    },
    "Strawberry": {
        "Germination": 50,
        "Vegetative": 65,
        "Flowering": 80,
        "Fruiting": 78
    }
}

# ============================================================
# GROWTH STAGE DATA
# ============================================================

GROWTH_VULNERABILITY = {
    "Germination": 0.8,
    "Vegetative": 1.1,
    "Flowering": 1.8,
    "Fruiting": 1.4
}

DEFAULT_CROP_PRIORITY = {
    "Germination": 35,
    "Vegetative": 45,
    "Flowering": 55,
    "Fruiting": 50
}


# ============================================================
# SOLAR EFFICIENCY
# ============================================================

def calculate_solar_efficiency(angle):

    radians = math.radians(angle)

    efficiency = 100 * max(0, math.cos(radians))

    return efficiency


# ============================================================
# CROP LIGHT CALCULATION
# ============================================================

def calculate_crop_light(angle, temperature):

    angle_factor = abs(angle) / 60

    crop_light = 25 + (70 * angle_factor)

    temperature_penalty = max(
        0,
        abs(temperature - 25) - 8
    ) * 0.6

    crop_light -= temperature_penalty

    crop_light = max(
        0,
        min(100, crop_light)
    )

    return crop_light


# ============================================================
# CALCULATE PERFORMANCE FOR ONE ANGLE
# ============================================================

def calculate_score(
    angle,
    solar_radiation,
    temperature,
    crop,
    growth_stage,
    crop_priority
):

    solar_efficiency = calculate_solar_efficiency(angle)

    crop_light = calculate_crop_light(
        angle,
        temperature
    )

    target_light = CROP_DATA[crop][growth_stage]

    crop_score = min(
        100,
        (crop_light / target_light) * 100
    )

    solar_score = solar_efficiency

    solar_priority = 1 - crop_priority

    overall_score = (
        solar_priority * solar_score
        +
        crop_priority * crop_score
    )

    pv_generation = (
        solar_radiation
        * solar_efficiency
        / 100
    )

    return {
        "angle": angle,
        "solar_efficiency": solar_efficiency,
        "crop_light": crop_light,
        "crop_score": crop_score,
        "solar_score": solar_score,
        "overall_score": overall_score,
        "pv_generation": pv_generation,
        "target_light": target_light
    }


# ============================================================
# OPTIMIZE ALL PANEL ANGLES
# ============================================================

def optimize_angles(
    solar_radiation,
    temperature,
    crop,
    growth_stage,
    crop_priority
):

    results = []

    for angle in range(-60, 61):

        result = calculate_score(
            angle,
            solar_radiation,
            temperature,
            crop,
            growth_stage,
            crop_priority
        )

        results.append(result)

    return pd.DataFrame(results)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <h1 style="text-align:center;">
    ☀️ Sun-Starved Tracker
    </h1>

    <h3 style="text-align:center;">
    AI-Powered Agri-Voltaics Optimizer
    </h3>

    <p style="text-align:center;">
    Balancing <b>Solar Energy Generation</b>
    with
    <b>Crop Sunlight Requirements</b>
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🌱 Farm Parameters")

crop = st.sidebar.selectbox(
    "Crop Type",
    list(CROP_DATA.keys())
)

growth_stage = st.sidebar.selectbox(
    "Growth Stage",
    list(CROP_DATA[crop].keys()),
    index=2
)

st.sidebar.subheader("☀️ Environmental Conditions")

solar_radiation = st.sidebar.slider(
    "Solar Radiation (W/m²)",
    100,
    1100,
    850,
    10
)

cloud_cover = st.sidebar.slider(
    "Cloud Cover (%)",
    0,
    100,
    20,
    5
)

temperature = st.sidebar.slider(
    "Temperature (°C)",
    10,
    45,
    30,
    1
)

st.sidebar.subheader("🔧 Solar Panel")

current_angle = st.sidebar.slider(
    "Current Panel Angle (°)",
    -60,
    60,
    20,
    1
)

st.sidebar.subheader("⚖️ Optimization Priority")

default_priority = DEFAULT_CROP_PRIORITY[growth_stage]

crop_priority_percent = st.sidebar.slider(
    "Crop Priority (%)",
    0,
    100,
    default_priority
)

crop_priority = crop_priority_percent / 100

solar_priority_percent = 100 - crop_priority_percent

st.sidebar.info(
    f"""
    Current priorities:

    🌱 Crop: {crop_priority_percent}%

    ☀️ Solar: {solar_priority_percent}%
    """
)


# ============================================================
# WEATHER ADJUSTMENT
# ============================================================

effective_radiation = (
    solar_radiation
    * (1 - 0.70 * cloud_cover / 100)
)


# ============================================================
# RUN OPTIMIZATION
# ============================================================

results = optimize_angles(
    solar_radiation=effective_radiation,
    temperature=temperature,
    crop=crop,
    growth_stage=growth_stage,
    crop_priority=crop_priority
)

best_row = results.loc[
    results["overall_score"].idxmax()
]

best_angle = int(best_row["angle"])

current_result = calculate_score(
    current_angle,
    effective_radiation,
    temperature,
    crop,
    growth_stage,
    crop_priority
)


# ============================================================
# MAIN METRICS
# ============================================================

st.subheader("🎯 AI Panel Position Recommendation")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Current Angle",
    f"{current_angle}°"
)

col2.metric(
    "Recommended Angle",
    f"{best_angle}°"
)

col3.metric(
    "Solar Efficiency",
    f"{best_row['solar_efficiency']:.1f}%"
)

col4.metric(
    "Crop Light",
    f"{best_row['crop_light']:.1f}%"
)


# ============================================================
# AI RECOMMENDATION
# ============================================================

st.divider()

recommendation_col, status_col = st.columns(
    [1.5, 1]
)

with recommendation_col:

    st.subheader("🤖 AI Recommendation")

    if best_row["crop_light"] < best_row["target_light"]:

        reason = (
            f"The {crop} crop is receiving insufficient "
            f"sunlight for the {growth_stage} stage. "
            f"The optimizer therefore increases crop "
            f"protection priority."
        )

    else:

        reason = (
            f"The {crop} crop is receiving sufficient "
            f"sunlight. The system can therefore give "
            f"more priority to solar-energy generation."
        )

    st.info(
        f"""
        Recommended Panel Angle:

        **{best_angle}°**

        {reason}

        Overall Balance Score:

        **{best_row['overall_score']:.1f}/100**
        """
    )


with status_col:

    st.subheader("🌱 Crop Status")

    target = best_row["target_light"]

    if best_row["crop_light"] >= target:

        st.success(
            f"""
            CROP STATUS: HEALTHY

            Required Light: {target}%

            Available Light:
            {best_row['crop_light']:.1f}%
            """
        )

    else:

        st.warning(
            f"""
            CROP STATUS: SUNLIGHT DEFICIT

            Required Light: {target}%

            Available Light:
            {best_row['crop_light']:.1f}%
            """
        )


# ============================================================
# DIGITAL ACTUATOR
# ============================================================

st.subheader("🔧 Digital Actuator Simulation")

difference = abs(
    best_angle - current_angle
)

if difference == 0:

    st.success(
        f"Panel is already at the optimal position: "
        f"{current_angle}°"
    )

else:

    st.write(
        f"""
        Virtual actuator command:

        **Move panel from {current_angle}° → {best_angle}°**
        """
    )

    progress = min(
        100,
        difference / 120 * 100
    )

    st.progress(
        int(progress)
    )


# ============================================================
# OPTIMIZATION LANDSCAPE
# ============================================================

st.divider()

st.header("📈 Optimization Landscape")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=results["angle"],
        y=results["solar_efficiency"],
        mode="lines",
        name="Solar Efficiency"
    )
)

fig.add_trace(
    go.Scatter(
        x=results["angle"],
        y=results["crop_light"],
        mode="lines",
        name="Crop Light"
    )
)

fig.add_trace(
    go.Scatter(
        x=results["angle"],
        y=results["overall_score"],
        mode="lines",
        name="Overall Score"
    )
)

fig.add_vline(
    x=best_angle,
    line_dash="dash",
    annotation_text=f"Optimal {best_angle}°"
)

fig.update_layout(
    title="Solar Energy vs Crop Sunlight",
    xaxis_title="Panel Angle (°)",
    yaxis_title="Performance (%)",
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# ENERGY VS AGRICULTURE TRADE-OFF
# ============================================================

st.header("⚖️ Energy–Agriculture Trade-Off")

fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(
        x=results["crop_light"],
        y=results["solar_efficiency"],
        mode="markers",
        text=[
            f"{angle}°"
            for angle in results["angle"]
        ],
        hovertemplate=
        "Crop Light: %{x:.1f}%"
        "<br>Solar Efficiency: %{y:.1f}%"
        "<br>Panel Angle: %{text}"
        "<extra></extra>",
        name="Candidate Angles"
    )
)

fig2.add_trace(
    go.Scatter(
        x=[best_row["crop_light"]],
        y=[best_row["solar_efficiency"]],
        mode="markers",
        marker=dict(
            size=18,
            symbol="star"
        ),
        name="Selected Angle"
    )
)

fig2.update_layout(
    title="Crop Sunlight vs Solar Generation",
    xaxis_title="Crop Sunlight (%)",
    yaxis_title="Solar Efficiency (%)",
    height=500
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# ============================================================
# WHAT-IF SIMULATOR
# ============================================================

st.divider()

st.header("🔬 Real-Time What-If Scenario Simulator")

st.write(
    "Change the environmental conditions and observe "
    "how the optimal panel angle changes."
)

sim_col1, sim_col2, sim_col3 = st.columns(3)

with sim_col1:

    scenario_cloud = st.slider(
        "Scenario Cloud Cover (%)",
        0,
        100,
        cloud_cover,
        5
    )

with sim_col2:

    scenario_radiation = st.slider(
        "Scenario Solar Radiation (W/m²)",
        100,
        1100,
        solar_radiation,
        10
    )

with sim_col3:

    scenario_growth = st.selectbox(
        "Scenario Growth Stage",
        list(CROP_DATA[crop].keys()),
        index=list(
            CROP_DATA[crop].keys()
        ).index(growth_stage)
    )


scenario_radiation_effective = (
    scenario_radiation
    * (1 - 0.70 * scenario_cloud / 100)
)

scenario_priority = (
    DEFAULT_CROP_PRIORITY[
        scenario_growth
    ] / 100
)

scenario_results = optimize_angles(
    solar_radiation=scenario_radiation_effective,
    temperature=temperature,
    crop=crop,
    growth_stage=scenario_growth,
    crop_priority=scenario_priority
)

scenario_best = scenario_results.loc[
    scenario_results["overall_score"].idxmax()
]


sc1, sc2, sc3 = st.columns(3)

sc1.metric(
    "New Optimal Angle",
    f"{int(scenario_best['angle'])}°"
)

sc2.metric(
    "Solar Efficiency",
    f"{scenario_best['solar_efficiency']:.1f}%"
)

sc3.metric(
    "Crop Light",
    f"{scenario_best['crop_light']:.1f}%"
)

st.success(
    f"""
    Dynamic Response:

    The system recalculated the optimal panel
    position and selected **{int(scenario_best['angle'])}°**.

    This demonstrates that the tracker is
    **adaptive rather than fixed**.
    """
)


# ============================================================
# ANGLE COMPARISON TABLE
# ============================================================

st.divider()

st.header("📋 Candidate Angle Comparison")

display_data = results.iloc[::5][
    [
        "angle",
        "solar_efficiency",
        "crop_light",
        "pv_generation",
        "overall_score"
    ]
].copy()

display_data.columns = [
    "Panel Angle (°)",
    "Solar Efficiency (%)",
    "Crop Light (%)",
    "PV Generation (W/m²)",
    "Overall Score"
]

display_data = display_data.round(2)

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# EXPLAINABLE OPTIMIZATION
# ============================================================

st.divider()

st.header("🧠 How the Optimizer Works")

st.code(
"""
For every candidate panel angle:

1. Estimate solar-energy generation.

2. Estimate sunlight reaching the crop canopy.

3. Compare crop sunlight with required sunlight.

4. Calculate solar score.

5. Calculate crop score.

6. Combine both objectives using dynamic weights.

7. Select the angle with the highest balance score.


Overall Score =

Solar Priority × Solar Score
+
Crop Priority × Crop Score
""",
    language="text"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    """
    AI26AG01 – Sun-Starved Tracker: Agri-Voltaics Optimizer |
    Hackathon Prototype |
    Digital actuator simulation — no physical hardware required.
    """
)