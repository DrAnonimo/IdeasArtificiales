#!/usr/bin/env python3

import argparse
import sys
from typing import Optional, Tuple, List, Dict

import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
from astroquery.jplhorizons import Horizons
from matplotlib import animation


def parse_figsize(s: Optional[str]) -> Tuple[float, float]:
    if not s:
        return (9.0, 9.0)
    try:
        parts = [float(p) for p in s.split(",")]
        if len(parts) != 2:
            raise ValueError
        return (parts[0], parts[1])
    except Exception as exc:  # noqa: BLE001
        raise argparse.ArgumentTypeError("--figsize must be like '9,9'") from exc


def fetch_ephemerides(
    target: str,
    start: str,
    stop: str,
    step: str,
    location: str = "500",  # Geocenter
) -> pd.DataFrame:
    """
    Fetch ephemerides for a target from JPL Horizons.

    Parameters
    ----------
    target: str
        Target identifier, e.g. "3I/ATLAS".
    start: str
        Start time (UTC) in a format Horizons accepts, e.g. "2025-07-01".
    stop: str
        Stop time (UTC), e.g. "2026-03-01".
    step: str
        Step size, e.g. "1d" or "6h".
    location: str
        Observer location code ("500" = geocenter). For topocentric, use observatory code.
    """
    # Try common identifiers in case Horizons indexing differs
    candidate_ids = [target, "3I", "3I ATLAS", "3I/Atlas"]

    last_err: Optional[Exception] = None
    for cand in candidate_ids:
        try:
            obj = Horizons(id=cand, location=location, epochs={"start": start, "stop": stop, "step": step})
            eph = obj.ephemerides()
            if len(eph) > 0:
                return eph.to_pandas()
        except Exception as exc:  # noqa: BLE001 - provide helpful fallback
            last_err = exc
            continue

    # If we reached here, re-raise the last error with context
    raise RuntimeError(
        f"Failed to fetch ephemerides for target '{target}'. "
        f"Tried candidates: {candidate_ids}. Last error: {last_err}"
    )


def fetch_vectors(
    target: str,
    start: str,
    stop: str,
    step: str,
    center: str = "500@10",  # Sun
    refplane: str = "ecliptic",
) -> pd.DataFrame:
    """Fetch state vectors (X,Y,Z) in AU for a target relative to center.

    center '500@10' is Sun. Use refplane 'ecliptic' or 'earth'.
    """
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


def compute_speed_from_vectors(vec_df: pd.DataFrame) -> np.ndarray:
    """Return speed magnitude in km/s from Horizons vectors table."""
    if not {"vx", "vy", "vz"}.issubset(vec_df.columns):
        raise ValueError("Vectors table missing vx/vy/vz columns")
    vx = vec_df["vx"].to_numpy(dtype=float)
    vy = vec_df["vy"].to_numpy(dtype=float)
    vz = vec_df["vz"].to_numpy(dtype=float)
    return np.sqrt(vx * vx + vy * vy + vz * vz)


def plot_colored_path(
    ax: plt.Axes,
    x: np.ndarray,
    y: np.ndarray,
    values: np.ndarray,
    cmap: str = "viridis",
    linewidth: float = 2.0,
    alpha: float = 1.0,
) -> LineCollection:
    """Plot a line as colored segments according to values and return the collection."""
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, cmap=cmap, linewidth=linewidth, alpha=alpha)
    if len(values) == len(x):
        v = (values[:-1] + values[1:]) / 2.0
    else:
        v = values
    lc.set_array(v)
    ax.add_collection(lc)
    return lc


def fetch_reference_body_ephem(
    bodies: List[str],
    start: str,
    stop: str,
    step: str,
    location: str,
) -> Dict[str, pd.DataFrame]:
    """Fetch RA/Dec for reference solar system bodies from Horizons.

    Bodies are names like 'sun', 'mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune'.
    Returns a dict mapping canonical body name to DataFrame.
    """
    name_to_id = {
        "sun": "10",
        "mercury": "199",
        "venus": "299",
        "earth": "399",
        "mars": "499",
        "jupiter": "599",
        "saturn": "699",
        "uranus": "799",
        "neptune": "899",
    }

    out: Dict[str, pd.DataFrame] = {}
    for raw in bodies:
        name = raw.strip().lower()
        if name not in name_to_id:
            continue
        if name == "earth" and location == "500":
            continue
        try:
            obj = Horizons(id=name_to_id[name], location=location, epochs={"start": start, "stop": stop, "step": step})
            eph = obj.ephemerides()
            if len(eph) > 0:
                out[name] = eph.to_pandas()
        except Exception:
            continue
    return out


