# Phase 1B acquisition audit

**Audit date:** 2026-11-02  
**Result:** Both archives match the official MD5 list. They were copied into the project. The Downloads originals were left in place.

## Owner decision

D-LS-001 records the owner statement communicated at 2026-11-02T10:36:00+05:30 and written into the decision log at 2026-11-02T10:42:27Z. CC BY 4.0 is accepted for this research use. `dev-clean.tar.gz` and `test-clean.tar.gz` are authorized, including extraction. No signature or legal opinion is claimed.

## Files

| Archive | Downloads path | Project path | Bytes |
|---------|----------------|--------------|------:|
| `dev-clean.tar.gz` | `/Users/shivanyaagrawal/Downloads/dev-clean.tar.gz` | `data/librispeech/archives/dev-clean.tar.gz` | 337,926,286 |
| `test-clean.tar.gz` | `/Users/shivanyaagrawal/Downloads/test-clean.tar.gz` | `data/librispeech/archives/test-clean.tar.gz` | 346,663,984 |

The project copies were hashed again and matched the Downloads files. Neither original was deleted.

## Checksums

`md5sum.txt` was retrieved again from `https://openslr.trmal.net/resources/12/md5sum.txt` during preparation. The local copy is `data/librispeech/metadata/openslr_md5sum.txt` (600 bytes).

| Archive | MD5 | Official MD5 | SHA-256 |
|---------|-----|--------------|---------|
| dev-clean | `42e2234ba48799c1f50f24a7926300a1` | match | `76f87d090650617fca0cac8f88b9416e0ebf80350acb97b343a85fa903728ab3` |
| test-clean | `32fa31d27d2e1cad72775fee3f4849a9` | match | `39fde525e59672dc6d1551919b1478f724438a95aa55f874b576be21967e6c23` |

SHA-256 has no expected value in `md5sum.txt`. It is the local reproducibility digest.

## Provenance limit

`kMDItemWhereFroms` on both Downloads files is `https://chatgpt.com/`, received by Brave. That is not an OpenSLR host. Filesystem created times are 2026-11-02T10:15:06Z and 2026-11-02T10:15:14Z. Modified times are 2026-11-02T10:26:17Z and 2026-11-02T10:29:15Z. Those are local file dates. `downloaded_at` remains null. The declared file URLs are the OpenSLR `openslr.trmal.net` URLs. The MD5 match is the integrity evidence.

## Extraction index

Extraction of each archive into its own directory wrote 2,805 and 2,712 regular files. A later run found those files already present at the same sizes and did not overwrite them. No absolute paths, `..` members, or links were accepted by the extractor.
