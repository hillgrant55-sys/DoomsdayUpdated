# Knowledge-loss test: results

Run 16 November 2026 under `seshat/PREREGISTRATION.md` (commit `eb24637`, in force before any code was written or value read). Open regions first, then the held-out regions once.

## Verdict

**Not supported.** In the open regions, losses of capability were no more likely after a sharp population decline than otherwise (Mantel–Haenszel risk ratio 0.94, permutation p = 0.56). The pass mark was a risk ratio of at least 1.5 with p below 0.05. The held-out regions pointed the other way (1.67, p = 0.13), but they were only the replication and cannot rescue a failed primary test.

## Results

Capability = infrastructure + information systems + money. A transition is one century step with real (not filler) observations at t−100, t and t+100. A sharp decline is a fall of at least 0.15 in log10 polity population (about 30%) over the previous century.

| | Open regions | Held-out regions |
|---|---|---|
| Transitions (regions) | 113 (12) | 43 (9) |
| Sharp declines | 20 | 10 |
| Capability losses | 28 (25%) | 13 (30%) |
| Loss rate after sharp decline / otherwise | 4 of 20 / 24 of 93 | 5 of 10 / 8 of 33 |
| Mantel–Haenszel risk ratio | **0.94** | **1.67** |
| Permutation p (one-sided) | 0.56 | 0.13 |

Military technology (secondary): risk ratio 0.85 (p = 0.74) open, 0.92 (p = 0.44) held out.

## The clearest pattern: losses happen when the polity changes

| Loss rate | Same polity continues | Polity changes |
|---|---|---|
| Capability, open | 0 of 40 | 28 of 73 (38%) |
| Capability, held out | 1 of 15 | 12 of 28 (43%) |
| Military technology, open | 0 of 40 | 23 of 73 (32%) |
| Military technology, held out | 0 of 18 | 12 of 30 (40%) |

Out of 76 recorded losses, 75 occur in a century in which one polity replaced another. A shrinking population inside a continuing state almost never shows a loss in these data. We cannot tell from Seshat whether this is real (conquest or collapse destroys institutions) or partly a coding effect (a new polity is described from different sources). The pattern holds in both samples and is strong, but it was not the preregistered hypothesis and is reported as exploratory.

## Expectations, scored

| # | Expectation | Outcome |
|---|---|---|
| 1 | Loss events under 15% of transitions | **Wrong** (25% open, 30% held out) |
| 2 | Risk ratio after sharp decline between 1.5 and 3 | **Wrong** in the open regions (0.94); 1.67 held out |
| 3 | Losses more common at polity transitions | Right, by a wide margin |
| 4 | Military technology shows no population effect | Right (0.85, 0.92) |
| 5 | The hypothesis is supported | **Wrong** |

## What this means

1. In these state-level societies, a century of sharp population decline does not by itself predict losing infrastructure, record-keeping or money. This fits Vaesen and colleagues' scepticism and Turchin and colleagues' finding that polity population does not drive military technology.
2. The samples are small: 156 usable transitions in 21 regions, because Seshat often fills centuries with copies. A modest effect could be missed, and the two samples disagree.
3. What does predict loss in the record is a change of polity. For the essay's question, that suggests capability is held less by head count than by the institutions that carry it: when the institution survives, a smaller population keeps what it had.

## Details

- Three region-centuries had more than one row; two were ambiguous and dropped (rules: keep real rows, drop if still several).
- Only 12 of 22 open regions and 9 of 13 held-out regions have any usable transition.

## Status

Question "does population decline cause capability loss": attempt 1 of 3, not supported. The held-out regions have now been used for this question.

## Reproduce

```
sh data/fetch_seshat.sh
python3 seshat/loss_test.py --open
python3 seshat/loss_test.py --holdout
```
