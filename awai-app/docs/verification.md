# Verification (AWAI-3260, 2026-11-18)

Source, build, browser and device evidence are recorded separately. Nothing here proves distribution (Itonami Store), production signing, live bot operation or advertiser funding.

## Source

- `npm test`: 7/7 pass. The fixtures are the real public responses captured on 2026-11-17T17:22Z (`test/fixtures/`).
  - The bundled profile is `murakumo-adnetwork`, and the sha256 of `profile.yaml`, `itonami.edn` and `cron/jobs.json` under `../hermes/profiles/murakumo-adnetwork/` equal the recorded digests. A different profile id, a profile without `propose-only`, or a non-itonami runtime is refused.
  - The descriptor passes the canonical runtime, and the derived `connect-src` is exactly `https://murakumo.cloud`, which is the value in `src-tauri/tauri.conf.json` and `public/index.html`.
  - Only the two declared URLs match. These do not: `?refresh=1`, POST, `/api/v1/free/impression`, `/api/v1/free/funding`, `https://ads.x402.nexus/campaigns`.
  - Live state: inventory `measured: false, stale: true`; free tier `house-sponsorship` with `advertiserFunded: 0`; verdict `unknown` (`inventory-unmeasured`, `inventory-stale`, `no-advertiser-funding`).
  - Negative controls: `advertiser-funded` only with a fresh measured inventory that has an active advertiser campaign and a free tier that counts one. Both zero and measured gives `house-only`. One source missing, stale, or the two disagreeing gives `unknown`. Wrong types, an unknown funding source, `active > campaigns`, a measured report without counts, and `advertiser` funding with 0 campaigns (or the reverse) are refused.
- Mutation check: changing the `advertiser-funded` rule from "both sources" to "either source" makes the negative-control test fail.

## Build

- `npm run build`: the canonical runtime and consent CSS match `vendor/PINS.json` (kotoba-lang/kotoba `91ed14c`), and the Awai UI tarball and its package files match `vendor/awai-ui-pin.json`. `dist/release.json` lists sha256 values for every file.
- `npm run build:android`: arm64 debug APK `network.itonami.koukoku` 0.1.0 (versionCode 1000, targetSdk 37, minSdk 35 from `tauri.conf.json`), sha256 `90656f988d1378badeab1f1f55a6f4eaeb91f6dd4020e7adb9a3ef977bdc89fb`. It is signed with the local debug identity and is not a release.
- The Android Gradle files carry Rodo's changes: the build task resolves the pinned local Tauri CLI, cleartext traffic and JNI debugging are off, the NDK version is pinned, and Gradle VFS watching is off.
- `npm run build:android:x86` (AWAI-3323, 2026-11-18): x86_64 debug APK, same package and versions, sha256 `c39ca13de05ce4381a8e95d974b9d14438c6c1903b7efb278ef9441e651331ae`, one native library `lib/x86_64/libitonami_koukoku_lib.so`. In a fresh checkout the first run failed in `:app:compileUniversalDebugKotlin` (`Unresolved reference 'PluginManager'`), because Tauri writes `gen/android/tauri.settings.gradle` during that run; the second run, with no change, succeeded. Debug identity only, not a release.

## Browser (375 px, loopback static server)

- Deny: the page showed 「取得を中止しました。何も送信していません。」 After that, one allow for each of the two reads; the page's Resource Timing list then held exactly two murakumo.cloud entries, one per allow, so the deny sent nothing.
- Allow once on both: the page showed the live verdict 「判定できません」 with the three reasons above.

## Device: disposable AOSP emulator

`sdk_phone64_arm64` Android 15 (`AE3A.240806.019`, userdebug, no Google services), a new AVD `Awai_Koukoku_AWAI3260` started with `-wipe-data` on port 5820. Other sessions' emulators were not touched. The emulator was stopped after the check.

| Step | Result | Evidence |
| -- | -- | -- |
| Install and launch | ok (TotalTime 1192 ms). The profile card shows the bot id, role, runtime, schedules and the propose-only notice. | `android-01-launch.png` |
| Read inventory | The canonical consent dialog shows the service, operation, capability, endpoint, GET path, data category and no redirects. | `android-02-consent.png` |
| Deny | 「取得を中止しました。何も送信していません。」, and the verdict stays 「未取得」. | `android-03-denied.png` |
| Allow once (inventory, then free tier) | 「判定できません」: inventory not measured, inventory stale, 0 advertiser-funded campaigns. Free tier: available, house-sponsorship, 10000 micros / 5 per day. | `android-04-after-allow.png` |

## Device: Awai OS x86_64 (AWAI-3323, 2026-11-18)

Not an emulator: an adb-connected Awai OS desktop, `Generic_x86_64` LineageOS-based Android 17 (`CP2A.260605.016`, userdebug, release-keys), 1920x1200, Awai home `network.awai.home`. The device had no default route and no DNS (only `10.77.0.0/24` to the host), and its network settings were not changed. The app was uninstalled after the check, leaving the device's package list as found.

| Step | Result | Evidence |
| -- | -- | -- |
| Install and launch | ok (TotalTime 428 ms), same profile card as on arm64, laid out for a wide screen. | `android-x86-01-launch.png` |
| Read inventory | The canonical consent dialog, identical fields to arm64. | `android-x86-02-consent.png` |
| Deny | 「取得を中止しました。何も送信していません。」, verdict stays 「未取得」. | `android-x86-03-denied.png` |
| Allow once (inventory, then free tier) | Each allow led to a fetch that failed with no network: 「取得できません: Failed to fetch」, and the verdict stays 「未取得」 (no partial or guessed verdict). The live verdict on a connected device is the arm64 row above. | `android-x86-04-offline.png` |

## Not verified / known gaps

- Network silence after a deny on the device was not captured at packet level. It rests on the canonical broker (which fetches only after approval), the browser Resource Timing count and the unchanged verdict on the device.
- The `advertiser-funded` and `house-only` UI paths were exercised only in the domain tests, because no advertiser funds the network today and the inventory is unmeasured.
- The x86_64 device run had no internet, so a successful live read was shown only on the arm64 emulator and in the browser. No phone hardware run, Itonami Store enrollment, production signing or NixOS package.
- The ad-server Worker at the repository root was not changed. Its custom domain `ads.x402.nexus` did not resolve in DNS on 2026-11-18.
