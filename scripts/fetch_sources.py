"""Download every source listed in scripts/sources.json into ../_raw/meaningful-change/<id>/.
PDFs from repositories, PMC full text as JATS XML from Europe PMC. Skips files already present.
Sources marked "manual" must be saved by hand (see METHODS.md)."""
import json, pathlib, subprocess, sys, time, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT.parent / "_raw" / "meaningful-change"
UA = {"User-Agent": "Mozilla/5.0"}

def get(url, headers=UA):
    """Fetch with curl (some repositories refuse Python's default TLS client)."""
    cmd = ["curl", "-sSfL", "-m", "120"]
    for k, v in headers.items():
        cmd += ["-H", f"{k}: {v}"]
    return subprocess.run(cmd + [url], check=True, capture_output=True).stdout

def main():
    srcs = json.loads((ROOT / "scripts" / "sources.json").read_text())
    only = set(sys.argv[1:])
    for s in srcs:
        if only and s["id"] not in only:
            continue
        d = RAW / s["id"]; d.mkdir(parents=True, exist_ok=True)
        try:
            fetch_one(s, d)
        except Exception as e:  # keep going; report at the end
            print(f"FAILED: {s['id']}: {e}")
        time.sleep(0.5)

def fetch_one(s, d):
    if s.get("manual"):
        print(f"MANUAL: {s['id']}: {s['manual']}"); return
    if True:
        if s.get("pmcid"):
            out = d / "fulltext.xml"
            if not out.exists():
                out.write_bytes(get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{s['pmcid']}/fullTextXML"))
        elif s.get("nva"):
            out = d / "paper.pdf"
            if not out.exists():
                pub, f = s["nva"]
                link = json.loads(get(f"https://api.nva.unit.no/publication/{pub}/filelink/{f}", {**UA, "Accept": "application/json"}))
                out.write_bytes(get(link["id"]))
        elif s.get("url"):
            out = d / "paper.pdf"
            if not out.exists():
                out.write_bytes(get(s["url"]))
        else:
            out = d / "paper.pdf"
            if not out.exists():
                print(f"MANUAL: {s['id']} needs {out}"); return
        print(s["id"], out.name, out.stat().st_size)

if __name__ == "__main__":
    main()
