# Evidence Hasher + Manifest
Creates and verifies a SHA-256 manifest for files. Useful for audit handoffs and integrity checks.

## Run
```bash
python3 evidence_hasher.py hash --path ./samples
python3 evidence_hasher.py verify --manifest manifest.json

## Notes
- `manifest.json` stores size, mtime, and SHA-256 per file.
- If a file changes, verification will show a mismatch.

**Demo**
1) Verify OK → `verified: true`
2) Tamper: `echo "tamper" >> samples/note.txt`
3) Verify again → `verified: false`
4) Re-hash → `verified: true`
