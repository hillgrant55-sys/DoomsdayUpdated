# Holdout definition

Committed 16 November 2026, after inspecting only the sheet names, column names, and per-column coverage (non-missing counts, number of countries, first and last year) of `data/raw/pwt110.xlsx`. No data values were read or printed before this commit.

**Rule.** A country is held out if the first hexadecimal digit of sha256(its three-letter ISO code, upper case) is 0, 1, 2, 3 or 4. Code: `harness/holdout.py`. The rule uses nothing about the data, applies to every dataset keyed by country (Penn World Table, OpenAlex, anything later), and cannot be tuned.

**Effect on Penn World Table 11.0.** 56 of 185 countries are held out:

ABW AGO AIA ALB ARE ARG ARM BGD BHS BOL CAF CIV CUW DMA DZA GBR GHA GNB GTM GUY HND HUN IDN IRN IRQ ISL ITA JOR KHM KOR KWT LBR LTU MAC MNE MRT MSR NGA NLD PRY QAT RUS SAU SLV SSD STP SWZ TCA TCD TGO TJK TUN VEN VGB ZAF ZWE

**Use.** Held-out countries are not read, plotted or summarised during model development. They are used once per question, for the final preregistered version of a model (PROTOCOL.md rules 4 and 5). Each use is recorded below.

**Known contamination.** Some held-out countries were in the 50–52 country sample of the first growth hindcast (`results/growth_hindcast.json`), which used a different dataset (GDP per capita and researcher counts, 1996–2023). Their growth after 2005 has therefore been seen in aggregate scores, though not country by country except for six outliers printed during checking (Ireland, Turkey, Malaysia, Russia, Argentina, Greece).

## Uses

None.
