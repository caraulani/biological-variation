"""Reference change value (RCV) calculations for two results from the same person.

All coefficients of variation (CV) are given in percent, e.g. 5.2 for 5.2 %.
Equations and their sources are listed in data/formulas.md.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from statistics import NormalDist

__all__ = ["z_score", "rcv", "compare", "index_of_individuality",
           "aps_from_bv", "desirable_cva_fallback", "RCVResult"]

_ND = NormalDist()


def z_score(probability: float = 0.95, sided: str = "two") -> float:
    """Standard normal quantile for a probability.

    sided="two": z such that P(|Z| < z) = probability (0.95 -> 1.960).
    sided="one": z such that P(Z < z) = probability (0.95 -> 1.645).
    """
    if not 0 < probability < 1:
        raise ValueError("probability must be between 0 and 1, e.g. 0.95")
    if sided == "two":
        return _ND.inv_cdf(1 - (1 - probability) / 2)
    if sided == "one":
        return _ND.inv_cdf(probability)
    raise ValueError("sided must be 'one' or 'two'")


def _check_cv(name: str, value) -> float:
    if value is None:
        raise ValueError(f"{name} is required. Use the CVA your own laboratory measured "
                         "(or the CVA reported by the source study, labelled as such).")
    v = float(value)
    if not math.isfinite(v) or v < 0:
        raise ValueError(f"{name} must be a non-negative number in percent")
    return v


def rcv(cvi: float, cva: float, probability: float = 0.95, sided: str = "two",
        model: str = "lognormal", z: float | None = None) -> tuple[float, float]:
    """Return (rcv_down, rcv_up) in percent.

    model="symmetric":  RCV = ± z * sqrt(2) * sqrt(CVA^2 + CVI^2)
    model="lognormal":  sigma = sqrt(ln(1 + CVA^2) + ln(1 + CVI^2))   (CVs as fractions)
                        RCV_up   = 100 * (exp(+z * sqrt(2) * sigma) - 1)
                        RCV_down = 100 * (exp(-z * sqrt(2) * sigma) - 1)
    z overrides probability/sided when given (some papers round z to 1.64 or 2.33).
    """
    cvi = _check_cv("cvi", cvi)
    cva = _check_cv("cva", cva)
    if z is None:
        z = z_score(probability, sided)
    if model == "symmetric":
        k = z * math.sqrt(2) * math.sqrt(cva ** 2 + cvi ** 2)
        return (-k, k)
    if model == "lognormal":
        sigma = math.sqrt(math.log(1 + (cva / 100) ** 2) + math.log(1 + (cvi / 100) ** 2))
        return (100 * (math.exp(-z * math.sqrt(2) * sigma) - 1),
                100 * (math.exp(z * math.sqrt(2) * sigma) - 1))
    raise ValueError("model must be 'symmetric' or 'lognormal'")


@dataclass
class RCVResult:
    value1: float
    value2: float
    percent_change: float
    rcv_down: float
    rcv_up: float
    exceeds: bool
    direction: str          # "up", "down" or "none"
    z: float
    model: str
    sided: str
    probability: float | None

    def to_dict(self):
        return asdict(self)


def compare(value1: float, value2: float, cvi: float, cva: float,
            probability: float = 0.95, sided: str = "two", model: str = "lognormal",
            z: float | None = None) -> RCVResult:
    """Compare a second result (value2) with a first (value1) from the same person.

    percent_change = 100 * (value2 - value1) / value1.
    exceeds is True when percent_change >= rcv_up or <= rcv_down.
    With sided="one" both limits use the one-sided z; the direction you test should be
    chosen before looking at the result, not after.
    """
    v1, v2 = float(value1), float(value2)
    if v1 <= 0 or v2 < 0:
        raise ValueError("values must be positive (value1 > 0)")
    down, up = rcv(cvi, cva, probability, sided, model, z)
    change = 100 * (v2 - v1) / v1
    exceeds = change >= up or change <= down
    direction = "none" if not exceeds else ("up" if change > 0 else "down")
    zz = z if z is not None else z_score(probability, sided)
    return RCVResult(v1, v2, change, down, up, exceeds, direction, zz, model, sided,
                     None if z is not None else probability)


def index_of_individuality(cvi: float, cvg: float, cva: float | None = None) -> float:
    """II = CVI / CVG (Harris 1974 form used in most BV papers).
    If cva is given, returns sqrt(CVI^2 + CVA^2) / CVG instead (the form that includes analytical variation)."""
    cvi = _check_cv("cvi", cvi)
    cvg = _check_cv("cvg", cvg)
    if cvg == 0:
        raise ValueError("cvg must be > 0")
    if cva is None:
        return cvi / cvg
    return math.sqrt(cvi ** 2 + _check_cv("cva", cva) ** 2) / cvg


_LEVELS = {"optimum": 0.25, "desirable": 0.50, "minimum": 0.75}


def aps_from_bv(cvi: float, cvg: float | None = None, level: str = "desirable") -> dict:
    """Analytical performance specifications from biological variation.

    imprecision: CVA <= k * CVI           (k = 0.25 / 0.50 / 0.75)
    bias:        B   <= k/2 * sqrt(CVI^2 + CVG^2)   (0.125 / 0.250 / 0.375)
    total error: TEa <= 1.65 * imprecision + bias
    """
    if level not in _LEVELS:
        raise ValueError("level must be optimum, desirable or minimum")
    k = _LEVELS[level]
    cvi = _check_cv("cvi", cvi)
    out = {"level": level, "imprecision_max": k * cvi, "bias_max": None, "total_error_max": None}
    if cvg is not None:
        b = (k / 2) * math.sqrt(cvi ** 2 + _check_cv("cvg", cvg) ** 2)
        out["bias_max"] = b
        out["total_error_max"] = 1.65 * out["imprecision_max"] + b
    return out


def desirable_cva_fallback(cvi: float) -> float:
    """0.5 * CVI: the 'desirable' imprecision limit. This is a performance goal, not a measured CVA.
    Use it only as a clearly labelled placeholder when a laboratory's own CVA is unknown."""
    return 0.5 * _check_cv("cvi", cvi)
