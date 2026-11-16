# Attempt 3, the absorption model: results

Run 16 November 2026 under `growth/PREREGISTRATION_v3.md` (commit `00e6fc8`, written before the code). Stage 1 only, on the open countries.

## Verdict

**The model failed at the gate. Stage 2 was not run; the held-out countries remain sealed.**

Over all stage 1 origins (1975–2013, 651 country-forecasts), the primary model A1 had a pooled error 1.2% *higher* than the best baseline. The gate required it to be lower.

Under PROTOCOL.md rule 5 this was the third and last attempt on the coalition question. The question is closed: **these data do not support the idea that coalition measures (workforce, human capital, research output) improve ten-year forecasts of country productivity growth.**

## Scores, stage 1 (open countries; spent data)

Root-mean-square error of forecast ten-year growth in output per worker, percentage points a year.

| Model | All origins 1975–2013 | vs best | Primary origins 1975–2000 | vs best |
|---|---|---|---|---|
| B1 persistence | 2.60 | +19% | 2.68 | +23% |
| B2 mean | 2.36 | +8% | 2.30 | +5% |
| B3 shrinkage | 2.25 | +3% | 2.26 | +3% |
| B4 convergence | 2.32 | +6% | 2.36 | +8% |
| **B5 combined** | **2.19** | — | **2.19** | — |
| A1 Nelson–Phelps | 2.22 | **+1.2%** | 2.12 | −2.9% |
| A2 two faces | 2.23 | +1.9% | 2.17 | −0.7% |

A1 beat the baseline in 5 of 9 origins overall, and 4 of 6 in the primary years. It was worse in 1975, 1980, 2010 and 2013.

## What the coefficients show (exploratory)

| Training windows | Origin | Human capital × gap | Human capital alone |
|---|---|---|---|
| 1960–1965 | 1975 | +0.012 | −0.006 |
| 1960–1970 | 1980 | +0.024 | −0.016 |
| 1965–1975 | 1985 | +0.019 | −0.007 |
| 1970–1980 | 1990 | +0.009 | +0.009 |
| 1975–1985 | 1995 | −0.000 | +0.020 |
| 1980–1990 | 2000 | −0.004 | +0.028 |
| 1985–1995 | 2005 | −0.004 | +0.025 |
| 1990–2000 | 2010 | +0.001 | +0.034 |

In windows from the 1960s and 1970s the Nelson–Phelps pattern is there: human capital speeds catch-up more in countries further from the frontier. From windows starting in the mid-1970s onward the interaction vanishes and human capital acts as a plain level effect instead. Fitting on recent windows only therefore throws away the period in which the mechanism showed up, and the model forecasts no better than the baseline. This was found on spent data and is not a result.

## Expectations, scored

| # | Expectation | Outcome |
|---|---|---|
| 1 | The interaction coefficient is positive on average | Right (mean +0.0065), but only because of early windows |
| 2 | The rolling window makes B5 better than in attempt 2 | **Wrong.** 2.19 against 2.17 in the primary years |
| 3 | A1 passes the gate | **Wrong** |
| 4 | A1 does not pass in stage 2 | Not tested |
| 5 | Research terms change the error by under 2% | Right over all origins (+0.7%); just over in the primary years (+2.2%) |
| 6 | Held-out errors larger than open | Not tested |

## What three attempts add up to

| Attempt | Data | Best coalition result vs best baseline | Passed |
|---|---|---|---|
| 1 | UNESCO researchers, ~50 countries, 2005–2010 origins | Research intensity −8% at one cutoff, +59% at the other | No |
| 2 | PWT and OpenAlex, 46–94 countries, 1975–2013 | Human capital −4.7% (needed −5%) | No |
| 3 | Same, absorption model with recent-decade training | Nelson–Phelps +1.2% | No (gate) |

Article counts never helped in any version. Human capital helped modestly in some periods and not in others. The best baseline throughout was a combination of a country's past growth and its distance from the frontier.

## Status under PROTOCOL.md

- Coalition question: 3 of 3 attempts used. Closed.
- The held-out countries are unread and remain available for a different question.

## Reproduce

```
python3 growth/hindcast_v3.py --stage1
```
