---
license: cc-by-4.0
language:
- en
pretty_name: "Meaningful change: open biological variation estimates and reference change values"
tags:
- laboratory-medicine
- clinical-chemistry
- biological-variation
- reference-change-value
- biomarkers
size_categories:
- n<1K
configs:
- config_name: all_estimates
  data_files: data/bv_estimates.csv
- config_name: primary_estimates
  data_files: data/primary_estimates.csv
---

# Meaningful change

Interactive version: https://lifefrom.ai/research/open-data/meaningful-change

Two results from the same person differ. Is the difference larger than normal day-to-day biological wobble plus measurement noise? The usual tool is the reference change value (RCV). It needs the within-subject biological variation (CVI) of the analyte and the analytical variation (CVA) of the measurement procedure.

This release gives:

- an open table of CVI and CVG (between-subject variation) estimates, each copied from the full text of a published study or meta-analysis, with DOI, table and row;
- one "primary" estimate per analyte, with the reason it was chosen;
- the RCV equations (symmetric and log-normal), the index of individuality and BV-based analytical performance specifications, each with its source (`data/formulas.md`);
- a reference implementation in Python and a TypeScript function, tested against RCVs printed in three papers;
- a compact JSON file for the lifefrom.ai website.

Version 1.0.0, 2026-11-25.

## Who it is for

Laboratory scientists, clinicians, sports scientists, researchers and developers who need citable CVI values and a checked RCV calculation.

## Relation to the EFLM Biological Variation Database

