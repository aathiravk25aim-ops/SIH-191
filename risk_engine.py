"""Explainable risk, relocation and carrying-capacity engine for SIH26191."""
from __future__ import annotations
import math
from typing import Any, Dict, Mapping

RISK_TIERS = (
    (80, "Critical", "#DC2626", "🔴"),
    (60, "High", "#F97316", "🟠"),
    (35, "Medium", "#EAB308", "🟡"),
    (0, "Low", "#22C55E", "🟢"),
)

DEFAULT_WEIGHTS = {"hazard": 0.45, "exposure": 0.30, "vulnerability": 0.25}
DECISION_THRESHOLDS = {"immediate": 80, "priority": 60, "prepare": 35}


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError):
        x = 0.0
    return round(max(low, min(high, x)), 1)


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normal(value: Any, maximum: float) -> float:
    maximum = max(1.0, _num(maximum, 1.0))
    return clamp(_num(value) / maximum * 100.0)


def risk_color(score: float) -> Dict[str, str]:
    s = _num(score)
    for threshold, tier, hex_color, emoji in RISK_TIERS:
        if s >= threshold:
            return {"tier": tier, "hex": hex_color, "emoji": emoji}
    return {"tier": "Low", "hex": "#22C55E", "emoji": "🟢"}


def classify_risk(score: float) -> str:
    return risk_color(score)["tier"]


def _hazard_family(disaster_type: str) -> str:
    text = str(disaster_type or "").lower()
    groups = {
        "flood": ("flood", "river", "surge", "tsunami", "inundation", "glof", "avulsion"),
        "landslide": ("landslide", "slope", "debris", "collapse", "subsidence", "mudslide"),
        "cyclone": ("cyclone", "storm", "coast", "tidal"),
        "earthquake": ("seismic", "earthquake", "fault", "liquefaction"),
        "fire": ("fire", "mine"),
    }
    for family, terms in groups.items():
        if any(term in text for term in terms):
            return family
    return "flood"


def multi_hazard_scores(row: Mapping[str, Any], escalation: float = 0.0) -> Dict[str, float]:
    intensity = _normal(row.get("hazard_intensity", 0), 10)
    density = _normal(row.get("population_density", 0), 6000)
    elevation = _num(row.get("elevation_m", 0))
    family = _hazard_family(row.get("disaster_type", ""))

    base = {name: intensity * 0.48 + density * 0.17 for name in ("flood", "landslide", "cyclone", "earthquake", "fire")}
    base[family] += 32
    if family in ("flood", "cyclone") and elevation < 50:
        base[family] += 15
    if family == "landslide" and elevation > 300:
        base[family] += 8
    if family == "earthquake" and elevation < 200:
        base[family] += 4

    multiplier = 1.0 + max(0.0, _num(escalation)) * 0.08
    return {name.title(): clamp(score * multiplier) for name, score in base.items()}


def assess_habitation(row: Mapping[str, Any], weights: Mapping[str, float] | None = None, escalation: float = 0.0) -> Dict[str, Any]:
    weights = dict(DEFAULT_WEIGHTS if weights is None else weights)
    hazard_scores = multi_hazard_scores(row, escalation)
    hazard = max(hazard_scores.values())

    population = max(1.0, _num(row.get("affected_population", 0)))
    density_score = _normal(row.get("population_density", 0), 6000)
    affected_score = _normal(population, 40000)
    exposure = clamp(density_score * 0.55 + affected_score * 0.45)

    shelter = max(0.0, _num(row.get("shelter_capacity", 0)))
    shelter_coverage = clamp(shelter / population * 100.0) if population else 0.0
    infrastructure_gap = 100.0 - shelter_coverage
    vulnerability = clamp(infrastructure_gap * 0.55 + hazard * 0.25 + _normal(row.get("hazard_intensity", 0), 10) * 0.20)

    total = sum(_num(v) for v in weights.values()) or 1.0
    score = clamp((hazard * _num(weights.get("hazard", 0)) + exposure * _num(weights.get("exposure", 0)) + vulnerability * _num(weights.get("vulnerability", 0))) / total)
    rc = risk_color(score)
    contributions = {
        "Hazard": hazard * _num(weights.get("hazard", 0)) / total,
        "Exposure": exposure * _num(weights.get("exposure", 0)) / total,
        "Vulnerability": vulnerability * _num(weights.get("vulnerability", 0)) / total,
    }
    return {
        "score": score,
        "risk_level": rc["tier"],
        "color": rc,
        "hazards": hazard_scores,
        "exposure": round(exposure, 1),
        "vulnerability": round(vulnerability, 1),
        "contributions": {k: round(v, 1) for k, v in contributions.items()},
    }


