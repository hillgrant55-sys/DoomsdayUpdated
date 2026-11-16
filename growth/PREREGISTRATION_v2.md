# Preregistration, attempt 2 of 3: does a coalition measure help forecast productivity growth?

Status: **in force.** Agreed by Grant Hill on 16 November 2026 and committed before any code was written or run. Not edited after this commit; deviations go in `growth/RESULTS_v2.md`. No Penn World Table values have been read; the design uses only the file's column names and coverage.

## Question

Given what a country's own past growth and income level already tell us, does any measure of the size or quality of its "coalition" (workers, skills, research output) improve a forecast of its productivity growth over the next ten years?

## What changed from attempt 1, and why (PROTOCOL rule 6)

| Change | Reason, stated before fitting |
|---|---|
| Penn World Table 11.0 replaces the 1996–2023 file | Attempt 1 had two cutoffs and about 50 rich countries. PWT gives 1950–2023. |
| Rolling origins every five years, ten-year horizon | More independent tests; one or two cutoffs cannot separate skill from luck. |
| Coalition models are added to a baseline that already contains persistence | In attempt 1 persistence was the best model but was left out of the coalition models, so they were never given a fair chance. |
| Research measured by articles (OpenAlex), as a share of the world total | Researcher head counts do not exist before 1996. Using shares removes growth that comes from OpenAlex indexing more journals over time. |
| Human capital added as a coalition measure | Nelson and Phelps (1966) and the later catch-up literature: skills govern how fast a country absorbs existing ideas. |

## Data

- `pwt110.xlsx`: output per worker q = rgdpna / emp. Human capital index hc. Population pop.
- `openalex_articles_by_country_year.csv`: articles by country and year.
- Countries: non-held-out only (`harness/holdout.py`). The held-out 56 are not read.

## Design

Origins C = 1975, 1980, …, 2010, and 2013 (so the last window ends in 2023). Horizon ten years.

Target: mean annual growth of q from C to C+10 (log difference / 10).

Predictors, all measured at or before C:
- g_lag: growth of q from C−10 to C
- lq: log q at C, minus the log of the highest q among sample countries at C (distance to the frontier)
- emp_g: growth of employment from C−10 to C
- lhc: log hc at C
- art_int: log of (country's share of sample articles, averaged over C−4..C) minus log of (country's share of sample employment at C)
- art_scale: log of the country's share of sample articles, averaged over C−4..C

Sample at each origin: population at least 1 million at C; q available at C−10, C and C+10; hc available at C; at least 20 articles a year on average over C−4..C. The same countries are used for every model at that origin.

Training at origin C: every earlier window that had finished by C (targets ending at or before C), pooled across countries and earlier origins, with origin fixed effects. Coefficients are estimated by least squares and applied to the predictors at C. The first origin with at least two finished training windows is the first one scored.

## Models

Baselines
- **B1 persistence:** g_lag
- **B2 mean:** cross-country mean of g_lag at C
- **B3 shrinkage:** regression on g_lag
- **B4 convergence:** regression on lq
- **B5 combined:** regression on g_lag and lq

Coalition models (B5 plus one variable each)
- **M1 head count:** + emp_g
- **M2 human capital:** + lhc
- **M3 research intensity:** + art_int
- **M4 research scale:** + art_scale
- **M5 all four**

## Fresh and spent targets (PROTOCOL rule 3)

Attempt 1 scored growth after 2005 and 2010 for about 50 countries, on a different output measure. Origins 2005, 2010 and 2013 therefore overlap targets already seen in aggregate.

- **Primary score:** origins 1975–2000. None of these targets has been seen.
- **Secondary, reported but not counted:** origins 2005, 2010, 2013.

## Scoring

Root-mean-square error of forecast growth across countries, pooled over the primary origins and also per origin. Mean error. 80% intervals from each model's training residual standard deviation, with coverage reported. Shared code: `harness/score.py`.

Uncertainty on the comparison: resample countries with replacement 2,000 times (keeping all of a country's origins together) and report the 90% interval of the ratio of a coalition model's RMSE to the best baseline's.

## Pass criterion

A coalition model passes if, over the primary origins, all three hold:
1. its pooled RMSE is at least 5% below the best baseline's;
2. its RMSE is below the best baseline's in at least five of the six primary origins (fewer if early origins cannot be scored; then all but one);
3. the 90% bootstrap interval of the RMSE ratio lies entirely below 1.

"Best baseline" means the baseline with the lowest pooled RMSE over the primary origins.

## If it passes, if it fails

- **Pass:** the passing model is frozen and run once on the held-out countries (PROTOCOL rule 4). Only if it also beats the best baseline there, by any margin, is the result reported as confirmed. The breach recorded in `data/HOLDOUT.md` (held-out article counts for 2020–2023 were seen) does not touch the primary origins.
- **Fail:** recorded as attempt 2 of 3. Diagnosis is exploratory. One attempt remains.

## Expectations

1. B5 is the best baseline.
2. Persistence (B1) is not the best baseline here, unlike attempt 1, because ten-year windows since 1965 include many growth reversals.
3. No coalition model passes.
4. M2 (human capital) gives the largest gain, between 1% and 4%.
5. M3 and M4 (articles) change the error by less than 2% either way.
6. Interval coverage is between 70% and 90% for B5.
7. Results for the secondary origins rank the models differently from the primary ones.

## Known weaknesses

- Article counts measure published output in indexed journals, not researchers or ideas, and early coverage favours English-language journals.
- Ten-year country growth is noisy; a real but small effect could fail criterion 3 for lack of power.
- PWT revises its history between versions; these are today's estimates.
- The AI has general knowledge of economic history that cannot be removed.
