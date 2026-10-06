"""Generate a reproducible synthetic mobile-mobility dataset for V0.1.

The generated data are synthetic and intended for development/testing only.
The raw trajectory table contains a hidden ``true_activity`` field solely for
model evaluation. Inference code should not use that field as an input feature.
"""

from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
N_PERSONS = 500
DAYS = 7
FREQ = "15min"

ZONES = {
    "Z1": (22.7196, 75.8577),
    "Z2": (22.7350, 75.8350),
    "Z3": (22.6900, 75.8500),
    "Z4": (22.7500, 75.8800),
    "Z5": (22.7050, 75.9000),
    "Z6": (22.6800, 75.8750),
}
ZONE_NAMES = list(ZONES)
ZONE_WEIGHTS = np.array([0.25, 0.16, 0.14, 0.14, 0.15, 0.16])


def _zone_for_activity(activity, home, work, rng):
    if activity == "HOME":
        return home
    if activity == "WORK":
        return work
    return rng.choice(ZONE_NAMES)


def _build_activity_schedule(worker, home, work, rng):
    """Return non-overlapping activity episodes for one person-day."""
    episodes = []

    if worker:
        dep = float(np.clip(rng.normal(8 * 60, 35), 6 * 60, 10 * 60))
        work_arrival = dep + float(np.clip(rng.normal(35, 15), 15, 75))
        work_departure = float(np.clip(rng.normal(17 * 60 + 30, 45), 16 * 60, 20 * 60))

        episodes.append(("HOME", 0.0, dep))
        episodes.append(("WORK", work_arrival, work_departure))

        r = rng.random()
        if r < 0.35:
            activity = "SHOPPING"
        elif r < 0.65:
            activity = "RESTAURANT"
        else:
            activity = None

        if activity:
            start = work_departure + float(rng.uniform(10, 35))
            duration = float(rng.uniform(30, 100))
            end = min(start + duration, 23 * 60)
            episodes.append((activity, start, end))

        last_end = max(e[2] for e in episodes)
        if last_end < 24 * 60:
            episodes.append(("HOME", last_end, 24 * 60))
    else:
        episodes.append(("HOME", 0.0, 24 * 60))
        if rng.random() < 0.65:
            activity = rng.choice(["SHOPPING", "RESTAURANT", "LEISURE"])
            start = float(rng.uniform(10 * 60, 17 * 60))
            duration = float(rng.uniform(45, 150))
            end = min(start + duration, 22 * 60)
            episodes = [("HOME", 0.0, start), (activity, start, end), ("HOME", end, 24 * 60)]

    return sorted(episodes, key=lambda x: x[1])


def _interpolate_travel(zone_a, zone_b, fraction, rng):
    """Interpolate between two zone centroids and add GPS-like noise."""
    lat_a, lon_a = ZONES[zone_a]
    lat_b, lon_b = ZONES[zone_b]
    lat = lat_a + fraction * (lat_b - lat_a)
    lon = lon_a + fraction * (lon_b - lon_a)
    return lat + rng.normal(0, 0.00025), lon + rng.normal(0, 0.00025)


