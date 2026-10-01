# SIH26191 – Relocation Planner (complete project)

**Frontend:** Streamlit (`app.py`) · **Backend:** FastAPI (`api.py`) · **Engine:** `risk_engine.py`, `models.py` · **Data:** `data.py` (24 habitations)

## Run
```bash
pip install -r requirements.txt
streamlit run app.py          # web UI  -> http://localhost:8501
uvicorn api:app --port 8000   # optional REST API -> http://localhost:8000/docs
```
Internet is needed for map tiles and OSM hospital/school lookup (falls back to listed facilities offline).
Dataset values are illustrative; replace `data.py` with real survey data / official hazard layers for production.
