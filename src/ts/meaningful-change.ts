/**
 * Reference change value (RCV) for two results from the same person.
 * CVs are in percent (5.2 means 5.2 %). Equations and sources: data/formulas.md.
 */

export type Sided = "one" | "two";
export type Model = "symmetric" | "lognormal";

export interface CompareInput {
  value1: number;
  value2: number;
  cvi: number;
  /** Analytical CV of the laboratory that produced the results. Required. */
  cva: number;
  probability?: number; // default 0.95
  sided?: Sided;        // default "two"
  model?: Model;        // default "lognormal"
  /** Optional fixed z (overrides probability and sided), e.g. 1.64 to match a paper. */
  z?: number;
}

export interface CompareResult {
  percentChange: number;
  rcvDown: number;
  rcvUp: number;
  exceeds: boolean;
  direction: "up" | "down" | "none";
  z: number;
}

/** Inverse standard normal CDF (Acklam's rational approximation, |error| < 1.2e-9 after one Halley step). */
export function normInv(p: number): number {
  if (!(p > 0 && p < 1)) throw new RangeError("p must be in (0, 1)");
  const a = [-3.969683028665376e1, 2.209460984245205e2, -2.759285104469687e2, 1.38357751867269e2, -3.066479806614716e1, 2.506628277459239];
  const b = [-5.447609879822406e1, 1.615858368580409e2, -1.556989798598866e2, 6.680131188771972e1, -1.328068155288572e1];
  const c = [-7.784894002430293e-3, -3.223964580411365e-1, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783];
  const d = [7.784695709041462e-3, 3.224671290700398e-1, 2.445134137142996, 3.754408661907416];
  const pl = 0.02425;
  let x: number;
  if (p < pl) {
    const q = Math.sqrt(-2 * Math.log(p));
    x = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1);
  } else if (p <= 1 - pl) {
    const q = p - 0.5, r = q * q;
    x = ((((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q) / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1);
  } else {
    const q = Math.sqrt(-2 * Math.log(1 - p));
    x = -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1);
  }
  // One Halley refinement step using erfc.
  const e = 0.5 * erfc(-x / Math.SQRT2) - p;
  const u = e * Math.sqrt(2 * Math.PI) * Math.exp((x * x) / 2);
  return x - u / (1 + (x * u) / 2);
}

function erfc(x: number): number {
  // Numerical Recipes erfc (Chebyshev), fractional error < 1.2e-7.
  const z = Math.abs(x), t = 1 / (1 + 0.5 * z);
  const r = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
  return x >= 0 ? r : 2 - r;
}

export function zScore(probability = 0.95, sided: Sided = "two"): number {
  if (!(probability > 0 && probability < 1)) throw new RangeError("probability must be in (0, 1)");
  return sided === "two" ? normInv(1 - (1 - probability) / 2) : normInv(probability);
}

function checkCv(name: string, v: number | null | undefined): number {
  if (v === null || v === undefined || !Number.isFinite(v) || v < 0) {
    throw new RangeError(`${name} is required as a non-negative percent. For cva, use your laboratory's own CVA.`);
  }
  return v;
}

/** Returns [rcvDown, rcvUp] in percent. */
export function rcv(cvi: number, cva: number, probability = 0.95, sided: Sided = "two", model: Model = "lognormal", z?: number): [number, number] {
  checkCv("cvi", cvi);
  checkCv("cva", cva);
  const zz = z ?? zScore(probability, sided);
  if (model === "symmetric") {
    const k = zz * Math.SQRT2 * Math.sqrt(cva * cva + cvi * cvi);
    return [-k, k];
  }
  if (model === "lognormal") {
    const sigma = Math.sqrt(Math.log(1 + (cva / 100) ** 2) + Math.log(1 + (cvi / 100) ** 2));
    return [100 * (Math.exp(-zz * Math.SQRT2 * sigma) - 1), 100 * (Math.exp(zz * Math.SQRT2 * sigma) - 1)];
  }
  throw new RangeError("model must be 'symmetric' or 'lognormal'");
}

export function compare(input: CompareInput): CompareResult {
  const { value1, value2, cvi, cva, probability = 0.95, sided = "two", model = "lognormal", z } = input;
  if (!(value1 > 0) || !(value2 >= 0)) throw new RangeError("values must be positive (value1 > 0)");
  const [rcvDown, rcvUp] = rcv(cvi, cva, probability, sided, model, z);
  const percentChange = (100 * (value2 - value1)) / value1;
  const exceeds = percentChange >= rcvUp || percentChange <= rcvDown;
  return {
    percentChange, rcvDown, rcvUp, exceeds,
    direction: !exceeds ? "none" : percentChange > 0 ? "up" : "down",
    z: z ?? zScore(probability, sided),
  };
}

/** II = CVI / CVG; with cva, sqrt(CVI^2 + CVA^2) / CVG. */
export function indexOfIndividuality(cvi: number, cvg: number, cva?: number): number {
  checkCv("cvi", cvi); checkCv("cvg", cvg);
  if (cvg === 0) throw new RangeError("cvg must be > 0");
  return cva === undefined ? cvi / cvg : Math.sqrt(cvi * cvi + checkCv("cva", cva) ** 2) / cvg;
}
