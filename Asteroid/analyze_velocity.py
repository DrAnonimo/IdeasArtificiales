#!/usr/bin/env python3

"""
Analyze velocity and acceleration of 3I/ATLAS from Horizons state vectors.

Computes speed, acceleration, and trajectory curvature from heliocentric velocity vectors.
"""

import argparse
import sys
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astroquery.jplhorizons import Horizons


def fetch_vectors(
    target: str,
    start: str,
    stop: str,
    step: str,
    center: str = "500@10",  # Sun
    refplane: str = "ecliptic",
) -> pd.DataFrame:
    """Fetch state vectors (X,Y,Z,VX,VY,VZ) from Horizons."""
    candidate_ids = [target, "3I", "3I ATLAS", "3I/Atlas"]
    last_err: Optional[Exception] = None
    for cand in candidate_ids:
        try:
            obj = Horizons(id=cand, location=center, epochs={"start": start, "stop": stop, "step": step})
            vec = obj.vectors(refplane=refplane)
            if len(vec) > 0:
                return vec.to_pandas()
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            continue
    raise RuntimeError(
        f"Failed to fetch vectors for target '{target}'. Tried {candidate_ids}. Last error: {last_err}"
    )


def analyze_velocity(ve_df: pd.DataFrame) -> pd.DataFrame:
    """Compute speed, acceleration, turning rate, and curvature from vectors.

    - speed: |v|
    - accel: |dv/dt|
    - turn_angle_rad: angle between successive velocity vectors (rad)
    - turn_rate_deg_per_day: angular turning rate (deg/day)
    - curvature_per_km: |v x a| / |v|^3 (1/km)
    - curvature_per_AU: curvature converted to 1/AU
    """
    if not {"x", "y", "z", "vx", "vy", "vz", "datetime_str"}.issubset(ve_df.columns):
        raise ValueError("Vectors table missing required columns")

    rows = []
    for idx in range(len(ve_df)):
        row = ve_df.iloc[idx]
        # Speed magnitude
        vx = float(row["vx"])
        vy = float(row["vy"])
        vz = float(row["vz"])
        speed = np.sqrt(vx**2 + vy**2 + vz**2)
        rows.append(
            {
                "datetime_str": str(row["datetime_str"]),
                "x": float(row["x"]),
                "y": float(row["y"]),
                "z": float(row["z"]),
                "vx": vx,
                "vy": vy,
                "vz": vz,
                "speed": speed,
            }
        )
    df = pd.DataFrame(rows)

    # Approximate acceleration from finite differences (requires smooth time grid)
    if len(df) >= 2:
        dt_hours = 24.0  # Assume daily step; adjust if needed
        dt_sec = dt_hours * 3600
        dvx = df["vx"].diff().fillna(0.0) / dt_sec
        dvy = df["vy"].diff().fillna(0.0) / dt_sec
        dvz = df["vz"].diff().fillna(0.0) / dt_sec
        df["accel"] = np.sqrt(dvx**2 + dvy**2 + dvz**2)

        # Change in speed
        df["speed_change"] = df["speed"].diff().fillna(0.0)

        # Turning angle between successive velocity vectors
        v_prev = np.stack([df["vx"].shift(1).fillna(df["vx"]).to_numpy(),
                           df["vy"].shift(1).fillna(df["vy"]).to_numpy(),
                           df["vz"].shift(1).fillna(df["vz"]).to_numpy()], axis=1)
        v_now = np.stack([df["vx"].to_numpy(), df["vy"].to_numpy(), df["vz"].to_numpy()], axis=1)
        dot = np.einsum("ij,ij->i", v_prev, v_now)
        norm_prev = np.linalg.norm(v_prev, axis=1)
        norm_now = np.linalg.norm(v_now, axis=1)
        cosang = np.clip(dot / (norm_prev * norm_now + 1e-12), -1.0, 1.0)
        angle = np.arccos(cosang)
        df["turn_angle_rad"] = angle
        df["turn_rate_deg_per_day"] = (angle * 180.0 / np.pi) / 1.0  # since dt=1 day

        # Curvature using kappa = |v x a| / |v|^3 (units of 1/(velocity units * time))
        ax = dvx.to_numpy()
        ay = dvy.to_numpy()
        az = dvz.to_numpy()
        vx = df["vx"].to_numpy()
        vy = df["vy"].to_numpy()
        vz = df["vz"].to_numpy()
        cross_x = vy * az - vz * ay
        cross_y = vz * ax - vx * az
        cross_z = vx * ay - vy * ax
        cross_mag = np.sqrt(cross_x ** 2 + cross_y ** 2 + cross_z ** 2)
        vmag = df["speed"].to_numpy()
        with np.errstate(divide="ignore", invalid="ignore"):
            curvature_per_km = cross_mag / (vmag ** 3 + 1e-18)
        df["curvature_per_km"] = curvature_per_km
        # Convert to 1/AU for an intuitive spatial scale
        KM_PER_AU = 149597870.7
        df["curvature_per_AU"] = curvature_per_km * KM_PER_AU
    else:
        df["accel"] = 0.0
        df["speed_change"] = 0.0
        df["turn_angle_rad"] = 0.0
        df["turn_rate_deg_per_day"] = 0.0
        df["curvature_per_km"] = 0.0
        df["curvature_per_AU"] = 0.0

    return df


