"""Finite Deformable Geometry: interactive register display.

Run from this folder:
    .venv\\Scripts\\streamlit run register_app.py
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

import dougalien_brand as brand
import registers as R
import sources

st.set_page_config(page_title="Finite Deformable Geometry • Dougalien Systems", page_icon=brand.page_icon("🪐"), layout="wide")
brand.apply_branding()

BLACK, REF = brand.INK, brand.SLATE
PALETTE = [brand.RUST, "#2E7D6B", "#7A5195", "#C08A3E", "#8C564B", "#3B6FB6"]


def ref_line(fig, y=1.0, label="ideal, Q = 1"):
    fig.add_hline(opacity=1, y=y, line=dict(color=REF, dash="dash", width=1.5), annotation_text=label,
                  annotation_position="top left")


def base_layout(fig, xtitle, ytitle, xlog=False, ylog=False, height=480):
    fig.update_layout(title_text="", height=height, template="simple_white", margin=dict(l=60, r=20, t=40, b=50),
                      legend=dict(orientation="h", y=-0.18), hovermode="closest")
    fig.update_xaxes(title=xtitle, type="log" if xlog else "linear", showgrid=True, gridcolor="#E3E6E5")
    fig.update_yaxes(title=ytitle, type="log" if ylog else "linear", showgrid=True, gridcolor="#E3E6E5")
    return fig


def errpts(x, y, e, name, color=BLACK, xerr=None, size=7, symbol="circle", text=None):
    return go.Scatter(x=x, y=y, mode="markers", name=name, text=text,
                      marker=dict(color=color, size=size, symbol=symbol),
                      error_y=dict(type="data", array=e, visible=True, thickness=1.2),
                      error_x=dict(type="data", array=xerr, visible=xerr is not None, thickness=1),
                      hovertemplate="%{text}<br>x=%{x:.4g}<br>Q=%{y:.4g}<extra></extra>" if text else None)


# ------------------------------------------------------------------ cached data
@st.cache_data(show_spinner="Loading Pantheon+ and its covariance…")
def pantheon_plus_register(zcol, lo0, lo1, nbins, full_cov):
    t, cov = R.load_pantheon_plus(full_cov)
    return R.flux_dimming_plus(t, cov, zcol=zcol, lo=(lo0, lo1), nbins=nbins)


@st.cache_data
def rotation_data(ud, ub, inc, qual):
    return R.rotation(ud, ub, inc, qual)


@st.cache_data
def shape_table(max_level):
    rows = []
    for n, faces in R.PLATONIC.items():
        v, f = R.platonic(n)
        rows.append(dict(shape=n, faces=faces, Q_v=R.q_v(*R.mesh_area_volume(v, f))))
    for L in range(1, max_level + 1):
        v, f = R.icosphere_cached(L)
        rows.append(dict(shape=f"Faceted sphere, level {L}", faces=len(f), Q_v=R.q_v(*R.mesh_area_volume(v, f))))
    return pd.DataFrame(rows)


SPHERE_LIMIT = 6 * np.sqrt(np.pi)  # the value the faceted sequence approaches; used only to draw the ideal line


# ------------------------------------------------------------------ pages
def page_premise():
    st.title("Finite Deformable Geometry")
    st.markdown("### The geometry of the universe, read from measurements")
    st.markdown("""
#### 1. What is a register?
A register is a measured value divided by its ideal value, so the ideal sits at **Q = 1**. The ideal is a reference
condition: a perfect sphere, a perfect circle, a straight line, a steady clock, an exactly even series. Each of these is
reached exactly only in a limit that takes infinity, such as infinitely many faces or the last term of an infinite series.
Measured things sit at some distance from that reference. Some sit very close: planetary orbits are within a fraction of a
percent of a circle, and supernova light curves stretch by the full (1 + z). Others sit far away. **The departure from the
ideal, its size and how it changes, is the information.**

#### 2. Why use registers?
- **They use only what arrives at a detector:** counts, flux ratios, angles, frequency ratios (redshift) and time ratios.
- **They carry no units and no size,** so populations of very different scale can be laid side by side.
- **They need no model to compute.** The ideal is a reference point to measure against.
- **Each one stands alone,** so one register can be added, questioned or replaced without disturbing the others.

#### 3. The assumptions currently accepted by the community
The standard picture of the universe begins with assumptions that are not themselves measured:
- **Expanding space,** described by a single scale factor that turns redshift into distance and time.
- **A smooth, uniform universe on large scales** (the cosmological principle), which fixes the geometry before any data arrive.
- **A distance ladder** whose upper rungs use that expansion history to convert brightness and redshift into distance.
- **Dark matter and dark energy,** about 95% of the content, added so that the model fits the data.
- **Infinite series and limits** in the analysis itself, such as the spherical-harmonic expansion of the microwave sky.

The registers start from the measurements instead, so they show what the data look like before any of these are added.

#### 4. The no-fixed-point argument
Within our Galaxy, distance can be measured directly: parallax uses Earth's own orbit as a measured baseline. Beyond the
Galaxy there is no stationary marker to measure from. Every galaxy moves relative to every other, like plates in plate
tectonics, and the two candidate rest frames on the sky (the microwave dipole and the quasar dipole) do not agree. So
**size, speed and distance beyond the Galaxy are calculations**, built on an assumed frame and an assumed expansion. What is
measured is redshift, angle, flux and time, and the registers are written in those. Where a register's data still lean on a
calculated quantity, its page says which one. The *No fixed point* page works through Andromeda as an example.

