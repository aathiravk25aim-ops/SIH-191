"""Backward-compatible model API backed by the explainable SIH26191 engine."""
from risk_engine import assess_habitation, carrying_capacity


class ExplainablePriorityModel:
    def _score(self, hazard_intensity, population_density):
        row = {
            "hazard_intensity": hazard_intensity,
            "population_density": population_density,
            "affected_population": max(1, population_density),
            "shelter_capacity": max(1, population_density),
        }
        return assess_habitation(row)["score"]

    def predict(self, rows):
        result = []
        for hazard_intensity, population_density in rows:
            score = self._score(hazard_intensity, population_density)
            if score >= 80:
                result.append("Immediate")
            elif score >= 60:
                result.append("Short-Term")
            else:
                result.append("Medium-Term")
        return result

    def predict_proba(self, rows):
        values = []
        anchors = {"Immediate": 90.0, "Short-Term": 65.0, "Medium-Term": 25.0}
        for hazard_intensity, population_density in rows:
            score = self._score(hazard_intensity, population_density)
            weights = {k: 1.0 / (1.0 + abs(score - v)) for k, v in anchors.items()}
            total = sum(weights.values()) or 1.0
            values.append({k: v / total for k, v in weights.items()})
        return values

    @property
    def classes_(self):
        return ["Immediate", "Medium-Term", "Short-Term"]


def train_priority_model():
    return ExplainablePriorityModel()


def predict_habitation_action(model, hazard_intensity, population_density):
    label = model.predict([[hazard_intensity, population_density]])[0]
    probabilities = model.predict_proba([[hazard_intensity, population_density]])[0]
    return label, {key: round(value * 100, 1) for key, value in probabilities.items()}


def calculate_carrying_capacity_deficit(affected_population, shelter_capacity, live_occupants=0, extra_fields=None):
    row = {"affected_population": affected_population, "shelter_capacity": shelter_capacity}
    if extra_fields:
        row.update(extra_fields)
    result = carrying_capacity(row, live_occupants)
    return {
        "affected_population": affected_population,
        "shelter_capacity": shelter_capacity,
        "effective_capacity": result["overall_effective_capacity"],
        "remaining_capacity": result["remaining_capacity"],
        "people_still_to_place": result["people_still_to_place"],
        "deficit": result["capacity_deficit"],
        "is_breached": result["capacity_deficit"] > 0,
        "utilization_pct": result["utilization_pct"],
        "bottleneck": result["bottleneck"],
        "bottleneck_capacity": result["bottleneck_capacity"],
        "resource_remaining": result["resource_remaining"],
        "resource_deficit": result["resource_deficit"],
        "resource_coverage_pct": result["resource_coverage_pct"],
        "lifeline_constrained": result["lifeline_constrained"],
        "resources": result["resources"],
    }
