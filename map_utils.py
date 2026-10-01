"""GIS map utilities for SIH26191. Requires folium, streamlit_folium, requests."""
from __future__ import annotations
import math
import requests
import folium
from folium.plugins import Fullscreen, MiniMap, MeasureControl, LocateControl, HeatMap
from streamlit_folium import st_folium
from risk_engine import assess_habitation, risk_color


def calculate_haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)


def _safe_json(response):
    try:
        return response.json()
    except Exception:
        return None


def fetch_nearby_osm_pois(lat, lon, radius_m=12000):
    """Best-effort real OSM POI lookup; returns hospitals and schools separately."""
    query = f"""
    [out:json][timeout:12];
    (
      nwr[amenity=hospital](around:{radius_m},{lat},{lon});
      nwr[amenity=clinic](around:{radius_m},{lat},{lon});
      nwr[amenity=school](around:{radius_m},{lat},{lon});
    );
    out center tags;
    """
    try:
        r = requests.post("https://overpass-api.de/api/interpreter", data=query, timeout=15)
        if r.status_code != 200:
            return {"hospitals": [], "schools": []}
        data = _safe_json(r) or {}
    except requests.RequestException:
        return {"hospitals": [], "schools": []}

    result = {"hospitals": [], "schools": []}
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        p_lat = el.get("lat", el.get("center", {}).get("lat"))
        p_lon = el.get("lon", el.get("center", {}).get("lon"))
        if p_lat is None or p_lon is None:
            continue
        amenity = tags.get("amenity", "")
        item = {"name": tags.get("name", "Unnamed facility"), "lat": p_lat, "lon": p_lon, "type": amenity.title()}
        if amenity in ("hospital", "clinic"):
            result["hospitals"].append(item)
        elif amenity == "school":
            result["schools"].append(item)
    return result


def _fallback_pois(row):
    def split_names(text):
        return [x.strip() for x in str(text or "").split(",") if x.strip()]
    hs = split_names(row.get("hospitals"))
    ss = split_names(row.get("schools"))
    hospitals = [{"name": n, "lat": row["red_lat"] + i * 0.008, "lon": row["red_lon"] + i * 0.006, "type": "Listed hospital"} for i, n in enumerate(hs[:3])]
    schools = [{"name": n, "lat": row["red_lat"] - i * 0.007, "lon": row["red_lon"] + i * 0.005, "type": "Listed school"} for i, n in enumerate(ss[:4])]
    return {"hospitals": hospitals, "schools": schools}


def _legend_html():
    return """
    <div style='position:fixed;bottom:20px;left:20px;z-index:9999;background:rgba(15,23,42,.95);color:#fff;padding:12px 16px;border-radius:14px;border:1px solid #334155;font:12px Arial;box-shadow:0 8px 28px rgba(0,0,0,.3)'>
      <b style='font-size:13px'>Risk & Infrastructure</b><br>
      <span style='color:#DC2626'>●</span> Critical 80–100 &nbsp;
      <span style='color:#F97316'>●</span> High 60–79<br>
      <span style='color:#EAB308'>●</span> Medium 35–59 &nbsp;
      <span style='color:#22C55E'>●</span> Low 0–34<br>
      <span style='color:#166534'>◆</span> Safe hub &nbsp;
      <span style='color:#2563EB'>✚</span> Hospital &nbsp;
      <span style='color:#7C3AED'>▣</span> School
    </div>
    """


