# Holdout definition: Seshat Equinox-2020

Committed 16 November 2026, after reading only the workbook's sheet names, column headers, licence files and the list of region names (NGAs). No polity, population or technology values have been read.

**Data.** Seshat Equinox-2020, GitHub repository seshatdb/Equinox_Data, commit `602c7cdf0649e1fbbdb37f5b5a387edbe19915d0`, file `Equinox_on_GitHub_June9_2022.xlsx`, sha256 `48c7fbd00b6ebca4405d171e1d8e4fb2ea74a2fcd3edd0762e699e7d472f0556`. Fetched by `data/fetch_seshat.sh`; not copied into this repository. The repository's README states the data are CC BY-NC-SA, while its LICENSE file is CC0; we follow the stricter terms and cite Turchin et al. (2020), Cliodynamics 11(1): 41–50.

**Rule.** A region (NGA, Seshat's "natural geographic area") is held out if the first hexadecimal digit of sha256(its name exactly as written in the NGAs sheet) is 0–4. All polities in a held-out region are held out.

**Held out (13 of 35 regions):** Big Island Hawaii, Cahokia, Cambodian Basin, Central Java, Chuuk Islands, Cuzco, Deccan, Lowland Andes, Niger Inland Delta, North Colombia, Orkhon Valley, Sogdiana, Susiana

**Use.** Held-out regions are not read, plotted or summarised during model development, and are used once per question for the final test (PROTOCOL.md rules 4 and 5).

## Uses

- 16 November 2026: knowledge-loss test (`seshat/RESULTS.md`), replication stage, run once.
