# Hindcast results

Run on 11 November 2026 under the rules in `PREREGISTRATION.md` (commit `97d607f`, written before any code was run).

## Verdict

**The cohort model fails the preregistered pass criterion.** It does not earn the right to register forecasts. `PREDICTIONS.md` stays empty.

| Cutoff | Within 5% on population | Beats all naive baselines on population | Beats all naive baselines on growth rate | Result |
|---|---|---|---|---|
| 1970 (does not count) | yes (−0.4%) | yes | no | fail |
| 1990 | yes (−4.6%) | **no** | yes | **fail** |
| 2000 | yes (−4.3%) | **no** | **no** | **fail** |

The baseline that beats it is the simplest one: add the same number of people each year as in the five years before the cutoff. From 1990 that is 3.3% high; from 2000 it is 0.3% low.

## Scoreboard

Observed 2023 (from `data/raw`): population 8.09 billion; mean growth 2015–2023 1.00% per year; 2.25 children per woman; 10.0% aged 65 and over.

"From 0" and "from 1650" are the two preregistered fitting windows. "Diverges" means the fitted curve reaches infinity before 2023.

### Fitted to data up to 1970

| Model | 2023 population (Bn) | Error | Growth 2015–23 (%/yr) | Error (points) |
|---|---|---|---|---|
| **Cohort model** | 8.06 | −0.4% | 1.07 | +0.08 |
| Naive: constant increment | 7.51 | −7.2% | 1.00 | 0.00 |
| Naive: constant growth | 10.96 | +35% | 2.05 | +1.05 |
| Naive: growth-rate trend | 13.12 | +62% | 2.65 | +1.65 |
| Capped power law, from 0 | 7.33 | −9.5% | 0.24 | −0.76 |
| Capped power law, from 1650 | 42.0 | +419% | 11.9 | +10.9 |
| Kapitza, from 0 | 15.1 | +87% | 5.1 | +4.1 |
| Kapitza, from 1650 | 25.7 | +218% | 8.1 | +7.1 |
| Hyperbola, from 1650 | 62.9 | +678% | 16.2 | +15.2 |
| Hyperbola, from 0 | diverges in 1998 | | | |
| Exponential-rate law, both windows | diverges by 1973 / 1983 | | | |

### Fitted to data up to 1990

| Model | 2023 population (Bn) | Error | Growth 2015–23 (%/yr) | Error (points) |
|---|---|---|---|---|
| Naive: constant increment | 8.36 | +3.3% | 1.15 | +0.15 |
| **Cohort model** | 7.72 | −4.6% | 0.88 | −0.12 |
| Naive: growth-rate trend | 9.13 | +13% | 1.54 | +0.54 |
| Capped power law, from 0 | 6.93 | −14% | 0.20 | −0.80 |
| Naive: constant growth | 9.65 | +19% | 1.80 | +0.80 |
| Kapitza, from 0 | 21.9 | +171% | 7.0 | +6.0 |
| Kapitza, from 1650 | 31.1 | +284% | 9.2 | +8.2 |
| Capped power law, from 1650 | 41.8 | +416% | 11.7 | +10.7 |
| Hyperbola, from 1650 | 56.0 | +592% | 14.9 | +13.9 |
| Hyperbola, from 0 | diverges in 2014 | | | |
| Exponential-rate law, both windows | diverges by 1992 / 1998 | | | |

### Fitted to data up to 2000

| Model | 2023 population (Bn) | Error | Growth 2015–23 (%/yr) | Error (points) |
|---|---|---|---|---|
| Naive: constant increment | 8.07 | −0.3% | 1.07 | +0.07 |
| **Cohort model** | 7.74 | −4.3% | 0.71 | −0.29 |
| Capped power law, from 1650 | 7.74 | −4.3% | 0.51 | −0.49 |
| Naive: growth-rate trend | 7.74 | −4.4% | 0.76 | −0.24 |
| Naive: constant growth | 8.49 | +4.9% | 1.38 | +0.39 |
| Capped power law, from 0 | 6.88 | −15% | 0.20 | −0.80 |
| Kapitza, from 1650 | 10.95 | +35% | 2.18 | +1.18 |
| Hyperbola, from 1650 | 16.5 | +104% | 5.2 | +4.2 |
| Kapitza, from 0 | 18.7 | +131% | 6.1 | +5.1 |
| Hyperbola, from 0 | 48.9 | +504% | 14.8 | +13.8 |
| Exponential-rate law, both windows | diverges by 2002 / 2008 | | | |