#### Together, these registers are the shape of the universe
Each register is one population's departure from its ideal. Read side by side, they are the geometry of the universe as
measured from here.
""")
    st.subheader("The registers")
    st.dataframe(pd.DataFrame([
        ["Shape: solids and spheres", "Any closed body", "a perfect sphere (infinitely many faces)", "number of faces", "computed meshes"],
        ["Shape: outlines (2D)", "Polygons, orbits, craters", "a perfect circle (infinitely many sides)", "sides, eccentricity, diameter", "computed outlines, JPL, Robbins and Mars crater catalogs"],
        ["Flux dimming", "Type Ia supernovae", "the local linear flux–redshift relation", "redshift z", "Pantheon, Pantheon+"],
        ["Time dilation", "Transients (supernovae, quasars)", "full (1+z) stretch of light curves", "redshift z", "DES, Blondin, Lewis & Brewer"],
        ["Ageing rate", "Passive galaxies", "a steady rate of redshift change per stellar age", "redshift z", "31 cosmic chronometers"],
        ["Acoustic angle", "Galaxy pairs", "angle shrinking as 1/z", "redshift z", "5 thin-shell angles"],
        ["Cusp", "Lensed image triplets", "a perfectly smooth lens", "opening angle", "3 radio lenses"],
        ["Rotation", "Disk galaxies", "rotation set by visible matter alone", "radius / disk scale", "SPARC"],
        ["Clock", "Clocks at measured g", "frequency shift matching local g", "single value", "Pound–Rebka, lattice clocks"],
        ["Deflection", "Light passing the Sun", "light bends as matter does", "single value", "VLBI, Cassini"],
        ["Light and matter together", "S2, binary pulsars", "light shift equal to the matter swing squared", "system", "GRAVITY, Keck, pulsar timing"],
        ["Gravity: departure from G", "Pulsars, the Sun, S2, disk galaxies", "one G everywhere", "pull from the system's own matter", "pulsar timing, solar-system tests, SPARC"],
        ["Mass: a reading", "Sgr A*, M87*, NGC 5548, disk galaxies", "measured part only (no assumptions)", "each assumption in turn", "GRAVITY, EHT, reverberation, SPARC"],
    ], columns=["Register", "Population", "Ideal (Q = 1)", "Read against", "Data"]), hide_index=True, width="stretch")
    st.caption("The CMB power spectrum is left out because its multipole index comes from a spherical-harmonic expansion, "
               "an infinite series.")


def mini_chart(fig, xtitle, ytitle, xticks=None, yticks=None, xlog=False, ylog=False, ideal=1.0, ideal_label="ideal"):
    """Shared look for the overview cards: same height, labelled axes, clean log ticks, a clear ideal line."""
    fig.update_layout(title_text="", height=300, template="simple_white", showlegend=False,
                      margin=dict(l=55, r=15, t=10, b=45), hovermode="closest", font=dict(size=13))
    fig.update_xaxes(title=xtitle, type="log" if xlog else "linear", showgrid=True, gridcolor="#E3E6E5",
                     tickvals=xticks, ticktext=[f"{t:g}" for t in xticks] if xticks else None)
    fig.update_yaxes(title=ytitle, type="log" if ylog else "linear", showgrid=True, gridcolor="#E3E6E5",
                     tickvals=yticks, ticktext=[f"{t:g}" for t in yticks] if yticks else None)
    if ideal is not None:
        fig.add_hline(opacity=1, y=ideal, line=dict(color=REF, dash="dash", width=2))
        # annotations on a log axis are placed in log10 units
        fig.add_annotation(text=ideal_label, xref="paper", x=1, xanchor="right", y=np.log10(ideal) if ylog else ideal,
                           yanchor="top", showarrow=False, font=dict(color=REF, size=12))
    return fig


def overview_card(col, title, fig, reads):
    with col.container(border=True):
        st.markdown(f"**{title}**")
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.caption(reads)


def page_overview():
    st.title("All registers at a glance")
    st.markdown("Each card is one register: the measurement against its ideal, drawn as a dashed slate line. "
                "Open a register in the sidebar for its controls and details.")
    cards = []

    # Shape: solids and spheres
    df = shape_table(6)
    fig = go.Figure(go.Scatter(x=df.faces, y=df.Q_v, mode="lines+markers", line=dict(color=BLACK, width=2),
                               marker=dict(size=8, color=BLACK), text=df.shape, hovertemplate="%{text}<br>Q_v=%{y:.4f}<extra></extra>"))
    mini_chart(fig, "number of faces", "Q_v = S^1.5 / V", xticks=[4, 10, 100, 1000, 10000, 100000], xlog=True,
               ideal=SPHERE_LIMIT, ideal_label="perfect sphere")
    fig.update_yaxes(range=[10.2, 20])
    cards.append(("Shape: solids and spheres", fig, "Every added face brings a body closer to the sphere."))

    # Shape: outlines
    fig = go.Figure()
    for i, n0 in enumerate((3, 4)):
        seq = R.polygon_doubling(n0, 10)
        fig.add_trace(go.Scatter(x=[n for n, _ in seq], y=[q for _, q in seq], mode="lines+markers",
                                 line=dict(color=PALETTE[i], width=2), marker=dict(size=7)))
    mini_chart(fig, "number of sides", "Q_a = P² / A", xticks=[3, 10, 100, 1000], xlog=True,
               ideal=4 * np.pi, ideal_label="perfect circle")
    fig.update_yaxes(range=[12.2, 21.5])
    cards.append(("Shape: outlines (2D)", fig, "Polygons close in on the circle each time their sides are doubled."))

    # Flux dimming
    zf, Qf, sf, *_ = pantheon_plus_register("zCMB", 0.015, 0.06, 17, R.pantheon_cov_available())
    fig = go.Figure(errpts(zf, Qf, sf, "Pantheon+", size=8))
    mini_chart(fig, "redshift z", "Q", xticks=[0.05, 0.1, 0.2, 0.5, 1, 2], xlog=True)
    fig.update_yaxes(range=[0.9, 1.85])
    cards.append(("Flux dimming", fig, "Supernova light dims faster than the local linear relation as redshift grows (Pantheon+)."))

    # Time dilation
    fig = go.Figure()
    for i, d in enumerate([d for d in R.time_dilation() if d["zmin"] is not None]):
        fig.add_trace(go.Scatter(x=[(d["zmin"] + d["zmax"]) / 2], y=[d["b"]], mode="markers+text", text=[d["study"].split(" 20")[0]],
                                 textposition="top center" if i else "bottom center", marker=dict(size=11, color=PALETTE[i]),
                                 textfont=dict(size=12),
                                 error_y=dict(type="data", array=[d["err"]]),
                                 error_x=dict(type="data", array=[(d["zmax"] - d["zmin"]) / 2])))
    fig.add_hline(opacity=1, y=0, line=dict(color=BLACK, dash="dot", width=1.5), annotation_text="no stretch",
                  annotation_position="top right", annotation_font=dict(size=12))
    mini_chart(fig, "redshift z", "stretch exponent b", ideal_label="full (1 + z) stretch")
    fig.update_xaxes(range=[0, 1.3]); fig.update_yaxes(range=[-0.15, 1.4])
    cards.append(("Time dilation", fig, "Supernova light curves stretch by the full (1 + z): the one register that sits on its ideal."))

    # Ageing rate
    z, q, e, *_ = R.ageing(True)
    fig = go.Figure(errpts(z, q, e, "chronometers", size=8))
    mini_chart(fig, "redshift z", "|dz/dt| ÷ local rate")
    cards.append(("Ageing rate", fig, "The rate of redshift change per stellar age climbs to about six times the local rate by z ≈ 2."))

    # Acoustic angle
    z, q, e = R.acoustic_angle()
    fig = go.Figure(errpts(z, q, e, "angles", size=9, text=R.ANGLES["source"]))
    mini_chart(fig, "redshift z", "θ·z ÷ (θ·z) at z = 0.11")
    fig.update_yaxes(range=[0.8, 2.25])
    cards.append(("Acoustic angle", fig, "Galaxy-pair angles follow 1/z nearby, then shrink more slowly than 1/z beyond z ≈ 1."))

    # Cusp
    fig = go.Figure()
    for i, (k, v) in enumerate(R.CUSP.items()):
        qs = np.array([R.cusp_q(a, b, c) for _, a, b, c in v[4]])
        fig.add_trace(go.Scatter(x=[v[0]], y=[np.median(qs)], mode="markers+text", text=[k], textposition="middle right",
                                 marker=dict(size=12, color=PALETTE[i]), error_y=dict(type="data", array=[np.std(qs, ddof=1)]),
                                 textfont=dict(size=12)))
    mini_chart(fig, "opening angle of the triplet (degrees)", "F_mid ÷ (F_out1 + F_out2)", ideal_label="smooth lens")
    fig.update_xaxes(range=[25, 100]); fig.update_yaxes(range=[0, 1.15])
    cards.append(("Cusp flux ratio", fig, "In all three radio lenses the middle image is fainter than the outer pair together."))

    # Rotation
    q, gb, fd, names, ng, rr = rotation_data(0.5, 0.7, 30, 2)
    x, y, lo, hi = R.binned_median_x(rr, q, np.logspace(-1, 1.3, 12))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.r_[x, x[::-1]], y=np.r_[hi, lo[::-1]], fill="toself", fillcolor=PALETTE[0], opacity=0.18,
                             line_width=0, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", line=dict(color=BLACK, width=2), marker=dict(size=7)))
    mini_chart(fig, "radius ÷ disk scale length", "g_obs ÷ g_bar", xticks=[0.1, 0.3, 1, 3, 10, 20], yticks=[1, 2, 3, 5, 10],
               xlog=True, ylog=True, ideal_label="visible matter alone")
    cards.append(("Galaxy rotation", fig, f"Median of {ng} SPARC galaxies with the middle 68% shaded: the departure grows outward."))

    # Light and matter together
    lm = pd.DataFrame(R.light_matter_table())
    fig = go.Figure()
    for i, r in lm.iterrows():
        fig.add_trace(go.Scatter(x=[r.Q], y=[r.system], mode="markers", marker=dict(size=10, color=PALETTE[i % len(PALETTE)]),
                                 error_x=dict(type="data", array=[r.err]),
                                 hovertemplate=f"{r.system}<br>Q = {r.Q:.5g} ± {r.err:.2g}<extra></extra>"))
    fig.add_vline(opacity=1, x=1.0, line=dict(color=REF, dash="dash", width=2))
    mini_chart(fig, "light register ÷ matter register", "", ideal=None)
    fig.update_yaxes(type="category", autorange="reversed", tickfont=dict(size=10))
    cards.append(("Light and matter together", fig, "Where both registers are read on one object (S2, binary pulsars) they agree; "
                  "the raw Hulse–Taylor offset is the Galaxy's pull."))

    # Gravity: departure from G
    gq, ggb, _, _ = R.gravity_galaxies()
    gx, gy, glo, ghi, _ = R.gravity_readings(ggb, gq)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.r_[gx, gx[::-1]], y=np.r_[ghi, glo[::-1]], fill="toself", fillcolor=PALETTE[0], opacity=0.18,
                             line_width=0, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=gx, y=gy, mode="lines+markers", line=dict(color=BLACK, width=2), marker=dict(size=6)))
    comp = R.gravity_compact()
    fig.add_trace(go.Scatter(x=[c[1] for c in comp], y=[c[2] for c in comp], mode="markers", text=[c[0] for c in comp],
                             marker=dict(size=9, color=PALETTE[1], symbol="diamond"), hovertemplate="%{text}<extra></extra>"))
    mini_chart(fig, "pull from own matter (m/s²)", "Q_G", xticks=[1e-12, 1e-9, 1e-6, 1e-3, 1, 1000], yticks=[1, 2, 5, 10],
               xlog=True, ylog=True, ideal_label="one G everywhere")
    fig.update_xaxes(ticktext=["10⁻¹²", "10⁻⁹", "10⁻⁶", "10⁻³", "1", "10³"])
    cards.append(("Gravity: departure from G", fig, "One G holds from neutron-star binaries to the planets; in thin galaxy "
                  "outskirts the pull grows to several times what the visible matter gives."))

    for i in range(0, len(cards), 2):
        cols = st.columns(2)
        for col, (title, fig, reads) in zip(cols, cards[i:i + 2]):
            overview_card(col, title, fig, reads)
    st.caption("The clock (Q = 1) and light deflection (Q = 2) registers are single values; see Clock & deflection.")


def page_same_shape():
    st.title("Do the registers share one shape?")
    st.markdown(
        "Each redshift register is set to Q = 1 by the nearby population, so its departure from the ideal is zero by "
        "construction at z = 0. Read from far to near, the departure shrinks toward zero as the light's path to us shortens. "
        "That is the same pattern as the shape registers, where the departure shrinks toward zero as a body gains faces; "
        "in both cases the zero point is a limit (a path of zero length, infinitely many faces).\n\n"
        "To test whether the registers share a shape, plot them against **1 + z** on log–log axes. If a register is a power "
        "of (1 + z), Q = (1 + z)^p, its departure ln Q = p · ln(1 + z) falls on a straight line that runs down to zero at "
        "z = 0, and p measures how quickly the departure grows with path. The same shape with a different strength gives "
        "straight lines with different slopes."
    )
    zf, Qf, sf, *_ = pantheon_plus_register("zCMB", 0.015, 0.06, 17, R.pantheon_cov_available())
    za, Qa, sa, *_ = R.ageing(True)
    zg, Qg, sg = R.acoustic_angle()
    sets = {
        "Flux dimming": (1 + zf, Qf, sf),
        "Ageing rate": (1 + za, Qa, sa),
        "Acoustic angle": (1 + zg[1:], Qg[1:], sg[1:]),  # the anchor point is Q = 1 by construction
    }
    des = next(d for d in R.time_dilation() if d["study"].startswith("White"))
    fits = {k: R.power_fit(*v) for k, v in sets.items()}

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        xx = np.geomspace(1, 3.3, 50)
        for i, (k, (x, Q, s)) in enumerate(sets.items()):
            p = fits[k][0]
            fig.add_trace(errpts(x, Q, s, k, PALETTE[i]))
            fig.add_trace(go.Scatter(x=xx, y=xx ** p, mode="lines", line=dict(color=PALETTE[i], width=1.5), name=f"(1+z)^{p:.2f}"))
        p_t = des["b"] - 1
        xt = np.geomspace(1 + des["zmin"], 1 + des["zmax"], 20)
        fig.add_trace(go.Scatter(x=xt, y=xt ** p_t, mode="lines", line=dict(color=PALETTE[3], width=3),
                                 name=f"Time dilation (DES): (1+z)^{p_t:.3f}"))
        ref_line(fig, label="ideal, Q = 1")
        base_layout(fig, "1 + z", "Q", xlog=True, ylog=True, height=500)
        st.plotly_chart(fig, width="stretch")
        st.caption("Each register with its own power of (1 + z). Straight lines on these axes mean a power law.")
    with c2:
        fig = go.Figure()
        for i, (k, (x, Q, s)) in enumerate(sets.items()):
            p = fits[k][0]
            fig.add_trace(go.Scatter(x=np.log(x), y=np.log(Q) / p, mode="markers", name=k, marker=dict(size=7, color=PALETTE[i]),
                                     error_y=dict(type="data", array=s / Q / p, thickness=1)))
        ll = np.linspace(0, 1.2, 10)
        fig.add_trace(go.Scatter(x=ll, y=ll, mode="lines", line=dict(color=BLACK, dash="dot"), name="one shared shape"))
        base_layout(fig, "ln(1 + z)", "ln Q ÷ p", height=500)
        st.plotly_chart(fig, width="stretch")
        st.caption("The same data with each register divided by its own strength p. If they share one shape they collapse "
                   "onto the dotted line.")

    rows = [dict(register=k, exponent_p=v[0], error=v[1], chi2=v[2], points=v[3], chi2_per_dof=v[2] / max(v[3] - 1, 1))
            for k, v in fits.items()]
    rows.append(dict(register="Time dilation (DES)", exponent_p=des["b"] - 1, error=des["err"], chi2=np.nan, points=1, chi2_per_dof=np.nan))
    st.dataframe(pd.DataFrame(rows).style.format({"exponent_p": "{:.3f}", "error": "{:.3f}", "chi2": "{:.1f}",
                                                  "chi2_per_dof": "{:.2f}"}, na_rep="—"), hide_index=True, width="stretch")
    pc, chi_c, dof_c = R.common_power_test(list(sets.values()))
    (pf, ef, *_), (pa, ea, *_), (pg, eg, *_) = fits["Flux dimming"], fits["Ageing rate"], fits["Acoustic angle"]
    sig_fg = abs(pf - pg) / np.hypot(ef, eg)
    st.markdown(f"""
**What the check says**

- **Same form.** Each redshift register is close to a power of (1 + z). Flux dimming and the acoustic angle fit within
  their errors. The ageing rate follows the same trend with more scatter than its quoted errors, which leave out the
  correlated chronometer uncertainties.
- **Different strength.** Forcing one exponent on all three gives p = {pc:.2f} with χ² = {chi_c:.0f} for {dof_c} degrees of
  freedom, so one shared strength is ruled out. In order: time dilation p = {des['b'] - 1:.3f} (it stays at its ideal),
  acoustic angle p = {pg:.2f}, flux dimming p = {pf:.2f} (these two differ by {sig_fg:.1f}σ), ageing rate p = {pa:.2f}
  (about {pa / pf:.1f} times flux dimming).
- So the registers look alike because they share a form: each departure falls smoothly toward zero as the light's path
  shortens, along a power of (1 + z), with each population at its own rate.
- **At the far end the data do not show the departure turning back toward zero.** The largest departures are at the
  highest redshifts. The last three flux-dimming bins (z ≈ 1.0 to 1.6) sit level near Q ≈ 1.65, which may be the first
  sign of the departure levelling off rather than continuing to grow; more supernovae beyond z ≈ 1.5 would settle it.
