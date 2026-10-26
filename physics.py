import math


# ============================================================
# CROP PROFILES
# ============================================================

CROP_PROFILES = {

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
# GROWTH-STAGE VULNERABILITY
# ============================================================

GROWTH_STAGES = {

    "Germination": {
        "vulnerability": 0.8,
        "default_crop_weight": 35
    },

    "Vegetative": {
        "vulnerability": 1.1,
        "default_crop_weight": 45
    },

    "Flowering": {
        "vulnerability": 1.8,
        "default_crop_weight": 55
    },

    "Fruiting": {
        "vulnerability": 1.4,
        "default_crop_weight": 50
    }
}


# ============================================================
# GET CROP TARGET LIGHT
# ============================================================

def get_target_light(crop, growth_stage):

    return CROP_PROFILES[
        crop
    ][
        growth_stage
    ]


# ============================================================
# SOLAR EFFICIENCY MODEL
# ============================================================

def calculate_solar_efficiency(angle):
    """
    Simplified solar-panel orientation model.

    0 degrees represents the ideal sun-facing position
    in this educational prototype.

    As the panel moves away from the ideal position,
    the estimated solar efficiency decreases.
    """

    angle_radians = math.radians(angle)

    efficiency = (
        100 *
        max(
            0,
            math.cos(angle_radians)
        )
    )

    return efficiency


# ============================================================
# CROP CANOPY LIGHT MODEL
# ============================================================

def calculate_crop_light(
    angle,
    temperature
):
    """
    Estimate relative light reaching the crop canopy.

    Larger panel tilt is assumed to reduce shading
    in this simplified prototype model.
    """

    # Convert panel angle to a 0–1 factor.
    angle_factor = (
        abs(angle) / 60
    )

    # Base crop light.
    crop_light = (
        25
        +
        70 * angle_factor
    )

    # Temperature stress adjustment.
    temperature_stress = max(
        0,
        abs(temperature - 25) - 8
    )

    temperature_penalty = (
        temperature_stress * 0.6
    )

    crop_light -= temperature_penalty

    crop_light = max(
        0,
        min(
            100,
            crop_light
        )
    )

    return crop_light


# ============================================================
# TEMPERATURE STRESS
# ============================================================

def calculate_temperature_stress(
    temperature
):
    """
    Calculate a simple environmental stress index.
    """

    if temperature <= 25:

        return 0

    if temperature <= 33:

        return (
            (temperature - 25)
            / 8
        )

    return min(
        2,
        1 +
        (
            temperature - 33
        ) / 7
    )


# ============================================================
# CLOUD EFFECT
# ============================================================

def calculate_effective_radiation(
    solar_radiation,
    cloud_cover
):
    """
    Estimate radiation available to the solar panel
    after cloud-cover attenuation.
    """

    cloud_factor = (
        1
        -
        0.70 *
        cloud_cover /
        100
    )

    return max(
        0,
        solar_radiation *
        cloud_factor
    )


# ============================================================
# CROP SUNLIGHT SCORE
# ============================================================

def calculate_crop_score(
    crop_light,
    target_light
):
    """
    Compare available crop light with required crop light.
    """

    if target_light <= 0:

        return 0

    score = (
        crop_light /
        target_light
    ) * 100

    return min(
        100,
        score
    )


# ============================================================
# SOLAR SCORE
# ============================================================

def calculate_solar_score(
    solar_efficiency
):

    return max(
        0,
        min(
            100,
            solar_efficiency
        )
    )


# ============================================================
# OVERALL BALANCE SCORE
# ============================================================

def calculate_overall_score(
    solar_score,
    crop_score,
    crop_priority
):
    """
    Combine the two competing objectives.

    crop_priority:
        0.0 = prioritize solar energy
        1.0 = prioritize crop sunlight
    """

    solar_priority = (
        1 -
        crop_priority
    )

    overall_score = (
        solar_priority *
        solar_score
        +
        crop_priority *
        crop_score
    )

    return overall_score


# ============================================================
# COMPLETE PHYSICS / PERFORMANCE CALCULATION
# ============================================================

def calculate_metrics(
    angle,
    solar_radiation,
    temperature,
    crop,
    growth_stage,
    crop_priority
):
    """
    Calculate all metrics required by the optimizer.
    """

    # --------------------------------------------------------
    # 1. Solar efficiency
    # --------------------------------------------------------

    solar_efficiency = (
        calculate_solar_efficiency(
            angle
        )
    )

    # --------------------------------------------------------
    # 2. Crop canopy light
    # --------------------------------------------------------

    crop_light = (
        calculate_crop_light(
            angle,
            temperature
        )
    )

    # --------------------------------------------------------
    # 3. Required crop light
    # --------------------------------------------------------

    target_light = (
        get_target_light(
            crop,
            growth_stage
        )
    )

    # --------------------------------------------------------
    # 4. Crop score
    # --------------------------------------------------------

    crop_score = (
        calculate_crop_score(
            crop_light,
            target_light
        )
    )

    # --------------------------------------------------------
    # 5. Solar score
    # --------------------------------------------------------

    solar_score = (
        calculate_solar_score(
            solar_efficiency
        )
    )

    # --------------------------------------------------------
    # 6. Overall optimization score
    # --------------------------------------------------------

    overall_score = (
        calculate_overall_score(
            solar_score,
            crop_score,
            crop_priority
        )
    )

    # --------------------------------------------------------
    # 7. Estimated PV generation
    # --------------------------------------------------------

    pv_generation = (
        solar_radiation *
        solar_efficiency /
        100
    )

    # --------------------------------------------------------
    # 8. Sunlight deficit
    # --------------------------------------------------------

    sunlight_deficit = max(
        0,
        target_light -
        crop_light
    )

    # --------------------------------------------------------
    # 9. Sunlight surplus
    # --------------------------------------------------------

    sunlight_surplus = max(
        0,
        crop_light -
        target_light
    )

    # --------------------------------------------------------
    # 10. Environmental stress
    # --------------------------------------------------------

    temperature_stress = (
        calculate_temperature_stress(
            temperature
        )
    )

    # --------------------------------------------------------
    # Return everything
    # --------------------------------------------------------

    return {

        "angle": angle,

        "solar_efficiency":
            solar_efficiency,

        "solar_score":
            solar_score,

        "crop_light":
            crop_light,

        "crop_score":
            crop_score,

        "target_light":
            target_light,

        "sunlight_deficit":
            sunlight_deficit,

        "sunlight_surplus":
            sunlight_surplus,

        "overall_score":
            overall_score,

        "pv_generation":
            pv_generation,

        "temperature_stress":
            temperature_stress,

        "crop":
            crop,

        "growth_stage":
            growth_stage
    }