### Cohort model: the other two targets and what each fit implied

| Cutoff | Children per woman 2023 (observed 2.25) | Aged 65+ 2023 (observed 10.0%) | Fitted fertility floor | Implied peak |
|---|---|---|---|---|
| 1970 | 2.26 | 12.0% | 2.26 | none before 2300 (25.9 Bn and rising) |
| 1990 | 2.04 | 11.1% | 2.04 | none before 2300 (10.3 Bn and rising slowly) |
| 2000 | 1.74 | 10.8% | 1.70 | 8.5 Bn in 2050 |
| 2023 (published fit) | n/a | n/a | 1.49 | 9.2 Bn in 2054 |

Figure: `figures/fig4_hindcast.png`.

## What the results say

1. **The fertility floor is not a measured constant.** The fitted value falls with every cutoff: 2.26, 2.04, 1.70, 1.49. In each fit it sits close to the lowest fertility any large group had reached by then. The model has no information about where fertility stops; it reports where the leaders currently are. Everything in the essay that depends on the floor (the pace of decline after the peak, the last-person date) inherits this.
2. **The peak forecast is unstable.** Fits to 1970 and 1990 give no peak at all. A fit to 2000 gives a peak four years earlier and 0.7 billion lower than the published fit. A forecast that changes this much with 23 more years of data should not be given a date.
3. **Fertility in late-starting countries falls too fast in the model.** In the 1990 and 2000 fits every group has converged to the floor by 2023. In reality the high-fertility group was still at 4.0–4.4 children per woman. The model undercounts that group by 19–26% and overcounts or matches the others, so the world total hides larger group errors.
4. **The 1970 result is good partly by cancellation.** Groups A and B are 18% and 15% too high, group C 5% too low. (Corrected 11 Nov after review; first written as "A and B are 18% too high".) The world fertility figure is right because all groups had hit a floor that happened to equal the 2023 world average.
5. **The model consistently ages the world too fast** (65+ share 0.8 to 2 points high).
6. **Constant increment is hard to beat over 20–50 years.** World population has grown by a near-constant 80 million or so a year since the 1970s. Any model claiming skill has to beat a straight line first.
7. **The single-equation laws are not forecasting tools.** The hyperbola fitted to 1650–1970 with today's data returns a singularity in late 2025 (t0 = 2025.8), within about a year of von Foerster's date, and from 1650–1990 gives 2026.3. That reproduces the 1960 result and shows why it fails. Kapitza's form collapses onto the hyperbola at the 1970 and 1990 cutoffs (its time constant runs to the lower bound of 5 years).

## Expectations, scored

| # | Expectation | Outcome |
|---|---|---|
| 1 | Hyperbola more than 50% too high at every cutoff | Right (104% to 678%, or diverges) |
| 2 | UN projections of the time beat every model | **Half wrong** (added 11 Nov, see addendum). The 1990 revision beats everything from the 1990 cutoff. The 1998 and 2002 revisions do not: constant increment beats them clearly, and the cohort model is marginally closer on population |
| 3 | Cohort model from 1970 more than 10% off | **Wrong** (−0.4%), though see point 4 above |
| 4 | Cohort model from 1990 and 2000 within 3–5%; better than the hyperbola, capped and exponential-rate laws, worse than the UN | **Partly right.** Range right (−4.6%, −4.3%). The capped law from 1650 ties it at 2000, and it is not worse than the UN's 1998 or 2002 revisions on population |
| 5 | Cohort model's 2023 fertility too low at every cutoff | **Wrong as worded.** Too low at 1990 and 2000, not at 1970 |
| 6 | At least one naive baseline beats the cohort model at 1990 or 2000 | Right, at both |

## Addendum, 11 November 2026: the UN's past projections

Added after the run above, when the data were obtained. Source: `data/raw/world-population-projections-by-un-prospects-revision.csv` (Our World in Data, "World population, comparison of UN projections"). Script: `hindcast/un_past.py`.

**Deviation.** The file gives projections every five years, so there is no 2023 value. We interpolate log-linearly between each revision's 2020 and 2025 figures. The 2020 errors, which need no interpolation, are given alongside.

