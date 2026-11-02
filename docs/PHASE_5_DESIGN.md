# Phase 5 design

`b2_semantic_v5` is a new controller. It does not replace `b2_semantic_v4`, and it does not edit Phases 1–4.

The research question is whether a semantic integrity and commitment gate can reduce unsupported commits while keeping some coverage on a controlled synthetic transcript set. The invariant is that no semantic frame is committed unless its evidence, critical values, modality, and candidate identity have been checked.

## What the controller may see

The controller receives a candidate bundle: ids, text, provenance, and rank. It does not receive the parent referent, the expected action, or the oracle file. A single candidate that says "Transfer 1000 rupees" is a well-formed transfer of 1000. The controller cannot know that the parent said 500 unless that value is leaked in, and leaking it would make the mutation test circular.

## Pipeline

1. An empty bundle returns HOLD / `EMPTY_BUNDLE` before modality analysis or `assess()`.
2. Missing or duplicate candidate ids return HOLD and do not commit.
3. Each candidate is read with the frozen lexical `assess()` and `frame_is_complete()`, plus `analyze_modality()` and `unrecognized_values()`.
4. A raw proposal is built. Two intents in one string become CLARIFY. Two different complete frames become HOLD when the critical-slot switch is on. Otherwise the earliest complete frame is CONTINUE if it is rank 0, or RETRY if recovery is on.
5. `apply_gate()` copies that proposal into a normalized decision. It does not edit the raw object. HOLD and CLARIFY stay uncommitted. CONTINUE and RETRY commit only when the candidate id is in the bundle, the modality switches allow execution, the frame values occur in that candidate's text, and no out-of-inventory critical span is present.
6. If the first proposal fails the gate, recovery may try a later candidate. A conflicting pair is not retried into a commit.
7. The normalized decision stores the candidate id with status `CONTROLLER_EMITTED`. The evaluator does not invent that id.

## Switches

All default to on: modality, polarity, critical slots, provenance, conditionality, gate, recovery, and risk. The risk score is a sum of flags. It cannot override a failed gate. Turning the gate off is the ablation that lets the raw proposal commit. Polite wording (`please`, `could you`, `can you`) stays execution-ready. The month `May` is not the modal `may`. `cancel` is not negation.

## What this cannot detect

An in-inventory swap, such as 7 AM to 8 AM or 500 to 1000, still produces a complete frame whose values are in the candidate text. v5 commits it. The oracle, which knows the parent, marks that commit unsafe. That gap is a result, not a leak to close.

Out-of-inventory values such as April 3 and 181 do not match the closed lexicon, so the frame is incomplete and the verifier records `OUT_OF_INVENTORY`. The controller can hold those without seeing the referent.

## Oracle

`phase5_oracle.py` labels cases from the transformation name. It does not import the controller. The labels are a specification table written in the same session as the controller. They are not human gold and they are not an independent discovery of the rules.
