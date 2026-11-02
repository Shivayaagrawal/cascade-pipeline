# Literature Matrix

**Access date:** 2026-11-02.

A row is included only when the source of the claim is stated. Papers that were not read are not given a method summary.

| Paper | Authors | Year | What was read | Research problem | Dataset | Architecture | Method | Evaluation | Results | Limitations | Relevance to CascadeGuard |
|-------|---------|------|---------------|------------------|---------|--------------|--------|------------|---------|-------------|---------------------------|
| Towards an ASR Error Robust Spoken Language Understanding System. Interspeech, pp. 901–905. DOI 10.21437/Interspeech.2020-2844 | Weitong Ruan, Yaroslav Nechaev, Luoxin Chen, Chengwei Su, Imre Kiss | 2020 | ISCA PDF text, 2026-11-02. Table 1 cells not copied because extraction reordered them. | ASR errors in a cascaded SLU system hurt NLU that was trained on clean transcripts. | ATIS text split plus aligned audio; private Alexa set | fastText, character CNN, 2-layer BiLSTM, softmax or CRF | 1-best hypotheses as adversarial views. Intent: CE plus KL. Slots: entity-exact pseudo-labels and marginalized CRF. | Classification F1; slot F1 on matched entities for ASR text. Must not regress on clean transcripts. | Prose: about 0.4% absolute ATIS classification gain on the matched ASR set. Alexa relative table values are in `docs/REFERENCE_PAPER_NOTES.md` and still need a visual PDF check. | ATIS is small. Alexa data and training hyperparameters are not reusable from the paper. No recovery policy. | This is the named reference. Shared problem: cascade error propagation. Different method and different data. |
| Speech Model Pre-training for End-to-End Spoken Language Understanding. arXiv:1904.03670. Author page says Interspeech 2019. | Loren Lugosch, Mirco Ravanelli, Patrick Ignoto, Vikrant Singh Tomar, Yoshua Bengio | 2019 | Abstract, Sections 1 and 3, and Table 1, fetched 2026-11-02. Training results sections were not re-read for this matrix. | End-to-end SLU from audio, with ASR pre-training to reduce labelled-data need. | Fluent Speech Commands, which this paper introduces | Not re-extracted in this phase beyond the abstract’s description of a model pre-trained to predict words and phonemes, then trained for intent. | End-to-end speech-to-intent. Not a cascaded robustness trainer. | PENDING. Metric tables in later sections were not used. | Not copied. This phase did not re-read the result tables. | The paper’s own system does not emit a transcript for error tracing. | Dataset source for the current CascadeGuard plan. Not the robustness method. |

| SLURP: A Spoken Language Understanding Resource Package. EMNLP 2020. arXiv:2011.13205. Audio DOI 10.5281/zenodo.4274930 | Emanuele Bastianelli, Andrea Vanzo, Pawel Swietojanski, Verena Rieser | 2020 | Abstract and the official README, including one JSON example. The paper’s model and result sections were not read. | Public English SLU data with more domains than a single command set. The abstract says 18 domains. | SLURP text in the GitHub repo; audio on Zenodo as `slurp_real` and `slurp_synth` | Not extracted. The README points at later SpeechBrain and ESPnet recipes. Those recipes were not read. | Not extracted from the paper. | The abstract names a transparent entity metric. The formula was not copied because the paper body was not read. | Not copied. | README `wer` fields are automatic ASR scores, not human labels. Synthetic audio is a separate directory. | Secondary benchmark for CascadeGuard. Not a reproduction target. |

## Cited by Ruan et al. and not independently read

Section 1 of Ruan et al. points at earlier n-best reranking, lattices, confusion networks, and end-to-end SLU. Those papers were **not** opened in this phase. Their methods and numbers are PENDING. They are not evidence for a CascadeGuard claim.

Named in that section, for a later reading list:

- N-best or hypothesis reranking: Jonson 2006; Sak, Saraclar, and Gungor 2011; Peng et al. 2013; Morbini et al. 2012; Kumar et al. 2017; Ogawa et al. 2019.
- End-to-end SLU: Lugosch et al. 2019; Serdyuk et al. 2018; Haghani et al. 2018; Tomashenko, Caubrière, and Estève 2019.
- Lattice or confusion representations: Ladhak et al. 2016; Henderson, Thomson, and Young 2014; Liu and Yang 2015; Shivakumar, Yang, and Georgiou 2019; Huang and Chen 2020.

No novelty claim follows from this list. CascadeGuard has not shown that diagnosis-plus-recovery is absent from later work, because that later work was not reviewed.
