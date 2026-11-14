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


def ref_line(fig, y=1.0, label="ideal, Q = 1", position="top left"):
    fig.add_hline(opacity=1, y=y, line=dict(color=REF, dash="dash", width=1.5), annotation_text=label,
                  annotation_position=position)


def base_layout(fig, xtitle, ytitle, xlog=False, ylog=False, height=480, log_ticks=True):
    fig.update_layout(title_text="", height=height, template="simple_white", margin=dict(l=60, r=20, t=40, b=50),
                      legend=dict(orientation="h", y=-0.18), hovermode="closest")
    fig.update_xaxes(title=xtitle, type="log" if xlog else "linear", showgrid=True, gridcolor="#E3E6E5")
    fig.update_yaxes(title=ytitle, type="log" if ylog else "linear", showgrid=True, gridcolor="#E3E6E5")
    # one labelling style per log axis (plain numbers or powers of ten), without the crowded 2-3-4-5 labels
    if log_ticks and xlog:
        _log_ticks(fig, "x")
    if log_ticks and ylog:
        _log_ticks(fig, "y")
    return fig


def errpts(x, y, e, name, color=BLACK, xerr=None, size=7, symbol="circle", text=None):
    return go.Scatter(x=x, y=y, mode="markers", name=name, text=text,
                      marker=dict(color=color, size=size, symbol=symbol),
                      error_y=dict(type="data", array=e, visible=True, thickness=1.2),
                      error_x=dict(type="data", array=xerr, visible=xerr is not None, thickness=1),
                      hovertemplate="%{text}<br>x=%{x:.4g}<br>Q=%{y:.4g}<extra></extra>" if text else None)


_SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def sci(v, digits=2):
    """A number for people: plain between 0.001 and 100,000 (1.39, 4,200), otherwise 1.6 × 10⁻¹⁰."""
    if v is None or not np.isfinite(v):
        return "—"
    if v == 0:
        return "0"
    e = int(np.floor(np.log10(abs(v))))
    if -3 <= e < 5:
        out = f"{v:,.{max(0, digits - 1 - e)}f}"
    else:
        m = round(v / 10 ** e, digits - 1)
        if abs(m) >= 10:
            m, e = m / 10, e + 1
        out = f"{m:.{digits - 1}f} × 10{str(e).translate(_SUP)}"
    return out.replace("-", "−", 1) if out.startswith("-") else out


def _cell(v, f):
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "—"
    return f(v) if callable(f) else f.format(v)


def show_table(df, names=None, fmt=None, wrap=False, **kw):
    """Tables with plain column names, people-style numbers and a dash for empty cells."""
    df = pd.DataFrame(df).copy()
    for col, f in (fmt or {}).items():
        df[col] = [_cell(v, f) for v in df[col]]
    for col in df.columns:
        if df[col].isna().any():
            df[col] = df[col].astype(object).where(df[col].notna(), "—")
    df = df.rename(columns=names or {})
    if wrap:  # long text wraps instead of running off the right edge
        st.table(df, hide_index=True)
    else:
        st.dataframe(df, hide_index=True, width="stretch", **kw)


def _log_tickvals(vals):
    """Tick positions for a log axis: one per decade over wide ranges, 1-2-5 steps over narrow ones."""
    v = np.asarray([x for x in vals if np.isfinite(x) and x > 0], float)
    if not len(v):
        return None, None
    lo, hi = int(np.floor(np.log10(v.min()))), int(np.ceil(np.log10(v.max())))
    span = hi - lo
    steps = (1,) if span >= 4 else (1, 3) if span == 3 else (1, 2, 5) if span == 2 else (1, 1.5, 2, 3, 5, 7)
    ks = range(lo, hi + 1, 2 if span >= 9 else 1)  # every other decade on very wide axes, so labels don't crowd
    ticks = [m * 10.0 ** k for k in ks for m in steps]
    if any(not (1e-3 <= t < 1e5) for t in ticks):
        power = lambda k: "1" if k == 0 else "10" if k == 1 else f"10{str(k).translate(_SUP)}"
        text = [(f"{m:g} × 10{str(k).translate(_SUP)}" if m != 1 else power(k)) for k in ks for m in steps]
    else:
        text = [f"{t:,g}" for t in ticks]
    return ticks, text


def _numeric(a):
    try:
        return np.asarray(a, float).ravel()
    except (TypeError, ValueError):
        return np.array([])


