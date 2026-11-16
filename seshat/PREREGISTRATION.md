# Preregistration: is capability lost when populations shrink?

Status: **in force.** Agreed by Grant Hill on 16 November 2026 and committed before any code was written or any value read. Before this commit, only the workbook's sheet names, column headers, region names and its Metadata sheet (descriptions of the sheets) were read. Not edited after this commit; deviations go in `seshat/RESULTS.md`. Holdout committed in `data/HOLDOUT_SESHAT.md`.

## Question

When a region's population falls sharply, is it more likely to lose technologies and institutions in the following century? This is the "forgetting" half of the coalition idea: if capability is held by the coalition, shrinking the coalition should sometimes destroy it.

## Prior work

- **For a population effect:** Kremer (1993, QJE) on isolated regions; Henrich (2004, American Antiquity 69: 197–214), a model of technological loss in small populations applied to Tasmania; Kline and Boyd (2010, Proc. R. Soc. B 277: 2559–2564), larger, better-connected Oceanic populations had more complex marine tools; Collard et al. (2013, PLOS ONE) found the same among food producers.
- **Against:** Collard et al. (2005) and Read (2008) found no relationship among hunter-gatherers; Vaesen, Collard, Cosgrove and Roebroeks (2016, PNAS 113: E2241–E2247) argue population size does not explain past changes in cultural complexity, with a reply from Henrich and colleagues; Aoki (2018) offers reasons the correlation could be absent even if the mechanism is real.
- **State-level societies:** Turchin et al. (2021, PLOS ONE 16: e0258161), using Seshat, find world population, connectivity and key enabling technologies predict gains in military technology, while polity population does not.

Almost all of this concerns gains, toolkit size, or small-scale societies. We test **losses** in **state-level** societies over the Holocene, using Seshat's region time series.

## Data and variables

Seshat Equinox-2020, sheet `AggrSCWarAgriRelig`: one row per region (NGA), polity and century (`Time`). Open regions only for the primary test.

- **Population change:** ΔPop = Pop(t) − Pop(t−100), where Pop is the sheet's polity population variable (log scale, as supplied). A **sharp decline** is ΔPop ≤ −0.15 (a fall of about 30% if Pop is log10; if the codebook shows a different scale, the threshold is set to the equivalent 30% fall before any values are read).
- **Capability index:** C = Infra + Info + Money (infrastructure, information systems, monetary system), as supplied.
- **Loss event:** C(t+100) < C(t).
- **Polity change:** whether the polity occupying the region at t+100 differs from the one at t. Losses at polity transitions may partly reflect different coders and sources, so results are stratified by it.

## Clarifications fixed before any value was read

From the workbook's Metadata sheet:
- Rows with `uniq = n` are fillers that copy earlier values so series run at century intervals. A transition is used only if the rows at t−100, t and t+100 all have `uniq = y`; this avoids counting copied rows as "no change".
- `Dupl` marks rows where one polity controlled two regions. Such rows stay in both regions' series; the permutation test shuffles within regions.
- Missing values (blank or −999) exclude a transition.
- Pop is taken to be log10 polity population, as in Turchin et al. (2018, PNAS 115: 144–151), so the −0.15 threshold stands.

## Test

- Primary statistic: risk ratio of a loss event after a sharp decline versus after no sharp decline, pooled with Mantel–Haenszel weights across the two polity-change strata.
- Significance: permutation test shuffling ΔPop within each region, 10,000 permutations, one-sided.
- **Supported** if the risk ratio is at least 1.5 and the permutation p-value is below 0.05 in the open regions, **and** the risk ratio in the held-out regions, computed once with the same code, is above 1.
- Secondary (reported, not decisive): the same test with Turchin et al.'s military-technology components (Metal, Weapon, Armor, Defense, Animal, Project) as the outcome.

## Expectations

1. Loss events are rare: under 15% of century transitions.
2. The risk ratio after sharp decline is between 1.5 and 3 for the capability index.
3. Losses are more common at polity transitions than within a polity.
4. Military technology shows no population effect (risk ratio under 1.5), consistent with Turchin et al.
5. The hypothesis is supported.

## Known weaknesses

- Seshat codes presence and absence from the historical record; absence of evidence can be coded as absence, and later polities may be better documented than earlier ones, which biases against observed losses.
- Polity population estimates for early periods are uncertain by large factors.
- Century steps are coarse; losses and recoveries within a century are invisible.
- The AI has general knowledge of world history (for example, the Bronze Age collapse and post-Roman Britain) that cannot be removed. The test design does not depend on which regions these are in.
