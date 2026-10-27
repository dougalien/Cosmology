"""Published sources for every register, in one place.

Each entry is (citation, link). Citations use *asterisks* for italics. The same list is shown on the
app's Sources page and on the Earth Systems Arcade sources page (geo-tools.netlify.app/citations/).
Values were checked against the papers and data files on 2026-10-27; the paper bibliography is in
Vol. 1 Finite Response Mapping (path_response_redshift_arxiv_v33.tex).
"""

SOURCES = [
    ("Flux dimming (supernovae)", [
        ("Scolnic, D., et al. (2022). The Pantheon+ analysis: The full data set and light-curve release. *The Astrophysical Journal*, 938, 113. Data file Pantheon+SH0ES.dat.",
         "https://doi.org/10.3847/1538-4357/ac8b7a"),
        ("Brout, D., et al. (2022). The Pantheon+ analysis: Cosmological constraints. *The Astrophysical Journal*, 938, 110. Source of the STAT+SYS covariance.",
         "https://doi.org/10.3847/1538-4357/ac8e04"),
        ("Scolnic, D. M., et al. (2018). The complete light-curve sample of spectroscopically confirmed SNe Ia from Pan-STARRS1 and cosmological constraints from the combined Pantheon sample. *The Astrophysical Journal*, 859, 101. The 40 binned Pantheon points.",
         "https://doi.org/10.3847/1538-4357/aab9bb"),
    ]),
    ("Time dilation", [
        ("White, R. M. T., et al. (2024). The Dark Energy Survey Supernova Program: Slow supernovae show cosmological time dilation out to z ~ 1. *Monthly Notices of the Royal Astronomical Society*, 533, 3365–3378. Also the summary used for Goldhaber et al. (2001).",
         "https://doi.org/10.1093/mnras/stae2030"),
        ("Blondin, S., et al. (2008). Time dilation in Type Ia supernova spectra at high redshift. *The Astrophysical Journal*, 682, 724–736.",
         "https://doi.org/10.1086/589568"),
        ("Lewis, G. F., & Brewer, B. J. (2023). Detection of the cosmological time dilation of high-redshift quasars. *Nature Astronomy*, 7, 1265–1269.",
         "https://doi.org/10.1038/s41550-023-02029-2"),
    ]),
    ("Ageing rate (cosmic chronometers)", [
        ("Bengaly, C., Dantas, M. A., Casarini, L., & Alcaniz, J. (2023). Measuring the Hubble constant with cosmic chronometers: A machine learning approach. *The European Physical Journal C*. Table 1, the 31 H(z) values used here (compiled from Jimenez et al. 2003, Simon et al. 2005, Stern et al. 2010, Moresco et al. 2012, Zhang et al. 2014, Moresco 2015, Moresco et al. 2016 and Ratsimbazafy et al. 2017).",
         "https://doi.org/10.1140/epjc/s10052-023-11734-1"),
        ("Moresco, M., et al. (2012). Improved constraints on the expansion rate of the Universe up to z ~ 1.1 from the spectroscopic evolution of cosmic chronometers. *Journal of Cosmology and Astroparticle Physics*, 2012(08), 006.",
         "https://doi.org/10.1088/1475-7516/2012/08/006"),
        ("Jimenez, R., & Loeb, A. (2002). Constraining cosmological parameters based on relative galaxy ages. *The Astrophysical Journal*, 573, 37–42. The chronometer method.",
         "https://doi.org/10.1086/340549"),
    ]),
    ("Acoustic angle and acoustic harmonics", [
        ("de Carvalho, E., Bernui, A., Avila, F., Novaes, C. P., & Nogueira-Cavalcante, J. P. (2021). BAO angular scale at z_eff = 0.11 with the SDSS blue galaxies. *Astronomy & Astrophysics*, 649, A20.",
         "https://doi.org/10.1051/0004-6361/202039936"),
        ("Carvalho, G. C., Bernui, A., Benetti, M., Carvalho, J. C., & Alcaniz, J. S. (2016). Baryon acoustic oscillations from the SDSS DR10 galaxies angular correlation function. *Physical Review D*, 93, 023530. The z = 0.235 and 0.365 angles.",
         "https://doi.org/10.1103/PhysRevD.93.023530"),
        ("de Carvalho, E., Bernui, A., Carvalho, G. C., Novaes, C. P., & Xavier, H. S. (2018). Angular baryon acoustic oscillation measure at z = 2.225 from the SDSS quasar survey. *Journal of Cosmology and Astroparticle Physics*, 2018(04), 064.",
         "https://doi.org/10.1088/1475-7516/2018/04/064"),
        ("Avila, F., Bernui, A., Sabogal, M. A., & Nunes, R. C. (2025). Transverse BAO scale measurement at z_eff = 1.725 with the SDSS quasars catalog. arXiv:2510.15650.",
         "https://arxiv.org/abs/2510.15650"),
        ("Planck Collaboration (2020). Planck 2018 results. I. Overview and the cosmological legacy of Planck. *Astronomy & Astrophysics*, 641, A1. Table 5: positions and amplitudes of the TT, TE and EE peaks and troughs.",
         "https://doi.org/10.1051/0004-6361/201833880"),
    ]),
    ("Cusp lenses", [
        ("Keeton, C. R., Gaudi, B. S., & Petters, A. O. (2003). Identifying lenses with small-scale structure. I. Cusp lenses. *The Astrophysical Journal*, 598, 138–161. Opening angles and R_cusp (Table B1).",
         "https://doi.org/10.1086/378934"),
        ("Fassnacht, C. D., et al. (1999). B2045+265: A new four-image gravitational lens from CLASS. *The Astronomical Journal*, 117. Table 3, radio fluxes at 8 epochs.",
         "https://arxiv.org/abs/astro-ph/9811167"),
        ("Jackson, N., et al. (1998). B0712+472 radio fluxes (MERLIN, VLBA, VLA), *Monthly Notices of the Royal Astronomical Society*, as tabulated in the JVAS/CLASS lens archive.", None),
        ("Patnaik, A. R., et al. (1992; 1999). B1422+231 radio fluxes: MERLIN 5 GHz and VLA 8.4 GHz (1992); VLBA + Effelsberg 8.4 GHz (1999).", None),
    ]),
    ("Galaxy rotation", [
        ("Lelli, F., McGaugh, S. S., & Schombert, J. M. (2016). SPARC: Mass models for 175 disk galaxies with Spitzer photometry and accurate rotation curves. *The Astronomical Journal*, 152, 157. Data files SPARC_Lelli2016c.mrt and MassModels_Lelli2016c.mrt.",
         "https://doi.org/10.3847/0004-6256/152/6/157"),
        ("McGaugh, S. S., Lelli, F., & Schombert, J. M. (2016). Radial acceleration relation in rotationally supported galaxies. *Physical Review Letters*, 117, 201101. The acceleration scale g† = 1.2 × 10⁻¹⁰ m/s².",
         "https://doi.org/10.1103/PhysRevLett.117.201101"),
    ]),
    ("Clock and deflection", [
        ("Pound, R. V., & Snider, J. L. (1965). Effect of gravity on gamma radiation. *Physical Review*, 140, B788.",
         "https://doi.org/10.1103/PhysRev.140.B788"),
        ("Takamoto, M., et al. (2020). Test of general relativity by a pair of transportable optical lattice clocks. *Nature Photonics*, 14, 411.",
         "https://doi.org/10.1038/s41566-020-0619-8"),
        ("Bertotti, B., Iess, L., & Tortora, P. (2003). A test of general relativity using radio links with the Cassini spacecraft. *Nature*, 425, 374.",
         "https://doi.org/10.1038/nature01997"),
    ]),
    ("No fixed point (relative motion)", [
        ("Planck Collaboration (2020). Planck 2018 results. I. *Astronomy & Astrophysics*, 641, A1. Table 2: the CMB dipole, 3362.08 µK toward (l, b) = (264.021°, 48.253°).",
         "https://doi.org/10.1051/0004-6361/201833880"),
        ("Secrest, N. J., et al. (2021). A test of the cosmological principle with quasars. *The Astrophysical Journal Letters*, 908, L51. The CatWISE2020 quasar dipole.",
         "https://doi.org/10.3847/2041-8213/abdd40"),
        ("Salomon, J.-B., Ibata, R., Reylé, C., et al. (2021). The proper motion of Andromeda from Gaia EDR3: Confirming a nearly radial orbit. *Monthly Notices of the Royal Astronomical Society*, 507, 2592.",
         "https://arxiv.org/abs/2012.09204"),
        ("McConnachie, A. W. (2012). The observed properties of dwarf galaxies in and around the Local Group. *The Astronomical Journal*, 144, 4. Andromeda's line-of-sight velocity.",
         "https://doi.org/10.1088/0004-6256/144/1/4"),
        ("Andromeda distances: Vilardell, F., et al. (2010), eclipsing binaries, *Astronomy & Astrophysics*, 509, A70; Riess, A. G., et al. (2012), Cepheids, *The Astrophysical Journal*, 745, 156; Li, S., et al. (2021), Cepheids, *The Astrophysical Journal*, 920, 84; McConnachie, A. W., et al. (2005), tip of the red giant branch, *Monthly Notices of the Royal Astronomical Society*, 356, 979.", None),
        ("Schönrich, R., Binney, J., & Dehnen, W. (2010). Local kinematics and the local standard of rest. *Monthly Notices of the Royal Astronomical Society*, 403, 1829. The Sun's motion (U, V, W).",
         "https://doi.org/10.1111/j.1365-2966.2010.16253.x"),
    ]),
    ("Shapes, orbits and craters", [
        ("Robbins, S. J. (2018). Lunar Crater Database v1 (1,296,796 craters). USGS Astrogeology Science Center. Described in Robbins (2019), *Journal of Geophysical Research: Planets*, 124, 871–892, doi:10.1029/2018JE005592.",
         "https://astrogeology.usgs.gov/search/map/moon_crater_database_v1_robbins"),
        ("Robbins, S. J., & Hynek, B. M. (2012). A new global database of Mars impact craters ≥1 km: 1. Database creation, properties, and parameters. *Journal of Geophysical Research*, 117, E05004. Data: 2020 release, 385,049 craters, from craters.sjrdesign.net.",
         "https://doi.org/10.1029/2011JE003966"),
        ("Orbital eccentricities: NASA/JPL planetary Keplerian elements (J2000) for the planets, and the JPL Small-Body Database for Ceres, Pluto, Eris, Sedna, 1P/Halley and C/1995 O1 (Hale-Bopp), retrieved June 2026.",
         "https://ssd.jpl.nasa.gov/"),
        ("Planet flattening: NASA Planetary Fact Sheet (Earth 1/298.257 is the WGS 84 value).",
         "https://nssdc.gsfc.nasa.gov/planetary/factsheet/"),
        ("Wadell, H. (1932). Volume, shape, and roundness of rock particles. *The Journal of Geology*, 40(5), 443–451. The shape-ratio idea behind Q_v.",
         "https://doi.org/10.1086/623964"),
    ]),
]


def page():
    import streamlit as st
    st.title("Sources")
    st.markdown("Every register divides a published measurement by its ideal. These are the publications and data "
                "files behind each page. The full list for all Dougalien Systems apps is at "
                "[geo-tools.netlify.app/citations](https://geo-tools.netlify.app/citations/#finite-deformable-geometry).")
    for group, items in SOURCES:
        st.subheader(group)
        st.markdown("\n".join(f"- {c}" + (f" [{u}]({u})" if u else "") for c, u in items))