def plot_velocity_analysis(
    df: pd.DataFrame,
    output: Optional[str] = None,
    theme: str = "light",
) -> None:
    """Plot speed over time, histogram of speed change, and speed vs turning/curvature."""
    fig, axes = plt.subplots(2, 2, figsize=(13, 10), constrained_layout=True)
    ax1, ax2, ax3, ax4 = axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]

    times = pd.to_datetime(df["datetime_str"].str.split().str[0], format="%Y-%b-%d", errors="coerce")

    if theme == "dark":
        plt.style.use("dark_background")
        color = "#59c"
        grid_color = (1, 1, 1, 0.15)
    else:
        plt.style.use("default")
        color = "#0b62a4"
        grid_color = (0, 0, 0, 0.15)

    ax1.plot(times, df["speed"], "-o", linewidth=2, markersize=4, color=color, label="Speed (km/s)")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Velocity magnitude (km/s)")
    ax1.grid(True, color=grid_color)
    ax1.set_title("Speed Over Time")
    ax1.legend(loc="best")

    ax2.hist(df["speed_change"], bins=20, edgecolor="black", alpha=0.6, color=color)
    ax2.set_xlabel("Speed Change per Day (km/s)")
    ax2.set_ylabel("Frequency")
    ax2.set_title("Speed Change Distribution")
    ax2.grid(True, color=grid_color, axis="y")

    # Speed vs turning rate
    ax3.scatter(df["turn_rate_deg_per_day"], df["speed"], s=18, color=color, alpha=0.8)
    ax3.set_xlabel("Turning rate (deg/day)")
    ax3.set_ylabel("Speed (km/s)")
    ax3.grid(True, color=grid_color)
    ax3.set_title("Speed vs Turning Rate")

    # Speed vs curvature (1/AU)
    ax4.scatter(df["curvature_per_AU"], df["speed"], s=18, color=color, alpha=0.8)
    ax4.set_xlabel("Curvature (1/AU)")
    ax4.set_ylabel("Speed (km/s)")
    ax4.grid(True, color=grid_color)
    ax4.set_title("Speed vs Curvature")

    if output:
        plt.savefig(output, dpi=200, bbox_inches="tight")
    else:
        plt.show()


def print_statistics(df: pd.DataFrame) -> None:
    """Print velocity and acceleration statistics to console."""
    print("\n=== Velocity Analysis ===")
    print(f"Data points: {len(df)}")
    print(f"\nSpeed (km/s):")
    print(f"  Min: {df['speed'].min():.3f}")
    print(f"  Max: {df['speed'].max():.3f}")
    print(f"  Mean: {df['speed'].mean():.3f}")
    print(f"  Std: {df['speed'].std():.3f}")

    if "speed_change" in df.columns:
        abs_change = np.abs(df["speed_change"])
        print(f"\nAbsolute Speed Change per Day (km/s):")
        print(f"  Mean: {abs_change.mean():.6f}")
        print(f"  Max: {abs_change.max():.6f}")
        print(f"  Relative to mean speed: {(abs_change.max() / df['speed'].mean()) * 100:.4f}%")

    if "accel" in df.columns:
        print(f"\nAcceleration magnitude (km/s²):")
        print(f"  Mean: {df['accel'].mean():.6f}")
        print(f"  Max: {df['accel'].max():.6f}")

    if "turn_rate_deg_per_day" in df.columns:
        print(f"\nTurning rate (deg/day):")
        print(f"  Mean: {df['turn_rate_deg_per_day'].mean():.6f}")
        print(f"  Max: {df['turn_rate_deg_per_day'].max():.6f}")

    if "curvature_per_AU" in df.columns:
        print(f"\nCurvature (1/AU):")
        print(f"  Mean: {df['curvature_per_AU'].mean():.6e}")
        print(f"  Max: {df['curvature_per_AU'].max():.6e}")

    print()


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze velocity and acceleration of 3I/ATLAS")
    parser.add_argument("--start", default="2025-07-01", help="Start date/time UTC")
    parser.add_argument("--stop", default="2026-03-01", help="Stop date/time UTC")
    parser.add_argument("--step", default="1d", help="Time step (e.g. 1d)")
    parser.add_argument("--target", default="3I/ATLAS", help="Horizons target identifier")
    parser.add_argument("--output", default=None, help="Optional output image filename")
    parser.add_argument("--theme", choices=["light", "dark"], default="light", help="Plot theme")
    parser.add_argument("--stats-only", action="store_true", help="Only print statistics, no plot")

    args = parser.parse_args(argv)

    try:
        vec_df = fetch_vectors(
            target=args.target,
            start=args.start,
            stop=args.stop,
            step=args.step,
            center="500@10",
            refplane="ecliptic",
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Error fetching vectors: {exc}\n")
        return 2

    df = analyze_velocity(vec_df)
    print_statistics(df)

    if not args.__dict__["stats_only"]:
        try:
            plot_velocity_analysis(df, output=args.output, theme=args.theme)
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Plotting failed: {exc}\n")
            return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

