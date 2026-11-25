#!/usr/bin/env bash
# Rebuild every output from the raw sources. Run from anywhere.
#   1. download sources (skips files already present)
#   2. extract text, 3. verify DOIs, 4. build tables and web JSON, 5. run tests, 6. checksums
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -I scripts/fetch_sources.py
uv run -q --with pymupdf==1.26.* python -I scripts/extract_all.py >/dev/null
python3 -I scripts/verify_dois.py >/dev/null
uv run -q --with pymupdf==1.26.* python -I scripts/build.py
python3 -I -m unittest discover -s tests -q
node --test tests/rcv.test.ts >/dev/null && echo "typescript tests: ok"
find . -type f ! -path './.git/*' ! -path './.venv/*' ! -path './.pytest_cache/*' ! -path '*/__pycache__/*' ! -name SHA256SUMS -print0 | sort -z | xargs -0 shasum -a 256 > SHA256SUMS
echo "done"
