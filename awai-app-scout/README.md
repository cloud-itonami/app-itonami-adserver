# Koukoku Scout

The Awai app paired one-to-one with the `adnetwork-scout` bot profile (`../hermes/profiles/adnetwork-scout`). It is a Tauri v3 app, Android first. Tracking: AWAI-3335 (parent AWAI-3241).

The bot collects publicly observable advertiser information from ad networks into a private R2 Iceberg table. By owner decision (2026-11-18), its read surface is a **static public export**: `public/adnetwork-scout/advertisers.v1.json` in this public repository, read from `raw.githubusercontent.com`. No server answers requests for it. The app:

- shows the bundled profile: role, runtime, schedules and the limits stated in its SOUL;
- reads the export once per tap, after the canonical consent dialog. Deny sends nothing;
- refuses a file that breaks the publishing rules, and shows a 404 as "not published", not as zero;
- shows the counts (records, advertisers per network, withheld, newest observation, generated time and staleness), the file's sha256, and the records with their evidence URLs.

It is read-only. It sends no outreach and does not write the catalog.

## Develop

```bash
npm ci
npm test                     # domain, descriptor, CSP, routes, exporter output, refusals
npm run build                # dist/ with dist/release.json
npm run build:android:x86    # x86_64 debug APK (in a fresh checkout the first run can fail on 'PluginManager'; run it again)
npm run build:android        # arm64 debug APK
python3 scripts/paired_profile.py   # after the profile changes
```

See `docs/verification.md` for what has and has not been verified.
