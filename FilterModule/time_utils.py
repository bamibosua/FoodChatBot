# time_utils.py
import re
from datetime import datetime, timedelta

def parse_hhmm(s: str):
    s = s.strip().replace(" ", "")
    if s == "24:00":
        return datetime.strptime("00:00", "%H:%M").time(), True
    try:
        return datetime.strptime(s, "%H:%M").time(), False
    except ValueError:
        return datetime.strptime("00:00", "%H:%M").time(), False

def is_open(time_range: str, current_time: str, min_open_minutes: int = 30):
    try:
        if not isinstance(time_range, str) or not time_range.strip():
            return True, 9999

        now_time = datetime.strptime(current_time.strip(), "%H:%M").time()
        today = datetime.today()
        now_dt = datetime.combine(today, now_time)

        periods = [p.strip() for p in time_range.split(",") if p.strip()]
        minutes_left_list = []

        for period in periods:
            if '-' not in period: continue
            parts = re.split(r'\s*[-–—]\s*', period)
            if len(parts) != 2: continue

            open_time, open_is_24 = parse_hhmm(parts[0])
            close_time, close_is_24 = parse_hhmm(parts[1])

            if open_is_24: open_time = datetime.strptime("00:00", "%H:%M").time()
            if close_is_24: close_time = datetime.strptime("00:00", "%H:%M").time()

            open_dt = datetime.combine(today, open_time)
            close_dt = datetime.combine(today, close_time)

            if close_dt <= open_dt:
                close_dt += timedelta(days=1)

            for day_offset in [-1, 0, 1]:
                check_open = open_dt + timedelta(days=day_offset)
                check_close = close_dt + timedelta(days=day_offset)
                
                if check_open <= now_dt <= check_close:
                    minutes_left = (check_close - now_dt).total_seconds() / 60
                    if minutes_left >= min_open_minutes:
                        return True, minutes_left
                    else:
                        minutes_left_list.append(minutes_left)

        return (False, max(minutes_left_list)) if minutes_left_list else (False, 0)
            
    except Exception:
        return True, 9999
