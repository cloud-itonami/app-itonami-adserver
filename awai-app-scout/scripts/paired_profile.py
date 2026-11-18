#!/usr/bin/env python3
"""Regenerate profiles/paired-profile.json from ../hermes/profiles/adnetwork-scout.

  python3 scripts/paired_profile.py      (run from awai-app-scout/, after the profile changes are committed)
"""
import hashlib, json, subprocess

D = '../hermes/profiles/adnetwork-scout/'
OUT = 'profiles/paired-profile.json'
LIMIT_MARKS = ('nothing is ever sent', 'Never write credentials', 'Do not touch other tables')


def read(f): return open(D + f, encoding='utf-8').read()
def sha(f): return hashlib.sha256(open(D + f, 'rb').read()).hexdigest()
def sentence(line): return line if line.endswith('.') else line[:line.rindex('.') + 1]


rev = subprocess.check_output(['git', '-C', '..', 'log', '-1', '--format=%H', '--', 'hermes/profiles/adnetwork-scout']).decode().strip()
jobs = json.load(open(D + 'cron/jobs.json'))
jobs = jobs.get('jobs', jobs) if isinstance(jobs, dict) else jobs
limits = [sentence(l.strip()) for l in read('SOUL.md').splitlines() if any(m in l for m in LIMIT_MARKS)]
doc = {
    "schema": "awai.koukoku-scout.paired-profile.v1",
    "provenance": {
        "repository": "network-awai/app-itonami-adserver",
        "path": "hermes/profiles/adnetwork-scout/",
        "revision": rev,
        "transformation": "profile.yaml and itonami.edn copied verbatim as text; from SOUL.md only the sentences stating its limits, cut at the sentence end; cron jobs reduced to name, schedule display and enabled; sha256 of each source file recorded",
        "sources": {f: sha(f) for f in ["profile.yaml", "itonami.edn", "SOUL.md", "cron/jobs.json"]},
    },
    "profile": {
        "id": "adnetwork-scout",
        "profile.yaml": read('profile.yaml'),
        "itonami.edn": read('itonami.edn'),
        "authority": limits,
        "cron": [{"name": j["name"], "schedule": j["schedule"].get("display") or j["schedule"].get("expr"), "enabled": j["enabled"]} for j in jobs],
    },
}
with open(OUT, 'w') as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(OUT, rev[:12])
