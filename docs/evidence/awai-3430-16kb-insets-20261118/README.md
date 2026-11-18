# 16 KB alignment and system-bar insets: Koukoku and Koukoku Scout (2026-11-18)

Tracking: AWAI-3430, child of the template-wide AWAI-3393. Same change as Hiring (AWAI-3392).

## Change

- `awai-app/src-tauri/build.rs` and `awai-app-scout/src-tauri/build.rs` link with `-Wl,-z,max-page-size=16384`, for Android targets only.
- `MainActivity.kt` in both apps:
  - The system bars, display cutout and IME bottom become padding on the content view.
  - The decor colour follows `@awai/ui` `--awai-background`: `#ffffff` light, `#14110f` dark.
  - Bar icons switch between light and dark, including on a live theme switch. `uiMode` is already in the manifest's `configChanges`.

## Build

The shared AWAI-3393 build lock was held from 05:09:58 to 05:22:29 UTC.

Command: `CARGO_BUILD_JOBS=4 nice -n 10 sh -c 'npm run build && npx tauri android build --apk --debug --target aarch64'`, after deleting `outputs/apk`, `intermediates/apk` and `intermediates/incremental`.

| App | APK bytes | APK sha256 | ELF LOAD segments | `zipalign -c -P 16 -v 4` |
| -- | -- | -- | -- | -- |
| Koukoku | 29,472,895 | `6c5666d671181a7de806892ce78636fa9db68615ba6464737b5abe4f16684f14` | 4, all `Align 0x4000` | OK |
| Koukoku Scout | 29,516,673 | `a222f714a2d89285d9fc9e53ab650e06adf0165ca90c2a8441966a62f21b88b7` | 4, all `Align 0x4000` | OK |

Debug identity only, not a release.

## VM

Disposable `sdk_phone64_arm64` Android 15 (`AE3A.240806.019`), 1080x1920, 3-button navigation. It was a new AVD started with `-wipe-data`; it was stopped and deleted after the check.

- WebView bounds were `[0,63]-[1080,1796]` (Koukoku) and `[0,63]-[1080,1794]` (Scout). The content starts below the status bar and ends above the navigation bar.
- Light and dark:
  - The bar colour and icons follow the theme (`*-light-top.jpg`, `*-dark-top.jpg`).
  - The page follows a live switch. On this software-rendered VM the repaint lagged a few seconds: `koukoku-dark-bottom.jpg` shows dark bars around the page before it turned dark, and `koukoku-dark-top.jpg` was taken after.
- First paint took about 30 s on this loaded host (load 50 to 60).

## Not established

The VM uses 4 KB pages (`getconf PAGE_SIZE` = 4096), so it cannot show the 16 KB compatibility warning either way. The fix is shown by the ELF alignment above. A run on a 16 KB-page or moto g05 device is still to do.
