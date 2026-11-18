# adnetwork-scout public export

`advertisers.v1.json` (with `advertisers.v1.json.sha256`) is the static, public read surface of the `adnetwork-scout` bot (owner decision 2026-11-18, AWAI-3335). Koukoku Scout (`awai-app-scout/`) reads it from `https://raw.githubusercontent.com/network-awai/app-itonami-adserver/main/public/adnetwork-scout/advertisers.v1.json`.

**Not published yet.** The first export is blocked: the catalog token returned 403 on 2026-11-18.

Public columns are only `network`, `advertiserKey`, `advertiserName`, `evidenceUrl`, `observedAt` and `kind`. `notes`, `raw_json`, `record_id`, `ingested_at` and outreach records stay private. Rows that fail the checks are withheld and counted in `withheld`.

## Publish (a reviewed PR, never an automatic push)

```bash
python3 scripts/adnetwork_public_export.py --out public/adnetwork-scout   # needs pyiceberg and a catalog token with read access
git diff --stat public/adnetwork-scout                                    # review the rows before committing
```

Open a PR with the two files, review the rows, and merge. Merging to `main` publishes them.
