### Is 3I/ATLAS behaving like a natural asteroid? A plain‑English look

Interstellar visitors are rare and exciting. 3I/ATLAS has sparked curiosity: its sky path changes, its speed rises near the Sun, and some wonder whether that hints at “propulsion.” We analyzed its motion with NASA JPL Horizons data to see if it matches normal, gravity‑only behavior or if something else might be at work.

### What we measured

- Sky track: how the object appears to drift across the night sky (RA/Dec).
- Solar‑system track: the true path around the Sun (heliocentric X–Y and X–Y–Z).
- Speed along the path: color‑coded so faster segments “heat up.”
- Planet references: Earth and other planets added for context.
- Motion consistency checks:
  - Energy over time: in pure gravity, total orbital energy stays essentially constant.
  - Angular momentum over time: also stays essentially constant.
- Velocity histograms: how fast the asteroid and planets move, side‑by‑side.

### What the results mean

1) Speed increases near the Sun? That’s normal. Just like a spacecraft falling toward a planet, gravity pulls 3I/ATLAS in and it accelerates; it slows as it climbs away. The color‑by‑speed plots and heliocentric trajectory show exactly that.

2) “Unexpected” direction changes? Also normal. Near closest approach, any inbound hyperbolic visitor will curve and “slingshot” past the Sun. That curve is gravity doing its thing.

3) Is there thrust? If an object were actively maneuvering (like a ship), we’d expect its total orbital energy and angular momentum to wobble beyond tiny noise. Our consistency checks show variations that are very small and in line with gravity‑only motion over the time spans we tested.

Bottom line: the motion of 3I/ATLAS is consistent with a natural, unbound (hyperbolic) object. If there are non‑gravitational effects, they’re small enough to sit within the noise and known perturbations.

### Reproduce the analysis

Prerequisites:
- Python 3.10+
- This repository cloned locally

Install:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

A) Sky path with references (geocenter)
```bash
python plot_3I_ATLAS.py --frame sky --bodies sun,venus,mars,jupiter --theme dark --figsize 12,10 --output sky.png
```

B) Heliocentric trajectory (2D), color by speed
```bash
python plot_3I_ATLAS.py --frame heliocentric --bodies mercury,venus,earth,mars,jupiter \
  --color-by speed --cmap plasma --figsize 12,10 --output helio_xy_speed.png
```

C) Heliocentric 3D trajectory (with Earth)
```bash
python plot_3I_ATLAS.py --frame heliocentric3d --bodies mercury,venus,earth,mars,jupiter \
  --theme dark --view-elev 30 --view-azim 60 --figsize 12,12 --output helio_xyz.png
```

D) 3D animation (GIF) — asteroid and planets moving over time
```bash
python plot_3I_ATLAS.py --frame heliocentric3d --bodies mercury,venus,earth,mars,jupiter \
  --animate --anim-fps 20 --anim-output atlas_3d.gif --theme dark --figsize 12,12
```

E) Velocity histograms — asteroid + planets, side‑by‑side
```bash
python plot_3I_ATLAS.py --frame heliocentric3d --bodies mercury,venus,earth,mars,jupiter \
  --velocity-hist --output atlas_hist.png
# Output saved as: atlas_hist_velocity_hist.png
```

F) Motion consistency (energy & angular momentum)
```bash
python analyze_velocity.py --output velocity_overview.png
# Optional: finer resolution to see tiny variations
python analyze_velocity.py --start 2025-07-01 --stop 2026-03-01 --step 6h --output velocity_overview_6h.png
```

Interpretation tips:
- Speed vs time should rise near perihelion then fall: normal gravity.
- Total energy and angular momentum should be nearly flat (small scatter ≲1%).
- Color‑by‑speed tracks should change smoothly with Sun distance.

### What would look suspicious?

- A persistent, non‑random drift in total energy or angular momentum (well beyond small percent‑level noise).
- Repeated, abrupt speed changes not tied to Sun‑distance or known perturbations.
- Spectral or thermal features inconsistent with natural ices/rock/dust (requires separate spectra).

### Conclusion

3I/ATLAS’s motion is classic celestial mechanics: speeding up toward the Sun, curving at perihelion, and coasting out on a hyperbolic path. The energy and angular‑momentum checks back that up. For now, all signs point to a natural interstellar visitor behaving exactly as physics says it should.
