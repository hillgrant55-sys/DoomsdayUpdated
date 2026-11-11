# Doomsday Postponed: the predictions ledger

Every forecast this project makes is recorded here before its outcome is known, then scored when the date arrives. The commit that adds an entry is its timestamp. Entries are never edited after registration; corrections are added as new entries.

**No predictions are registered yet.** The standards in the README require a model to pass a hindcast (fitted on data up to an earlier date and scored on what followed) before it may register forecasts. The hindcast comparison is the next piece of work.

## Format for each entry

| Field | Content |
|---|---|
| ID | P-YYYY-NNN |
| Registered | Date and commit hash |
| Quantity | Exactly what is forecast, and from which source it will be scored |
| Forecast | Central value and interval |
| Resolves | Date the outcome becomes known |
| Scoring rule | Stated in advance (for example, whether the observed value falls in the interval, and the error relative to the central value) |
| Model | Script, commit and parameters that produced it |
| Outcome | Filled in on resolution, never before |

## Registered predictions

None.

## Scored predictions

None.