def fetch_reference_body_vectors(
    bodies: List[str],
    start: str,
    stop: str,
    step: str,
    center: str = "500@10",
    refplane: str = "ecliptic",
) -> Dict[str, pd.DataFrame]:
    """Fetch heliocentric (or barycentric) vectors for reference bodies."""
    name_to_id = {
        "sun": "10",
        "mercury": "199",
        "venus": "299",
        "earth": "399",
        "mars": "499",
        "jupiter": "599",
        "saturn": "699",
        "uranus": "799",
        "neptune": "899",
    }
    out: Dict[str, pd.DataFrame] = {}
    for raw in bodies:
        name = raw.strip().lower()
        if name not in name_to_id:
            continue
        if name == "sun":
            continue  # center is Sun; no trajectory to plot
        try:
            obj = Horizons(id=name_to_id[name], location=center, epochs={"start": start, "stop": stop, "step": step})
            vec = obj.vectors(refplane=refplane)
            if len(vec) > 0:
                out[name] = vec.to_pandas()
        except Exception:
            continue
    return out


def plot_ra_dec(
    df: pd.DataFrame,
    output: Optional[str] = None,
    title: Optional[str] = None,
    theme: str = "light",
    linewidth: float = 2.0,
    markersize: float = 4.0,
    annotate: bool = True,
    dpi: int = 200,
    aspect: str = "auto",
    ymin: Optional[float] = None,
    ymax: Optional[float] = None,
    ypad: float = 2.0,
    figsize: Tuple[float, float] = (9.0, 9.0),
    ref_bodies: Optional[Dict[str, pd.DataFrame]] = None,
    color_by_speed: bool = False,
    speed_series: Optional[np.ndarray] = None,
    cmap: str = "viridis",
    show_colorbar: bool = True,
) -> None:
    """
    Plot RA vs Dec sky-plane trajectory with improved styling and axis controls.

    Expects RA in hours and DEC in degrees in columns named 'RA' and 'DEC'.
    """
    if not {"RA", "DEC"}.issubset(df.columns):
        missing = {"RA", "DEC"} - set(df.columns)
        raise ValueError(f"Ephemerides are missing required columns: {sorted(missing)}")

    if theme == "dark":
        plt.style.use("dark_background")
        line_color = "#59c"
        annot_color = "#ddd"
        grid_color = (1, 1, 1, 0.15)
        ref_colors = {
            "sun": "#ffcc33",
            "mercury": "#aaaaaa",
            "venus": "#f5c06e",
            "earth": "#33a1ff",
            "mars": "#ff6b57",
            "jupiter": "#c9a97b",
            "saturn": "#e6d2a2",
            "uranus": "#82d1d8",
            "neptune": "#6b8cff",
        }
    else:
        plt.style.use("default")
        line_color = "#0b62a4"
        annot_color = "#222"
        grid_color = (0, 0, 0, 0.15)
        ref_colors = {
            "sun": "#d18b00",
            "mercury": "#666666",
            "venus": "#b8860b",
            "earth": "#0066cc",
            "mars": "#cc3322",
            "jupiter": "#a07a43",
            "saturn": "#b39b66",
            "uranus": "#3aa6b9",
            "neptune": "#3c5fd0",
        }

    ra_hours = df["RA"].to_numpy(dtype=float)
    dec_deg = df["DEC"].to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)

    ra_deg = ra_hours * 15.0

    if color_by_speed and speed_series is not None and len(speed_series) >= 2:
        lc = plot_colored_path(
            ax,
            ra_deg,
            dec_deg,
            values=np.asarray(speed_series, dtype=float),
            cmap=cmap,
            linewidth=linewidth,
            alpha=1.0,
        )
        if show_colorbar:
            cbar = plt.colorbar(lc, ax=ax)
            cbar.set_label("Speed (km/s)")
        if markersize > 0:
            ax.plot(ra_deg, dec_deg, "o", markersize=markersize, color=line_color, alpha=0.4)
    else:
        ax.plot(ra_deg, dec_deg, "-o", markersize=markersize, linewidth=linewidth, color=line_color, label="3I/ATLAS")

    if ref_bodies:
        for name, rdf in ref_bodies.items():
            if not {"RA", "DEC"}.issubset(rdf.columns):
                continue
            r_ra_deg = rdf["RA"].to_numpy(dtype=float) * 15.0
            r_dec = rdf["DEC"].to_numpy(dtype=float)
            ax.plot(
                r_ra_deg,
                r_dec,
                "-s",
                markersize=max(markersize - 1.0, 2.0),
                linewidth=max(linewidth - 0.8, 0.8),
                color=ref_colors.get(name, "#888"),
                alpha=0.9,
                label=name.capitalize(),
            )

    if annotate and len(df) > 0:
        for idx in np.linspace(0, len(df) - 1, num=min(10, len(df)), dtype=int):
            ax.annotate(
                str(df.iloc[idx]["datetime_str"]).split()[0],
                (ra_deg[idx], dec_deg[idx]),
                fontsize=9,
                color=annot_color,
            )

    ax.invert_xaxis()

    current_min_x, current_max_x = np.min(ra_deg), np.max(ra_deg)
    ticks_deg = np.linspace(current_min_x, current_max_x, num=7)
    ax.xaxis.set_major_locator(FixedLocator(ticks_deg))
    ax.set_xticklabels([f"{(td/15):.1f}h" for td in ticks_deg])

    ymin_eff = float(np.min(dec_deg)) if ymin is None else float(ymin)
    ymax_eff = float(np.max(dec_deg)) if ymax is None else float(ymax)
    if ymin is None or ymax is None:
        ymin_eff -= ypad
        ymax_eff += ypad
    ax.set_ylim(ymin_eff, ymax_eff)

    ax.set_xlabel("Right Ascension (hours)")
    ax.set_ylabel("Declination (deg)")
    ax.grid(True, color=grid_color)
    ax.set_aspect(aspect, adjustable="box")
    ax.set_title(title or "3I/ATLAS sky-plane trajectory (geocentric)")
    # Always show legend for reference bodies; main trajectory may be color-mapped without label
    handles, labels = ax.get_legend_handles_labels()
    if labels:
        ax.legend(loc="best")

    if output:
        plt.savefig(output, dpi=dpi, bbox_inches="tight")
    else:
        plt.show()


