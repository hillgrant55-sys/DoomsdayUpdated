# Protocol: what happens after a test fails

Adopted 12 November 2026, before the next datasets (Penn World Table, OpenAlex) were obtained. Changes to this file are made by adding dated amendments at the bottom, never by editing the rules above them.

## Rules

1. **A failed test is published as it stands.** The failing version, its rules and its scores stay in the repository. A revision is a new version with its own preregistration and results files. Old files are corrected only for errors of fact, with the correction dated.

2. **Work done after seeing a test's outcome is exploratory.** Diagnosing a failure and trying fixes is expected. Anything found that way is labelled exploratory in every file and post, and is not reported as a result until it passes a test it has not seen.

3. **A used test is spent.** Once the errors on a set of targets have been seen, no revised model may be scored on those targets and called confirmed. Each revision needs fresh targets: different cutoffs, different units, a different quantity, or data not yet released.

4. **A holdout is set aside before new data is opened.** For each new dataset, the holdout is defined in a committed file before the data is read beyond its column names and coverage. It is used once per question, for the final version of a model.

5. **Three preregistered attempts per question.** If the third fails, the question is written up as "these data do not support this idea" and closed. Reopening it requires new data, and an amendment here saying what changed.

6. **A change needs a reason other than the test score.** Each new feature or structural change is justified in the preregistration by a mechanism or by cited prior work, stated before fitting.

7. **Forecasts of unreleased data count most.** Predictions registered in `PREDICTIONS.md` before the outcome exists cannot be contaminated. Only a model that has passed a hindcast may register them, and their scores take precedence over any hindcast when judging a model.

## Spent as of adoption

| Question | Targets already seen | Attempts used |
|---|---|---|
| World population forecast (cohort model) | World population 2023, growth 2015–23, world fertility 2023, share aged 65+ 2023, from cutoffs 1970, 1990, 2000 | 1 of 3 |
| Does a coalition measure help forecast country growth | Growth of output per working-age person to 2019 and 2023, from cutoffs 2005 and 2010, for the 50–52 countries in `results/growth_hindcast.json` | 1 of 3 |

## Exploratory findings awaiting a fresh test

- Adding research intensity to the convergence model lowered forecast error by 8–9% at both cutoffs (`growth/RESULTS.md`, point 3). Found on spent data.
- The fitted fertility floor tracks the lowest fertility observed at the time of fitting (`hindcast/RESULTS.md`). Found on spent data.

## Amendments

None.
