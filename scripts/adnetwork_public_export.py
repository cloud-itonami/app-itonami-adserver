#!/usr/bin/env python3
"""Write the public, static export of adnetwork-scout's advertiser observations.

Owner decision 2026-11-18 (AWAI-3335): scout's read surface is a static public
export committed to this public repository and read from
raw.githubusercontent.com. No server answers requests for it.

Only these columns of `cloud_itonami.adnetwork_advertiser` are published:
network, advertiser_key, advertiser_name, evidence_url, observed_at, kind.
`notes`, `raw_json`, `record_id`, `ingested_at` and everything the outreach
tick writes stay private. A row that fails a check (an e-mail-like value, a
non-https or credentialed evidence URL, a timestamp without a zone, an
unexpected shape) is withheld, not repaired; the export says how many.

Read-only against the catalog. The token is resolved by the shared
`datalake_catalog` module (env or Keychain) and is never printed.

  python3 scripts/adnetwork_public_export.py --out public/adnetwork-scout
  python3 scripts/adnetwork_public_export.py --rows rows.json --out DIR   # offline
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys

SCHEMA = "awai.adnetwork-scout.public-export.v1"
CATALOG = ("cloud_itonami", "adnetwork_advertiser")
FIELDS = ["network", "advertiserKey", "advertiserName", "evidenceUrl", "observedAt", "kind"]
SOURCE_COLUMNS = {
    "network": "network",
    "advertiserKey": "advertiser_key",
    "advertiserName": "advertiser_name",
    "evidenceUrl": "evidence_url",
    "observedAt": "observed_at",
    "kind": "kind",
}
FILE = "advertisers.v1.json"

NETWORK = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
KEY = re.compile(r"^(?=.{3,253}$)[a-z0-9-]+(\.[a-z0-9-]+)+(/[A-Za-z0-9._~-]+)*$")
KIND = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
URL = re.compile(r"^https://[A-Za-z0-9.-]+(:[0-9]{1,5})?(/[^\s@]*)?$")
STAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:\d{2})$")


def public_row(row: dict) -> dict | None:
    """Project one catalog row to the public shape, or None to withhold it."""
    out = {k: row.get(src) for k, src in SOURCE_COLUMNS.items()}
    for v in out.values():
        if v is not None and not isinstance(v, str):
            return None
        if isinstance(v, str) and "@" in v:
            return None
    if not (out["network"] and NETWORK.match(out["network"])):
        return None
    if not (out["advertiserKey"] and KEY.match(out["advertiserKey"])):
        return None
    if not (out["evidenceUrl"] and URL.match(out["evidenceUrl"])):
        return None
    if not (out["observedAt"] and STAMP.match(out["observedAt"])):
        return None
    if out["kind"] is not None and not KIND.match(out["kind"]):
        return None
    name = out["advertiserName"]
    if name is not None:
        name = name.strip()
        if not name or len(name) > 200 or any(ord(c) < 32 for c in name):
            return None
        out["advertiserName"] = name
    return out


def build(rows: list[dict], snapshot_id: str | None, generated_at: str) -> dict:
    kept, withheld = [], 0
    seen = set()
    for row in rows:
        pub = public_row(row)
        if pub is None:
            withheld += 1
            continue
        ident = tuple(pub[k] or "" for k in FIELDS)
        if ident in seen:
            continue
        seen.add(ident)
        kept.append(pub)
    kept.sort(key=lambda r: (r["network"], r["advertiserKey"], r["kind"] or "", r["evidenceUrl"], r["observedAt"]))
    return {
        "schema": SCHEMA,
        "source": {"profile": "adnetwork-scout",
                   "catalog": ".".join(CATALOG),
                   "snapshotId": snapshot_id},
        "generatedAt": generated_at,
        "fields": FIELDS,
        "count": len(kept),
        "withheld": withheld,
        "advertisers": kept,
    }


def encode(export: dict) -> bytes:
    return (json.dumps(export, ensure_ascii=False, indent=1, sort_keys=False) + "\n").encode()


def write(export: dict, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    body = encode(export)
    digest = hashlib.sha256(body).hexdigest()
    with open(os.path.join(out_dir, FILE), "wb") as f:
        f.write(body)
    with open(os.path.join(out_dir, FILE + ".sha256"), "w") as f:
        f.write(f"{digest}  {FILE}\n")
    return digest


def catalog_rows(root_scripts: str) -> tuple[list[dict], str | None]:
    sys.path.insert(0, root_scripts)
    from datalake_catalog import connect  # noqa: E402  (shared connection, token never printed)
    table = connect().load_table(CATALOG)
    snap = table.current_snapshot()
    return table.scan().to_arrow().to_pylist(), (str(snap.snapshot_id) if snap else None)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--rows", help="offline: a JSON array of catalog rows instead of reading the catalog")
    ap.add_argument("--root-scripts",
                    default=os.path.expanduser("~/github/com-junkawasaki/root/scripts"))
    args = ap.parse_args(argv)
    if args.rows:
        with open(args.rows) as f:
            rows, snap = json.load(f), None
    else:
        rows, snap = catalog_rows(args.root_scripts)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    export = build(rows, snap, now)
    digest = write(export, args.out)
    print(f"EXPORT\trows={len(rows)}\tcount={export['count']}\twithheld={export['withheld']}\tsha256={digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
