"""FastAPI backend. Run: uvicorn api:app --reload --port 8000  (docs at /docs)"""
from fastapi import FastAPI, HTTPException
from data import load_dataset
from risk_engine import assess_habitation, carrying_capacity, relocation_decision, resource_requirements, vulnerable_population_breakdown
from models import train_priority_model, predict_habitation_action

app = FastAPI(title="SIH26191 Relocation Decision API", version="1.0")
DF = load_dataset()
MODEL = train_priority_model()

def _row(name: str):
    m = DF[DF["location"] == name]
    if m.empty:
        raise HTTPException(404, f"Unknown location: {name}")
    return m.iloc[0].to_dict()

@app.get("/health")
def health():
    return {"status": "ok", "habitations": len(DF)}

@app.get("/habitations")
def habitations():
    out = []
    for r in DF.to_dict("records"):
        a = assess_habitation(r)
        out.append({**r, "risk_score": a["score"], "risk_level": a["risk_level"]})
    return sorted(out, key=lambda x: -x["risk_score"])

@app.get("/habitations/{name}")
def habitation(name: str, live_occupants: int = 0, escalation: float = 0.0):
    r = _row(name)
    a = assess_habitation(r, escalation=escalation)
    label, proba = predict_habitation_action(MODEL, r["hazard_intensity"], r["population_density"])
    return {"habitation": r, "assessment": a, "decision": relocation_decision(a, r),
            "capacity": carrying_capacity(r, live_occupants), "ml_label": label, "ml_probabilities": proba,
            "vulnerable": vulnerable_population_breakdown(r["affected_population"]),
            "resources_needed": resource_requirements(carrying_capacity(r, live_occupants)["people_still_to_place"])}
