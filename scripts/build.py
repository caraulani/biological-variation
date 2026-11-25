"""Build every output of the meaningful-change release from the downloaded sources.

Steps
1. Extract text from every source (scripts/extract_all.py).
2. Parse Table 2 of the EuBIVAS summary report (82 measurands) from its sideways pages.
3. Load hand-entered rows from other sources (data/curated_rows.csv).
4. Check every row against the source text: each evidence string must occur in the extracted
   text (whitespace removed, dashes unified), and the CVI, its CI, CVG and CVA must occur inside
   the evidence. Any failure stops the build.
5. Pick one primary estimate per analyte (rule in METHODS.md).
6. Write data/bv_estimates.csv, data/primary_estimates.csv and web/meaningful-change.json.
"""
import csv, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT.parent / "_raw" / "meaningful-change"
ACCESS_DATE = "2026-11-25"
VERSION = "1.0.0"

SOURCES = {
    "carobene2022_summary": ("10.1515/cclm-2021-0370", "Carobene A, et al. Clin Chem Lab Med 2022;60:505-517 (EuBIVAS summary report)", "publisher PDF, University of Dundee repository copy"),
    "coskun2019_haem_meta": ("10.1515/cclm-2019-0658", "Coskun A, et al. Clin Chem Lab Med 2020;58:25-32 (haematology meta-analysis)", "publisher PDF, Acibadem University repository copy"),
    "fernandezcalle2022_thyroid_meta": ("10.1515/cclm-2021-0904", "Fernandez-Calle P, et al. Clin Chem Lab Med 2022 (thyroid meta-analysis)", "publisher PDF, Acibadem University repository copy"),
    "jonker2022_kidney_meta": ("10.1515/cclm-2020-1168", "Jonker N, et al. Clin Chem Lab Med 2022;60:469-478 (kidney meta-analysis)", "publisher PDF, University of Bergen repository (NVA) copy"),
    "diazgarzon2019_lipid_meta": ("10.1016/j.cca.2019.05.013", "Diaz-Garzon J, et al. Clin Chim Acta 2019;495:467-475 (lipid meta-analysis)", "accepted manuscript, University of Dundee repository copy"),
    "ricos2020_glyc_meta": ("10.1515/almed-2020-0029", "Ricos C, et al. Adv Lab Med 2020 (glucose, HbA1c, glycated albumin meta-analysis)", "open access full text, Europe PMC JATS XML (PMC10197502)"),
    "itkonen2024_sexhormones": ("10.1016/j.cca.2024.117806", "Itkonen O, et al. Clin Chim Acta 2024;555:117806 (EuBIVAS sex hormones in men)", "publisher PDF (CC BY), University of Dundee repository copy"),
    "carobene2025_insulinres": ("10.1515/cclm-2024-0672", "Carobene A, et al. Clin Chem Lab Med 2025 (EuBIVAS insulin resistance markers)", "accepted manuscript proof, University of Dundee repository copy"),
    "carobene2023_iron": ("10.1515/cclm-2022-1091", "Carobene A, et al. Clin Chem Lab Med 2023 (EuBIVAS serum iron, letter)", "publisher PDF, Acibadem University repository copy"),
    "coskun2022_trace": ("10.1515/cclm-2021-0886", "Coskun A, et al. Clin Chem Lab Med 2022 (EuBIVAS zinc, copper, selenium)", "publisher PDF, Acibadem University repository copy"),
    "coskun2022_trace_meta": ("10.1515/cclm-2021-0723", "Coskun A, et al. Clin Chem Lab Med 2022 (zinc, copper, selenium meta-analysis, letter)", "publisher PDF, Acibadem University repository copy"),
    "aslan2025_urine_meta": ("10.1016/j.cca.2024.120032", "Aslan B, et al. Clin Chim Acta 2025 (urine markers meta-analysis)", "accepted manuscript, University of Dundee repository copy"),
    "diazgarzon2021_tn_meta": ("10.1093/clinchem/hvaa261", "Diaz-Garzon J, et al. Clin Chem 2021;67:256-264 (cardiac troponin meta-analysis)", "publisher PDF, Acibadem University repository copy"),
    "hollestelle2023_coag_meta": ("10.1515/cclm-2022-1207", "Hollestelle MJ, et al. Clin Chem Lab Med 2023 (coagulation and fibrinolysis meta-analysis)", "publisher PDF (CC BY), Erasmus University repository copy"),
    "aarsand2021_coag": ("10.1093/clinchem/hvab100", "Aarsand AK, et al. Clin Chem 2021;67:1259 (EuBIVAS coagulation markers, Bayesian model)", "publisher PDF, Acibadem University repository copy"),
    "nutrients2013_b12": ("10.3390/nu5093634", "McArthur JO, et al. Nutrients 2013;5:3634-3645 (vitamins B6, B12 and folate in women)", "open access full text (CC BY 3.0), Europe PMC JATS XML (PMC3798926)"),
    "cavalier2021_vitd": ("10.3390/nu13020431", "Cavalier E, et al. Nutrients 2021;13:431 (EuBIVAS 25-hydroxyvitamin D)", "open access full text (CC BY), Europe PMC JATS XML (PMC7911223)"),
    "ercan2019_pth": ("10.11613/bm.2019.030702", "Ercan M, et al. Biochem Med (Zagreb) 2019;29:030702 (PTH)", "open access full text, Europe PMC JATS XML (PMC6610671)"),
}