""")
    st.caption("Each point's own error is used; correlations between points are ignored in these fits.")

    st.subheader("A link between two registers: flux dimming × acoustic angle")
    st.markdown("If the two exponents add to 1, then multiplying the two registers gives back the frequency ratio itself: "
                "**Q_flux × Q_angle = 1 + z**. That ties how bright supernovae look to how large galaxy-pair angles look, "
                "using redshift alone.")
    zg1, Qg1, sg1 = zg[1:], Qg[1:], sg[1:]
    inside = zg1 <= zf.max()
    # flux register at the angle redshifts: read from the bins where they overlap, from its power law beyond them
    Qf_at = np.where(inside, np.exp(np.interp(np.log1p(zg1), np.log1p(zf), np.log(Qf))), (1 + zg1) ** pf)
    prod = Qf_at * Qg1
    e_prod = prod * (sg1 / Qg1)
    c1, c2 = st.columns([3, 2])
    with c1:
        fig = go.Figure()
        for mask, sym, lab in [(inside, "circle", "flux read from its bins"), (~inside, "circle-open", "flux from its power law (beyond the supernova data)")]:
            fig.add_trace(go.Scatter(x=1 + zg1[mask], y=prod[mask], mode="markers", name=lab,
                                     marker=dict(size=11, color=PALETTE[0], symbol=sym, line=dict(width=2, color=PALETTE[0])),
                                     error_y=dict(type="data", array=e_prod[mask])))
        xx = np.linspace(1, 3.4, 20)
        fig.add_trace(go.Scatter(x=xx, y=xx, mode="lines", line=dict(color=BLACK, dash="dot"), name="Q_flux × Q_angle = 1 + z"))
        base_layout(fig, "1 + z", "Q_flux × Q_angle", height=420)
        st.plotly_chart(fig, width="stretch")
    with c2:
        s_sum = np.hypot(ef, eg)
        st.metric("Sum of exponents p_flux + p_angle", f"{pf + pg:.2f} ± {s_sum:.2f}",
                  f"{abs(pf + pg - 1) / s_sum:.1f}σ from exactly 1", delta_color="off")
        st.dataframe(pd.DataFrame({"z": zg1, "Q_flux": Qf_at, "Q_angle": Qg1, "product": prod, "1 + z": 1 + zg1,
                                   "off by (σ)": (prod - 1 - zg1) / e_prod}).style.format(precision=2),
                     hide_index=True, width="stretch")
    st.caption("The two registers come from different populations, supernovae and galaxy pairs, measured by different surveys. "
               "The exponents add to 1 within their errors. Point by point, the two high-redshift products sit within 1σ of "
               "1 + z and the two low-redshift ones fall short of it, by about 1σ and 2σ (see the table). An expanding-space picture "
               "predicts the same relation, so this is a check that the two registers agree with each other.")


def page_shape():
    st.title("Shape: solids and spheres")
    st.markdown(
        "**Q_v = S^(3/2) / V** compares a body's surface S with the volume V it holds. It has no units and does not change "
        "with size. Every number here comes straight from a triangle mesh: the area is a sum of triangle areas and the "
        "volume a sum of small tetrahedra."
    )
    max_level = st.sidebar.slider("Finest faceted-sphere level", 2, 7, 6,
                                  help="Each level splits every triangle into four: 20·4^level faces.")
    df = shape_table(max_level)
    c1, c2 = st.columns([3, 2])
    with c1:
        fig = go.Figure()
        pl, ic = df.iloc[:5], df.iloc[5:]
        fig.add_trace(go.Scatter(x=pl.faces, y=pl.Q_v, mode="markers+text", text=pl.shape, textposition="top right",
                                 marker=dict(size=11, color=BLACK), name="Platonic solids"))
        fig.add_trace(go.Scatter(x=[20] + list(ic.faces), y=[pl.Q_v.iloc[-1]] + list(ic.Q_v), mode="lines+markers",
                                 marker=dict(size=7, color=PALETTE[2]), name="Faceted spheres (icosahedron split again and again)"))
        fig.add_hline(opacity=1, y=SPHERE_LIMIT, line=dict(color=REF, dash="dash"),
                      annotation_text="perfect sphere")
        base_layout(fig, "number of faces", "Q_v", xlog=True, height=520)
        fig.update_yaxes(range=[10.3, 20.5])
        st.plotly_chart(fig, width="stretch")
    with c2:
        st.dataframe(df.style.format({"Q_v": "{:.5f}"}), hide_index=True, width="stretch", height=430)
    st.info(f"At level {max_level} the body has {20 * 4 ** max_level:,} faces and Q_v = {df.Q_v.iloc[-1]:.6f}, "
            f"against {SPHERE_LIMIT:.6f} for the sphere. Each level closes about three quarters of the remaining gap.")

    st.subheader("Real bodies")
    c1, c2 = st.columns(2)
    with c1:
        q6 = R.spheroid_qv(0.0, 6)
        rows = [dict(body=b, flattening=f, Q_v=R.spheroid_qv(f, 6)) for b, f in R.BODIES.items()]
        bd = pd.DataFrame(rows)
        bd["Q_v / round body"] = bd.Q_v / q6
        st.markdown("Planets and the Sun as flattened spheres (measured flattening, level-6 mesh):")
        st.dataframe(bd.style.format({"flattening": "{:.5f}", "Q_v": "{:.5f}", "Q_v / round body": "{:.6f}"}),
                     hide_index=True, width="stretch")
        st.caption("The last column compares each body with an unflattened body on the same mesh. Spinning bodies bulge at "
                   "the equator, so every one sits above it; Saturn, the flattest, sits highest.")
    with c2:
        rough = st.slider("Roughness of a rubble-pile body", 0.0, 0.4, 0.15, 0.01)
        seed = st.number_input("Random seed", 0, 999, 3)
        v, f = R.lumpy_body(4, rough, int(seed))
        qv = R.q_v(*R.mesh_area_volume(v, f))
        st.metric("Q_v of this body", f"{qv:.3f}")
        mesh = go.Figure(go.Mesh3d(x=v[:, 0], y=v[:, 1], z=v[:, 2], i=f[:, 0], j=f[:, 1], k=f[:, 2],
                                   color="#a0896b", flatshading=True, lighting=dict(ambient=0.4, diffuse=0.8)))
        mesh.update_layout(title_text="", height=360, margin=dict(l=0, r=0, t=0, b=0), scene=dict(aspectmode="data",
                           xaxis_visible=False, yaxis_visible=False, zaxis_visible=False))
        st.plotly_chart(mesh, width="stretch")


CIRCLE_LIMIT = 4 * np.pi  # the value the doubled polygons approach; used only to draw the ideal line


def page_outline():
    st.title("Shape: outlines (2D)")
    st.markdown(
        "**Q_a = P² / A** compares an outline's boundary length P with the area A it encloses. It has no units and does "
        "not change with size. The ideal is a perfect circle."
    )
    tab1, tab2, tab3 = st.tabs(["Regular polygons", "Orbits", "Craters on the Moon and Mars"])
    with tab1:
        levels = st.slider("Times each polygon's sides are doubled", 1, 14, 8)
        fig = go.Figure()
        rows = []
        for i, n0 in enumerate(R.POLYGON_SEEDS):
            seq = R.polygon_doubling(n0, levels)
            fig.add_trace(go.Scatter(x=[n for n, _ in seq], y=[q for _, q in seq], mode="lines+markers",
                                     marker=dict(size=7, color=PALETTE[i]), name=f"starting from {n0} sides"))
            rows += [dict(sides=n, Q_a=q) for n, q in seq]
        fig.add_hline(opacity=1, y=CIRCLE_LIMIT, line=dict(color=REF, dash="dash"), annotation_text="perfect circle")
        base_layout(fig, "number of sides", "Q_a", xlog=True, height=480)
        fig.update_yaxes(range=[12.3, 21.3])
        st.plotly_chart(fig, width="stretch")
        st.caption("Each polygon is drawn inside the same circle and its sides are doubled again and again, the way Archimedes "
                   "did it: the new side is √(2 − √(4 − s²)), with no angles or π. Every doubling brings Q_a closer to the "
                   "circle.")
        df = pd.DataFrame(rows).drop_duplicates("sides").sort_values("sides")
        st.dataframe(df.style.format({"Q_a": "{:.9f}"}), hide_index=True, width="stretch", height=260)
    with tab2:
        rows = [dict(object=n, kind=k, eccentricity=e, Q_a=R.ellipse_q(e)) for n, k, e in R.ORBITS]
        od = pd.DataFrame(rows)
        od["Q_a / circle"] = od.Q_a / CIRCLE_LIMIT
        ee = np.linspace(0, 0.995, 120)
        fig = go.Figure(go.Scatter(x=ee, y=[R.ellipse_q(e, 4000) for e in ee], mode="lines", line=dict(color="#9AA5AB"),
                                   name="any ellipse"))
        for i, k in enumerate(od.kind.unique()):
            sub = od[od.kind == k]
            fig.add_trace(go.Scatter(x=sub.eccentricity, y=sub.Q_a, mode="markers+text", text=sub.object, textposition="top left",
                                     marker=dict(size=10, color=PALETTE[i % len(PALETTE)]), name=k))
        fig.add_hline(opacity=1, y=CIRCLE_LIMIT, line=dict(color=REF, dash="dash"), annotation_text="perfect circle")
        base_layout(fig, "eccentricity", "Q_a of the orbit", ylog=True, height=480)
        st.plotly_chart(fig, width="stretch")
        st.dataframe(od.style.format({"eccentricity": "{:.4f}", "Q_a": "{:.6f}", "Q_a / circle": "{:.6f}"}),
                     hide_index=True, width="stretch")
        st.caption("Each orbit is traced as a fine polygon from its measured eccentricity (JPL). The planets sit within a "
                   "fraction of a percent of the circle; the comets sit far above it.")
    with tab3:
        fig = go.Figure()
        for i, body in enumerate(["moon", "mars"]):
            b = R.crater_bins(body)
            d = np.array([r["d"] for r in b]); q = np.array([r["q"] for r in b])
            fig.add_trace(go.Scatter(x=d, y=q, mode="lines+markers", marker=dict(size=9, color=PALETTE[i]), name=f"{body.title()} (median)",
                                     text=[f"{r['bin']}: {r['n']:,} craters" for r in b], hovertemplate="%{text}<br>Q_a=%{y:.4f}<extra></extra>",
                                     error_y=dict(type="data", symmetric=False, array=[r["q95"] - r["q"] for r in b],
                                                  arrayminus=[r["q"] - r["q05"] for r in b])))
        fig.add_hline(opacity=1, y=CIRCLE_LIMIT, line=dict(color=REF, dash="dash"), annotation_text="perfect circle")
        base_layout(fig, "crater diameter (km)", "Q_a of the rim ellipse", xlog=True, height=480)
        st.plotly_chart(fig, width="stretch")
        st.caption("About 1.3 million lunar craters (Robbins 2018) and 385,000 Martian craters, each from the ellipse fitted to "
                   "its traced rim. Points are medians and bars the 5th to 95th percentiles. Craters on both bodies stay close "
                   "to the circle, and larger craters come closer than small ones.")


def page_flux():
    st.title("Flux dimming")
    st.markdown("Q = 10^((m − C)/5) / z: the dimming of supernova light divided by redshift, with the nearby supernovae "
                "setting Q = 1. It is built from magnitudes (flux ratios) and redshifts (frequency ratios).")
    src = st.sidebar.radio("Data", ["Pantheon+ (binned with covariance)", "Pantheon 2018 (40 bins)"])
    fig = go.Figure()
    if src.startswith("Pantheon+"):
        full = st.sidebar.checkbox("Use full STAT+SYS covariance", value=R.pantheon_cov_available(),
                                   disabled=not R.pantheon_cov_available(),
                                   help="Reads the 33 MB covariance from the manuscript folder.")
        zcol = st.sidebar.radio("Redshift column", ["zCMB", "zHD"], horizontal=True,
                                help="zCMB is the measured redshift in the CMB frame. zHD adds a modelled correction for local motions.")
        lo = st.sidebar.slider("Nearby supernovae that set Q = 1 (redshift range)", 0.01, 0.12, (0.015, 0.06), 0.005)
        nb = st.sidebar.slider("Number of bins", 8, 30, 17)
        zb, Q, sQ, n, na, nt = pantheon_plus_register(zcol, lo[0], lo[1], nb, full)
        fig.add_trace(errpts(zb, Q, sQ, f"Pantheon+ ({nt} supernovae, {na} nearby)", text=[f"n={k}" for k in n]))
        if st.sidebar.checkbox("Overlay Pantheon 2018 bins", value=True):
            zq, Qb, _ = R.flux_dimming_binned()
            fig.add_trace(go.Scatter(x=zq, y=Qb, mode="markers", marker=dict(color="#6B7A82", size=5), name="Pantheon 2018 bins"))
    else:
        za = st.sidebar.slider("Bins below this redshift set Q = 1", 0.02, 0.1, 0.05, 0.005)
        zq, Qb, sQb = R.flux_dimming_binned(za)
        fig.add_trace(errpts(zq, Qb, sQb, "Pantheon 2018 (40 bins)"))
    ref_line(fig, label="local linear relation, Q = 1")

    st.sidebar.markdown("**Response shapes to compare (optional)**")
    z, m, s = R.pantheon_binned()
    zz = np.geomspace(0.01, 2.3, 300)
    rows = []
    for i, (name, (fn, q0, c0, uc)) in enumerate(R.LAWS.items()):
        if not st.sidebar.checkbox(name, value=False, key="law" + name):
            continue
        refit = q0 is not None and st.sidebar.checkbox("best match to the bins", key="refit" + name)
        if q0 is None:
            q, c = 0.0, 0.0
        elif refit:
            q, c = R.fit_law(fn, q0, c0, uc, z, m, s)
        else:
            q = st.sidebar.slider(f"q  ({name})", 0.05, 3.0, float(q0), 0.01, key="q" + name)
            c = st.sidebar.slider("c", 0.0, 1.0, float(c0), 0.01, key="c" + name) if uc else 0.0
        chi2, rms = R.law_stats(fn, q, c, z, m, s)
        rows.append(dict(shape=name, q=q, c=c, chi2=chi2, dof=40 - (0 if q0 is None else 2 if uc else 1) - 1, rms_mag=rms))
        fig.add_trace(go.Scatter(x=zz, y=fn(zz, q, c), mode="lines", line=dict(color=PALETTE[i + 1], width=2), name=f"{name}  q={q:.3f}"))
    base_layout(fig, "redshift z", "Q (flux dimming / z, nearby = 1)", xlog=True, height=520)
    st.plotly_chart(fig, width="stretch")
    if rows:
        st.dataframe(pd.DataFrame(rows).style.format({"q": "{:.3f}", "c": "{:.3f}", "chi2": "{:.1f}", "rms_mag": "{:.3f}"}),
                     hide_index=True, width="stretch")
        st.caption("Each shape is written in redshift alone and equals 1 for nearby supernovae. χ² and RMS are measured on "
                   "the 40 Pantheon 2018 bins, in magnitudes, with the overall brightness level left free. These curves are "
                   "for comparison; the register is the black points.")


def page_time():
    st.title("Time dilation")
    st.markdown("Transients carry their own clocks. The measured exponent b in (observed width / rest width) = (1+z)^b "
                "gives the register Q_t = (1+z)^(b−1), which equals 1 at full stretch (b = 1).")
    view = st.sidebar.radio("Show", ["Exponent b", "Q_t(z) = (1+z)^(b−1)"])
    data = R.time_dilation()
    fig = go.Figure()
    if view == "Exponent b":
        for i, d in enumerate(data):
            if d["zmin"] is not None:
                fig.add_trace(go.Scatter(x=[(d["zmin"] + d["zmax"]) / 2], y=[d["b"]], mode="markers", name=d["study"],
                                         marker=dict(size=10, color=PALETTE[i]),
                                         error_y=dict(type="data", array=[d["err"]]),
                                         error_x=dict(type="data", array=[(d["zmax"] - d["zmin"]) / 2])))
            else:
                lo, hi = d.get("err_lo", d["err"]), d.get("err_hi", d["err"])
                fig.add_hrect(y0=d["b"] - lo, y1=d["b"] + hi, fillcolor=PALETTE[i], opacity=0.15, line_width=0,
                              annotation_text=d["study"], annotation_position="top left")
        ref_line(fig, 1.0, "b = 1, full (1+z) stretch")
        fig.add_hline(opacity=1, y=0, line=dict(color=BLACK, dash="dot"), annotation_text="b = 0, no stretch")
        base_layout(fig, "redshift z", "exponent b")
        fig.update_xaxes(range=[0, 1.4]); fig.update_yaxes(range=[-0.15, 1.7])
    else:
        zz = np.linspace(0, 4, 200)
        for i, d in enumerate(data):
            zr = zz[zz <= (d["zmax"] or 4)]
            lo, hi = d.get("err_lo", d["err"]), d.get("err_hi", d["err"])
            fig.add_trace(go.Scatter(x=zr, y=(1 + zr) ** (d["b"] - 1), mode="lines", line=dict(color=PALETTE[i], width=2), name=d["study"]))
            fig.add_trace(go.Scatter(x=np.r_[zr, zr[::-1]], y=np.r_[(1 + zr) ** (d["b"] + hi - 1), ((1 + zr) ** (d["b"] - lo - 1))[::-1]],
                                     fill="toself", fillcolor=PALETTE[i], opacity=0.15, line_width=0, showlegend=False))
        ref_line(fig, 1.0, "Q_t = 1")
        base_layout(fig, "redshift z", "Q_t")
    st.plotly_chart(fig, width="stretch")
    st.dataframe(pd.DataFrame(data)[["study", "b", "err", "zmin", "zmax", "n"]], hide_index=True, width="stretch")
    st.caption("Light-curve widths (a time ratio) read against redshift (a frequency ratio). Studies without a "
               "redshift range in the local data are drawn as bands.")


def page_ageing():
    st.title("Ageing rate")
    st.markdown("Passively ageing galaxies are clocks spread across redshift. Pairs of them give the change in redshift per "
                "change in stellar age, |dz/dt|. The register divides it by the local rate, so Q = 1 would mean a steady rate.")
    za = st.sidebar.slider("Chronometers below this redshift set the local rate", 0.1, 0.5, 0.2, 0.05)
    z, q, e, anc, anc_e = R.ageing(True, za)
    fig = go.Figure(errpts(z, q, e, "31 cosmic chronometers"))
    ref_line(fig, label="steady rate, Q = 1")
    base_layout(fig, "redshift z", "|dz/dt| / local rate")
    st.plotly_chart(fig, width="stretch")
    st.metric("Local rate |dz/dt|", f"{anc:.4f} ± {anc_e:.4f} per billion years")
    st.caption("Published chronometer values are quoted after a 1/(1+z) conversion that belongs to an expanding frame. "
               "That conversion is undone here, so the register is redshift change per stellar time. "
               "Stellar ages come from population models.")


def page_angle():
    st.title("Acoustic angle")
    st.markdown("Galaxies prefer a fixed separation, which shows in a thin redshift slice as a preferred angle between pairs. "
                "The register is Q = θ(z)·z / (θ(z_a)·z_a): with the ideal, an angle that shrinks as 1/z, Q stays at 1.")
    k = st.sidebar.selectbox("Anchor point", range(5), format_func=lambda i: f"z = {R.ANGLES['z'][i]}  ({R.ANGLES['source'][i]})")
    z, q, e = R.acoustic_angle(k)
    view = st.sidebar.radio("Show", ["Register Q", "Measured angle θ (degrees)"])
    if view.startswith("Register"):
        fig = go.Figure(errpts(z, q, e, "thin-shell angles", text=R.ANGLES["source"]))
        ref_line(fig, label="angle ∝ 1/z, Q = 1")
        base_layout(fig, "redshift z", "Q")
    else:
        th, et = R.ANGLES["theta"], R.ANGLES["err"]
        fig = go.Figure(errpts(z, th, et, "measured θ", text=R.ANGLES["source"]))
        zz = np.geomspace(0.08, 2.5, 100)
        fig.add_trace(go.Scatter(x=zz, y=th[k] * z[k] / zz, mode="lines", line=dict(color=REF, dash="dash"), name="θ ∝ 1/z"))
        base_layout(fig, "redshift z", "θ (degrees)", xlog=True, ylog=True)
    st.plotly_chart(fig, width="stretch")
    st.dataframe(pd.DataFrame(dict(z=z, theta_deg=R.ANGLES["theta"], err=R.ANGLES["err"], Q=q, dQ=e, source=R.ANGLES["source"])),
                 hide_index=True, width="stretch")
    st.caption("The five points come from different surveys and galaxy types.")


def page_cusp():
    st.title("Cusp flux ratio")
    st.markdown("When a lens splits one source into a tight triplet of images, a perfectly smooth lens would make the middle "
                "image as bright as the two outer ones together, in the limit of a closed triplet. The register is "
                "**Q = F_middle / (F_outer1 + F_outer2)**, from radio flux ratios.")
    fig = go.Figure()
    rows = []
    for i, (k, v) in enumerate(R.CUSP.items()):
        th = v[0]
        vals = np.array([R.cusp_q(a, b, c) for _, a, b, c in v[4]])
        fig.add_trace(go.Scatter(x=np.full(len(vals), th), y=vals, mode="markers", marker=dict(symbol="line-ew-open", size=18, color=PALETTE[i]),
                                 text=[r[0] for r in v[4]], name=f"{k}, each epoch", hovertemplate="%{text}<br>%{y:.3f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=[th], y=[np.median(vals)], mode="markers", marker=dict(size=12, color=PALETTE[i]),
                                 error_y=dict(type="data", array=[np.std(vals, ddof=1)]), name=f"{k}, median"))
        rows.append(dict(system=k, opening_angle_deg=th, median_Q=np.median(vals), spread=np.std(vals, ddof=1), epochs=len(vals)))
    ref_line(fig, 1.0, "smooth lens, closed triplet: Q = 1")
    base_layout(fig, "opening angle of the triplet (degrees)", "Q")
    fig.update_xaxes(range=[25, 90]); fig.update_yaxes(range=[0, 1.15])
    st.plotly_chart(fig, width="stretch")
    st.dataframe(pd.DataFrame(rows).style.format(precision=3), hide_index=True, width="stretch")
    st.caption("Dashes are single epochs and instruments. In all three lenses the middle image is fainter than the outer pair "
               "together. Radio fluxes are used because they are free of dust and microlensing.")


def page_rotation():
    st.title("Galaxy rotation")
    st.markdown("Q = g_obs / g_bar compares the rotation a galaxy shows with the rotation its visible matter alone would give. "
                "Q = 1 would mean visible matter accounts for all of it.")
    ud = st.sidebar.slider("Disk mass-to-light ratio", 0.2, 1.0, 0.5, 0.05)
    ub = st.sidebar.slider("Bulge mass-to-light ratio", 0.3, 1.2, 0.7, 0.05)
    inc = st.sidebar.slider("Minimum inclination (degrees)", 0, 60, 30, 5)
    qual = st.sidebar.select_slider("Maximum SPARC quality flag", [1, 2, 3], 2)
    xaxis = st.sidebar.radio("Read against", ["radius / disk scale length", "visible-matter acceleration g_bar"])
    q, gb, fd, names, ng, rr = rotation_data(ud, ub, inc, qual)
    fig = go.Figure()
    if xaxis.startswith("radius"):
        X, edges, xt = rr, np.logspace(-1, 1.3, 12), "radius / disk scale length"
    else:
        X, edges, xt = gb, np.logspace(-13, -8.5, 10), "visible-matter acceleration g_bar (m/s²)"
    fig.add_trace(go.Scattergl(x=X, y=q, mode="markers", marker=dict(size=3, color="#9AA5AB", opacity=0.5), name="each radius",
                               text=names, hovertemplate="%{text}<br>Q=%{y:.2f}<extra></extra>"))
    x, y, lo, hi = R.binned_median_x(X, q, edges)
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", line=dict(color=BLACK, width=2), name="median (16–84%)",
                             error_y=dict(type="data", symmetric=False, array=hi - y, arrayminus=y - lo)))
    ref_line(fig, label="visible matter alone, Q = 1")
    base_layout(fig, xt, "Q = g_obs / g_bar", xlog=True, ylog=True, height=560)
    st.plotly_chart(fig, width="stretch")
    c1, c2, c3 = st.columns(3)
    c1.metric("Galaxies shown", ng)
    c2.metric("Median Q inside 1 disk scale length", f"{np.nanmedian(q[rr < 1]):.2f}")
    c3.metric("Median Q beyond 5 disk scale lengths", f"{np.nanmedian(q[rr > 5]):.1f}")
    st.caption("Rotation speeds are Doppler shifts, which are frequency ratios, and radius over disk scale length is a ratio of "
               "two angles on the sky. The visible-matter side needs a mass-to-light ratio and a catalog distance, set in the sidebar "
               "and taken from SPARC.")


def page_single():
    st.title("Single-value registers")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Clock")
        st.latex(r"Q_\tau = \frac{(\Delta\nu/\nu)\,c^2}{g\,h}")
        st.metric("Measured", "Q_τ = 1", "Pound–Rebka–Snider (~1%), lattice clocks (parts in 10⁵)", delta_color="off")
        st.caption("Each test measures g on the spot. All of them sit at Earth's surface gravity, so this is one point for now.")
    with c2:
        st.subheader("Deflection")
        st.latex(r"Q_\lambda = \frac{\alpha_{obs}}{\alpha_{traj}} = 1 + \gamma")
        st.metric("Measured", "Q_λ = 2", "γ known to 2.3×10⁻⁵ (Cassini)", delta_color="off")
        st.caption("Light passing the Sun bends twice as much as a body moving at the same speed would.")


def page_light_matter():
    st.title("Light and matter together")
    st.markdown("""
