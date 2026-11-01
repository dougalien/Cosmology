"""Register calculations for the Finite Deformable Geometry display app.

Every register is a measured quantity divided by its reference value, so the
reference sits at Q = 1. The reference is an ideal that only infinity could
reach; measured populations come close to it, or not, but never sit on it.
"""
from __future__ import annotations

import csv
import os
from functools import lru_cache

import numpy as np
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "register_data")
SOURCE = r"C:\Users\allen\OneDrive\Documents\ArXiv Papers\Vol. 1 Finite Response Mapping"
PANTHEON_COV = os.path.join(SOURCE, "clean_registers", "pantheon_plus", "Pantheon+SH0ES_STAT+SYS.cov")
KPC = 3.0857e19
G_DAGGER = 1.2e-10
# 1 km/s/Mpc expressed as a rate per gigayear: published chronometer rates converted back to redshift per time
PER_GYR = 1.0227e-3


def _csv(name):
    with open(os.path.join(DATA, name), encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))


# ----------------------------------------------------------------- shape (Q_v)
def mesh_area_volume(verts, faces):
    """Surface area and enclosed volume of a closed triangle mesh.

    Area is the sum of triangle areas; volume is the divergence-theorem sum of
    signed tetrahedra from the origin. Only products, sums and square roots.
    """
    a, b, c = verts[faces[:, 0]], verts[faces[:, 1]], verts[faces[:, 2]]
    cr = np.cross(b - a, c - a)
    area = 0.5 * np.linalg.norm(cr, axis=1).sum()
    vol = abs(np.einsum("ij,ij->i", a, np.cross(b, c)).sum()) / 6.0
    return area, vol


def q_v(area, vol):
    return area ** 1.5 / vol


def _hull_faces(verts):
    from scipy.spatial import ConvexHull
    h = ConvexHull(verts)
    return h.simplices


def platonic(name):
    """Unit-scale vertex sets; faces come from the convex hull (triangulated)."""
    s5 = np.sqrt(5.0)
    p = (1 + s5) / 2
    if name == "Tetrahedron":
        v = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
    elif name == "Cube":
        v = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    elif name == "Octahedron":
        v = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    elif name == "Dodecahedron":
        v = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
        for a in (-1, 1):
            for b in (-1, 1):
                v += [(0, a / p, b * p), (a / p, b * p, 0), (a * p, 0, b / p)]
    elif name == "Icosahedron":
        v = []
        for a in (-1, 1):
            for b in (-1, 1):
                v += [(0, a, b * p), (a, b * p, 0), (a * p, 0, b)]
    else:
        raise ValueError(name)
    v = np.array(v, float)
    return v, orient_outward(v, _hull_faces(v))


def orient_outward(verts, faces):
    """Flip faces so every normal points away from the origin (fine for star-shaped meshes)."""
    faces = faces.copy()
    a, b, c = verts[faces[:, 0]], verts[faces[:, 1]], verts[faces[:, 2]]
    inward = np.einsum("ij,ij->i", np.cross(b - a, c - a), a + b + c) < 0
    faces[inward] = faces[inward][:, [0, 2, 1]]
    return faces


PLATONIC = {"Tetrahedron": 4, "Cube": 6, "Octahedron": 8, "Dodecahedron": 12, "Icosahedron": 20}


def icosphere(level):
    """Icosahedron subdivided `level` times, vertices pushed onto the unit sphere.

    20 * 4**level triangular faces. Each new vertex is a normalised midpoint,
    which needs a square root and nothing else.
    """
    v, f = platonic("Icosahedron")
    v = v / np.linalg.norm(v, axis=1, keepdims=True)
    verts = [tuple(x) for x in v]
    faces = [tuple(x) for x in f]
    for _ in range(level):
        cache, new = {}, []

        def mid(i, j):
            key = (min(i, j), max(i, j))
            if key not in cache:
                m = np.add(verts[i], verts[j])
                m = m / np.sqrt(np.dot(m, m))
                verts.append(tuple(m))
                cache[key] = len(verts) - 1
            return cache[key]

        for a, b, c in faces:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            new += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        faces = new
    return np.array(verts), np.array(faces)


@lru_cache(maxsize=16)
def icosphere_cached(level):
    return icosphere(level)


def spheroid_qv(flattening, level=6):
    """Q_v of an oblate spheroid (polar/equatorial = 1 - f) from a fine mesh."""
    v, f = icosphere_cached(level)
    v = v * np.array([1.0, 1.0, 1.0 - flattening])
    return q_v(*mesh_area_volume(v, f))


def lumpy_body(level, roughness, seed=0):
    """A non-convex 'rubble' body: icosphere with smoothed random radial bumps."""
    v, f = icosphere_cached(level)
    rng = np.random.default_rng(seed)
    r = 1 + roughness * rng.standard_normal(len(v))
    # three passes of neighbour averaging so bumps are lumps, not spikes
    nb = [[] for _ in range(len(v))]
    for a, b, c in f:
        nb[a] += [b, c]; nb[b] += [a, c]; nb[c] += [a, b]
    for _ in range(3):
        r = np.array([0.5 * r[i] + 0.5 * r[n].mean() for i, n in enumerate(nb)])
    r = 1 + (r - r.mean()) * (roughness / max(r.std(), 1e-12))
    return v * r[:, None], f


# Flattening values (equatorial - polar) / equatorial. Planets: NASA Planetary Fact Sheet.
# Sun: equator-pole radius difference 7.2 mas (Kuhn et al. 2012, SDO/HMI) over a 959.63 arcsec mean radius.
BODIES = {"Sun": 7.5e-6, "Earth": 1 / 298.257, "Mars": 0.00589, "Saturn": 0.09796, "Jupiter": 0.06487}


# ------------------------------------------------------- flux dimming / redshift
def pantheon_binned():
    d = np.loadtxt(os.path.join(DATA, "pantheon_binned.txt"))
    return d[:, 1], d[:, 2], d[:, 3]


def flux_dimming_binned(z_anchor=0.05):
    z, m, s = pantheon_binned()
    lo = z < z_anchor
    w = 1 / s[lo] ** 2
    C = np.sum(w * (m[lo] - 5 * np.log10(z[lo]))) / np.sum(w)
    Q = 10 ** ((m - C) / 5) / z
    return z, Q, Q * np.log(10) / 5 * s


def _pantheon_plus_table():
    with open(os.path.join(DATA, "Pantheon+SH0ES.dat")) as f:
        cols = f.readline().split()
        rows = [l.split() for l in f if l.strip()]
    col = {c: i for i, c in enumerate(cols)}
    return {c: np.array([float(r[col[c]]) for r in rows]) for c in ("zHD", "zCMB", "m_b_corr", "IS_CALIBRATOR", "m_b_corr_err_DIAG")}


def pantheon_cov_available():
    return os.path.exists(PANTHEON_COV)


