# Growth-law hindcast: results

Run 12 November 2026 under `growth/PREREGISTRATION.md` (commit `06de04b`, written before the code).

## Verdict

**No coalition model passes.** Counting researchers, or workers, did not improve forecasts of country growth over the best baseline at both cutoffs. The best forecast of a country's growth in output per working-age person was its own past growth.

## Scores (test window: cutoff to 2019)

Root-mean-square error of forecast annual growth, percentage points. "vs best baseline" is relative to the lowest baseline error at that cutoff; the pass mark was −5% or better at both.

| Model | Data to 2005 (50 countries) | vs best baseline | Data to 2010 (52 countries) | vs best baseline |
|---|---|---|---|---|
| B1 persistence | **1.72** | — | **1.04** | — |
| B2 cross-country mean | 1.92 | +12% | 1.79 | +72% |
| B3 shrinkage | 1.86 | +9% | 1.43 | +38% |
| B4 convergence | 1.74 | +1% | 1.81 | +74% |
| M1 research intensity | 1.58 | **−8%** | 1.66 | +59% |
| M2 researcher growth | 1.67 | −3% | 1.85 | +78% |
| M3 head count | 1.74 | +2% | 1.53 | +47% |
| M4 scale (number of researchers) | 1.74 | +1% | 1.80 | +73% |

Mean observed growth: 2.06% a year over 2005–2019 and 2.31% over 2010–2019. Bias was +0.6 to +1.1 points for every model from 2005 and within ±0.3 from 2010. The 80% intervals covered 84–96% of countries from 2005 and 75–98% from 2010. Results to 2023 (secondary) rank the models the same way; full tables in `results/growth_hindcast.json`.

Weighted by working-age population, persistence is also best at both cutoffs (1.02 and 1.01), by a wider margin.

## The essay's law at the aggregate level

**Deviation.** The file has no world researcher figure before 2000, so the world law could not be run as registered. Substitute: the fixed country sample treated as one economy.

| Data to | (a) growth continues | (b) the essay's law with realised researcher growth | Observed |
|---|---|---|---|
| 2005 | 2.10% | 2.08% | 2.45% |
| 2010 | 1.99% | 2.02% | 2.69% |

The two predictions differ by 0.03 points or less, because researcher growth barely changed between training and test (3.2% then 3.0%; 3.0% then 3.3%). Both were low by 0.4 to 0.7 points. With inputs this steady, the law makes the same prediction as "nothing changes", so these data cannot test it.

## Expectations, scored

| # | Expectation | Outcome |
|---|---|---|
| 1 | Persistence is the worst baseline | **Wrong.** It is the best at both cutoffs |
| 2 | The mean or shrinkage is the best baseline; convergence improves on the mean by under 10% | **Wrong** on the first part. Convergence beats the mean by 9% from 2005 and is slightly worse from 2010 |
| 3 | No coalition model passes | Right |
| 4 | Head count comes closest | **Wrong as worded.** Closest from 2010; research intensity is closest from 2005 |
| 5 | Every model biased high by 0.5–1.5 points | Right from 2005, wrong from 2010 |
| 6 | Interval coverage below 80% for every model | **Wrong.** Above 80% for all but two models at one cutoff |
| 7 | The law is no closer than "growth continues" | Not testable as registered; in the substitute the two are indistinguishable |

## What this does and does not show

1. **Our reading of the literature was wrong for this sample.** We expected regression to the mean to beat persistence, following Pritchett and Summers. Here persistence won clearly. The sample is 50-odd countries that report R&D data, mostly middle- and high-income, over windows of 9 to 14 years that overlap long growth episodes (China, eastern Europe). We have not shown their finding fails in general.
2. **Researcher counts add nothing detectable once a country's own history is known.** The pass criterion was not met.
3. **Exploratory, not preregistered:** against the convergence model alone, adding research intensity lowers the error at both cutoffs (1.74 to 1.58; 1.81 to 1.66). That is a consistent 8–9% gain over a weak baseline. It would need its own preregistered test, with persistence included, before it means anything.
4. **The essay's output-peak date has no empirical support beyond its calibration.** The law cannot be distinguished from constant growth with these data.
5. **The sample is small and selected.** Countries without R&D statistics are excluded, which removes most low-income countries.

## Reproduce

```
python3 growth/hindcast.py
```