Gravity shows in two kinds of register. A **matter register** reads how a body moves: the Doppler swing of its orbit, the
turn of the orbit, the shrinking of its period. A **light register** reads what happens to light and clocks: a steady
redshift, a clock running slow, a delay as light passes a mass. These systems give both registers for **the same object**,
using only frequency ratios, times and angles. If gravity were a gap between the two, they would disagree here.
They do not. **They move away from the ideal together, in a fixed proportion: the light shift is the square of the
matter swing.** One cause sets both.
""")
    rows = R.light_matter_table()
    df = pd.DataFrame(rows)
    fig = go.Figure()
    for i, r in df.iterrows():
        fig.add_trace(go.Scatter(x=[r.Q], y=[r.system], mode="markers", name=r.system, showlegend=False,
                                 marker=dict(size=10, color=PALETTE[i % len(PALETTE)]),
                                 error_x=dict(type="data", array=[r.err], visible=True, thickness=1.5),
                                 hovertemplate=f"{r.system}<br>Q = {r.Q:.5g} ± {r.err:.2g}<extra></extra>"))
    fig.add_vline(opacity=1, x=1.0, line=dict(color=REF, dash="dash", width=1.5), annotation_text="ideal, Q = 1",
                  annotation_position="top")
    base_layout(fig, "Q (light register against matter register)", "", height=420)
    fig.update_yaxes(type="category", autorange="reversed")
    st.plotly_chart(fig, width="stretch")

    st.header("1. S2 at the centre of the Galaxy")
    grav, side = R.s2_predicted_shift()
    c1, c2, c3 = st.columns(3)
    c1.metric("Orbital swing at closest approach", f"{R.S2_ORBIT['v_peri_kms']:.0f} km/s", "Doppler shift plus the track on the sky", delta_color="off")
    c2.metric("Extra redshift predicted from the swing²", f"{grav + side:.0f} km/s",
              f"{grav:.0f} gravitational + {side:.0f} from sideways motion", delta_color="off")
    c3.metric("Measured / predicted (latest)", f"{R.S2_REDSHIFT[-1][1]:.2f} ± {df.err.iloc[2]:.2f}", "Q = 1 is the ideal", delta_color="off")
    st.caption("The prediction needs only the swing, the orbit's shape and its tilt on the sky: frequencies and angles. "
               "The published fits also solve for the distance to the Galactic centre and the central mass at the same time, "
               "so the quoted errors carry that fit with them.")

    st.header("2. Binary pulsars: time only")
    ht = R.hulse_taylor_register()
    st.markdown("A pulsar is a clock in orbit. Its arrival times give three separate things: how fast the orbit **turns** "
                "(matter), how much the clock **slows and speeds** around the orbit (light), and how fast the orbit "
                "**shrinks**. The first two fix the system; the third is then a free check.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Shrink: measured / predicted, raw", f"{ht['raw'][0]:.4f} ± {ht['raw'][1]:.4f}", "arrival times only", delta_color="off")
    c2.metric("After removing the Galaxy's pull", f"{ht['gal'][0]:.4f} ± {ht['gal'][1]:.4f}", "this step needs a distance", delta_color="off")
    c3.metric("Double pulsar: light delay / predicted", f"{R.DOUBLE_PULSAR_S[0]:.5f} ± {R.DOUBLE_PULSAR_S[1]:.5f}", "Kramer et al. 2006", delta_color="off")
    st.markdown(f"""