def load_pantheon_plus(full_cov=True):
    t = _pantheon_plus_table()
    n = len(t["zHD"])
    if full_cov and pantheon_cov_available():
        import pandas as pd
        cov = pd.read_csv(PANTHEON_COV, header=None, skiprows=1, engine="c").to_numpy().reshape(n, n)
    else:
        cov = np.diag(t["m_b_corr_err_DIAG"] ** 2)
    return t, cov


def flux_dimming_plus(t, cov, zcol="zHD", lo=(0.015, 0.06), nbins=17, zmax=2.3):
    """GLS-binned flux-dimming register, as in clean_registers/flux_dimming_cov.py."""
    z = t[zcol]
    keep = (t["IS_CALIBRATOR"] == 0) & (z > 0.01)
    idx = np.where(keep)[0]
    y = t["m_b_corr"][idx] - 5 * np.log10(z[idx])
    C = cov[np.ix_(idx, idx)]
    zz = z[idx]

    def wts(mask):
        Ci = np.linalg.inv(C[np.ix_(mask, mask)])
        w = np.zeros(len(idx)); w[mask] = Ci.sum(1) / Ci.sum()
        return w

    anchor = (zz >= lo[0]) & (zz < lo[1])
    wl = wts(anchor)
    edges = np.geomspace(lo[1], zmax, nbins + 1)
    W, zb, nb = [], [], []
    for a, b in zip(edges[:-1], edges[1:]):
        mk = (zz >= a) & (zz < b)
        if mk.sum() >= 5:
            W.append(wts(mk) - wl); zb.append(np.exp(np.mean(np.log(zz[mk])))); nb.append(int(mk.sum()))
    W = np.array(W)
    D = W @ y
    CD = W @ C @ W.T
    Q = 10 ** (D / 5)
    sQ = Q * np.log(10) / 5 * np.sqrt(np.diag(CD))
    return np.array(zb), Q, sQ, np.array(nb), int(anchor.sum()), len(idx)


# Response shapes Q(z), each equal to 1 as z -> 0. They are comparison curves laid over the
# register, written in redshift alone; none of them is part of the register itself.
def law_published(z, q, c=0.0):
    return ((1 + z) ** q - 1) / (q * z)


def law_lumfactor(z, q, c=0.0):
    return (1 + z) * ((1 + z) ** q - 1) / (q * z)


def law_saturating(z, q, c):
    return (1 + z) * ((1 + z) ** q - 1) / (q * z * (1 + c * z))


def law_path_may(z, q=0.0, c=0.0):
    """Path departure C(z) = (1+z) ln(1+z) / z, the q -> 0 limit of law_lumfactor (no free parameter)."""
    return (1 + z) * np.log1p(z) / z


LAWS = {
    "Path response  [(1+z)^q - 1] / (q z)": (law_published, 2.102, 0.0, False),
    "Path response x (1+z)": (law_lumfactor, 0.34, 0.0, False),
    "Path response x (1+z), saturating": (law_saturating, 0.98, 0.27, True),
    "Pure path response  (1+z) ln(1+z) / z": (law_path_may, None, 0.0, False),
}


def law_residuals(fn, q, c, z, m, s):
    """Magnitude residuals after the free offset is marginalised (weighted mean removed)."""
    mod = 5 * np.log10(z * fn(z, q, c))
    r = m - mod
    w = 1 / s ** 2
    r = r - np.sum(w * r) / np.sum(w)
    return r


def fit_law(fn, q0, c0, uses_c, z, m, s):
    def res(p):
        q = p[0]; c = p[1] if uses_c else 0.0
        return law_residuals(fn, q, c, z, m, s) / s
    p0 = [q0, c0] if uses_c else [q0]
    lb = [1e-3, -0.9] if uses_c else [1e-3]
    sol = least_squares(res, p0, bounds=(lb, [10, 10] if uses_c else [10]))
    q = sol.x[0]; c = sol.x[1] if uses_c else 0.0
    return q, c


def law_stats(fn, q, c, z, m, s):
    r = law_residuals(fn, q, c, z, m, s)
    return float(np.sum((r / s) ** 2)), float(np.sqrt(np.mean(r ** 2)))


# ----------------------------------------------------------------- time dilation
def time_dilation():
    rows = _csv("stage10_real_published_time_dilation_constraints.csv")
    out = []
    for r in rows:
        out.append(dict(study=r["study"], b=float(r["b"]), err=float(r["sigma_total_quadrature"]),
                        zmin=float(r["z_min"]) if r["z_min"] else None,
                        zmax=float(r["z_max"]) if r["z_max"] else None, n=r["sample_size"]))
    out.append(dict(study="Lewis & Brewer 2023 (quasars)", b=1.28, err=0.285, zmin=None, zmax=None, n="",
                    err_lo=0.29, err_hi=0.28))
    return out


# ----------------------------------------------------------------- ageing rate
def chronometers():
    rows = _csv("stage9_cosmic_chronometer_31pt.csv")
    z = np.array([float(r["z"]) for r in rows])
    H = np.array([float(r["H_km_s_Mpc"]) for r in rows])
    sH = np.array([float(r["sigma_H"]) for r in rows])
    return z, H, sH


def ageing(undo_frame=True, z_anchor=0.2):
    """Rate of redshift change per unit stellar age, |dz/dt| = H (1+z), relative to the local rate.

    Published chronometer values carry a 1/(1+z) frame conversion; undo_frame removes it.
    """
    z, H, sH = chronometers()
    f = (1 + z) if undo_frame else np.ones_like(z)
    R, sR = H * f, sH * f
    a = z < z_anchor
    w = 1 / sR[a] ** 2
    anc = np.sum(w * R[a]) / np.sum(w)
    anc_err = 1 / np.sqrt(np.sum(w))
    return z, R / anc, sR / anc, anc * PER_GYR, anc_err * PER_GYR


# ----------------------------------------------------------------- acoustic angle
ANGLES = dict(
    z=np.array([0.110, 0.235, 0.365, 1.725, 2.225]),
    theta=np.array([19.80, 9.06, 6.33, 1.928, 1.77]),
    err=np.array([1.05, 0.23, 0.22, 0.094, 0.31]),
    source=["de Carvalho+ 2021", "Carvalho+ 2016", "Carvalho+ 2016", "Avila+ 2025", "de Carvalho+ 2018"],
)


def acoustic_angle(anchor_index=0):
    z, th, et = ANGLES["z"], ANGLES["theta"], ANGLES["err"]
    k = anchor_index
    q = th * z / (th[k] * z[k])
    dq = q * np.sqrt((et / th) ** 2 + (et[k] / th[k]) ** 2)
    dq[k] = 0
    return z, q, dq


# ----------------------------------------------------------------- acoustic harmonic
def harmonic(spectrum="TT"):
    rows = [r for r in _csv("planck2018_extrema.csv") if r["spectrum"] == spectrum]
    m0 = 1.0 if spectrum == "TT" else 0.5
    l = np.array([float(r["ell"]) for r in rows]); e = np.array([float(r["ell_err"]) for r in rows])
    mm = m0 + 0.5 * np.arange(len(l))
    q = (l / l[0]) / (mm / m0)
    dq = q * np.sqrt((e / l) ** 2 + (e[0] / l[0]) ** 2); dq[0] = 0
    return mm, q, dq, [r["extremum"] for r in rows]


