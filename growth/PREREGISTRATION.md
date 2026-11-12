# Preregistration: does counting researchers help forecast growth?

Written 11–12 November 2026, before any of the code below was written or run. Deviations go in `growth/RESULTS.md`; this file is not edited afterwards.

## Why this test

The essay's output-peak date rests on a law in which growth in output per worker is driven by the number of researchers. That law was calibrated on twenty years of world data and never tested. The population model failed its hindcast, so from here population is treated as an input (UN estimates and projections), and the test moves to the growth law. This is also the first pass at the "coalition" question: which count, if any, carries information about future growth.

## Prior work (checked before writing this)

Pritchett and Summers (NBER WP 20573, 2014) show that country growth rates persist very little from decade to decade and regress to the world mean. So the baselines to beat are the cross-country mean and a shrunken version of a country's own past growth, not persistence. Bloom, Jones, Van Reenen and Webb (2020) and Jones (2022) are the source of the researcher-driven law.

## What we already know (leakage)

The essay calibrated the world law on 2000–2019: output per worker grew 2.07% a year and researchers 3.48% a year. So the world-level outcome for the test windows is already known to us. The country-level outcomes have not been examined.

## Data

`researchers-in-rd-per-million-people-vs-gdp-pc.csv` (GDP per capita 1990–2025, researchers per million 1996–2024), `population.csv`, `population-by-age-group.csv` (working age = 15–64). Today's estimates throughout.

- q = GDP per capita × population / working-age population (output per working-age person).
- Growth over a window = log ratio of q divided by years.
- Researchers R = researchers per million × population. A value "at year t" is the mean of available values in t−2..t+2; missing if none.
- Countries: three-letter codes, population at least 1 million at the cutoff, q available at 1996, the midpoint, the cutoff and the end of the test window, and researchers available at 1996, the midpoint and the cutoff (±2 years each). The same set of countries is used for every model at a given cutoff.

## Cutoffs, windows, target

Cutoffs C = 2005 and 2010. Training window 1996–C, split at the midpoint m (2000 for 2005; 2003 for 2010). Primary test window C–2019. Secondary: C–2023 (reported, does not count).

Target: each country's mean annual growth of q over the test window.

## Models

Every regression is estimated across countries on training data only: second-half growth (m to C) on predictors measured at m or over the first half (1996 to m). The fitted coefficients are then applied with predictors measured at C or over the second half, to forecast C–2019.

Baselines
- **B1 persistence:** the country's own growth over 1996–C.
- **B2 mean:** the unweighted cross-country mean of growth over 1996–C, the same number for every country.
- **B3 shrinkage:** regress second-half growth on first-half growth; apply to second-half growth.
- **B4 convergence:** regress growth on log q at the start of the period.

Coalition models (each is B4 plus one variable)
- **M1 research intensity:** + log researchers per million at the start.
- **M2 researcher growth:** + growth of R over the preceding half-window.
- **M3 head count:** + growth of the working-age population during the forecast period itself (treated as known in advance, since it is nearly determined by people already born).
- **M4 scale:** + log R at the start (absolute number of researchers).

World law (one number per cutoff, reported separately): world q growth over C–2019 predicted as (a) the same as 1996–C; (b) the essay's law, growth × (R_test growth factor) with λ set so that 1996–C was a steady state, using realised world researcher growth.

## Scoring

Root-mean-square error of forecast growth across countries, in percentage points a year, unweighted (primary) and weighted by working-age population (secondary). Also mean error (bias).

Intervals: for each model, the standard deviation s of its errors in an inner hindcast (fit on first half, score on second half is not possible for regressions with one split, so s is the in-sample residual standard deviation for B3, B4, M1–M4, and the standard deviation of second-half minus first-half growth for B1 and B2). The 80% interval is forecast ± 1.28 s. We report the share of countries whose outcome falls inside.

## Pass criterion

A coalition model **passes** if, at both cutoffs, its unweighted RMSE over C–2019 is at least 5% lower than the best of B1–B4. Anything less is reported as "no detectable gain."

## Expectations

1. B1 (persistence) is the worst baseline at both cutoffs.
2. B2 or B3 is the best baseline; B4 improves on B2 by less than 10%.
3. No coalition model passes.
4. M3 (head count) comes closest, because working-age growth correlates with stage of development.
5. Every model is biased high for C–2019 (growth slowed after 2008), by 0.5 to 1.5 points.
6. Interval coverage is below 80% for every model.
7. World law: (b) is no closer than (a).

## What the outcomes would mean

- Pass: researcher counts carry forecastable information at the country level; worth building on with better data (Penn World Table, OpenAlex).
- Fail with M1–M4 close to B4: at this horizon and with these data, counting researchers adds nothing to forecasting country growth. That would not refute the idea-based law, which is a claim about the world frontier over long periods, but it would mean this dataset cannot test it and the essay's output date has no empirical support beyond its calibration.
- Sample size is small (tens of countries, biased toward rich ones that report R&D data). A fail is weak evidence; a pass would need replication.
