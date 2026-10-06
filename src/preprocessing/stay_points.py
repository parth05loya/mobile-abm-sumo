"""Baseline stay-point detection for mobile location trajectories."""

from __future__ import annotations

import numpy as np
import pandas as pd

EARTH_RADIUS_M = 6_371_000.0


def haversine_m(lat1, lon1, lat2, lon2):
    """Return great-circle distance in metres; supports scalars/arrays."""
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(a))


def detect_stay_points(
    df: pd.DataFrame,
    radius_m: float = 150.0,
    min_duration_min: float = 20.0,
) -> pd.DataFrame:
    """Detect stay points independently for each person.

    A candidate starts at observation ``i``. The algorithm advances until the
    first observation outside ``radius_m``. If the elapsed time is at least
    ``min_duration_min``, observations from ``i`` through ``j-1`` form a stay.
    Otherwise the candidate start moves forward by one observation.

    The method is intentionally simple and interpretable; it is the baseline
    against which more advanced clustering/segmentation methods can be tested.
    """
    required = {"person_id", "timestamp", "lat", "lon"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    work = df.copy()
    work["timestamp"] = pd.to_datetime(work["timestamp"])
    work = work.sort_values(["person_id", "timestamp"]).reset_index(drop=True)
    results = []

    for person_id, group in work.groupby("person_id", sort=False):
        group = group.reset_index(drop=True)
        i = 0

        while i < len(group) - 1:
            j = i + 1
            while j < len(group):
                distance = float(haversine_m(
                    group.loc[i, "lat"], group.loc[i, "lon"],
                    group.loc[j, "lat"], group.loc[j, "lon"],
                ))
                if distance > radius_m:
                    break
                j += 1

            end_idx = j if j < len(group) else len(group)
            segment = group.iloc[i:end_idx]
            if len(segment) >= 2:
                duration = (
                    segment["timestamp"].iloc[-1] - segment["timestamp"].iloc[0]
                ).total_seconds() / 60
                if duration >= min_duration_min:
                    results.append({
                        "person_id": person_id,
                        "start_time": segment["timestamp"].iloc[0],
                        "end_time": segment["timestamp"].iloc[-1],
                        "duration_min": duration,
                        "centroid_lat": segment["lat"].mean(),
                        "centroid_lon": segment["lon"].mean(),
                        "n_observations": len(segment),
                    })
                    i = end_idx
                    continue
            i += 1

    return pd.DataFrame(results)