def harmonic_saturation(m, qinf=1.3486, k=1.447):
    return qinf - (qinf - 1) * m ** (-k)


# ----------------------------------------------------------------- cusp
CUSP = {
    # name: (opening angle, alternative angle, published R_cusp, R_err, [(label, A, B_middle, C)])
    "B2045+265": (34.9, 35.3, 0.501, 0.035, [
        ("VLA 8.5 GHz 1995", 18.4, 9.42, 14.8), ("VLA 14.9 GHz 1995", 15.5, 9.18, 11.8),
        ("VLBA 5.0 GHz 1995", 15.8, 8.09, 8.75), ("VLA 4.9 GHz 1996", 23.40, 12.65, 15.19),
        ("VLA 8.5 GHz 1996", 16.55, 8.90, 10.99), ("VLA 14.9 GHz 1996", 10.69, 5.75, 7.13),
        ("VLA 1.4 GHz 1996", 29.02, 15.73, 19.92), ("MERLIN 5.0 GHz 1997", 16.8, 9.82, 14.8)]),
    "B0712+472": (76.9, 79.8, 0.26, 0.02, [
        ("MERLIN 5 GHz 1995", 15.3, 14.1, 6.9), ("MERLIN 5 GHz 1996", 10.5, 8.5, 4.7),
        ("VLBA 5 GHz 1995", 10.7, 8.8, 3.6), ("VLA 15 GHz 1995", 15.6, 11.6, 5.9)]),
    "B1422+231": (77.0, 74.9, 0.187, 0.006, [
        ("MERLIN 5 GHz 1991", 216.0, 221.0, 115.0), ("VLA 8.4 GHz 1991", 148.0, 153.0, 79.0),
        ("VLBA+Eff 8.4 GHz 1997", 152.0, 164.0, 81.0)]),
}
CUSP_OPTICAL = {"RXJ0911+0551": (69.6, 0.192, 0.011)}


def cusp_q(a, b, c):
    return b / (a + c)


def cusp_r(a, b, c):
    return (a - b + c) / (a + b + c)


def q_from_r(r):
    """Q = F_mid/(F_out1+F_out2) = (1 - R)/(1 + R) when the outer pair outshines the middle."""
    return (1 - r) / (1 + r)


# ----------------------------------------------------------------- rotation (SPARC)
@lru_cache(maxsize=1)
def sparc_tables():
    gal = {}
    lines = open(os.path.join(DATA, "SPARC_Lelli2016c.mrt")).read().splitlines()[98:]
    for ln in lines:
        p = ln.split()
        if len(p) >= 18:
            gal[p[0]] = dict(D=float(p[2]), eD=float(p[3]), fD=int(p[4]), inc=float(p[5]), eInc=float(p[6]), L36=float(p[7]),
                              Rd=float(p[11]), MHI=float(p[13]), Q=int(p[17]))
    rows = []
    for ln in open(os.path.join(DATA, "MassModels_Lelli2016c.mrt")).read().splitlines():
        p = ln.split()
        if len(p) == 10 and p[0] in gal:
            rows.append((p[0],) + tuple(float(x) for x in p[1:9]))
    return gal, rows


def rotation(ud=0.5, ub=0.7, min_inc=30, max_quality=2):
    gal, rows = sparc_tables()
    out = []
    for name, D, R, Vo, eV, Vg, Vd, Vb, _sb in rows:
        g = gal[name]
        if g["inc"] < min_inc or g["Q"] > max_quality or R <= 0 or Vo <= 0:
            continue
        gb = (np.sign(Vg) * Vg ** 2 + ud * Vd ** 2 + ub * Vb ** 2) * 1e6 / (R * KPC)
        go = Vo ** 2 * 1e6 / (R * KPC)
        if gb <= 0:
            continue
        out.append((go / gb, gb, g["fD"], name, R / g["Rd"] if g["Rd"] > 0 else np.nan))
    q = np.array([o[0] for o in out]); gb = np.array([o[1] for o in out]); fd = np.array([o[2] for o in out])
    names = [o[3] for o in out]
    rr = np.array([o[4] for o in out])
    return q, gb, fd, names, len({n for n in names}), rr


def binned_median(gb, q, mask, edges=np.logspace(-13, -8.5, 10), min_n=8):
    xs, ys, lo, hi = [], [], [], []
    for a, b in zip(edges[:-1], edges[1:]):
        s = mask & (gb >= a) & (gb < b)
        if s.sum() >= min_n:
            l = np.log10(q[s])
            xs.append(np.sqrt(a * b)); ys.append(np.median(l))
            lo.append(np.percentile(l, 16)); hi.append(np.percentile(l, 84))
    return np.array(xs), 10 ** np.array(ys), 10 ** np.array(lo), 10 ** np.array(hi)


def binned_median_x(x, q, edges, min_n=8):
    xs, ys, lo, hi = [], [], [], []
    for a, b in zip(edges[:-1], edges[1:]):
        s = (x >= a) & (x < b)
        if s.sum() >= min_n:
            l = np.log10(q[s])
            xs.append(np.sqrt(a * b)); ys.append(np.median(l))
            lo.append(np.percentile(l, 16)); hi.append(np.percentile(l, 84))
    return np.array(xs), 10 ** np.array(ys), 10 ** np.array(lo), 10 ** np.array(hi)


def mcgaugh(gb):
    x = G_DAGGER / gb
    return 1 / (1 - np.exp(-1 / np.sqrt(x)))


# ----------------------------------------------------------------- 2D outlines: Q_a = P^2 / A
# Regular polygons built by side doubling (Archimedes): only square roots, no angles.
# Inscribed in a unit circle, a side s gives the side of the doubled polygon as
# sqrt(2 - sqrt(4 - s^2)); the apothem is sqrt(1 - s^2 / 4).
POLYGON_SEEDS = {
    3: np.sqrt(3.0),
    4: np.sqrt(2.0),
    5: np.sqrt((5 - np.sqrt(5.0)) / 2),
    6: 1.0,
}


def polygon_q(n, s):
    apothem = np.sqrt(1 - s * s / 4)
    perimeter = n * s
    area = perimeter * apothem / 2
    return perimeter ** 2 / area


def polygon_doubling(n0, levels):
    n, s = n0, POLYGON_SEEDS[n0]
    out = [(n, polygon_q(n, s))]
    for _ in range(levels):
        s = np.sqrt(2 - np.sqrt(4 - s * s))
        n *= 2
        out.append((n, polygon_q(n, s)))
    return out