def plot_heliocentric_3d(
    vec_df: pd.DataFrame,
    output: Optional[str] = None,
    title: Optional[str] = None,
    theme: str = "light",
    linewidth: float = 2.2,
    markersize: float = 0.0,
    dpi: int = 200,
    figsize: Tuple[float, float] = (10.0, 10.0),
    ref_vectors: Optional[Dict[str, pd.DataFrame]] = None,
    show_sun: bool = True,
    color_by_speed: bool = False,
    cmap: str = "viridis",
    show_colorbar: bool = True,
    view_azim: float = 45.0,
    view_elev: float = 20.0,
) -> None:
    """Plot heliocentric ecliptic XYZ trajectory in 3D."""
    if theme == "dark":
        plt.style.use("dark_background")
        traj_color = "#59c"
        grid_color = (1, 1, 1, 0.2)
        planet_colors = {
            "mercury": "#aaaaaa",
            "venus": "#f5c06e",
            "earth": "#33a1ff",
            "mars": "#ff6b57",
            "jupiter": "#c9a97b",
            "saturn": "#e6d2a2",
            "uranus": "#82d1d8",
            "neptune": "#6b8cff",
        }
    else:
        plt.style.use("default")
        traj_color = "#0b62a4"
        grid_color = (0, 0, 0, 0.2)
        planet_colors = {
            "mercury": "#666666",
            "venus": "#b8860b",
            "earth": "#0066cc",
            "mars": "#cc3322",
            "jupiter": "#a07a43",
            "saturn": "#b39b66",
            "uranus": "#3aa6b9",
            "neptune": "#3c5fd0",
        }

    if not {"x", "y", "z"}.issubset(vec_df.columns):
        raise ValueError("Vectors table missing 'x'/'y'/'z' columns (AU)")

    x = vec_df["x"].to_numpy(dtype=float)
    y = vec_df["y"].to_numpy(dtype=float)
    z = vec_df["z"].to_numpy(dtype=float)

    fig = plt.figure(figsize=figsize, constrained_layout=True)
    ax = fig.add_subplot(111, projection="3d")

    if color_by_speed:
        speeds = compute_speed_from_vectors(vec_df)
        for i in range(len(x) - 1):
            segment_speed = (speeds[i] + speeds[i + 1]) / 2.0
            ax.plot(
                [x[i], x[i + 1]],
                [y[i], y[i + 1]],
                [z[i], z[i + 1]],
                "-",
                color=plt.cm.get_cmap(cmap)(segment_speed / speeds.max()),
                linewidth=linewidth,
            )
        if markersize > 0:
            ax.scatter(x, y, z, c=traj_color, s=markersize, alpha=0.4)
        if show_colorbar:
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(speeds.min(), speeds.max()))
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, pad=0.1)
            cbar.set_label("Speed (km/s)")
    else:
        ax.plot(x, y, z, "-", linewidth=linewidth, color=traj_color, label="3I/ATLAS (heliocentric)")
        if markersize > 0:
            ax.scatter(x, y, z, c=traj_color, s=markersize, alpha=0.6)

    if ref_vectors:
        for name, vdf in ref_vectors.items():
            if not {"x", "y", "z"}.issubset(vdf.columns):
                continue
            px, py, pz = vdf["x"].to_numpy(dtype=float), vdf["y"].to_numpy(dtype=float), vdf["z"].to_numpy(dtype=float)
            ax.plot(px, py, pz, "-", linewidth=1.2, color=planet_colors.get(name, "#888"), alpha=0.9, label=name.capitalize())

    if show_sun:
        ax.scatter([0.0], [0.0], [0.0], s=80, c="#ffcc33" if theme == "dark" else "#d18b00", marker="*", label="Sun", depthshade=False)

    ax.set_xlabel("X (AU)")
    ax.set_ylabel("Y (AU)")
    ax.set_zlabel("Z (AU)")
    ax.grid(True, alpha=0.3)
    ax.set_title(title or "3I/ATLAS heliocentric trajectory (ecliptic XYZ)")
    ax.legend(loc="best")

    ax.view_init(elev=view_elev, azim=view_azim)

    if output:
        plt.savefig(output, dpi=dpi, bbox_inches="tight")
    else:
        plt.show()


