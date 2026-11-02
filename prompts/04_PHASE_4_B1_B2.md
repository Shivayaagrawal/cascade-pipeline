Implement B1 multi-candidate and B2 failure-aware controller.

First inspect whether the selected ASR actually exposes genuine N-best hypotheses.

If not:

- Do not label synthetic variants as N-best.
- Use independent decoding configurations only as explicitly labelled candidate sources, or mark N-best unavailable.

Evaluate NLU for each candidate.

Implement transparent candidate scoring and configurable risk rules.

Controller actions:

- CONTINUE
- RETRY
- CLARIFY
- HOLD

Log each trigger and decision.

Do not execute real-world actions.