EUBIVAS_POP = ("EuBIVAS: ostensibly healthy adults from 6 European centres (91 included: 38 men, "
               "43 women under 50, 10 women over 50; age about 20-69 years)")
EUBIVAS_SAMPLING = ("fasting samples weekly for 10 consecutive weeks (April-June 2015); "
                    "all samples from one person analysed in duplicate in one run")

def norm(s):
    s = s.replace("–", "-").replace("‒", "-").replace("−", "-").replace("—", "-")
    return re.sub(r"\s+", "", s)

def source_text(sid, fname):
    p = RAW / sid / fname
    if not p.exists():
        sys.exit(f"missing source text {p}; run scripts/fetch_sources.py and scripts/extract_all.py")
    return norm(p.read_text())

NUM = r"\d+(?:\.\d+)?"
VAL = re.compile(rf"({NUM})\s*(?:\(\s*({NUM})\s*–\s*({NUM})\s*\)?)?|NC")

def parse_summary_table():
    lines = (RAW / "carobene2022_summary" / "rotated.txt").read_text().splitlines()
    rows = {}
    for ln in lines:
        m = re.match(r"^\s*(\d{1,2})\s{2,}(.+?)\s{2,}(\d+)\s+(\(\d+/\d+\)|M|F)\s+([\d,]+)\s+(.*)$", ln)
        if not m:
            continue
        no = int(m.group(1))
        tail = re.sub(r"\[\d+\]\s*$", "", m.group(6)).strip()
        vals = [(x.group(0), x.groups()) for x in VAL.finditer(tail)]
        if len(vals) != 4:
            sys.exit(f"summary Table 2 row {no}: expected 4 values, got {len(vals)}: {tail!r}")
        (mean_s, _), (cva_s, cva_g), (cvi_s, cvi_g), (cvg_s, cvg_g) = vals
        rows[no] = {
            "label": m.group(2).strip(), "n": int(m.group(3)), "sex_split": m.group(4),
            "line": ln.strip(),
            "cva": cva_g[0], "cvi": cvi_g[0], "cvi_lo": cvi_g[1] or "", "cvi_hi": cvi_g[2] or "",
            "cvg": "" if cvg_s == "NC" else cvg_g[0],
            "cvg_lo": "" if cvg_s == "NC" else (cvg_g[1] or ""), "cvg_hi": "" if cvg_s == "NC" else (cvg_g[2] or ""),
        }
    if len(rows) != 82:
        sys.exit(f"summary Table 2: parsed {len(rows)} rows, expected 82")
    return rows

