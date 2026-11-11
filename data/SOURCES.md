# Data sources

All files in `raw/` were downloaded by the author from Our World in Data (OWID) as CSV and uploaded unmodified on 10 November 2026. Only the filenames were changed (an upload prefix was removed). OWID publishes these under CC BY 4.0; each chart page names the original sources, which should be cited alongside OWID.

The chart addresses below are inferred from the downloaded filenames and should be checked against the live site. Exact upstream sources and versions should be copied from each chart page before publication.

| File | OWID chart | Used for | SHA-256 |
|---|---|---|---|
| population.csv | ourworldindata.org/grapher/population | World and country population, 10,000 BCE–2023 (HYDE 3.3 before 1800, Gapminder 1800–1949, UN WPP 2024 after, per OWID) | 6e72d4ffe8f0e940df60c90b13c8ad6eda85043b995b244e8b3e20b1e833b541 |
| population-unwpp.csv | ourworldindata.org/grapher/population-unwpp | Cross-check of 1950–2023 population | 69cefa274afbd51851369b79f364c41303c1581cedbbbca5ca38a475364888d8 |
| children-born-per-woman.csv | ourworldindata.org/grapher/children-born-per-woman | Fertility by country, grouping, fit target | b93978e9477851b133bf13baf986c162220ad2e388fafcc6bbc325cb2d41bc0a |
| life-expectancy.csv | ourworldindata.org/grapher/life-expectancy | Life expectancy by country, fit target | c304603fb8a7da263619a8ae43b7097f35b648c458855e23f1c4ef8f2ae75c01 |
| population-by-age-group.csv | ourworldindata.org/grapher/population-by-age-group | Age-structure validation (not fitted) | 602e74d0b95aa509a664dbb5b19c4ac8d280a48ec1e572a4cee044e1a458ade5 |
| population-with-un-projections.csv | ourworldindata.org/grapher/population-with-un-projections | UN medium projection benchmark | a77c8da5a75a47c82057c12ae52a38f4f11e3333c2a39a8b0260928caee45aa2 |
| births-by-age-of-mother.csv | ourworldindata.org/grapher/births-by-age-of-mother | Age pattern of childbearing | a10cd3068864dc36f894d671ff88405b24b7ae315cc857bbf0182e0298875542 |
| global-average-gdp-per-capita-over-the-long-run.csv | ourworldindata.org/grapher/global-average-gdp-per-capita-over-the-long-run | Growth of output per worker; failed GDP fit | 4f80c567684e3a19b2750ace696508f694aff6ff21b20199e355ff57ee87558b |
| researchers-in-rd-per-million-people-vs-gdp-pc.csv | ourworldindata.org/grapher/researchers-in-rd-per-million-people-vs-gdp-pc | Researcher growth (calibrates λ) | eb8f344e4c93131010b56e7feaea10104087c72df6b40f914fc3d3deed4ca6b9 |
| migrant-stock-share.csv | ourworldindata.org/grapher/migrant-stock-share | Size of omitted migration | 0f1831c454c3762613bdbf1b3598cb04044aaa6220c19e005dd828ddd6030d3c |
| population-of-cities-towns-and-villages.csv | ourworldindata.org/grapher/population-of-cities-towns-and-villages | Not yet used | 7b4f39b7a8b803b6f2efd0fe865df3ab9dfb8d0f4eae693ec486313366af7d59 |

To verify: `cd data/raw && sha256sum *.csv`.

Not yet obtained, needed for the next analyses: UN World Population Prospects past revisions (for the hindcast), Penn World Table, OpenAlex counts.
