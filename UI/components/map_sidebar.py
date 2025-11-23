# components/map_sidebar.py
import streamlit as st
from datetime import datetime
from streamlit_folium import st_folium
from .map_utils import create_route_map

def init_map_session_state():
    """Khởi tạo session_state cho map"""
    defaults = {
        "route_start": "",
        "route_end": "",
        "route_map": None,
        "route_info": "",
        "submit_route": False,
        "reload_trigger": False,
        "saved_routes": []
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def render_map_sidebar(map_col=None):
    init_map_session_state()
    if map_col is None:
        return

    with map_col:
        st.markdown('<i class="fa-solid fa-map-location"></i> Route Planning', unsafe_allow_html=True)

        # Form nhập tuyến
        with st.form("route_form"):
            start_loc = st.text_input("Starting Point", value=st.session_state.route_start, placeholder="E.g., Ho Chi Minh City")
            end_loc = st.text_input("Destination", value=st.session_state.route_end, placeholder="E.g., Hanoi")
            submit_route = st.form_submit_button("Find Route", use_container_width=True)

        # Xử lý submit / trigger
        if submit_route or st.session_state.submit_route or st.session_state.reload_trigger:
            st.session_state.submit_route = False
            st.session_state.reload_trigger = False
            st.session_state.route_start = start_loc
            st.session_state.route_end = end_loc

            with st.spinner("Calculating route..."):
                route_map, route_info = create_route_map(start_loc, end_loc)
                if route_map:
                    st.session_state.route_map = route_map
                    st.session_state.route_info = route_info
                else:
                    st.error(route_info)

        # Render map + info
        if st.session_state.route_map:
            st.markdown(f"<div class='route-info'>{st.session_state.route_info}</div>", unsafe_allow_html=True)
            st_folium(st.session_state.route_map, width=None, height=400, key="route_map_display")

            if st.button("Save Route", use_container_width=True):
                route_data = {
                    "start": st.session_state.route_start,
                    "end": st.session_state.route_end,
                    "info": st.session_state.route_info,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                if route_data not in st.session_state.saved_routes:
                    st.session_state.saved_routes.append(route_data)
                    st.success("Route saved!")

        # Quick route templates
        st.markdown("---")
        st.markdown('<i class="fa-solid fa-location-pin"></i> Popular Routes', unsafe_allow_html=True)
        popular_routes = [
            {"name": "HCMC → Hanoi", "start": "Ho Chi Minh City", "end": "Hanoi"},
            {"name": "HCMC → Da Nang", "start": "Ho Chi Minh City", "end": "Da Nang"},
            {"name": "Hanoi → Ha Long", "start": "Hanoi", "end": "Ha Long"},
            {"name": "HCMC → Vung Tau", "start": "Ho Chi Minh City", "end": "Vung Tau"},
            {"name": "HCMC → Da Lat", "start": "Ho Chi Minh City", "end": "Da Lat"}
        ]
        for route in popular_routes:
            if st.button(route["name"], key=f"route_{route['name']}", use_container_width=True):
                st.session_state.route_start = route['start']
                st.session_state.route_end = route['end']
                st.session_state.submit_route = True

        # Saved routes
        if st.session_state.saved_routes:
            st.markdown("---")
            st.markdown('<i class="fa-solid fa-street-view"></i> Saved Routes', unsafe_allow_html=True)
            for i, saved in enumerate(st.session_state.saved_routes):
                with st.expander(f"{saved['start'][:15]}... → {saved['end'][:15]}..."):
                    st.write(f"**Start:** {saved['start']}")
                    st.write(f"**End:** {saved['end']}")
                    st.write(f"**{saved['info']}**")
                    st.caption(f"{saved['timestamp']}")

                    col_a, col_b = st.columns(2)
                    if col_a.button("Reload", key=f"reload_route_{i}"):
                        st.session_state.route_start = saved['start']
                        st.session_state.route_end = saved['end']
                        st.session_state.reload_trigger = True

                    if col_b.button("Delete", key=f"delete_route_{i}"):
                        st.session_state.saved_routes.pop(i)
                        st.experimental_rerun()

        # Map info
        st.markdown("---")
        st.info("""
        💡 **Instructions:**
        - Enter location names (e.g., Ho Chi Minh City, Hanoi)
        - Click "Find Route"
        - View map and detailed information
        - Save favorite routes
        """)