def ellipse_q(e, n=20000):
    """Q_a of an ellipse from a fine polygon on its outline.

    Points come from the rational parametrisation x = a(1-u^2)/(1+u^2), y = 2bu/(1+u^2),
    so no angle or series is needed; perimeter is a sum of chords, area the shoelace sum.
    """
    a, b = 1.0, np.sqrt(1 - e * e)
    u = np.linspace(-1, 1, n)
    x = a * (1 - u * u) / (1 + u * u)
    y = 2 * b * u / (1 + u * u)
    x = np.r_[x, -x[-2:0:-1]]
    y = np.r_[y, y[-2:0:-1]]
    xs, ys = np.r_[x, x[0]], np.r_[y, y[0]]
    perimeter = np.hypot(np.diff(xs), np.diff(ys)).sum()
    area = 0.5 * abs(np.sum(xs[:-1] * ys[1:] - xs[1:] * ys[:-1]))
    return perimeter ** 2 / area


# Eccentricities: JPL planetary elements and the JPL Small-Body Database (Volume area projection research).
ORBITS = [
    ("Venus", "Planet", 0.0068), ("Earth", "Planet", 0.0167), ("Mars", "Planet", 0.0934),
    ("Mercury", "Planet", 0.2056), ("Ceres", "Main belt", 0.0796), ("Pluto", "Dwarf / Kuiper belt", 0.2518),
    ("Eris", "Scattered disk", 0.4370), ("Sedna", "Detached", 0.8613), ("Halley", "Periodic comet", 0.9679),
    ("Hale-Bopp", "Long-period comet", 0.9950),
]


def crater_bins(body):
    rows = _csv(f"{body}_crater_bins.csv")
    return [dict(bin=r["diameter_bin"], d=float(r["diameter_midpoint_km"]), n=int(r["count"]),
                 q=float(r["median_Q_a"]), q05=float(r["Q_a_p05"]), q95=float(r["Q_a_p95"])) for r in rows]


# ----------------------------------------------------------------- shared-shape check
def power_fit(x, Q, s):
    """Fit Q = x^p through Q = 1 at x = 1 (straight line through the origin in log-log).

    Returns p, its error, chi-square and the number of points. Errors are propagated to ln Q.
    """
    lx, ly, sy = np.log(x), np.log(Q), s / Q
    w = 1 / sy ** 2
    p = np.sum(w * lx * ly) / np.sum(w * lx * lx)
    ep = 1 / np.sqrt(np.sum(w * lx * lx))
    chi2 = float(np.sum(((ly - p * lx) / sy) ** 2))
    return float(p), float(ep), chi2, len(x)


def common_power_test(sets):
    """One exponent for every register at once: chi-square of the joint fit and its degrees of freedom."""
    lx = np.concatenate([np.log(x) for x, _, _ in sets])
    ly = np.concatenate([np.log(Q) for _, Q, _ in sets])
    sy = np.concatenate([s / Q for _, Q, s in sets])
    w = 1 / sy ** 2
    p = np.sum(w * lx * ly) / np.sum(w * lx * lx)
    return float(p), float(np.sum(((ly - p * lx) / sy) ** 2)), len(lx) - 1


# ----------------------------------------------------------------- relative motion (no fixed point)
C_KMS = 299792.458
# 1 mas/yr at 1 kpc is 4.74047 km/s
K_PM = 4.74047

# Andromeda (M31). Measured: redshift, proper motion, angular size. Distance is a ladder calculation.
M31 = dict(
    l=121.17, b=-21.57,                      # direction on the sky (degrees, Galactic)
    v_helio=-300.0, v_helio_e=4.0,           # line-of-sight Doppler, km/s (McConnachie 2012)
    pm_ra=48.98, pm_ra_e=10.47,              # Gaia EDR3 proper motion, µas/yr (Salomon et al. 2021)
    pm_dec=-36.85, pm_dec_e=8.03,
    theta_deg=3.17,                          # optical extent D25 (degrees)
)
# published distances (kpc): the value every speed and size depends on
M31_DISTANCES = [
    ("Eclipsing binaries (Vilardell 2010)", 744, 33),
    ("Cepheids (Riess 2012)", 752, 27),
    ("Cepheids (Li 2021)", 761, 11),
    ("Tip of the red giant branch (McConnachie 2005)", 785, 25),
]
# Sun's motion relative to nearby stars (km/s, Schönrich 2010); the Galaxy's rotation speed V_c is added to V
SUN_UVW = (11.1, 12.24, 7.25)

# whole-sky dipoles, Galactic (l, b) in degrees
CMB_DIPOLE = dict(l=264.021, b=48.253, dT_mK=3.3621, T0_K=2.7255)        # Planck 2018
QUASAR_DIPOLE = dict(l=238.2, b=28.8, D=0.01554, D_expected=0.0072, sigma=4.9)  # CatWISE, Secrest 2021


def m31_pm_total():
    """Total proper motion and its error (µas/yr), from the two measured components."""
    a, b = M31["pm_ra"], M31["pm_dec"]
    mu = np.hypot(a, b)
    e = np.hypot(a * M31["pm_ra_e"], b * M31["pm_dec_e"]) / mu
    return float(mu), float(e)


def m31_transverse(d_kpc):
    """Sideways speed (km/s) that the measured proper motion becomes once a distance is chosen."""
    mu, e = m31_pm_total()
    d = np.asarray(d_kpc, float)
    return K_PM * mu * 1e-3 * d, K_PM * e * 1e-3 * d


def m31_galactocentric_radial(v_c):
    """Line-of-sight speed after removing the Sun's assumed orbit. Only v_helio is measured."""
    l, b = np.radians(M31["l"]), np.radians(M31["b"])
    U, V, W = SUN_UVW
    return M31["v_helio"] + U * np.cos(b) * np.cos(l) + (V + np.asarray(v_c, float)) * np.cos(b) * np.sin(l) + W * np.sin(b)


def looming(d_kpc, sep_deg=1.0):
    """Time to contact and the angular growth rate it implies.

    tau = theta / (dtheta/dt) is pure angle-per-time: no distance enters. Here we run it backwards to show the
    rate a measurement would need to see, for an assumed distance and the measured closing speed.
    Returns tau (Gyr), relative growth per year, growth of a sep_deg separation (µas/yr).
    """
    d_km = np.asarray(d_kpc, float) * KPC / 1e3
    tau_s = d_km / abs(M31["v_helio"])
    tau_yr = tau_s / 3.15576e7
    rel = 1 / tau_yr
    return tau_yr / 1e9, rel, rel * sep_deg * 3.6e9


def sky_angle(l1, b1, l2, b2):
    """Great-circle angle between two sky directions, degrees."""
    l1, b1, l2, b2 = map(np.radians, (l1, b1, l2, b2))
    c = np.sin(b1) * np.sin(b2) + np.cos(b1) * np.cos(b2) * np.cos(l1 - l2)
    return float(np.degrees(np.arccos(np.clip(c, -1, 1))))


