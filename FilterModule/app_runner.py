# FilterModule/app_runner.py
from .restaurant_service import find_best_restaurants

def run_app(user_intent):
    """
    Chạy service tìm kiếm và in kết quả ra console (Kèm khoảng cách).
    """
    print(f"🔹 [App Runner] Nhận Intent: {user_intent}")

    # Chạy tìm kiếm
    results = find_best_restaurants(user_intent, use_cache=False)

    print(f"\n🔹 KẾT QUẢ TÌM KIẾM ({len(results)} quán):")
    if not results:
        print("   ❌ Không tìm thấy.")
    else:
        # In tối đa 10 quán
        for i, r in enumerate(results[:len(results)], 1):
            name = r.get('name', 'No Name')
            rating = r.get('rating', 0)
            reviews = r.get('reviews', 0)
            price = r.get('price', 'N/A')
            addr = r.get('address', 'No Address')
            
            # --- [NEW] Lấy khoảng cách từ dictionary ---
            dist = r.get('distance', 0) 
            
            is_open = r.get('is_open', False)
            mins = r.get('minutes_left', 0)
            
            # Hiển thị trạng thái mở cửa
            status = f"Đang mở (còn {mins}p)" if is_open and mins > 0 else "Đang mở (24h+)" if is_open else "Đóng cửa"
            
            schedule = r.get('opening_schedule', {})
            
            # --- IN THÔNG TIN ---
            print(f"[{i}] {name}")
            # --- [NEW] In dòng khoảng cách ---
            print(f"    📏 Khoảng cách: {dist} km (từ tâm tìm kiếm)")
            
            print(f"    ⭐ Rating: {rating} ({reviews} đánh giá)")
            print(f"    💰 Giá: {price} VNĐ")
            print(f"    ⏰ Trạng thái: {status}")
            print(f"    📍 Đ/c: {addr}")
            
            # --- IN LỊCH MỞ CỬA ---
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