The EFLM Biological Variation Database (https://biologicalvariation.eu) is the authoritative, curated source of biological variation estimates, with BIVAC appraisal of the studies it includes and global meta-analysis estimates. This release is an open-licence complement to it: a smaller table built only from journal articles, with nothing copied from the database.

## Using an RCV correctly

- An RCV says whether the difference between two results is larger than expected from measurement noise plus normal within-person variation. It does not identify the cause of the difference.
- An RCV applies only to two results measured by the same laboratory with the same method. Results from different laboratories or methods can differ by more than any RCV because of calibration and method bias, which the RCV does not include.
- The CVA you enter must be your laboratory's routine between-run (long-term) CVA for that method, for example from internal quality control at a similar concentration. Do not use a study's within-run CVA (`cva_study`). Study CVAs come from duplicate measurements in one run and are usually smaller, so they give RCVs that are too narrow.

## How the data were extracted and checked

Each value was read from the source full text and checked as follows:

- every number comes from a full text that was read; abstract-only sources were excluded;
- each row stores the source text it was read from (`evidence`); the build script stops if that text is not in the extracted source, or if CVI, its CI, CVG or CVA are not in it;
- the 81 rows from the EuBIVAS summary report table were parsed by script from the source, not typed;
- a rendered PDF page was compared by eye with the extracted digits;
- every DOI was checked against Crossref;
- the RCV code reproduces 11 RCVs printed in 3 papers.

These checks confirm that the numbers match the sources as extracted. Whether an estimate suits a given population, method or purpose is for the user to judge.

## Coverage

| | Count |
|---|---|
| Estimate rows | 171 (162 included; 9 kept in the CSV for transparency but excluded from primary choice and the web file: D-dimer x2, 25-hydroxyvitamin D x3, vitamin B12/folate/B6 x4) |
| Analytes with a primary estimate | 123 |
| ... of which match a LifeFrom `marker_slug` | 110 |
| Web entries | 124 (CRP is published under both `crp` and `hs-crp`) |
| Source publications for the numbers | 18, all full text read, all DOIs checked with Crossref |

Groups: liver enzymes, electrolytes, kidney, lipids and apolipoproteins, glucose, HbA1c, insulin and HOMA-IR, proteins (albumin, immunoglobulins, complement, transferrin, CRP, haptoglobin and others), iron and soluble transferrin receptor, thyroid (TSH, FT4, FT3, T4, T3, thyroglobulin, antibodies, TSI), PTH and bone turnover markers, cortisol, male sex hormones, PSA and tumour markers, haemostasis (including INR and von Willebrand factor antigen), trace elements, complete blood count, three urine analytes, troponin I and troponin T.

Gaps (no web entry): ferritin, 25-hydroxyvitamin D, D-dimer, urine albumin/ACR, vitamin B12, folate, vitamin B6 (weak source, CSV only), female sex hormones. Why, per analyte: `data/exclusions.csv`.

## Files

| File | Content |
|---|---|
| `data/bv_estimates.csv` | Every estimate row (one row per analyte per source/subgroup). |
| `data/primary_estimates.csv` | One row per analyte: the primary estimate. Same columns. |
| `data/formulas.md`, `data/formulas.json` | Equations with sources. |
| `data/eubivas_summary_map.csv` | How each of the 82 rows of Table 2 of the EuBIVAS summary report maps to an analyte, marker slug, specimen and platform. |
| `data/curated_rows.csv` | Hand-entered rows from the other 17 sources, with the exact text they were read from. |
| `data/primary_overrides.csv` | Primary choices set by override rather than by the rule (troponin I). |
| `data/web_aliases.csv` | Estimates published under a second marker slug (CRP as hs-CRP). |
| `data/references.json`, `data/doi_verification.csv` | Every DOI used, with the title, journal and year returned by Crossref. |
| `data/exclusions.csv` | What was left out and why. |
| `web/meaningful-change.json` | Primary estimates and formulas for the website. |
| `src/python/meaningful_change/` | Python reference implementation (standard library only). |
| `src/ts/meaningful-change.ts` | TypeScript implementation (no dependencies). |
| `examples/worked_examples.md` | Worked examples with the arithmetic. |
| `tests/` | Python and TypeScript tests; `literature_examples.json` holds the published RCVs we reproduce. |
| `scripts/` | Download, text extraction, DOI check and build. `scripts/build.sh` rebuilds everything; downloads go to `../_raw/` next to the repository folder. |

### Columns of `bv_estimates.csv`

| Column | Meaning |
|---|---|
| `row_id` | Stable row id. |
| `analyte` | Analyte name as used here. |
| `marker_slug` | LifeFrom marker id (from LifeFrom release 1 `markers.csv`); empty if none matches. |
| `specimen` | Serum, citrated plasma, whole blood, urine. |
| `population` | Who was studied. Meta-analysis rows give the inclusion criteria. |
| `sex` | `mixed`, `male` or `female` (the subgroup the estimate describes). |
| `n_subjects` | People contributing to the estimate (single studies). |
| `n_studies` | Studies in the meta-analysis (where printed). |
| `sampling` | Sampling interval and duration. |
| `cvi`, `cvi_lo`, `cvi_hi` | Within-subject CV, % with 95 % CI. |
| `cvg`, `cvg_lo`, `cvg_hi` | Between-subject CV, % with 95 % CI (empty if not given). |
| `cva_study` | Analytical CV reported by the source, %. |
| `cva_kind` | How that CVA was obtained (usually duplicates within one run). |
| `method` | Platform or assay group. |
| `design` | `single study` or `meta-analysis`. |
| `bivac` | Quality grading as stated by the source. |
| `source_id`, `doi`, `source_label` | The publication the numbers were read from. |
| `location` | Table and row (and page) in that publication. |
| `document_version` | Publisher PDF, accepted manuscript or PMC full text, and where it was read. |
| `full_text_read` | Always `yes`. Abstract-only sources were excluded. |
| `access_date` | 2026-11-25. |
| `evidence` | The text the numbers were read from, as extracted. The build fails if this text is not found in the source or the numbers are not in it. |
| `primary_paper_doi` | For rows from the EuBIVAS summary report: the EuBIVAS paper that first published the estimate. |
| `include` | `no` for rows kept for transparency but left out of the web file. |
| `primary`, `primary_reason` | Whether this row is the analyte's primary estimate, and why. |
| `notes` | Caveats copied or derived from the source. |

### `web/meaningful-change.json`

`{version, generated, analytes: [{slug, marker_slug, name, specimen, cvi, cvi_ci: [lo, hi], cvg, cva_study, n_subjects, population, doi, source_label, location}], formulas: {...}}`. `cvi_ci`, `cvg`, `cva_study` and `n_subjects` can be `null`.

## Using the code

Python (3.9+, no dependencies):

```python
import sys; sys.path.insert(0, "src/python")
from meaningful_change import compare
r = compare(80, 92, cvi=4.4, cva=2.5, probability=0.95, sided="two", model="lognormal")
r.percent_change, r.rcv_down, r.rcv_up, r.exceeds
```

TypeScript:

```ts
import { compare } from "./src/ts/meaningful-change.ts";
compare({ value1: 80, value2: 92, cvi: 4.4, cva: 2.5 });
```

`cva` is required. Use the CVA of the laboratory that produced the results. See `data/formulas.md`, section 5.

## How it was built

Sources were found through Europe PMC, Crossref and Unpaywall, then downloaded from open repositories or read as open full text. Text was extracted from PDFs (including tables printed sideways) and every number was checked against that text by the build script. See `METHODS.md`.

## Limitations

- Most primary estimates come from one study, EuBIVAS: about 90 healthy, mostly young and middle-aged Europeans, weekly samples over 10 weeks in spring 2015, one analyser per measurand group. CVI can differ with age, sex, health status, sampling interval and season. Estimates for disease states are not included.
- Several EuBIVAS papers are paywalled. For those, we took the numbers from the open EuBIVAS summary report (Carobene et al. 2022), which tabulates them. Subgroup (sex) estimates from those papers are therefore missing; the summary report names the measurands where CVI differed by sex, and our notes repeat that.
- Sex hormone rows are for men only; PSA rows for men only; CA 125 and HE4 rows for women only.
- `cva_study` is a within-run duplicate CVA from a research setting. It is usually smaller than a routine laboratory's between-day CVA and will give RCVs that are too narrow if used as a stand-in.
- Population percentiles are not healthy reference intervals, and a BV estimate is not a reference interval either.
- The log-normal RCV assumes log-normal within-person variation. For CRP, troponin and other analytes with skewed or episodic behaviour the RCV is a rough guide only.
- 25-hydroxyvitamin D: EuBIVAS found a steady rise over spring, so the steady-state BV model does not apply. Trimmed CVIs are in the CSV for reference but not in the web file.
- Vitamin B12, folate and vitamin B6 rows are in the CSV only, flagged as weak, and not in the web file. They come from one small study (22 young women in an iron-status trial, 4 samples over 12 weeks, no confidence intervals, no duplicate CVA). Treat them as rough.
- Troponin T and the troponin I meta-analysis row pool several assays; healthy concentrations are near detection limits.

## How to cite

LifeFrom; Caraulani J. Meaningful change: open biological variation estimates and reference change values. Version 1.0.0, 2026. https://github.com/caraulani/biological-variation

Please also cite the source publication for any estimate you use (DOI in each row).

## Licence

Data (CSV, JSON, Markdown) under CC BY 4.0. Code (`src/`, `scripts/`, `tests/`) under MIT. See `LICENSE`. The numbers are taken from the cited publications; their text and tables are not redistributed here. Nothing from the EFLM Biological Variation Database is included.
