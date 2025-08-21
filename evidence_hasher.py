#!/usr/bin/env python3
import argparse, hashlib, json, os
from pathlib import Path
from datetime import datetime, timezone

TOOL_VERSION = "1.0.0"

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def walk_files(path: Path):
    if path.is_file():
        yield path
    else:
        for root, _, files in os.walk(path):
            for fn in files:
                yield Path(root) / fn

def manifest_from_path(path: Path):
    base = path if path.is_dir() else path.parent
    entries = []
    for p in sorted(walk_files(path)):
        if p.name == "manifest.json":
            continue
        st = p.stat()
        entries.append({
            "path": str(p.relative_to(base)),
            "size": st.st_size,
            "modified": int(st.st_mtime),
            "sha256": sha256_file(p),
        })
    return {
        "tool": "evidence_hasher",
        "version": TOOL_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(base.resolve()),
        "entries": entries
    }

def verify_manifest(manifest_path: Path):
    man = json.load(open(manifest_path))
    root = Path(man.get("root", "."))
    results = []
    for e in man.get("entries", []):
        f = root / e["path"]
        ok = f.exists() and f.is_file()
        actual = sha256_file(f) if ok else None
        results.append({
            "path": e["path"],
            "exists": ok,
            "expected": e["sha256"],
            "actual": actual,
            "match": (actual == e["sha256"]) if actual else False
        })
    return results

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("hash");   h.add_argument("--path", required=True)
    v = sub.add_parser("verify"); v.add_argument("--manifest", required=True)
    a = ap.parse_args()

    if a.cmd == "hash":
        man = manifest_from_path(Path(a.path))
        json.dump(man, open("manifest.json", "w"), indent=2)
        print(f"Wrote manifest.json with {len(man['entries'])} entries.")
    else:
        res = verify_manifest(Path(a.manifest))
        ok = all(r.get("match") for r in res if r.get("expected"))
        print(json.dumps({"verified": ok, "results": res}, indent=2))
