# Phase 3 limitations

CascadeGuard remains a synthetic, text-only simulation. These experiments do not measure speech recognition, waveform decoding, genuine N-best lists, speech WER or CER, audio robustness, or conversational generalization. `RETRY` rescores a string that was already in the bundle.

The challenge labels and `b2_semantic_v4` were both defined from the transformation operators. High action accuracy for E7 means the implementation follows those operators. It does not show that a different annotator, or a person, would have chosen the same actions. The LLM audit was not relabeled and is not ground truth. Its previously reported agreements stay 30/30, 57/90, and 43/90.

A single fluent sentence whose date or amount was replaced by another real lexicon value cannot be rejected without the parent gold or a second candidate. Those comparisons are two-candidate contradiction cases. The controller never sees the parent gold.

No intent has an empty required-slot list, so the two frozen empty slot maps were excluded rather than treated as legal intent-only requests. The implementation therefore does not demonstrate a true no-slot intent. There is no such intent in this grammar.

`please` is not modeled as uncertainty. The uncertainty cases are the prefix `Maybe`, which did not occur in the earlier audit sample. Weather `it` is ignored. Context cases use the token `that`.

Several ablations do not move test coverage. Contradiction detection is redundant with the critical-slot gate on this set, and the frozen risk score does not change the commits the gates already make. A missing effect is reported as a missing effect.

E7 answers 4 of 40 test cases. The low unsafe-commit rate is paired with that low coverage. A system that held every case would also have no unsafe commits, and its selective risk would be null rather than zero. E7 is not that system: it does commit four frames, all of which match the parent frame and were marked safe by the operator. Whether four safe answers out of forty is a useful balance is not settled by the action-accuracy number.

The test script was executed twice so that forced selection would stop being counted as coverage. The weight file was not changed. No threshold was chosen from the test split.

The human annotation sheet is still blank. No inter-annotator agreement is claimed.
