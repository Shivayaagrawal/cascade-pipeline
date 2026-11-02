# Risk Register

**Date:** 2026-11-02.  
**Review:** Phase 0.5 license pass, then the Common Voice direction the same day. No experiment has reduced these risks. Mozilla terms are not accepted. Acquisition stays blocked.

| ID | Risk | Evidence | Impact | Mitigation | Status |
|----|------|----------|--------|------------|--------|
| R1 | FSC license texts conflict. | Phase 0.5 evidence in the license register. | A mirror or the wrong instrument could be downloaded. | FSC is SUPERSEDED as the implementation dataset. Owner decision remains Pending. Do not download FSC. | Open. Historical. |
| R2 | Local annotations were not inspected. Publisher slot names may differ from the CSV. | No files under the repo or parent `cnn` tree | Intent and slot metrics could score the wrong fields. | Phase 1 reads the header and writes the real names into the schema. No invented slots. | Open. Blocks label feasibility. |
| R3 | FSC or SLURP results presented as the Ruan et al. experiment, or the two datasets pooled. | Amended design: FSC primary, SLURP secondary, ATIS excluded. Schemas differ. | A false reproduction or a meaningless average. | Separate adapters and separate tables. No ATIS download. | Open. Design recorded. Data not obtained. |
| R12 | SLURP audio and text licenses differ. | Phase 0.5 register rows. | One license could be assumed to cover both. | SLURP is SUPERSEDED for Phase 1. Decisions stay Pending. Do not download. | Open. Historical. |
| R13 | Common Voice terms are not accepted, and the catalogue record is not confirmed in the owner’s account. | Public dataset page and Common Voice terms read 2026-11-02. CC0-1.0 is printed on the dataset page, with extra bans on speaker identification and re-sharing. | A download before acceptance, or a frozen ID that does not match the account, would break the gate. | Owner decision Pending. `docs/DATASET_CARD.md`. | Open. Blocks Phase 1. |
| R14 | The listed English archive is larger than the free disk. | Catalogue size 88.43 GB. `df -h` showed about 60 GiB free on 2026-11-02. | A default full download will fail or fill the disk. | Do not download the full archive. Identify a smaller official subset in the MDC account before any transfer. | Open. |
| R15 | Common Voice has transcripts and no native intent or slot labels. Scripted speech is not conversation. | Datasheet describes `sentence` and read speech. | Intent accuracy or slot F1 would be fabricated. A semantic result could be over-claimed as robustness on spontaneous speech. | Milestone A is WER/CER only. Milestone B needs a guide, dual review, and adjudication. | Open. |
| R4 | faster-whisper may not return N-best lists. | Public README shows one text per segment. Package not installed. | B1 cannot be labelled native N-best. | Provenance field is mandatory. Independent decodes stay labelled as such. | Open. |
| R5 | Scores are not calibrated. | No calibration run exists. | A threshold on a logit can look like a probability. | `docs/METRIC_DEFINITIONS.md` forbids that wording until a validation reliability check is saved. | Open. |
| R6 | Speaker or file leakage. | Official claim is speaker-disjoint. Not checked locally. | Inflated test scores. | Phase 1 overlap check must fail the run if a speaker is shared. | Open. |
| R7 | Synthetic errors treated as natural error rates. | Protocol risk, no data yet. | Invalid deployment claims. | Reports name the transform and seed and refuse a prevalence claim. | Controlled by protocol. Still easy to violate in prose. |
| R8 | Recovery adds latency or abstains too often. | Not measured. | A safer table can hide a system that always HOLDs. | HOLD rate, clarification rate, and P50/P95 are required beside accuracy. | Open. |
| R9 | CNN or SLURP work blocks the cascade. | Decision C marks the CNN optional. The older phase-wise table called Phase 2 a CNN deliverable. | The robustness questions never get a B0 run. | CNN is off the critical path. UI stays in Phase 8. | Reduced for the CNN. Still watch scope. |
| R10 | Results cannot be rerun. | No git repository, no lockfile, system Python 3.13.7 versus README 3.11. | A later number has no commit to point at. | Phase 1 creates a virtualenv and pins dependencies. Git init was not done in Phase 0 because it was not requested. | Open. |
| R11 | Table 1 of the reference paper was misread from a text extractor. | Extractor reordered cells. | A false citation. | Absolute Table 1 cells stay out of claims until the PDF is checked visually. | Open. |

## Top three for the owner

1. Confirm the Common Voice record in your own MDC account and accept the terms yourself, or do not download. The public page is not acceptance.
2. Do not download the full English archive. It is listed at 88.43 GB and this disk has about 60 GiB free.
3. Do not report intent or slot scores before a checked manual subset exists. FSC and SLURP stay superseded and blocked. This register does not authorize Phase 1.
