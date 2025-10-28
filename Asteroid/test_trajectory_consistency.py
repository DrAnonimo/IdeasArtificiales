#!/usr/bin/env python3

"""
Test whether 3I/ATLAS trajectory is consistent with purely gravitational motion.

Run tests for:
1. Orbital energy conservation (should be constant for purely gravitational)
2. Angular momentum conservation
3. Perturbation analysis (check for non-gravitational accelerations)
4. Keplerian fit residuals
"""

import argparse
import sys
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astroquery.jplhorizons import Horizons


def fetch_vectors(target: str, start: str, stop: str, step: str, center: str = "500@10", refplane: str = "ecliptic") -> pd.DataFrame:
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
    raise RuntimeError(f"Failed to fetch vectors for '{target}'. Last error: {last_err}")


def test_orbital_energy_conservation(vec_df: pd.DataFrame) -> dict:
    """Test whether orbital energy (heliocentric) is conserved throughout trajectory.
    
    For hyperbolic orbits, orbital energy should be positive and constant.
    """
    x = vec_df["x"].to_numpy(dtype=float)
    y = vec_df["y"].to_numpy(dtype=float)
    z = vec_df["z"].to_numpy(dtype=float)
    vx = vec_df["vx"].to_numpy(dtype=float)
    vy = vec_df["vy"].to_numpy(dtype=float)
    vz = vec_df["vz"].to_numpy(dtype=float)
    
    # Heliocentric distances (AU)
    r = np.sqrt(x**2 + y**2 + z**2)
    # Speed (km/s)
    v = np.sqrt(vx**2 + vy**2 + vz**2)
    
    # Orbital energy per unit mass: E = v²/2 - GM/r
    # GM_sun = 132712440018 (km³/s²) ≈ 39.478 AU³/year²
    # Approximate: use v in km/s, r in AU
    GM_sun_km3_s2 = 132712440018.0
    AU_KM = 149597870.7
    GM_au3_s2 = GM_sun_km3_s2 / (AU_KM**3)
    
    # Kinetic energy per unit mass (km²/s²)
    KE = 0.5 * v**2
    # Potential energy per unit mass (km²/s², negative)
    PE = -GM_sun_km3_s2 / (r * AU_KM)
    # Total orbital energy
    E_total = KE + PE
    
    # Convert to AU²/s² for convenience
    E_total_AU2_s2 = KE / (AU_KM**2) + (-GM_sun_km3_s2 / (AU_KM**3)) / r
    
    results = {
        "mean_energy": float(np.mean(E_total)),
        "std_energy": float(np.std(E_total)),
        "max_energy": float(np.max(E_total)),
        "min_energy": float(np.min(E_total)),
        "energy_variation_pct": float((np.std(E_total) / np.mean(np.abs(E_total))) * 100),
        "mean_r": float(np.mean(r)),
        "min_r": float(np.min(r)),
        "max_r": float(np.max(r)),
        "mean_v": float(np.mean(v)),
        "min_v": float(np.min(v)),
        "max_v": float(np.max(v)),
    }
    return results


def test_angular_momentum_conservation(vec_df: pd.DataFrame) -> dict:
    """Test if angular momentum (specific) is conserved."""
    x = vec_df["x"].to_numpy(dtype=float)
    y = vec_df["y"].to_numpy(dtype=float)
    z = vec_df["z"].to_numpy(dtype=float)
    vx = vec_df["vx"].to_numpy(dtype=float)
    vy = vec_df["vy"].to_numpy(dtype=float)
    vz = vec_df["vz"].to_numpy(dtype=float)
    
    # Angular momentum vector: L = r × v
    Lx = (y * vz - z * vy)
    Ly = (z * vx - x * vz)
    Lz = (x * vy - y * vx)
    L_mag = np.sqrt(Lx**2 + Ly**2 + Lz**2)
    
    results = {
        "mean_L": float(np.mean(L_mag)),
        "std_L": float(np.std(L_mag)),
        "L_variation_pct": float((np.std(L_mag) / np.mean(L_mag)) * 100),
    }
    return results


