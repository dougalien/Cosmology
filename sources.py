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
    ("Light and matter together", [
        ("GRAVITY Collaboration (2018). Detection of the gravitational redshift in the orbit of the star S2 near the Galactic centre massive black hole. *Astronomy & Astrophysics*, 615, L15. f = 0.90 ± 0.09 ± 0.15; pericentre speed and eccentricity.",
         "https://doi.org/10.1051/0004-6361/201833718"),
        ("Do, T., et al. (2019). Relativistic redshift of the star S0-2 orbiting the Galactic Center supermassive black hole. *Science*, 365, 664–668. f = 0.88 ± 0.17.",
         "https://doi.org/10.1126/science.aav8137"),
        ("GRAVITY Collaboration (2019). Test of the Einstein equivalence principle near the Galactic Center supermassive black hole. *Physical Review Letters*, 122, 101102. f = 0.97 ± 0.05 ± 0.05 with 2018 data added.",
         "https://arxiv.org/abs/1902.04193"),
        ("Weisberg, J. M., & Huang, Y. (2016). Relativistic measurements from timing the binary pulsar PSR B1913+16. *The Astrophysical Journal*, 829, 55. Table 2 timing parameters.",
         "https://arxiv.org/abs/1606.02744"),
        ("Kramer, M., et al. (2006). Tests of general relativity from timing the double pulsar. *Science*, 314, 97–102. s_obs/s_pred = 0.99987 ± 0.00050.",
         "https://arxiv.org/abs/astro-ph/0609417"),
    ]),
    ("Gravity: departure from G", [
        ("Compact systems reuse the Light and matter together and solar-system sources: Bertotti et al. (2003) Cassini; Lambert & Le Poncin-Lafitte (2009) VLBI; Froeschl\u00e9, Mignard & Arenou (1997) Hipparcos; Park et al. (2017) MESSENGER; Weisberg & Huang (2016); Kramer et al. (2006); GRAVITY (2018, 2019).", None),
        ("Park, R. S., et al. (2017). Precession of Mercury's perihelion from ranging to the MESSENGER spacecraft. *The Astronomical Journal*, 153, 121. \u03b2 \u2212 1 = (\u22122.7 \u00b1 3.9) \u00d7 10\u207b\u2075.",
         "https://doi.org/10.3847/1538-3881/aa5be2"),
        ("Lambert, S. B., & Le Poncin-Lafitte, C. (2009). Determining the relativistic parameter \u03b3 using very long baseline interferometry. *Astronomy & Astrophysics*, 499, 331. \u03b3 = 0.99984 \u00b1 0.00015.",
         "https://arxiv.org/abs/0903.1615"),
        ("Bertotti, B., Iess, L., & Tortora, P. (2003). Cassini radio links (also under Clock and deflection). \u03b3 \u2212 1 = (2.1 \u00b1 2.3) \u00d7 10\u207b\u2075.",
         "https://doi.org/10.1038/nature01997"),
        ("Galaxies: SPARC (Lelli, McGaugh & Schombert 2016), as on the Galaxy rotation page.", None),
    ]),
    ("Mass: a reading", [
        ("GRAVITY Collaboration (2020). Detection of the Schwarzschild precession in the orbit of the star S2 near the Galactic centre massive black hole. *Astronomy & Astrophysics*, 636, L5. S2 orbit: a = 125.058 \u00b1 0.041 mas, P = 16.0455 \u00b1 0.0013 yr; R0 = 8246.7 pc.",
         "https://doi.org/10.1051/0004-6361/202037813"),
        ("Galactic-centre distances: Do, T., et al. (2019), *Science*, 365, 664 (7946 pc); Reid, M. J., et al. (2019), *The Astrophysical Journal*, 885, 131 (8150 pc); GRAVITY Collaboration (2019), *Astronomy & Astrophysics*, 625, L10 (8178 pc); GRAVITY Collaboration (2021), *Astronomy & Astrophysics*, 647, A59 (8275 pc).", None),
        ("Event Horizon Telescope Collaboration (2019). First M87 Event Horizon Telescope results. I and VI. *The Astrophysical Journal Letters*, 875, L1 and L6. Ring diameter 42 \u00b1 3 \u00b5as, \u03b8_g = 3.8 \u00b1 0.4 \u00b5as, shape factor \u03b1 \u2248 11, D = 16.8 \u00b1 0.8 Mpc, M = 6.5 \u00b1 0.7 \u00d7 10\u2079.",
         "https://doi.org/10.3847/2041-8213/ab0ec7"),
        ("Event Horizon Telescope Collaboration (2024). The persistent shadow of the supermassive black hole of M 87. I. *Astronomy & Astrophysics*, 681, A79. 2018 ring 43.3 (+1.5/\u22123.1) \u00b5as; brightness position angle shifted about 30\u00b0.",
         "https://doi.org/10.1051/0004-6361/202347932"),
        ("M87 other recipes: Walsh, J. L., et al. (2013), *The Astrophysical Journal*, 770, 86 (gas, 3.5 \u00d7 10\u2079 at 17.9 Mpc); Gebhardt, K., et al. (2011), *The Astrophysical Journal*, 729, 119 (stars, 6.6 \u00d7 10\u2079 at 17.9 Mpc); Liepold, E. R., et al. (2023), *The Astrophysical Journal Letters*, 945, L35 (stars, 5.37 \u00d7 10\u2079 at 16.8 Mpc).", None),
        ("Lu, K.-X., et al. (2016). Reverberation mapping of the broad-line region in NGC 5548: Evidence for radiation pressure? *The Astrophysical Journal*, 827, 118. Table 4: H\u03b2 lags 4.17\u201324.80 days across campaigns; mean mass (8.39 \u00b1 0.72) \u00d7 10\u2077 with f = 6.3.",
         "https://arxiv.org/abs/1607.08060"),
        ("Virial factor f: Onken, C. A., et al. (2004), *The Astrophysical Journal*, 615, 645 (5.5); Graham, A. W., et al. (2011), *Monthly Notices of the Royal Astronomical Society*, 412, 2211 (2.8); Grier, C. J., et al. (2013), *The Astrophysical Journal*, 773, 90 (4.3); Ho, L. C., & Kim, M. (2014), *The Astrophysical Journal*, 789, 17 (6.3).", None),
        ("G: CODATA 2018 (6.67430 \u00d7 10\u207b\u00b9\u00b9); lowest and highest single lab results Rosi, G., et al. (2014), *Nature*, 510, 518 (6.67191) and Quinn, T., et al. (2013), *Physical Review Letters*, 111, 101102 (6.67545).", None),
        ("Disk galaxies: SPARC (Lelli, McGaugh & Schombert 2016), as on the Galaxy rotation page.", None),
    ]),
    ("Light: departure from the vacuum limit", [
        ("BIPM (2019). *The International System of Units (SI)*, 9th edition. The metre is defined from c = 299,792,458 m/s (adopted 1983, 17th CGPM).",
         "https://www.bipm.org/en/publications/si-brochure"),
        ("Refractive indices at 589 nm: air 1.000293, water 1.3330, BK7 1.5168, diamond 2.4175 (CRC Handbook of Chemistry and Physics; Schott BK7 data sheet).", None),
        ("Malitson, I. H. (1965). Interspecimen comparison of the refractive index of fused silica. *Journal of the Optical Society of America*, 55, 1205. Sellmeier fit used for the glass curve.",
         "https://doi.org/10.1364/JOSA.55.001205"),
        ("Hau, L. V., Harris, S. E., Dutton, Z., & Behroozi, C. H. (1999). Light speed reduction to 17 metres per second in an ultracold atomic gas. *Nature*, 397, 594–598.",
         "https://doi.org/10.1038/17561"),
        ("Pulsar dispersion measures: ATNF Pulsar Catalogue (Manchester et al. 2005, *The Astronomical Journal*, 129, 1993): Crab DM 56.77, J0437−4715 DM 2.64. J0437−4715 parallax distance 156.79 pc: Reardon, D. J., et al. (2016), *Monthly Notices of the Royal Astronomical Society*, 455, 1751.",
         "https://www.atnf.csiro.au/research/pulsar/psrcat/"),
        ("Bertotti, B., Iess, L., & Tortora, P. (2003). A test of general relativity using radio links with the Cassini spacecraft. *Nature*, 425, 374–376.",
         "https://doi.org/10.1038/nature01997"),
        ("Abbott, B. P., et al. (2017). Gravitational waves and gamma-rays from a binary neutron star merger: GW170817 and GRB 170817A. *The Astrophysical Journal Letters*, 848, L13. Speed difference between −3 × 10⁻¹⁵ and +7 × 10⁻¹⁶.",
         "https://doi.org/10.3847/2041-8213/aa920c"),
        ("Abdo, A. A., et al. (2009). A limit on the variation of the speed of light arising from quantum gravity effects. *Nature*, 462, 331–334. GRB 090510.",
         "https://doi.org/10.1038/nature08574"),
        ("Evenson, K. M., et al. (1972). Speed of light from direct frequency and wavelength measurements of the methane-stabilized laser. *Physical Review Letters*, 29, 1346. Earlier values: Michelson (1879, 1927), Essen (1950), Froome (1958), as summarized in the CODATA history.",
         "https://doi.org/10.1103/PhysRevLett.29.1346"),
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
        ("Kuhn, J. R., Bush, R., Emilio, M., & Scholl, I. F. (2012). The precise solar shape and its variability. *Science*, 337, 1638–1640. The Sun's flattening: equator-pole radius difference 7.2 ± 0.5 milliarcseconds, about 7.5 × 10⁻⁶.",
         "https://doi.org/10.1126/science.1223231"),
        ("Wadell, H. (1932). Volume, shape, and roundness of rock particles. *The Journal of Geology*, 40(5), 443–451. The shape-ratio idea behind Q_v.",
         "https://doi.org/10.1086/623964"),
    ]),
]


def page():
    import streamlit as st
    st.title("Sources")
    st.markdown("Every register divides a published measurement by its ideal. These are the publications and data "
                "files behind each page. The full list for all Dougalien Systems apps is at "
                "[dougalien.github.io/geo-tools/citations/](https://dougalien.github.io/geo-tools/citations/#finite-deformable-geometry).")
    for group, items in SOURCES:
        st.subheader(group)
        st.markdown("\n".join(f"- {c}" + (f" [{u}]({u})" if u else "") for c, u in items))
