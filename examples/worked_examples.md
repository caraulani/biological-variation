# Worked examples

Arithmetic is shown step by step and rounded for display only; the code keeps full precision. Examples 1 and 2 reproduce numbers printed in published papers (they are also in `tests/literature_examples.json`). Example 3 uses made-up results to show how CVA choice changes the answer.

An RCV says whether a difference is larger than expected from measurement noise plus normal within-person variation. It does not say what caused the difference or what to do about it.

## Example 1. TSH, log-normal RCV, one-sided 95 % (Fernández-Calle et al. 2022)

Source: Fernández-Calle P, et al. Clin Chem Lab Med 2022, doi:10.1515/cclm-2021-0904, Table 2 (TSH: mean CVA 6.4 %, CVI 17.9 %; printed RCV −35.5 % / +55.1 %).

    CVA = 6.4 % = 0.064      CVI = 17.9 % = 0.179      z (one-sided 95 %) = 1.6449

    ln(1 + 0.064²) = ln(1.004096) = 0.0040876
    ln(1 + 0.179²) = ln(1.032041) = 0.0315384
    sum                            = 0.0356260
    s = √0.0356260                 = 0.188749
    z × √2 × s = 1.6449 × 1.41421 × 0.188749 = 0.439062

    RCV_up   = 100 × (e^0.439062 − 1)  = 100 × (1.551252 − 1) = +55.1 %
    RCV_down = 100 × (e^−0.439062 − 1) = 100 × (0.644641 − 1) = −35.5 %

## Example 2. PTH, symmetric RCV, two-sided 95 % (Ercan et al. 2019)

Source: Ercan M, et al. Biochem Med (Zagreb) 2019;29:030702, doi:10.11613/bm.2019.030702, Table 2 ("All group": CVA 3.8 %, CVI 21.1 %, RCV 59.4 %).

    CVA² + CVI² = 3.8² + 21.1² = 14.44 + 445.21 = 459.65
    √459.65     = 21.4394
    RCV = 1.95996 × 1.41421 × 21.4394 = 59.4 %

## Example 3. Two creatinine results, 80 then 92 µmol/L (made-up numbers)

CVI: 4.4 % (EuBIVAS, enzymatic method; `creatinine-serum` primary row). Change: 100 × (92 − 80) / 80 = +15.0 %. Two-sided 95 %, z = 1.95996, log-normal.

**a) With the study CVA (1.1 %, labelled "cva_study").**

    ln(1 + 0.011²) = 0.000121
    ln(1 + 0.044²) = 0.001934
    s = √0.002055 = 0.045333
    z × √2 × s = 1.95996 × 1.41421 × 0.045333 = 0.125656
    RCV_up = 100 × (e^0.125656 − 1) = +13.4 %     RCV_down = −11.8 %
    +15.0 % ≥ +13.4 %  → exceeds

**b) With the desirable-goal fallback CVA = 0.5 × 4.4 = 2.2 % (label it as a fallback).**

    ln(1 + 0.022²) = 0.000484
    s = √(0.000484 + 0.001934) = 0.049173
    RCV_up = +14.6 %     RCV_down = −12.7 %
    +15.0 % ≥ +14.6 %  → exceeds, by a narrow margin

A routine laboratory's between-day CVA for creatinine may be larger than either value. With a larger CVA the same +15 % could fall inside the RCV. This is why the calculator asks for the laboratory's own CVA.

## Example 4. Index of individuality and APS for creatinine (EuBIVAS, enzymatic)

    II = CVI / CVG = 4.4 / 17.1 = 0.26   (well below 0.6)
    Desirable imprecision ≤ 0.5 × 4.4 = 2.2 %
    Desirable bias ≤ 0.25 × √(4.4² + 17.1²) = 0.25 × 17.66 = 4.4 %
