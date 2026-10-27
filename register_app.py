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


def ref_line(fig, y=1.0, label="ideal, Q = 1 (never reached)"):
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
    st.markdown("### The geometry of the universe, by measurement only")
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
- **They need no model to compute.** The ideal is a reference to measure against, not an assumption about what the object is.
- **Each one stands alone,** so one register can be added, questioned or replaced without disturbing the others.
- **Where an ideal involves infinity or π,** the register works with finite measured quantities and treats the ideal only
  as the direction they head in.

#### 3. The assumptions currently accepted by the community
The standard picture of the universe begins with assumptions that are not themselves measured:
- **Expanding space,** described by a single scale factor that turns redshift into distance and time.
- **A smooth, uniform universe on large scales** (the cosmological principle), which fixes the geometry before any data arrive.
- **A distance ladder** whose upper rungs use that expansion history to convert brightness and redshift into distance.
- **Dark matter and dark energy,** about 95% of the content, added so that the model fits the data.
- **Infinite series and limits** in the analysis itself, such as the spherical-harmonic expansion of the microwave sky.

The registers assume none of these. They do not show that the assumptions are wrong; they show what the measurements look
like without them.

#### 4. The no-fixed-point argument
Within our Galaxy, distance can be measured directly: parallax uses Earth's own orbit as a measured baseline. Beyond the
Galaxy there is no stationary marker to measure from. Every galaxy moves relative to every other, like plates in plate
tectonics, and the two candidate rest frames on the sky (the microwave dipole and the quasar dipole) do not agree. So
**size, speed and distance beyond the Galaxy are calculations**, built on an assumed frame and an assumed expansion. What is
measured is redshift, angle, flux and time, and the registers are written in those. Where a register's data still lean on a
calculated quantity, its page says which one. The *No fixed point* page works through Andromeda as an example.

#### Together, these registers are the shape of the universe
Each register is one population's departure from its ideal. Read side by side, they are the geometry of the universe as
measured from here: no expansion assumed, no fixed point required, and nothing added to make things fit.
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
    ], columns=["Register", "Population", "Ideal (Q = 1)", "Read against", "Data"]), hide_index=True, width="stretch")
    st.caption("The CMB power spectrum is not used. Its multipole index comes from a spherical-harmonic expansion, an infinite series, "
               "so it is not a measurement-only quantity.")


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
    st.markdown("Each card is one register: the measurement against its ideal, drawn as a dashed slate line that no "
                "population reaches. Nothing here is fitted. Open a register in the sidebar for its controls and details.")
    cards = []

    # Shape: solids and spheres
    df = shape_table(6)
    fig = go.Figure(go.Scatter(x=df.faces, y=df.Q_v, mode="lines+markers", line=dict(color=BLACK, width=2),
                               marker=dict(size=8, color=BLACK), text=df.shape, hovertemplate="%{text}<br>Q_v=%{y:.4f}<extra></extra>"))
    mini_chart(fig, "number of faces", "Q_v = S^1.5 / V", xticks=[4, 10, 100, 1000, 10000, 100000], xlog=True,
               ideal=SPHERE_LIMIT, ideal_label="perfect sphere")
    fig.update_yaxes(range=[10.2, 20])
    cards.append(("Shape: solids and spheres", fig, "More faces bring a body closer to the sphere; no finite number of faces gets there."))

    # Shape: outlines
    fig = go.Figure()
    for i, n0 in enumerate((3, 4)):
        seq = R.polygon_doubling(n0, 10)
        fig.add_trace(go.Scatter(x=[n for n, _ in seq], y=[q for _, q in seq], mode="lines+markers",
                                 line=dict(color=PALETTE[i], width=2), marker=dict(size=7)))
    mini_chart(fig, "number of sides", "Q_a = P² / A", xticks=[3, 10, 100, 1000], xlog=True,
               ideal=4 * np.pi, ideal_label="perfect circle")
    fig.update_yaxes(range=[12.2, 21.5])
    cards.append(("Shape: outlines (2D)", fig, "Polygons doubled again and again close in on the circle and never reach it."))

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
        "in both cases the zero point is a limit that is never actually reached (a path of zero length, infinitely many faces).\n\n"
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
               "1 + z and the two low-redshift ones fall short of it, by about 1σ and 2σ (see the table). The same relation is also what an expanding-space picture "
               "predicts, so it shows the registers agree with each other rather than choosing between pictures.")


def page_shape():
    st.title("Shape: solids and spheres")
    st.markdown(
        "**Q_v = S^(3/2) / V** compares a body's surface S with the volume V it holds. It has no units and does not change "
        "with size. Every number here comes straight from a triangle mesh: the area is a sum of triangle areas and the "
        "volume a sum of small tetrahedra, using only sums, products and square roots."
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
                      annotation_text="perfect sphere: needs infinitely many faces")
        base_layout(fig, "number of faces", "Q_v", xlog=True, height=520)
        fig.update_yaxes(range=[10.3, 20.5])
        st.plotly_chart(fig, width="stretch")
    with c2:
        st.dataframe(df.style.format({"Q_v": "{:.5f}"}), hide_index=True, width="stretch", height=430)
    st.info(f"Every added face brings the body closer to the sphere, and no finite number of faces gets there. At level "
            f"{max_level} the body has {20 * 4 ** max_level:,} faces and Q_v = {df.Q_v.iloc[-1]:.6f}. The sphere itself, the "
            "ideal, belongs to infinity. That is why the register uses the finite bodies and treats the sphere only as the "
            "direction they head in.")

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
        "not change with size. The ideal is a perfect circle, which needs infinitely many sides. Every value here is built "
        "from finite outlines, using only sums, products and square roots."
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
        fig.add_hline(opacity=1, y=CIRCLE_LIMIT, line=dict(color=REF, dash="dash"), annotation_text="perfect circle: needs infinitely many sides")
        base_layout(fig, "number of sides", "Q_a", xlog=True, height=480)
        fig.update_yaxes(range=[12.3, 21.3])
        st.plotly_chart(fig, width="stretch")
        st.caption("Each polygon is drawn inside the same circle and its sides are doubled again and again, the way Archimedes "
                   "did it: the new side is √(2 − √(4 − s²)). No angle and no π is used. Every doubling brings Q_a closer to the "
                   "circle, and no finite polygon reaches it.")
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
                   "fraction of a percent of the circle without reaching it; the comets sit far above it.")
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
                   "to the circle, and larger craters come closer than small ones, but none sits on it.")