The raw Hulse–Taylor register sits **{(ht['raw'][0] - 1) * 100:.2f}%** above the ideal, about
{(ht['raw'][0] - 1) / ht['raw'][1]:.0f} times its error. That offset is not in the pulsar's gravity. It is the pulsar and the
Sun being pulled differently by the Galaxy, plus the pulsar's sideways drift. Removing it needs a distance (a calculation),
and once removed Q sits at 1. So the measurement-only register sees exactly what the *No fixed point* page says it
should: the part that disagrees is relative motion.
""")
    st.caption("Masses come out as times (the Sun's mass is 4.93 µs in these units) and cancel in every ratio. "
               f"From the turn and the clock term: {ht['m1']:.3f} and {ht['m2']:.3f} solar masses. The only π is 2π per orbit, "
               "which turns one orbit into radians: a unit, not a limit.")

    st.header("What this says about a mechanism")
    st.markdown("""
- The light and matter registers are **not independent** in any system where both are read. Their ratio sits at Q = 1 to
  7% (S2), 0.2% (Hulse–Taylor) and 0.05% (double pulsar).
- So gravity is not the **difference** between them. It is one departure from the ideal that shows up in both, with the
  light register as the square of the matter one.
- A mechanism has to produce both from one cause. The clock rate (the light register) is the natural candidate, with the
  motion of matter following from how the clock rate changes from place to place.
""")
    st.dataframe(df.style.format({"Q": "{:.5f}", "err": "{:.5f}"}), hide_index=True, width="stretch")


def page_gravity():
    st.title("Gravity: departure from G")
    st.markdown("""
FDG uses ideals for comparison, not constants. Here the ideal is **one G everywhere**: the pull a system shows equals
the pull its own matter gives with the G measured in the lab. The register is **Q_G = pull shown ÷ pull from its own
matter**, so Q_G = 1 means the one-G ideal holds there. Systems are read against the pull of their matter, from
neutron-star binaries down to the thin outer edges of galaxies.
""")
    ud = st.sidebar.slider("Disk mass-to-light ratio (galaxies)", 0.2, 1.0, 0.5, 0.05)
    ub = st.sidebar.slider("Bulge mass-to-light ratio (galaxies)", 0.3, 1.2, 0.7, 0.05)
    q, gb, names, ng = R.gravity_galaxies(ud, ub)
    x, y, lo, hi, rd = R.gravity_readings(gb, q)
    comp = R.gravity_compact()

    fig = go.Figure()
    fig.add_trace(go.Scattergl(x=gb, y=q, mode="markers", marker=dict(size=3, color="#9AA5AB", opacity=0.45),
                               name=f"galaxies, each radius ({ng} galaxies)", text=names,
                               hovertemplate="%{text}<br>pull from matter %{x:.2e} m/s²<br>Q_G=%{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", line=dict(color=BLACK, width=2.5), name="galaxies, median (16–84%)",
                             error_y=dict(type="data", symmetric=False, array=hi - y, arrayminus=y - lo)))
    groups = {}
    for name, g, qq, e, grp in comp:
        groups.setdefault(grp, []).append((name, g, qq, e))
    symbols = {"Solar System": "circle", "Binary pulsars": "diamond", "Galactic centre": "star"}
    for i, (grp, rows) in enumerate(groups.items()):
        fig.add_trace(go.Scatter(x=[r[1] for r in rows], y=[r[2] for r in rows], mode="markers", name=grp,
                                 marker=dict(size=12, color=PALETTE[i], symbol=symbols.get(grp, "circle"), line=dict(color="white", width=1)),
                                 error_y=dict(type="data", array=[r[3] for r in rows], visible=True), text=[r[0] for r in rows],
                                 hovertemplate="%{text}<br>pull %{x:.2e} m/s²<br>Q_G=%{y:.5f}<extra></extra>"))
    # on log axes, annotations are placed in log10 units
    fig.add_hline(opacity=1, y=1.0, line=dict(color=REF, dash="dash", width=1.5))
    fig.add_annotation(text="one G everywhere, Q_G = 1", xref="paper", x=1, xanchor="right", y=0, yanchor="bottom",
                       showarrow=False, font=dict(color=REF, size=12))
    for k, (level, dash) in enumerate(((1.5, "dot"), (2.0, "dash"))):
        if level in rd:
            fig.add_vline(opacity=1, x=rd[level], line=dict(color=brand.RUST, dash=dash, width=1.2))
            fig.add_annotation(text=f"Q_G = {level:g}", x=np.log10(rd[level]), xanchor="left", yref="paper", y=1 - 0.05 * k,
                               showarrow=False, font=dict(color=brand.RUST, size=12))
    base_layout(fig, "pull from the system's own matter (m/s²)", "Q_G = pull shown ÷ pull from its own matter",
                xlog=True, ylog=True, height=600)
    fig.update_xaxes(range=[-12.7, 3.2])
    fig.update_yaxes(range=[np.log10(0.6), np.log10(25)])
    st.plotly_chart(fig, width="stretch")

    st.subheader("Readings")
    c1, c2, c3 = st.columns(3)
    c1.metric("Q_G reaches 1.5 at a pull of", f"{rd.get(1.5, float('nan')):.1e} m/s²", "a reading, not an input", delta_color="off")
    c2.metric("Q_G reaches 2 at a pull of", f"{rd.get(2.0, float('nan')):.1e} m/s²", "a reading, not an input", delta_color="off")
    c3.metric("Slope in the thinnest matter", f"{rd['slope']:.2f}", "log Q_G per log pull, below 10⁻¹¹ m/s²", delta_color="off")
    st.markdown(f"""
- From neutron-star binaries to the outer Solar System, about **eleven decades of pull**, Q_G stays at 1 to between
  1 part in 1,000 and 1 part in 100,000.
- In galaxies Q_G stays near 1 while the matter is dense, then leaves 1 as the matter thins. It reaches 2 at a
  pull of about {rd.get(2.0, float('nan')):.0e} m/s² and keeps rising. Where it leaves 1 is a reading of this register, the
  same kind of reading as the exponent in the redshift registers.
- Gravity is therefore not one fixed G at every scale. It holds the ideal where matter is concentrated and departs
  from it where matter is thin.
""")
    st.dataframe(pd.DataFrame([dict(system=n, pull_m_s2=g, Q_G=qq, error=e, group=grp) for n, g, qq, e, grp in comp])
                 .style.format({"pull_m_s2": "{:.2e}", "Q_G": "{:.5f}", "error": "{:.1e}"}), hide_index=True, width="stretch")
    st.caption("Compact systems: each Q is the published ratio of a measured effect to its one-G prediction, with the mass "
               "taken from the same system's orbits. Their pulls use radar distances in the Solar System and orbit sizes "
               "from timing; S2's uses the distance to the Galactic centre. Galaxies: rotation is a Doppler shift, and the pull "
               "from visible matter comes from light and gas with the mass-to-light ratios set in the sidebar. The catalog "
               "distance cancels out of that pull but still scales Q_G, so the galaxy points carry the catalog distance and the "
               "mass-to-light ratio as their calculated parts. The ideal itself is uncertain: lab measurements of G disagree "
               "by several parts in 10,000.")


def page_mass():
    st.title("Mass: a reading, not a measurement")
    st.markdown("""
No instrument reads a mass. What is measured is always an **angle**, a **time**, a **frequency shift** or a **flux**.
A mass comes from multiplying that measured part by **assumed parts**: a distance, an ideal shape (a perfect ellipse,
a perfect circle, a disk seen at a tilt), a steady state, and a calibration borrowed from other objects. This page keeps
the two apart. Every slider is an assumption; the measured part never moves.

