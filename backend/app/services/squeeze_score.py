"""Core squeeze scoring logic - pure functions, fully testable.

Squeeze Score (0-100) combines:
  - Borrow cost       25%
  - Utilization       20%
  - SI % Float        20%
  - Days to Cover     15%
  - Volume spike      10%
  - Options gamma     10%
"""
from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class SqueezeSignals:
    """Point-in-time signals for a single ticker."""
    # Securities lending (near-realtime)
    cost_to_borrow: Optional[float] = None  # annualized %
    utilization: Optional[float] = None     # % of lendable supply (0-100)
    shares_on_loan: Optional[float] = None

    # FINRA (stale - twice-monthly)
    si_pct_float: Optional[float] = None    # %
    days_to_cover: Optional[float] = None   # SI / ADV
    short_interest: Optional[float] = None  # shares

    # Price/volume
    volume_ratio: Optional[float] = None    # volume / ADV_30d
    momentum_5d: Optional[float] = None     # 5-day return %
    rsi_14: Optional[float] = None

    # Options (daily)
    gamma_exposure: Optional[float] = None  # net dealer gamma
    put_call_ratio: Optional[float] = None


@dataclass
class SqueezeResult:
    score: float                  # 0-100 composite
    rule_score: float             # rules-only
    breakdown: Dict[str, float]   # {component: score_contribution}
    is_high_conviction: bool      # score >= 75


def _normalize(value: float, low: float, high: float) -> float:
    """Clip and normalize value to [0, 1] range."""
    if value is None:
        return 0.0
    return max(0.0, min(1.0, (value - low) / max(high - low, 1e-9)))


def compute_rule_score(signals: SqueezeSignals) -> SqueezeResult:
    """Compute rule-based squeeze score from signals.
    
    All component scores are 0-100. Weighted sum produces final 0-100 score.
    """
    breakdown = {}

    # --- Borrow cost (25%) ---
    # 0% borrow -> 0, 100%+ borrow -> 100
    ctb = signals.cost_to_borrow or 0.0
    borrow_score = _normalize(ctb, 0, 150) * 100
    breakdown["borrow_cost"] = round(borrow_score * 0.25, 2)

    # --- Utilization (20%) ---
    # 0% -> 0, 100% -> 100
    util = signals.utilization or 0.0
    util_score = _normalize(util, 0, 100) * 100
    breakdown["utilization"] = round(util_score * 0.20, 2)

    # --- SI % Float (20%) ---
    # 0% -> 0, 50%+ -> 100
    si_pct = signals.si_pct_float or 0.0
    si_score = _normalize(si_pct, 0, 50) * 100
    breakdown["si_pct_float"] = round(si_score * 0.20, 2)

    # --- Days to Cover (15%) ---
    # DTC: inverted - 0 DTC -> 100, 10+ DTC -> 0
    # Low DTC = faster potential squeeze
    dtc = signals.days_to_cover
    if dtc is not None:
        dtc_score = _normalize(10 - dtc, 0, 10) * 100  # invert
    else:
        dtc_score = 0.0
    breakdown["days_to_cover"] = round(dtc_score * 0.15, 2)

    # --- Volume spike (10%) ---
    # volume_ratio: 1x -> 0, 5x+ -> 100
    vol_ratio = signals.volume_ratio or 1.0
    vol_score = _normalize(vol_ratio, 1, 5) * 100
    breakdown["volume_spike"] = round(vol_score * 0.10, 2)

    # --- Options gamma (10%) ---
    # Gamma exposure: normalized to [-1, 1] range conceptually
    # Negative GEX = dealer short gamma = amplifies price moves
    gamma = signals.gamma_exposure
    if gamma is not None and gamma < 0:
        # More negative = more amplification = higher score
        gamma_score = min(100.0, abs(gamma) / 1e6 * 100)
    else:
        gamma_score = 0.0
    breakdown["gamma_exposure"] = round(gamma_score * 0.10, 2)

    rule_score = sum(breakdown.values())
    rule_score = max(0.0, min(100.0, rule_score))

    return SqueezeResult(
        score=rule_score,
        rule_score=rule_score,
        breakdown=breakdown,
        is_high_conviction=rule_score >= 75,
    )


def blend_ml_score(rule_result: SqueezeResult, ml_prob: float) -> SqueezeResult:
    """Blend rule-based score with ML model probability.
    
    Final = 0.5 * rule_score + 0.5 * (ml_prob * 100)
    """
    ml_score_100 = ml_prob * 100
    blended = 0.5 * rule_result.rule_score + 0.5 * ml_score_100
    blended = max(0.0, min(100.0, blended))
    breakdown = dict(rule_result.breakdown)
    breakdown["ml_model"] = round(ml_score_100 * 0.5, 2)
    return SqueezeResult(
        score=blended,
        rule_score=rule_result.rule_score,
        breakdown=breakdown,
        is_high_conviction=blended >= 75,
    )