def _log_ticks(fig, axis):
    vals = np.concatenate([_numeric(getattr(t, axis, None)) for t in fig.data if getattr(t, axis, None) is not None] or [np.array([])])
    tv, tt = _log_tickvals(vals)
    if tv:
        (fig.update_xaxes if axis == "x" else fig.update_yaxes)(tickmode="array", tickvals=tv, ticktext=tt)


# ------------------------------------------------------------------ cached data
@st.cache_data(show_spinner="Loading Pantheon+…")
def pantheon_plus_register(zcol, lo0, lo1, nbins):
    t, cov = R.load_pantheon_plus()
    return R.flux_dimming_plus(t, cov, zcol=zcol, lo=(lo0, lo1), nbins=nbins)


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
    st.header("Premise: why read the universe in registers", anchor=False)
    st.markdown("""
#### 1. What is a register?
A register is a measured value divided by its ideal value, so the ideal sits at **Q = 1**. The ideal is a reference
condition: a perfect sphere, a perfect circle, a straight line, a steady clock, an exactly even series. Each of these is
reached exactly only in a limit that takes infinity, such as infinitely many faces or the last term of an infinite series.
Measured things sit at some distance from that reference. Some sit very close: large craters are close to a circle, and
supernova light curves stretch by the full (1 + z). Others sit far away. **The departure from the
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
measured is redshift, angle, flux and time, and the registers are written in those.
""")
    st.subheader("The registers")
    show_table(pd.DataFrame([
        ["Shape: solids and spheres", "Any closed body", "a perfect sphere (infinitely many faces)", "number of faces", "computed meshes"],
        ["Shape: outlines (2D)", "Polygons, craters", "a perfect circle (infinitely many sides)", "sides, diameter", "computed outlines, Robbins Moon and Mars crater catalogs"],
        ["Flux dimming", "Type Ia supernovae", "the local linear flux–redshift relation", "redshift z", "Pantheon+ raw peak magnitudes mB, heliocentric redshifts"],
        ["Time dilation", "Type Ia supernovae", "full (1+z) stretch of light curves", "redshift z", "White et al. 2024 (DES), Blondin et al. 2008"],
        ["Cusp", "Lensed image triplets", "a perfectly smooth lens", "opening angle", "3 radio lenses"],
        ["Light: departure from the vacuum limit", "Glass, water, air, cold atoms", "the vacuum speed (a defined limit, never met)", "medium or path", "refractive indices, slow-light experiment"],
    ], columns=["Register", "Population", "Ideal (Q = 1)", "Read against", "Data"]), wrap=True)
    st.caption("Left out because a model sits on the measured side: the CMB power spectrum (spherical-harmonic expansion, "
               "an infinite series); supernova distance moduli (bias corrections simulated in flat ΛCDM, Brout et al. 2022 "
               "§3.1); cosmic-chronometer ages (stellar population models); thin-shell acoustic angles (projection "
               "correction computed in Planck ΛCDM, de Carvalho et al. 2021 §4.2); orbital eccentricities (fitted from "
               "dynamical ephemerides).")


def mini_chart(fig, xtitle, ytitle, xticks=None, yticks=None, xlog=False, ylog=False, ideal=1.0, ideal_label="ideal"):
    """Shared look for the overview cards: same height, labeled axes, clean log ticks, a clear ideal line."""
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
    st.header("All registers at a glance")
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
    zf, Qf, sf, *_ = pantheon_plus_register("zHEL", 0.015, 0.06, 17)
    fig = go.Figure(errpts(zf, Qf, sf, "Pantheon+", size=8))
    mini_chart(fig, "redshift z", "Q", xticks=[0.05, 0.1, 0.2, 0.5, 1, 2], xlog=True)
    fig.update_yaxes(range=[0.9, 1.85])
    cards.append(("Flux dimming", fig, "Raw supernova peak magnitudes against the local linear relation (Pantheon+)."))

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

    for i in range(0, len(cards), 2):
        cols = st.columns(2)
        for col, (title, fig, reads) in zip(cols, cards[i:i + 2]):
            overview_card(col, title, fig, reads)


