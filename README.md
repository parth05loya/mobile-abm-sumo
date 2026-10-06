# Mobile Data–Driven Activity-Based Travel Demand Model with SUMO

A portfolio and research prototype for transforming anonymized or synthetic mobile-phone mobility observations into activity schedules, travel demand, OD matrices, and microscopic traffic simulation inputs.

## Project objective

The long-term goal is an end-to-end mobility modelling pipeline:

```text
Mobile trajectories
      ↓
Stay-point detection
      ↓
Home / work inference
      ↓
Activity classification
      ↓
Activity chains
      ↓
Trip generation
      ↓
Time-dependent OD demand
      ↓
SUMO traffic simulation
      ↓
Validation and scenario analysis
```

The project is intentionally being developed in stages. Early versions use synthetic data so the methodology can be developed without relying on proprietary, personally identifiable, or restricted telecom data.

## Current status — V0.1

The first dataset contains:

| Component | V0.1 |
|---|---:|
| Synthetic persons | 500 |
| Days | 7 |
| Mobile observations | 284,177 |
| Activity episodes | 7,837 |
| Trips | 3,951 |
| Traffic analysis zones | 6 |

Activity labels currently include:

- Home
- Work
- Shopping
- Restaurant
- Leisure

### V0.1 files

- `data/raw/synthetic_mobile_trajectories.csv` — synthetic 15-minute mobile observations
- `data/raw/synthetic_activity_episodes.csv` — synthetic activity episodes used to generate the observations
- `data/raw/trip_records.csv` — trip-level records derived from activity transitions
- `data/processed/od_matrix.csv` — aggregated OD matrix
- `data/reference/zones.csv` — zone centroids
- `data/reference/project_summary.csv` — dataset summary

## Planned development

### Phase 1 — Mobility preprocessing
- Stay-point detection
- Noise filtering
- Trajectory segmentation
- Residence and workplace inference

### Phase 2 — Activity-based modelling
- Activity-purpose classification
- Activity duration modelling
- Activity-chain construction
- Trip generation
- Time-of-day distributions

### Phase 3 — Spatial demand modelling
- Traffic analysis zones
- Purpose-specific OD matrices
- Temporal OD matrices
- Land-use and POI features

### Phase 4 — Machine learning
- Rule-based baseline
- Random Forest / gradient-boosting classifiers
- Sequential activity models
- Model evaluation and error analysis

### Phase 5 — SUMO integration
- Network preparation
- Route generation
- Demand injection
- TraCI-based simulation control
- Simulation outputs and KPIs

### Phase 6 — External data and validation
Potential future integrations include:
- OpenStreetMap network and POIs
- TomTom traffic/travel-time data
- Public traffic counts
- Other openly licensed mobility datasets

## Repository structure

```text
mobile-abm-sumo/
├── data/
│   ├── raw/
│   ├── processed/
│   └── reference/
├── notebooks/
├── src/
│   ├── preprocessing/
│   ├── activity_inference/
│   ├── demand_generation/
│   ├── routing/
│   └── sumo/
├── tests/
├── docs/
└── README.md
```

## Data and privacy

This repository uses synthetic data for the initial development stage. No real individual's location history is intentionally included.

When external datasets are introduced, licensing, aggregation, anonymization, privacy, and permitted-use conditions should be reviewed before inclusion. Proprietary employer/client data should not be committed to this repository.

## Roadmap

- [x] Create V0.1 synthetic mobility dataset
- [x] Create initial OD matrix
- [ ] Build stay-point detection
- [ ] Infer home and work locations
- [ ] Infer activity purposes without ground-truth labels
- [ ] Build activity chains
- [ ] Generate time-dependent OD matrices
- [ ] Add GIS visualization
- [ ] Add ML activity classifier
- [ ] Integrate SUMO
- [ ] Add TomTom-based validation
- [ ] Publish scenario-analysis examples

## Why this project?

The project combines transportation planning, travel-demand modelling, GIS, Python, machine learning, APIs, and microscopic traffic simulation into one reproducible workflow.

The intended outcome is not just a collection of software demonstrations, but an evidence-driven mobility modelling system that can be extended as additional data and modelling methods are added.