| UN revision | 2020 error | 2023 population (Bn, interpolated) | Error | Growth 2015–23 (%/yr) | Error (points) | Error in its base-year estimate | Error with base-year error removed |
|---|---|---|---|---|---|---|---|
| 1982 | −1.0% | 8.03 | −0.8% | n/a | n/a | −0.6% | −0.3% |
| 1984 | −0.8% | 8.05 | −0.5% | n/a | n/a | −0.7% | +0.2% |
| 1990 | +2.6% | 8.34 | +3.0% | 1.06 | +0.06 | +0.2% | +2.8% |
| 1998 | −4.9% | 7.69 | −4.9% | 0.91 | −0.09 | −1.9% | −3.1% |
| 2002 | −4.4% | 7.73 | −4.5% | 0.89 | −0.11 | −2.0% | −2.6% |
| 2012 | −2.2% | 7.94 | −1.9% | 1.00 | 0.00 | −2.0% | 0.0% |

"Base-year estimate" is the revision's figure for its first projected year compared with today's estimate for that year. The last column compares projected growth from that year with actual growth.

**Against the models.**

- *From 1990.* UN 1990 revision +3.0% and +0.06 points on growth. Constant increment +3.3% and +0.15. Cohort model −4.6% and −0.12. The UN is best on both.
- *From about 2000.* UN 1998 revision −4.9%, 2002 revision −4.5%; growth −0.09 and −0.11 points. Constant increment −0.3% and +0.07. Cohort model −4.3% and −0.29. Constant increment is best. The cohort model is marginally closer than the UN on population and much worse on growth rate.

**What this adds.**

1. The cohort model and the UN's 1998 and 2002 revisions miss 2023 in the same direction by a similar amount. Both expected fertility to fall faster than it did.
2. About two points of the UN's 1998–2002 error come from its population estimates for the base year, which were later revised up. Our models were given today's estimates and had no such handicap. On projected growth alone the UN (−3.1%, −2.6%) is better than the cohort model (−4.3%).
3. The UN's 1982 and 1984 revisions, made 40 years ahead, are within 1% of 2023. Our cohort model from 1970 is also close, and we called that partly luck. We have no basis for saying whether the UN's 1980s accuracy was skill or luck either.
4. The verdict on the cohort model does not change. The pass criterion was fixed in advance and did not involve the UN.

## Deviations and details not fixed in advance

- **Search cost function.** Differential evolution minimised the sum of log(1 + r²/9) over residuals, as in the published fit; the least-squares refinements and the reported misfit use plain squared residuals. The preregistration did not say this.
- **Seed choice.** Fit-period misfit (seed 1 / seed 2): 1970, 254.8 / 256.0; 1990, 526.265 / 526.265; 2000, 597.2 / 598.2. The 1990 seeds agree to five digits and give the same forecast to 0.03%.
- **Single-equation fits.** Bounds and optimiser were not specified in advance. Used: differential evolution plus three hand-chosen starts for the closed-form models, 12 random starts plus three hand-chosen for the capped law, each refined by least squares. Results were identical to a first run using the hand-chosen starts only. The exponential-rate law is evaluated from its exact solution, t(N) = t0 + τ[Ei(−KN) − Ei(−KN0)].
- **Constants at bounds.** Excess-mortality constant at its cap in all cohort fits (as in the published fit). In the 1970 fit the fertility-transition scale is at its upper bound (seed 1). Kapitza time constant at its lower bound (5 years) in five of six fits; capped-law ceiling at its upper bound (200 Bn) in two.
- **Exponential-rate law.** The form used is the one written in the preregistration. Checked on 11 Nov against Zaccone and Trachenko (arXiv:2502.19063): the equation dy/dt = (y/τ) exp(Ky) is theirs. They do not fit one K to the whole record; they describe different historical regimes as different limits of the equation. Our single-K fit over 0–cutoff or 1650–cutoff is therefore our use of their equation, not a test of their paper's claims.
- **World fertility in the model** is total births divided by the sum over groups of births/fertility, which equals the world rate given the shared age pattern of childbearing.
- **Process error.** The first three attempts at the single-equation script stalled on runaway ODE solutions and were killed. No results from them were used. Logged in `ERRORS.md`.

## Limits that still apply

Today's estimates of the past were used, not the estimates available at each cutoff. The model's structure, bounds and mortality schedules were chosen in 2026. Passing would not have validated anything after 2050; failing at 23–33 years makes the post-2050 claims weaker still.

## Reproduce

```
python3 hindcast/simple_models.py                     # about 2 minutes
for c in 1970 1990 2000; do for s in 1 2; do CUTOFF=$c python3 hindcast/cohort_h.py $s; done; done   # about 10–15 minutes each
python3 hindcast/score.py
```
