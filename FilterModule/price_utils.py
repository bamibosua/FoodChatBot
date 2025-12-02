# price_utils.py
import re

def parse_price(raw):
    if not raw:
        return None

    s = str(raw).lower().strip()

    if 'k' in s:
        first_part = s.split('k')[0]
        clean_num = re.sub(r'[^\d.,]', '', first_part).replace(',', '.')
        
        try:
            return int(float(clean_num) * 1000)
        except ValueError:
            return None

    s = s.replace("đ", "").replace("vnd", "")
    s = s.replace(".", "").replace(",", "") 
    
    nums = re.findall(r'\d+', s)
    if not nums:
        return None

    return int(nums[0])
