# Formulas

All CVs are in percent unless a line says "as a fraction". Every equation below is followed by where it was read. "Read" means the full text was opened and read on 2026-11-25. "Not read" means the DOI was checked against Crossref but the full text was not available to us; the equation is then taken from a later paper that was read and that cites the original.

## Notation

| Symbol | Meaning |
|---|---|
| CVI | Within-subject biological variation: how much one person's true value moves around their own set point over time. |
| CVG | Between-subject biological variation: how much set points differ between people. |
| CVA | Analytical variation: the imprecision of the measurement procedure that produced the two results. |
| z | Standard normal quantile for the chosen probability. |
| RCV | Reference change value: the smallest percent difference between two serial results that is unlikely (at the chosen probability) to come from CVA and CVI alone. |

## z values

| Probability | Two-sided z | One-sided z |
|---|---|---|
| 90 % | 1.645 | 1.282 |
| 95 % | 1.960 | 1.645 |
| 99 % | 2.576 | 2.326 |

Two-sided: "has it changed in either direction?" One-sided: "has it risen?" or "has it fallen?", decided before looking at the second result. Published papers often round z (1.64, 2.33). The code accepts an explicit z so such tables can be reproduced.

## 1. Classic (symmetric) RCV

    RCV = ± z × √2 × √(CVA² + CVI²)

The √2 is there because both results carry independent analytical and biological variation.

- Read: Ercan M, et al. Biochem Med (Zagreb) 2019;29:030702, doi:10.11613/bm.2019.030702, Methods (equation for RCV, with Z = 1.96 at 95 %). That paper attributes the equations to Fraser and Harris.
- Read: Díaz-Garzón Marco J, et al. Adv Lab Med 2020, doi:10.1515/almed-2020-0063, section on interpretation of serial results.
- Read: Bottani M, et al. Ann Transl Med 2020;8:855, doi:10.21037/atm-19-4498, Figure 4 legend (Z = change / [2^½ (CVA² + CVI²)^½]).
- Not read (DOI verified): Fraser CG. Reference change values. Clin Chem Lab Med 2012;50:807-812, doi:10.1515/cclm.2011.733.

## 2. Log-normal (asymmetric) RCV

Work on the log scale, where the within-person distribution is closer to normal. With CVs as fractions:

    σ_A = √(ln(1 + CVA²))
    σ_I = √(ln(1 + CVI²))
    RCV_up   = 100 × (exp(+z × √2 × √(σ_A² + σ_I²)) − 1)
    RCV_down = 100 × (exp(−z × √2 × √(σ_A² + σ_I²)) − 1)

The rise needed is larger than the fall needed. (1 + RCV_up/100) × (1 + RCV_down/100) = 1. For small CVs the two models give almost the same limits.

- Original, not read: Fokkema MR, Herrmann Z, Muskiet FAJ, Moecks J. Reference change values for brain natriuretic peptides revisited. Clin Chem 2006;52:1602-1603, doi:10.1373/clinchem.2006.069369. The DOI resolves and Crossref gives this title, journal, volume and pages. The University of Groningen repository lists a free copy, but its download page sits behind an automated-browser check, which we did not try to get past. The equation is therefore taken from the papers below.
- Read: Fernández-Calle P, et al. Clin Chem Lab Med 2022, doi:10.1515/cclm-2021-0904, Methods: RCV = 100 % (exp(± Z 2^½ (CV²LnA + CV²LnI)^½) − 1) with CVLn = (ln(1 + CV²))^½.
- Read: Corrigendum to Díaz-Garzón J, et al. Clin Chem 2021 (troponin meta-analysis), Clin Chem 2022;68:477, doi:10.1093/clinchem/hvab273: gives the corrected equation RCV = 100 % · (exp(± Z · 2^½ · (CV²LnA + CV²LnI)^½) − 1).
- Read: Bottani M, et al. 2020 (above), Methods, which cites Fokkema et al. for its asymmetric RCVs, and Table 2, whose values our code reproduces.
- Note: the PMC rendering of Díaz-Garzón 2020 prints the same equation with CV_T = CVA + CVI and the same sign in both lines; that looks like a typesetting loss. We follow Fernández-Calle 2022, whose Table 2 RCVs our code reproduces (7 of them are in the test suite).