def plot_heliocentric_xy(
    vec_df: pd.DataFrame,
    output: Optional[str] = None,
    title: Optional[str] = None,
    theme: str = "light",
    linewidth: float = 2.2,
    markersize: float = 0.0,
    dpi: int = 200,
    figsize: Tuple[float, float] = (9.0, 9.0),
    ref_vectors: Optional[Dict[str, pd.DataFrame]] = None,
    show_sun: bool = True,
    color_by_speed: bool = False,
    cmap: str = "viridis",
    show_colorbar: bool = True,
) -> None:
    """Plot heliocentric ecliptic XY trajectory from Horizons vectors (AU)."""
    if theme == "dark":
        plt.style.use("dark_background")
        traj_color = "#59c"
        grid_color = (1, 1, 1, 0.15)
        ref_colors = {
            "mercury": "#aaaaaa",
            "venus": "#f5c06e",
            "earth": "#33a1ff",
            "mars": "#ff6b57",
            "jupiter": "#c9a97b",
            "saturn": "#e6d2a2",
            "uranus": "#82d1d8",
            "neptune": "#6b8cff",
        }
    else:
        plt.style.use("default")
        traj_color = "#0b62a4"
        grid_color = (0, 0, 0, 0.15)
        ref_colors = {
            "mercury": "#666666",
            "venus": "#b8860b",
            "earth": "#0066cc",
            "mars": "#cc3322",
            "jupiter": "#a07a43",
            "saturn": "#b39b66",
            "uranus": "#3aa6b9",
            "neptune": "#3c5fd0",
        }

    if not {"x", "y"}.issubset(vec_df.columns):
        raise ValueError("Vectors table missing 'x'/'y' columns (AU)")

    x = vec_df["x"].to_numpy(dtype=float)
    y = vec_df["y"].to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)

    if color_by_speed:
        speeds = compute_speed_from_vectors(vec_df)
        lc = plot_colored_path(ax, x, y, speeds, cmap=cmap, linewidth=linewidth, alpha=1.0)
        if show_colorbar:
            cbar = plt.colorbar(lc, ax=ax)
            cbar.set_label("Speed (km/s)")
        if markersize > 0:
            ax.plot(x, y, "o", color=traj_color, markersize=markersize, alpha=0.4)
    else:
        ax.plot(x, y, "-", linewidth=linewidth, color=traj_color, label="3I/ATLAS (heliocentric)")
        if markersize > 0:
            ax.plot(x, y, "o", color=traj_color, markersize=markersize)

    if ref_vectors:
        for name, vdf in ref_vectors.items():
            if not {"x", "y"}.issubset(vdf.columns):
                continue
            ax.plot(
                vdf["x"].to_numpy(dtype=float),
                vdf["y"].to_numpy(dtype=float),
                "-",
                linewidth=1.0,
                color=ref_colors.get(name, "#888"),
                alpha=0.9,
                label=name.capitalize(),
            )

    if show_sun:
        ax.scatter([0.0], [0.0], s=60, c="#ffcc33" if theme == "dark" else "#d18b00", marker="*", label="Sun", zorder=5)

    ax.set_xlabel("X (AU) — ecliptic frame, Sun at origin")
    ax.set_ylabel("Y (AU)")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, color=grid_color)
    ax.set_title(title or "3I/ATLAS heliocentric trajectory (ecliptic XY)")
    # Always show legend for Sun/planets; main trajectory may be color-mapped without label
    handles, labels = ax.get_legend_handles_labels()
    if labels:
        ax.legend(loc="best")

    if output:
        plt.savefig(output, dpi=dpi, bbox_inches="tight")
    else:
        plt.show()


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Plot the trajectory of 3I/ATLAS from JPL Horizons")
    parser.add_argument("--start", default="2025-07-01", help="Start date/time UTC (e.g. 2025-07-01)")
    parser.add_argument("--stop", default="2026-03-01", help="Stop date/time UTC (e.g. 2026-03-01)")
    parser.add_argument("--step", default="1d", help="Time step (e.g. 1d, 12h)")
    parser.add_argument("--location", default="500", help="Observer code (500=geocenter, or MPC obs code)")
    parser.add_argument("--target", default="3I/ATLAS", help="Horizons target identifier")
    parser.add_argument("--output", default=None, help="Optional output image filename (e.g. plot.png)")

    parser.add_argument("--frame", choices=["sky", "heliocentric", "heliocentric3d"], default="sky", help="Plot frame: sky-plane RA/Dec, heliocentric XY, or heliocentric XYZ")

    # Styling options
    parser.add_argument("--theme", choices=["light", "dark"], default="light", help="Plot theme")
    parser.add_argument("--linewidth", type=float, default=2.0, help="Line width")
    parser.add_argument("--markersize", type=float, default=4.0, help="Marker size (0 to hide in heliocentric)")
    parser.add_argument("--no-annotate", action="store_true", help="Disable date annotations (sky frame)")
    parser.add_argument("--dpi", type=int, default=200, help="Output image DPI")
    parser.add_argument("--color-by", choices=["none", "speed"], default="none", help="Color code trajectory by value")
    parser.add_argument("--cmap", type=str, default="viridis", help="Matplotlib colormap for color mapping")
    parser.add_argument("--no-colorbar", action="store_true", help="Hide colorbar when color-coding")
    parser.add_argument("--aspect", choices=["auto", "equal"], default="auto", help="Axis aspect ratio (sky frame)")
    parser.add_argument("--ymin", type=float, default=None, help="Y-axis minimum (deg, sky frame)")
    parser.add_argument("--ymax", type=float, default=None, help="Y-axis maximum (deg, sky frame)")
    parser.add_argument("--ypad", type=float, default=2.0, help="Padding added to Y limits when not set (deg, sky frame)")
    parser.add_argument("--figsize", type=str, default="9,9", help="Figure size as 'W,H' in inches")

    # Reference bodies
    parser.add_argument(
        "--bodies",
        type=str,
        default="sun,venus,mars,jupiter",
        help="Comma-separated list of bodies to overlay (sun,mercury,venus,earth,mars,jupiter,saturn,uranus,neptune).",
    )
    parser.add_argument("--no-bodies", action="store_true", help="Disable plotting of reference bodies")

    # Heliocentric vectors options
    parser.add_argument("--refplane", choices=["ecliptic", "earth"], default="ecliptic", help="Reference plane for vectors")

    # 3D view options
    parser.add_argument("--view-elev", type=float, default=20.0, help="3D plot elevation angle (degrees)")
    parser.add_argument("--view-azim", type=float, default=45.0, help="3D plot azimuth angle (degrees)")

    # Animation options (heliocentric frame only)
    parser.add_argument("--animate", action="store_true", help="Create an animation in heliocentric frame")
    parser.add_argument("--anim-fps", type=int, default=15, help="Frames per second for animation")
    parser.add_argument("--anim-output", type=str, default=None, help="Output filename for animation (e.g. traj.mp4 or traj.gif)")

    # Velocity histogram option
    parser.add_argument("--velocity-hist", action="store_true", help="Generate velocity histograms for asteroid and planets")

    args = parser.parse_args(argv)

    if args.frame == "sky":
        try:
            df = fetch_ephemerides(
                target=args.target,
                start=args.start,
                stop=args.stop,
                step=args.step,
                location=args.location,
            )
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(
                "Error fetching ephemerides from JPL Horizons.\n"
                f"Target tried: {args.target}\n"
                f"Details: {exc}\n"
                "If the target identifier fails, try variations like '3I', '3I ATLAS', or use the Horizons web interface to confirm the exact designation.\n"
            )
            return 2

        ref_data: Optional[Dict[str, pd.DataFrame]] = None
        if not args.__dict__["no_bodies"] and args.bodies:
            ref_list = [s.strip() for s in args.bodies.split(",") if s.strip()]
            ref_data = fetch_reference_body_ephem(ref_list, args.start, args.stop, args.step, args.location)

        speed_series: Optional[np.ndarray] = None
        if args.color_by == "speed":
            try:
                vec_df_for_speed = fetch_vectors(
                    target=args.target,
                    start=args.start,
                    stop=args.stop,
                    step=args.step,
                    center="500@10",
                    refplane="ecliptic",
                )
                speed_series = compute_speed_from_vectors(vec_df_for_speed)
                if len(speed_series) != len(df):
                    min_len = min(len(speed_series), len(df))
                    speed_series = speed_series[:min_len]
                    df = df.iloc[:min_len]
            except Exception:
                speed_series = None

        if {"r", "delta", "V"}.issubset(df.columns) and len(df) > 0:
            peri_row = df.loc[df["r"].idxmin()]
            sys.stdout.write(
                f"Loaded {len(df)} ephemeris points. Min heliocentric distance r={peri_row['r']} au at {peri_row['datetime_str']}.\n"
            )

        try:
            plot_ra_dec(
                df,
                output=args.output,
                title=None,
                theme=args.theme,
                linewidth=args.linewidth,
                markersize=args.markersize,
                annotate=not args.__dict__["no_annotate"],
                dpi=args.dpi,
                aspect=args.aspect,
                ymin=args.ymin,
                ymax=args.ymax,
                ypad=args.ypad,
                figsize=parse_figsize(args.figsize),
                ref_bodies=ref_data,
                color_by_speed=(args.color_by == "speed"),
                speed_series=speed_series,
                cmap=args.cmap,
                show_colorbar=not args.__dict__["no_colorbar"],
            )
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Plotting failed: {exc}\n")
            return 3
    elif args.frame == "heliocentric":
        try:
            vec_df = fetch_vectors(
                target=args.target,
                start=args.start,
                stop=args.stop,
                step=args.step,
                center="500@10",
                refplane=args.refplane,
            )
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(
                "Error fetching vectors from JPL Horizons.\n"
                f"Target tried: {args.target}\n"
                f"Details: {exc}\n"
            )
            return 2

        ref_vecs: Optional[Dict[str, pd.DataFrame]] = None
        if not args.__dict__["no_bodies"] and args.bodies:
            ref_list = [s.strip() for s in args.bodies.split(",") if s.strip()]
            ref_vecs = fetch_reference_body_vectors(ref_list, args.start, args.stop, args.step, center="500@10", refplane=args.refplane)

        if args.velocity_hist and args.frame in ["heliocentric", "heliocentric3d"]:
            speeds_dict = {"3I/ATLAS": compute_speed_from_vectors(vec_df)}
            if ref_vecs:
                for name, vdf in ref_vecs.items():
                    try:
                        speeds_dict[name.capitalize()] = compute_speed_from_vectors(vdf)
                    except Exception:
                        continue
            fig, axes = plt.subplots(1, len(speeds_dict), figsize=(4 * len(speeds_dict), 6), constrained_layout=True)
            if len(speeds_dict) == 1:
                axes = [axes]
            for ax, (name, speeds) in zip(axes, speeds_dict.items()):
                ax.hist(speeds, bins=20, edgecolor="black", alpha=0.7)
                ax.set_xlabel("Velocity (km/s)"), ax.set_ylabel("Frequency")
                ax.set_title(f"{name}")
                ax.grid(True, alpha=0.3)
            fig.suptitle("Velocity Histograms", fontsize=14)
            if args.output:
                base = args.output.rsplit(".", 1)[0]
                plt.savefig(f"{base}_velocity_hist.png", dpi=args.dpi, bbox_inches="tight")
            else:
                plt.show()

        try:
            if not args.animate:
                plot_heliocentric_xy(
                    vec_df,
                    output=args.output,
                    title=None,
                    theme=args.theme,
                    linewidth=args.linewidth,
                    markersize=args.markersize,
                    dpi=args.dpi,
                    figsize=parse_figsize(args.figsize),
                    ref_vectors=ref_vecs,
                    show_sun=True,
                    color_by_speed=(args.color_by == "speed"),
                    cmap=args.cmap,
                    show_colorbar=not args.__dict__["no_colorbar"],
                )
            else:
                # Build animation from vectors
                fig, ax = plt.subplots(figsize=parse_figsize(args.figsize), constrained_layout=True)
                # Precompute ranges
                x = vec_df["x"].to_numpy(dtype=float)
                y = vec_df["y"].to_numpy(dtype=float)
                # Planets
                ref_trajs = {}
                if ref_vecs:
                    for name, vdf in ref_vecs.items():
                        ref_trajs[name] = (vdf["x"].to_numpy(dtype=float), vdf["y"].to_numpy(dtype=float))

                # Set style
                if args.theme == "dark":
                    plt.style.use("dark_background")
                    traj_color = "#59c"
                    planet_colors = {
                        "mercury": "#aaaaaa",
                        "venus": "#f5c06e",
                        "earth": "#33a1ff",
                        "mars": "#ff6b57",
                        "jupiter": "#c9a97b",
                        "saturn": "#e6d2a2",
                        "uranus": "#82d1d8",
                        "neptune": "#6b8cff",
                    }
                else:
                    plt.style.use("default")
                    traj_color = "#0b62a4"
                    planet_colors = {
                        "mercury": "#666666",
                        "venus": "#b8860b",
                        "earth": "#0066cc",
                        "mars": "#cc3322",
                        "jupiter": "#a07a43",
                        "saturn": "#b39b66",
                        "uranus": "#3aa6b9",
                        "neptune": "#3c5fd0",
                    }

                # Artists
                asteroid_path, = ax.plot([], [], "-", color=traj_color, linewidth=args.linewidth, label="3I/ATLAS")
                asteroid_dot = ax.plot([], [], "o", color=traj_color, markersize=max(args.markersize, 4))[0]
                planet_paths = {}
                planet_dots = {}
                if ref_trajs:
                    for name, (px, py) in ref_trajs.items():
                        path, = ax.plot([], [], "-", color=planet_colors.get(name, "#888"), linewidth=1.2, label=name.capitalize())
                        dot = ax.plot([], [], "o", color=planet_colors.get(name, "#888"), markersize=4)[0]
                        planet_paths[name] = path
                        planet_dots[name] = dot

                # Sun
                ax.scatter([0.0], [0.0], s=60, c="#ffcc33" if args.theme == "dark" else "#d18b00", marker="*", label="Sun", zorder=5)

                # Limits
                all_x = [x]
                all_y = [y]
                if ref_trajs:
                    for px, py in ref_trajs.values():
                        all_x.append(px)
                        all_y.append(py)
                xmin = float(np.min(np.concatenate(all_x)))
                xmax = float(np.max(np.concatenate(all_x)))
                ymin = float(np.min(np.concatenate(all_y)))
                ymax = float(np.max(np.concatenate(all_y)))
                dx = xmax - xmin
                dy = ymax - ymin
                pad = 0.05 * max(dx, dy)
                ax.set_xlim(xmin - pad, xmax + pad)
                ax.set_ylim(ymin - pad, ymax + pad)
                ax.set_aspect("equal", adjustable="box")
                ax.grid(True, alpha=0.2)
                ax.set_xlabel("X (AU)")
                ax.set_ylabel("Y (AU)")
                ax.set_title("Heliocentric motion (ecliptic XY)")
                ax.legend(loc="best")

                # Initialization and update
                def init():
                    asteroid_path.set_data([], [])
                    asteroid_dot.set_data([], [])
                    for name in planet_paths:
                        planet_paths[name].set_data([], [])
                        planet_dots[name].set_data([], [])
                    return [asteroid_path, asteroid_dot, *planet_paths.values(), *planet_dots.values()]

                n = len(x)
                def update(frame):
                    i = frame
                    asteroid_path.set_data(x[: i + 1], y[: i + 1])
                    asteroid_dot.set_data([x[i]], [y[i]])
                    if ref_trajs:
                        for name, (px, py) in ref_trajs.items():
                            planet_paths[name].set_data(px[: i + 1], py[: i + 1])
                            planet_dots[name].set_data([px[i]], [py[i]])
                    return [asteroid_path, asteroid_dot, *planet_paths.values(), *planet_dots.values()]

                anim = animation.FuncAnimation(fig, update, init_func=init, frames=n, interval=1000/args.anim_fps, blit=True)
                if args.anim_output:
                    out = args.anim_output
                    if out.lower().endswith(".gif"):
                        try:
                            anim.save(out, writer="pillow", fps=args.anim_fps)
                        except Exception as exc:
                            sys.stderr.write(f"GIF save failed: {exc}\n")
                            return 3
                    else:
                        try:
                            anim.save(out, writer="ffmpeg", fps=args.anim_fps)
                        except Exception as exc:
                            sys.stderr.write(f"MP4 save failed: {exc}. Try installing ffmpeg or use .gif\n")
                            return 3
                else:
                    plt.show()
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Plotting failed: {exc}\n")
            return 3
    elif args.frame == "heliocentric3d":
        try:
            vec_df = fetch_vectors(
                target=args.target,
                start=args.start,
                stop=args.stop,
                step=args.step,
                center="500@10",
                refplane=args.refplane,
            )
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(
                "Error fetching vectors from JPL Horizons.\n"
                f"Target tried: {args.target}\n"
                f"Details: {exc}\n"
            )
            return 2

        ref_vecs: Optional[Dict[str, pd.DataFrame]] = None
        if not args.__dict__["no_bodies"] and args.bodies:
            ref_list = [s.strip() for s in args.bodies.split(",") if s.strip()]
            ref_vecs = fetch_reference_body_vectors(ref_list, args.start, args.stop, args.step, center="500@10", refplane=args.refplane)

        if args.velocity_hist:
            speeds_dict = {"3I/ATLAS": compute_speed_from_vectors(vec_df)}
            if ref_vecs:
                for name, vdf in ref_vecs.items():
                    try:
                        speeds_dict[name.capitalize()] = compute_speed_from_vectors(vdf)
                    except Exception:
                        continue
            fig, axes = plt.subplots(1, len(speeds_dict), figsize=(4 * len(speeds_dict), 6), constrained_layout=True)
            if len(speeds_dict) == 1:
                axes = [axes]
            for ax, (name, speeds) in zip(axes, speeds_dict.items()):
                ax.hist(speeds, bins=20, edgecolor="black", alpha=0.7)
                ax.set_xlabel("Velocity (km/s)"), ax.set_ylabel("Frequency")
                ax.set_title(f"{name}")
                ax.grid(True, alpha=0.3)
            fig.suptitle("Velocity Histograms", fontsize=14)
            if args.output:
                base = args.output.rsplit(".", 1)[0]
                plt.savefig(f"{base}_velocity_hist.png", dpi=args.dpi, bbox_inches="tight")
            else:
                plt.show()

        if args.animate:
            # Create 3D animation
            fig = plt.figure(figsize=parse_figsize(args.figsize), constrained_layout=True)
            ax = fig.add_subplot(111, projection="3d")
            x = vec_df["x"].to_numpy(dtype=float)
            y = vec_df["y"].to_numpy(dtype=float)
            z = vec_df["z"].to_numpy(dtype=float)
            ref_trajs = {}
            if ref_vecs:
                for name, vdf in ref_vecs.items():
                    if {"x", "y", "z"}.issubset(vdf.columns):
                        ref_trajs[name] = (vdf["x"].to_numpy(dtype=float), vdf["y"].to_numpy(dtype=float), vdf["z"].to_numpy(dtype=float))
            if args.theme == "dark":
                plt.style.use("dark_background")
                traj_color = "#59c"
                planet_colors = {
                    "mercury": "#aaaaaa", "venus": "#f5c06e", "earth": "#33a1ff", "mars": "#ff6b57",
                    "jupiter": "#c9a97b", "saturn": "#e6d2a2", "uranus": "#82d1d8", "neptune": "#6b8cff",
                }
            else:
                plt.style.use("default")
                traj_color = "#0b62a4"
                planet_colors = {
                    "mercury": "#666666", "venus": "#b8860b", "earth": "#0066cc", "mars": "#cc3322",
                    "jupiter": "#a07a43", "saturn": "#b39b66", "uranus": "#3aa6b9", "neptune": "#3c5fd0",
                }
            asteroid_line, = ax.plot([], [], [], "-", color=traj_color, linewidth=args.linewidth, label="3I/ATLAS")
            asteroid_dot = ax.plot([], [], [], "o", color=traj_color, markersize=max(args.markersize, 6))[0]
            planet_lines, planet_dots = {}, {}
            if ref_trajs:
                for name, (px, py, pz) in ref_trajs.items():
                    planet_lines[name], = ax.plot([], [], [], "-", color=planet_colors.get(name, "#888"), linewidth=1.2, label=name.capitalize())
                    planet_dots[name] = ax.plot([], [], [], "o", color=planet_colors.get(name, "#888"), markersize=4)[0]
            ax.scatter([0.0], [0.0], [0.0], s=80, c="#ffcc33" if args.theme == "dark" else "#d18b00", marker="*", label="Sun", depthshade=False)
            ax.set_xlabel("X (AU)"), ax.set_ylabel("Y (AU)"), ax.set_zlabel("Z (AU)")
            ax.set_title("Heliocentric motion (ecliptic XYZ)")
            ax.grid(True, alpha=0.3)
            ax.legend(loc="best")
            ax.view_init(elev=args.view_elev, azim=args.view_azim)

            def init():
                asteroid_line.set_data([], []), asteroid_line.set_3d_properties([])
                asteroid_dot.set_data([], []), asteroid_dot.set_3d_properties([])
                for name in planet_lines:
                    planet_lines[name].set_data([], []), planet_lines[name].set_3d_properties([])
                    planet_dots[name].set_data([], []), planet_dots[name].set_3d_properties([])
                return [asteroid_line, asteroid_dot, *planet_lines.values(), *planet_dots.values()]

            def update(frame):
                i = frame
                asteroid_line.set_data(x[: i + 1], y[: i + 1]), asteroid_line.set_3d_properties(z[: i + 1])
                asteroid_dot.set_data([x[i]], [y[i]]), asteroid_dot.set_3d_properties([z[i]])
                if ref_trajs:
                    for name, (px, py, pz) in ref_trajs.items():
                        planet_lines[name].set_data(px[: i + 1], py[: i + 1]), planet_lines[name].set_3d_properties(pz[: i + 1])
                        planet_dots[name].set_data([px[i]], [py[i]]), planet_dots[name].set_3d_properties([pz[i]])
                return [asteroid_line, asteroid_dot, *planet_lines.values(), *planet_dots.values()]

            anim = animation.FuncAnimation(fig, update, init_func=init, frames=len(x), interval=1000/args.anim_fps, blit=True)
            if args.anim_output:
                out = args.anim_output
                if out.lower().endswith(".gif"):
                    try:
                        anim.save(out, writer="pillow", fps=args.anim_fps)
                    except Exception as exc:
                        sys.stderr.write(f"GIF save failed: {exc}\n")
                        return 3
                else:
                    try:
                        anim.save(out, writer="ffmpeg", fps=args.anim_fps)
                    except Exception as exc:
                        sys.stderr.write(f"MP4 save failed: {exc}. Try installing ffmpeg or use .gif\n")
                        return 3
            else:
                plt.show()
        else:
            plot_heliocentric_3d(
                vec_df,
                output=args.output,
                title=None,
                theme=args.theme,
                linewidth=args.linewidth,
                markersize=args.markersize,
                dpi=args.dpi,
                figsize=parse_figsize(args.figsize),
                ref_vectors=ref_vecs,
                show_sun=True,
                color_by_speed=(args.color_by == "speed"),
                cmap=args.cmap,
                show_colorbar=not args.__dict__["no_colorbar"],
                view_elev=args.view_elev,
                view_azim=args.view_azim,
            )
        try:
            pass
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"3D plotting failed: {exc}\n")
            return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
