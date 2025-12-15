import streamlit as st
import json
import os
import base64
import folium
import uuid
from streamlit_folium import st_folium

from .logic import parse_user_input, process_logic, generate_reply
from .map_utils import geocode
from .map_utils import create_multi_destination_map

from UI.config.settings import NUMBER_OF_MESSAGES_TO_DISPLAY
from UI.utils.helpers import save_current_chat, new_chat_id, initialize_conversation, load_user_chats

def init_food_state():
    defaults = {
        "history": [],
        "conversation_history": initialize_conversation(st.session_state.current_chat_id, st.session_state.username),
        "final_data": {"location": None, "foods": [], "budget": None, "taste": None},  # Giữ nguyên default
        "chat_titles": {},
        "favorites": [],
        "pending_user_input": None,
        "filtered_restaurants": {},
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Tạo chat mới nếu chưa có current_chat_id
    if "current_chat_id" not in st.session_state or st.session_state.current_chat_id is None:
        st.session_state.current_chat_id = new_chat_id()
        # RESET FINAL DATA KHI TẠO CHAT MỚI
        st.session_state.final_data = {
            "location": None,
            "foods": [],
            "budget": None,
            "taste": None
        }

    # Load all_chats khi đăng nhập
    if "all_chats" not in st.session_state or not st.session_state.all_chats:
        st.session_state.all_chats = load_user_chats(st.session_state.username)

    # Reset final_data khi bắt đầu chat mới (nếu history rỗng)
    if len(st.session_state.history) == 0:
        st.session_state.final_data = {
            "location": None,
            "foods": [],
            "budget": None,
            "taste": None
        }
        
        welcome = (
            "Hello! I'm your food assistant!\n"
            "Please enter your preferred district in Ho Chi Minh City, "
            "your taste or food you want, and your budget (VND)."
        )
        st.session_state.history.append({"role": "assistant", "content": welcome})
        st.session_state.conversation_history.append(
            {"role": "assistant", "content": welcome}
        )
        # Lưu chat welcome message ngay khi tạo
        save_current_chat()
    
    if "final_data" not in st.session_state:
        st.session_state.final_data = {
            "location": None,
            "foods": [],
            "budget": None,
            "taste": None
        }
        
def init_map_session_state():
    defaults = {
        # Input & location
        "current_location": "",
        "current_location_input": "",

        # Map & route
        "multi_map": None,
        "multi_info": {},
        "show_default_map": True,
        "map_key": "map_default",

        # Error handling
        "route_error": None,

        # Data
        "filtered_restaurants": [],
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v



def render_messages():
    """
    Render messages với giao diện bubble + auto scroll xuống cuối
    Sử dụng HTML + CSS + JavaScript nhúng trong Streamlit
    """

    # Import module cho phép nhúng HTML/JS/CSS trực tiếp vào Streamlit
    import streamlit.components.v1 as components
    
    # Lấy danh sách tin nhắn gần nhất từ session_state
    # NUMBER_OF_MESSAGES_TO_DISPLAY dùng để giới hạn số tin nhắn hiển thị
    messages = st.session_state.history[-NUMBER_OF_MESSAGES_TO_DISPLAY:]
    
    # ================= BUILD HTML =================
    # Khởi tạo chuỗi HTML chứa CSS + container chat
    html_content = """
    <style>
    /* Khung chứa toàn bộ tin nhắn */
    .chat-container {
        max-height: 450px;              /* Chiều cao tối đa của khung chat */
        overflow-y: auto;               /* Cho phép scroll theo chiều dọc */
        padding: 1rem;                  /* Khoảng cách trong */
        scroll-behavior: smooth;        /* Cuộn mượt */
    }
    
    /* Style chung cho mỗi tin nhắn */
    .chat-message {
        padding: 1rem;                  /* Padding cho bubble */
        border-radius: 0.8rem;          /* Bo góc */
        margin-bottom: 1rem;            /* Khoảng cách giữa các tin */
        display: flex;                  /* Dùng flex để căn avatar + nội dung */
        align-items: flex-start;
        gap: 0.8rem;                    /* Khoảng cách avatar -> nội dung */
        animation: fadeIn 0.3s ease-in; /* Hiệu ứng xuất hiện */
    }
    
    /* Animation khi tin nhắn xuất hiện */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Tin nhắn của BOT */
    .chat-message.bot {
        background: white;              /* Nền trắng */
        margin-right: 20%;              /* Chừa bên phải */
        border-bottom-left-radius: 0.2rem;
    }

    /* Tin nhắn của USER */
    .chat-message.user {
        background: #CEE6F2;             /* Nền xanh nhạt */
        margin-left: 20%;               /* Chừa bên trái */
        flex-direction: row-reverse;    /* Đảo avatar sang phải */
        border-bottom-right-radius: 0.2rem;
    }
    
    /* Avatar (icon) */
    .chat-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;             /* Avatar hình tròn */
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;              /* Kích thước emoji */
        flex-shrink: 0;                 /* Không bị co lại */
        background: rgba(255, 255, 255, 0.2);
    }
    
    /* Nội dung tin nhắn */
    .chat-content {
        flex: 1;                        /* Chiếm hết phần còn lại */
        color: black;                  /* Màu chữ */
        line-height: 1.6;              /* Giãn dòng */
        word-wrap: break-word;         /* Tự xuống dòng khi dài */
    }
    
    /* Nhãn role (ASSISTANT / YOU) */
    .chat-role {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.3rem;
        opacity: 0.9;
    }
    </style>
    
    <!-- Container chính của chat -->
    <div class="chat-container" id="chatContainer">
    """

    
    # ================= ADD MESSAGES =================
    # Lặp qua từng tin nhắn trong history
    for msg in messages:
        # Xác định class CSS theo role
        role_class = "bot" if msg["role"] == "assistant" else "user"
        
        # Chọn avatar tương ứng
        avatar = "🤖" if msg["role"] == "assistant" else "👨‍🚀"
        
        # Nhãn hiển thị role
        role_label = "ASSISTANT" if msg["role"] == "assistant" else "YOU"
        
        # Thay ký tự xuống dòng bằng <br> để hiển thị trong HTML
        content = msg["content"].replace("\n", "<br>")
        
        # Ghép HTML cho từng tin nhắn
        html_content += f"""
        <div class="chat-message {role_class}">
            <div class="chat-avatar">{avatar}</div>
            <div class="chat-content">
                <div class="chat-role">{role_label}</div>
                {content}
            </div>
        </div>
        """

    # ================= AUTO SCROLL SCRIPT =================
    html_content += """
        <div id="bottom"></div>
    </div>
    
    <script>
    // Hàm cuộn xuống cuối khung chat
    function scrollToBottom() {
        const container = document.getElementById('chatContainer');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }
    
    // Cuộn khi trang load xong
    window.addEventListener('load', scrollToBottom);
    
    // Cuộn lại nhiều lần để đảm bảo nội dung render xong
    setTimeout(scrollToBottom, 100);
    setTimeout(scrollToBottom, 300);
    setTimeout(scrollToBottom, 500);
    </script>
    """

    # Render with iframe
    components.html(html_content, height=490, scrolling=False)

def render_main_chat():
        
    init_food_state()

    current_title = st.session_state.chat_titles.get(
        st.session_state.current_chat_id, "New Chat"
    )
    st.markdown(f"{current_title}")

    render_messages()

    # XỬ LÝ PENDING INPUT TRƯỚC KHI RENDER
    if st.session_state.pending_user_input:
        user_msg = st.session_state.pending_user_input
        st.session_state.pending_user_input = None

        # 1️.parse
        parsed_data, original_lang = parse_user_input(user_msg)

        if isinstance(parsed_data, dict) and parsed_data.get("intent") == "NotFood":
            bot_reply = parsed_data["message"]
            
            # Lưu bot reply
            st.session_state.history.append({"role": "assistant", "content": bot_reply})
            st.session_state.conversation_history.append(
                {"role": "assistant", "content": bot_reply}
            )
            # LƯU NGAY SAU KHI CÓ PHẢN HỒI
            save_current_chat()
            st.rerun()

        # 2️.xử lý logic (chỉ chạy 1 lần)
        processed_result = process_logic(       
            parsed_data,
            original_lang,
            st.session_state.final_data
        )

        # lưu kết quả vào session_state
        st.session_state.processed_result = processed_result
        st.session_state.original_lang_for_result = original_lang
        st.session_state.filtered_restaurants = processed_result.get("processed_data", {})

        # 3️tạo output bot_reply
        bot_reply = generate_reply(processed_result, original_lang)

        # LƯU BOT REPLY
        st.session_state.history.append({"role": "assistant", "content": bot_reply})
        st.session_state.conversation_history.append(
            {"role": "assistant", "content": bot_reply}
        )
        
        # LƯU NGAY SAU KHI CÓ PHẢN HỒI VÀO HISTORY
        save_current_chat()
        st.rerun()
    
    # NHẬN INPUT MỚI
    user_input = st.chat_input("Type your message...")

    if user_input:
        # LƯU USER MESSAGE
        st.session_state.history.append({"role": "user", "content": user_input})
        st.session_state.conversation_history.append(
            {"role": "user", "content": user_input}
        )
        # LƯU NGAY SAU KHI NGƯỜI DÙNG GỬI
        save_current_chat()
        
        st.session_state.pending_user_input = user_input
        st.rerun()
 
def render_map_sidebar(map_col=None, restaurant_places=None):
    # Khởi tạo các biến cần thiết trong session_state
    init_map_session_state()

    # Nếu không có cột để render map thì thoát luôn
    if map_col is None:
        return

    # TỰ ĐỘNG RESET KHI RESTAURANT THAY ĐỔI (CHỈ RESET KHI ĐÃ CÓ ROUTE)
    check_and_reset_on_restaurant_change(restaurant_places)

    with map_col:
        st.markdown("## 🗺️ Route")

        # Render form nhập vị trí + xử lý submit
        render_location_form_and_handle_submit(restaurant_places)

        # Render bản đồ (route / marker / map mặc định)
        render_map_view(restaurant_places)

        # Render chi tiết từng route (distance, time, address)
        render_route_details()


def init_map_session_state():
    """Khởi tạo session state cho map"""
    if "multi_map" not in st.session_state:
        st.session_state.multi_map = None
    
    if "multi_info" not in st.session_state:
        st.session_state.multi_info = {}
    
    if "show_default_map" not in st.session_state:
        st.session_state.show_default_map = True
    
    if "map_key" not in st.session_state:
        st.session_state.map_key = "map_default"
    
    if "current_location" not in st.session_state:
        st.session_state.current_location = ""
    
    if "route_error" not in st.session_state:
        st.session_state.route_error = None
    
    # Khởi tạo fingerprint để track thay đổi restaurant
    if "previous_restaurants_ids" not in st.session_state:
        st.session_state.previous_restaurants_ids = None


def check_and_reset_on_restaurant_change(restaurant_places):
    """
    Tự động reset routes khi danh sách restaurant thay đổi
    CHỈ reset nếu đã có route (user đã nhập location trước đó)
    """
    # Tạo fingerprint của danh sách restaurant hiện tại
    current_restaurants_ids = get_restaurant_fingerprint(restaurant_places)
    
    # Lấy fingerprint đã lưu từ session_state
    previous_restaurants_ids = st.session_state.get("previous_restaurants_ids", None)
    
    # So sánh: nếu khác nhau => restaurants đã thay đổi
    if previous_restaurants_ids != current_restaurants_ids:
        # *CHỈ RESET NẾU ĐÃ CÓ ROUTE*
        # Kiểm tra xem user đã tạo route chưa
        has_existing_route = (
            st.session_state.multi_map is not None or
            st.session_state.current_location.strip() != ""
        )
        
        if has_existing_route:
            # Reset toàn bộ routes và input
            reset_route_state()
            
            # Clear input location
            if "current_location_input" in st.session_state:
                st.session_state.current_location_input = ""
            if "current_location" in st.session_state:
                st.session_state.current_location = ""
            
            # Clear error
            st.session_state.route_error = None
        
        # Luôn cập nhật fingerprint mới (dù có reset hay không)
        st.session_state.previous_restaurants_ids = current_restaurants_ids


def get_restaurant_fingerprint(restaurant_places):
    """
    Tạo một "fingerprint" duy nhất cho danh sách restaurant
    Dùng để detect khi danh sách thay đổi
    """
    if not restaurant_places:
        return None
    
    # Tạo tuple fingerprint:
    # enumerate để lấy cả index (i) và item (r)
    # r.get("place_id") nếu có → dùng làm fingerprint
    # nếu không có place_id, dùng r.get("name")
    # nếu cả hai đều không có, dùng fallback là "idx_{i}" để đảm bảo mỗi nhà hàng có giá trị duy nhất
    ids = tuple(
        r.get("place_id") or r.get("name") or f"idx_{i}"
        for i, r in enumerate(restaurant_places)
    )
    
    # Trả về tuple fingerprints
    return ids


def render_location_form_and_handle_submit(restaurant_places):
    # Tạo form để người dùng nhập vị trí hiện tại
    with st.form("location_form", clear_on_submit=False):
        # Ô nhập địa chỉ
        st.text_input(
            "📍 Your Location",
            key="current_location_input",
            placeholder="E.g., District 1, Ho Chi Minh City"
        )

        # Nút submit
        submit = st.form_submit_button(
            "🚗 Show Routes",
            use_container_width=True
        )

    # Khi user bấm submit
    if submit:
        # Gọi hàm xử lý logic tạo route
        handle_route_submit(
            st.session_state.current_location_input,
            restaurant_places
        )
        
        if st.session_state.route_error:
            st.error(st.session_state.route_error)


def handle_route_submit(location, restaurant_places):
    reset_route_state()
    
    # Trường hợp 1: chưa nhập location nhưng có nhà hàng
    if not location.strip():
        st.warning("⚠️ Please enter your location!")
        return 

    # Trường hợp 2: có location nhưng không có nhà hàng
    elif location.strip() and not restaurant_places:
        st.warning("⚠️ No restaurants to route to!")
        return
    
    # Hiển thị spinner khi đang tạo route
    else:
        with st.spinner("Creating routes..."):
            create_and_store_routes(location, restaurant_places)
    
    # Lưu location đã được strip vào session_state
    st.session_state.current_location = location.strip()


def create_and_store_routes(location, restaurant_places):
    # Gọi hàm tạo map + route info (Folium + OSRM)
    m, info = create_multi_destination_map(location, restaurant_places)

    # Nếu tạo route thành công và không có lỗi
    if m and info and not info.get("error"):
        # Lưu map vào session_state để render lại sau rerun
        st.session_state.multi_map = m

        # Lưu thông tin route (distance, time, address…)
        st.session_state.multi_info = info

        # Tắt map mặc định
        st.session_state.show_default_map = False
        
        # Tạo key mới cho map (tránh Streamlit cache map cũ)
        st.session_state.map_key = f"map_route_{uuid.uuid4()}"
        
        # Xoá lỗi (nếu có)
        st.session_state.route_error = None

    else:
        # Trường hợp tạo route thất bại
        st.session_state.route_error = (
            info.get("error", "Unknown error occurred while creating routes. Please check your location and try again.")
        )
        reset_route_state()


def reset_route_state():
    # Reset toàn bộ trạng thái liên quan tới route
    st.session_state.multi_map = None
    st.session_state.multi_info = {}
    st.session_state.show_default_map = True
    st.session_state.map_key = "map_default"


def render_map_view(restaurant_places):
    # Tiêu đề khu vực hiển thị bản đồ
    st.markdown("### 🗺️ Map View")

    # Ưu tiên hiển thị map có route
    if has_route_map():
        render_route_map()

    # Nếu chưa có route nhưng có nhà hàng → vẽ marker
    elif restaurant_places:
        render_restaurant_markers_map(restaurant_places)

    # Không có gì → map mặc định
    else:
        render_default_map()


def has_route_map():
    # Kiểm tra có map route hợp lệ hay không
    return (
        st.session_state.multi_map and
        not st.session_state.get("show_default_map", True)
    )


def render_route_map():
    # Hiển thị bản đồ có tuyến đường
    st_folium(
        st.session_state.multi_map,
        height=500,
        width=360,
        key=st.session_state.map_key,   
        returned_objects=[]  # Không trigger rerun
    )


def render_restaurant_markers_map(restaurant_places):
    # Tạo map mặc định tại TP.HCM
    m = folium.Map(location=[10.776, 106.7], zoom_start=16)

    bounds = []
    # Vẽ marker cho từng nhà hàng
    for r in restaurant_places:
        if r.get("lat") and r.get("lng"):
            folium.Marker(
                [r["lat"], r["lng"]],
                popup=r.get("name", "Restaurant"),
                icon=folium.Icon(
                    color="blue",
                    icon="utensils",
                    prefix="fa"
                )
            ).add_to(m)
            bounds.append([r["lat"], r["lng"]])
            
    # Điều chỉnh vùng hiển thị để bao phủ tất cả marker
    if bounds:
        m.fit_bounds(bounds)
        
    # Render map
    st_folium(m, height=500, width=360, key="map_restaurants")


def render_default_map():
    # Map rỗng mặc định
    m = folium.Map(location=[10.776, 106.7], zoom_start=16)
    st_folium(m, height=500, width=360, key="map_default")


def render_route_details():
    # Nếu chưa có route thì không render chi tiết
    if not has_route_map():
        return

    # Separator
    st.markdown("---")
    st.markdown("### 🎯 Route Details")

    # Icon dùng để đánh số route
    icons = "🔵🔴🟣🟠🟤"

    # Render chi tiết từng route
    for idx, (name, info) in enumerate(
        st.session_state.multi_info.items(), 1
    ):
        render_single_route_detail(idx, name, info, icons)


def render_single_route_detail(idx, name, info, icons):
    # Nếu route này bị lỗi
    if "error" in info:
        st.error(f"❌ {name}: {info['error']}")
        return

    # Tạo expander cho từng route
    with st.expander(
        # Tiêu đề expander: icon + số thứ tự + tên + khoảng cách
        f"{icons[(idx - 1) % len(icons)]} "
        f"{idx}. {name} - {info['distance_km']:.1f} km",
        icon="📍",
        expanded=(idx <= 2)  # Mở sẵn 2 route đầu
    ):
        # Chia layout thành 2 cột
        col1, col2 = st.columns(2)

        # Hiển thị khoảng cách
        col1.metric(
            "📏 Distance",
            f"{info['distance_km']:.2f} km"
        )

        # Hiển thị thời gian (giờ → phút)
        col2.metric(
            "⏱️ Time",
            f"{info['duration_hrs']*60:.0f} min"
        )

        # Hiển thị địa chỉ nhà hàng
        st.caption(f"📍 {info.get('address', 'N/A')}")