Even for the Sun the reading is **G·M**, known to about ten digits from the planets' orbits. Turning it into kilograms
needs G, and lab measurements of G disagree by several parts in 10,000. So every mass below is given as a **ratio to
the Sun's G·M**, which cancels G. Each one is then a comparison, not a constant.
""")
    budget = R.mass_budget()
    st.header("How much of each mass is measured")
    fig = go.Figure()
    colors = {"measured": "#2E7D6B", "assumed": brand.RUST, "changes": "#7A5195"}
    labels = [f"{o} · {what}" for o, what, _ in budget]
    for kind, col in colors.items():
        sel = [(lab, (f - 1) * 100) for (o, what, f), lab in zip(budget, labels) if what.startswith(kind)]
        if sel:
            fig.add_trace(go.Bar(x=[v for _, v in sel], y=[l for l, _ in sel], orientation="h", name=kind, marker_color=col,
                                 hovertemplate="%{y}<br>± %{x:.3g}%<extra></extra>"))
    base_layout(fig, "spread it puts on the mass (± %, log scale)", "", xlog=True, height=560)
    fig.update_xaxes(tickvals=[1e-8, 1e-6, 1e-4, 1e-2, 1, 100],
                     ticktext=["0.00000001%", "0.000001%", "0.0001%", "0.01%", "1%", "100%"])
    fig.update_yaxes(type="category", categoryorder="array", categoryarray=labels[::-1])
    fig.update_layout(barmode="overlay")
    st.plotly_chart(fig, width="stretch")
    st.caption("Measured: the published error on the angles, times and Doppler shifts. Assumed: half the range between the "
               "lowest and highest values in use (distances from different teams, shape factors, calibrations, lab G). "
               "Changes: the same measurement repeated in different years.")
    st.markdown("""
- The **measured part is the small part** everywhere except the Sun. For Sgr A* the angles and period are good to 0.1%;
  the distance, which goes in cubed, adds six times more.
- For M87* and quasars the biggest spread is **which recipe** or **which calibration** is chosen, not the data.
- In NGC 5548 the measurement itself **changes**: the lag is different every year, so a single mass is an average over
  a system that never holds still.
""")

    st.header("How much of the motion has been watched")
    cyc = R.cycles_seen()
    fig = go.Figure(go.Bar(x=[c[1] for c in cyc], y=[c[0] for c in cyc], orientation="h", marker_color=BLACK,
                           hovertemplate="%{y}<br>%{x:.2g} of one orbit<extra></extra>"))
    fig.add_vline(opacity=1, x=1.0, line=dict(color=REF, dash="dash", width=1.5), annotation_text="one full orbit",
                  annotation_position="top")
    base_layout(fig, "fraction of one full orbit watched (log scale)", "", xlog=True, height=360)
    fig.update_yaxes(type="category", autorange="reversed")
    st.plotly_chart(fig, width="stretch")
    st.caption("A mass from orbits assumes the orbit closes and repeats. Only around the Sun and Sgr A* has a whole orbit "
               "been seen. For a galaxy's outer disk we have watched about one twenty-millionth of a turn: the rotation is "
               "a snapshot, and steady circular motion is an assumption. The orbit times here are themselves calculations "
               "from the same assumed masses and distances, so treat them as rough.")

    st.header("1. Sgr A*: angles and a period")
    th3p2, e = R.sgr_a_measured_part()
    d = st.slider("Assumed distance to the Galactic centre (pc)", 7800, 8400, 8178, 1)
    c1, c2, c3 = st.columns(3)
    c1.metric("Measured: angle³ / period² (arcsec³/yr²)", f"{th3p2:.4e}", f"± {e * 100:.2f}%", delta_color="off")
    c2.metric("Assumed: distance³ (pc³)", f"{d ** 3:.3e}", "AU per arcsec is the distance in pc", delta_color="off")
    c3.metric("Reading (million Suns)", f"{R.mass_sgr_a(d) / 1e6:.3f}", "G cancels in Sun units", delta_color="off")
    ds = np.linspace(7800, 8400, 61)
    fig = go.Figure(go.Scatter(x=ds, y=R.mass_sgr_a(ds) / 1e6, mode="lines", line=dict(color=BLACK, width=2),
                               name="same angles and period, any distance"))
    fig.add_trace(go.Scatter(x=[x for _, x in R.GC_DISTANCES], y=[R.mass_sgr_a(x) / 1e6 for _, x in R.GC_DISTANCES],
                             mode="markers+text", text=[n for n, _ in R.GC_DISTANCES], textposition="top left",
                             marker=dict(size=10, color=brand.RUST), name="distances in use"))
    base_layout(fig, "assumed distance (pc)", "mass (million Suns)", height=400)
    st.plotly_chart(fig, width="stretch")
    st.caption("The angle and period come from GRAVITY (2020). Teams fit the distance from the same orbit by matching the "
               "Doppler speed (km/s) to the motion across the sky (mas/yr), which assumes the orbit is a perfect closed "
               "ellipse around a point. The mass goes as the cube of that distance.")

    st.header("2. M87*: one ring angle")
    c1, c2 = st.columns(2)
    alpha = c1.slider("Assumed ring-to-mass shape factor", 9.5, 12.5, 11.0, 0.1,
                      help="Ring diameter in units of GM/(D c²). A perfect circular shadow of a non-spinning hole gives 10.39.")
    dm = c2.slider("Assumed distance to M87 (Mpc)", 15.0, 18.5, 16.8, 0.1)
    rows = []
    for name, ring, er in R.M87_RING:
        rows.append(dict(reading=f"{name}: {ring:.1f} ± {er:.1f} µas", mass_billion=R.mass_m87(ring, alpha, dm) / 1e9))
    c1, c2, c3 = st.columns(3)
    c1.metric("Measured: ring diameter (2017)", "42 ± 3 µas", "2018: 43.3 µas, bright side turned ~30°", delta_color="off")
    c2.metric("Reading with your assumptions (billion Suns)", f"{rows[0]['mass_billion']:.2f}", delta_color="off")
    c3.metric("With the ideal circle, 10.39 (billion Suns)", f"{R.mass_m87(42.0, R.M87_ALPHA_IDEAL, dm) / 1e9:.2f}",
              "the ideal is a comparison, not the answer", delta_color="off")
    fig = go.Figure()
    for i, (name, m, up, dn) in enumerate(R.M87_OTHER):
        fig.add_trace(go.Scatter(x=[m / 1e9], y=[name], mode="markers", marker=dict(size=11, color=PALETTE[i]), showlegend=False,
                                 error_x=dict(type="data", symmetric=False, array=[up / 1e9], arrayminus=[dn / 1e9])))
    fig.add_vline(opacity=1, x=rows[0]["mass_billion"], line=dict(color=BLACK, dash="dot"), annotation_text="your reading",
                  annotation_position="top")
    base_layout(fig, "mass (billion Suns, at 16.8 Mpc)", "", height=320)
    fig.update_yaxes(type="category")
    st.plotly_chart(fig, width="stretch")
    st.caption("Same object, three recipes. Gas motions and star motions disagree by nearly a factor of two, each with "
               "its own model of how the gas or stars move. The ring itself changed between 2017 and 2018.")

    st.header("3. NGC 5548: a delay and a line width")
    c1, c2 = st.columns(2)
    lag = c1.slider("Lag in the year you pick (days)", float(R.NGC5548_LAG_D[0]), float(R.NGC5548_LAG_D[1]), 15.0, 0.1)
    f = c2.select_slider("Assumed virial factor f", [v for _, v in R.VIRIAL_F], value=6.3,
                         format_func=lambda v: f"{v} ({dict((b, a) for a, b in R.VIRIAL_F)[v]})")
    m = R.mass_reverb(lag, R.NGC5548_WIDTH, f)
    c1, c2, c3 = st.columns(3)
    c1.metric("Measured: lag", f"{lag:.1f} days", f"has ranged {R.NGC5548_LAG_D[0]}–{R.NGC5548_LAG_D[1]} days", delta_color="off")
    c2.metric("Measured: line width", f"{R.NGC5548_WIDTH:.0f} km/s", "Doppler spread, round value", delta_color="off")
    c3.metric("Reading (10⁷ Suns)", f"{m / 1e7:.1f}", "lag × width² × f", delta_color="off")
    lags = np.linspace(R.NGC5548_LAG_D[0], R.NGC5548_LAG_D[1], 50)
    fig = go.Figure()
    for i, (name, fv) in enumerate(R.VIRIAL_F):
        fig.add_trace(go.Scatter(x=lags, y=R.mass_reverb(lags, R.NGC5548_WIDTH, fv) / 1e7, mode="lines",
                                 line=dict(color=PALETTE[i], width=2), name=f"f = {fv} ({name})"))
    fig.add_hrect(y0=(R.NGC5548_MEAN_MASS[0] - R.NGC5548_MEAN_MASS[1]) / 1e7, y1=(R.NGC5548_MEAN_MASS[0] + R.NGC5548_MEAN_MASS[1]) / 1e7,
                  fillcolor="#9AA5AB", opacity=0.3, line_width=0, annotation_text="published mean over years (f = 6.3)",
                  annotation_position="top left")
    base_layout(fig, "lag (days)", "mass (10⁷ Suns)", height=420)
    st.plotly_chart(fig, width="stretch")
    st.caption("Lags across campaigns from Lu et al. (2016, Table 4). When the lag grows the line narrows, which is why the "
               "published mean holds steady: that steadiness is the virial assumption at work. f is never measured in NGC 5548; "
               "it is borrowed from galaxies where a different mass recipe was used.")

    st.header("4. A disk galaxy: a Doppler swing and an outline")
    gal, _ = R.sparc_tables()
    names = sorted(n for n, g in gal.items() if g["Q"] == 1 and g["inc"] >= 30)
    name = st.selectbox("Galaxy (SPARC, quality 1)", names, index=names.index("NGC3198"))
    gx = R.sparc_galaxy(name)
    c1, c2, c3 = st.columns(3)
    inc = c1.slider("Assumed tilt (degrees)", 30.0, 89.0, float(gx["inc"]), 0.5,
                    help=f"Catalog: {gx['inc']:.0f} ± {gx['eInc']:.0f}°, from the outline read as a perfect circle seen at a tilt.")
    dd = c2.slider("Assumed distance (Mpc)", max(0.5, gx["D"] * 0.6), gx["D"] * 1.4, float(gx["D"]), 0.1,
                   help=f"Catalog: {gx['D']} ± {gx['eD']} Mpc")
    ml = c3.slider("Assumed mass-to-light ratio (visible mass)", 0.2, 1.0, 0.5, 0.05)
    gm = R.galaxy_mass(gx, inc, dd, ml)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Measured: line-of-sight swing", f"{gm['vlos']:.0f} km/s", "at the last measured radius", delta_color="off")
    c2.metric("Mass from motion (Suns)", f"{gm['motion']:.2e}", f"v = {gm['v']:.0f} km/s, R = {gm['R_kpc']:.1f} kpc", delta_color="off")
    c3.metric("Mass from light and gas (Suns)", f"{gm['visible']:.2e}", "goes as distance²", delta_color="off")
    c4.metric("Motion ÷ visible", f"{gm['motion'] / gm['visible']:.1f}", "goes as 1 / distance", delta_color="off")
    incs = np.linspace(max(30, gx["inc"] - 20), min(89, gx["inc"] + 15), 60)
    ms = [R.galaxy_mass(gx, i, dd, ml)["motion"] for i in incs]
    fig = go.Figure(go.Scatter(x=incs, y=ms, mode="lines",
                               line=dict(color=BLACK, width=2), name="mass from motion"))
    fig.add_vrect(x0=gx["inc"] - gx["eInc"], x1=gx["inc"] + gx["eInc"], fillcolor="#9AA5AB", opacity=0.3, line_width=0,
                  annotation_text="catalog tilt ± error", annotation_position="top left")
    fig.add_trace(go.Scatter(x=[incs[0], incs[-1]], y=[gm["visible"]] * 2, mode="lines", line=dict(color=brand.RUST, dash="dash", width=2),
                             name="mass from light and gas (does not depend on tilt)"))
    base_layout(fig, "assumed tilt (degrees)", "mass inside the last radius (Suns)", ylog=True, height=420)
    fig.update_yaxes(range=[np.log10(min(min(ms), gm["visible"]) * 0.7), np.log10(max(max(ms), gm["visible"]) * 1.4)])
    st.plotly_chart(fig, width="stretch")
    st.caption("Only the Doppler shift along the line of sight is measured. Rotation speed = swing ÷ sin(tilt), so the "
               "tilt matters most for galaxies seen nearly face-on. Real disks are oval, warped and lopsided, so the "
               "circle-seen-at-a-tilt is an ideal. The 'missing mass' ratio in the last metric changes with the assumed "
               "distance and mass-to-light ratio, and the visible mass uses 1.33 × the hydrogen mass for gas.")

    st.header("What this says")
    st.markdown("""
- A mass is a **reading assembled from measured ratios and chosen ideals**. The measured part is usually the small part
  of the spread.