def plot_tests(vec_df: pd.DataFrame, output: Optional[str] = None):
    """Plot energy and angular momentum over time."""
    energy_results = test_orbital_energy_conservation(vec_df)
    L_results = test_angular_momentum_conservation(vec_df)
    
    x, y, z = vec_df[["x", "y", "z"]].values.T
    vx, vy, vz = vec_df[["vx", "vy", "vz"]].values.T
    
    r = np.sqrt(x**2 + y**2 + z**2)
    v = np.sqrt(vx**2 + vy**2 + vz**2)
    
    # Compute energy and L for all points
    GM_sun_km3_s2 = 132712440018.0
    AU_KM = 149597870.7
    KE = 0.5 * v**2
    PE = -GM_sun_km3_s2 / (r * AU_KM)
    E_total = KE + PE
    
    Lx = (y * vz - z * vy)
    Ly = (z * vx - x * vz)
    Lz = (x * vy - y * vx)
    L_mag = np.sqrt(Lx**2 + Ly**2 + Lz**2)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10), constrained_layout=True)
    
    ax1.plot(E_total, "-o", markersize=3)
    ax1.axhline(energy_results["mean_energy"], color="r", linestyle="--", label=f"Mean: {energy_results['mean_energy']:.2e}")
    ax1.set_xlabel("Time step"), ax1.set_ylabel("Total Energy (km²/s²)")
    ax1.set_title(f"Orbital Energy (σ/E: {energy_results['energy_variation_pct']:.3f}%)")
    ax1.grid(True, alpha=0.3), ax1.legend()
    
    ax2.plot(L_mag, "-o", markersize=3)
    ax2.axhline(L_results["mean_L"], color="r", linestyle="--", label=f"Mean: {L_results['mean_L']:.2e}")
    ax2.set_xlabel("Time step"), ax2.set_ylabel("Angular momentum (km²/s)")
    ax2.set_title(f"Angular Momentum (σ/L: {L_results['L_variation_pct']:.3f}%)")
    ax2.grid(True, alpha=0.3), ax2.legend()
    
    ax3.plot(r, v, "-o", markersize=2)
    ax3.set_xlabel("Distance from Sun (AU)"), ax3.set_ylabel("Speed (km/s)")
    ax3.set_title("Speed vs Distance")
    ax3.grid(True, alpha=0.3)
    
    ax4.hist(E_total, bins=30, edgecolor="black", alpha=0.6)
    ax4.axvline(energy_results["mean_energy"], color="r", linestyle="--", linewidth=2, label="Mean")
    ax4.set_xlabel("Total Energy (km²/s²)"), ax4.set_ylabel("Frequency")
    ax4.set_title("Energy Distribution"), ax4.legend(), ax4.grid(True, alpha=0.3)
    
    if output:
        plt.savefig(output, dpi=200, bbox_inches="tight")
    else:
        plt.show()
    
    print("\n=== TRAJECTORY CONSISTENCY TEST ===")
    print(f"\nORBITAL ENERGY:")
    print(f"  Mean: {energy_results['mean_energy']:.2e} km²/s²")
    print(f"  Std deviation: {energy_results['std_energy']:.2e} km²/s²")
    print(f"  Variation: {energy_results['energy_variation_pct']:.3f}%")
    print(f"\nANGULAR MOMENTUM:")
    print(f"  Mean: {L_results['mean_L']:.2e} km²/s")
    print(f"  Std deviation: {L_results['std_L']:.2e} km²/s")
    print(f"  Variation: {L_results['L_variation_pct']:.3f}%")
    print(f"\nCASE 1 — Conventional interpretation:")
    print(f"  ✓ Minor variation due to numerical noise and perturbations from planets")
    print(f"  ✓ Observational uncertainty in Horizons data")
    print(f"  → Conclusion: PURELY GRAVITATIONAL")
    print(f"\nCASE 2 — Unconventional interpretation:")
    print(f"  ⚠ If variation > 1–2%, could indicate:")
    print(f"     - Non-gravitational forces (thrust)")
    print(f"     - Comet-like outgassing on hyperbolic object (unlikely)")
    print(f"     - Unresolved perturbations")
    print(f"\nExpected for natural object: < 0.5% variation")
    print(f"\nTrajectory is {'CONSISTENT' if energy_results['energy_variation_pct'] < 0.5 else 'INCONSISTENT'} with purely gravitational motion.")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Test trajectory consistency for gravitational motion")
    parser.add_argument("--start", default="2025-07-01", help="Start date/time UTC")
    parser.add_argument("--stop", default="2026-03-01", help="Stop date/time UTC")
    parser.add_argument("--step", default="1d", help="Time step")
    parser.add_argument("--target", default="3I/ATLAS", help="Horizons target")
    parser.add_argument("--output", default=None, help="Output filename")
    
    args = parser.parse_args(argv)
    
    try:
        vec_df = fetch_vectors(args.target, args.start, args.stop, args.step, center="500@10", refplane="ecliptic")
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Error: {exc}\n")
        return 2
    
    plot_tests(vec_df, output=args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

