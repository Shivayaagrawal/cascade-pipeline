# Reference Paper Notes

**Access date:** 2026-11-02.  
**Text read:** PDF text extraction of the ISCA copy, pages stated in that file as 901–905. Table cell alignment in the extractor was unreliable. Prose and section numbers below are from that extraction. Absolute cells in Table 1 are **PENDING** a visual check of the PDF before they are quoted as results.

This paper is the reference named in the Phase 0 plan. It is **not** the paper that introduced Fluent Speech Commands. An amendment draft dated 2026-11-02 shortened the authors to “Ruan, Y., Nechaev, A., Chen, X., Su, Y., and Kiss, I.” Those initials do not match the PDF. The names in the table below are the ones printed on the paper.

## Identity

| Field | Value | Status |
|-------|--------|--------|
| Title | Towards an ASR Error Robust Spoken Language Understanding System | VERIFIED, ISCA HTML and PDF |
| Authors | Weitong Ruan, Yaroslav Nechaev, Luoxin Chen, Chengwei Su, Imre Kiss | VERIFIED |
| Affiliation on the PDF | Amazon Alexa, Cambridge, USA | VERIFIED |
| Venue | Interspeech 2020, 25–29 October 2020, Shanghai, China | VERIFIED |
| Pages | 901–905 | VERIFIED, ISCA BibTeX |
| DOI | 10.21437/Interspeech.2020-2844 | VERIFIED |
| PDF | https://www.isca-archive.org/interspeech_2020/ruan20_interspeech.pdf | Fetched 2026-11-02 |
| HTML | https://www.isca-archive.org/interspeech_2020/ruan20_interspeech.html | Fetched 2026-11-02 |
| Code release | Not specified in the paper | PENDING |
| Full paper available | Yes, ISCA PDF | VERIFIED |

## Methodology extracted from the paper

| Component | What the paper states | Where |
|-----------|----------------------|--------|
| Research problem | A cascaded SLU system passes ASR errors into NLU. NLU trained on human transcripts has not seen those errors. | Abstract; Section 1 |
| SLU task | Intent classification and slot filling (NER), trained and scored as separate tasks. A semantic frame is the intent plus slots. Example: “what is the weather in Boston today” → `get_weather`, `city:Boston`, `date:today`. | Section 1 |
| ASR hypotheses used | Footnote 1: “In this paper, we only use ASR 1-best.” N-best lists are discussed as prior work, not as the method under test. | Section 1, footnote 1 |
| Public dataset | ATIS. Text split stated as 5,871 utterances: 4,478 train, 500 validation, 893 test. Audio was aligned to those utterances. | Section 5.1 |
| ASR system on ATIS | Amazon Transcribe. N-best hypotheses were obtained, then two evaluation sets were built by picking the hypothesis with the best WER or the worst WER: ASR-3.5 (3.5% WER) and ASR-4.0 (4% WER). | Section 5.1 |
| Private dataset | Alexa dataset: “a few millions” of annotated transcriptions and corresponding ASR hypotheses from the 2019 Alexa ASR used for live traffic. Not public. | Section 5.1 |
| Error types discussed | Homophones, compound-word splits, phonetic confusion, citing Kumar et al. on Alexa skill squatting. | Section 2 |
| Robustness rule | Robustness improves only if performance rises on a set that contains ASR errors **and** does not fall on a set without ASR errors. | Section 2 |
| NER scoring on ASR text | Slot F1 on ASR hypotheses counts only entities that still match after the error (“matched entities”). A split such as “netherlands” → “nether lands” is treated as not comparable to the original slot span. | Section 2; Section 5.3 |
| Architecture | Shared encoder: frozen 300-d fastText skip-gram word embeddings; OOV = mean of the 150 least frequent embeddings; character CNN with 32-d embeddings and 32 trigram filters; two BiLSTMs, 300 units per direction. Classification decoder: sum-pool, 600×600 ELU, softmax. NER decoder: linear-chain CRF. | Section 3 |
| Classification loss | Cross-entropy on the transcript, cross-entropy on the ASR hypothesis, plus KL between the two predictive distributions. Weights λ1, λ2, λ3. The text says the first and third terms together worked best. | Section 4.1 |
| NER training | Pseudo-label ASR hypotheses that differ from the transcript, then train a marginalized CRF. Entity Exact Match (EEM) is the rule used in the experiments. Token Exact Match is described and not selected. Unmatched spans get label `NA` and are marginalized. | Section 4.2 |
| Baselines | Model trained on transcriptions. Ablations: transcription plus ASR data augmentation; train on ASR only; proposed loss. | Section 5.2 |
| Optimizer, learning rate, batch size, epochs, seeds | Not specified in the paper. | PENDING |
| Embedding training corpus | fastText skip-gram. Corpus and embedding release are not specified beyond the fastText citation. | Section 3.1 |
| Metrics | Classification F1. NER slot-F1, with the matched-entity restriction on ASR text. The slot-F1 citation is the CoNLL-2000 chunking shared task. | Sections 5.2–5.3; reference [21] |
| Reported outcome (prose) | On ATIS classification, baseline F1 falls as WER rises. Training with the proposed loss is described as about 0.4% absolute better on the matching ASR set, with similar transcript F1. Training on ASR only improved ASR-set F1 and hurt transcript F1, which the authors call overfitting to ASR. | Section 5.2 |
| Table 1 absolute F1 cells | Present in the paper. The text extractor reordered rows, so individual cells are not copied here. | PENDING visual confirmation |
| Table 2, as extracted | Relative classification change versus baseline on the Alexa set. Proposed row uses weights 1.0, 0.0, 40.0 and is extracted as +0.88% on transcripts and +4.41% on ASR. Confirm on the PDF before citation. | Section 5, Table 2 |
| Table 3, as extracted | Relative NER slot-F1 by Alexa domain. Extracted transcript / ASR deltas: Music −0.35 / +0.9; SmartHome +0.19 / +5.3; Notifications +0.38 / +10.72; Shopping 0 / +2.58. Confirm on the PDF before citation. | Table 3 |
| Limitations stated by the authors | ATIS is small and has limited domain and slot diversity. Future work named in the conclusion is contextual encoders such as BERT, which this paper does not evaluate. | Sections 5.1 and 6 |
| What the paper does not establish | No failure detector. No RETRY, CLARIFY, or HOLD policy. No latency or false-alarm study. No claim about Fluent Speech Commands. No public Alexa split. No released code in the paper. | Sections 1–6 |

