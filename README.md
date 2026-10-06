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

### Completed

- Reproducible synthetic mobile-trajectory generator
- Synthetic activity episodes and trip records
- Baseline stay-point detection
- Separation of model inputs from hidden ground-truth labels
- Initial OD-matrix generation

The generator creates a 7-day population of 500 synthetic persons at 15-minute observation intervals. Exact output counts are generated at runtime rather than hard-coded because the trajectory generator is under active development.

### Important modelling principle

The raw synthetic trajectory contains `true_activity` and `true_zone` only as **evaluation ground truth**. The inference pipeline deliberately excludes those columns. This lets us measure how accurately the algorithms recover activities from location observations, rather than simply reading the answer from the data.

## Reproduce the data

From the repository root:

```bash
python scripts/generate_synthetic_data.py
```

The complete generated dataset is written to `data/generated/`, which is excluded from Git by `.gitignore`.

## Run stay-point detection

After generating the data:

```bash
python scripts/run_stay_point_detection.py
```

The baseline detector uses only:

- `person_id`
- `timestamp`
- `lat`
- `lon`

It does **not** use `true_activity` or `true_zone`.

The output is:

```text
data/processed/stay_points.csv
```

Each detected stay contains its start/end time, duration, centroid coordinates, and observation count.

## Data model

A simplified raw trajectory looks like:

```text
person_id | timestamp           | lat      | lon      | true_activity
P0001     | 2026-01-05 08:00   | ...      | ...      | HOME
P0001     | 2026-01-05 08:15   | ...      | ...      | HOME
P0001     | 2026-01-05 08:30   | ...      | ...      | TRAVEL
P0001     | 2026-01-05 08:45   | ...      | ...      | WORK
```

`true_activity` is hidden from the inference algorithm. The eventual real-data version would not require such a field.

## Repository structure

```text
mobile-abm-sumo/
├── data/
│   ├── raw/                 # Small browser-friendly examples
│   ├── generated/           # Full generated data; gitignored
│   ├── processed/           # Derived modelling outputs
│   └── reference/           # Zone/reference data
├── scripts/
│   ├── generate_synthetic_data.py
│   └── run_stay_point_detection.py
├── src/
│   ├── preprocessing/
│   │   └── stay_points.py
│   ├── activity_inference/
│   ├── demand_generation/
│   ├── routing/
│   └── sumo/
├── notebooks/
├── tests/
├── docs/
└── README.md
```

## Development roadmap

### Phase 1 — Mobility preprocessing
- [x] Generate synthetic trajectories
- [x] Include realistic travel periods between activities
- [x] Build baseline stay-point detection
- [ ] Noise filtering and trajectory-quality checks
- [ ] Residence/home inference
- [ ] Workplace inference

### Phase 2 — Activity-based modelling
- [ ] Infer activity episodes from detected stays
- [ ] Activity-purpose classification
- [ ] Activity duration modelling
- [ ] Activity-chain construction
- [ ] Trip generation
- [ ] Time-of-day distributions

### Phase 3 — Spatial demand modelling
- [ ] Traffic analysis zones
- [ ] Purpose-specific OD matrices
- [ ] Temporal OD matrices
- [ ] Land-use and POI features

### Phase 4 — Machine learning
- [ ] Rule-based activity-classification baseline
- [ ] Random Forest / gradient-boosting classifier
- [ ] Sequential activity model
- [ ] Model evaluation and error analysis

### Phase 5 — SUMO integration
- [ ] Network preparation
- [ ] Route generation
- [ ] Demand injection
- [ ] TraCI-based simulation control
- [ ] Simulation outputs and KPIs

### Phase 6 — External data and validation
Potential future integrations include:

- OpenStreetMap network and POIs
- TomTom traffic/travel-time data
- Public traffic counts
- Other openly licensed mobility datasets

## Privacy and data governance

This repository uses synthetic data for the initial development stage. No real individual's location history is intentionally included.

When external datasets are introduced, licensing, aggregation, anonymization, privacy, and permitted-use conditions should be reviewed before inclusion. Proprietary employer/client data should not be committed to this repository.

## Why this project?

The project combines transportation planning, travel-demand modelling, GIS, Python, machine learning, APIs, and microscopic traffic simulation into one reproducible workflow.

The intended outcome is not just a collection of software demonstrations, but an evidence-driven mobility modelling system that can be extended as additional data and modelling methods are added.