def page_shape():
    st.header("Shape: solids and spheres")
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
        show_table(df, fmt={"Q_v": "{:.5f}", "faces": "{:,}"}, names={"shape": "Shape", "faces": "Faces"}, height=430)
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
        show_table(bd, fmt={"flattening": "{:.5f}", "Q_v": "{:.5f}", "Q_v / round body": "{:.6f}"},
                   names={"body": "Body", "flattening": "Flattening"})
        st.caption("The last column compares each body with an unflattened body on the same mesh. Every one "
                   "sits above it; Saturn, the flattest, sits highest.")
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
    st.header("Shape: outlines (2D)")
    st.markdown(
        "**Q_a = P² / A** compares an outline's boundary length P with the area A it encloses. It has no units and does "
        "not change with size. The ideal is a perfect circle. This is the classical isoperimetric ratio (Osserman 1978): "
        "no outline of a given length encloses more area than a circle, so the circle has the lowest Q_a."
    )
    tab1, tab3 = st.tabs(["Regular polygons", "Craters on the Moon and Mars"])
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
        show_table(df, fmt={"Q_a": "{:.6f}"}, names={"sides": "Sides"}, height=260)
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
    st.header("Flux dimming: how supernova light fades with redshift")
    st.markdown("Q = 10^((m − C)/5) / z: the dimming of supernova light divided by redshift, with the nearby supernovae "
                "setting Q = 1. It is built from peak magnitudes (flux ratios) and heliocentric redshifts (frequency ratios).")
    fig = go.Figure()
    lo = st.sidebar.slider("Nearby supernovae that set Q = 1 (redshift range)", 0.01, 0.12, (0.015, 0.06), 0.005)
    nb = st.sidebar.slider("Number of bins", 8, 30, 17)
    zb, Q, sQ, n, na, nt = pantheon_plus_register("zHEL", lo[0], lo[1], nb)
    fig.add_trace(errpts(zb, Q, sQ, f"Pantheon+ ({nt:,} supernovae, {na:,} nearby)", text=[f"n={k}" for k in n]))
    st.caption("m is the raw SALT2 peak magnitude mB (Scolnic et al. 2022). No bias correction, no stretch or colour "
               "standardization and no host-mass step are applied, because the published corrected magnitudes use "
               "simulations run in flat ΛCDM (Brout et al. 2022, §3.1). A supernova seen by several surveys counts once. "
               "Points are plain bin means; bars are the standard error of each bin's own scatter. DES 5-year is left out: its release gives only corrected distance moduli.")
    ref_line(fig, label="local linear relation, Q = 1")

    base_layout(fig, "redshift z", "Q (flux dimming / z, nearby = 1)", xlog=True, height=520)
    st.plotly_chart(fig, width="stretch")


def page_time():
    st.header("Time dilation: how far light curves stretch")
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
                              annotation_text=d["study"],
                              annotation_position="bottom left" if d["b"] < 1 else "top left")
        ref_line(fig, 1.0, "b = 1, full (1+z) stretch", position="bottom right")
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
    show_table(pd.DataFrame(data)[["study", "b", "err", "zmin", "zmax", "n"]], fmt={"b": "{:g}", "err": "{:.2g}", "zmin": "{:g}", "zmax": "{:g}",
                                                                              "n": lambda v: f"{float(v):,.0f}" if str(v).strip() else "—"},
               names={"study": "Study", "err": "± b", "zmin": "Lowest z", "zmax": "Highest z", "n": "Objects"})
    st.caption("Light-curve widths (a time ratio) read against redshift (a frequency ratio). Studies without a "
               "redshift range in the local data are drawn as bands.")


def page_cusp():
    st.header("Cusp flux ratio: the brightness of lensed image triplets")
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
    show_table(rows, fmt={"opening_angle_deg": "{:.1f}", "median_Q": "{:.3f}", "spread": "{:.3f}"},
               names={"system": "Lens", "opening_angle_deg": "Opening angle (degrees)", "median_Q": "Median Q", "spread": "Spread",
                      "epochs": "Epochs"})
    st.caption("Dashes are single epochs and instruments. In all three lenses the middle image is fainter than the outer pair "
               "together. Radio fluxes are used because they are free of dust and microlensing.")


