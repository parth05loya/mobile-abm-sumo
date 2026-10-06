"""Stay-point detection for mobile location trajectories.

The algorithm follows a simple stay-point definition: a sequence of observations
is a stay when the user remains within a spatial radius for at least a minimum
duration. This is deliberately a transparent baseline before more advanced
trajectory segmentation or clustering methods are introduced.
"""

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

    Parameters
    ----------
    df:
        DataFrame containing ``person_id``, ``timestamp``, ``lat`` and ``lon``.
    radius_m:
        Maximum distance from the candidate start point before the candidate
        stay is considered to have ended.
    min_duration_min:
        Minimum elapsed time required to classify a sequence as a stay.

    Returns
    -------
    pandas.DataFrame
        One row per detected stay with start/end timestamps, duration, centroid,
        observation count and the person's ID.
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

        while i < len(group):
            j = i + 1
            found = False

            while j < len(group):
                distance = haversine_m(
                    group.loc[i, "lat"],
                    group.loc[i, "lon"],
                    group.loc[j, "lat"],
                    group.loc[j, "lon"],
                )

                elapsed = (group.loc[j, "timestamp"] - group.loc[i, "timestamp"]).total_seconds() / 60

                if distance > radius_m:
                    if elapsed >= min_duration_min:
                        segment = group.iloc[i:j]
                        results.append({
                            "person_id": person_id,
                            "start_time": segment["timestamp"].iloc[0],
                            "end_time": segment["timestamp"].iloc[-1],
                            "duration_min": (segment["timestamp"].iloc[-1] - segment["timestamp"].iloc[0]).total_seconds() / 60,
                            "centroid_lat": segment["lat"].mean(),
                            "centroid_lon": segment["lon"].mean(),
                            "n_observations": len(segment),
                        })
                        i = j
                        found = True
                    break
                j += 1

            if found:
                continue

            # If no spatial break was found, test the remaining tail as a stay.
            segment = group.iloc[i:]
            if len(segment) >= 2:
                elapsed = (segment["timestamp"].iloc[-1] - segment["timestamp"].iloc[0]).total_seconds() / 60
                max_distance = haversine_m(
                    segment["lat"].iloc[0], segment["lon"].iloc[0],
                    segment["lat"].iloc[-1], segment["lon"].iloc[-1],
                )
                if elapsed >= min_duration_min and max_distance <= radius_m:
                    results.append({
                        "person_id": person_id,
                        "start_time": segment["timestamp"].iloc[0],
                        "end_time": segment["timestamp"].iloc[-1],
                        "duration_min": elapsed,
                        "centroid_lat": segment["lat"].mean(),
                        "centroid_lon": segment["lon"].mean(),
                        "n_observations": len(segment),
                    })
            break

    return pd.DataFrame(results)