def page_flux():
    st.title("Flux dimming")
    st.markdown("Q = 10^((m − C)/5) / z: the dimming of supernova light divided by redshift, with the nearby supernovae "
                "setting Q = 1. Only magnitudes (flux ratios) and redshifts (frequency ratios) are used. No distance, "
                "absolute brightness or expansion rate enters.")
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
    st.caption("Only light-curve widths and redshifts are used: a time ratio against a frequency ratio. Studies without a "
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
               "That conversion is undone here, so the register is redshift change per stellar time and nothing else. "
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
    st.caption("Angles and redshifts only. The five points come from different surveys and galaxy types.")


def page_cusp():
    st.title("Cusp flux ratio")
    st.markdown("When a lens splits one source into a tight triplet of images, a perfectly smooth lens would make the middle "
                "image as bright as the two outer ones together, in the limit of a closed triplet. The register is "
                "**Q = F_middle / (F_outer1 + F_outer2)**, from radio flux ratios only.")
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
    st.caption("Rotation speeds are Doppler shifts, which are frequency ratios. Radius over disk scale length is a ratio of two "
               "angles on the sky, so the default axis uses no distance. The visible-matter side is built from light with an "
               "assumed mass-to-light ratio and a catalog distance; those are the calculated parts of this register.")


def page_single():
    st.title("Single-value registers")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Clock")
        st.latex(r"Q_\tau = \frac{(\Delta\nu/\nu)\,c^2}{g\,h}")
        st.metric("Measured", "Q_τ = 1", "Pound–Rebka–Snider (~1%), lattice clocks (parts in 10⁵)", delta_color="off")
        st.caption("Only tests where g is measured on the spot qualify. All of them sit at Earth's surface gravity, so this is one point, not a curve.")
    with c2:
        st.subheader("Deflection")
        st.latex(r"Q_\lambda = \frac{\alpha_{obs}}{\alpha_{traj}} = 1 + \gamma")
        st.metric("Measured", "Q_λ = 2", "γ known to 2.3×10⁻⁵ (Cassini)", delta_color="off")
        st.caption("Light passing the Sun bends twice as much as a body moving at the same speed would. Measured inside the Solar System only.")


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
              "an angle per year, not a speed", delta_color="off")
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
                   "is a different guess at where on this line Andromeda sits.")
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
        st.caption(f"The often-quoted ~110 km/s is not measured. It is the 300 km/s Doppler speed minus the Sun's own orbit, "
                   f"which has to be assumed. At {v_c} km/s the closing speed is {-float(R.m31_galactocentric_radial(v_c)):.0f} km/s. "
                   "Changing the frame changes the speed by almost a factor of three.")

    st.header("2. A measurement-only way out: looming")
    st.markdown("An object coming toward you grows on the sky. Its angular size divided by its rate of growth is the **time "
                "to contact**, τ = θ / (dθ/dt), and no distance enters. Flies and drivers use the same quantity. Multiply τ "
                "by the measured closing speed and you get a distance built from measurements alone.")
    tau, rel, rate1 = R.looming(d_pick)
    _, _, rate_full = R.looming(d_pick, R.M31["theta_deg"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Time to contact this implies", f"{float(tau):.2f} billion years", f"at your assumed {d_pick} kpc", delta_color="off")
    c2.metric("Growth of Andromeda's full width", f"{float(rate_full):.1f} µas/yr", f"{R.M31['theta_deg']}° across", delta_color="off")
    c3.metric("Growth of a 1° separation", f"{float(rate1):.1f} µas/yr", "e.g. between two of its star clusters", delta_color="off")
    st.markdown(f"Gaia measures Andromeda's whole sideways drift to about ±{mu_e:.0f} µas/yr. The looming signal is a few µas/yr, "
                "below that today. Precision improves with time baseline, so this is a test that waits on more years of data, "
                "not on a model.")

    st.header("3. The sky's \"hotspot\": two rest frames that disagree")
    dr = R.dipole_register()
    st.markdown(f"""
The microwave sky is **{R.CMB_DIPOLE['dT_mK']:.3f} mK** warmer in one direction, a fraction **{dr['beta']:.2e}** of its
{R.CMB_DIPOLE['T0_K']} K temperature. That is measured. Reading it as our motion gives **{dr['v_kms']:.0f} km/s**, which is a
calculation that assumes the whole dipole is motion. If it is, distant quasars should bunch toward the same direction by a
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
    st.caption("The registers stay in the left-hand column: redshift, angle, flux and time ratios.")


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
    "No fixed point": page_motion,
    "Sources": sources.page,
}

st.sidebar.title("FDG registers")
choice = st.sidebar.radio("Register", list(PAGES), label_visibility="collapsed")
st.sidebar.divider()
PAGES[choice]()
