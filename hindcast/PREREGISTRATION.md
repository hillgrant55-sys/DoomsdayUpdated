# Hindcast: rules and expectations, written before any run

Committed on 11 November 2026 before any hindcast code was run. The commit hash of this file is the timestamp. Nothing below may be edited afterwards; deviations are reported in `hindcast/RESULTS.md`.

## Question

If each model had been fitted using only data up to a cutoff year, how well would it have predicted 2023?

## Design

**Cutoffs:** 1970, 1990, 2000.

**Targets, all from the files in `data/raw`:**
1. World population in 2023.
2. Mean world growth rate, 2015–2023 (log ratio divided by 8).
3. World children per woman in 2023 (cohort model only).
4. Share of world population aged 65 and over in 2023 (cohort model only).

**Data vintage:** today's estimates of the past, cut off at each date. This is more lenient than using the estimates available at the time, and is a disclosed limitation.

**Models**

| Model | Form | Free constants |
|---|---|---|
| Hyperbola (von Foerster 1960) | N = K/(t0 − t)^k | 3 |
| Finite-time cutoff (Kapitza 1996) | N = (K/τ) arccot((T1 − t)/τ) | 3 |
| Capped power law | dN/dt = a N^(1+b) (1 − N/M) | 4 |
| Exponential-rate law (Zaccone and Trachenko 2025) | dN/dt = (N/τ) exp(K N), single K | 3 |
| Three-group cohort model (this project) | `src/model5.py` equations | 16 |
| Naive: constant growth | last 5-year growth rate held fixed | 0 |
| Naive: constant increment | last 5-year absolute increase held fixed | 0 |
| Naive: growth-rate trend | linear trend of the growth rate over the previous 20 years, extended (floored at zero) | 0 |
| UN medium projection of the time | to be added when the past-revision data are obtained | n/a |

The Korotayev–Malkov–Khaltourina literacy model is not included because we have not verified its equations from the source.

**Fitting the single-equation models:** least squares on log population at the project's standard dates (every century to 1700, every decade to 1950, every 5 years after) up to the cutoff, with assumed errors of 15% before 1500, 5% for 1500–1949 and 2% from 1950. Each is fitted twice: on all dates from year 0, and on dates from 1650 only. Both are reported; neither is preferred in advance.

**Fitting the cohort model:**
- Only data up to the cutoff are used, including the age pattern of childbearing.
- Countries are grouped using only pre-cutoff data: by mean fertility in the five years ending at the cutoff, A below 3 children per woman, B from 3 to 5, C at 5 or above. (The published model groups by fertility in 1975 and 2010, which would leak the future.)
- Bounds are those of the published model, except that group-specific bounds are widened to common ranges (initial populations 0.001–0.3 billion, premodern fertility 3.5–8.5), because group sizes change with the cutoff.
- Search: differential evolution, population 8 per constant, 200 generations, seeds 1 and 2, followed by two least-squares refinements. The seed with the lower misfit on the fitting period is used. No result is chosen by looking at its forecast.
- Fixed assumptions carried over unchanged: the two mortality schedules (limit life expectancy 82.4), the 1915–1949 excess-mortality cap, assumed data errors.

## Pass criterion for the cohort model

It passes at a cutoff if it (a) beats all three naive baselines on both world population and growth rate, and (b) is within 5% on world population. It earns the right to register forecasts only if it passes at both 1990 and 2000. The 1970 result is reported but does not count toward passing, because we expect it to fail (below).

## Expectations

1. The hyperbola fails badly at every cutoff (2023 population too high by more than 50%).
2. The UN's own projections from 1990 and 2000, once added, beat every model here on world population.
3. The cohort model from 1970 does poorly (more than 10% off), because most of the world had not begun its fertility decline and the fertility floor cannot be identified.
4. The cohort model from 1990 and 2000 is within 3–5% on world population: better than the hyperbola, capped and exponential-rate laws, worse than the UN.
5. The cohort model's 2023 world fertility is too low at every cutoff.
6. At least one naive baseline beats the cohort model on world population at one of the 1990 or 2000 cutoffs, so the model has roughly even odds of failing the pass criterion.

## What cannot be fixed, only disclosed

- The cohort model's structure was designed in 2026 with knowledge of how the transition unfolded.
- Its bounds, mortality schedules and error weights were also chosen with that knowledge.
- A 23- to 53-year test says nothing about the post-2050 claims (fertility floor, output peak).