- In solar units G cancels, so masses are **comparisons with the Sun**, not values against a constant.
- The closer the object, and the more of its motion we have watched, the more the reading rests on measurement.
  Sgr A* is the best case and still carries a distance cubed. A galaxy's mass rests on a snapshot of less than one
  millionth of a turn, a tilt read from an ideal circle, and a distance.
""")


def page_motion():
    st.title("No fixed point: relative motion")
    st.markdown("""
In plate tectonics every measurement is one plate moving against another. Absolute plate speeds only appear once a
reference frame is chosen, such as the hotspots or a no-net-rotation frame, and even the hotspots drift. Beyond our Galaxy
the sky is in the same position. What arrives at a detector is a **frequency ratio** (redshift), an **angle**, and **an
angle per unit time**. Every speed and distance out there comes from one of those plus a chosen frame or a chosen distance.
Expansion is that kind of choice, made for the whole universe at once: it turns redshift into speed and distance.
""")

    st.header("1. Andromeda: what is measured, and what is calculated")
    mu, mu_e = R.m31_pm_total()
    c1, c2, c3 = st.columns(3)
    c1.metric("Redshift (measured)", f"z = {R.M31['v_helio'] / R.C_KMS:.5f}",
              f"closing at {-R.M31['v_helio']:.0f} ± {R.M31['v_helio_e']:.0f} km/s along the line of sight", delta_color="off")
    c2.metric("Sideways drift (measured)", f"{mu:.0f} ± {mu_e:.0f} µas/yr",
              "an angle per year", delta_color="off")
    c3.metric("Distance (calculated)", f"{min(d for _, d, _ in R.M31_DISTANCES)}–{max(d for _, d, _ in R.M31_DISTANCES)} kpc",
              "from the Cepheid / TRGB / eclipsing-binary ladder", delta_color="off")
    st.markdown("The line-of-sight closing speed between the Sun and Andromeda is a Doppler measurement. A sideways speed "
                "needs a distance, so **the answer to “is it a head-on collision?” is set by the distance chosen.**")

    d_pick = st.sidebar.slider("Assumed distance to Andromeda (kpc)", 500, 1000, 770, 10)
    v_c = st.sidebar.slider("Assumed rotation speed of the Galaxy at the Sun (km/s)", 200, 260, 235, 5)

    c1, c2 = st.columns(2)
    with c1:
        d = np.linspace(500, 1000, 101)
        vt, vt_e = R.m31_transverse(d)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=np.r_[d, d[::-1]], y=np.r_[vt + vt_e, (vt - vt_e)[::-1]], fill="toself",
                                 fillcolor="rgba(180,83,42,0.15)", line=dict(width=0), name="proper-motion error", hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=d, y=vt, mode="lines", line=dict(color=brand.RUST, width=2.5), name="sideways speed = 4.74 µ d"))
        for i, (n, dv, de) in enumerate(R.M31_DISTANCES):
            v, _ = R.m31_transverse(dv)
            fig.add_trace(go.Scatter(x=[dv], y=[v], mode="markers", marker=dict(size=10, color=PALETTE[(i + 1) % 6]),
                                     error_x=dict(type="data", array=[de]), name=n))
        fig.add_hline(opacity=1, y=-R.M31["v_helio"], line=dict(color=REF, dash="dash", width=1.5),
                      annotation_text="measured line-of-sight closing speed", annotation_position="top left")
        base_layout(fig, "assumed distance (kpc)", "sideways speed relative to the Sun (km/s)", height=430)
        fig.update_yaxes(range=[0, 360])
        fig.update_layout(legend=dict(orientation="h", y=-0.3, font=dict(size=11)))
        st.plotly_chart(fig, width="stretch")
        v_pick, v_pick_e = R.m31_transverse(d_pick)
        st.caption(f"At your assumed {d_pick} kpc the drift becomes {float(v_pick):.0f} ± {float(v_pick_e):.0f} km/s sideways. "
                   "Speed is in direct proportion to the distance chosen: double the distance and you double the speed. Each published distance "
                   "puts Andromeda at a different point on this line.")
    with c2:
        vc = np.linspace(200, 260, 61)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=vc, y=-R.m31_galactocentric_radial(vc), mode="lines", line=dict(color=BLACK, width=2.5),
                                 name="closing speed seen from the Galaxy's centre"))
        fig.add_hline(opacity=1, y=-R.M31["v_helio"], line=dict(color=REF, dash="dash", width=1.5),
                      annotation_text="measured from the Sun: 300 km/s", annotation_position="bottom left")
        fig.add_trace(go.Scatter(x=[v_c], y=[-float(R.m31_galactocentric_radial(v_c))], mode="markers",
                                 marker=dict(size=12, color=brand.RUST), name="your assumed rotation speed"))
        base_layout(fig, "assumed rotation speed of the Galaxy at the Sun (km/s)", "closing speed (km/s)", height=430)
        fig.update_yaxes(range=[0, 330])
        fig.update_layout(legend=dict(orientation="h", y=-0.3, font=dict(size=11)))
        st.plotly_chart(fig, width="stretch")
        st.caption(f"The often-quoted ~110 km/s is the 300 km/s Doppler speed minus the Sun's own orbital speed, "
                   f"which comes from a Galaxy model. At {v_c} km/s the closing speed is {-float(R.m31_galactocentric_radial(v_c)):.0f} km/s. "
                   "Changing the frame changes the speed by almost a factor of three.")

    st.header("2. Looming: time to contact from angles")
    st.markdown("An object coming toward you grows on the sky. Its angular size divided by its rate of growth is the **time "
                "to contact**, τ = θ / (dθ/dt). Flies and drivers use the same quantity. Multiply τ "
                "by the measured closing speed and you get a distance.")
    tau, rel, rate1 = R.looming(d_pick)
    _, _, rate_full = R.looming(d_pick, R.M31["theta_deg"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Time to contact this implies", f"{float(tau):.2f} billion years", f"at your assumed {d_pick} kpc", delta_color="off")
    c2.metric("Growth of Andromeda's full width", f"{float(rate_full):.1f} µas/yr", f"{R.M31['theta_deg']}° across", delta_color="off")
    c3.metric("Growth of a 1° separation", f"{float(rate1):.1f} µas/yr", "e.g. between two of its star clusters", delta_color="off")
    st.markdown(f"Gaia measures Andromeda's whole sideways drift to about ±{mu_e:.0f} µas/yr. The looming signal is a few µas/yr, "
                "below that today. Precision grows with the time baseline, so more years of Gaia data will bring it within reach.")

    st.header("3. The sky's \"hotspot\": two rest frames that disagree")
    dr = R.dipole_register()
    st.markdown(f"""
The microwave sky is **{R.CMB_DIPOLE['dT_mK']:.3f} mK** warmer in one direction, a fraction **{dr['beta']:.2e}** of its
{R.CMB_DIPOLE['T0_K']} K temperature. That is measured. Reading all of it as our motion gives **{dr['v_kms']:.0f} km/s**. If that reading is right, distant quasars should bunch toward the same direction by a
predicted amount. They point **{dr['offset_deg']:.0f}°** away, and bunch too strongly.
""")
    c1, c2 = st.columns([3, 2])
    with c1:
        pts = [("CMB dipole (measured direction)", R.CMB_DIPOLE["l"], R.CMB_DIPOLE["b"], brand.RUST, "circle"),
               ("Quasar-count dipole (CatWISE)", R.QUASAR_DIPOLE["l"], R.QUASAR_DIPOLE["b"], PALETTE[1], "diamond"),
               ("Andromeda", R.M31["l"], R.M31["b"], PALETTE[2], "star")]
        fig = go.Figure()
        for n, l, b, col, sym in pts:
            fig.add_trace(go.Scattergeo(lon=[-(l if l <= 180 else l - 360)], lat=[b], mode="markers+text", text=[n.split(" (")[0]],
                                        textposition="top center", marker=dict(size=13, color=col, symbol=sym), name=n))
        edge = np.linspace(-90, 90, 91)
        fig.add_trace(go.Scattergeo(lon=np.r_[np.full(91, 179.9), np.full(91, -179.9)], lat=np.r_[edge, edge[::-1]], mode="lines",
                                    line=dict(color=REF, width=1), hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scattergeo(lon=np.linspace(-180, 180, 181), lat=np.zeros(181), mode="lines",
                                    line=dict(color=REF, width=1, dash="dot"), name="plane of the Galaxy", hoverinfo="skip"))
        fig.update_geos(projection_type="mollweide", showland=False, showcoastlines=False, showframe=False,
                        lataxis=dict(showgrid=True, gridcolor="#E3E6E5", dtick=30, range=[-90, 90]), lonaxis=dict(showgrid=True, gridcolor="#E3E6E5", dtick=60, range=[-180, 180]),
                        bgcolor="rgba(0,0,0,0)")
        fig.update_layout(title_text="", height=380, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.05))
        st.plotly_chart(fig, width="stretch")
        st.caption("Whole sky in Galactic coordinates, drawn the way astronomers do: the Galaxy's centre in the middle, "
                   "its disk along the equator, longitude increasing to the left.")
    with c2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0], y=[dr["Q"]], mode="markers", marker=dict(size=14, color=BLACK),
                                 error_y=dict(type="data", array=[dr["Q_e"]], thickness=1.5, width=10), name="measured"))
        ref_line(fig, 1.0, "one shared rest frame, Q = 1")
        base_layout(fig, "quasar dipole ÷ CMB prediction", "Q", height=380)
        fig.update_xaxes(range=[-1, 1], showticklabels=False, showgrid=False)
        fig.update_yaxes(range=[0, 3])
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")
    st.markdown(f"**Q = {dr['Q']:.2f} ± {dr['Q_e']:.2f}.** The quasars bunch about twice as strongly as the CMB speed predicts, "
                f"about {R.QUASAR_DIPOLE['sigma']}σ from a shared frame. Like hotspots that turn out to drift against each other, "
                "the two best candidates for a fixed frame do not agree.")
    st.caption("CMB dipole: Planck 2018. Quasar dipole: Secrest et al. 2021 (CatWISE2020). The ± on Q is backed out from their "
               "quoted significance. The quasar frame is also used, through VLBI and Gaia, to fix directions on the sky: it pins "
               "orientation but carries no speed or position.")

    st.header("4. The same move, made for the whole universe")
    st.dataframe(pd.DataFrame([
        ["Andromeda's line-of-sight speed", "redshift (frequency ratio)", "nothing: local Doppler", "—"],
        ["Andromeda's sideways speed", "angle per year", "a distance", "the distance ladder"],
        ["Andromeda's speed toward the Galaxy", "redshift", "the Sun's orbit", "a Galaxy rotation model"],
        ["Our speed through the universe", "CMB temperature dipole", "that the dipole is all motion", "a CMB rest frame (quasars disagree)"],
        ["Distance and speed of far galaxies", "redshift", "that redshift is recession", "expansion"],
    ], columns=["Quantity", "What is measured", "What has to be added", "Assumption"]), hide_index=True, width="stretch")
    st.caption("The registers are built from the left-hand column: redshift, angle, flux and time ratios.")


def page_bubbles():
    st.title("Bubbles and belts")
    st.markdown("""
