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


# Flattening values (equatorial - polar) / equatorial
BODIES = {"Sun": 9e-6, "Earth": 1 / 298.257, "Mars": 0.00589, "Saturn": 0.09796, "Jupiter": 0.06487}


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
            gal[p[0]] = dict(D=float(p[2]), fD=int(p[4]), inc=float(p[5]), Rd=float(p[11]), Q=int(p[17]))
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