def page_light_speed():
    st.header("Light: departure from the vacuum limit")
    st.markdown("""
Light speed is called a constant, but no light anyone has measured moves at it. Two things sit behind the word.

- **A unit choice.** Since 1983 the meter has been *defined* as the distance light travels in vacuum in
  1/299,792,458 of a second. So 299,792,458 m/s is exact by definition and can no longer be measured. Every speed
  measured since is already a ratio to it.

A pure vacuum is never found. So, as everywhere in FDG, the vacuum speed is an **ideal**, a limit for comparison.
The register is **Q_c = measured speed ÷ the vacuum limit**, and the chart reads how far each case falls short of it,
**1 − Q_c**. Nothing that carries a signal has ever been measured above it.
""")
    rows = [r for r in R.light_speed_table() if r["group"] == "Matter"]  # measured ratios only
    df = pd.DataFrame(rows)
    colors = {"Matter": PALETTE[0], "Plasma": PALETTE[1], "Near mass": PALETTE[2], "Vacuum tests": PALETTE[5], "Calculated": "#9AA5AB"}
    symbols = {"measured": "circle", "illustration": "circle-open", "illustration, upper limit": "triangle-left-open"}
    fig = go.Figure()
    for (grp, kind), d in df.groupby(["group", "kind"], sort=False):
        fig.add_trace(go.Scatter(
            x=d.departure, y=d.reading, mode="markers", name=grp if grp.lower() == kind else f"{grp} ({kind})",
            marker=dict(size=13, color=colors[grp], symbol=symbols[kind], line=dict(width=2, color=colors[grp])),
            customdata=np.c_[d.measured, d.added], text=[f"{q:.15g}" if np.isfinite(q) else "at least this close" for q in d.Q_c],
            hovertemplate="%{y}<br>1 − Q_c = %{x:.3g}<br>Q_c = %{text}<br>measured: %{customdata[0]}<br>added: %{customdata[1]}<extra></extra>"))
    base_layout(fig, "departure from the vacuum limit, 1 − Q_c (left is closer to the ideal)", "", xlog=True, height=720, log_ticks=False)
    fig.update_xaxes(range=[-20, 0.4], dtick=2, exponentformat="power")
    fig.update_yaxes(type="category", autorange="reversed", categoryorder="array", categoryarray=list(df.reading))
    fig.update_layout(legend=dict(orientation="h", y=-0.12))
    st.plotly_chart(fig, width="stretch")
    st.caption("Every reading is measured. Hover for what is measured.")

    st.subheader("Readings")
    c1, c2, c3 = st.columns(3)
    reg = df[df.kind == "measured"]
    c1.metric("Register readings span", f"{np.log10(reg.departure.max() / reg.departure.min()):.0f} decades",
              "slow light near 1 to air", delta_color="off")
    st.markdown("""
- **Matter** gives the large departures. Q_c here is 1/n, the refractive index, read from refraction angles alone.
  Light crossing a cold atom cloud slowed to 17 m/s, and has been stopped altogether.
""")

    st.subheader("How the ideal was fixed")
    h = pd.DataFrame(R.C_HISTORY, columns=["year", "who", "km_s", "err"])
    h["departure"] = np.abs(h.km_s / R.C_KMS - 1)
    h["rel_err"] = h.err / R.C_KMS
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=h.year, y=h.departure, mode="markers+lines", name="|measured ÷ today's defined value − 1|",
                             line=dict(color=PALETTE[0], dash="dot"), marker=dict(size=10, color=PALETTE[0]), text=h.who,
                             hovertemplate="%{text}, %{x}<br>off by %{y:.2g}<extra></extra>"))
    fig.add_trace(go.Scatter(x=h.year, y=h.rel_err, mode="markers", name="the measurement's own stated uncertainty",
                             marker=dict(size=10, color=BLACK, symbol="line-ew-open", line=dict(width=3)), text=h.who,
                             hovertemplate="%{text}, %{x}<br>uncertainty %{y:.2g}<extra></extra>"))
    fig.add_vline(opacity=1, x=1983, line=dict(color=REF, dash="dash", width=1.5), annotation_text="1983: value fixed by definition",
                  annotation_position="top left")
    base_layout(fig, "year", "fractional difference", ylog=True, height=440, log_ticks=False)
    fig.update_yaxes(exponentformat="power")
    st.plotly_chart(fig, width="stretch")
    st.markdown("""
For three centuries c was a measurement, and each new method came closer to the last. By 1972 the measurements agreed to
a few parts in a billion, limited by how well the meter itself was known. In 1983 the number was frozen and the meter
was redefined from it. Since then a "measurement of c" is really a measurement of length. The ideal was not found in
nature; it was chosen as the best limit known, and kept fixed so that everything else could be compared with it.
""")
    show_table(df[["reading", "group", "kind", "departure", "Q_c", "measured", "added"]],
               fmt={"departure": sci, "Q_c": lambda q: "≈ 1" if 1 - q < 1e-5 else sci(q, 4)},
               names={"reading": "Reading", "group": "Group", "kind": "Kind", "departure": "1 − Q_c", "measured": "Measured",
                      "added": "Added"}, wrap=True)