## 3. Index of individuality (II)

    II = CVI / CVG

Some authors include analytical variation: II = √(CVI² + CVA²) / CVG. The code offers both; the web file uses neither (it only gives CVI and CVG).

A low II (below about 0.6) means each person's values stay in a narrow band inside a much wider population range. A population reference interval then says little about change in one person, and the RCV is more useful.

- Read: Díaz-Garzón Marco J, et al. 2020 (above): II = CVI/CVG and the II < 0.6 reading.
- Read: Fernández-Calle P, et al. 2022 (above), Table 2 footnote: II below 0.6 indicates high individuality.
- Original, not read (DOI verified): Harris EK. Effects of intra- and interindividual variation on the appropriate use of normal ranges. Clin Chem 1974;20:1535-1542, doi:10.1093/clinchem/20.12.1535.

## 4. Analytical performance specifications (APS) from biological variation

| Level | Imprecision | Bias | Total allowable error |
|---|---|---|---|
| Optimum | CVA ≤ 0.25 × CVI | B ≤ 0.125 × √(CVI² + CVG²) | TEa ≤ 1.65 × (0.25 × CVI) + 0.125 × √(CVI² + CVG²) |
| Desirable | CVA ≤ 0.50 × CVI | B ≤ 0.250 × √(CVI² + CVG²) | TEa ≤ 1.65 × (0.50 × CVI) + 0.250 × √(CVI² + CVG²) |
| Minimum | CVA ≤ 0.75 × CVI | B ≤ 0.375 × √(CVI² + CVG²) | TEa ≤ 1.65 × (0.75 × CVI) + 0.375 × √(CVI² + CVG²) |

- Read: Ercan M, et al. 2019 (above), Table 3 footnote, gives all three levels. That footnote prints the bias term as √(CVA² + CVG²); every other source we read uses √(CVI² + CVG²), so we treat CVA there as a typo and use CVI.
- Read: desirable level (CVA ≤ 0.50 CVI; B ≤ 0.25 √(CVI² + CVG²)) in Bottani 2020 (Table 2 footnotes), Itkonen 2024 (doi:10.1016/j.cca.2024.117806, Table 1 footnotes), Díaz-Garzón 2019 lipid meta-analysis (doi:10.1016/j.cca.2019.05.013, Table 2 footnote) and Fernández-Calle 2022 (Table 2; e.g. TSH bias 10.1 = 0.25 × √(17.9² + 36.2²)).
- Framework, not read (DOI verified): Sandberg S, et al. Defining analytical performance specifications: Consensus Statement from the 1st Strategic Conference of the EFLM (the "Milan" models). Clin Chem Lab Med 2015;53:833-835, doi:10.1515/cclm-2015-0067. The Milan consensus places BV-based APS as one of three models; the EuBIVAS summary report (read) notes that for CRP and other acute-phase proteins a "state of the art" model may fit better.

## 5. CVA: what to enter

The RCV needs the CVA of the measurement procedure that produced the two results.

1. Best: your laboratory's own long-term CVA at a concentration near the results (for example from internal quality control).
2. The CVA reported by the BV study (`cva_study` in the data). This comes from duplicate measurement of study samples in one run on one analyser. It is usually smaller than a routine laboratory's between-day CVA, so it gives RCVs that are too narrow for routine use. The EuBIVAS PTH paper says the same: each laboratory should compute its own RCV with its own CVA.
3. Labelled fallback: the desirable imprecision limit 0.5 × CVI. This is a performance goal, not a measurement. Using it says "if the lab meets the desirable goal". Mark any RCV computed this way.

We do not publish "typical" CVA values.
