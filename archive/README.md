# Archive

Exploratory scripts and figures from the first day of work, kept for transparency. They are not part of the pipeline and will not run as they are: they use paths from the original workspace.

Cautions:
- `fit.py`, `fit2.py`, `cohort.py` and `kremer*.py` use population, fertility and life-expectancy values typed from memory, not downloaded data (ERRORS.md, item 1).
- `cohort.py` and the first version of the cohort model in `kremer.py` contain the replacement-fertility bug (ERRORS.md, item 2).
- `model.py` through `model3.py` are successive versions of the demographic model; `de*.py` are the global parameter searches. `model3.py` with `de3.py` produced `results/start_params.json`.
- `model4.py`, `de4.py`, `proj4.py`, `scen4.py`, `figs4.py` and `polish4.py` are the abandoned attempt to tie capability to measured income, which fitted much worse.
- `figures/` holds the figures sent during exploration, in order: single-equation ceiling fits, the first two-variable model, and the three-group model on the uploaded data.
