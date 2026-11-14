<p><a href="https://dougalien.com"><img src="assets/dougalien_systems_logo.png" alt="Dougalien Systems" height="48"></a></p>

# Finite Deformable Geometry

The geometry of the universe, read from measurements. A [Dougalien Systems](https://dougalien.com) app.

**Live app:** https://doug-cosmology.streamlit.app/

A register is a measured value divided by its ideal value, so the ideal sits at Q = 1. The app shows only registers: shape (solids, spheres, outlines, orbits, craters), flux dimming (Pantheon+ and DES 5-year supernovae, heliocentric redshifts), time dilation, aging rate (cosmic chronometers), the acoustic angle, cusp flux ratios, and light speed in matter as a departure from the vacuum limit. Each page shows its data and sources.

## Standing order: protect the registers

The registers are the most important part of FDG.

- **A register stands alone, without interpretation.** It is a measured value divided by a geometry-free ideal. Its measured side holds only what arrives at a detector (angles, counts, fluxes, frequency ratios, times). Its ideal takes no theory of the object: no GR or PPN prediction, no equivalence-principle formula, no expansion.
- **Anything that uses an assumption is not a register and is not shown in this app.** That covers a distance beyond parallax, a mass-to-light ratio, a GR ideal, a frame or local-motion correction, or a model map.
- **Registers can be used in calculations** to compare or estimate things. That work never changes a register and is never called a register.
- Work on gravity or cosmology must not break or interfere with the registers.

The app shows registers only (2026-11-14): Shape (solids, outlines), Flux dimming (Pantheon+ and DES 5-year, heliocentric redshift zHEL), Time dilation, Aging rate, Acoustic angle, Cusp, and Light speed in matter (glass, water, air, cold atoms). Earlier illustration pages (rotation, clock and deflection, light and matter, gravity, mass, plasma, no fixed point) and the light-speed rows near mass, in vacuum tests and in plasma are in git history before this change. There is no plasma register: published pulsar lags are DMs fitted with the 1/f² law (Hassall et al. 2012).

## Run it

```
pip install -r requirements.txt
streamlit run register_app.py
```

To put it online, sign in at [share.streamlit.io](https://share.streamlit.io), choose **Create app**, and pick repository `dougalien/Cosmology`, branch `main`, main file `register_app.py`.

## Files

| File | What's in it |
| --- | --- |
| `register_app.py` | The pages |
| `registers.py` | The register calculations and data loading |
| `register_data/` | Published data the registers read (Pantheon+, DES, chronometers, crater counts; some files are no longer read by a page) |
| `dougalien_brand.py`, `assets/`, `.streamlit/config.toml` | The Dougalien Systems look |

The full Pantheon+ STAT+SYS covariance is large and is read from a local folder when present; without it the app uses the binned data and says so.