def build_gis_map(df, selected_loc="None", show_heatmap=True, show_hospitals=True, show_schools=True):
    if selected_loc != "None" and selected_loc in set(df["location"].astype(str)):
        selected = df[df["location"] == selected_loc].iloc[0]
        center = [float(selected["red_lat"]), float(selected["red_lon"])]
        zoom = 10
    else:
        center = [22.5937, 78.9629]
        zoom = 5
        selected = None

    m = folium.Map(location=center, zoom_start=zoom, tiles=None, control_scale=True, prefer_canvas=True)
    folium.TileLayer("OpenStreetMap", name="Street", show=True).add_to(m)
    folium.TileLayer("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", attr="OpenTopoMap", name="Terrain", show=False, max_zoom=17).add_to(m)
    folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Esri World Imagery", name="Satellite", show=False, max_zoom=19).add_to(m)

    risk_group = folium.FeatureGroup(name="Hazard Zones", show=True).add_to(m)
    safe_group = folium.FeatureGroup(name="Safe Relocation Hubs", show=True).add_to(m)
    hospital_group = folium.FeatureGroup(name="Hospitals / Clinics", show=show_hospitals).add_to(m)
    school_group = folium.FeatureGroup(name="Schools / Staging", show=show_schools).add_to(m)
    route_group = folium.FeatureGroup(name="Evacuation Corridors", show=True).add_to(m)
    heat_points = []

    for _, row in df.iterrows():
        assessment = assess_habitation(row.to_dict())
        score = assessment["score"]
        rc = risk_color(score)
        lat, lon = float(row["red_lat"]), float(row["red_lon"])
        zone_radius = 4000 + score * 45
        heat_points.append([lat, lon, score / 100.0])

        folium.Circle(
            location=[lat, lon], radius=zone_radius, color=rc["hex"], fill=True,
            fill_color=rc["hex"], fill_opacity=0.12, weight=2,
            tooltip=f"{rc['emoji']} {row['location']} · {score:.0f}/100"
        ).add_to(risk_group)
        folium.CircleMarker(
            location=[lat, lon], radius=8 + score / 18, color="#FFFFFF", weight=2,
            fill=True, fill_color=rc["hex"], fill_opacity=.95,
            tooltip=f"{row['location']} | {rc['tier']} | {score:.1f}/100",
            popup=folium.Popup(
                f"<b style='font-size:15px'>{rc['emoji']} {row['location']}</b><br>"
                f"State: {row['state']}<br>Hazard: {row['disaster_type']}<br>"
                f"Risk score: <b>{score:.1f}/100</b> ({rc['tier']})<br>"
                f"Affected population: {int(row['affected_population']):,}<br>"
                f"Safe hub: {row['green_name']}<br>"
                f"Shelter capacity: {int(row['shelter_capacity']):,}", max_width=330)
        ).add_to(risk_group)

        folium.Marker(
            [float(row["green_lat"]), float(row["green_lon"])],
            icon=folium.Icon(color="green", icon="shield", prefix="fa"),
            tooltip=f"Safe hub · {row['green_name']}",
            popup=folium.Popup(f"<b>🛡 {row['green_name']}</b><br>Capacity: {int(row['shelter_capacity']):,}<br>Elevation: {row['safe_elevation_m']} m", max_width=300)
        ).add_to(safe_group)

        folium.PolyLine(
            [[lat, lon], [float(row["green_lat"]), float(row["green_lon"])]],
            color="#2563EB", weight=3, opacity=.75, dash_array="8,8",
            tooltip=f"Evacuation corridor → {row['green_name']}"
        ).add_to(route_group)

    if show_heatmap and heat_points:
        HeatMap(heat_points, name="Risk Heatmap", radius=28, blur=24, min_opacity=.25, show=False).add_to(m)

    if selected is not None:
        pois = fetch_nearby_osm_pois(float(selected["red_lat"]), float(selected["red_lon"]))
        if not pois["hospitals"] and not pois["schools"]:
            pois = _fallback_pois(selected)
        for h in pois["hospitals"][:12]:
            folium.Marker(
                [h["lat"], h["lon"]], icon=folium.Icon(color="blue", icon="plus", prefix="fa"),
                tooltip=f"Hospital: {h['name']}", popup=folium.Popup(f"<b>🏥 {h['name']}</b><br>{h['type']}", max_width=260)
            ).add_to(hospital_group)
        for s in pois["schools"][:16]:
            folium.Marker(
                [s["lat"], s["lon"]], icon=folium.Icon(color="purple", icon="graduation-cap", prefix="fa"),
                tooltip=f"School: {s['name']}", popup=folium.Popup(f"<b>🏫 {s['name']}</b><br>{s['type']}<br>Potential staging / secondary shelter point", max_width=280)
            ).add_to(school_group)
        m.fit_bounds([[selected["red_lat"], selected["red_lon"]], [selected["green_lat"], selected["green_lon"]]])

    Fullscreen(position="topleft").add_to(m)
    MiniMap(toggle_display=True, position="bottomright").add_to(m)
    MeasureControl(primary_length_unit="kilometers", position="topleft").add_to(m)
    LocateControl(position="topleft").add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    m.get_root().html.add_child(folium.Element(_legend_html()))
    return st_folium(m, width="100%", height=650, returned_objects=[])
