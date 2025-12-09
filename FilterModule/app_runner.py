# new_version_module2/app_runner.py
from .restaurant_service import find_best_restaurants

def run_app(user_intent):
    """
    Chạy service tìm kiếm và TRẢ VỀ kết quả.
    """
    print(f"🔹 [App Runner] Nhận Intent: {user_intent}")

    results = find_best_restaurants(user_intent, use_cache=False)

    print(f"\n🔹 KẾT QUẢ TÌM KIẾM ({len(results)} quán):")
    if not results:
        print("   ❌ Không tìm thấy.")
    else:
        for i, r in enumerate(results[:5], 1):
            name = r.get('name', 'No Name')
            rating = r.get('rating', 0)
            reviews = r.get('reviews', 0)
            price = r.get('price', 'N/A')
            addr = r.get('address', 'No Address')
            is_open = r.get('is_open', False)
            mins = r.get('minutes_left', 0)
            status = f"Đang mở (còn {mins}p)" if is_open else "Đóng cửa"
            
            # Lấy lịch mở cửa
            schedule = r.get('opening_schedule', {})
            
            # ===============================================
            # [FIX] CHÈN LẠI CÁC DÒNG IN THÔNG TIN CƠ BẢN
            # ===============================================
            print(f"[{i}] {name}")
            print(f"    ⭐ Rating: {rating} ({reviews} đánh giá)")
            print(f"    💰 Giá: {price} VNĐ")
            print(f"    ⏰ Trạng thái: {status}")
            print(f"    📍 Đ/c: {addr}")
            
            # In Lịch mở cửa (Phần này giữ nguyên)
            print(f"    🗓️ Lịch mở cửa:")
            if schedule:
                day_order = ["thứ hai", "thứ ba", "thứ tư", "thứ năm", "thứ sáu", "thứ bảy", "chủ nhật"]
                
                sorted_schedule = sorted(
                    schedule.items(), 
                    key=lambda item: day_order.index(item[0]) if item[0] in day_order else 999
                )

                for day, time_range in sorted_schedule:
                    print(f"       - {day.capitalize()}: {time_range}")
            else:
                print(f"       - (Không có thông tin lịch mở cửa)")
            print("-" * 40)

    return results