def dipole_register():
    """Q = quasar-count dipole / the dipole the CMB-frame speed predicts. Q = 1 if both mark one rest frame.

    The error on the observed amplitude is backed out from the published significance of the excess.
    """
    d = QUASAR_DIPOLE
    s = (d["D"] - d["D_expected"]) / d["sigma"]
    q = d["D"] / d["D_expected"]
    beta = CMB_DIPOLE["dT_mK"] * 1e-3 / CMB_DIPOLE["T0_K"]
    return dict(Q=q, Q_e=s / d["D_expected"], beta=beta, v_kms=beta * C_KMS,
                offset_deg=sky_angle(CMB_DIPOLE["l"], CMB_DIPOLE["b"], d["l"], d["b"]))


# ----------------------------------------------------------------- light and matter in one system
# The Sun's mass written as a time, G M_sun / c^3 (seconds). Masses below are in these units; every register
# here is a ratio, so this unit cancels.
T_SUN = 4.925490947e-6

# S2 around the Galactic centre. f scales the extra redshift at closest approach (gravitational shift plus the
# shift from sideways motion) against the value predicted from the orbit's own Doppler swing. f = 1 is the ideal.
S2_REDSHIFT = [
    # study, f, statistical error, systematic error
    ("GRAVITY 2018 (VLT)", 0.90, 0.09, 0.15),
    ("Keck, Do et al. 2019", 0.88, 0.17, 0.0),
    ("GRAVITY 2019 (VLT, more 2018 data)", 0.97, 0.05, 0.05),
]
S2_ORBIT = dict(v_peri_kms=7650.0, e=0.88466)   # orbital speed at closest approach (Doppler swing plus sky track) and orbit shape (GRAVITY 2018)


def s2_predicted_shift():
    """Extra redshift at closest approach predicted from the swing alone (km/s): gravitational part, sideways-motion part.

    For an orbit of eccentricity e, at closest approach the gravitational shift is beta^2/(1+e) and the sideways
    (transverse Doppler) shift is beta^2/2, where beta is the orbital swing as a fraction of c. Both are frequency ratios.
    """
    b = S2_ORBIT["v_peri_kms"] / C_KMS
    grav = b * b / (1 + S2_ORBIT["e"]) * C_KMS
    side = b * b / 2 * C_KMS
    return grav, side


def s2_register():
    """f for each study with its combined error."""
    return [(s, f, float(np.hypot(a, b))) for s, f, a, b in S2_REDSHIFT]


# Hulse-Taylor binary pulsar PSR B1913+16, timing only (Weisberg & Huang 2016, Table 2).
HULSE_TAYLOR = dict(
    Pb_d=0.322997448918,            # orbital period (days)
    e=0.6171340,                    # orbit shape
    wdot=4.226585, wdot_e=0.000004, # turn of the orbit (degrees per year): matter register
    gamma_s=4.307e-3, gamma_e=0.004e-3,   # clock slowing and speeding around the orbit (s): light register
    pbdot_obs=-2.423e-12, pbdot_obs_e=0.001e-12,      # measured shrinking of the period (s/s)
    pbdot_gal=-2.398e-12, pbdot_gal_e=0.004e-12,      # after removing the Galaxy's pull, which needs a distance
)


def _pulsar_pk(Pb_d, e, wdot, gamma_s):
    """Masses from the orbit's turn and the clock term, then the period shrink they predict.

    The only pi here is 2*pi/Pb, which turns one orbit into one full turn in radians: a unit, not a limit.
    """
    n = 2 * np.pi / (Pb_d * 86400.0)
    wd = np.deg2rad(wdot) / (365.25 * 86400.0)
    M = (wd * (1 - e ** 2) / (3 * n ** (5 / 3))) ** 1.5 / T_SUN
    k = gamma_s / (e * n ** (-1 / 3) * T_SUN ** (2 / 3) * M ** (-4 / 3))
    m2 = (-M + np.sqrt(M * M + 4 * k)) / 2
    m1 = M - m2
    fe = (1 + 73 / 24 * e ** 2 + 37 / 96 * e ** 4) / (1 - e ** 2) ** 3.5
    pbdot = -192 * np.pi / 5 * n ** (5 / 3) * fe * T_SUN ** (5 / 3) * m1 * m2 * M ** (-1 / 3)
    return M, m1, m2, pbdot


def hulse_taylor_register(n_draws=20000, seed=1):
    """Q = measured period shrink / shrink predicted from the turn and the clock term. Errors by resampling."""
    p = HULSE_TAYLOR
    M, m1, m2, pred = _pulsar_pk(p["Pb_d"], p["e"], p["wdot"], p["gamma_s"])
    rng = np.random.default_rng(seed)
    _, _, _, draws = _pulsar_pk(p["Pb_d"], p["e"], p["wdot"] + p["wdot_e"] * rng.standard_normal(n_draws),
                                p["gamma_s"] + p["gamma_e"] * rng.standard_normal(n_draws))
    out = {}
    for key, obs, oe in [("raw", p["pbdot_obs"], p["pbdot_obs_e"]), ("gal", p["pbdot_gal"], p["pbdot_gal_e"])]:
        q = obs / draws
        out[key] = (float(obs / pred), float(np.hypot(q.std(), oe / abs(obs))))
    return dict(m1=float(m1), m2=float(m2), pbdot_pred=float(pred), **out)


# Double pulsar PSR J0737-3039A/B (Kramer et al. 2006): the delay as light passes the companion, against the value
# predicted from the orbit's turn and the two pulsars' orbit sizes.
DOUBLE_PULSAR_S = (0.99987, 0.00050)


def light_matter_table():
    """One row per system: register, Q, error, what it compares."""
    ht = hulse_taylor_register()
    rows = [dict(system=s, register="S2 extra redshift / swing²", Q=f, err=e, compares="light shift against orbital swing")
            for s, f, e in s2_register()]
    rows.append(dict(system="Hulse-Taylor pulsar (raw)", register="period shrink / predicted", Q=ht["raw"][0], err=ht["raw"][1],
                     compares="clock term and orbit turn against orbit shrink"))
    rows.append(dict(system="Hulse-Taylor pulsar (Galaxy's pull removed)", register="period shrink / predicted", Q=ht["gal"][0],
                     err=ht["gal"][1], compares="same, after a distance-based correction"))
    rows.append(dict(system="Double pulsar", register="light delay shape / predicted", Q=DOUBLE_PULSAR_S[0], err=DOUBLE_PULSAR_S[1],
                     compares="light passing the companion against orbit turn and sizes"))
    return rows


# ----------------------------------------------------------------- gravity register: departure from G
# Q_G = the pull a system shows / the pull its own matter gives with the one G measured in the lab.
# The ideal is one G everywhere. x is the pull from the matter alone (m/s^2). In galaxies that number is built
# from light and gas with an assumed mass-to-light ratio, and the catalog distance cancels out of it.
GM_SUN = T_SUN * (C_KMS * 1e3) ** 3          # m^3/s^2, from the planets' orbits
R_SUN = 6.957e8                               # m
AU_M = 1.495978707e11                         # m (radar)


