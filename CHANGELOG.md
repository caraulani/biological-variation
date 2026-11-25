# Changelog

## 1.0.0 - 2026-11-25

First release.

- 171 estimate rows from 18 full-text publications; 123 analytes with a primary estimate, 110 linked to LifeFrom marker slugs; 124 web entries (CRP published as both `crp` and `hs-crp`).
- Sources: the EuBIVAS summary report (Table 2), EuBIVAS papers on sex hormones, iron, trace elements, insulin resistance markers and coagulation (with sex subgroups), BIVAC-based meta-analyses (haematology, thyroid, kidney, lipids, glycaemic markers, trace elements, urine markers, cardiac troponins, coagulation and fibrinolysis), and single studies for PTH, vitamin B12, folate and vitamin B6.
- Troponin I primary set to the EuBIVAS Siemens high-sensitivity assay row by override; PTH primary from Ercan 2019.
- 25-hydroxyvitamin D, D-dimer, vitamin B12, folate and vitamin B6 rows kept in the CSV with `include = no` and left out of the web file.
- Equations for symmetric and log-normal RCV, index of individuality and BV-based analytical performance specifications, with sources.
- Python reference implementation and TypeScript function; tests reproduce 11 RCVs printed in 3 papers.
- Web JSON for lifefrom.ai.