def generate(output_dir="data/generated"):
    rng = np.random.default_rng(SEED)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    persons = []
    for i in range(1, N_PERSONS + 1):
        pid = f"P{i:04d}"
        home = rng.choice(ZONE_NAMES, p=ZONE_WEIGHTS)
        work_choices = [z for z in ZONE_NAMES if z != home]
        work = rng.choice(work_choices)
        persons.append((pid, home, work))

    observations = []
    activities = []

    for pid, home, work in persons:
        for day_idx in range(DAYS):
            date = pd.Timestamp("2026-01-05") + pd.Timedelta(days=day_idx)
            worker = date.dayofweek < 5 and rng.random() < 0.82
            episodes = _build_activity_schedule(worker, home, work, rng)

            # Assign a zone to every activity episode.
            located = []
            for activity, start, end in episodes:
                zone = _zone_for_activity(activity, home, work, rng)
                located.append((activity, start, end, zone))
                if end > start:
                    activities.append({
                        "person_id": pid,
                        "date": date.date(),
                        "activity": activity,
                        "start_min": round(start, 1),
                        "end_min": round(end, 1),
                        "zone": zone,
                    })

            # Build complete 15-minute observations. Between activities, the
            # person is represented as TRAVEL with interpolated coordinates.
            for idx, (activity, start, end, zone) in enumerate(located):
                next_episode = located[idx + 1] if idx + 1 < len(located) else None
                for t in pd.date_range(
                    date + pd.Timedelta(minutes=int(start)),
                    date + pd.Timedelta(minutes=min(int(end), 1439)),
                    freq=FREQ,
                ):
                    minute = t.hour * 60 + t.minute
                    if minute > end:
                        continue
                    lat, lon = ZONES[zone]
                    observations.append({
                        "person_id": pid,
                        "timestamp": t,
                        "lat": lat + rng.normal(0, 0.0007),
                        "lon": lon + rng.normal(0, 0.0007),
                        "true_zone": zone,
                        "true_activity": activity,
                    })

                if next_episode is not None:
                    next_activity, next_start, _, next_zone = next_episode
                    travel_start = end
                    travel_end = next_start
                    if travel_end > travel_start:
                        travel_times = pd.date_range(
                            date + pd.Timedelta(minutes=int(np.ceil(travel_start / 15) * 15)),
                            date + pd.Timedelta(minutes=int(np.floor(travel_end / 15) * 15)),
                            freq=FREQ,
                        )
                        for t in travel_times:
                            minute = t.hour * 60 + t.minute
                            fraction = (minute - travel_start) / max(travel_end - travel_start, 1)
                            fraction = float(np.clip(fraction, 0, 1))
                            lat, lon = _interpolate_travel(zone, next_zone, fraction, rng)
                            observations.append({
                                "person_id": pid,
                                "timestamp": t,
                                "lat": lat,
                                "lon": lon,
                                "true_zone": "TRAVEL",
                                "true_activity": "TRAVEL",
                            })

    mobile = (pd.DataFrame(observations)
              .drop_duplicates(["person_id", "timestamp"])
              .sort_values(["person_id", "timestamp"])
              .reset_index(drop=True))
    activity_df = pd.DataFrame(activities)

    mobile.to_csv(out / "synthetic_mobile_trajectories.csv", index=False)
    activity_df.to_csv(out / "synthetic_activity_episodes.csv", index=False)

    zones = pd.DataFrame([{"zone": z, "lat": xy[0], "lon": xy[1]} for z, xy in ZONES.items()])
    zones.to_csv(out / "zones.csv", index=False)

    trips = []
    for (pid, date), group in activity_df.sort_values("start_min").groupby(["person_id", "date"]):
        seq = group.to_dict("records")
        for a, b in zip(seq, seq[1:]):
            if a["zone"] != b["zone"]:
                trips.append({
                    "person_id": pid,
                    "date": date,
                    "origin_zone": a["zone"],
                    "destination_zone": b["zone"],
                    "purpose": b["activity"],
                    "departure_min": a["end_min"],
                    "arrival_min": b["start_min"],
                })

    trip_df = pd.DataFrame(trips)
    trip_df.to_csv(out / "trip_records.csv", index=False)

    od = (trip_df.groupby(["origin_zone", "destination_zone"]).size()
          .unstack(fill_value=0)
          .reindex(index=ZONE_NAMES, columns=ZONE_NAMES, fill_value=0))
    od.to_csv(out / "od_matrix.csv")

    print(
        f"Generated {len(mobile):,} observations, "
        f"{len(activity_df):,} activity episodes, and "
        f"{len(trip_df):,} trips in {out}"
    )


if __name__ == "__main__":
    generate()