TAGLINE = "Read the shape of the universe from measurements, by comparing each measured value with its ideal."

# Every page, grouped for the sidebar menu: (menu group, function, menu title, url)
PAGE_LIST = [
    ("", None, "Home", "home"),
    ("Start here", page_premise, "Premise", "premise"),
    ("Start here", page_overview, "All registers", "all-registers"),
    ("Shape", page_shape, "Shape: solids and spheres", "solids"),
    ("Shape", page_outline, "Shape: outlines (2D)", "outlines"),
    ("Light across redshift", page_flux, "Flux dimming", "flux"),
    ("Light across redshift", page_time, "Time dilation", "time-dilation"),
    ("Lensing", page_cusp, "Cusp", "cusp"),
    ("Light and its medium", page_light_speed, "Light: vacuum limit", "light-speed"),
    ("Sources", sources.page, "Sources", "sources"),
]

# one line on each page, for the Home page
ABOUT = {
    "premise": "what a register is, why use them, and what they leave out",
    "all-registers": "every register on one screen, each against its ideal",
    "solids": "faceted solids closing in on a perfect sphere, and real bodies",
    "outlines": "polygons and craters against a perfect circle",
    "flux": "how supernova light dims with redshift (Pantheon+)",
    "time-dilation": "how far distant light curves stretch",
    "cusp": "the brightness of lensed image triplets",
    "light-speed": "light speed in glass, water, air and cold atoms",
    "sources": "the data and papers behind every page",
}

GROUP_ABOUT = {
    "Start here": "The idea, and all the registers side by side.",
    "Shape": "Bodies and outlines measured against a perfect sphere or circle.",
    "Light across redshift": "What happens to light from farther and farther away.",
    "Lensing": "The brightness of lensed image triplets.",
    "Light and its medium": "How fast light travels, and what it travels through.",
    "Sources": "Where the data come from.",
}


def page_home():
    st.header("Start here", anchor=False)
    st.markdown(
        "This app reads the shape of the universe straight from published measurements. It does that by laying each "
        "measurement against an ideal, a perfect version of the same thing, and showing how far the real thing departs "
        "from it.")
    with st.container(border=True):
        st.markdown(
            "**What is a register?** *Register* is the name this app gives to that comparison. It is a working term "
            "for this project, not a standard term you will find in textbooks or papers. A register takes one kind of "
            "measurement and divides it by its ideal value. The result is called **Q**:\n\n"
            "- **Q = 1** means the measurement matches the ideal exactly.\n"
            "- **Q above or below 1** means it departs from the ideal, and by how much.\n\n"
            "For example, a crater's rim can be compared with a perfect circle, or the dimming of supernova light "
            "with the simple straight-line rule seen in nearby supernovae. Because Q has no units, very different "
            "things can be read side by side. The size of each departure, and how it changes, is what the pages show.")
    st.markdown(
        "**How to get around:** the menu on the left lists every page, in groups. Start with *Premise* for the idea "
        "and *All registers* for the whole picture, then open any register. Each page's own settings appear in the "
        "sidebar under the menu. On every chart the ideal, Q = 1, is drawn as a dashed line. *Sources* lists the "
        "data and papers behind each page.")
    groups = {}
    for group, _fn, title, url in PAGE_LIST:
        if group:
            groups.setdefault(group, []).append((title, url))
    for group, items in groups.items():
        with st.container(border=True):
            st.subheader(group, anchor=False)
            st.caption(GROUP_ABOUT[group])
            for title, url in items:
                st.page_link(PAGES_BY_URL[url], label=f"**{title}**: {ABOUT[url]}")
    st.page_link(PAGES_BY_URL["premise"], label="Begin with the premise →")


PAGES_BY_URL = {url: st.Page(fn or page_home, title=title, url_path=url, default=(url == "home"))
                for _g, fn, title, url in PAGE_LIST}
NAV = {}
for group, _fn, _title, url in PAGE_LIST:
    NAV.setdefault(group, []).append(PAGES_BY_URL[url])
page = st.navigation(NAV, expanded=True)  # list every page, so none hide behind "View more"

# The same title banner on every page, as on the other Dougalien Systems apps; each page then gives its own heading
brand.app_header("Finite Deformable Geometry", TAGLINE)
page.run()
