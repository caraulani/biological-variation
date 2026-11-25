"""Fetch Crossref metadata for every DOI in data/references.json and write the verified
title, journal, year, volume and pages to data/doi_verification.csv. Raw responses are cached in
../_raw/crossref/."""
import csv, json, pathlib, subprocess, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT.parent / "_raw" / "crossref"

def crossref(doi):
    f = CACHE / (doi.replace("/", "_") + ".json")
    if not f.exists():
        out = subprocess.run(["curl", "-sSf", "-m", "60", "-A", "meaningful-change-build/1.0 (mailto:none)",
                              f"https://api.crossref.org/works/{doi}"], capture_output=True, check=True).stdout
        f.write_bytes(out); time.sleep(0.3)
    return json.loads(f.read_text())["message"]

def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    refs = json.loads((ROOT / "data" / "references.json").read_text())
    rows = []
    for r in refs:
        m = crossref(r["doi"])
        title = " ".join("".join(m.get("title", [""])).split())
        year = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
        rows.append({"ref_id": r["ref_id"], "doi": r["doi"], "crossref_title": title,
                     "journal": "".join(m.get("container-title", [""])), "year": year,
                     "volume": m.get("volume", ""), "pages": m.get("page", ""),
                     "first_author": (m.get("author") or [{}])[0].get("family", ""),
                     "doi_resolves": "yes"})
    with open(ROOT / "data" / "doi_verification.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    for r in rows:
        print(r["doi"], "|", r["year"], r["journal"][:25], "|", r["crossref_title"][:110])

if __name__ == "__main__":
    main()
