"""Modern carrying-capacity and relocation-readiness page."""
import pandas as pd
import streamlit as st
from risk_engine import carrying_capacity, vulnerable_population_breakdown, resource_requirements
from ui import kpi


def _fmt(n): return f"{int(n):,}"


def render_capacity_page(df):
    st.markdown('<div class="section-title">🏕️ Relocation Readiness Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Move beyond a simple shelter-capacity number. Check physical space, lifelines, vulnerable groups and deployment requirements in one operational view.</div>', unsafe_allow_html=True)

    left, right = st.columns([1.45, 1])
    with left:
        selected_name = st.selectbox("📍 Safe relocation hub", df["green_name"].astype(str).tolist())
        row = df[df["green_name"] == selected_name].iloc[0]
    with right:
        max_occ = int(row["shelter_capacity"])
        live = st.number_input("👥 Current occupants", min_value=0, max_value=max_occ, value=min(0,max_occ), step=max(1, max_occ//50 or 1))

    result = carrying_capacity(row.to_dict(), int(live))
    remaining = result["remaining_capacity"]
    people = result["affected_population"]
    deficit = result["capacity_deficit"]

    cols = st.columns(4)
    vals = [("👥","Affected population",_fmt(people),"people requiring safe placement"),("🏠","Shelter capacity",_fmt(result["safe_capacity"]),"registered physical capacity"),("🟢","Available space",_fmt(remaining),"after current occupancy"),("🚨","Placement deficit",_fmt(deficit),"people still without space")]
    for col,(i,l,v,s) in zip(cols,vals):
        with col: kpi(i,l,v,s)

    st.markdown("### 🧭 Readiness status")
    a,b,c=st.columns(3)
    with a:
        cls='good' if deficit==0 else 'bad'; text='READY' if deficit==0 else 'CAPACITY BREACH'
        st.markdown(f'<div class="status {cls}">🏠 {text}<br><small>Physical shelter coverage</small></div>',unsafe_allow_html=True)
    with b:
        cls='good' if result['resource_deficit']==0 else 'warn'; text='LIFELINES READY' if result['resource_deficit']==0 else 'LIFELINE BOTTLENECK'
        st.markdown(f'<div class="status {cls}">💧 {text}<br><small>Limiting resource: {result["bottleneck"]}</small></div>',unsafe_allow_html=True)
    with c:
        st.markdown(f'<div class="status info">📊 {result["demand_coverage_pct"]:.0f}% DEMAND COVERED<br><small>Effective readiness coverage</small></div>',unsafe_allow_html=True)

    st.markdown("### 📦 Lifeline capacity matrix")
    resource_df = pd.DataFrame([{"Resource":k,"Capacity":v,"Share of demand":min(100,round(v/max(people,1)*100,1))} for k,v in result["resources"].items()])
    st.dataframe(resource_df, hide_index=True, width="stretch", column_config={"Share of demand":st.column_config.ProgressColumn("Share of demand",min_value=0,max_value=100,format="%d%%")})

    st.markdown("### 🧑‍🤝‍🧑 Vulnerability triage")
    bd = vulnerable_population_breakdown(people)
    bdf=pd.DataFrame([{"Group":k,"People":v,"Priority":"HIGH" if k in ("Children (<12y)","Elderly (60y+)","Persons with disabilities") else "NORMAL"} for k,v in bd.items()])
    st.dataframe(bdf,hide_index=True,width="stretch")

    st.markdown("### 🚑 Deployment pack")
    req=resource_requirements(result["people_still_to_place"])
    cols=st.columns(6)
    for col,(icon,label,key) in zip(cols,[("🚌","Buses","buses"),("🚑","Ambulances","ambulances"),("🧑‍🚒","Rescuers","rescue_personnel"),("💧","Water/day","water_liters_day"),("🍱","Meals","meals"),("🏥","Medical beds","medical_beds")]):
        with col: kpi(icon,label,_fmt(req[key]),"estimated requirement")

    st.markdown(f'''<div class="action-card"><div class="small">RECOMMENDED OPERATIONAL ACTION</div><div class="big">{'🚨 Activate relocation logistics' if deficit or result['resource_deficit'] else '✅ Hub is operationally ready'}</div><div class="small">{result['people_still_to_place']:,} people remain in the placement pipeline. Bottleneck: {result['bottleneck']}.</div></div>''',unsafe_allow_html=True)
