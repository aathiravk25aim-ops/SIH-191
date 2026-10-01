"""SURAKSHA-ZONE AI — modern Streamlit command dashboard."""
import pandas as pd
import streamlit as st
from data import load_dataset
from risk_engine import assess_habitation, relocation_decision
from models import train_priority_model, predict_habitation_action
from map_utils import build_gis_map, calculate_haversine
from capacity_page import render_capacity_page
from ui import inject_css, hero, kpi, render_auth_page, render_weather_simulator, render_ai_lab

st.set_page_config(page_title="SURAKSHA-ZONE AI", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")
inject_css()

# Landing page -> authentication -> operational dashboard.
if not st.session_state.get("home_entered", False):
    st.markdown("""<div class="hero"><div class="eyebrow">SIH26191 · DISASTER MANAGEMENT</div><h1>🛡️ SURAKSHA-ZONE AI</h1><p>Proactive multi-hazard intelligence for vulnerable habitations, relocation readiness and resource-aware decisions.</p><div class="pill">🌊 HAZARD INTELLIGENCE · 🗺️ GIS · 🤖 AI · 🚑 RESPONSE READINESS</div></div>""", unsafe_allow_html=True)
    a,b,c=st.columns(3)
    with a: st.markdown("### 🌪️ Multi-hazard\nFlood, rainfall, wind, landslide and coastal scenario intelligence.")
    with b: st.markdown("### 🏕️ Relocation readiness\nCheck shelter, lifelines, vulnerable groups and deployment needs.")
    with c: st.markdown("### 🧠 Explainable AI\nUnderstand the signals behind each planning horizon.")
    if st.button("🔐 Continue to Secure Access", use_container_width=True):
        st.session_state.home_entered=True
        st.rerun()
    st.stop()

if not st.session_state.get("authenticated", False):
    render_auth_page()
    st.stop()

@st.cache_data
def get_df(): return load_dataset()

@st.cache_data
def scored(df, wh, we, wv, esc):
    rows=[]
    for r in df.to_dict("records"):
        a=assess_habitation(r,{"hazard":wh,"exposure":we,"vulnerability":wv},esc)
        d=relocation_decision(a,r)
        rows.append({"Location":r["location"],"State":r["state"],"Hazard":r["disaster_type"],"Score":a["score"],"Risk":f'{a["color"]["emoji"]} {a["risk_level"]}',"Action":d["action"],"Horizon":d["horizon"],"Affected":r["affected_population"],"Shelter":r["shelter_capacity"],"Distance to hub (km)":calculate_haversine(r["red_lat"],r["red_lon"],r["green_lat"],r["green_lon"])})
    return pd.DataFrame(rows).sort_values("Score",ascending=False).reset_index(drop=True)

df=get_df(); model=train_priority_model(); hero()
with st.sidebar:
    st.markdown("## 🛡️ Control Center")
    st.caption("Tune the decision model and explore scenarios.")
    wh=st.slider("⚠️ Hazard weight",0.0,1.0,0.45,0.05)
    we=st.slider("👥 Exposure weight",0.0,1.0,0.30,0.05)
    wv=st.slider("🧑‍🤝‍🧑 Vulnerability weight",0.0,1.0,0.25,0.05)
    esc=st.slider("📈 Escalation scenario",0.0,5.0,0.0,0.5)
    states=st.multiselect("📍 State filter",sorted(df.state.unique()))
    st.divider(); st.caption("SIH26191 • Disaster Management")

fdf=df[df.state.isin(states)] if states else df
t1,t2,t3,t4,t5=st.tabs(["📊 Mission Overview","🗺️ Hazard Intelligence","🌦️ Weather & Hazard Simulator","🏕️ Relocation Readiness","🤖 AI Decision Lab"])

with t1:
    table=scored(fdf,wh,we,wv,esc)
    cols=st.columns(4)
    with cols[0]: kpi("🏘️","Habitations",f"{len(table)}","monitored locations")
    with cols[1]: kpi("🚨","Critical",f"{int((table.Score>=80).sum())}","priority intervention")
    with cols[2]: kpi("👥","People exposed",f"{int(table.Affected.sum()):,}","estimated affected")
    with cols[3]: kpi("🏠","Shelter capacity",f"{int(table.Shelter.sum()):,}","registered capacity")
    st.markdown("### 🔥 Relocation priority radar")
    st.caption("Higher score = greater decision urgency. This is a planning aid, not an official hazard declaration.")
    st.dataframe(table,width="stretch",hide_index=True,column_config={"Score":st.column_config.ProgressColumn("Risk score",min_value=0,max_value=100,format="%.1f")})
    a,b=st.columns([2,1])
    with a: st.bar_chart(table.set_index("Location")["Score"],height=330)
    with b:
        st.markdown("### 🎯 Quick actions")
        st.download_button("⬇️ Export priority list",table.to_csv(index=False),"suraksha_priority.csv","text/csv",use_container_width=True)
        st.info("Use the GIS tab to inspect a location, then use Relocation Readiness to test its safe hub.")

with t2:
    st.markdown("### 🗺️ Multi-hazard operational map")
    a,b,c=st.columns([2,1,1]);
    with a: sel=st.selectbox("📍 Focus location",["None"]+fdf.location.tolist())
    with b: heat=st.checkbox("🌡️ Risk heatmap",True)
    with c: poi=st.checkbox("🏥 Hospitals & schools",True)
    build_gis_map(fdf,sel,heat,poi,poi)
    st.caption("Decision-support buffers are illustrative; they are not official hazard polygons.")

with t3:
    render_weather_simulator(fdf)

with t4:
    render_capacity_page(fdf)

with t5:
    render_ai_lab(model, fdf)

st.markdown('<div class="footer">🛡️ SURAKSHA-ZONE AI · SIH26191 · Proactive relocation decision intelligence · Illustrative planning data</div>',unsafe_allow_html=True)
