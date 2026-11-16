# Second coalition test: results

Run 16 November 2026 under `growth/PREREGISTRATION_v2.md` (commit `527d9af`, agreed and committed before the code was written). Non-held-out countries only. The held-out countries were not run, because nothing passed.

## Verdict

**No coalition model passes. Attempt 2 of 3 is a fail.**

Human capital came closest. It met two of the three conditions and missed the third by 0.3 percentage points.

| Model (combined baseline plus…) | Change in error vs best baseline | Better in how many of 6 forecast years | Bootstrap 90% interval of error ratio | Result |
|---|---|---|---|---|
| Employment growth | −1.6% | 5 | 0.977 to 0.991 | fail |
| **Human capital** | **−4.7%** | 5 | 0.937 to 0.968 | **fail** (needed −5%) |
| Research intensity (article share per worker) | −0.1% | 2 | 0.990 to 1.007 | fail |
| Research scale (article share) | +0.7% | 2 | 0.993 to 1.021 | fail |
| All four | −2.1% | 5 | 0.958 to 0.999 | fail |

## Scores, primary forecast years (1975–2000), 375 country-forecasts

Root-mean-square error of forecast ten-year growth in output per worker, percentage points a year.

| Model | Error | vs best baseline | Mean error | 80% interval coverage |
|---|---|---|---|---|
| B1 persistence | 2.68 | +23% | −0.17 | 71% |
| B2 cross-country mean | 2.30 | +6% | −0.17 | 77% |
| B3 shrinkage | 2.23 | +3% | −0.28 | 74% |
| B4 convergence | 2.35 | +8% | +0.58 | 73% |
| **B5 combined (best baseline)** | **2.17** | — | −0.25 | 75% |
| M1 head count | 2.14 | −1.6% | −0.26 | 75% |
| M2 human capital | 2.07 | −4.7% | −0.07 | 75% |
| M3 research intensity | 2.17 | −0.1% | −0.22 | 75% |
| M4 research scale | 2.19 | +0.7% | −0.31 | 74% |
| M5 all four | 2.13 | −2.1% | −0.14 | 76% |

Countries per forecast year: 46 (1975), 54, 56, 63, 70, 86 (2000). Error by year is in `results/growth_v2.json`.

## Secondary forecast years (2005, 2010, 2013; not counted)

| Model | Error |
|---|---|
| B5 combined | 2.11 |
| M1 head count | 2.18 |
| M2 human capital | 2.27 |
| M3 research intensity | 2.12 |
| M4 research scale | 2.05 |
| M5 all four | 2.24 |

Human capital, the best addition in 1975–2000, is the worst here. Research scale, which did nothing in 1975–2000, is the best here by 3%.

## Expectations, scored

| # | Expectation | Outcome |
|---|---|---|
| 1 | The combined model is the best baseline | Right |
| 2 | Persistence is not the best baseline | Right; it is the worst |
| 3 | No coalition model passes | Right |
| 4 | Human capital gives the largest gain, 1–4% | Largest, yes; 4.7% is just outside the range |
| 5 | Articles change the error by under 2% | Right (−0.1%, +0.7%) |
| 6 | Coverage for the combined model between 70% and 90% | Right (75%) |
| 7 | Secondary years rank the models differently | Right |

## What this shows

1. **Persistence reverses between tests.** In attempt 1 (about 50 mostly rich countries, 1996–2019) a country's own past growth was the best predictor. Here, over 1975–2010 and a wider set of countries, it is the worst, as Pritchett and Summers describe. Attempt 1's result was a feature of its sample and period.
2. **Article counts carry no detectable forecasting information** beyond past growth and income level, in the years that count.
3. **Human capital is the only measure with a consistent gain in 1975–2000**, and the gain disappears after 2005. A gain that holds for six forecast years and then reverses for three is not something to build on without a further test.
4. **The baseline itself is weak.** The best model's error is 2.2 points a year on a quantity whose cross-country spread is about the same. Ten-year country growth is mostly unpredictable from these variables.

## Details not fixed in advance

- **Intercept.** The rules specified origin fixed effects in training but not which intercept to use for the forecast year. Used: the observation-weighted mean of the training intercepts.
- **Missing article years** within the five-year average are counted as zero.
- **Bootstrap** resamples countries (2,000 draws, seed 20261116) without refitting, as the rules say. It therefore understates the uncertainty in the comparison.
- **Tie.** In 1975 human capital and the baseline have the same error to two decimals; it is not counted as a win.

## Status under PROTOCOL.md

Attempt 2 of 3 used. Targets now spent: ten-year growth in output per worker from Penn World Table for the non-held-out countries, forecast years 1975–2013. The held-out countries remain unread.

## Reproduce

```
python3 growth/hindcast_v2.py
```
