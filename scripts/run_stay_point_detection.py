"""Run the baseline stay-point detector on generated mobile trajectories."""

from pathlib import Path
import sys

import pandas as pd

# Allow running this script directly from the repository root.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.preprocessing.stay_points import detect_stay_points

INPUT = ROOT / "data" / "generated" / "synthetic_mobile_trajectories.csv"
OUTPUT = ROOT / "data" / "processed" / "stay_points.csv"


def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Input not found: {INPUT}. Run 'python scripts/generate_synthetic_data.py' first."
        )

    df = pd.read_csv(INPUT, parse_dates=["timestamp"])
    # IMPORTANT: true_activity/true_zone are intentionally not passed to the detector.
    model_input = df[["person_id", "timestamp", "lat", "lon"]]

    stays = detect_stay_points(model_input, radius_m=150, min_duration_min=20)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    stays.to_csv(OUTPUT, index=False)

    print(f"Detected {len(stays):,} stay points")
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
