# Phase 1D.4 approval record

**Date:** 2026-11-02  
**Status:** APPROVED  
**Applies to:** the Phase 1D.3 experimental protocol as a methodology.  
**Does not apply to:** dataset acquisition, licence acceptance, storage changes, Phase 1E, or Phase 2 implementation.

## Why this status

The protocol meets the review gate:

- RQ1–RQ4 are scoped and falsifiable. Speech, N-best, and human action labels stay outside the current evidence.
- B0, B1, and B2 comparisons that share a reader are separated from the prefix-to-lexical reader change.
- Metric denominators match `experiments/sim-eval-v3/report.json`. Selective risk and unsafe commits are 3/145. Zero commits leave the rate undefined. The 142/200 abstention column is the selective layer on the same 200 ids as the 145/200 coverage count, and 142 + 3 = 145.
- Derived recovery labels are not described as human gold. A simulated retry is correct only when the committed frame matches gold.
- No interval or significance test is claimed. The `min_support` curve stays intact.
- Seed 17, immutable directories, the hash manifest, and test-set isolation are specified.
- The open wording notes I-2 and I-3 in `docs/PHASE_1D4_ISSUES_REGISTER.md` do not contradict a stored result.

## What remains unauthorized

Phase 1E stays blocked. SLURP stays unauthorized. The project cap stays 5,000,000,000 bytes. Phase 2 does not start from this approval. A later implementation plan needs its own decision and a new output directory.

## Integrity commands

Run from `/Users/shivanyaagrawal/cnn/CascadeGuard` on 2026-11-02. No experiment runner was executed. `test-clean` contents were not read.

Hash check, comparing each file with the preservation set in `docs/PHASE_1D3_REPRODUCIBILITY_PROTOCOL.md`:

```text
python3 - <<'PY'
import hashlib
from pathlib import Path
root = Path('/Users/shivanyaagrawal/cnn/CascadeGuard')
expected = {
    'experiments/B0/summary.json': '3873057391b2f36727f503a4d504ddea9453472e6d518a63a2fef2481ae850ee',
    'experiments/B1/summary.json': '597a2800c946018467865dfcf3d8e547bc51c10487596cc134ca2181fee695b2',
    'experiments/B2/summary.json': '34a40fdd233f5d4faa00af73c26f1afcc32c4d83922db8df57b7a7184dce0e5d',
    'artifacts/reports/simulation_report.json': '7adf69ee6ac344e7ef205099af3686ddf7cceaffa111a8789f03b83ed8319856',
    'experiments/sim-eval-v2/report.json': '74499b716103e26ef829cb56816bf738d67d3d3e5961848c4cfe37f2e8f4f77d',
    'experiments/sim-eval-v3/report.json': '7d1ca46400795908f6ffcd17091d4348e633493923fc030e5160e9f2ff8a8cd6',
    'experiments/sim-eval-v3b/report.json': '4c47b2b04e42b06972f7bd9e10da51d219d18a46e273d71fc50e78f2070631cf',
    'experiments/sim-eval-v3b/decision_log.jsonl': '9c486601dcac141ccf7453f84b144fbd5d5c491da1b1a32542e7a14a796a4e75',
    'configs/evaluation_v3.yaml': 'ac4bb7ea743195e6ea860a4f2c34dc546437321f28c811055782fe4b1c5ed842',
    'data/librispeech/annotations/phase_1c_pilot_30.csv': '56a4dc49b3a2f5add5c361c2b23edde923c8265a998de76c7e5b87462e5d6a5c',
}
ok = True
for rel, exp in expected.items():
    digest = hashlib.sha256((root / rel).read_bytes()).hexdigest()
    match = digest == exp
    ok = ok and match
    print(('OK' if match else 'CHANGED'), rel)
print('ALL_MATCH' if ok else 'MISMATCH')
PY
```

Result: `ALL_MATCH`, including

- `experiments/sim-eval-v3/report.json` `7d1ca46400795908f6ffcd17091d4348e633493923fc030e5160e9f2ff8a8cd6`
- `experiments/sim-eval-v3b/decision_log.jsonl` `9c486601dcac141ccf7453f84b144fbd5d5c491da1b1a32542e7a14a796a4e75`
- `data/librispeech/annotations/phase_1c_pilot_30.csv` `56a4dc49b3a2f5add5c361c2b23edde923c8265a998de76c7e5b87462e5d6a5c`

Archive names:

```text
find data -type f \( -name '*.tar.gz' -o -name '*.zip' -o -name '*.tgz' \) -print
```

Output:

```text
data/librispeech/archives/test-clean.tar.gz
data/librispeech/archives/dev-clean.tar.gz
```

Tests:

```text
python3 -m pytest -q
```

Output: `71 passed in 5.87s`.

The decision-log census that confirmed 145 commits, 142 frame matches, and 3 unsafe commits counted stored JSON fields only.
