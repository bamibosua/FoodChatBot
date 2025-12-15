import unittest
import json
import sys
from io import StringIO
from unittest.mock import patch, MagicMock
from datetime import datetime, time, date, timedelta

# --- IMPORT MODULES TỪ PACKAGE FILTERMODULE ---
from FilterModule.price_utils import parse_price
from FilterModule.time_utils import (
    get_vietnamese_day, parse_time, is_time_in_range, 
    is_restaurant_open, filter_open_restaurants
)
from FilterModule.data_utils import geocode_osm_fallback, geocode_location, fetch_places_google_maps
from FilterModule.filter_utils import (
    ai_check_food_relevance_batch, prefilter, postfilter, filter_and_split_restaurants
)
from FilterModule.restaurant_service import find_best_restaurants
from FilterModule.app_runner import run_app

class TestSuite100Cases(unittest.TestCase):

    # =========================================================================
    # PHẦN 1: PRICE UTILS (20 Cases)
    # =========================================================================
    def test_001_price_simple_k(self): self.assertEqual(parse_price("50k"), 50000)
    def test_002_price_simple_K(self): self.assertEqual(parse_price("100K"), 100000)
    def test_003_price_full_numeric(self): self.assertEqual(parse_price("50000"), 50000)
    def test_004_price_with_dot(self): self.assertEqual(parse_price("50.000"), 50000)
    def test_005_price_with_comma(self): self.assertEqual(parse_price("50,000"), 50000)
    def test_006_price_range_hyphen(self): self.assertEqual(parse_price("20k-50k"), 50000)
    def test_007_price_range_text_to(self): self.assertEqual(parse_price("20k đến 50k"), 50000)
    def test_008_price_correction_under_1000(self): self.assertEqual(parse_price("50"), 50000)
    def test_009_price_correction_boundary_999(self): self.assertEqual(parse_price("999"), 999000)
    def test_010_price_no_correction_1000(self): self.assertEqual(parse_price("1000"), 1000)
    def test_011_price_dirty_text_prefix(self): self.assertEqual(parse_price("Giá khoảng 30k"), 30000)
    def test_012_price_dirty_text_suffix(self): self.assertEqual(parse_price("35k/người"), 35000)
    def test_013_price_mixed_units(self): self.assertEqual(parse_price("50 - 100k"), 100000)
    def test_014_price_mixed_units_reverse(self): self.assertEqual(parse_price("100k - 50"), 100000)
    def test_015_price_float_style(self): self.assertEqual(parse_price("2.5k"), 2500)
    def test_016_price_none(self): self.assertIsNone(parse_price(None))
    def test_017_price_empty_string(self): self.assertIsNone(parse_price(""))
    def test_018_price_whitespace(self): self.assertIsNone(parse_price("   "))
    def test_019_price_text_only(self): self.assertIsNone(parse_price("Miễn phí"))
    def test_020_price_special_chars(self): self.assertIsNone(parse_price("!@#$%"))

    # =========================================================================
    # PHẦN 2: TIME UTILS - BASIC (20 Cases)
    # =========================================================================
    def test_021_day_mon(self): self.assertEqual(get_vietnamese_day(date(2025,12,8)), "thứ hai")
    def test_022_day_tue(self): self.assertEqual(get_vietnamese_day(date(2025,12,9)), "thứ ba")
    def test_023_day_wed(self): self.assertEqual(get_vietnamese_day(date(2025,12,10)), "thứ tư")
    def test_024_day_thu(self): self.assertEqual(get_vietnamese_day(date(2025,12,11)), "thứ năm")
    def test_025_day_fri(self): self.assertEqual(get_vietnamese_day(date(2025,12,12)), "thứ sáu")
    def test_026_day_sat(self): self.assertEqual(get_vietnamese_day(date(2025,12,13)), "thứ bảy")
    def test_027_day_sun(self): self.assertEqual(get_vietnamese_day(date(2025,12,14)), "chủ nhật")
    
    def test_028_parse_time_std(self): self.assertEqual(parse_time("14:30"), time(14,30))
    def test_029_parse_time_start(self): self.assertEqual(parse_time("00:00"), time(0,0))
    def test_030_parse_time_end(self): self.assertEqual(parse_time("23:59"), time(23,59))
    def test_031_parse_time_fail_hour(self): self.assertIsNone(parse_time("25:00"))
    def test_032_parse_time_fail_min(self): self.assertIsNone(parse_time("10:61"))
    def test_033_parse_time_fail_format(self): self.assertIsNone(parse_time("10h30"))
    
    def test_034_range_mid(self): self.assertTrue(is_time_in_range(time(10,0), time(8,0), time(12,0)))
    def test_035_range_bound_start(self): self.assertTrue(is_time_in_range(time(8,0), time(8,0), time(12,0)))
    def test_036_range_bound_end(self): self.assertTrue(is_time_in_range(time(12,0), time(8,0), time(12,0)))
    def test_037_range_out_before(self): self.assertFalse(is_time_in_range(time(7,59), time(8,0), time(12,0)))
    def test_038_range_out_after(self): self.assertFalse(is_time_in_range(time(12,1), time(8,0), time(12,0)))
    
    def test_039_range_overnight_in_pm(self): self.assertTrue(is_time_in_range(time(23,0), time(22,0), time(2,0)))
    def test_040_range_overnight_in_am(self): self.assertTrue(is_time_in_range(time(1,0), time(22,0), time(2,0)))

    # =========================================================================
    # PHẦN 3: TIME UTILS - LOGIC MỞ CỬA & BỎ QUA 30 PHÚT (16 Cases)
    # =========================================================================
    
    def test_041_status_no_data(self):
        """Không có operating_hours -> Mặc định True"""
        self.assertTrue(is_restaurant_open({}, time(10,0), "thứ hai")[0])

    def test_042_status_explicit_closed(self):
        """Ghi rõ 'Đóng cửa'"""
        r = {'operating_hours': {'thứ hai': 'Đóng cửa'}}
        self.assertFalse(is_restaurant_open(r, time(10,0), "thứ hai")[0])

    def test_043_status_wrong_day(self):
        """Không có dữ liệu ngày thứ ba"""
        r = {'operating_hours': {'thứ hai': '08:00-22:00'}}
        self.assertFalse(is_restaurant_open(r, time(10,0), "thứ ba")[0])

    def test_044_status_24h(self):
        r = {'operating_hours': {'thứ hai': '00:00–00:00'}}
        self.assertTrue(is_restaurant_open(r, time(3,0), "thứ hai")[0])

    def test_045_status_normal_open(self):
        r = {'operating_hours': {'thứ hai': '08:00–22:00'}}
        self.assertTrue(is_restaurant_open(r, time(10,0), "thứ hai")[0])

    # test_046: Còn 31p -> MỞ (Logic mới vẫn MỞ)
    def test_046_closing_31_mins(self):
        """Còn 31p -> MỞ"""
        r = {'operating_hours': {'thứ hai': '08:00–10:31'}}
        is_open, mins = is_restaurant_open(r, time(10,0), "thứ hai")
        self.assertTrue(is_open)
        self.assertEqual(mins, 31)

    # test_047, test_048, test_049, test_051 ĐÃ ĐƯỢC LOẠI BỎ THEO YÊU CẦU

    def test_050_closing_overnight_safe(self):
        """Qua đêm, còn nhiều giờ -> MỞ"""
        r = {'operating_hours': {'thứ hai': '22:00–02:00'}}
        is_open, _ = is_restaurant_open(r, time(23,0), "thứ hai")
        self.assertTrue(is_open)

    def test_052_multi_shift_morning(self):
        r = {'operating_hours': {'thứ hai': '10:00-14:00, 17:00-22:00'}}
        self.assertTrue(is_restaurant_open(r, time(11,0), "thứ hai")[0])

    def test_053_multi_shift_break(self):
        r = {'operating_hours': {'thứ hai': '10:00-14:00, 17:00-22:00'}}
        self.assertFalse(is_restaurant_open(r, time(15,0), "thứ hai")[0])

    def test_054_multi_shift_evening(self):
        r = {'operating_hours': {'thứ hai': '10:00-14:00, 17:00-22:00'}}
        self.assertTrue(is_restaurant_open(r, time(18,0), "thứ hai")[0])

    def test_055_filter_func_labeling(self):
        """Test hàm filter_open_restaurants gắn nhãn đúng"""
        data = [{'operating_hours': {'thứ hai': '00:00-23:59'}}]
        res = filter_open_restaurants(data, "10:00", "thứ hai")
        self.assertTrue(res[0]['is_currently_open'])

    def test_056_filter_func_bad_time(self):
        """Input giờ sai -> Dùng giờ hiện tại (không crash)"""
        data = [{'operating_hours': {'thứ hai': '00:00-23:59'}}]
        filter_open_restaurants(data, "sai_gio", "thứ hai") # Should not raise error

    def test_057_data_closed_string(self):
        """String 'Closed' trong data"""
        r = {'operating_hours': {'thứ hai': 'Closed'}}
        self.assertFalse(is_restaurant_open(r, time(12,0), "thứ hai")[0])
    
    def test_058_data_digit_check(self):
        """Chuỗi rác không có số -> False"""
        r = {'operating_hours': {'thứ hai': 'Nghỉ lễ'}}
        self.assertFalse(is_restaurant_open(r, time(12,0), "thứ hai")[0])

    def test_059_format_en_dash(self):
        """Test dấu gạch ngang khác nhau (– vs -)"""
        r = {'operating_hours': {'thứ hai': '08:00-22:00'}} # Hyphen
        self.assertTrue(is_restaurant_open(r, time(10,0), "thứ hai")[0])
        
    def test_060_format_em_dash(self):
        r = {'operating_hours': {'thứ hai': '08:00–22:00'}} # En dash
        self.assertTrue(is_restaurant_open(r, time(10,0), "thứ hai")[0])


    # =========================================================================
    # PHẦN 4: FILTER UTILS - LOCATION & BUDGET (25 Cases)
    # =========================================================================
    
    def test_061_loc_numeric_q1(self):
        data = [{'address': 'Q.1'}]
        self.assertEqual(len(prefilter(data, location="Q.1")), 1)

    def test_062_loc_numeric_quan1(self):
        data = [{'address': 'Quận 1'}]
        self.assertEqual(len(prefilter(data, location="Quận 1")), 1)

    def test_063_loc_numeric_district1(self):
        data = [{'address': 'District 1'}]
        self.assertEqual(len(prefilter(data, location="Quận 1")), 1)

    def test_064_loc_numeric_trap_12(self):
        """Quận 1 != Quận 12"""
        data = [{'address': 'Quận 12'}]
        self.assertEqual(len(prefilter(data, location="Quận 1")), 0)

    def test_065_loc_numeric_trap_phuong1(self):
        """Quận 1 != Phường 1"""
        data = [{'address': 'Phường 1, Quận 5'}]
        self.assertEqual(len(prefilter(data, location="Quận 1")), 0)

    def test_066_loc_numeric_trap_p1(self):
        """Quận 1 != P.1"""
        data = [{'address': 'P.1, Q.3'}]
        self.assertEqual(len(prefilter(data, location="Quận 1")), 0)

    def test_067_loc_numeric_case_insensitive(self):
        data = [{'address': 'quận 1'}]
        self.assertEqual(len(prefilter(data, location="QUẬN 1")), 1)

    def test_068_loc_numeric_space(self):
        data = [{'address': 'Quận 1'}]
        self.assertEqual(len(prefilter(data, location="Quận   1")), 1)

    def test_069_loc_numeric_01(self):
        """Quận 1 == Quận 01"""
        data = [{'address': 'Quận 01'}]
        self.assertEqual(len(prefilter(data, location="Quận 1")), 1)

    def test_070_loc_numeric_no_match(self):
        data = [{'address': 'Quận 3'}]
        self.assertEqual(len(prefilter(data, location="Quận 1")), 0)

    def test_071_loc_keyword_basic(self):
        data = [{'address': 'Phạm Ngũ Lão'}]
        self.assertEqual(len(prefilter(data, location="Phạm Ngũ Lão")), 1)

    def test_072_loc_keyword_partial(self):
        data = [{'address': 'Đường Phạm Ngũ Lão, Q1'}]
        self.assertEqual(len(prefilter(data, location="Phạm Ngũ Lão")), 1)

    def test_073_loc_keyword_fail(self):
        data = [{'address': 'Nguyễn Trãi'}]
        self.assertEqual(len(prefilter(data, location="Lê Lợi")), 0)

    def test_074_loc_keyword_multi_and(self):
        """AND Logic: Phải có cả 2"""
        data = [{'address': 'A, B'}]
        self.assertEqual(len(prefilter(data, location="A, B")), 1)

    def test_075_loc_keyword_multi_and_fail(self):
        data = [{'address': 'A, C'}]
        self.assertEqual(len(prefilter(data, location="A, B")), 0)

    def test_076_budget_exact(self):
        data = [{'price': '50k'}]
        self.assertEqual(len(postfilter(data, budget="50k")), 1)

    def test_077_budget_under(self):
        data = [{'price': '30k'}]
        self.assertEqual(len(postfilter(data, budget="50k")), 1)

    def test_078_budget_over(self):
        data = [{'price': '60k'}]
        self.assertEqual(len(postfilter(data, budget="50k")), 0)

    def test_079_budget_none_input(self):
        data = [{'price': '100k'}]
        # Không có budget -> Lấy hết
        self.assertEqual(len(postfilter(data, budget=None)), 1)

    def test_080_budget_empty_data(self):
        self.assertEqual(len(postfilter([], budget="50k")), 0)

    def test_081_budget_default_price(self):
        """Quán không giá -> Default 50k -> Pass budget 60k"""
        data = [{'price': ''}]
        self.assertEqual(len(postfilter(data, budget="60k")), 1)

    def test_082_budget_default_price_fail(self):
        """Quán không giá -> Default 50k -> Fail budget 40k"""
        data = [{'price': ''}]
        self.assertEqual(len(postfilter(data, budget="40k")), 0)

    def test_083_budget_range_pass(self):
        data = [{'price': '20k-40k'}] # Max 40k
        self.assertEqual(len(postfilter(data, budget="50k")), 1)

    def test_084_budget_range_fail(self):
        data = [{'price': '20k-60k'}] # Max 60k
        self.assertEqual(len(postfilter(data, budget="50k")), 0)
    
    def test_085_filter_integration_steps(self):
        """Test chạy qua cả Location và Time"""
        data = [{'address': 'Q1', 'operating_hours': {'thứ hai': '08:00-22:00'}}]
        # Giả lập 10h sáng thứ 2
        res = prefilter(data, location="Q1", current_day="thứ hai", current_time="10:00")
        self.assertEqual(len(res), 1)

    # =========================================================================
    # PHẦN 5: SERVICE, MOCK & APP RUNNER (17 Cases)
    # =========================================================================
    
    @patch('FilterModule.filter_utils.genai')
    def test_086_ai_mock_success(self, mock_genai):
        mock_model = mock_genai.GenerativeModel.return_value
        mock_model.generate_content.return_value.text = '{"ids": [0]}'
        data = [{'title': 'A', 'id':0}, {'title': 'B', 'id':1}]
        
        # ĐÃ BỎ tham số api_key
        res = ai_check_food_relevance_batch(data, "food") 
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['title'], 'A')

    @patch('FilterModule.filter_utils.genai')
    def test_087_ai_mock_exception(self, mock_genai):
        """AI lỗi -> Trả về nguyên gốc"""
        mock_genai.configure.side_effect = Exception("Boom")
        data = [{'title': 'A'}]
        
        # ĐÃ BỎ tham số api_key
        res = ai_check_food_relevance_batch(data, "food")
        self.assertEqual(len(res), 1)

    @patch('FilterModule.data_utils.requests.get')
    def test_088_osm_fallback_success(self, mock_get):
        mock_get.return_value.json.return_value = [{'lat': '1.0', 'lon': '1.0'}]
        lat, lng = geocode_osm_fallback("Place")
        self.assertEqual(lat, 1.0)

    @patch('FilterModule.data_utils.requests.get')
    def test_089_osm_fallback_empty(self, mock_get):
        mock_get.return_value.json.return_value = []
        lat, lng = geocode_osm_fallback("Place")
        self.assertIsNone(lat)

    @patch('FilterModule.data_utils.requests.get')
    def test_090_osm_fallback_error(self, mock_get):
        mock_get.side_effect = Exception("Net Error")
        lat, lng = geocode_osm_fallback("Place")
        self.assertIsNone(lat)

    @patch('FilterModule.data_utils.GoogleSearch')
    def test_091_geocode_serp_success(self, mock_search):
        mock_search.return_value.get_dict.return_value = {
            "place_results": {"gps_coordinates": {"latitude": 10, "longitude": 10}}
        }
        lat, lng = geocode_location("Loc", "key")
        self.assertEqual(lat, 10)

    @patch('FilterModule.data_utils.GoogleSearch')
    @patch('FilterModule.data_utils.geocode_osm_fallback', return_value=(5,5))
    def test_092_geocode_serp_fail_fallback(self, mock_osm, mock_search):
        mock_search.return_value.get_dict.return_value = {"error": "Fail"}
        lat, lng = geocode_location("Loc", "key")
        self.assertEqual(lat, 5)

    @patch('FilterModule.data_utils.GoogleSearch')
    def test_093_fetch_places_retry_logic(self, mock_search):
        """Zoom 15 fail -> Zoom 13 success"""
        mock_search.return_value.get_dict.side_effect = [
            {"local_results": []},
            {"local_results": [{"title": "Found"}]}
        ]
        res = fetch_places_google_maps("q", 0, 0, "k")
        self.assertEqual(len(res), 1)

    @patch('FilterModule.data_utils.GoogleSearch')
    def test_094_fetch_places_all_fail(self, mock_search):
        mock_search.return_value.get_dict.return_value = {"local_results": []}
        res = fetch_places_google_maps("q", 0, 0, "k")
        self.assertEqual(len(res), 0)

    @patch('FilterModule.restaurant_service.geocode_location', return_value=(10,10))
    @patch('FilterModule.restaurant_service.fetch_places_google_maps', return_value=[{'title': 'A'}])
    @patch('FilterModule.restaurant_service.filter_and_split_restaurants', return_value=[])
    def test_095_find_best_empty_after_filter(self, *args):
        """Tìm thấy quán nhưng lọc xong rỗng"""
        res = find_best_restaurants({}, use_cache=False)
        self.assertEqual(res, [])

    @patch('FilterModule.restaurant_service.geocode_location', side_effect=Exception("Geo Fail"))
    def test_096_find_best_geo_fail(self, *args):
        res = find_best_restaurants({}, use_cache=False)
        self.assertEqual(res, [])

    @patch('FilterModule.restaurant_service.geocode_location', return_value=(10,10))
    @patch('FilterModule.restaurant_service.fetch_places_google_maps', return_value=[{'title':'A'}])
    @patch('FilterModule.restaurant_service.filter_and_split_restaurants')
    def test_097_sorting_check(self, mock_filter, *args):
        # Mở > Rating > Review
        mock_filter.return_value = [
            {'title': 'ClosedHigh', 'is_currently_open': False, 'rating': 5},
            {'title': 'OpenLow', 'is_currently_open': True, 'rating': 3}
        ]
        res = find_best_restaurants({}, use_cache=False)
        self.assertEqual(res[0]['name'], 'OpenLow') # Mở cửa ưu tiên
        self.assertEqual(res[1]['name'], 'ClosedHigh')

    @patch('FilterModule.app_runner.find_best_restaurants', return_value=[])
    def test_098_app_runner_empty(self, mock_find):
        captured = StringIO()
        sys.stdout = captured
        run_app({})
        sys.stdout = sys.__stdout__
        self.assertIn("Không tìm thấy", captured.getvalue())

    @patch('FilterModule.app_runner.find_best_restaurants')
    def test_099_app_runner_display(self, mock_find):
        mock_find.return_value = [{
            'name': 'TestQuan', 'rating': 5, 'reviews': 100,
            'price': 50000, 'address': 'TestAddr', 'is_open': True,
            'minutes_left': 60, 'opening_schedule': {'thứ hai': '08:00-22:00'}
        }]
        captured = StringIO()
        sys.stdout = captured
        run_app({})
        sys.stdout = sys.__stdout__
        self.assertIn("TestQuan", captured.getvalue())
        self.assertIn("Lịch mở cửa", captured.getvalue())

    def test_100_price_range_text_garbage(self):
        """Case thứ 100: Text rác trong khoảng giá"""
        self.assertEqual(parse_price("giá 20k - 50k nhé"), 50000)

    def test_101_filter_integration_full_flow(self):
        """Case 101: Test flow kết hợp"""
        data = [{'address': 'Quận 1', 'price': '30k', 'operating_hours': {'thứ hai': '00:00-23:59'}}]
        # Location Q1, Budget 50k, Time OK
        res = filter_and_split_restaurants(data, location="Quận 1", budget="50k", current_day="thứ hai", current_time="10:00")
        self.assertEqual(len(res), 1)

    def test_102_filter_integration_fail_location(self):
        """Case 102: Fail do location"""
        data = [{'address': 'Quận 3', 'price': '30k', 'operating_hours': {'thứ hai': '00:00-23:59'}}]
        res = filter_and_split_restaurants(data, location="Quận 1", budget="50k")
        self.assertEqual(len(res), 0)

if __name__ == '__main__':
    unittest.main()