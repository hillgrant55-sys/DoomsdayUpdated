# Preregistration, attempt 3 of 3: the absorption model

Committed 16 November 2026, before any code for this model was written or run. Not edited after this commit; deviations go in `growth/RESULTS_v3.md`. This is the last attempt allowed on the coalition question (PROTOCOL.md rule 5).

## Question

Does a country's capacity to absorb existing ideas (its human capital and its research output) set how fast it closes the gap to the productivity frontier, and does modelling it that way improve ten-year growth forecasts?

## Prior work and the reason for each change (PROTOCOL rule 6)

| Feature | Source | What it implies here |
|---|---|---|
| Human capital × distance to frontier | Nelson and Phelps (1966); Benhabib and Spiegel (1994, J. Monetary Econ. 34: 143–173) | Catch-up speed rises with human capital. The effect of skills should be larger the further a country is from the frontier. Attempts 1 and 2 entered human capital only additively. |
| Research × distance to frontier | Griffith, Redding and Van Reenen (2004, Rev. Econ. Stat. 86: 883–895), "two faces of R&D" | Research helps both innovation (direct effect) and imitation (interaction with the gap). Attempt 2 entered articles only additively. |
| Coefficients fitted on recent decades only | Kremer, Willis and You (2022, NBER Macro Annual 36: 337–412); Patel, Sandefur and Subramanian (2021, J. Dev. Econ. 152) | Convergence patterns changed from the 1990s on. Pooling all decades with fixed coefficients averages two regimes. |

**Disclosure.** The third row was looked for after attempt 2 showed a reversal after 2005. The literature supplies the reason, but the choice was prompted by our own spent results. The first two rows follow from the papers alone.

## Model

All variables as defined in `growth/PREREGISTRATION_v2.md` (q = output per worker; g_lag; lq; lhc; art_int). New: gap = −lq, the log distance to the sample frontier at the origin (zero for the frontier country, positive otherwise).

- **A1, primary (Nelson–Phelps):** y = a + b1·g_lag + b2·gap + b3·lhc + b4·lhc·gap
- **A2, secondary (two faces):** A1 + b5·art_int + b6·art_int·gap

Baselines, all refitted under the same rules: B1 persistence, B2 cross-country mean, B3 shrinkage (g_lag), B4 convergence (gap), B5 combined (g_lag, gap).

**Training window.** For a forecast from origin C, regressions are fitted on the three most recent ten-year windows that had finished by C (origins C−10, C−15, C−20 where available), with origin fixed effects and the observation-weighted mean intercept as in attempt 2. Every regression model uses this window, so the baselines have the same advantage.

The model is fixed here. No variable, interaction, window length or sample rule may be changed after this commit.

## Stage 1: development run on the open countries (spent data, exploratory)

Purpose: check the code and see how the model behaves. Origins 1975–2013, open countries only. These targets are spent, so nothing from stage 1 counts as evidence.

**Gate.** Stage 2 is run only if A1's pooled RMSE over all stage 1 origins is below that of the best baseline in stage 1. If not, attempt 3 is recorded as failed at the gate and the holdout stays sealed for future questions. In either case the decision to run stage 2 is put to Grant Hill before it is run.

## Stage 2: confirmation on the held-out countries (once)

- Countries scored: the 56 held-out countries (`harness/holdout.py`), subject to the sample rules of attempt 2 (population ≥ 1 million, data at C−10, C and C+10, human capital at C, at least 20 articles a year).
- Training at origin C: all countries, open and held-out, using only windows finished by C. This is the information a forecaster would have had at C.
- Primary origins: 1975–2000. Secondary (reported, not counted): 2005, 2010, 2013. Held-out Russia and Argentina appeared, as individual errors, in attempt 1's checking output; their post-2005 growth has therefore been seen.
- Known breach: held-out article counts for 2020–2023 were seen (`data/HOLDOUT.md`). They enter no primary origin.

**Pass criterion (identical to attempt 2), for A1 only.** Over the primary origins:
1. A1's pooled RMSE is at least 5% below the best baseline's (lowest pooled RMSE among B1–B5 on the held-out countries);
2. A1 beats that baseline in at least five of six origins (all but one if fewer can be scored);
3. the 90% bootstrap interval of the RMSE ratio, resampling held-out countries 2,000 times, lies entirely below 1.

A2 is reported but cannot pass or fail the question.

## Outcomes

- **Pass:** "Absorptive capacity, measured by human capital, improves ten-year growth forecasts in countries the model never saw" is recorded as a result. The model is frozen and may be used for registered forecasts in `PREDICTIONS.md`.
- **Fail (at the gate or in stage 2):** the coalition question is closed under PROTOCOL rule 5: "these data do not support the idea that coalition measures improve country growth forecasts." Reopening needs new data.

## Expectations

1. The interaction coefficient b4 is positive on average across origins (more human capital, faster catch-up).
2. The rolling window makes B5 better than it was in attempt 2's pooled training.
3. A1 passes the stage 1 gate.
4. A1 does not pass in stage 2.
5. A2's research terms change the error by less than 2% either way.
6. Held-out errors are larger than open-country errors for every model (smaller sample, more low-income countries).

## Known weaknesses

- The held-out sample is small (likely 20–40 countries per origin), so a real effect may fail condition 3 for lack of power.
- Acemoglu's comment on Kremer, Willis and You argues that convergence estimates without country fixed effects are biased. Forecasting models cannot use country fixed effects for countries with short histories, so this bias is accepted.
- PWT's human capital index is built from years of schooling and assumed returns; it does not measure skills directly.
