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
        ("Guy, J., et al. (2007). SALT2: using distant supernovae to improve the use of Type Ia supernovae as distance indicators. *Astronomy & Astrophysics*, 466, 11. §1: the flux normalization is free, so training needs no distances and no prior on cosmology.",
         "https://doi.org/10.1051/0004-6361:20066930"),
        ("Scolnic, D. M., et al. (2018). The complete light-curve sample of spectroscopically confirmed SNe Ia from Pan-STARRS1 and cosmological constraints from the combined Pantheon sample. *The Astrophysical Journal*, 859, 101. The 40 binned Pantheon points.",
         "https://doi.org/10.3847/1538-4357/aab9bb"),
    ]),
    ("Time dilation", [
        ("White, R. M. T., et al. (2024). The Dark Energy Survey Supernova Program: Slow supernovae show cosmological time dilation out to z ~ 1. *Monthly Notices of the Royal Astronomical Society*, 533, 3365–3378. Also the summary used for Goldhaber et al. (2001).",
         "https://doi.org/10.1093/mnras/stae2030"),
        ("Blondin, S., et al. (2008). Time dilation in Type Ia supernova spectra at high redshift. *The Astrophysical Journal*, 682, 724–736.",
         "https://doi.org/10.1086/589568"),
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
    ("Shapes and craters", [
        ("Robbins, S. J. (2018). Lunar Crater Database v1 (1,296,796 craters). USGS Astrogeology Science Center. Described in Robbins (2019), *Journal of Geophysical Research: Planets*, 124, 871–892, doi:10.1029/2018JE005592.",
         "https://astrogeology.usgs.gov/search/map/moon_crater_database_v1_robbins"),
        ("Robbins, S. J., & Hynek, B. M. (2012). A new global database of Mars impact craters ≥1 km: 1. Database creation, properties, and parameters. *Journal of Geophysical Research*, 117, E05004. Data: 2020 release, 385,049 craters, from craters.sjrdesign.net.",
         "https://doi.org/10.1029/2011JE003966"),
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
