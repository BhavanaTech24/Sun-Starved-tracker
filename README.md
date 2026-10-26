# ☀️ Sun-Starved Tracker

## AI26AG01 - Agri-Voltaics Optimizer

An intelligent crop-aware solar-panel optimization system that balances renewable-energy generation with the sunlight requirements of crops.

## Problem

Conventional solar trackers focus mainly on maximizing electricity generation. In agrivoltaic farms, excessive panel shading can reduce sunlight reaching crops.

Our system solves this by considering:

- Solar radiation
- Cloud cover
- Temperature
- Crop type
- Crop growth stage
- Crop sunlight requirement
- Solar-panel angle

## Core Workflow

Weather & Solar Data
↓
Solar Radiation Analysis
↓
Crop Sunlight Requirement
↓
Evaluate Panel Angles
↓
Multi-Objective Optimization
↓
Optimal Panel Position
↓
Digital Actuator Simulation
↓
Continuous Adjustment

## Main Features

### 1. Crop-Aware Optimization

The system considers different crop types and growth stages.

### 2. Dual-Objective Optimization

The system balances:

- Solar-energy generation
- Crop sunlight availability

### 3. Dynamic Priority

The importance of crop protection changes depending on the crop's growth stage and sunlight requirement.

### 4. What-If Simulation

Users can change:

- Cloud cover
- Solar radiation
- Growth stage

and observe the new recommended panel angle.

### 5. Pareto-Style Trade-Off

The system visualizes the relationship between crop sunlight and solar generation.

### 6. Digital Actuator

The physical actuator is simulated digitally.

For example:

Current angle: 20°

Recommended angle: 42°

The system generates a virtual command to move the panel.

## Technologies

- Python
- Streamlit
- Plotly
- Pandas
- NumPy

## Hardware

No physical hardware is required for this prototype.

In a real deployment, the recommended angle could be sent to a motor or servo controller.

## How to Run

Create a virtual environment:

```bash
python -m venv .venv