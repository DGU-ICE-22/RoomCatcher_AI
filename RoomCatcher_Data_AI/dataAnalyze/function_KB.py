import requests
import os 
import json
from django.core.exceptions import ImproperlyConfigured
from product_crawling_v2 import product_crawling_v2
from transpose_location_to_address_dabang import get_address_from_coordinates
from extract_tag_from_product import extract_keywords
import sqlite3
from datetime import datetime

def get_secret(setting, secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

def connect_db():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    secret_file = os.path.join(base_dir, '..', '..', 'secret.json')

    with open(secret_file) as f:
        secrets = json.loads(f.read())
        
    room_data = product_crawling_v2(secrets)

    return room_data

def create_address(item):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    secret_file = os.path.join(base_dir, '..', '..', 'secret.json')

    with open(secret_file) as f:
        secrets = json.loads(f.read())
    API_KEY = get_secret('API_KEY', secrets)
    x,y = item.get('wgs84위도', None), item.get('wgs84경도', None)
    if x is None or y is None:
        return ValueError("No location information found.")
    address = get_address_from_coordinates(y, x, API_KEY)
    return address

def process_and_save_data(room_data):
    conn = sqlite3.connect('room_lists.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dataAnalyze_ProductKB (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            floor_type TEXT,
            total_area REAL,
            num_bathrooms INTEGER,
            rent_ratio REAL,
            house_type TEXT,
            min_rent_price INTEGER,
            listing_source TEXT,
            sale_price INTEGER,
            latitude REAL,
            building_area REAL,
            false_listing_result TEXT,
            building_usage_code TEXT,
            complex_name TEXT,
            rent_deposit INTEGER,
            num_rooms INTEGER,
            usage_month TEXT,
            exclusive_area REAL,
            agent_address TEXT,
            registration_date TEXT,
            listing_status TEXT,
            years_used REAL,
            building_coverage_ratio TEXT,
            listing_serial_number INTEGER,
            ad_description TEXT,
            num_images INTEGER,
            net_supply_area REAL,
            listing_type TEXT,
            net_exclusive_area REAL,
            source_name TEXT,
            max_rent_price INTEGER,
            transaction_type TEXT,
            floor_area_ratio TEXT,
            mortgage TEXT,
            agent_name TEXT,
            max_loan_amount REAL,
            total_floors INTEGER,
            listing_name TEXT,
            complex_serial_number INTEGER,
            supply_area REAL,
            move_in_date TEXT,
            sale_price_comparison INTEGER,
            floor_number TEXT,
            longitude REAL,
            usage_year TEXT,
            cluster_id TEXT,
            district_address TEXT,
            price_per_pyeong INTEGER,
            orientation TEXT,
            has_elevator INTEGER,
            listing_type_code TEXT,
            category TEXT,
            group_type TEXT,
            detailed_address TEXT,
            building_name TEXT,
            land_area REAL,
            transaction_type_code TEXT,
            image_url TEXT,
            door_structure TEXT,
            product_address TEXT
        )
    ''')
    try:
        for items in room_data:
            items = items["dataBody"]["data"]["propertyList"]
            for item in items:
                image_url = f"{item.get('이미지도메인URL', '')}{item.get('이미지디렉토리경로내용', '')}{item.get('이미지파일명', '')}"
                address = create_address(item)
                registration_date = str(datetime.strptime(item.get('등록년월일', ''), '%Y.%m.%d').date() if item.get('등록년월일') else None)
                cursor.execute('''
                    INSERT INTO dataAnalyze_ProductKB (
                        floor_type, total_area, num_bathrooms, rent_ratio, house_type,
                        min_rent_price, listing_source, sale_price, latitude, building_area,
                        false_listing_result, building_usage_code, complex_name, rent_deposit,
                        num_rooms, usage_month, exclusive_area, agent_address, registration_date,
                        listing_status, years_used, building_coverage_ratio, listing_serial_number,
                        ad_description, num_images, net_supply_area, listing_type, net_exclusive_area,
                        source_name, max_rent_price, transaction_type, floor_area_ratio, mortgage,
                        agent_name, max_loan_amount, total_floors, listing_name, complex_serial_number,
                        supply_area, move_in_date, sale_price_comparison, floor_number, longitude,
                        usage_year, cluster_id, district_address, price_per_pyeong, orientation,
                        has_elevator, listing_type_code, category, group_type, detailed_address,
                        building_name, land_area, transaction_type_code, image_url, door_structure, product_address
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('해당층구분', ''), item.get('연면적', None), item.get('욕실수', None), item.get('전세가율', None),
                    item.get('주택형타입내용', ''), item.get('최소월세가', None), item.get('매물유입구분', ''), item.get('매매일반거래가', None),
                    item.get('wgs84위도', None), item.get('건축면적', None), item.get('허위매물처리결과구분명', ''), item.get('건축물용도코드명', ''),
                    item.get('단지명', ''), item.get('월세보증금', None), item.get('방수', None), item.get('사용월', ''), item.get('전용면적', None),
                    item.get('중개업소주소', ''), registration_date, item.get('매물상태구분', ''), item.get('사용년차', None), item.get('건폐율내용', ''),
                    item.get('매물일련번호', None), item.get('특징광고내용', ''), item.get('매물이미지개수', None), item.get('순공급면적', None),
                    item.get('매물종별구분명', ''), item.get('순전용면적', None), item.get('매물유입구분명', ''), item.get('최대전세가', None),
                    item.get('매물거래구분명', ''), item.get('용적률내용', ''), item.get('융자금', ''), item.get('중개업소명', ''), item.get('최대대출가능금액', None),
                    item.get('총층수', None), item.get('매물명', ''), item.get('단지기본일련번호', None), item.get('공급면적', None), item.get('입주가능일내용', ''),
                    item.get('실거래가대비', None), item.get('해당층수', ''), item.get('wgs84경도', None), item.get('사용년', ''), item.get('클러스터식별자', ''),
                    item.get('시군구주소', ''), item.get('평당단가', None), item.get('방향구분명', ''), item.get('승강기유무', 0), item.get('매물종별구분', ''),
                    item.get('카테고리2', ''), item.get('매물종별그룹구분명', ''), item.get('상세번지내용', ''), item.get('건물명', ''), item.get('대지면적', None),
                    item.get('매물거래구분', ''), image_url, item.get('현관구조내용', ''), address
                ))

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Transaction failed: {e}")
    finally:
        conn.close()

