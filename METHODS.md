# Methods

Enough detail to rebuild the release and get the same numbers. Access date for every source: 2026-11-25.

## 1. Finding sources

1. Europe PMC REST search (`https://www.ebi.ac.uk/europepmc/webservices/rest/search`) for titles containing "biological variation", "EuBIVAS" or "within-subject biological" in Clin Chem Lab Med, Clin Chem, Clin Chim Acta, Scand J Clin Lab Invest, Ann Clin Biochem, Biochem Med (Zagreb), Adv Lab Med and Clin Biochem, plus targeted searches (EuBIVAS, lipids, vitamin D, iron, HbA1c, systematic reviews and meta-analyses).
2. Unpaywall (`https://api.unpaywall.org/v2/<doi>`) for open locations of each candidate.
3. Priority: EuBIVAS papers (a multicentre study designed to meet all 14 items of the Biological Variation Data Critical Appraisal Checklist, BIVAC), then BIVAC-based meta-analyses by the EFLM Working Group on Biological Variation, then other single studies.
4. A source was used only if its full text could be read. Abstract-only sources were excluded and logged in `data/exclusions.csv`.

## 2. Getting the full texts

`scripts/sources.json` lists each source and where its full text came from:

- PDFs from institutional repositories (University of Dundee Discovery, Acibadem University open access, University of Bergen via the NVA API `publication/<id>/filelink/<file>`, Amsterdam UMC);
- JATS XML from Europe PMC (`/rest/<PMCID>/fullTextXML`) for open access articles;
- an Erasmus University repository copy (Hollestelle 2023, coagulation meta-analysis, CC BY);
- one PMC article (Bottani 2020, PTH) whose publisher blocks XML download; the page was read in a browser and the needed lines saved by hand as `fulltext_excerpt.txt`. It is cited for equations only. The article page stated CC BY-NC-ND 4.0 when read, so its RCV examples and the EuBIVAS PTH row first published in it are not shipped (the PTH row is marked `withheld` in `data/eubivas_summary_map.csv`; the build checks it and then leaves it out of every output).

Publisher websites (De Gruyter, Oxford Academic) refuse scripted downloads, so repository copies were used. Where the repository copy is the accepted manuscript rather than the typeset version, `document_version` says so.

`python3 -I scripts/fetch_sources.py` downloads everything into `../_raw/meaningful-change/<source_id>/`, a folder next to the repository folder. Crossref responses are cached in `../_raw/crossref/`. Downloads are not part of the release.

### Second search for gaps (2026-11-25)

For ferritin, vitamin B12, folate, 25-hydroxyvitamin D, troponin T, coagulation, D-dimer and urine albumin/ACR we ran further Europe PMC searches (open-access full text, author manuscripts, other open journals), rechecked Unpaywall for every candidate (generic address research@lifefrom.ai), and tried open repository and publisher copies. Pages behind a CAPTCHA or bot check (PMC for some articles, ScienceDirect, one university repository) were not bypassed. Outcomes per analyte are in `data/exclusions.csv`.

## 3. Text extraction

`scripts/extract_all.py` (PyMuPDF 1.26):

- `paper.txt`: page text in reading order. De Gruyter PDFs set digits in a font that maps them to private-use code points U+F130 to U+F139. These are mapped back to 0 to 9. The mapping was confirmed on known strings ("women < 50", table numbers, and PTH values that also appear in the independently read PMC page) and by viewing a rendered page.
- `rotated.txt`: pages whose text runs bottom to top (tables printed sideways) are laid out again as left-to-right rows by grouping text spans by their x position.
- `fulltext.txt`: JATS XML flattened to text, table rows joined with " | ".

## 4. Building the table

`scripts/build.py`:

1. **EuBIVAS summary report, Table 2** (Carobene et al. 2022, doi:10.1515/cclm-2021-0370; 82 measurands; CVA, CVI and CVG with 95 % CIs for the whole EuBIVAS population). Rows are parsed from `rotated.txt`. Each parsed label must equal the label in `data/eubivas_summary_map.csv`, which adds the analyte name, LifeFrom marker slug, specimen, platform group (from the report's abstract) and the DOI of the EuBIVAS paper that first published the estimate (from the report's reference list).
2. **Other sources**: rows were entered by hand in `data/curated_rows.csv`, each with an `evidence` field holding the text the numbers were read from, copied from the extracted text.
3. **Checks** (build stops on failure): each evidence string must occur in the source text after removing whitespace and unifying dashes; CVI, its CI limits, CVG, its CI limits and CVA must each appear as a separate number inside the evidence; CI limits must bracket the point estimate (otherwise a note is added).
4. **DOIs**: `scripts/verify_dois.py` fetches Crossref metadata for every DOI in `data/references.json`. All resolved and titles matched the cited works (`data/doi_verification.csv`).

