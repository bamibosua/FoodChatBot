# components/map_sidebar.py
import streamlit as st
from streamlit_folium import st_folium
try:
    from map import create_route_map
    OSM_AVAILABLE = True
except:
    OSM_AVAILABLE = False

def render_map_sidebar():
    st.markdown("Route Planning")

    with st.form("route_form"):
        start = st.text_input("From", value=st.session_state.get("route_start", ""))
        end = st.text_input("To", value=st.session_state.get("route_end", ""))
        submitted = st.form_submit_button("Find Route")

    if submitted or st.session_state.get("submit_route", False) or st.session_state.get("reload_trigger", False):
        st.session_state.submit_route = False
        st.session_state.reload_trigger = False
        st.session_state.route_start = start
        st.session_state.route_end = end

        with st.spinner("Finding route..."):
            if OSM_AVAILABLE:
                route_map, info = create_route_map(start, end)
                if route_map:
                    st.session_state.route_map = route_map
                    st.session_state.route_info = info
                else:
                    st.error(info)

    if st.session_state.get("route_map"):
        st.markdown(f"<div class='route-info'>{st.session_state.route_info}</div>", unsafe_allow_html=True)
        st_folium(st.session_state.route_map, height=400, key="map")

        if st.button("Save Route"):
            route = {
                "start": start,
                "end": end,
                "info": st.session_state.route_info,
                "timestamp": st.session_state.route_info.split("Time:")[-1] if "Time:" in st.session_state.route_info else ""
            }
            if route not in st.session_state.saved_routes:
                st.session_state.saved_routes.append(route)
                st.success("Route saved!")

    # Popular routes
    st.markdown("Popular Routes")
    routes = [
        ("HCMC → Hanoi", "Ho Chi Minh City", "Hanoi"),
        ("HCMC → Da Nang", "Ho Chi Minh City", "Da Nang"),
        ("HCMC → Vung Tau", "Ho Chi Minh City", "Vung Tau"),
    ]
    for name, s, e in routes:
        if st.button(name, key=name):
            st.session_state.route_start = s
            st.session_state.route_end = e
            st.session_state.submit_route = True
            st.rerun()

    # Saved routes
    if st.session_state.saved_routes:
        st.markdown("Saved Routes")
        for i, r in enumerate(st.session_state.saved_routes):
            with st.expander(f"{r['start'][:15]} → {r['end'][:15]}"):
                st.write(r["info"])
                if st.button("Reload", key=f"reload_{i}"):
                    st.session_state.route_start = r["start"]
                    st.session_state.route_end = r["end"]
                    st.session_state.reload_trigger = True
                    st.rerun()