def add_tag_to_KB():
    conn = sqlite3.connect('room_lists.db')
    cursor = conn.cursor()
    
     # 1. `dataAnalyze_productKB` 테이블에서 `ad_description` 항목과 `id` 값을 가져오기
    cursor.execute('SELECT id, ad_description FROM dataAnalyze_ProductKB')
    product_ads = cursor.fetchall()
    
    try:
        for product_id, ad_description in product_ads:
            if not ad_description:
                continue
            # 2. `extract_keywords` 함수를 사용하여 `ad_description`에서 키워드 추출
            tags = extract_keywords(ad_description)
            # 3. 'dataAnalyze_tag 테이블에 태그 추가 
            tag_ids = []
            for tag in tags:
                # 중복된 tag가 있는지 확인
                cursor.execute('SELECT id FROM dataAnalyze_tag WHERE tagName = ?', (tag,))
                result = cursor.fetchone()
                
                if result:
                    # 중복된 tag가 있으면 해당 tag_id를 가져옴
                    tag_id = result[0]
                else:
                    # 중복된 tag가 없으면 새로운 tag를 삽입하고 tag_id를 가져옴
                    cursor.execute('INSERT INTO dataAnalyze_tag (tagName) VALUES (?)', (tag,))
                    tag_id = cursor.lastrowid
                
                tag_ids.append(tag_id)
            
            # 4. `dataAnalyze_productTag` 테이블에 `id` 및 `tag` 추가
            for tag_id in tag_ids:
                cursor.execute('INSERT INTO dataAnalyze_productTag (productId_id, tagId_id) VALUES (?, ?)', (product_id, tag_id))
            
        conn.commit()
    
    except Exception as e:
        conn.rollback()
        print(f"Transaction failed`: {e}")
    finally:
        conn.close()
    
def main():
    room_data = connect_db()
    process_and_save_data(room_data)
    add_tag_to_KB()
if __name__ == "__main__":
    # main()
    # room_data = connect_db()
    # print(create_address(room_data[0]["dataBody"]["data"]["propertyList"][0]))
    add_tag_to_KB()