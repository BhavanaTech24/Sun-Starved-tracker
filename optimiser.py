import pandas as pd
from physics import calculate_metrics


# ============================================================
# OPTIMIZE PANEL ANGLES
# ============================================================

def optimize_angles(
    solar_radiation,
    temperature,
    crop,
    growth_stage,
    crop_priority,
    angle_min=-60,
    angle_max=60,
    step=1
):
    """
    Evaluate every candidate panel angle and calculate:

    - Solar efficiency
    - Crop sunlight
    - Crop score
    - Solar score
    - Overall balance score
    - Estimated PV generation

    Returns a pandas DataFrame.
    """

    results = []

    for angle in range(
        angle_min,
        angle_max + 1,
        step
    ):

        metrics = calculate_metrics(
            angle=angle,
            solar_radiation=solar_radiation,
            temperature=temperature,
            crop=crop,
            growth_stage=growth_stage,
            crop_priority=crop_priority
        )

        results.append(metrics)

    return pd.DataFrame(results)


# ============================================================
# FIND BEST PANEL ANGLE
# ============================================================

def recommend_angle(results):
    """
    Select the panel angle having
    the highest overall optimization score.
    """

    if results.empty:
        return None

    best_index = results[
        "overall_score"
    ].idxmax()

    best = results.loc[
        best_index
    ].to_dict()

    best["angle"] = int(
        best["angle"]
    )

    return best


# ============================================================
# GET TOP CANDIDATE ANGLES
# ============================================================

def get_top_angles(
    results,
    number_of_angles=5
):
    """
    Returns the best candidate angles
    according to the overall score.
    """

    if results.empty:
        return pd.DataFrame()

    top_angles = results.sort_values(
        by="overall_score",
        ascending=False
    ).head(number_of_angles)

    return top_angles.reset_index(
        drop=True
    )


# ============================================================
# CALCULATE CURRENT PANEL STATUS
# ============================================================

def evaluate_current_angle(
    results,
    current_angle
):
    """
    Find the calculated performance
    of the current panel position.
    """

    if results.empty:
        return None

    matching = results[
        results["angle"] == current_angle
    ]

    if matching.empty:
        return None

    return matching.iloc[0].to_dict()


# ============================================================
# CALCULATE IMPROVEMENT
# ============================================================

def calculate_improvement(
    current_result,
    recommended_result
):
    """
    Compare current panel position
    with the AI-recommended position.
    """

    if (
        current_result is None
        or recommended_result is None
    ):
        return {}

    return {
        "solar_change":
            recommended_result["solar_efficiency"]
            -
            current_result["solar_efficiency"],

        "crop_light_change":
            recommended_result["crop_light"]
            -
            current_result["crop_light"],

        "overall_score_change":
            recommended_result["overall_score"]
            -
            current_result["overall_score"],

        "angle_change":
            recommended_result["angle"]
            -
            current_result["angle"]
    }


# ============================================================
# PARETO FRONTIER
# ============================================================

def calculate_pareto_frontier(results):
    """
    Identify non-dominated solutions.

    A solution is considered Pareto-optimal when there is
    no other solution that is better in BOTH:

    1. Solar efficiency
    2. Crop sunlight
    """

    if results.empty:
        return pd.DataFrame()

    pareto_rows = []

    for i, row in results.iterrows():

        dominated = False

        for j, other in results.iterrows():

            if i == j:
                continue

            better_or_equal_solar = (
                other["solar_efficiency"]
                >= row["solar_efficiency"]
            )

            better_or_equal_crop = (
                other["crop_light"]
                >= row["crop_light"]
            )

            strictly_better = (
                other["solar_efficiency"]
                > row["solar_efficiency"]
                or
                other["crop_light"]
                > row["crop_light"]
            )

            if (
                better_or_equal_solar
                and
                better_or_equal_crop
                and
                strictly_better
            ):
                dominated = True
                break

        if not dominated:
            pareto_rows.append(row)

    pareto = pd.DataFrame(
        pareto_rows
    )

    return pareto.sort_values(
        by="angle"
    ).reset_index(
        drop=True
    )


# ============================================================
# DYNAMIC PRIORITY
# ============================================================

def calculate_dynamic_priority(
    crop,
    growth_stage,
    current_crop_light,
    target_crop_light,
    base_priority
):
    """
    Increase crop priority when the crop is experiencing
    a sunlight deficit.

    This is one of the key intelligent features
    of the Sun-Starved Tracker.
    """

    deficit = max(
        0,
        target_crop_light - current_crop_light
    )

    deficit_ratio = (
        deficit
        /
        max(target_crop_light, 1)
    )

    priority = (
        base_priority
        +
        deficit_ratio * 0.40
    )

    priority = max(
        0.0,
        min(1.0, priority)
    )

    return priority