These numbers are the paper’s reported results. Cascade Pipeline has not reproduced them.

## Three-way split

### 1. Original methodology

Decoupled ASR then NLU. NLU is a CNN-BiLSTM classifier and a CNN-BiLSTM-CRF tagger. Robustness comes from training on paired human transcripts and Amazon Transcribe or Alexa 1-best hypotheses: KL consistency for intent, marginalized CRF with entity-exact pseudo-labels for slots. Success means better F1 on ASR text without worse F1 on clean transcripts.

### 2. What could be approximated here

**PENDING, and not approved.** An approximation would require:

- audio plus human transcripts plus intent and slot annotations;
- a declared ASR, which would not be Amazon Transcribe unless that service is explicitly approved (the project rules disallow paid APIs unless the owner approves);
- paired transcript and 1-best hypothesis per utterance;
- the same clean-versus-ASR evaluation rule.

ATIS audio and the LDC license were not inspected. The Alexa corpus cannot be reproduced. None of the training hyperparameters needed for an exact rerun are in the paper. Calling a later Cascade Pipeline run an exact reproduction would be false.

### 3. Cascade Pipeline extension

Specified in `docs/PROJECT_SCOPE.md` and not present in Ruan et al.:

- trace an error from audio or transcript into the semantic frame;
- compare one transcript with several candidates, and record whether those candidates are native N-best or another source;
- a diagnosis step and a bounded controller with CONTINUE, RETRY, CLARIFY, and HOLD;
- report recovery success, harmful recovery, false alarms, and latency, not only F1.

Ruan et al. cite n-best reranking as earlier work and then study 1-best robustness training. Cascade Pipeline’s B1 is closer to that earlier problem than to Ruan’s training method. It is a different experiment.

## Conflict with the current dataset plan

`docs/PROJECT_SCOPE.md` selects Fluent Speech Commands. Ruan et al. use ATIS and a private Alexa set. Fluent Speech Commands is introduced by Lugosch et al., Interspeech 2019, which studies end-to-end speech-to-intent models. Notes on that dataset paper remain in `docs/DATASET_CARD.md`.

Using FSC does **not** reproduce Ruan et al. Switching the primary data to ATIS would be a dataset change and needs approval in `docs/RESEARCH_DEVIATIONS.md` before implementation. Phase 0 does not make that switch.
