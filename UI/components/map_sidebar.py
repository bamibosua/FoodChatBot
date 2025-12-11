import streamlit as st
from streamlit_folium import st_folium
import folium
from UI.components.map_utils import create_multi_destination_map

def init_map_session_state():
    defaults = {
        "current_location": "",
        "multi_map": None,
        "multi_info": {},
        "show_default_map": True
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render_map_sidebar(map_col=None, RESTAURANT_PLACES=[]):
    init_map_session_state()
    if map_col is None:
        return

    with map_col:
        st.markdown("## 🗺️ Route")
        
        #RESTAURANT_PLACES = st.session_state.get("filtered_restaurants", [])
        # ---------------- INPUT FORM ----------------
        with st.form("location_form", clear_on_submit=False):
            st.text_input(
                "📍 Your Location",
                key="current_location_input",
                placeholder="E.g., District 1, Ho Chi Minh City"
            )
            loc = st.session_state.current_location_input
            submit = st.form_submit_button("🚗 Show Routes", use_container_width=True)

        # ---------------- SUBMIT ----------------
    
        if submit:
            if not loc.strip():
                st.warning("⚠️ Please enter your location!")
            else:
                st.session_state.current_location = st.session_state.current_location_input

                with st.spinner("🔄 Creating routes..."):
                    if not RESTAURANT_PLACES:
                        st.session_state.multi_map = None
                        st.session_state.multi_info = {}
                        st.session_state.show_default_map = True
                    else:
                        m, info = create_multi_destination_map(loc, RESTAURANT_PLACES)
                        if m:
                            st.session_state.multi_map = m
                            st.session_state.multi_info = info
                            st.session_state.show_default_map = False
                        else:
                            st.session_state.multi_map = None
                            st.session_state.multi_info = {}
                            st.session_state.show_default_map = True
                            
# =======================================================
        #          LUÔN HIỂN THỊ MAP - FIX LOGIC
        # =======================================================
        st.markdown("### 🗺️ Map View")

        # ✅ FIX: Kiểm tra route map TRƯỚC
        if st.session_state.multi_map and not st.session_state.get("show_default_map", True):
            st_folium(
                st.session_state.multi_map,
                height=450,
                returned_objects=[],
                key="map_route"
            )

        # Nếu CHƯA có route nhưng CÓ RESTAURANTS → show markers only
        elif RESTAURANT_PLACES:
            m = folium.Map(location=[10.776, 106.7], zoom_start=12)
            for r in RESTAURANT_PLACES:
                if r.get("lat") and r.get("lng"):  # ← FIX: Kiểm tra tọa độ
                    folium.Marker(
                        [r["lat"], r["lng"]],
                        popup=r.get("name", "Restaurant"),
                        icon=folium.Icon(color='blue', icon='utensils', prefix='fa')
                    ).add_to(m)

            st_folium(m, height=450, key="map_restaurants")

        # Không có gì → default map
        else:
            default_map = folium.Map(location=[10.776, 106.7], zoom_start=12)
            st_folium(default_map, height=450, key="map_default")


        # ---------------- ROUTE DETAILS ----------------
        if st.session_state.multi_info and not st.session_state.show_default_map:
            st.markdown("---")
            st.markdown("### 🎯 Route Details")

            icons = "🔵🔴🟣🟠🟤"

            for idx, (name, info) in enumerate(st.session_state.multi_info.items(), 1):
                with st.expander(
                    f"{icons[(idx - 1) % len(icons)]} {idx}. {name} - {info['distance_km']:.1f} km",
                    icon="📍",
                    expanded=(idx <= 2)
                ):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📏 Distance", f"{info['distance_km']:.2f} km")
                    with col2:
                        st.metric("⏱️ Time", f"{info['duration_hrs']*60:.0f} min")