def summary_rows():
    parsed = parse_summary_table()
    mp = list(csv.DictReader(open(ROOT / "data" / "eubivas_summary_map.csv")))
    plain = source_text("carobene2022_summary", "paper.txt")
    out = []
    for m in mp:
        no = int(m["row_no"]); p = parsed[no]
        if norm(p["label"]) != norm(m["printed_label"]):
            sys.exit(f"row {no}: label {p['label']!r} != map {m['printed_label']!r}")
        # independent check: CVI string also present in the plain (non-rotated) extraction
        warn = ""
        if p["cvi_lo"] and norm(f"{p['cvi']}({p['cvi_lo']}–{p['cvi_hi']})") not in plain:
            warn = "CVI string not found in plain-text extraction (layout); checked in rotated extraction only"
        sex = {"M": "male", "F": "female"}.get(p["sex_split"], "mixed")
        pop = EUBIVAS_POP if sex == "mixed" else EUBIVAS_POP + f"; this measurand: {sex}s only"
        out.append({
            "row_id": f"eubivas_t2_{no:02d}", "source_id": "carobene2022_summary", "text_file": "rotated.txt",
            "analyte": m["analyte"], "marker_slug": m["marker_slug"], "specimen": m["specimen"],
            "population": pop, "sex": sex, "n_subjects": p["n"], "n_studies": "",
            "sampling": EUBIVAS_SAMPLING if "coagulation" not in m["platform_group"] else EUBIVAS_SAMPLING.replace("all samples from one person analysed in duplicate in one run", "Bayesian model"),
            "cvi": p["cvi"], "cvi_lo": p["cvi_lo"], "cvi_hi": p["cvi_hi"],
            "cvg": p["cvg"], "cvg_lo": p["cvg_lo"], "cvg_hi": p["cvg_hi"],
            "cva_study": p["cva"], "cva_kind": "CV-ANOVA of duplicate analysis of all study samples" if "coagulation" not in m["platform_group"] else "as printed (no CI)",
            "method": m["platform_group"], "design": "single study", "bivac": "EuBIVAS (designed to meet all 14 BIVAC items)",
            "location": f"Table 2, row {no} ('{m['printed_label']}'), pp. 509-511; primary paper ref {m['primary_paper_ref']} (doi {m['primary_paper_doi']})",
            "evidence": p["line"], "notes": "; ".join(x for x in (m["notes"], warn) if x),
            "include": m["include"], "primary_paper_doi": m["primary_paper_doi"],
        })
    return out

def check_row(r):
    text = source_text(r["source_id"], r["text_file"])
    ev_parts = [e for e in r["evidence"].split(" || ") if e.strip()]
    for e in ev_parts:
        if norm(e) not in text:
            sys.exit(f"{r['row_id']}: evidence not found in {r['source_id']}/{r['text_file']}: {e!r}")
    # value check on whitespace-collapsed evidence so neighbouring numbers stay separate
    ev = re.sub(r"\s+", " ", " ".join(ev_parts))
    for a, b in (("–", "-"), ("‒", "-"), ("−", "-")):
        ev = ev.replace(a, b)
    for k in ("cvi", "cvi_lo", "cvi_hi", "cvg", "cvg_lo", "cvg_hi", "cva_study"):
        v = str(r.get(k, "")).strip()
        if v and not re.search(rf"(?<![\d.]){re.escape(v)}(?![\d])", ev):
            sys.exit(f"{r['row_id']}: {k}={v} not found as a separate number in evidence {ev!r}")
    if r["cvi_lo"] and not (float(r["cvi_lo"]) <= float(r["cvi"]) <= float(r["cvi_hi"])):
        r["notes"] = (r["notes"] + "; " if r["notes"] else "") + "printed CVI CI does not contain the point estimate"

def pick_primary(rows):
    groups = {}
    for r in rows:
        if r.get("include", "yes") != "yes":
            continue
        groups.setdefault(r["marker_slug"] or r["analyte"], []).append(r)
    overrides = {o["key"]: o for o in csv.DictReader(open(ROOT / "data" / "primary_overrides.csv"))}
    by_id = {r["row_id"]: r for r in rows}
    prim = {}
    for key, rs in groups.items():
        if key in overrides:
            prim[key] = (by_id[overrides[key]["row_id"]], overrides[key]["reason"])
            continue
        def rank(r):
            eub = r["source_id"] in ("carobene2022_summary", "itkonen2024_sexhormones", "carobene2023_iron",
                                     "coskun2022_trace", "carobene2025_insulinres")
            all_sex = r["sex"] == "mixed"
            meta = r["design"] == "meta-analysis"
            tier = 0 if (eub and all_sex) else 1 if meta else 2 if eub else 3
            n = int(r["n_subjects"] or 0)
            cva = float(r["cva_study"] or 99)
            return (tier, -n, cva)
        best = sorted(rs, key=rank)[0]
        t = rank(best)[0]
        reason = {0: "EuBIVAS whole-cohort estimate: designed to meet all 14 BIVAC quality items, about 90 healthy adults, weekly samples, CVA from duplicate analysis",
                  1: "No EuBIVAS whole-cohort estimate; BIVAC-based meta-analysis of studies in healthy adults",
                  2: "Only EuBIVAS subgroup estimate available (see population)",
                  3: "Only study found with readable full text; see notes for its quality limits"}[t]
        if len([r for r in rs if rank(r)[0] == t]) > 1:
            reason += "; among equal-tier rows chose the larger n, then the lower CVA"
        prim[key] = (best, reason)
    return prim