def _pulsar_pull(Pb_d, M_sun_units):
    """Pull at the orbit of a binary pulsar from its period and total mass (Kepler's third law)."""
    GM = GM_SUN * M_sun_units
    Pb = Pb_d * 86400.0
    a = (GM * (Pb / (2 * np.pi)) ** 2) ** (1 / 3)
    return GM / a ** 2


def gravity_compact():
    """Systems where both sides are weighed by gravity itself: Q_G = 1 means one G holds there."""
    ht = hulse_taylor_register()
    g_sun = lambda r_m: GM_SUN / r_m ** 2
    rows = [
        ("Cassini light delay, 1.6 solar radii", g_sun(1.6 * R_SUN), 1 + 1.05e-5, 1.15e-5, "Solar System"),
        ("Radio light bending, 6–56 solar radii", g_sun(17.7 * R_SUN), 0.99992, 0.000075, "Solar System"),
        ("Mercury's orbit turning", g_sun(0.387 * AU_M), 1.000023, 0.000020, "Solar System"),
        ("Starlight bending (Hipparcos), ~1 AU", g_sun(0.86 * AU_M), 0.9985, 0.0015, "Solar System"),
        ("Hulse–Taylor pulsar (Galaxy's pull removed)", _pulsar_pull(HULSE_TAYLOR["Pb_d"], ht["m1"] + ht["m2"]),
         ht["gal"][0], ht["gal"][1], "Binary pulsars"),
        ("Double pulsar", _pulsar_pull(0.10225156248, 1.3381 + 1.2489), DOUBLE_PULSAR_S[0], DOUBLE_PULSAR_S[1], "Binary pulsars"),
        ("S2 at closest approach (Galactic centre)", 4.30e6 * GM_SUN / (119.5 * AU_M) ** 2, S2_REDSHIFT[-1][1],
         float(np.hypot(*S2_REDSHIFT[-1][2:])), "Galactic centre"),
    ]
    return rows


def gravity_galaxies(ud=0.5, ub=0.7, min_inc=30, max_quality=2):
    """Q_G at every radius of every SPARC galaxy, against the pull of its visible matter."""
    q, gb, fd, names, ng, rr = rotation(ud, ub, min_inc, max_quality)
    return q, gb, names, ng


def gravity_readings(gb, q, edges=np.logspace(-12.5, -8.5, 17)):
    """Where the binned median of Q_G crosses 1.5 and 2, and its slope in the thinnest matter.

    These are readings of the register, not constants put in.
    """
    x, y, lo, hi = binned_median_x(gb, q, edges)
    lx, ly = np.log10(x), np.log10(y)
    out = {}
    for level in (1.5, 2.0):
        i = np.where((ly[:-1] - np.log10(level)) * (ly[1:] - np.log10(level)) <= 0)[0]
        if len(i):
            j = i[-1]
            f = (np.log10(level) - ly[j]) / (ly[j + 1] - ly[j])
            out[level] = float(10 ** (lx[j] + f * (lx[j + 1] - lx[j])))
    thin = gb < 1e-11
    out["slope"] = float(np.polyfit(np.log10(gb[thin]), np.log10(q[thin]), 1)[0])
    return x, y, lo, hi, out


# ----------------------------------------------------------------- mass: a reading built from measurements and ideals
# No mass here is read off an instrument. Each one is a measured part (angles, times, frequency shifts, fluxes)
# multiplied by assumed parts (a distance, a shape, a calibration). Masses are in solar masses: every recipe divides by
# the Sun's G*M, which the planets' orbits give to about ten digits, so G itself cancels. Only a mass in kilograms needs G.
G_LAB = (6.67430e-11, 6.67191e-11, 6.67545e-11)  # CODATA 2018; lowest and highest single lab results (Rosi 2014, Quinn 2013)
M_SUN_KG = GM_SUN / G_LAB[0]
RG_SUN = GM_SUN / (C_KMS * 1e3) ** 2             # the Sun's mass written as a length, G M / c^2 (m)
MPC_M = 3.0857e22
DAY_S = 86400.0
YEAR_S = 365.25 * DAY_S

# S2 orbit (GRAVITY 2020, A&A 636, L5): angular half-size of the orbit on the sky and its period.
S2_ANGLE_MAS = (125.058, 0.041)
S2_PERIOD_YR = (16.0455, 0.0013)
S2_FIRST_YEAR = 1992
# Distance to the Galactic centre from different teams (pc). Each one is itself fit from the same orbits plus an ideal ellipse.
GC_DISTANCES = [
    ("Keck, Do et al. 2019", 7946.0),
    ("Masers, Reid et al. 2019", 8150.0),
    ("GRAVITY 2019", 8178.0),
    ("GRAVITY 2020", 8246.7),
    ("GRAVITY 2021", 8275.0),
]


def mass_sgr_a(d_pc):
    """Kepler's ratio in Earth-orbit units: a^3 / P^2 with a = angle (arcsec) x distance (pc) in AU. Solar masses."""
    th = S2_ANGLE_MAS[0] / 1000.0
    return th ** 3 * d_pc ** 3 / S2_PERIOD_YR[0] ** 2


def sgr_a_measured_part():
    """The distance-free reading: angle^3 / period^2 (arcsec^3 / yr^2) and its fractional error."""
    th, P = S2_ANGLE_MAS[0] / 1000.0, S2_PERIOD_YR[0]
    err = np.hypot(3 * S2_ANGLE_MAS[1] / S2_ANGLE_MAS[0], 2 * S2_PERIOD_YR[1] / S2_PERIOD_YR[0])
    return th ** 3 / P ** 2, float(err)


# M87*: one ring angle (EHT 2019 Paper I/VI; 2018 campaign, EHT 2024). The ring is turned into a mass by a shape
# factor alpha = ring diameter / (G M / D c^2). A perfect circular shadow of a non-spinning hole gives 2*sqrt(27) = 10.39;
# EHT calibrated 11.0 from simulated images. Then a distance.
M87_RING = [("EHT 2017", 42.0, 3.0), ("EHT 2018", 43.3, 2.3)]
M87_ALPHA_IDEAL = 2 * np.sqrt(27.0)
M87_ALPHA = (11.0, 10.0, 12.0)
M87_D_MPC = (16.8, 16.0, 17.6)
# Other recipes for the same object, rescaled to 16.8 Mpc (mass goes as distance for these methods).
M87_OTHER = [
    ("Gas motions (Walsh et al. 2013)", 3.5e9 * 16.8 / 17.9, 0.9e9 * 16.8 / 17.9, 0.7e9 * 16.8 / 17.9),
    ("Star motions (Liepold et al. 2023)", 5.37e9, 0.37e9, 0.25e9),
    ("Star motions (Gebhardt et al. 2011)", 6.6e9 * 16.8 / 17.9, 0.4e9 * 16.8 / 17.9, 0.4e9 * 16.8 / 17.9),
    ("Ring angle (EHT 2019)", 6.5e9, 0.7e9, 0.7e9),
]


