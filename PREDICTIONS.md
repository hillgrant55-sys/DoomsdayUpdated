# Doomsday Postponed: the predictions ledger

Every forecast this project makes is recorded here before its outcome is known, then scored when the date arrives. The commit that adds an entry is its timestamp. Entries are never edited after registration; corrections are added as new entries.

**No predictions are registered yet.** The standards in the README require a model to pass a hindcast (fitted on data up to an earlier date and scored on what followed) before it may register forecasts. The first hindcast was run on 11 November 2026 and the model failed it (see Status below).

## Format for each entry

| Field | Content |
|---|---|
| ID | P-YYYY-NNN |
| Registered | Date and commit hash |
| Quantity | Exactly what is forecast, and from which source it will be scored |
| Forecast | Central value and interval |
| Resolves | Date the outcome becomes known |
| Scoring rule | Stated in advance (for example, whether the observed value falls in the interval, and the error relative to the central value) |
| Model | Script, commit and parameters that produced it |
| Outcome | Filled in on resolution, never before |

## Registered predictions

None.

## Scored predictions

None.

## Status, 11 November 2026

No entries. The cohort model failed the pass criterion set in `hindcast/PREREGISTRATION.md` (results in `hindcast/RESULTS.md`), so nothing from it is registered here.

## Scoreboard 1: does AI show up in US growth? (registered 16 November 2026)

These entries register **other people's published forecasts**, plus our own stated expectations, so they can be scored against official data as it arrives. None of them comes from a model of ours; our models have not passed a hindcast (PROTOCOL.md amendment of 16 Nov 2026). Where a source gave an increment over its own baseline, we converted it to a level using the baseline stated below. That conversion is ours, not theirs.

**How much can these entries tell apart?** In Penn World Table data for the US, 1955–2023, consecutive five-year averages differ with a standard deviation of 0.9 points for GDP per hour and 1.4 points for real GDP growth. Forecasts closer together than about half a point will not be distinguishable by one five-year outcome. These entries can separate "little visible effect" from a boom of the size Goldman Sachs or the survey's rapid-AI scenario describe. They cannot separate Acemoglu from Penn Wharton.

### S1. US real GDP growth, average 2025–2029

- **Measure:** BEA annual real GDP (chained dollars); 100 × ln(GDP 2029 / GDP 2024) / 5, using data as published on 31 October 2030.
- **Resolves:** November 2030.
- **Score:** absolute error of each point forecast; contestants ranked.

| Contestant | Forecast (% a year) | Source |
|---|---|---|
| Official forecasters (FOMC, CBO and others; eight of nine between 1.9 and 2.1) | 2.0 | Compiled in Karger et al. (2026) |
| Office of Management and Budget | 2.8 | Karger et al. (2026) |
| Survey: academic economists, unconditional | 2.5 | Karger et al. (2026) |
| Survey: AI experts, unconditional | 2.5 | Karger et al. (2026) |
| Survey: superforecasters, unconditional | 2.5 | Karger et al. (2026) |
| Survey: general public, unconditional | 2.4 | Karger et al. (2026) |
| Survey, rapid-AI scenario: economists / AI experts / superforecasters / public | 3.3 / 3.7 / 3.7 / 3.5 | Karger et al. (2026); conditional forecasts, reported for comparison |
| **Our expectation (judgement, not a model)** | **2.2** | Hill and Claude |

### S2. US nonfarm business labor productivity growth, average 2026–2030

- **Measure:** BLS annual index of output per hour, nonfarm business sector; 100 × ln(index 2030 / index 2025) / 5, using data as published on 31 October 2031.
- **Resolves:** November 2031.
- **Baseline used to convert increments:** 1.5% a year, the BLS rate for the 2007–2019 business cycle.
- **Caveat:** most of these sources describe a ten-year period, often with effects building up over time. A five-year average from 2026 will understate a forecast whose effect arrives late. This entry tests whether the effect is visible by 2030, not whether the ten-year forecast was right.

