import traceback
import os 
import json
from django.core.exceptions import ImproperlyConfigured
from product_crawling_v2 import product_crawling_v2
from product_crawling_detail import product_crawling_detail
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
        
def detail_and_save_data(room_data, listing_serial_number):
    
    conn = sqlite3.connect('room_lists.db')
    cursor = conn.cursor()
    
    # Create table with additional columns for management cost and options
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dataAnalyze_ProductKB_detail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            매물일련번호 INTEGER,
            단지기본일련번호 INTEGER,
            매물명 TEXT,
            매물도로기본주소 TEXT,
            매물도로상세주소 TEXT,
            해당층수 INTEGER,
            카테고리1 TEXT,
            카테고리2 TEXT,
            지하구분 TEXT,
            지하층수 TEXT,
            총지상층수 INTEGER,
            방향명 TEXT,
            공급면적 REAL,
            전용면적 REAL,
            연면적 REAL,
            대지면적 REAL,
            건축면적 REAL,
            공급면적평 REAL,
            전용면적평 REAL,
            방수 INTEGER,
            욕실수 INTEGER,
            현관구조내용 TEXT,
            입주가능일내용 TEXT,
            입주가능일협의여부 TEXT,
            매매가 INTEGER,
            전세가 INTEGER,
            월세가 INTEGER,
            월세보증금 INTEGER,
            융자금액 INTEGER,
            보증금총액 INTEGER,
            월세금총액 INTEGER,
            기전세금액 INTEGER,
            기월세액 INTEGER,
            전세전환시금액 INTEGER,
            옵션금액 INTEGER,
            분양가 INTEGER,
            권리금액 INTEGER,
            채권금액 INTEGER,
            특징광고내용 TEXT,
            물건특징내용 TEXT,
            제휴중개업소명 TEXT,
            매물주차가능여부 TEXT,
            매물주차대수 INTEGER,
            세대당추차대수비율 REAL,
            난방방식명 TEXT,
            내진설계여부 TEXT,
            방거실형태명 TEXT,
            원룸구조명 TEXT,
            관리비 INTEGER,
            관리비_전기세여부 INTEGER,
            관리비_가스여부 INTEGER,
            관리비_수도여부 INTEGER,
            관리비_인터넷여부 INTEGER,
            관리비_tv여부 INTEGER,
            시스템에어컨여부 INTEGER,
            벽걸이에어컨여부 INTEGER,
            입식에어컨여부 INTEGER,
            침대여부 INTEGER,
            책상여부 INTEGER,
            옷장여부 INTEGER,
            붙박이장여부 INTEGER,
            식탁여부 INTEGER,
            소파여부 INTEGER,
            신발장여부 INTEGER,
            냉장고여부 INTEGER,
            세탁기여부 INTEGER,
            건조기여부 INTEGER,
            샤워부스여부 INTEGER,
            욕조여부 INTEGER,
            비데여부 INTEGER,
            싱크대여부 INTEGER,
            식기세척기여부 INTEGER,
            가스레인지여부  INTEGER,
            인덕션레인지여부 INTEGER,
            베란다여부 INTEGER,
            자체경비원여부 INTEGER,
            비디오전화여부 INTEGER,
            인터폰여부 INTEGER,
            cctv여부 INTEGER,
            방범창여부 INTEGER,
            현관보안여부 INTEGER,
            무인택배박스여부 INTEGER,
            엘리베이터여부 INTEGER,
            테라스여부 INTEGER,
            마당여부 INTEGER,
            사용승인일 TEXT,
            수정일시 TEXT
        )
    ''')

    fail_list = []
    try:
        item = room_data["dataBody"]["data"]["dtailInfo"]
        admnCstInfo = room_data["dataBody"]["data"]["admnCstInfo"]
        optnInfo = room_data["dataBody"]["data"]["optnInfo"]

        # Prepare management cost details
        management_costs = {
            "관리비": item.get("관리비", None),
            "관리비_전기세여부": None,
            "관리비_가스여부": None,
            "관리비_수도여부": None,
            "관리비_인터넷여부": None,
            "관리비_tv여부": None,
        }

        # Populate management cost details from admnCstInfo
        for cost_item in admnCstInfo:
            if cost_item["세부내역타입코드"] == "01":  # 전기세
                management_costs["관리비_전기세여부"] = cost_item["금액"]
            elif cost_item["세부내역타입코드"] == "11":  # 가스
                management_costs["관리비_가스여부"] = cost_item["금액"]
            elif cost_item["세부내역타입코드"] == "12":  # 수도
                management_costs["관리비_수도여부"] = cost_item["금액"]
            elif cost_item["세부내역타입코드"] == "13":  # 인터넷
                management_costs["관리비_인터넷여부"] = cost_item["금액"]
            elif cost_item["세부내역타입코드"] == "14":  # TV
                management_costs["관리비_tv여부"] = cost_item["금액"]

        # Prepare option details
        try:
            options = {
                "시스템에어컨여부": optnInfo.get("시스템에어컨여부", None) if optnInfo else None,
                "벽걸이에어컨여부": optnInfo.get("벽걸이에어컨여부", None) if optnInfo else None,
                "입식에어컨여부": optnInfo.get("입식에어컨여부", None) if optnInfo else None,
                "침대여부": optnInfo.get("침대여부", None) if optnInfo else None,
                "책상여부": optnInfo.get("책상여부", None) if optnInfo else None,
                "옷장여부": optnInfo.get("옷장여부", None) if optnInfo else None,
                "붙박이장여부": optnInfo.get("붙박이장여부", None) if optnInfo else None,
                "식탁여부": optnInfo.get("식탁여부", None) if optnInfo else None,
                "소파여부": optnInfo.get("소파여부", None) if optnInfo else None,
                "신발장여부": optnInfo.get("신발장여부", None) if optnInfo else None,
                "냉장고여부": optnInfo.get("냉장고여부", None) if optnInfo else None,
                "세탁기여부": optnInfo.get("세탁기여부", None) if optnInfo else None,
                "건조기여부": optnInfo.get("건조기여부", None) if optnInfo else None,
                "샤워부스여부": optnInfo.get("샤워부스여부", None) if optnInfo else None,
                "욕조여부": optnInfo.get("욕조여부", None) if optnInfo else None,
                "비데여부": optnInfo.get("비데여부", None) if optnInfo else None,
                "싱크대여부": optnInfo.get("싱크대여부", None) if optnInfo else None,
                "식기세척기여부": optnInfo.get("식기세척기여부", None) if optnInfo else None,
                "가스레인지여부": optnInfo.get("가스레인지여부", None) if optnInfo else None,
                "인덕션레인지여부": optnInfo.get("인덕션레인지여부", None) if optnInfo else None,
                "베란다여부": optnInfo.get("베란다여부", None) if optnInfo else None,
                "자체경비원여부": optnInfo.get("자체경비원여부", None) if optnInfo else None,
                "비디오전화여부": optnInfo.get("비디오전화여부", None) if optnInfo else None,
                "인터폰여부": optnInfo.get("인터폰여부", None) if optnInfo else None,
                "cctv여부": optnInfo.get("cctv여부", None) if optnInfo else None,
                "방범창여부": optnInfo.get("방범창여부", None) if optnInfo else None,
                "현관보안여부": optnInfo.get("현관보안여부", None) if optnInfo else None,
                "무인택배박스여부": optnInfo.get("무인택배박스여부", None) if optnInfo else None,
                "엘리베이터여부": optnInfo.get("엘리베이터여부", None) if optnInfo else None,
                "테라스여부": optnInfo.get("테라스여부", None) if optnInfo else None,
                "마당여부": optnInfo.get("마당여부", None) if optnInfo else None
            }
        except Exception as e:
            print(f"Failed to process options: {e}")
            options = None
        # Insert data into the table
        cursor.execute('''
            INSERT INTO dataAnalyze_ProductKB_detail (
                매물일련번호, 단지기본일련번호, 매물명, 매물도로기본주소, 매물도로상세주소,
                해당층수, 카테고리1, 카테고리2, 지하구분, 지하층수, 총지상층수,
                방향명, 공급면적, 전용면적, 연면적, 대지면적, 건축면적,
                공급면적평, 전용면적평, 방수, 욕실수, 현관구조내용,
                입주가능일내용, 입주가능일협의여부, 매매가, 전세가, 월세가,
                월세보증금, 융자금액, 보증금총액, 월세금총액, 기전세금액,
                기월세액, 전세전환시금액, 옵션금액, 분양가, 권리금액,
                채권금액, 특징광고내용, 물건특징내용, 제휴중개업소명, 매물주차가능여부,
                매물주차대수, 세대당추차대수비율, 난방방식명, 내진설계여부, 방거실형태명,
                원룸구조명, 관리비, 관리비_전기세여부, 관리비_가스여부, 관리비_수도여부,
                관리비_인터넷여부, 관리비_tv여부, 시스템에어컨여부, 벽걸이에어컨여부, 입식에어컨여부,
                침대여부, 책상여부, 옷장여부, 붙박이장여부, 식탁여부,
                소파여부, 신발장여부, 냉장고여부, 세탁기여부, 건조기여부,
                샤워부스여부, 욕조여부, 비데여부, 싱크대여부, 식기세척기여부,
                가스레인지여부, 인덕션레인지여부, 베란다여부, 자체경비원여부, 비디오전화여부,
                인터폰여부, cctv여부, 방범창여부, 현관보안여부, 무인택배박스여부,
                엘리베이터여부, 테라스여부, 마당여부, 사용승인일, 수정일시
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.get('매물일련번호', None), item.get('단지기본일련번호', None), item.get('매물명', None),
            item.get('매물도로기본주소', None), item.get('매물도로상세주소', None), item.get('해당층수', None),
            item.get('카테고리1', None), item.get('카테고리2', None), item.get('지하구분', None),
            item.get('지하층수', None), item.get('총지상층수', None), item.get('방향명', None),
            item.get('공급면적', None), item.get('전용면적', None), item.get('연면적', None),
            item.get('대지면적', None), item.get('건축면적', None), item.get('공급면적평', None),
            item.get('전용면적평', None), item.get('방수', None), item.get('욕실수', None),
            item.get('현관구조내용', None), item.get('입주가능일내용', None), item.get('입주가능일협의여부', None),
            item.get('매매가', None), item.get('전세가', None), item.get('월세가', None),
            item.get('월세보증금', None), item.get('융자금액', None), item.get('보증금총액', None),
            item.get('월세금총액', None), item.get('기전세금액', None), item.get('기월세액', None),
            item.get('전세전환시금액', None), item.get('옵션금액', None), item.get('분양가', None),
            item.get('권리금액', None), item.get('채권금액', None), item.get('특징광고내용', None),
            item.get('물건특징내용', None), item.get('제휴중개업소명', None), item.get('매물주차가능여부', None),
            item.get('매물주차대수', None), item.get('세대당추차대수비율', None), item.get('난방방식명', None),
            item.get('내진설계여부', None), item.get('방거실형태명', None), item.get('원룸구조명', None),
            management_costs.get("관리비", None), management_costs.get("관리비_전기세여부", None),
            management_costs.get("관리비_가스여부", None), management_costs.get("관리비_수도여부", None),
            management_costs.get("관리비_인터넷여부", None), management_costs.get("관리비_tv여부", None),
            options.get("시스템에어컨여부", None), options.get("벽걸이에어컨여부", None),
            options.get("입식에어컨여부", None), options.get("침대여부", None), options.get("책상여부", None),
            options.get("옷장여부", None), options.get("붙박이장여부", None), options.get("식탁여부", None),
            options.get("소파여부", None), options.get("신발장여부", None), options.get("냉장고여부", None),
            options.get("세탁기여부", None), options.get("건조기여부", None), options.get("샤워부스여부", None),
            options.get("욕조여부", None), options.get("비데여부", None), options.get("싱크대여부", None),
            options.get("식기세척기여부", None), options.get("가스레인지여부", None),
            options.get("인덕션레인지여부", None), options.get("베란다여부", None),
            options.get("자체경비원여부", None), options.get("비디오전화여부", None),
            options.get("인터폰여부", None), options.get("cctv여부", None), options.get("방범창여부", None),
            options.get("현관보안여부", None), options.get("무인택배박스여부", None),
            options.get("엘리베이터여부", None), options.get("테라스여부", None), options.get("마당여부", None),
            item.get('사용승인일', None), item.get('수정일시', None)
        ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Transaction failed: {e}")
        traceback.print_exc()
        fail_list.append(listing_serial_number)
        
    finally:
        conn.close()
    
def get_listing_serial_number():        # productKB에서 매물일련번호 리스트 가져오기
    # 데이터베이스 연결
    conn = sqlite3.connect('room_lists.db')
    cursor = conn.cursor()
    
    # 데이터베이스에서 listing_serial_number 열의 모든 데이터를 가져옴
    cursor.execute('SELECT listing_serial_number FROM dataAnalyze_productKB')
    result = cursor.fetchall()
    
    # 결과를 리스트로 변환
    listing_serial_numbers = [row[0] for row in result]
    
    # 연결 종료
    conn.close()
    
    return listing_serial_numbers

def assign_tag(listing_serial_number):        # 매물일련번호를 받아서 태그를 부여
    # 데이터베이스 연결 후 데이터의 정보를 기반으로 태그를 생성함.
    # 일정한 태그를 유지할 수 있음. 
    return listing_serial_number    # 임시로 listing_serial_number를 반환하도록 함.

def add_tag_to_KB(table_name='dataAnalyze_ProductKB_detail'):        # productKB에 태그 추가
    conn = sqlite3.connect('room_lists.db')
    cursor = conn.cursor()
    if table_name == 'dataAnalyze_ProductKB':
        # 1. `dataAnalyze_productKB` 테이블에서 `ad_description` 항목과 `id` 값을 가져오기
        cursor.execute('SELECT id, ad_description FROM {}'.format(table_name))
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
            
    elif table_name == 'dataAnalyze_ProductKB_detail':
        conn = sqlite3.connect('room_lists.db')
        cursor = conn.cursor()

        # 1. dataAnalyze_ProductKB_detail 테이블에서 id, 매물일련번호, 특징광고내용, 물건특징내용 항목을 가져옴
        cursor.execute('''
            SELECT id, 매물일련번호, 특징광고내용, 물건특징내용
            FROM {}
        '''.format(table_name))
        product_ads = cursor.fetchall()

        # 4. dataAnalyze_productTag_detail 테이블이 존재하지 않는다면 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dataAnalyze_productTag_detail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_detail_id INTEGER,
                listing_serial_number INTEGER,
                tagId_id INTEGER,
                product_id INTEGER,
                FOREIGN KEY(product_detail_id) REFERENCES dataAnalyze_ProductKB_detail(id),
                FOREIGN KEY(tagId_id) REFERENCES dataAnalyze_tag(id),
                FOREIGN KEY(product_id) REFERENCES dataAnalyze_ProductKB(id)
            )
        ''')

        try:
            for product_id, listing_serial_number, ad_description, property_description in product_ads:
                if not ad_description and not property_description:
                    continue
                
                # 2. assign_tag 함수를 사용하여 키워드 추출
                tags_1 = assign_tag(listing_serial_number)
                tags_2 = set(extract_keywords(ad_description) + extract_keywords(property_description))

                print("DB기반 결과\n", tags_1, "extract 결과\n", tags_2)     # 이 시점에서 tag들을 깔끔하게 처리하는 과정이 필요함. 
                
                # 3. 추출한 키워드를 dataAnalyze_tag_detail 테이블에 추가하고 tag_id를 가져옴
                tag_ids = []
                for tag in tags:
                    cursor.execute('SELECT id FROM dataAnalyze_tag WHERE tagName = ?', (tag,))
                    result = cursor.fetchone()

                    if result:
                        tag_id = result[0]
                    else:
                        cursor.execute('INSERT INTO dataAnalyze_tag (tagName) VALUES (?)', (tag,))
                        tag_id = cursor.lastrowid

                    tag_ids.append(tag_id)

                # 5. productTag_detail 테이블에 데이터 삽입
                for tag_id in tag_ids:
                    cursor.execute('''
                        INSERT INTO dataAnalyze_productTag_detail (product_detail_id, listing_serial_number, tagId_id, product_id)
                        VALUES (?, ?, ?, ?)
                    ''', (product_id, listing_serial_number, tag_id, None))

                # 6. ProductKB 테이블에서 매물일련번호를 가진 데이터의 id를 가져와서 product_id로 삽입
                cursor.execute('SELECT id FROM dataAnalyze_ProductKB WHERE listing_serial_number = ?', (listing_serial_number,))
                result = cursor.fetchone()
                if result:
                    product_id_main = result[0]
                    cursor.execute('''
                        UPDATE dataAnalyze_productTag_detail 
                        SET product_id = ?
                        WHERE listing_serial_number = ? AND product_detail_id = ?
                    ''', (product_id_main, listing_serial_number, product_id))

            conn.commit()

        except Exception as e:
            conn.rollback()
            print(f"Transaction failed: {e}")
        finally:
            conn.close()
    
def main_cluster_ver():        # 매물 데이터 클러스터 단위로 크롤링 및 저장
    room_data = connect_db()
    process_and_save_data(room_data)
    add_tag_to_KB()    

def main_detail_ver():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    secret_file = os.path.join(base_dir, '..', '..','secret.json')

    with open(secret_file) as f:
        secrets = json.loads(f.read())
    listing_serial_number_lists = get_listing_serial_number()         #productKB에서 모든 매물일련번호 리스트 가져오기 
    for serial_number in listing_serial_number_lists:
        detail_info = product_crawling_detail(serial_number, secrets)  # 매물 상세 정보 가져오기
        detail_and_save_data(detail_info, serial_number)     # 가져온 상세 정보로 데이터베이스에 저장
    add_tag_to_KB("dataAnalyze_ProductKB_detail")        # 상세 정보에 태그 추가
    
if __name__ == "__main__":
    main_detail_ver()