def mass_m87(ring_uas, alpha, d_mpc):
    theta_g = ring_uas / alpha * np.pi / (180 * 3600e6)   # radians; the pi only converts degrees to radians
    return theta_g * d_mpc * MPC_M / RG_SUN


# Quasar-style reverberation, NGC 5548 (Lu et al. 2016, Table 4): the Hbeta lag in different years, and the virial factor f
# that turns lag x width^2 into a mass. f is not measured in the object; it is calibrated on other galaxies.
NGC5548_LAG_D = (4.17, 24.80)          # shortest and longest Hbeta lag across the campaigns (days)
NGC5548_MEAN_MASS = (8.39e7, 0.72e7)   # mean over campaigns with f = 6.3
NGC5548_WIDTH = 2100.0                 # km/s, a round line width that gives that mean mass with a 15-day lag and f = 6.3
VIRIAL_F = [("Graham et al. 2011", 2.8), ("Grier et al. 2013", 4.3), ("Onken et al. 2004", 5.5), ("Ho & Kim 2014", 6.3)]


def mass_reverb(lag_d, width_kms, f):
    return f * (C_KMS * 1e3 * lag_d * DAY_S) * (width_kms * 1e3) ** 2 / GM_SUN


def sparc_galaxy(name):
    """Last measured radius of one SPARC galaxy: catalog distance, inclination, rotation and light."""
    gal, rows = sparc_tables()
    g = gal[name]
    last = [r for r in rows if r[0] == name][-1]
    return dict(name=name, D=g["D"], eD=g["eD"], inc=g["inc"], eInc=g["eInc"], L36=g["L36"], MHI=g["MHI"],
                R_kpc=last[2], V=last[3], eV=last[4])


def galaxy_mass(gx, inc, d_mpc, ml=0.5):
    """Mass inside the last radius from motion, and the mass of the visible light and gas.

    Measured: the line-of-sight Doppler swing v sin(i) and the angle R/D on the sky. Assumed: the tilt i (from the
    outline, taken as a perfect circle seen at an angle), the distance, circular orbits in a steady state, and a
    mass-to-light ratio. Light gives L ~ flux x D^2; motion gives M ~ v^2 x angle x D.
    """
    vlos = gx["V"] * np.sin(np.deg2rad(gx["inc"]))
    v = vlos / np.sin(np.deg2rad(inc))
    R = gx["R_kpc"] * d_mpc / gx["D"] * KPC
    m_motion = (v * 1e3) ** 2 * R / GM_SUN
    k = (d_mpc / gx["D"]) ** 2
    m_visible = (ml * gx["L36"] + 1.33 * gx["MHI"]) * 1e9 * k
    return dict(v=v, vlos=vlos, R_kpc=R / KPC, motion=m_motion, visible=m_visible)


def cycles_seen():
    """How much of one full turn of the motion behind each mass has been watched. The periods are themselves calculations."""
    gx = sparc_galaxy("NGC3198")
    gm = galaxy_mass(gx, gx["inc"], gx["D"])
    t_gal = 2 * np.pi * gm["R_kpc"] * KPC / (gm["v"] * 1e3) / YEAR_S
    m87 = mass_m87(42.0, 11.0, 16.8)
    t_ring = 2 * np.pi * (np.sqrt(27.0) / 2 * 2) ** 1.5 * m87 * T_SUN / DAY_S   # gas orbit near the ring, days
    lag_s = 15 * DAY_S
    t_blr = 2 * np.pi * C_KMS * lag_s / NGC5548_WIDTH / YEAR_S
    return [
        ("Sun: Mercury, by radar and spacecraft since 1964", (2026 - 1964) / 0.2408, "orbits"),
        ("Sgr A*: the star S2, since " + str(S2_FIRST_YEAR), (2026 - S2_FIRST_YEAR) / S2_PERIOD_YR[0], "orbits"),
        ("M87*: gas near the ring, one week of observing", 7 / t_ring, "orbits"),
        ("NGC 5548: broad-line gas, one season (~150 days)", 150 / 365.25 / t_blr, "orbits"),
        ("NGC 3198: outer disk, ~100 years of telescopes", 100 / t_gal, "orbits"),
    ]


def mass_budget():
    """For each object: the spread from the measured part and from each assumed part, as a factor (high / low)^(1/2)."""
    out = [("Sun (in kg)", "measured: G·M from planets", 1 + 1e-10),
           ("Sun (in kg)", "assumed: which lab value of G", np.sqrt(G_LAB[2] / G_LAB[1]))]
    _, e = sgr_a_measured_part()
    ds = [d for _, d in GC_DISTANCES]
    out.append(("Sgr A*", "measured: angle³ / period²", 1 + e))
    out.append(("Sgr A*", "assumed: distance", np.sqrt(mass_sgr_a(max(ds)) / mass_sgr_a(min(ds)))))
    out.append(("M87*", "measured: ring angle", np.sqrt(45.0 / 39.0)))
    out.append(("M87*", "assumed: ring-to-mass shape factor", np.sqrt(M87_ALPHA[2] / M87_ALPHA[1])))
    out.append(("M87*", "assumed: distance", np.sqrt(M87_D_MPC[2] / M87_D_MPC[1])))
    ms = [m for _, m, _, _ in M87_OTHER]
    out.append(("M87*", "assumed: which recipe (gas, stars, ring)", np.sqrt(max(ms) / min(ms))))
    out.append(("NGC 5548", "measured: lag × width² (mean over years)", 1 + NGC5548_MEAN_MASS[1] / NGC5548_MEAN_MASS[0]))
    out.append(("NGC 5548", "changes: lag in different years", np.sqrt(NGC5548_LAG_D[1] / NGC5548_LAG_D[0])))
    fs = [f for _, f in VIRIAL_F]
    out.append(("NGC 5548", "assumed: virial factor f", np.sqrt(max(fs) / min(fs))))
    gx = sparc_galaxy("NGC3198")
    out.append(("NGC 3198", "measured: Doppler swing", 1 + 2 * gx["eV"] / gx["V"]))
    lo = galaxy_mass(gx, gx["inc"] + gx["eInc"], gx["D"])["motion"]; hi = galaxy_mass(gx, gx["inc"] - gx["eInc"], gx["D"])["motion"]
    out.append(("NGC 3198", "assumed: tilt from a circular outline", np.sqrt(hi / lo)))
    out.append(("NGC 3198", "assumed: distance", np.sqrt((gx["D"] + gx["eD"]) / (gx["D"] - gx["eD"]))))
    return out


