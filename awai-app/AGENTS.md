# Koukoku

Follow the workspace AGENTS.md, including the Kotoba end-user apps contract.

- The common domain is `.cljc` (`src/koukoku/domain.cljc`), and the UI is CLJS through Squint with the pinned `@awai/ui`. Tauri v3 is a thin host. Do not fork the UI components or the consent logic.
- Every external request goes through the canonical client runtime broker with `each-operation` consent. Add a route only by declaring it in `koukoku.domain/operations`. Keep the CSP `connect-src` equal to `clientRuntimeConnectSrc` of the descriptor.
- The funding verdict stays fail-closed: an unmeasured or stale inventory is never read as "no campaigns", and a shape that cannot be verified is refused rather than shown.
- `profiles/paired-profile.json` is a copy of `../hermes/profiles/murakumo-adnetwork`. Regenerate it from those files and update the recorded revision and digests; do not edit fields by hand.
- Do not submit ads, write KV, trigger `?refresh=1`, serve, bill, or launch or reconfigure the bot from this app. Those need separate owner approval (AWAI-420).
- Keep source, build, device, distribution and live-operation evidence separate, and record unknowns as unknown.
