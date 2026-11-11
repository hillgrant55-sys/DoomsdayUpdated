# Error log

Mistakes made during the work, mostly by the AI assistant, and how each was caught. Kept public because catching errors is part of the method.

| # | Date | Error | How caught | Effect on results |
|---|---|---|---|---|
| 1 | 2026-11-10 | The first fits used population, fertility and life-expectancy values typed from memory rather than downloaded data. | Stated in the responses at the time; replaced once the author supplied OWID files. | Early exploratory fits only (now in `archive/`); no published number depends on them. |
| 2 | 2026-11-10 | The first age-structured model computed replacement fertility incorrectly, so the premodern population grew by about 0.2% a year when it should have been stationary. | Stationarity check before refitting on the real data. | Early parameter values discarded; fixed before the final model. |
| 3 | 2026-11-10 | Overstated the novelty of the approach. "Capability ends the growth regime that created it" is the central claim of Galor and Weil (2000), and "AI restarts the ideas loop" is Davidson (2021). | Literature searches prompted by outside feedback; reading Galor and Weil directly. | No numbers affected; framing of all posts changed. |
| 4 | 2026-11-10 | Kapitza (1996) was first cited from memory. | Verified against the journal's site before the second draft. | None; citation was correct. |
| 5 | 2026-11-10 | Manuscript said world growth held between 1.7 and 2.2% a year in 1950–1990 and that each group had 54 population dates. | Rechecked against the data: 1.6–2.2%, and 58 dates. | Text corrected. |
| 6 | 2026-11-10 | Equations in the manuscript were stored as raw LaTeX and exported as source code. | Author noticed in the PDF and Word exports. | Replaced with typeset images. |
| 7 | 2026-11-11 | `refit5.py` set the 1915–1949 mortality limit by text substitution that matched only the model file's original default. After the default was later changed, a rerun would have silently fitted one case twice. | Rebuilding the repository and rerunning everything from scratch. | None on reported results (the original run predated the change, and the clean rerun reproduces them exactly); fixed. |
| 8 | 2026-11-11 | First versions of `hindcast/simple_models.py` stalled on runaway ODE solutions; three runs were killed. | Runs did not finish. Fixed by freezing runaway solutions and using the exact solution of the exponential-rate law. | None: no numbers from the stalled runs were used, and final results match the one earlier run that completed. |
| 9 | 2026-11-11 | Wrong expectation: we predicted in advance that the cohort model fitted to 1970 would miss 2023 world population by more than 10%. It missed by 0.4%. | The preregistered hindcast. | None on results; scored as wrong in `hindcast/RESULTS.md`. |

Known model limitations (not errors) are listed in the manuscript's Reliability section.