# ------------------------------------------------- bubbles: where a wind meets its surroundings
MU0 = 4e-7 * np.pi
K_B = 1.380649e-23
M_P = 1.67262e-27
# Planetary magnetopauses: distance from the Sun (AU, radar), equatorial surface field (nT),
# observed nose distance range (planet radii, spacecraft crossings). Bagenal (2013) Table; Mercury from Winslow et al. (2013).
MAGNETOPAUSES = [
    ("Mercury", 0.387, 195.0, 1.40, 1.60),
    ("Earth", 1.000, 30600.0, 8.0, 12.0),
    ("Jupiter", 5.20, 428000.0, 63.0, 92.0),
    ("Saturn", 9.54, 21000.0, 22.0, 27.0),
    ("Uranus", 19.2, 23000.0, 17.0, 19.0),
    ("Neptune", 30.1, 14000.0, 23.0, 26.0),
]
# Voyager in-situ crossings (AU) and year: termination shock and heliopause
VOYAGER = [
    ("Voyager 1", "termination shock", 94.0, 2004.96, "north"),
    ("Voyager 2", "termination shock", 83.7, 2007.66, "south"),
    ("Voyager 1", "heliopause", 121.6, 2012.65, "north"),
    ("Voyager 2", "heliopause", 119.0, 2018.84, "south"),
]


def magnetopause_ideal(p_1au_npa, d_au, b_nt, f=2.0):
    """Nose distance (planet radii) where the planet's compressed dipole field pressure equals the wind's push.

    (f B0)^2 / (2 mu0) * r^-6 = P_wind, with P_wind = P(1 AU) / d^2. f is the assumed field compression at the edge.
    """
    p = p_1au_npa * 1e-9 / d_au ** 2
    b = b_nt * 1e-9
    return ((f * b) ** 2 / (2 * MU0 * p)) ** (1 / 6)


def magnetopause_register(p_1au_npa=2.0, f=2.0):
    rows = []
    for name, d, b, lo, hi in MAGNETOPAUSES:
        r0 = magnetopause_ideal(p_1au_npa, d, b, f)
        mid = 0.5 * (lo + hi)
        rows.append(dict(body=name, d_au=d, ideal=r0, measured=mid, lo=lo, hi=hi, Q=mid / r0, err=0.5 * (hi - lo) / r0))
    return rows


def outside_pressure(b_nt=0.5, n_cm3=0.1, t_k=7500.0, v_kms=25.4):
    """Push from the local interstellar gas on the heliosphere, in Pa: field + heat (ions and electrons) + oncoming flow (ions)."""
    n = n_cm3 * 1e6
    mag = (b_nt * 1e-9) ** 2 / (2 * MU0)
    heat = 2 * n * K_B * t_k
    ram = n * M_P * (v_kms * 1e3) ** 2
    return dict(field=mag, heat=heat, flow=ram, total=mag + heat + ram)


def heliosphere_ideal(p_1au_npa, p_out_pa):
    """Distance (AU) where the wind's push, falling as 1/d^2 from its 1 AU value, equals the outside push."""
    return np.sqrt(p_1au_npa * 1e-9 / p_out_pa)


def two_wind_surface(eta, n=600):
    """Where two winds meet. Star 1 (stronger) at x=0, star 2 at x=1; eta = (Mdot v)_2 / (Mdot v)_1 <= 1.

    Returns the equal-push surface (an Apollonius circle; closed) and the momentum-carrying surface of
    Canto, Raga & Wilkin (1996): theta1 cot theta1 = 1 + eta (theta2 cot theta2 - 1), R = sin theta2 / sin(theta1+theta2).
    """
    from scipy.optimize import brentq
    k = np.sqrt(eta)
    nose = 1 / (1 + k)                       # distance of the meeting point from star 1, on the line between them
    phi = np.linspace(0, 2 * np.pi, 400)
    if abs(1 - k) < 1e-6:
        circ = (np.full(2, 0.5), np.array([-3.0, 3.0]))
    else:
        xc, rc = 1 / (1 - k ** 2), k / (1 - k ** 2)
        circ = (xc + rc * np.cos(phi), rc * np.sin(phi))
    tc = lambda t: t / np.tan(t) if t > 1e-9 else 1.0
    xs, ys = [nose], [0.0]
    theta2_last = 0.0
    for t2 in np.linspace(1e-4, np.pi - 1e-4, n):
        rhs = 1 + eta * (tc(t2) - 1)
        try:
            t1 = brentq(lambda t: tc(t) - rhs, 1e-9, np.pi - 1e-9)
        except ValueError:
            break
        if t1 + t2 >= np.pi - 1e-3:
            break
        r = np.sin(t2) / np.sin(t1 + t2)
        xs.append(r * np.cos(t1)); ys.append(r * np.sin(t1))
        theta2_last = t2
    xs, ys = np.array(xs), np.array(ys)
    keep = np.hypot(xs, ys) < 6
    open_half_angle = np.degrees(np.pi - theta2_last)   # cone half-angle around star 2, seen from far away
    return dict(nose=nose, circle=circ, flow=(xs[keep], ys[keep]), cone_deg=open_half_angle)


# ----------------------------------------------------------- belts: orbital period ratios
RESONANCES_J = [("3:1", 1 / 3, "gap"), ("5:2", 2 / 5, "gap"), ("7:3", 3 / 7, "gap"), ("2:1", 1 / 2, "gap"),
                ("3:2", 2 / 3, "clump (Hildas)"), ("1:1", 1.0, "clump (Trojans)")]
RESONANCES_N = [("1:1", 1.0, "clump (Neptune Trojans)"), ("3:2", 1.5, "clump (Plutinos)"), ("2:1", 2.0, "clump"),
                ("5:2", 2.5, "clump")]


@lru_cache(maxsize=1)
def period_ratio_bins():
    rows = _csv("asteroid_period_ratio_bins.csv")
    out = {}
    for planet in ("Jupiter", "Neptune"):
        r = [x for x in rows if x["planet"] == planet]
        lo = np.array([float(x["lo"]) for x in r]); hi = np.array([float(x["hi"]) for x in r])
        out[planet] = (0.5 * (lo + hi), np.array([int(x["count"]) for x in r]), hi[0] - lo[0])
    return out


def resonance_readings(planet="Jupiter"):
    """Where each gap or clump actually sits, read from the counts, compared with the exact whole-number ratio."""
    c, n, w = period_ratio_bins()[planet]
    table = RESONANCES_J if planet == "Jupiter" else RESONANCES_N
    out = []
    for lab, r, kind in table:
        half = 0.006 if planet == "Jupiter" else 0.03
        m = (c > r - half) & (c < r + half)
        if m.sum() < 3 or n[m].sum() == 0:
            continue
        if kind == "gap":
            loc = c[m][np.argmin(n[m])]
            depth = n[m].min() / np.median(n[(c > r - 4 * half) & (c < r + 4 * half)])
        else:
            loc = np.sum(c[m] * n[m]) / n[m].sum()
            depth = n[m].max() / max(np.median(n[(c > r - 4 * half) & (c < r + 4 * half)]), 1)
        out.append(dict(ratio=lab, exact=r, kind=kind, found=loc, Q=loc / r, bin_Q=w / r, count_ratio=depth))
    return out
