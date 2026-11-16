# The disruption question: why we are not running a test

Written 16 November 2026, after a literature check and before any data on disruption was collected. No attempt under PROTOCOL.md was used.

## The question

Park, Leahey and Funk (Nature 613: 138–144, 2023) reported that papers and patents became less disruptive over time, measured by the CD index, while the absolute number of highly disruptive works stayed roughly level. Our question was whether disruptive output falls where researcher numbers fall, for example in the former Soviet states in the 1990s.

## Why it cannot be answered well with available measures

1. **No ready measure in our data.** OpenAlex has no disruption field (checked against its API reference). Computing the CD index needs the full citation network: every citing paper of every paper. SciSciNet V2 provides paper-level scores, but it is a large download and inherits the problems below.
2. **The measure itself is disputed.**
   - Holst et al. (arXiv:2402.14583, 2024) argue the decline is driven by database entries recorded with zero references, which score as maximally disruptive. In SciSciNet they find 97% of papers with the maximum score make zero references.
   - Petersen, Arroyave and Pammolli (arXiv:2306.01949; Journal of Informetrics) argue the index falls mechanically as reference lists lengthen ("citation inflation").
   - Park, Leahey and Funk reply (arXiv:2503.00184, 2025) that the decline survives excluding zero-reference works, and that the critics' dataset has about three times more of them.
   - A weighted variant of the index ("Is disruption decreasing, or is it accelerating?") finds disruption roughly stable, rising slightly since 2000.
   - Leibel and Bornmann (arXiv:2308.02383) review the variants and their limitations.
3. **At country level the index tracks referencing practice, not innovation.** A 2026 preprint, "The disruption index does not measure scientific innovation" (arXiv:2606.07332), finds Iraq and Nigeria rank as the most "disruptive" countries, with over half their articles scoring positive. A cross-country test of disruption against researcher numbers would therefore mostly compare how countries cite.

## Decision

Not run. Any result would be dominated by which variant of a contested measure we chose and by national citation habits. The question stays open for a future measure validated against expert judgement. This is recorded as a finding of the literature check, not as a failed test.