Anything that blows out a wind blows a bubble, but only where the wind runs into something. The edge sits where the
wind's push, which thins as it spreads, falls to the push from outside. That balance is the **ideal**: a closed, round
edge at one distance. The register is **Q = measured edge distance ÷ balance distance**. Every measured edge here was
crossed by a spacecraft, so the distances are measured inside the Solar System, not calculated from afar. The second half
reads the asteroid and Kuiper belts as timing: orbital periods compared with whole-number fractions of a planet's period.
""")
    st.sidebar.markdown("**The wind (measured near Earth)**")
    p1 = st.sidebar.slider("Solar wind push at Earth's distance (nPa)", 0.5, 5.0, 2.0, 0.1,
                           help="Spacecraft upstream of Earth measure 1 to 3 nPa on most days; storms reach 10 or more.")
    st.sidebar.markdown("**Assumed parts**")
    f = st.sidebar.slider("Field pile-up at a magnetic edge (factor)", 1.5, 2.5, 2.0, 0.05,
                          help="A planet's field is compressed against the wind. 2 is the textbook flat-wall value; 2.44 allows for a curved edge.")
    st.sidebar.markdown("**Interstellar gas (measured by Voyager and IBEX)**")
    b_out = st.sidebar.slider("Outside magnetic field (nT)", 0.2, 0.8, 0.5, 0.05)
    n_out = st.sidebar.slider("Outside ion density (per cm³)", 0.04, 0.2, 0.10, 0.01)
    v_out = st.sidebar.slider("Oncoming flow speed (km/s)", 15.0, 35.0, 25.4, 0.1)
    t_out = st.sidebar.slider("Outside temperature (K)", 5000, 10000, 7500, 250)

    # ---------------- 1. one wind, many edges
    st.header("1. One wind, many edges")
    mp = R.magnetopause_register(p1, f)
    po = R.outside_pressure(b_out, n_out, t_out, v_out)
    r_h = R.heliosphere_ideal(p1, po["total"])
    hel = [dict(body=f"{who.replace('Voyager ', 'V')} {'shock' if edge.startswith('term') else 'heliopause'} ({side[0].upper()})", ideal=r_h, measured=d, Q=d / r_h, year=yr) for who, edge, d, yr, side in R.VOYAGER]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r["body"] for r in mp], y=[r["Q"] for r in mp], mode="markers", name="planet magnetic bubbles",
                             marker=dict(size=13, color=PALETTE[1], line=dict(color="white", width=1)),
                             error_y=dict(type="data", array=[r["err"] for r in mp], visible=True),
                             text=[f"ideal {r['ideal']:.1f}, crossed {r['lo']:g}–{r['hi']:g} planet radii" for r in mp],
                             hovertemplate="%{x}<br>%{text}<br>Q=%{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[h["body"] for h in hel], y=[h["Q"] for h in hel], mode="markers", name="the Sun's bubble (Voyager crossings)",
                             marker=dict(size=13, color=brand.RUST, symbol="diamond", line=dict(color="white", width=1)),
                             text=[f"ideal {h['ideal']:.0f} AU, crossed at {h['measured']:g} AU in {int(h['year'])}" for h in hel],
                             hovertemplate="%{x}<br>%{text}<br>Q=%{y:.2f}<extra></extra>"))
    ref_line(fig, label="edge exactly where the pushes balance, Q = 1")
    fig.layout.annotations[-1].update(xref="paper", x=1, xanchor="right")
    base_layout(fig, "", "Q = measured edge ÷ balance distance", height=480)
    fig.update_xaxes(type="category")
    fig.update_yaxes(range=[0, max(2.4, max(r["Q"] for r in mp) + 0.3)])
    st.plotly_chart(fig, width="stretch")
    c1, c2, c3 = st.columns(3)
    c1.metric("Sun's balance distance", f"{r_h:.0f} AU", "with the sidebar inputs", delta_color="off")
    c2.metric("Termination shock, two directions", f"{R.VOYAGER[0][2]:g} vs {R.VOYAGER[1][2]:g} AU",
              f"{abs(R.VOYAGER[0][2] / R.VOYAGER[1][2] - 1) * 100:.0f}% apart", delta_color="off")
    c3.metric("Heliopause, two directions", f"{R.VOYAGER[2][2]:g} vs {R.VOYAGER[3][2]:g} AU",
              f"{abs(R.VOYAGER[2][2] / R.VOYAGER[3][2] - 1) * 100:.0f}% apart", delta_color="off")
    st.markdown(f"""
- **One input sets every ideal.** The planets' balance distances and the Sun's all use the same solar wind push from the
  sidebar, thinned by distance from the Sun. Move it and every ideal moves together; the measured crossings stay put.
- **Earth and Neptune sit near Q = 1.** Their edges are where a plain balance of field against wind puts them.
- **Jupiter and Saturn sit well above 1.** Their bubbles are inflated from inside: Io and Enceladus pour gas into them,
  which adds a push the ideal leaves out. The departure is a reading of that extra push.
- **Uranus sits below 1.** Its field is tipped about 60° from its spin axis and set off-centre, so the plain field
  ideal overstates it. One flyby, in one season, gave its edge.
- **The Sun's bubble has two edges.** The wind's push meets the outside push near the ideal ({r_h:.0f} AU here), and
  that is about where the wind is stopped (termination shock, Q ≈ {hel[0]['Q']:.2f} and {hel[1]['Q']:.2f}). The slowed wind then
  piles up in a layer about 25–35 AU thick before the true edge, the heliopause (Q ≈ {hel[2]['Q']:.2f}).
- **Shape.** Two crossings, one about 30° north and one about 30° south of the nose, differ by 12% at the shock and 2% at the heliopause.
  The tilt of the outside field squeezes the south. The tail has never been crossed: models range from a long comet
  tail to a two-lobed "croissant" to a nearly round bubble. The edge also breathes with the 11-year solar cycle, and the
  crossings came years apart.
""")
    pdf = pd.DataFrame([dict(part="outside magnetic field", push_pPa=po["field"] * 1e12),
                        dict(part="outside heat (ions + electrons)", push_pPa=po["heat"] * 1e12),
                        dict(part="oncoming interstellar flow", push_pPa=po["flow"] * 1e12),
                        dict(part="total outside push", push_pPa=po["total"] * 1e12)])
    st.dataframe(pdf.style.format({"push_pPa": "{:.3f}"}), hide_index=True, width="stretch")
    st.caption("Push in piconewtons per square metre (pPa). The wind's push at Earth's distance is about 2,000 pPa, so it "
               "falls by the square of distance to match about 0.2 pPa near 100 AU. Neutral interstellar hydrogen passes "
               "through the edge and is left out. Planet balance: (f·B)²/2μ₀ at the edge, with the field falling as the "
               "cube of distance. Crossing ranges for the planets come from many spacecraft passes; the point is the middle "
               "of the range.")

    # ---------------- 2. two winds meeting
    st.header("2. When two bubbles meet")
    st.markdown("""
Two stars with winds, side by side. The ideal is the surface where their pushes are equal. That surface is **closed**:
a sphere wrapped around the weaker star (a flat wall if they push equally). Real wind carries momentum sideways, so the
meeting surface follows the flow (Cantó, Raga and Wilkin 1996) and **opens into a cone** that trails away from the
stronger wind. The two agree at the nose and part company away from it. Binary stars such as WR 140, η Carinae and the
WR 104 pinwheel show the cone; the heliosphere's nose and tail are the same story with the interstellar gas as the
second wind.
""")
    eta = st.slider("Weaker wind's push ÷ stronger wind's push (outflow × speed)", 0.005, 1.0, 0.1, 0.005, format="%.3f")
    s = R.two_wind_surface(eta)
    g = go.Figure()
    cx, cy = s["circle"]
    g.add_trace(go.Scatter(x=cx, y=cy, mode="lines", name="ideal: equal push (closed)", line=dict(color=REF, dash="dash", width=2)))
    fx, fy = s["flow"]
    g.add_trace(go.Scatter(x=np.r_[fx[::-1], fx[1:]], y=np.r_[-fy[::-1], fy[1:]], mode="lines", name="with momentum carried (opens)",
                           line=dict(color=brand.RUST, width=3)))
    g.add_trace(go.Scatter(x=[0, 1], y=[0, 0], mode="markers+text", text=["stronger wind", "weaker wind"], textposition="bottom center",
                           marker=dict(size=[18, 11], color=[BLACK, PALETTE[1]]), showlegend=False))
    base_layout(g, "along the line between the stars (separation = 1)", "across", height=520)
    g.update_xaxes(range=[-0.6, 3.4], scaleanchor="y", scaleratio=1)
    g.update_yaxes(range=[-1.6, 1.6])
    st.plotly_chart(g, width="stretch")
    c1, c2 = st.columns(2)
    c1.metric("Nose, from the stronger star", f"{s['nose']:.3f}", "both shapes agree here: Q = 1", delta_color="off")
    c2.metric("Cone half-angle far away", f"{s['cone_deg']:.0f}°", "the ideal sphere has none: it closes", delta_color="off")

    # ---------------- 3. belts
    st.header("3. Belts at a frequency")
    st.markdown("""
An asteroid's orbit is fitted from where it appears and when, so its **period** is timing, measured directly. Here each
period is divided by Jupiter's (or, for the Kuiper belt, Neptune's). The ideal is an exact whole-number fraction.
Where the fraction is exact, Jupiter's pull lines up with the asteroid on the same part of every orbit; for some
fractions that empties the orbit (a gap), for others it locks the asteroid in place (a clump).
""")
    planet = st.radio("Belt", ["Asteroid belt (against Jupiter)", "Kuiper belt (against Neptune)"], horizontal=True)
    pl = "Jupiter" if planet.startswith("Asteroid") else "Neptune"
    c, n, w = R.period_ratio_bins()[pl]
    reads = R.resonance_readings(pl)
    h = go.Figure()
    h.add_trace(go.Bar(x=c, y=n, width=w, marker_color="#7C8A86", name=f"objects per bin (bin width {w:g})",
                       hovertemplate="period ratio %{x:.4f}<br>%{y} objects<extra></extra>"))
    for r in reads:
        h.add_vline(opacity=1, x=r["exact"], line=dict(color=brand.RUST if r["kind"] == "gap" else PALETTE[1], dash="dot", width=1.3))
        h.add_annotation(x=r["exact"], y=1.0, yref="paper", text=r["ratio"], showarrow=False, yanchor="bottom",
                         font=dict(color=brand.RUST if r["kind"] == "gap" else PALETTE[1], size=12))
    base_layout(h, f"orbital period ÷ {pl}'s period", "number of objects", ylog=(pl == "Jupiter"), height=480)
    h.update_layout(bargap=0, showlegend=True)
    st.plotly_chart(h, width="stretch")
    rdf = pd.DataFrame([dict(ratio=f"{r['ratio']}  (exact {r['exact']:.4f})", what=r["kind"],
                             found_at=r["found"], Q=r["Q"], one_bin=r["bin_Q"]) for r in reads])
    st.dataframe(rdf.rename(columns={"found_at": "found at", "Q": "Q = found ÷ exact", "one_bin": "one bin, in Q"})
                 .style.format({"found at": "{:.4f}", "Q = found ÷ exact": "{:.4f}", "one bin, in Q": "±{:.4f}"}),
                 hide_index=True, width="stretch")
    st.markdown("""
- In the asteroid belt the **gaps** sit at Q = 1 to within about a bin: 1/3, 2/5, 3/7 and 1/2 of Jupiter's period. These are
  the Kirkwood gaps. The 2:1 gap is also where the main belt ends.
- The **clumps** also sit at Q = 1: the Hildas at 2/3 of Jupiter's period and the Trojans sharing it (1:1).
- In the Kuiper belt the Plutinos, Pluto among them, pile up at exactly 3/2 of Neptune's period, with smaller piles at 2/1
  and 5/2.
- So the belts are organised by frequency. Gaps and clumps are set by timing against one planet, read without any distance.
  Distances follow afterwards, by calculation.
""")
    st.caption("Orbits: JPL Small-Body Database snapshot (as packaged in the public Kaggle asteroid file Asteroid_Updated.csv), "
               "744,296 orbits with orbit-quality code 0–5. Jupiter's period 11.8626 years, Neptune's 164.79 years. A gap is "
               "read at its emptiest bin, and a clump at its count-weighted centre, within ±0.006 of the exact ratio "
               "(Jupiter) or ±0.03 (Neptune). The Kuiper sample holds about 2,300 objects, so its piles are small.")


PAGES = {
    "Premise": page_premise,
    "All registers": page_overview,
    "Do they share a shape?": page_same_shape,
    "Shape: solids and spheres": page_shape,
    "Shape: outlines (2D)": page_outline,
    "Flux dimming": page_flux,
    "Time dilation": page_time,
    "Ageing rate": page_ageing,
    "Acoustic angle": page_angle,
    "Cusp": page_cusp,
    "Rotation": page_rotation,
    "Clock & deflection": page_single,
    "Light and matter together": page_light_matter,
    "Gravity: departure from G": page_gravity,
    "Mass: a reading": page_mass,
    "Bubbles and belts": page_bubbles,
    "No fixed point": page_motion,
    "Sources": sources.page,
}

st.sidebar.title("FDG registers")
choice = st.sidebar.radio("Register", list(PAGES), label_visibility="collapsed")
st.sidebar.divider()
PAGES[choice]()
