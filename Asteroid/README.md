## 3I/ATLAS trajectory plot (JPL Horizons)

This small Python tool fetches ephemerides for the interstellar object `3I/ATLAS` from JPL Horizons and plots its sky-plane trajectory (RA/Dec) over a specified date range.

### Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Usage

- Geocentric RA/Dec from 2025-07-01 to 2026-03-01, step 1 day, show interactively:

```bash
python plot_3I_ATLAS.py
```

- Customize dates, step, observer, and save to file:

```bash
python plot_3I_ATLAS.py \
  --start 2025-08-01 \
  --stop 2026-02-01 \
  --step 12h \
  --location 500 \
  --output atlas_ra_dec.png
```

Notes:
- `--location` accepts JPL Horizons observer codes. `500` is geocenter; you can use MPC observatory codes for topocentric ephemerides.
- If the target identifier `3I/ATLAS` returns an error, the script will try a couple of common variations. You can also supply `--target` with the exact designation as recognized by Horizons.
- The RA axis is inverted to match sky plots (east to the left).

### What it does
- Queries JPL Horizons via `astroquery.jplhorizons` for ephemerides (RA, Dec, r, delta, V magnitude, etc.).
- Plots RA vs Dec with a connected line and a few date annotations.

### Requirements
See `requirements.txt`.