## 5. Choosing the primary estimate

Per analyte (grouped by `marker_slug`, or by name when no slug matches), in this order:

1. EuBIVAS estimate for the whole cohort (all sexes): fully BIVAC-compliant design, about 90 subjects, weekly sampling, CVA from duplicates.
2. If none: a BIVAC-based meta-analysis estimate in healthy adults.
3. If none: an EuBIVAS subgroup estimate (e.g. men only).
4. Otherwise the single available study.

Ties within a tier: larger `n_subjects`, then lower `cva_study`. This picks enzymatic over Jaffe creatinine (same n, lower CVA).

Overrides (`data/primary_overrides.csv`): PTH uses Ercan 2019 (a small single study of intact PTH) because the EuBIVAS PTH 1-84 row is withheld (source licence); troponin I uses the EuBIVAS Siemens high-sensitivity assay row (n 66), a clinical assay, instead of the Singulex research assay row (n 89) that the tie rule would pick.

Web aliases (`data/web_aliases.csv`): the EuBIVAS CRP estimate (mean 0.72 mg/L, i.e. the hs-CRP range) is published twice, under `crp` and `hs-crp`, pointing to the same row.

Why EuBIVAS first. EuBIVAS is a single multicentre study run to one harmonised protocol: the same inclusion criteria, weekly fasting samples over the same 10 weeks, the same pre-analytical handling, all samples from one person measured in duplicate in one run on one analyser per measurand group, and the same statistical method. Its CVA and CVI therefore come from the same design, and its CIs describe one study rather than a pooled set. That matters for an RCV, which combines CVA and CVI. A meta-analysis pools studies with different sampling intervals, methods, populations and CVA estimates; its weights depend partly on quality grades, and its CVI is not tied to any one CVA. Meta-analysis rows are kept next to the EuBIVAS rows. Readers who prefer pooled estimates can compare with the EFLM Biological Variation Database (https://biologicalvariation.eu), which publishes meta-analysis-derived global estimates that include EuBIVAS. Where both exist in our table, the two are usually close (for example TSH 18.9 % EuBIVAS vs 17.9 % meta-analysis).

## 6. Formulas and code

Equations and sources are in `data/formulas.md`. The Python module uses only the standard library (`statistics.NormalDist` for z). The TypeScript module uses Acklam's inverse-normal approximation with one Halley refinement step; it matches Python's z to better than 1e-5.

Rows marked `include = no` stay in `bv_estimates.csv` but are never primary and never in the web file: D-dimer and 25-hydroxyvitamin D (sources advise against an average CVI) and vitamin B12, folate and B6 (one small study without confidence intervals or duplicate CVA).

## 7. Tests

- `tests/literature_examples.json`: 11 RCVs printed in 3 papers (Ercan 2019, PTH; Fernández-Calle 2022, thyroid analytes; Carobene 2023, iron). Examples from Bottani 2020 are not included, for the licence reason above. The code must reproduce each within 0.1 percentage points, because papers compute from unrounded CVs but print rounded ones. Where a paper used a rounded z (1.64 or 2.33), the test passes that z explicitly and says so.
- One set of printed RCVs could not be reproduced and is not in the tests: Itkonen 2024 Table 1 (sex hormones). Testosterone matches with z = 1.64; FSH, prolactin, LH and DHEA-S differ by 0.1 to 0.2. A corrigendum exists that we could not read.
- `tests/test_data.py`: web JSON schema, one primary per analyte, every DOI verified, every marker slug present in LifeFrom release 1 `markers.csv` (skipped when that file is not in `../_raw/lifefrom-release-1/`).

Run everything with `scripts/build.sh` (needs Python 3.9+, `uv`, Node 22.18+ and network access).
