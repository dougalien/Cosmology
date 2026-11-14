"""Published sources for every register, in one place.

Each entry is (citation, link). Citations use *asterisks* for italics. The same list is shown on the
app's Sources page and on the Earth Systems Arcade sources page (dougalien.github.io/geo-tools/citations/).
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
    ("Flux dimming: DES 5-year", [
        ("DES Collaboration (2024). The Dark Energy Survey: Cosmology results with ~1500 new high-redshift Type Ia supernovae using the full 5-year dataset. *The Astrophysical Journal Letters*, 973, L14.",
         "https://doi.org/10.3847/2041-8213/ad6f9f"),
        ("Popovic, B., et al. (2026). The Dark Energy Survey Supernova Program: A reanalysis of cosmology results with an updated Type Ia supernova calibration (DES-Dovekie). *Monthly Notices of the Royal Astronomical Society*. Data: DES-Dovekie_HD.csv and the STAT+SYS covariance, github.com/des-science/DES-SN5YR.",
         "https://arxiv.org/abs/2511.07517"),
    ]),
    ("Time dilation", [
        ("White, R. M. T., et al. (2024). The Dark Energy Survey Supernova Program: Slow supernovae show cosmological time dilation out to z ~ 1. *Monthly Notices of the Royal Astronomical Society*, 533, 3365–3378. Also the summary used for Goldhaber et al. (2001).",
         "https://doi.org/10.1093/mnras/stae2030"),
        ("Blondin, S., et al. (2008). Time dilation in Type Ia supernova spectra at high redshift. *The Astrophysical Journal*, 682, 724–736.",
         "https://doi.org/10.1086/589568"),
        ("Lewis, G. F., & Brewer, B. J. (2023). Detection of the cosmological time dilation of high-redshift quasars. *Nature Astronomy*, 7, 1265–1269.",
         "https://doi.org/10.1038/s41550-023-02029-2"),
    ]),
    ("Aging rate (cosmic chronometers)", [
        ("Bengaly, C., Dantas, M. A., Casarini, L., & Alcaniz, J. (2023). Measuring the Hubble constant with cosmic chronometers: A machine learning approach. *The European Physical Journal C*. Table 1, the 31 H(z) values used here (compiled from Jimenez et al. 2003, Simon et al. 2005, Stern et al. 2010, Moresco et al. 2012, Zhang et al. 2014, Moresco 2015, Moresco et al. 2016 and Ratsimbazafy et al. 2017).",
         "https://doi.org/10.1140/epjc/s10052-023-11734-1"),
        ("Moresco, M., et al. (2012). Improved constraints on the expansion rate of the Universe up to z ~ 1.1 from the spectroscopic evolution of cosmic chronometers. *Journal of Cosmology and Astroparticle Physics*, 2012(08), 006.",
         "https://doi.org/10.1088/1475-7516/2012/08/006"),
        ("Jimenez, R., & Loeb, A. (2002). Constraining cosmological parameters based on relative galaxy ages. *The Astrophysical Journal*, 573, 37–42. The chronometer method.",
         "https://doi.org/10.1086/340549"),
    ]),
    ("Acoustic angle", [
        ("de Carvalho, E., Bernui, A., Avila, F., Novaes, C. P., & Nogueira-Cavalcante, J. P. (2021). BAO angular scale at z_eff = 0.11 with the SDSS blue galaxies. *Astronomy & Astrophysics*, 649, A20.",
         "https://doi.org/10.1051/0004-6361/202039936"),
        ("Carvalho, G. C., Bernui, A., Benetti, M., Carvalho, J. C., & Alcaniz, J. S. (2016). Baryon acoustic oscillations from the SDSS DR10 galaxies angular correlation function. *Physical Review D*, 93, 023530. The z = 0.235 and 0.365 angles.",
         "https://doi.org/10.1103/PhysRevD.93.023530"),
        ("de Carvalho, E., Bernui, A., Carvalho, G. C., Novaes, C. P., & Xavier, H. S. (2018). Angular baryon acoustic oscillation measure at z = 2.225 from the SDSS quasar survey. *Journal of Cosmology and Astroparticle Physics*, 2018(04), 064.",
         "https://doi.org/10.1088/1475-7516/2018/04/064"),
        ("Avila, F., Bernui, A., Sabogal, M. A., & Nunes, R. C. (2025). High-redshift transverse BAO measurements with the SDSS quasar catalog. arXiv:2510.15650. θ = 1.911° ± 0.062° at z_eff = 1.725.",
         "https://arxiv.org/abs/2510.15650"),
    ]),
    ("Cusp lenses", [
        ("Keeton, C. R., Gaudi, B. S., & Petters, A. O. (2003). Identifying lenses with small-scale structure. I. Cusp lenses. *The Astrophysical Journal*, 598, 138–161. Opening angles and R_cusp (Table B1).",
         "https://doi.org/10.1086/378934"),
        ("Fassnacht, C. D., et al. (1999). B2045+265: A new four-image gravitational lens from CLASS. *The Astronomical Journal*, 117. Table 3, radio fluxes at 8 epochs.",
         "https://arxiv.org/abs/astro-ph/9811167"),
        ("Jackson, N., et al. (1998). B0712+472 radio fluxes (MERLIN, VLBA, VLA), *Monthly Notices of the Royal Astronomical Society*, as tabulated in the JVAS/CLASS lens archive.", None),
        ("Patnaik, A. R., et al. (1992; 1999). B1422+231 radio fluxes: MERLIN 5 GHz and VLA 8.4 GHz (1992); VLBA + Effelsberg 8.4 GHz (1999).", None),
    ]),
    ("Light: departure from the vacuum limit", [
        ("BIPM (2019). *The International System of Units (SI)*, 9th edition. The meter is defined from c = 299,792,458 m/s (adopted 1983, 17th CGPM).",
         "https://www.bipm.org/en/publications/si-brochure"),
        ("Refractive indices at 589 nm: air 1.000293, water 1.3330, BK7 1.5168, diamond 2.4175 (CRC Handbook of Chemistry and Physics; Schott BK7 data sheet).", None),
        ("Hau, L. V., Harris, S. E., Dutton, Z., & Behroozi, C. H. (1999). Light speed reduction to 17 metres per second in an ultracold atomic gas. *Nature*, 397, 594–598.",
         "https://doi.org/10.1038/17561"),
        ("Evenson, K. M., et al. (1972). Speed of light from direct frequency and wavelength measurements of the methane-stabilized laser. *Physical Review Letters*, 29, 1346. Earlier values: Michelson (1879, 1927), Essen (1950), Froome (1958), as summarized in the CODATA history.",
         "https://doi.org/10.1103/PhysRevLett.29.1346"),
    ]),
    ("Premise: no fixed point (the two sky dipoles)", [
        ("Planck Collaboration (2020). Planck 2018 results. I. *Astronomy & Astrophysics*, 641, A1. Table 2: the CMB dipole, 3362.08 µK toward (l, b) = (264.021°, 48.253°).",
         "https://doi.org/10.1051/0004-6361/201833880"),
        ("Secrest, N. J., et al. (2021). A test of the cosmological principle with quasars. *The Astrophysical Journal Letters*, 908, L51. The CatWISE2020 quasar dipole.",
         "https://doi.org/10.3847/2041-8213/abdd40"),
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
        ("Kuhn, J. R., Bush, R., Emilio, M., & Scholl, I. F. (2012). The precise solar shape and its variability. *Science*, 337, 1638–1640. The Sun's flattening: equator-pole radius difference 7.2 ± 0.5 milliarcseconds, about 7.5 × 10⁻⁶.",
         "https://doi.org/10.1126/science.1223231"),
        ("Wadell, H. (1932). Volume, shape, and roundness of rock particles. *The Journal of Geology*, 40(5), 443–451. The shape-ratio idea behind Q_v.",
         "https://doi.org/10.1086/623964"),
    ]),
    ("Ideas from earlier work", [
        ('Osserman, R. (1978). The isoperimetric inequality. *Bulletin of the American Mathematical Society*, 84(6), 1182–1238. Q_a = P²/A is the classical isoperimetric ratio, lowest for a circle.',
         'https://doi.org/10.1090/S0002-9904-1978-14553-4'),
    ]),
]


def page():
    import streamlit as st
    st.header("Sources: the data and papers behind each register")
    st.markdown("Every register divides a published measurement by its ideal. These are the publications and data "
                "files behind each page. The full list for all Dougalien Systems apps is at "
                "[dougalien.github.io/geo-tools/citations/](https://dougalien.github.io/geo-tools/citations/#finite-deformable-geometry).")
    for group, items in SOURCES:
        st.subheader(group)
        st.markdown("\n".join(f"- {c}" + (f" [{u}]({u})" if u else "") for c, u in items))
