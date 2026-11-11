# Doomsday Updated

A response to von Foerster, Mora and Amiot, "Doomsday: Friday, 13 November, A.D. 2026" (*Science* 132, 1291, 1960), and the code base for a blog that builds simple models from public data, publishes dated forecasts, and scores them.

The 1960 paper fitted two thousand years of population estimates with a hyperbola that reaches infinity on 13 November 2026. This repository refits the idea behind it (a population whose members raise one another's productivity) with modern data, adds the limit the original left out, and asks when a shrinking coalition can no longer sustain its total output.

**Status:** first analysis complete and reproducible. No forecasts are registered yet; see [PREDICTIONS.md](PREDICTIONS.md).

## Headline results (baseline model)

| Quantity | Value |
|---|---|
| Working-age population peaks | 6.1 billion, January 2048 |
| World population peaks | 9.2 billion, November 2054 |
| World population in 2100 | 7.3 billion |
| World output peaks ("doomsday") | 1.86 × 2025 level, 30 December 2069 |
| Population falls below one person | 26 March 4348 |
| Fitted fertility floor | 1.49 children per woman |

These are model outputs, not forecasts we stand behind. The model's population is well below the UN medium projection (10.2 billion in 2100), mainly because it lets late-transition countries' fertility fall too fast. The full list of known weaknesses is in the manuscript's Reliability section and in [ERRORS.md](ERRORS.md).

## Repository layout

```
data/raw/        Downloaded source data, unmodified (see data/SOURCES.md)
data/derived/    Group and world series built from data/raw by src/prep*.py
src/             Final analysis pipeline
results/         Fitted parameters, results.json, run logs
figures/         Figures 1-3 of the manuscript
paper/           Manuscript pointer and equation images
archive/         Superseded exploratory scripts and figures (not part of the pipeline)
```

## Reproducing the results

Tested with Python 3.13, NumPy 2.5, SciPy 1.18, pandas 3.0, Matplotlib 3.11.

```
pip install -r requirements.txt
bash run_all.sh
```

`run_all.sh` rebuilds every derived file, refits the model from `results/start_params.json`, reruns all projections and scenarios, and redraws the figures, in about one minute. On 11 November 2026 a clean run reproduced every value in `results/results.json` and every pixel of the three figures exactly.

The global parameter search that produced `start_params.json` is not rerun by default because it takes about 20 minutes per seed. It is `archive/exploration/de3.py` with the model in `archive/exploration/model3.py`; the final model (`src/model5.py`) differs from it in using the observed age pattern of childbearing and in limiting the 1915–1949 excess mortality, plus extra outputs and switches used only by the scenarios.

## Pipeline

| Step | Script | Output |
|---|---|---|
| 1 | `src/prep.py` | Countries split into three groups by timing of fertility decline; group population, fertility and life expectancy (`data/derived/groups.csv`) |
| 2 | `src/cross.py` | Country-year table of fertility against life expectancy (`cross.csv`) |
| 3 | `src/prep2.py` | Age structure, UN projections, births by mother's age, GDP by group |
| 4 | `src/refit5.py` | Fitted parameters (`results/best5_d*.json`) |
| 5 | `src/proj5.py` | Projections, validation, economic scenarios (`results/results.json`) |
| 6 | `src/figs.py` | Figures 1–3 |
| 7 | `src/verify.py`, `src/econ.py` | Spot checks of numbers quoted in the text; the failed fit of the growth law to world GDP |

## Standards

1. Hindcast before forecast: no prediction is registered until the model has been scored on data it was not fitted to.
2. Primary data only, downloaded from the source, with checksums recorded. Nothing typed in from memory.
3. Every number in a post comes from code in this repository.
4. Predictions are timestamped by commit before the outcome is known, with scoring rules stated in advance.
5. Misses are reported as prominently as hits.
6. Prior work is cited in every post. The model here is a fitted, age-structured version of the unified-growth argument (Kremer 1993; Galor and Weil 2000; Korotayev 2005; Jones 2022), not a new theory.

## How AI was used

The analysis, code, figures and first draft were produced in conversation with Claude (Anthropic), directed and reviewed by the author. Errors made along the way, and how they were caught, are logged in [ERRORS.md](ERRORS.md).

## Licensing

Data in `data/raw` are from Our World in Data, published under CC BY 4.0; cite the original sources listed in `data/SOURCES.md`. A license for the code has not yet been chosen. The 1960 paper and other copyrighted articles are cited but not included.
