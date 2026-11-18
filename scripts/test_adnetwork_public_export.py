"""python3 -m unittest scripts/test_adnetwork_public_export.py"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import adnetwork_public_export as ex  # noqa: E402

GOOD = {
    "record_id": "r1", "network": "exoclick", "advertiser_key": "brand.example.com",
    "advertiser_name": "Example Brand", "evidence_url": "https://www.exoclick.com/advertisers/",
    "observed_at": "2026-09-05T09:00:00+09:00", "kind": "advertiser-page",
    "notes": "private note", "raw_json": "{\"secret\":1}", "ingested_at": "2026-09-05T00:00:00Z",
}


def row(**kw):
    r = dict(GOOD)
    r.update(kw)
    return r


class PublicExport(unittest.TestCase):
    def test_only_public_columns(self):
        e = ex.build([GOOD], "42", "2026-11-18T00:00:00Z")
        self.assertEqual(e["count"], 1)
        self.assertEqual(set(e["advertisers"][0]), set(ex.FIELDS))
        body = ex.encode(e).decode()
        for private in ("private note", "secret", "record_id", "ingested_at", "r1"):
            self.assertNotIn(private, body)

    def test_withheld(self):
        bad = [
            row(advertiser_name="Contact sales@brand.example.com"),
            row(evidence_url="http://www.exoclick.com/"),
            row(evidence_url="https://user:pw@exoclick.com/"),
            row(evidence_url="javascript:alert(1)"),
            row(advertiser_key="not a domain"),
            row(advertiser_key="Brand.Example.com"),
            row(observed_at="2026-09-05T09:00:00"),
            row(network=""),
            row(kind="Advertiser Page"),
            row(advertiser_name="   "),
            row(advertiser_name=7),
        ]
        e = ex.build(bad, None, "2026-11-18T00:00:00Z")
        self.assertEqual((e["count"], e["withheld"]), (0, len(bad)))

    def test_nullable_and_dedupe_and_order(self):
        e = ex.build([row(advertiser_key="z.example.com", kind=None, advertiser_name=None),
                      GOOD, row(record_id="r2")], None, "t")
        self.assertEqual(e["count"], 2)
        self.assertEqual([a["advertiserKey"] for a in e["advertisers"]],
                         ["brand.example.com", "z.example.com"])

    def test_digest_file(self):
        with tempfile.TemporaryDirectory() as d:
            digest = ex.write(ex.build([GOOD], None, "t"), d)
            import hashlib
            with open(os.path.join(d, ex.FILE), "rb") as f:
                self.assertEqual(hashlib.sha256(f.read()).hexdigest(), digest)
            with open(os.path.join(d, ex.FILE + ".sha256")) as f:
                self.assertEqual(f.read(), f"{digest}  {ex.FILE}\n")
            with open(os.path.join(d, ex.FILE)) as f:
                self.assertEqual(json.load(f)["schema"], ex.SCHEMA)


if __name__ == "__main__":
    unittest.main()
