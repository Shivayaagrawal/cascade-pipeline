# Phase 0.5 licensing audit

**Date:** 2026-11-02.  
**Status:** NOT READY FOR PHASE 1.  
**Scope:** Documentation review only. No dataset archive, no package install, no virtual environment, no dataset clone, no `src/`, no experiments.

This note is not legal advice and is not an owner acceptance.

## Gates

| Gate | Result |
|------|--------|
| A — rows reviewed | Complete. Evidence and an owner decision are on every register row. Unresolved legal points stay Pending. |
| B — required artifacts Accepted | Not met. FSC, SLURP audio, and SLURP text are Pending. |
| C — owner approves Phase 1 | Not met. Cursor did not authorize Phase 1. |

## Completed checks

- Fluent.ai dataset page re-read. It says academic research only, names CC BY-NC-ND 4.0, and links https://fluent.ai/wp-content/uploads/2021/04/Fluent_Speech_Commands_Public_License.pdf as the full license.
- The page’s dataset access link is https://groups.google.com/a/fluent.ai/forum/#!forum/fluent-speech-commands. No version or checksum is on that link. The group was not joined.
- https://www.fluent.ai/research/fluent-speech-commands/ timed out. It is not a verified download channel in this pass.
- https://github.com/GrindstoneLZX/FluentSpeechCommandsDataset was not fetched and not cloned.
- Fluent Speech Commands Public License PDF re-read. Grant is reproduce but not Share, for NonCommercial and academic purpose only. The same sentence says commercial purpose is not authorized, including training, testing, bench-marking, industrial research, or developing a product.
- CC BY-NC-ND 4.0 legal code read because the page names it. It is not the file linked as the full license.
- Zenodo 10.5281/zenodo.4274930 version 1.0 record read. `LICENSE.txt` fetched. It states CC BY-NC 4.0. `slurp_real.tar.gz` and `slurp_synth.tar.gz` were not downloaded. Printed md5 values were not recomputed.
- CC BY-NC 4.0 legal code read. NonCommercial is defined by primary purpose, not by the word academic.
- GitHub `pswietojanski/slurp` inspected through the API and raw license/README URLs. Commit `8eb16545762be97ace75334109d73824217311f1` (2022-04-20). `LICENSE.txt` states CC BY 4.0 for the textual part and CC BY-NC 4.0 for audio. CC BY 4.0 legal code read. The repository was not cloned.

## Unresolved questions

1. Which FSC instrument governs a file from the Google Group?
2. Does the PDF allow this project’s noncommercial training and evaluation, given the commercial-purpose list?
3. What release id and checksum would an FSC download have to match?
4. Will the owner accept SLURP audio, SLURP text, both, or neither?
5. Is `slurp_synth` in or out of the acquisition list if audio is later accepted?

## Blocked artifacts

| Artifact | Owner decision | Effect |
|----------|----------------|--------|
| FSC audio and annotations | Pending | Acquisition blocked. Refusal would block the primary benchmark. |
| SLURP audio | Pending | Acquisition blocked. Refusal would block SLURP audio experiments under that license. |
| SLURP text | Pending | Acquisition blocked. |
| SLURP `usrid` metadata | Pending | Do not publish those attributes. |
| ATIS | Pending, and out of implementation | Not required for Gate B. |
| Google Speech Commands | Pending | Optional. Not required for Gate B. |

No row is Refused, because the owner did not refuse one in this pass. No row is Accepted.

## Exact next action

The owner writes Accepted or Refused for FSC, SLURP audio, and SLURP text in `docs/DATASET_LICENSE_REGISTER.md`. That act is Gate B only if every required artifact is Accepted. Phase 1 still needs a separate approval after that. Do not start Phase 1 from this audit.