def carrying_capacity(row: Mapping[str, Any], live_occupants: int = 0) -> Dict[str, Any]:
    """Calculate capacity without double-counting current occupants.

    `affected_population` = people who need safe accommodation.
    `live_occupants` = people already inside the selected shelter.
    Required remaining space is therefore affected_population - live_occupants.
    """
    shelter = max(0, int(_num(row.get("shelter_capacity", 0))))
    affected = max(0, int(_num(row.get("affected_population", 0))))
    current = max(0, int(live_occupants))
    current = min(current, shelter)

    physical_remaining = max(0, shelter - current)
    people_still_to_place = max(0, affected - current)
    capacity_deficit = max(0, people_still_to_place - physical_remaining)

    resources = {
        "Shelter capacity": shelter,
        "Drinking water": max(0, int(_num(row.get("water_liters_day", 0)) / 3)),
        "Food packets": max(0, int(_num(row.get("food_packets", 0)))),
        "Sanitation": max(0, int(_num(row.get("sanitation_units", 0)) * 20)),
        "Medical beds": max(0, int(_num(row.get("beds_available", 0)) * 8)),
    }
    bottleneck, bottleneck_capacity = min(resources.items(), key=lambda x: x[1])
    resource_remaining = max(0, bottleneck_capacity - current)
    resource_deficit = max(0, people_still_to_place - resource_remaining)

    overall_effective_capacity = min(resources.values()) if resources else shelter
    utilization_pct = round((current / shelter) * 100, 1) if shelter else 100.0
    demand_coverage_pct = round(min(100.0, ((current + physical_remaining) / affected) * 100), 1) if affected else 100.0
    resource_coverage_pct = round(min(100.0, ((current + resource_remaining) / affected) * 100), 1) if affected else 100.0

    return {
        "safe_capacity": shelter,
        "current_occupants": current,
        "remaining_capacity": physical_remaining,
        "affected_population": affected,
        "people_still_to_place": people_still_to_place,
        "capacity_deficit": capacity_deficit,
        "utilization_pct": utilization_pct,
        "demand_coverage_pct": demand_coverage_pct,
        "resources": resources,
        "bottleneck": bottleneck,
        "bottleneck_capacity": bottleneck_capacity,
        "resource_remaining": resource_remaining,
        "resource_deficit": resource_deficit,
        "resource_coverage_pct": resource_coverage_pct,
        "lifeline_constrained": resource_deficit > 0,
        "overall_effective_capacity": overall_effective_capacity,
    }


def relocation_decision(assessment: Mapping[str, Any], row: Mapping[str, Any]) -> Dict[str, Any]:
    score = _num(assessment.get("score"))
    population = max(0, int(_num(row.get("affected_population", 0))))
    capacity = carrying_capacity(row)
    if score >= 80 or capacity["capacity_deficit"] > 0:
        action = "IMMEDIATE RELOCATION"
        recommendation = "Evacuate vulnerable groups first, activate transport, and use a verified safe hub."
        horizon = "Immediate"
    elif score >= 60:
        action = "PRIORITY RELOCATION"
        recommendation = "Pre-stage transport and move high-vulnerability groups before escalation."
        horizon = "Short-Term"
    elif score >= 35:
        action = "PREPARE FOR RELOCATION"
        recommendation = "Monitor hazard escalation, reserve shelter space, and pre-position resources."
        horizon = "Medium-Term"
    else:
        action = "MONITOR"
        recommendation = "Maintain readiness and continue monitoring."
        horizon = "Monitor"
    return {
        "action": action,
        "recommendation": recommendation,
        "horizon": horizon,
        "population_to_relocate": population if action != "MONITOR" else 0,
        "vulnerable_population": round(population * 0.26),
        "score": score,
    }


def vulnerable_population_breakdown(affected_population: int) -> Dict[str, int]:
    p = max(0, int(affected_population or 0))
    children = round(p * 0.20)
    elderly = round(p * 0.09)
    women = round(p * 0.49)
    pwd = round(p * 0.03)
    general = max(0, p - children - elderly - pwd)
    return {"Children (<12y)": children, "Elderly (60y+)": elderly, "Women": women, "Persons with disabilities": pwd, "General adults": general}


def resource_requirements(population: int, assumptions: Mapping[str, float] | None = None) -> Dict[str, int]:
    a = {"bus_capacity": 50, "water_lpd": 3, "people_per_ambulance": 1000, "people_per_rescuer": 100}
    a.update(assumptions or {})
    p = max(0, int(population))
    return {
        "buses": math.ceil(p / a["bus_capacity"]) if p else 0,
        "ambulances": math.ceil(p / a["people_per_ambulance"]) if p else 0,
        "rescue_personnel": math.ceil(p / a["people_per_rescuer"]) if p else 0,
        "water_liters_day": math.ceil(p * a["water_lpd"]),
        "meals": p,
        "medical_beds": math.ceil(p * 0.05),
    }