def main():
    rows = summary_rows()
    for r in csv.DictReader(open(ROOT / "data" / "curated_rows.csv")):
        r["include"] = r.get("include") or "yes"; r["primary_paper_doi"] = ""
        rows.append(r)
    for r in rows:
        check_row(r)
        doi, label, version = SOURCES[r["source_id"]]
        r.update(doi=doi, source_label=label, document_version=version,
                 full_text_read="yes", access_date=ACCESS_DATE)
    # rows marked "withheld" are checked like every other row but kept out of every output file,
    # because the licence of the publication that first printed the estimate does not allow it
    withheld = [r for r in rows if r.get("include") == "withheld"]
    rows = [r for r in rows if r.get("include") != "withheld"]
    if withheld:
        print(f"withheld rows (not written): {', '.join(r['row_id'] for r in withheld)}")
    prim = pick_primary(rows)
    prim_ids = {b["row_id"]: reason for b, reason in prim.values()}
    for r in rows:
        r["primary"] = "yes" if r["row_id"] in prim_ids else "no"
        r["primary_reason"] = prim_ids.get(r["row_id"], "")

    cols = ["row_id", "analyte", "marker_slug", "specimen", "population", "sex", "n_subjects", "n_studies",
            "sampling", "cvi", "cvi_lo", "cvi_hi", "cvg", "cvg_lo", "cvg_hi", "cva_study", "cva_kind",
            "method", "design", "bivac", "source_id", "doi", "source_label", "location", "document_version",
            "full_text_read", "access_date", "evidence", "primary_paper_doi", "include", "primary",
            "primary_reason", "notes"]
    rows.sort(key=lambda r: (r["marker_slug"] or "~" + r["analyte"], r["primary"] != "yes", r["row_id"]))
    with open(ROOT / "data" / "bv_estimates.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    prows = [r for r in rows if r["primary"] == "yes"]
    with open(ROOT / "data" / "primary_estimates.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(prows)

    def num(x):
        return None if x in ("", None) else float(x)
    def slugify(s):
        return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    formulas = json.loads((ROOT / "data" / "formulas.json").read_text())
    aliases = {a["marker_slug"]: a["also_publish_as"] for a in csv.DictReader(open(ROOT / "data" / "web_aliases.csv"))}
    web_rows = []
    for r in prows:
        web_rows.append(r)
        if r["marker_slug"] in aliases:
            web_rows.append({**r, "marker_slug": aliases[r["marker_slug"]]})
    web = {"version": VERSION, "generated": ACCESS_DATE,
           "analytes": [{
               "slug": r["marker_slug"] or slugify(r["analyte"]),
               "marker_slug": r["marker_slug"] or None,
               "name": r["analyte"], "specimen": r["specimen"],
               "cvi": num(r["cvi"]),
               "cvi_ci": [num(r["cvi_lo"]), num(r["cvi_hi"])] if r["cvi_lo"] else None,
               "cvg": num(r["cvg"]), "cva_study": num(r["cva_study"]),
               "n_subjects": int(r["n_subjects"]) if r["n_subjects"] else None,
               "population": r["population"], "doi": r["doi"], "source_label": r["source_label"],
               "location": r["location"]} for r in web_rows],
           "formulas": formulas}
    (ROOT / "web").mkdir(exist_ok=True)
    (ROOT / "web" / "meaningful-change.json").write_text(json.dumps(web, ensure_ascii=False, indent=1) + "\n")
    print(f"web_entries={len(web_rows)} rows={len(rows)} included={sum(r['include']=='yes' for r in rows)} analytes(primary)={len(prows)} "
          f"with_marker_slug={sum(1 for r in prows if r['marker_slug'])} sources={len({r['source_id'] for r in rows})}")

if __name__ == "__main__":
    main()