| Contestant | Increment (points a year) | Forecast (% a year) | Source |
|---|---|---|---|
| No AI effect | 0 | 1.5 | BLS 2007–2019 cycle |
| Current cycle continues | — | 2.2 | BLS rate since Q4 2019, through Q3 2026 |
| Acemoglu | ≤0.07 (≤0.66% TFP over 10 years) | 1.57 | Acemoglu (2025), Economic Policy 40: 13–58 |
| Penn Wharton Budget Model | ~0.15 (1.5% level by 2035) | 1.65 | Arnon (2025) |
| OECD | 0.4–1.3 | 1.9–2.8 (midpoint 2.35) | Filippucci et al. |
| Aghion and Bunel | 0.68–1.3 | 2.18–2.8 (midpoint 2.49) | Aghion and Bunel (2024) |
| Goldman Sachs, after widespread adoption | 1.5 | 3.0 | Briggs and Kodnani (2023); Goldman expects measurable effects from 2027 |
| **Our expectation (judgement, not a model)** | — | **2.0** | Hill and Claude |

Ranges are scored on their midpoints, and we also report whether the outcome falls inside the range.

### S3. US labor productivity growth in 2030 (single year)

- **Measure:** as S2, for the year 2030 alone: 100 × ln(index 2030 / index 2029).
- **Resolves:** November 2031.

| Contestant | Forecast (% ) | Source |
|---|---|---|
| Survey: economists, unconditional | 2.0 | Karger et al. (2026) |
| Survey: economists, slow / moderate / rapid AI scenario | 2.0 / 2.5 / 3.2 | Karger et al. (2026); conditional |
| **Our expectation** | **2.0** | Hill and Claude |

A single year is noisy; S3 is kept because it is the survey's own target.

### Sources

- Karger, Kuusela, Abaluck, Bryan, Halperin, Jones, Murphy, Trammell, Reynolds, Mayland, Viswanathan, Mittal, Ceppas de Castro, Rosenberg and Tetlock, "Forecasting the Economic Effects of AI", Federal Reserve Bank of Chicago WP 2026-07 (March 2026).
- Acemoglu, "The Simple Macroeconomics of AI", Economic Policy 40 (2025): 13–58.
- Aghion and Bunel, "AI and Growth: Where Do We Stand?" (2024).
- Briggs and Kodnani, Goldman Sachs (2023); Goldman Sachs Research, "AI may start to boost US GDP in 2027".
- Arnon (2025), Penn Wharton Budget Model; OECD (Filippucci et al.), as compiled in Karger et al. (2026) and by Tom Cunningham, "Forecasts of AI & Economic Growth" (2025).
- BLS, Productivity and Costs, Third Quarter 2026, Preliminary (5 November 2026).

### S4. Do AI structure predictors substitute for experimental structural biology? Experimental structures released by the PDB in 2030

Registered 16 November 2026. Prior evidence: an NBER study of AlphaFold2 (w35143) finds the rate of experimental structure determination almost unchanged after July 2021, with predicted structures used to complement experiments. This entry asks whether that still holds as prediction tools improve.

- **Measure:** "Number of Structures Released Annually" for 2030 in the RCSB PDB table "Overall Growth of Released Structures Per Year" (rcsb.org/stats/growth/growth-released-structures), as displayed on 31 March 2031.
- **Values as retrieved 16 Nov 2026** (mirror sierra.k8s.rcsb.org; other mirrors differ by under 1% for complete years): 2015 9,244; 2016 10,805; 2017 11,061; 2018 11,169; 2019 11,479; 2020 14,006; 2021 12,586; 2022 14,290; 2023 14,500; 2024 15,471; 2025 15,730.
- **Resolves:** April 2031.

| Contestant | Forecast for 2030 | Basis |
|---|---|---|
| Substitution: AI prediction displaces experiments | below 15,730 (the 2025 level) | Directional; no published point forecast |
| Trend continues (log-linear fit, 2015–2025) | 20,739 (80% band 19,419–22,149) | 5.0% a year; band from fit residuals |
| **Our expectation (judgement)** | **within the trend band** | Complement, as in the NBER evidence |

Outcome below 15,730: substitution supported. Inside the band: complement continues. Above the band: AI is accelerating experimental work.

