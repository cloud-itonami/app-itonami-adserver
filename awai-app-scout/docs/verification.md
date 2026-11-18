# Verification (AWAI-3335, 2026-11-18)

Nothing here proves distribution, production signing, live bot operation, or that a real export exists.

## Source

- `npm test`: 6/6.
  - The bundled profile is `adnetwork-scout` at `f5b8883067cc`. The sha256 values of `profile.yaml`, `itonami.edn`, `SOUL.md` and `cron/jobs.json` match the files in this repository, and each limit sentence appears verbatim in `SOUL.md`.
  - The descriptor passes the canonical runtime. The derived `connect-src` is exactly `https://raw.githubusercontent.com`, the value in `tauri.conf.json` and `index.html`.
  - Only the export URL matches. POST, a query, another file, another branch and another repository do not.
  - The fixture `test/fixtures/export-synthetic.json` is **synthetic**: `scripts/adnetwork_public_export.py` produced it from four made-up rows, and withheld one for an e-mail-like name. It is accepted, and the summary counts per network and compares observation times as instants.
  - Refused: `notes` or `raw_json` in a row, an e-mail-like value, an `http:` or `javascript:` evidence URL, a non-domain key, a time without a zone, a padded name, a bad kind, a wrong count, schema, profile or field list.
- `python3 -m unittest scripts/test_adnetwork_public_export.py` (repository root): 4/4. Only the six public columns are written, private values are absent, bad rows are withheld and counted, and the `.sha256` sidecar matches.
- Mutation check: disabling the e-mail-like check fails one app test and one exporter test.

## Browser (375 px, loopback static server)

- Deny: 「取得を中止しました。何も送信していません。」, and Resource Timing listed no external request.
- Allow once: exactly one request, to the export URL, which answered 404. The page showed 「export はまだ公開されていません（404）。件数は 0 ではなく不明です。」
- The screen that lists records was **not** exercised with data in the browser. No real export is published. The broker keeps its own `fetch`, so a page-level substitute could not stand in (which is the intended behaviour). The domain tests cover the parsing and the summary; the rendering is unverified until the first export is published.

## Device: Awai OS x86_64

The adb-connected Awai OS desktop: `Generic_x86_64` LineageOS-based Android 17, `CP2A.260605.016`, not an emulator. The x86_64 debug APK has sha256 `c0e12340345adc449f9fda4f3b3a1a62ce83a69e652bf06cf25280cdfb011fbc` and is signed with the debug identity only. It installed and launched (TotalTime 295 ms) with the profile card and the read button (`android-x86-01-launch.png`). This device has no internet route, so no read was attempted there. The app was uninstalled afterwards.

## Real export: not produced

`scripts/adnetwork_public_export.py` against the catalog failed with **RESTError 403 Forbidden** on 2026-11-18. The Keychain item `gftd.cf` / `API_TOKEN` exists but is not allowed to read the R2 Data Catalog (expired, or missing the permission). Scout's SOUL says to stop on 403 and not to try other credentials, so nothing was published. An empty file was not published either, because it would claim zero advertisers.
