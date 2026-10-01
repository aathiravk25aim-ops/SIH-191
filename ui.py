import streamlit as st
import pandas as pd
from models import predict_habitation_action


def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    :root{--navy:#071426;--blue:#0ea5e9;--cyan:#22d3ee;--green:#22c55e;--amber:#f59e0b;--red:#ef4444;--muted:#64748b;--card:rgba(255,255,255,.92)}
    html,body,[class*="css"]{font-family:'Inter',sans-serif}
    .stApp{background:radial-gradient(circle at 10% 5%,rgba(34,211,238,.14),transparent 25%),radial-gradient(circle at 90% 15%,rgba(14,165,233,.13),transparent 28%),linear-gradient(135deg,#f8fbff 0%,#eef6fb 55%,#f8fafc 100%);}
    .stApp:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.20;background-image:linear-gradient(rgba(14,165,233,.12) 1px,transparent 1px),linear-gradient(90deg,rgba(14,165,233,.12) 1px,transparent 1px);background-size:42px 42px;mask-image:linear-gradient(to bottom,black,transparent 75%);}
    [data-testid="stHeader"]{background:rgba(255,255,255,0);}
    [data-testid="stSidebar"]{background:linear-gradient(180deg,#071426 0%,#0b2037 100%);border-right:1px solid rgba(255,255,255,.08)}
    [data-testid="stSidebar"] *{color:#e5f3ff!important}
    .hero{position:relative;overflow:hidden;padding:34px 38px;border-radius:26px;background:linear-gradient(120deg,rgba(7,20,38,.98),rgba(9,50,78,.94));color:white;box-shadow:0 20px 50px rgba(7,20,38,.20);margin-bottom:22px}
    .hero:after{content:'🛰️  🗺️  🌊  🏘️';position:absolute;right:26px;bottom:12px;font-size:44px;opacity:.20;letter-spacing:12px}
    .hero .eyebrow{font-size:12px;letter-spacing:2px;text-transform:uppercase;color:#67e8f9;font-weight:800}
    .hero h1{font-size:38px;line-height:1.05;margin:8px 0 10px;font-weight:800}
    .hero p{max-width:760px;color:#c7d9e8;font-size:15px;margin:0}
    .pill{display:inline-block;padding:7px 12px;border-radius:999px;background:rgba(34,211,238,.13);border:1px solid rgba(103,232,249,.25);color:#a5f3fc;font-size:12px;font-weight:700;margin-top:18px}
    .kpi{background:var(--card);border:1px solid rgba(15,23,42,.06);border-radius:18px;padding:18px 20px;box-shadow:0 8px 30px rgba(15,23,42,.07);min-height:118px;transition:transform .2s ease,box-shadow .2s ease}
    .kpi:hover{transform:translateY(-3px);box-shadow:0 14px 35px rgba(15,23,42,.12)}
    .kpi .icon{font-size:26px}.kpi .label{color:#64748b;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;margin-top:8px}.kpi .value{font-size:28px;font-weight:800;color:#0f172a;margin-top:2px}.kpi .sub{font-size:11px;color:#64748b;margin-top:4px}
    .section-title{font-size:20px;font-weight:800;color:#0f172a;margin:20px 0 8px}.section-sub{color:#64748b;font-size:13px;margin-bottom:14px}
    .glass{background:rgba(255,255,255,.78);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.8);border-radius:20px;padding:20px;box-shadow:0 10px 35px rgba(15,23,42,.06)}
    .status{padding:12px 15px;border-radius:14px;font-weight:700;font-size:13px}.status.good{background:#ecfdf5;color:#047857;border:1px solid #a7f3d0}.status.warn{background:#fffbeb;color:#b45309;border:1px solid #fde68a}.status.bad{background:#fef2f2;color:#b91c1c;border:1px solid #fecaca}.status.info{background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe}
    .action-card{padding:22px;border-radius:20px;background:linear-gradient(135deg,#0b2037,#0f3b5b);color:white;box-shadow:0 12px 35px rgba(7,20,38,.16)}
    .action-card .big{font-size:26px;font-weight:800}.action-card .small{color:#b9d6e8;font-size:12px;margin-top:5px}
    div[data-baseweb="tab-list"]{gap:7px;background:rgba(255,255,255,.68);padding:7px;border-radius:16px;border:1px solid rgba(15,23,42,.05)}
    button[data-baseweb="tab"]{border-radius:11px!important;font-weight:700!important}
    button[data-baseweb="tab"][aria-selected="true"]{background:#0b2037!important;color:white!important}
    .stButton>button{border-radius:12px;border:1px solid #dbe5ee;background:white;font-weight:700;box-shadow:0 4px 14px rgba(15,23,42,.05);transition:.2s}.stButton>button:hover{transform:translateY(-2px);border-color:#22d3ee}
    .stDownloadButton>button{border-radius:12px!important;font-weight:700!important}
    .metric-wrap{display:flex;gap:8px;align-items:center}.metric-icon{font-size:23px}
    .footer{margin-top:30px;padding:18px;text-align:center;color:#64748b;font-size:11px}
    .auth-shell{min-height:78vh;display:flex;align-items:center;justify-content:center;background:radial-gradient(circle at 20% 30%,rgba(34,211,238,.20),transparent 30%),radial-gradient(circle at 80% 70%,rgba(14,165,233,.20),transparent 30%);border-radius:30px;position:relative;overflow:hidden}.auth-panel{width:min(760px,92%);padding:48px;border-radius:28px;background:rgba(7,20,38,.96);color:white;box-shadow:0 30px 80px rgba(7,20,38,.28);text-align:center;position:relative;z-index:2}.auth-brand{font-size:14px;font-weight:800;letter-spacing:2px;color:#67e8f9}.auth-eyebrow{font-size:10px;letter-spacing:2px;color:#94a3b8;margin-top:24px}.auth-panel h1{font-size:48px;margin:8px 0}.auth-panel p{color:#c7d9e8}.auth-orb{position:absolute;width:220px;height:220px;border-radius:50%;filter:blur(5px);background:rgba(34,211,238,.15)}.orb1{left:8%;top:10%}.orb2{right:8%;bottom:8%}.hazard-card{min-height:140px;padding:18px;border-radius:18px;background:rgba(255,255,255,.84);border:1px solid #e2e8f0;box-shadow:0 8px 25px rgba(15,23,42,.06);margin-bottom:12px;display:flex;gap:13px}.hazard-icon{font-size:30px}.hazard-score{font-size:25px;font-weight:800;margin:5px 0}.status-mini{font-size:10px;font-weight:800;padding:4px 7px;border-radius:999px}.hazard-meta{font-size:11px;color:#64748b;margin-top:8px}.sim-summary{padding:24px;border-radius:20px;background:linear-gradient(135deg,#071426,#0f3b5b);color:white;margin-top:8px}.sim-summary .small,.decision-kicker,.ai-eyebrow{font-size:10px;letter-spacing:2px;color:#67e8f9;font-weight:800}.sim-number{font-size:52px;font-weight:800;line-height:1}.sim-number span{font-size:16px;color:#9fb7c8}.insight-line{padding:12px 15px;margin:7px 0;border-radius:12px;background:rgba(255,255,255,.78);border:1px solid #e2e8f0}.ai-hero{padding:28px;border-radius:24px;background:linear-gradient(120deg,#071426,#123c59);color:white;margin-bottom:18px;box-shadow:0 18px 50px rgba(7,20,38,.18)}.ai-hero h2{font-size:34px;margin:6px 0}.ai-hero p{color:#c7d9e8;max-width:800px}.decision-output{padding:25px;border-radius:20px;background:linear-gradient(135deg,#0b2037,#0d4667);color:white;box-shadow:0 16px 40px rgba(7,20,38,.18);margin-bottom:18px}.decision-main{font-size:34px;font-weight:800;margin:7px 0}.decision-detail{font-size:12px;color:#b9d6e8}.signal{margin:14px 0}.signal>div:first-child{display:flex;justify-content:space-between}.signal-track{height:9px;background:#e2e8f0;border-radius:99px;overflow:hidden;margin:7px 0}.signal-track i{display:block;height:100%;background:linear-gradient(90deg,#22d3ee,#0ea5e9);border-radius:99px}.signal small{color:#64748b}.reason{padding:13px 15px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:13px;margin:8px 0;color:#334155}.reason span{color:#0891b2;font-weight:900;margin-right:8px}
    </style>
    """, unsafe_allow_html=True)


def hero():
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">SIH26191 · DISASTER MANAGEMENT · DECISION INTELLIGENCE</div>
      <h1>🛡️ SURAKSHA-ZONE AI</h1>
      <p>Intelligent identification of hazard-based red zones, carrying-capacity assessment, and immediate relocation intelligence for vulnerable habitations.</p>
      <div class="pill">LIVE DECISION SUPPORT · MULTI-HAZARD · GIS · RESOURCE READINESS</div>
    </div>
    """, unsafe_allow_html=True)


def kpi(icon, label, value, sub=""):
    st.markdown(f'''<div class="kpi"><div class="icon">{icon}</div><div class="label">{label}</div><div class="value">{value}</div><div class="sub">{sub}</div></div>''', unsafe_allow_html=True)


def render_auth_page():
    """Render a polished demo authentication gateway."""
    st.markdown("""
    <div class="auth-shell">
      <div class="auth-orb orb1"></div><div class="auth-orb orb2"></div>
      <div class="auth-panel">
        <div class="auth-brand">🛡️ SURAKSHA-ZONE AI</div>
        <div class="auth-eyebrow">SECURE DISASTER INTELLIGENCE CONSOLE</div>
        <h1>Welcome back.</h1>
        <p>Sign in to access multi-hazard intelligence, relocation readiness and AI-assisted decision support.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)
    with st.form("auth_form"):
        c1,c2=st.columns([1,1])
        with c1: username=st.text_input("👤 Operator ID", placeholder="Enter operator ID")
        with c2: role=st.selectbox("🎫 Access role", ["District Control Room","Disaster Management Officer","Field Operations","Demo / Evaluation"])
        password=st.text_input("🔐 Access key", type="password", placeholder="For demo, enter any key")
        remember=st.checkbox("Keep this session active", value=True)
        submitted=st.form_submit_button("🚀 Enter Command Center", use_container_width=True)
    if submitted:
        if username.strip() and password.strip():
            st.session_state.authenticated=True
            st.session_state.operator=username.strip()
            st.session_state.role=role
            st.rerun()
        else:
            st.error("Please enter an Operator ID and Access key.")
    st.caption("Demo authentication gateway — connect this form to your institutional identity provider before production deployment.")


def render_weather_simulator(df):
    """Interactive weather + hazard scenario simulator with separate outputs."""
    st.markdown('<div class="section-title">🌦️ Weather & Hazard Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Create a hypothetical multi-hazard scenario and inspect each hazard independently before viewing the combined operational picture.</div>', unsafe_allow_html=True)
    left,right=st.columns([1,1.25])
    with left:
        location=st.selectbox("📍 Simulation location", df.location.tolist())
        duration=st.slider("⏱️ Scenario duration (hours)",1,72,12)
        rain=st.slider("🌧️ Rainfall (mm / 24h)",0,500,180,10)
        wind=st.slider("💨 Wind speed (km/h)",0,180,65,5)
        temp=st.slider("🌡️ Temperature (°C)",-5,50,31)
        river=st.slider("🌊 River / water-level rise (m)",0.0,10.0,2.0,0.1)
        slope=st.slider("⛰️ Slope saturation (%)",0,100,55,5)
        surge=st.slider("🌊 Coastal surge (m)",0.0,8.0,0.5,0.1)
    row=df[df.location==location].iloc[0].to_dict()
    rain_r=min(100,rain/4); wind_r=min(100,wind/1.8); heat_r=min(100,max(0,(temp-25)*5)); flood_r=min(100,rain_r*.45+river*8+surge*5); landslide_r=min(100,rain_r*.35+slope*.65); cyclone_r=min(100,wind_r*.75+surge*12); heatwave_r=heat_r
    hazards=[("🌧️","Extreme Rainfall",rain_r,"mm/24h",rain), ("🌊","Flood / Inundation",flood_r,"water rise",river), ("⛰️","Landslide Trigger",landslide_r,"saturation",slope), ("💨","High Wind",wind_r,"km/h",wind), ("🌀","Cyclone / Storm Surge",cyclone_r,"surge",surge), ("🌡️","Heat Stress",heatwave_r,"°C",temp)]
    with right:
        st.markdown("### 🔬 Individual hazard outputs")
        cols=st.columns(2)
        for i,(icon,name,score,unit,value) in enumerate(hazards):
            level="CRITICAL" if score>=80 else "HIGH" if score>=60 else "MODERATE" if score>=35 else "LOW"
            cls="bad" if score>=80 else "warn" if score>=60 else "info" if score>=35 else "good"
            with cols[i%2]:
                st.markdown(f'<div class="hazard-card"><div class="hazard-icon">{icon}</div><div><b>{name}</b><div class="hazard-score">{score:.0f}/100</div><span class="status-mini {cls}">{level}</span><div class="hazard-meta">Input: {value} {unit}</div></div></div>',unsafe_allow_html=True)
        combined=min(100,0.30*rain_r+0.20*flood_r+0.15*landslide_r+0.15*wind_r+0.10*cyclone_r+0.10*heatwave_r)
        st.markdown(f'<div class="sim-summary"><div class="small">COMBINED SCENARIO INDEX</div><div class="sim-number">{combined:.0f}<span>/100</span></div><div>📍 {location} · ⏱️ {duration}h scenario</div></div>',unsafe_allow_html=True)
    st.markdown("### 🧭 What the simulator is detecting")
    explanation=[]
    if rain_r>=60: explanation.append("🌧️ Rainfall is high enough to increase surface runoff and saturation risk.")
    if flood_r>=60: explanation.append("🌊 Flood/inundation pressure is elevated from rainfall, water-level rise or surge.")
    if landslide_r>=60: explanation.append("⛰️ Slope saturation indicates elevated landslide-trigger conditions.")
    if wind_r>=60: explanation.append("💨 Wind loading is elevated and may affect trees, utilities and evacuation logistics.")
    if cyclone_r>=60: explanation.append("🌀 Storm/cyclone pressure is elevated due to wind and coastal surge inputs.")
    if heatwave_r>=60: explanation.append("🌡️ Heat stress is elevated relative to the baseline temperature threshold.")
    if not explanation: explanation.append("✅ No individual simulated hazard crossed the elevated threshold.")
    for x in explanation: st.markdown(f'<div class="insight-line">{x}</div>',unsafe_allow_html=True)
    st.info("Simulator outputs are hypothetical decision-support signals, not official weather warnings or hazard declarations.")


def render_ai_lab(model, df):
    """Premium AI decision laboratory with explainability and scenario comparison."""
    st.markdown('<div class="ai-hero"><div class="ai-eyebrow">🧠 EXPLAINABLE DECISION INTELLIGENCE</div><h2>AI Decision Lab</h2><p>Stress-test a habitation scenario, inspect the model probabilities, and understand which operational signals are driving the recommended horizon.</p></div>',unsafe_allow_html=True)
    left,right=st.columns([1,1.35])
    with left:
        st.markdown("### 🎛️ Scenario controls")
        h=st.slider("🌊 Hazard intensity",0.0,10.0,7.0,0.5)
        p=st.number_input("👥 Population density / km²",0,30000,2500,100)
        preset=st.selectbox("⚡ Load a scenario",["Custom","Urban flood","Mountain landslide","Coastal storm","Extreme rainfall"])
        if preset!="Custom":
            presets={"Urban flood":(8.5,6000),"Mountain landslide":(9.0,1800),"Coastal storm":(8.0,4200),"Extreme rainfall":(7.5,3000)}
            ph,pp=presets[preset]
            st.caption(f"Preset values: hazard {ph}/10 · density {pp:,}/km²")
        label,proba=predict_habitation_action(model,h,p)
        action_icon={"Immediate":"🚨","Short-Term":"⚠️","Medium-Term":"🟡","Monitor":"🟢"}.get(label,"🧭")
        st.markdown(f'<div class="decision-output"><div class="decision-kicker">MODEL DECISION HORIZON</div><div class="decision-main">{action_icon} {label}</div><div class="decision-detail">The output is a scenario classification for planning support, not an automatic evacuation order.</div></div>',unsafe_allow_html=True)
        st.markdown("### 🔍 Signal decomposition")
        for name,val,desc in [("Hazard pressure",h*10,"Direct hazard intensity"),("Population exposure",min(100,p/100),"Population density pressure"),("Combined stress",min(100,(h*10*.6)+(min(100,p/100)*.4)),"Illustrative combined signal")]:
            st.markdown(f'<div class="signal"><div><b>{name}</b><span>{val:.0f}%</span></div><div class="signal-track"><i style="width:{val:.0f}%"></i></div><small>{desc}</small></div>',unsafe_allow_html=True)
    with right:
        st.markdown("### 📊 Probability profile")
        pdf=pd.DataFrame({"Horizon":list(proba.keys()),"Probability (%)":list(proba.values())})
        st.bar_chart(pdf.set_index("Horizon"),height=320)
        st.markdown("### 🧩 Why did the model respond this way?")
        reasons=[]
        if h>=7: reasons.append("High hazard intensity is pushing the scenario toward earlier intervention.")
        elif h>=4: reasons.append("Moderate hazard intensity contributes meaningful risk pressure.")
        else: reasons.append("Lower hazard intensity reduces immediate intervention pressure.")
        if p>=5000: reasons.append("Very high population density increases potential exposure and resource demand.")
        elif p>=2000: reasons.append("Population density adds a moderate exposure burden.")
        else: reasons.append("Lower population density reduces the exposure component.")
        for r in reasons: st.markdown(f'<div class="reason"><span>✓</span>{r}</div>',unsafe_allow_html=True)
        st.markdown("### 🧪 Compare scenarios")
        compare=[("Current",h,p),("Lower hazard",max(0,h-2),p),("Higher exposure",h,min(30000,p+3000))]
        cdf=[]
        for n,hh,pp in compare:
            ll,_=predict_habitation_action(model,hh,pp); cdf.append({"Scenario":n,"Hazard":hh,"Density":pp,"Horizon":ll})
        st.dataframe(pd.DataFrame(cdf),hide_index=True,width="stretch")
