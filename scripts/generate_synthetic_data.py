"""Generate the reproducible V0.1 synthetic mobility dataset.

The generated data are synthetic and intended for development/testing only.
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
            weekday = date.dayofweek < 5
            worker = weekday and rng.random() < 0.82
            schedule = [("HOME", 0, 24 * 60)]

            if worker:
                dep = np.clip(rng.normal(8 * 60, 35), 6 * 60, 10 * 60)
                arr_work = dep + np.clip(rng.normal(35, 15), 15, 75)
                leave_work = np.clip(rng.normal(17 * 60 + 30, 45), 16 * 60, 20 * 60)
                schedule = [("HOME", 0, dep), ("WORK", arr_work, leave_work)]

                r = rng.random()
                if r < 0.35:
                    activity = "SHOPPING"
                elif r < 0.65:
                    activity = "RESTAURANT"
                else:
                    activity = None
                if activity:
                    start = leave_work + rng.uniform(10, 35)
                    duration = rng.uniform(30, 100)
                    schedule.append((activity, start, min(start + duration, 23 * 60)))
            elif rng.random() < 0.65:
                activity = rng.choice(["SHOPPING", "RESTAURANT", "LEISURE"])
                start = rng.uniform(10 * 60, 17 * 60)
                duration = rng.uniform(45, 150)
                schedule.append((activity, start, min(start + duration, 22 * 60)))

            schedule.sort(key=lambda x: x[1])
            episode_locs = []
            for act, start, end in schedule:
                zone = home if act == "HOME" else work if act == "WORK" else rng.choice(ZONE_NAMES)
                episode_locs.append((act, start, end, zone))
                if end > start:
                    activities.append({
                        "person_id": pid,
                        "date": date.date(),
                        "activity": act,
                        "start_min": round(start, 1),
                        "end_min": round(end, 1),
                        "zone": zone,
                    })

            for t in pd.date_range(date, date + pd.Timedelta(hours=23, minutes=45), freq=FREQ):
                minute = t.hour * 60 + t.minute
                selected = next(((a, z) for a, s, e, z in episode_locs if s <= minute <= e), None)
                if selected:
                    act, zone = selected
                    lat, lon = ZONES[zone]
                    observations.append({
                        "person_id": pid,
                        "timestamp": t,
                        "lat": lat + rng.normal(0, 0.0007),
                        "lon": lon + rng.normal(0, 0.0007),
                        "true_zone": zone,
                        "true_activity": act,
                    })

    mobile = pd.DataFrame(observations)
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

    print(f"Generated {len(mobile):,} observations, {len(activity_df):,} activity episodes, and {len(trip_df):,} trips in {out}")


if __name__ == "__main__":
    generate()
