<p><a href="https://dougalien.com"><img src="assets/dougalien_systems_logo.png" alt="Dougalien Systems" height="48"></a></p>

# Finite Deformable Geometry

The geometry of the universe, read from measurements. A [Dougalien Systems](https://dougalien.com) app.

**Live app:** https://doug-cosmology.streamlit.app/

A register is a measured value divided by its ideal value, so the ideal sits at Q = 1. The app lays published measurements side by side as registers: shape (solids, spheres, outlines, orbits, craters), flux dimming (Pantheon+ supernovae), time dilation, aging rate (cosmic chronometers), the acoustic angle, cusp flux ratios, galaxy rotation (SPARC), single-value registers, light and matter read together on one object (S2 and binary pulsars), gravity as a departure from one G, light speed as a departure from the vacuum limit, mass as a reading built from measured angles, times and Doppler shifts plus assumed distances and shapes, whether the redshift registers share one shape, and relative motion. Each page shows its data and sources.

## Standing order: protect the registers

The registers are the most important part of FDG.

- **A register stands alone, without interpretation.** It is a measured value divided by a geometry-free ideal. Its measured side holds only what arrives at a detector (angles, counts, fluxes, frequency ratios, times). Its ideal takes no theory of the object: no GR or PPN prediction, no equivalence-principle formula, no expansion.
- **Anything that uses an assumption is an illustration, never a register.** That covers a distance beyond parallax, a mass-to-light ratio, a GR ideal or a model map. Illustrations are kept and labeled, under *Illustrations (not registers)* in the menu, or marked row by row on a register page.
- **Registers can be used in calculations** to compare or estimate things. That work never changes a register and is never called a register.
- Work on gravity or cosmology must not break or interfere with the registers.

Currently illustrations: Rotation, Clock & deflection, Light and matter together, Gravity: departure from G, Mass, Plasma, No fixed point. There is no plasma register: published pulsar lags are DMs fitted with the 1/f² law. Also the near-mass, vacuum-test, calculated and Crab rows on Light speed,.

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
| `register_data/` | Published data the registers read (Pantheon+, SPARC, chronometers, Planck, crater counts) |
| `dougalien_brand.py`, `assets/`, `.streamlit/config.toml` | The Dougalien Systems look |

The full Pantheon+ STAT+SYS covariance is large and is read from a local folder when present; without it the app uses the binned data and says so.
