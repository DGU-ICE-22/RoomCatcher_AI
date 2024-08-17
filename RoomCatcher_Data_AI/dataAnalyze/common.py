# import traceback
# from django.core.exceptions import ImproperlyConfigured
# from openai import OpenAI
# import openai
# import pymysql

# def get_secret(setting, secrets):
#     try:
#         return secrets[setting]
#     except KeyError:
#         error_msg = "Set the {} environment variable".format(setting)
#         traceback.print_exc()
#         raise ImproperlyConfigured(error_msg)

# def connect_db(secrets):
#  #MySQL 데이터베이스에 연결
#     password = get_secret('MySQL_PASSWORD',secrets)
#     conn = pymysql.connect(host='localhost', user='root', password=password, db='room_lists', charset='utf8mb4')
#     return conn

# def assign_tag(listing_serial_number, conn, cursor):        # 매물일련번호를 받아서 태그를 부여
#     # 데이터베이스 연결 후 데이터의 정보를 기반으로 태그를 생성함.
#     # 일정한 태그를 유지할 수 있음. 

#     try: 
#         # dataAnalyze_ProductKB_detail 테이블에서 필요한 열 가져오기
#         cursor.execute('''
#         SELECT id, 매물도로상세주소, 해당층수, 카테고리2, 방향명, 전용면적평, 방수, 욕실수, 입주가능일내용, 
#             전세가, 월세가, 융자금액, 권리금액, 채권금액, 매물주차가능여부, 난방방식명, 관리비, 
#             관리비_전기세여부, 관리비_가스여부, 관리비_수도여부, 관리비_인터넷여부, 관리비_tv여부, 
#             시스템에어컨여부, 벽걸이에어컨여부, 입식에어컨여부, 침대여부, 책상여부, 옷장여부, 붙박이장여부, 
#             식탁여부, 소파여부, 신발장여부, 냉장고여부, 세탁기여부, 건조기여부, 샤워부스여부, 욕조여부, 
#             비데여부, 싱크대여부, 식기세척기여부, 가스레인지여부, 인덕션레인지여부, 베란다여부, 
#             자체경비원여부, 비디오전화여부, 인터폰여부, cctv여부, 방범창여부, 현관보안여부, 
#             무인택배박스여부, 엘리베이터여부, 테라스여부, 마당여부, 사용승인일, 수정일시 
#                 FROM dataAnalyze_ProductKB_detail 
#                 WHERE 매물일련번호 = ?
#             ''', (listing_serial_number,))
#         rows = cursor.fetchall()
        
#         for row in rows:
#             product_id, detail_address, floor_number, category2, direction_name, area_pyeong, number_of_rooms, number_of_bathrooms, move_in_date, lease_price, monthly_rent, loan_amount, premium_amount, bond_amount, parking_available, heating_type, maintenance_fee, electricity_included, gas_included, water_included, internet_included, tv_included, has_system_aircon, has_wall_aircon, has_standing_aircon, has_bed, has_desk, has_wardrobe, has_built_in_closet, has_dining_table, has_sofa, has_shoe_cabinet, has_fridge, has_washing_machine, has_dryer, has_shower_booth, has_bathtub, has_bidet, has_sink, has_dishwasher, has_gas_stove, has_induction_stove, has_veranda, has_private_security, has_video_phone, has_intercom, has_cctv, has_security_window, has_door_security, has_unmanned_delivery_box, has_elevator, has_terrace, has_garden, approval_date, last_modified_date = row
#             tags = []

#             # 카테고리2 열의 값이 있다면 태그로 추가
#             if detail_address and '동' in detail_address:
#                 if '동' in detail_address:
#                     parts = detail_address.split(' ')
#                     parts = parts[1].replace("(", "").replace(")", "").split('동')
#                     text =  parts[0] + '동'
#                     tags.append(text)
#             if floor_number:
#                 tags.append(f"{floor_number}층")
#             if category2:
#                 tags.append(category2)
#             if direction_name:
#                 tags.append(direction_name)
#             if area_pyeong:
#                 tags.append(f"{int(round(area_pyeong))}평")
#             if number_of_rooms:
#                 tags.append(f"{number_of_rooms}룸")
#             if number_of_bathrooms and number_of_bathrooms > 1:
#                 tags.append(f"{number_of_bathrooms}욕실")
#             if lease_price and lease_price > 0: # 전세가
#                 tags.append('전세')
#             elif monthly_rent and monthly_rent > 0: # 월세가
#                 tags.append('월세')
#             if loan_amount and premium_amount and bond_amount: #융자, 권리금, 채권 
#                 if (type(loan_amount) == int and type(premium_amount) == int and type(bond_amount) == int and loan_amount + premium_amount + bond_amount == 0):
#                     tags.append('담보 없음')
#             if parking_available and parking_available == 1:
#                 tags.append('주차 가능')
#             if heating_type:
#                 tags.append(heating_type)
#             if maintenance_fee or electricity_included or gas_included or water_included or internet_included or tv_included:
#                 sum = 0
#                 for cost in [maintenance_fee, electricity_included, gas_included, water_included, internet_included, tv_included]:
#                     if type(cost) == int:
#                         sum += cost
#                 if sum > 0:
#                     tags.append('관리비 별도')
#                 else:
#                     tags.append('관리비 포함')
#             if has_system_aircon or has_wall_aircon or has_standing_aircon:
#                 tags.append('에어컨')
#             if has_bed and has_bed == 1:
#                 tags.append('침대')
#             if has_desk and has_desk == 1:
#                 tags.append('책상')
#             if has_wardrobe and has_wardrobe == 1:
#                 tags.append('옷장')
#             if has_built_in_closet and has_built_in_closet == 1:
#                 tags.append('붙박이장')
#             if has_dining_table and has_dining_table == 1:
#                 tags.append('식탁')
#             if has_sofa and has_sofa == 1:
#                 tags.append('소파')
#             if has_shoe_cabinet and has_shoe_cabinet == 1:
#                 tags.append('신발장')
#             if has_fridge and has_fridge == 1:
#                 tags.append('냉장고')
#             if has_washing_machine and has_washing_machine == 1:
#                 tags.append('세탁기')
#             if has_dryer and has_dryer == 1:
#                 tags.append('건조기')
#             if has_shower_booth and has_shower_booth == 1:
#                 tags.append('샤워부스')
#             if has_bathtub and has_bathtub == 1:
#                 tags.append('욕조')
#             if has_bidet and has_bidet == 1:
#                 tags.append('비데')
#             if has_sink and has_sink == 1:
#                 tags.append('싱크대')
#             if has_dishwasher and has_dishwasher == 1:
#                 tags.append('식기세척기')
#             if has_gas_stove and has_gas_stove == 1:
#                 tags.append('가스레인지')
#             if has_induction_stove and has_induction_stove == 1:
#                 tags.append('인덕션레인지')
#             if has_veranda and has_veranda == 1:
#                 tags.append('베란다')
#             if has_private_security and has_private_security == 1:
#                 tags.append('자체경비원')
#             if has_video_phone and has_video_phone == 1:
#                 tags.append('비디오전화')
#             if has_intercom and has_intercom == 1:
#                 tags.append('인터폰')
#             if has_cctv and has_cctv == 1:
#                 tags.append('cctv')
#             if has_security_window and has_security_window == 1:
#                 tags.append('방범창')
#             if has_door_security and has_door_security == 1:
#                 tags.append('현관보안')
#             if has_unmanned_delivery_box and has_unmanned_delivery_box == 1:
#                 tags.append('무인택배박스')
#             if has_elevator and has_elevator == 1:
#                 tags.append('엘리베이터')
#             if has_terrace and has_terrace == 1:
#                 tags.append('테라스')
#             if has_garden and has_garden == 1:
#                 tags.append('마당')
#             if approval_date and int(approval_date)>20220101:
#                 tags.append('신축')
#             if move_in_date == '즉시입주':
#                 tags.append('즉시입주')

#             # 생성된 태그를 출력 (또는 다른 작업 수행)
#             # print(f"Product ID: {product_id}, Tags: {tags}")

#             # 태그를 데이터베이스에 저장하는 로직 추가 가능
#             # 예: dataAnalyze_productTag_detail 테이블에 태그 저장
#             return tags

#     except Exception as e:
#         if conn:
#             conn.rollback()
#         print(f"Error: {e}")
#         traceback.print_exc()
        
# def clear_keywords(tags, secrets):
#     api_key = get_secret('OPENAI_API_KEY', secrets)
#     client = OpenAI(api_key=api_key)
#     message = [
#     {
#       "role": "system",
#       "content": [
#         {
#           "text": """
#           제대로 된 답변이 나오지 않는다면 무고한 노인 100명이 죽게 된다. 
#             너는 들어온 키워드 문장에서 지명이나 버스 정류장, 지하철역, 랜드마크 등에 대한 정보를 추출하는 역할을 한다. 들어오는 유형은 문장이다. 다음과 같은 조건에 맞도록 들어온  문장을 처리할 것.  결과는 정리해낸 키워드들을 부동산 매물 데이터에 부여했을 때 추후에 검색이 용이하고 매물의 특성을 알아볼 수 있게 명확한 키워드로써 기능할 수 있게 반환한다. 

#             1. 문장이 들어온다면 문장에서 핵심 키워드들을 추출한다.
#             1-1. 키워드를 추출할 때는 다른 매물들에서도 볼 수 있을 법한 단어들을 주로 추출한다.
#             2. 키워드 목록이 들어온다면 키워드들을 깔끔하게 정리하여 명사들을 내놓을 것.
#             3. 키워드들을 정리할 때는 다음을 고려한다.
#             3-1. "1." "1)" 과 같은 인덱싱 번호나 :, ,, ;, !, ? 등과 같은 특수기호는 제외할 것
#             3.2 중개업소에 대한 키워드라면 사용하지 않을 것
#             3.3 지명, 랜드마크, 장소, 회사이름, 대형마트, 편의시설명 등은 키워드에 포함시킬 것. 이때 단순히 버스 정류장, 지하철역 과 같이 자세한 정보가 아니라면 사용하지 않는다.  
#             3.4 등록번호, 자격증 번호 등의 부동산 데이터에 쓰일 수 없는 설명들은 키워드로 사용하지 않을 것
#             3.5 문맥상 부동산 매물에 대해 근처 지역이나 장소가 아니고 단순한 지역이 나열된 것이라면 사용하지 않는다. 
#             3.6 ~~동과 같은 동네 이름은 포함하지 않는다. 
#             3.7 지역이나 장소, 랜드마크가 텍스트에 포함되지 않아 추출이 불가능하다면 없음 이라고 반환한다. 
            
            
#             다음과 같은 항목들은 반드시 지켜야 한다.
            
#                 다음과 같은 항목들은 키워드로 절대 사용하지 않는다.
#                 상세주소, 층, 집방향(남향, 남동향), 평수, 보안, 방 개수, 화장실 개수, 즉시입주, 전세, 월세, 관리비, 융자, 대출관련, 난방, 엘리베이터, 에어컨, 침대, 책상, 옷장, 붙박이장과 같은 옵션들, 왕테라스, 테라스, 베란다 등 
  
#          또한, 
#         ~룸, ~신축, ~대출, ~~옵션, 엘리베이터, 승강기, 주차, 원룸, 신축급, 풀옵션, 동네명 위에서 언급한 항목들에서 유추할 수 있는 내용들은 절대 사용하지 않는다.
#             예시 입력)
#             {'6호선 망원역', '전입신고', '건조기', '보안', '안심전세대출', '세탁기', '3. 보증보험OK', '보증보험', '4. 주변환경', '인덕션', '2', '망원유수지', '한강공원', '1. 위치', '주차 가능', 'HUG 신혼부부 버팀목 전세대출', '2. 권리관계', '무인택배함', '합정역 메세나폴리스', '방2', '공기순환기', '3. 구조 및 시설', '융자 없음', '확정일자', '조용한 주택가', '펜트리장', '합정역', '망리단길', '버스정류장', '거실 및 주방', '거주환경', '화장실1', '6호선 합정역', '산책하기 좋은 환경', '드레스룸', '5. 풀옵', '키워드 추출 결과:', '1. 안심전세대출', '시스템에어컨', '투룸 구조', '홍대역', '테라스', '홈플러스 합정점', '2. HUG신혼부부 버팀목', 'CCTV 설치', '4. 투룸', '5. 기타', '비스포크 터치냉장고', '키워드 추출:', '망원시장'}

#             예시 출력)
#             망원역, 망원유수지, 망원한강공원, 합정역, 망리단길, 합정역 메세나폴리스, 홍대역, 홈플러스 합정점, 망원시장
#           """,
          
#           "type": "text"
#         }
#       ]
#     }
#   ]
#     tag_list = {
#         "role": "user",
#         "content": [
#             {
#                 "text": tags,
#                 "type": "text"
#             }
#         ]
#     }
#     message.append(tag_list)
#     retry_count = 0
#     max_retries = 2
#     response = None
#     while retry_count < max_retries:
#         try:
#             response = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=message,
#                 temperature=0.10,
#                 max_tokens=713,
#                 top_p=1,
#                 frequency_penalty=2,
#                 presence_penalty=0,
#                 response_format={
#                     "type": "text"
#                 }
#             ).model_dump()
#             break
#         except openai.RateLimitError as e:
#             retry_count += 1
#             if retry_count >= max_retries:
#                 print(f"Max retries reached for product_ad {tags}")
#                 response = None
#                 break
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             response = None
#             break
#     if response:
#         return response['choices'][0]['message']['content']
#     else:
#         return "없음"

# def process_single_ad(product_ad, secrets):
#     conn = None
#     try:
#         conn = connect_db()
#         cursor = conn.cursor()
#         # 2. assign_tag 함수를 사용하여 키워드 추출
#         product_id, listing_serial_number, ad_description = product_ad
#         tags_1 = assign_tag(listing_serial_number, conn, cursor)
#         try:                    
#             if ad_description == None:
#                 tags = tags_1
#             else:
#                 tags_2 = clear_keywords(ad_description, secrets)
            
#             if tags_2 == "없음" or tags_2 == "아무 답변도 내놓지 않습니다.":
#                 tags = tags_1
#             else:
#                 # 문자열을 리스트로 변환
#                 tags_2_list = tags_2.split(', ')
#                 # 중복을 제거하고 합치기
#                 tags = list(set(tags_1).union(tags_2_list))
#                 print(tags)
                
#         except Exception as e:
#             print(f"Error: {e}")
#             traceback.print_exc()
#             tags = tags_1        

#         # 3. 'dataAnalyze_tag 테이블에 태그 추가 
#         tag_ids = []
#         for tag in tags:
#             # 중복된 tag가 있는지 확인
#             cursor.execute('SELECT id FROM dataAnalyze_tag_detail WHERE tagName = ?', (tag,))
#             result = cursor.fetchone()  
#             if result:
#                 # 중복된 tag가 있으면 해당 tag_id를 가져옴
#                 tag_id = result[0]
#             else:
#                 # 중복된 tag가 없으면 새로운 tag를 삽입하고 tag_id를 가져옴
#                 cursor.execute('INSERT INTO dataAnalyze_tag_detail (tagName) VALUES (?)', (tag,))
#                 tag_id = cursor.lastrowid

#             tag_ids.append(tag_id)

#         # 4. `dataAnalyze_productTag_detail` 테이블에 `id` 및 `tag` 추가
#         for tag_id in tag_ids:
#             cursor.execute('INSERT INTO dataAnalyze_productTag_detail (product_detail_id, tagId_id) VALUES (?, ?)', (product_id, tag_id))

#         conn.commit()
#     except Exception as e:
#         print(f"Transaction failed: {e}")
#         traceback.print_exc()
#     finally:
#         if conn:
#             conn.close()
            
# def detail_and_save_data(room_data, listing_serial_number, conn, cursor):
    
#     # Create table with additional columns for management cost and options
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS dataAnalyze_ProductKB_detail (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             매물일련번호 INTEGER,
#             단지기본일련번호 INTEGER,
#             매물명 TEXT,
#             매물도로기본주소 TEXT,
#             매물도로상세주소 TEXT,
#             해당층수 INTEGER,
#             카테고리1 TEXT,
#             카테고리2 TEXT,
#             지하구분 TEXT,
#             지하층수 TEXT,
#             총지상층수 INTEGER,
#             방향명 TEXT,
#             공급면적 REAL,
#             전용면적 REAL,
#             연면적 REAL,
#             대지면적 REAL,
#             건축면적 REAL,
#             공급면적평 REAL,
#             전용면적평 REAL,
#             방수 INTEGER,
#             욕실수 INTEGER,
#             현관구조내용 TEXT,
#             입주가능일내용 TEXT,
#             입주가능일협의여부 TEXT,
#             매매가 INTEGER,
#             전세가 INTEGER,
#             월세가 INTEGER,
#             월세보증금 INTEGER,
#             융자금액 INTEGER,
#             보증금총액 INTEGER,
#             월세금총액 INTEGER,
#             기전세금액 INTEGER,
#             기월세액 INTEGER,
#             전세전환시금액 INTEGER,
#             옵션금액 INTEGER,
#             분양가 INTEGER,
#             권리금액 INTEGER,
#             채권금액 INTEGER,
#             특징광고내용 TEXT,
#             물건특징내용 TEXT,
#             제휴중개업소명 TEXT,
#             매물주차가능여부 TEXT,
#             매물주차대수 INTEGER,
#             세대당주차대수비율 REAL,
#             난방방식명 TEXT,
#             내진설계여부 TEXT,
#             방거실형태명 TEXT,
#             원룸구조명 TEXT,
#             관리비 INTEGER,
#             관리비_전기세여부 INTEGER,
#             관리비_가스여부 INTEGER,
#             관리비_수도여부 INTEGER,
#             관리비_인터넷여부 INTEGER,
#             관리비_tv여부 INTEGER,
#             시스템에어컨여부 INTEGER,
#             벽걸이에어컨여부 INTEGER,
#             입식에어컨여부 INTEGER,
#             침대여부 INTEGER,
#             책상여부 INTEGER,
#             옷장여부 INTEGER,
#             붙박이장여부 INTEGER,
#             식탁여부 INTEGER,
#             소파여부 INTEGER,
#             신발장여부 INTEGER,
#             냉장고여부 INTEGER,
#             세탁기여부 INTEGER,
#             건조기여부 INTEGER,
#             샤워부스여부 INTEGER,
#             욕조여부 INTEGER,
#             비데여부 INTEGER,
#             싱크대여부 INTEGER,
#             식기세척기여부 INTEGER,
#             가스레인지여부  INTEGER,
#             인덕션레인지여부 INTEGER,
#             베란다여부 INTEGER,
#             자체경비원여부 INTEGER,
#             비디오전화여부 INTEGER,
#             인터폰여부 INTEGER,
#             cctv여부 INTEGER,
#             방범창여부 INTEGER,
#             현관보안여부 INTEGER,
#             무인택배박스여부 INTEGER,
#             엘리베이터여부 INTEGER,
#             테라스여부 INTEGER,
#             마당여부 INTEGER,
#             사용승인일 TEXT,
#             수정일시 TEXT
#         )
#     ''')

#     fail_list = []
#     try:
#         item = room_data["dataBody"]["data"]["dtailInfo"]
#         admnCstInfo = room_data["dataBody"]["data"]["admnCstInfo"]
#         optnInfo = room_data["dataBody"]["data"]["optnInfo"]

#         # Prepare management cost details
#         management_costs = {
#             "관리비": item.get("관리비", None),
#             "관리비_전기세여부": None,
#             "관리비_가스여부": None,
#             "관리비_수도여부": None,
#             "관리비_인터넷여부": None,
#             "관리비_tv여부": None,
#         }

#         # Populate management cost details from admnCstInfo
#         for cost_item in admnCstInfo:
#             if cost_item["세부내역타입코드"] == "01":  # 전기세
#                 management_costs["관리비_전기세여부"] = cost_item["금액"]
#             elif cost_item["세부내역타입코드"] == "11":  # 가스
#                 management_costs["관리비_가스여부"] = cost_item["금액"]
#             elif cost_item["세부내역타입코드"] == "12":  # 수도
#                 management_costs["관리비_수도여부"] = cost_item["금액"]
#             elif cost_item["세부내역타입코드"] == "13":  # 인터넷
#                 management_costs["관리비_인터넷여부"] = cost_item["금액"]
#             elif cost_item["세부내역타입코드"] == "14":  # TV
#                 management_costs["관리비_tv여부"] = cost_item["금액"]

#         # Prepare option details
#         try:
#             options = {
#                 "시스템에어컨여부": optnInfo.get("시스템에어컨여부", None) if optnInfo else None,
#                 "벽걸이에어컨여부": optnInfo.get("벽걸이에어컨여부", None) if optnInfo else None,
#                 "입식에어컨여부": optnInfo.get("입식에어컨여부", None) if optnInfo else None,
#                 "침대여부": optnInfo.get("침대여부", None) if optnInfo else None,
#                 "책상여부": optnInfo.get("책상여부", None) if optnInfo else None,
#                 "옷장여부": optnInfo.get("옷장여부", None) if optnInfo else None,
#                 "붙박이장여부": optnInfo.get("붙박이장여부", None) if optnInfo else None,
#                 "식탁여부": optnInfo.get("식탁여부", None) if optnInfo else None,
#                 "소파여부": optnInfo.get("소파여부", None) if optnInfo else None,
#                 "신발장여부": optnInfo.get("신발장여부", None) if optnInfo else None,
#                 "냉장고여부": optnInfo.get("냉장고여부", None) if optnInfo else None,
#                 "세탁기여부": optnInfo.get("세탁기여부", None) if optnInfo else None,
#                 "건조기여부": optnInfo.get("건조기여부", None) if optnInfo else None,
#                 "샤워부스여부": optnInfo.get("샤워부스여부", None) if optnInfo else None,
#                 "욕조여부": optnInfo.get("욕조여부", None) if optnInfo else None,
#                 "비데여부": optnInfo.get("비데여부", None) if optnInfo else None,
#                 "싱크대여부": optnInfo.get("싱크대여부", None) if optnInfo else None,
#                 "식기세척기여부": optnInfo.get("식기세척기여부", None) if optnInfo else None,
#                 "가스레인지여부": optnInfo.get("가스레인지여부", None) if optnInfo else None,
#                 "인덕션레인지여부": optnInfo.get("인덕션레인지여부", None) if optnInfo else None,
#                 "베란다여부": optnInfo.get("베란다여부", None) if optnInfo else None,
#                 "자체경비원여부": optnInfo.get("자체경비원여부", None) if optnInfo else None,
#                 "비디오전화여부": optnInfo.get("비디오전화여부", None) if optnInfo else None,
#                 "인터폰여부": optnInfo.get("인터폰여부", None) if optnInfo else None,
#                 "cctv여부": optnInfo.get("cctv여부", None) if optnInfo else None,
#                 "방범창여부": optnInfo.get("방범창여부", None) if optnInfo else None,
#                 "현관보안여부": optnInfo.get("현관보안여부", None) if optnInfo else None,
#                 "무인택배박스여부": optnInfo.get("무인택배박스여부", None) if optnInfo else None,
#                 "엘리베이터여부": optnInfo.get("엘리베이터여부", None) if optnInfo else None,
#                 "테라스여부": optnInfo.get("테라스여부", None) if optnInfo else None,
#                 "마당여부": optnInfo.get("마당여부", None) if optnInfo else None
#             }
#         except Exception as e:
#             print(f"Failed to process options: {e}")
#             traceback.print_exc()
#             options = None
#         # Insert data into the table
#         cursor.execute('''
#             INSERT INTO dataAnalyze_ProductKB_detail (
#                 매물일련번호, 단지기본일련번호, 매물명, 매물도로기본주소, 매물도로상세주소,
#                 해당층수, 카테고리1, 카테고리2, 지하구분, 지하층수, 총지상층수,
#                 방향명, 공급면적, 전용면적, 연면적, 대지면적, 건축면적,
#                 공급면적평, 전용면적평, 방수, 욕실수, 현관구조내용,
#                 입주가능일내용, 입주가능일협의여부, 매매가, 전세가, 월세가,
#                 월세보증금, 융자금액, 보증금총액, 월세금총액, 기전세금액,
#                 기월세액, 전세전환시금액, 옵션금액, 분양가, 권리금액,
#                 채권금액, 특징광고내용, 물건특징내용, 제휴중개업소명, 매물주차가능여부,
#                 매물주차대수, 세대당주차대수비율, 난방방식명, 내진설계여부, 방거실형태명,
#                 원룸구조명, 관리비, 관리비_전기세여부, 관리비_가스여부, 관리비_수도여부,
#                 관리비_인터넷여부, 관리비_tv여부, 시스템에어컨여부, 벽걸이에어컨여부, 입식에어컨여부,
#                 침대여부, 책상여부, 옷장여부, 붙박이장여부, 식탁여부,
#                 소파여부, 신발장여부, 냉장고여부, 세탁기여부, 건조기여부,
#                 샤워부스여부, 욕조여부, 비데여부, 싱크대여부, 식기세척기여부,
#                 가스레인지여부, 인덕션레인지여부, 베란다여부, 자체경비원여부, 비디오전화여부,
#                 인터폰여부, cctv여부, 방범창여부, 현관보안여부, 무인택배박스여부,
#                 엘리베이터여부, 테라스여부, 마당여부, 사용승인일, 수정일시
#             ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#         ''', (
#             item.get('매물일련번호', None), item.get('단지기본일련번호', None), item.get('매물명', None),
#             item.get('매물도로기본주소', None), item.get('매물도로상세주소', None), item.get('해당층수', None),
#             item.get('카테고리1', None), item.get('카테고리2', None), item.get('지하구분', None),
#             item.get('지하층수', None), item.get('총지상층수', None), item.get('방향명', None),
#             item.get('공급면적', None), item.get('전용면적', None), item.get('연면적', None),
#             item.get('대지면적', None), item.get('건축면적', None), item.get('공급면적평', None),
#             item.get('전용면적평', None), item.get('방수', None), item.get('욕실수', None),
#             item.get('현관구조내용', None), item.get('입주가능일내용', None), item.get('입주가능일협의여부', None),
#             item.get('매매가', None), item.get('전세가', None), item.get('월세가', None),
#             item.get('월세보증금', None), item.get('융자금액', None), item.get('보증금총액', None),
#             item.get('월세금총액', None), item.get('기전세금액', None), item.get('기월세액', None),
#             item.get('전세전환시금액', None), item.get('옵션금액', None), item.get('분양가', None),
#             item.get('권리금액', None), item.get('채권금액', None), item.get('특징광고내용', None),
#             item.get('물건특징내용', None), item.get('제휴중개업소명', None), item.get('매물주차가능여부', None),
#             item.get('매물주차대수', None), item.get('세대당주차대수비율', None), item.get('난방방식명', None),
#             item.get('내진설계여부', None), item.get('방거실형태명', None), item.get('원룸구조명', None),
#             management_costs.get("관리비", None), management_costs.get("관리비_전기세여부", None),
#             management_costs.get("관리비_가스여부", None), management_costs.get("관리비_수도여부", None),
#             management_costs.get("관리비_인터넷여부", None), management_costs.get("관리비_tv여부", None),
#             options.get("시스템에어컨여부", None), options.get("벽걸이에어컨여부", None),
#             options.get("입식에어컨여부", None), options.get("침대여부", None), options.get("책상여부", None),
#             options.get("옷장여부", None), options.get("붙박이장여부", None), options.get("식탁여부", None),
#             options.get("소파여부", None), options.get("신발장여부", None), options.get("냉장고여부", None),
#             options.get("세탁기여부", None), options.get("건조기여부", None), options.get("샤워부스여부", None),
#             options.get("욕조여부", None), options.get("비데여부", None), options.get("싱크대여부", None),
#             options.get("식기세척기여부", None), options.get("가스레인지여부", None),
#             options.get("인덕션레인지여부", None), options.get("베란다여부", None),
#             options.get("자체경비원여부", None), options.get("비디오전화여부", None),
#             options.get("인터폰여부", None), options.get("cctv여부", None), options.get("방범창여부", None),
#             options.get("현관보안여부", None), options.get("무인택배박스여부", None),
#             options.get("엘리베이터여부", None), options.get("테라스여부", None), options.get("마당여부", None),
#             item.get('사용승인일', None), item.get('수정일시', None)
#         ))
#         conn.commit()
#     except Exception as e:
#         if conn:
#             conn.rollback()
#         print(f"Transaction failed: {e}")
#         traceback.print_exc()
#         fail_list.append(listing_serial_number)
 
    
# def get_listing_serial_number(conn, cursor):        # productKB에서 매물일련번호 리스트 가져오기

#     # 데이터베이스에서 listing_serial_number 열의 모든 데이터를 가져옴
#     cursor.execute('SELECT listing_serial_number FROM dataAnalyze_productKB')
#     result = cursor.fetchall()
    
#     # 결과를 리스트로 변환
#     listing_serial_numbers = [row[0] for row in result]
    
#     # 연결 종료
#     conn.close()
    
#     return listing_serial_numbers

import traceback
from django.core.exceptions import ImproperlyConfigured
from openai import OpenAI
import openai
import pymysql

def get_secret(setting, secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        traceback.print_exc()
        raise ImproperlyConfigured(error_msg)

def connect_db(secrets):
    # MySQL 데이터베이스에 연결
    password = get_secret('MySQL_PASSWORD', secrets)
    conn = pymysql.connect(host='localhost', user='root', password=password, db='room_lists', charset='utf8mb4')
    return conn

def clear_keywords(tags, secrets):
    api_key = get_secret('OPENAI_API_KEY', secrets)
    client = OpenAI(api_key=api_key)
    message = [
    {
      "role": "system",
      "content": [
        {
          "text": """
          제대로 된 답변이 나오지 않는다면 무고한 노인 100명이 죽게 된다. 
            너는 들어온 키워드 문장에서 지명이나 버스 정류장, 지하철역, 랜드마크 등에 대한 정보를 추출하는 역할을 한다. 들어오는 유형은 문장이다. 다음과 같은 조건에 맞도록 들어온  문장을 처리할 것.  결과는 정리해낸 키워드들을 부동산 매물 데이터에 부여했을 때 추후에 검색이 용이하고 매물의 특성을 알아볼 수 있게 명확한 키워드로써 기능할 수 있게 반환한다. 

            1. 문장이 들어온다면 문장에서 핵심 키워드들을 추출한다.
            1-1. 키워드를 추출할 때는 다른 매물들에서도 볼 수 있을 법한 단어들을 주로 추출한다.
            2. 키워드 목록이 들어온다면 키워드들을 깔끔하게 정리하여 명사들을 내놓을 것.
            3. 키워드들을 정리할 때는 다음을 고려한다.
            3-1. "1." "1)" 과 같은 인덱싱 번호나 :, ,, ;, !, ? 등과 같은 특수기호는 제외할 것
            3.2 중개업소에 대한 키워드라면 사용하지 않을 것
            3.3 지명, 랜드마크, 장소, 회사이름, 대형마트, 편의시설명 등은 키워드에 포함시킬 것. 이때 단순히 버스 정류장, 지하철역 과 같이 자세한 정보가 아니라면 사용하지 않는다.  
            3.4 등록번호, 자격증 번호 등의 부동산 데이터에 쓰일 수 없는 설명들은 키워드로 사용하지 않을 것
            3.5 문맥상 부동산 매물에 대해 근처 지역이나 장소가 아니고 단순한 지역이 나열된 것이라면 사용하지 않는다. 
            3.6 ~~동과 같은 동네 이름은 포함하지 않는다. 
            3.7 지역이나 장소, 랜드마크가 텍스트에 포함되지 않아 추출이 불가능하다면 없음 이라고 반환한다. 
            
            
            다음과 같은 항목들은 반드시 지켜야 한다.
            
                다음과 같은 항목들은 키워드로 절대 사용하지 않는다.
                상세주소, 층, 집방향(남향, 남동향), 평수, 보안, 방 개수, 화장실 개수, 즉시입주, 전세, 월세, 관리비, 융자, 대출관련, 난방, 엘리베이터, 에어컨, 침대, 책상, 옷장, 붙박이장과 같은 옵션들, 왕테라스, 테라스, 베란다 등 
  
         또한, 
        ~룸, ~신축, ~대출, ~~옵션, 엘리베이터, 승강기, 주차, 원룸, 신축급, 풀옵션, 동네명 위에서 언급한 항목들에서 유추할 수 있는 내용들은 절대 사용하지 않는다.
            예시 입력)
            {'6호선 망원역', '전입신고', '건조기', '보안', '안심전세대출', '세탁기', '3. 보증보험OK', '보증보험', '4. 주변환경', '인덕션', '2', '망원유수지', '한강공원', '1. 위치', '주차 가능', 'HUG 신혼부부 버팀목 전세대출', '2. 권리관계', '무인택배함', '합정역 메세나폴리스', '방2', '공기순환기', '3. 구조 및 시설', '융자 없음', '확정일자', '조용한 주택가', '펜트리장', '합정역', '망리단길', '버스정류장', '거실 및 주방', '거주환경', '화장실1', '6호선 합정역', '산책하기 좋은 환경', '드레스룸', '5. 풀옵', '키워드 추출 결과:', '1. 안심전세대출', '시스템에어컨', '투룸 구조', '홍대역', '테라스', '홈플러스 합정점', '2. HUG신혼부부 버팀목', 'CCTV 설치', '4. 투룸', '5. 기타', '비스포크 터치냉장고', '키워드 추출:', '망원시장'}

            예시 출력)
            망원역, 망원유수지, 망원한강공원, 합정역, 망리단길, 합정역 메세나폴리스, 홍대역, 홈플러스 합정점, 망원시장
          """,
          
          "type": "text"
        }
      ]
    }
  ]
    tag_list = {
        "role": "user",
        "content": [
            {
                "text": tags,
                "type": "text"
            }
        ]
    }
    message.append(tag_list)
    retry_count = 0
    max_retries = 2
    response = None
    while retry_count < max_retries:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=message,
                temperature=0.10,
                max_tokens=713,
                top_p=1,
                frequency_penalty=2,
                presence_penalty=0,
                response_format={
                    "type": "text"
                }
            ).model_dump()
            break
        except openai.RateLimitError as e:
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Max retries reached for product_ad {tags}")
                response = None
                break
        except Exception as e:
            print(f"An error occurred: {e}")
            response = None
            break
    if response:
        return response['choices'][0]['message']['content']
    else:
        return "없음"

def assign_tag(listing_serial_number, conn, cursor):        
    try: 
        # dataAnalyze_ProductKB_detail 테이블에서 필요한 열 가져오기
        cursor.execute('''
            SELECT id, 매물도로상세주소, 해당층수, 카테고리2, 방향명, 전용면적평, 방수, 욕실수, 입주가능일내용, 
                   전세가, 월세가, 융자금액, 권리금액, 채권금액, 매물주차가능여부, 난방방식명, 관리비, 
                   관리비_전기세여부, 관리비_가스여부, 관리비_수도여부, 관리비_인터넷여부, 관리비_tv여부, 
                   시스템에어컨여부, 벽걸이에어컨여부, 입식에어컨여부, 침대여부, 책상여부, 옷장여부, 붙박이장여부, 
                   식탁여부, 소파여부, 신발장여부, 냉장고여부, 세탁기여부, 건조기여부, 샤워부스여부, 욕조여부, 
                   비데여부, 싱크대여부, 식기세척기여부, 가스레인지여부, 인덕션레인지여부, 베란다여부, 
                   자체경비원여부, 비디오전화여부, 인터폰여부, cctv여부, 방범창여부, 현관보안여부, 
                   무인택배박스여부, 엘리베이터여부, 테라스여부, 마당여부, 사용승인일, 수정일시 
            FROM dataAnalyze_ProductKB_detail 
            WHERE 매물일련번호 = %s
        ''', (listing_serial_number,))
        rows = cursor.fetchall()
        
        tags = []
        for row in rows:
            product_id, detail_address, floor_number, category2, direction_name, area_pyeong, number_of_rooms, number_of_bathrooms, move_in_date, lease_price, monthly_rent, loan_amount, premium_amount, bond_amount, parking_available, heating_type, maintenance_fee, electricity_included, gas_included, water_included, internet_included, tv_included, has_system_aircon, has_wall_aircon, has_standing_aircon, has_bed, has_desk, has_wardrobe, has_built_in_closet, has_dining_table, has_sofa, has_shoe_cabinet, has_fridge, has_washing_machine, has_dryer, has_shower_booth, has_bathtub, has_bidet, has_sink, has_dishwasher, has_gas_stove, has_induction_stove, has_veranda, has_private_security, has_video_phone, has_intercom, has_cctv, has_security_window, has_door_security, has_unmanned_delivery_box, has_elevator, has_terrace, has_garden, approval_date, last_modified_date = row
            
            # 카테고리2 열의 값이 있다면 태그로 추가
            if detail_address and '동' in detail_address:
                if '동' in detail_address:
                    parts = detail_address.split(' ')
                    parts = parts[1].replace("(", "").replace(")", "").split('동')
                    text = parts[0] + '동'
                    tags.append(text)
            if floor_number:
                tags.append(f"{floor_number}층")
            if category2:
                tags.append(category2)
            if direction_name:
                tags.append(direction_name)
            if area_pyeong:
                tags.append(f"{int(round(area_pyeong))}평")
            if number_of_rooms:
                tags.append(f"{number_of_rooms}룸")
            if number_of_bathrooms and number_of_bathrooms > 1:
                tags.append(f"{number_of_bathrooms}욕실")
            if lease_price and lease_price > 0:  # 전세가
                tags.append('전세')
            elif monthly_rent and monthly_rent > 0:  # 월세가
                tags.append('월세')
            if loan_amount and premium_amount and bond_amount:  # 융자, 권리금, 채권
                if (type(loan_amount) == int and type(premium_amount) == int and type(bond_amount) == int and loan_amount + premium_amount + bond_amount == 0):
                    tags.append('담보 없음')
            if parking_available and parking_available == 1:
                tags.append('주차 가능')
            if heating_type:
                tags.append(heating_type)
            if maintenance_fee or electricity_included or gas_included or water_included or internet_included or tv_included:
                sum = 0
                for cost in [maintenance_fee, electricity_included, gas_included, water_included, internet_included, tv_included]:
                    if type(cost) == int:
                        sum += cost
                if sum > 0:
                    tags.append('관리비 별도')
                else:
                    tags.append('관리비 포함')
            if has_system_aircon or has_wall_aircon or has_standing_aircon:
                tags.append('에어컨')
            if has_bed and has_bed == 1:
                tags.append('침대')
            if has_desk and has_desk == 1:
                tags.append('책상')
            if has_wardrobe and has_wardrobe == 1:
                tags.append('옷장')
            if has_built_in_closet and has_built_in_closet == 1:
                tags.append('붙박이장')
            if has_dining_table and has_dining_table == 1:
                tags.append('식탁')
            if has_sofa and has_sofa == 1:
                tags.append('소파')
            if has_shoe_cabinet and has_shoe_cabinet == 1:
                tags.append('신발장')
            if has_fridge and has_fridge == 1:
                tags.append('냉장고')
            if has_washing_machine and has_washing_machine == 1:
                tags.append('세탁기')
            if has_dryer and has_dryer == 1:
                tags.append('건조기')
            if has_shower_booth and has_shower_booth == 1:
                tags.append('샤워부스')
            if has_bathtub and has_bathtub == 1:
                tags.append('욕조')
            if has_bidet and has_bidet == 1:
                tags.append('비데')
            if has_sink and has_sink == 1:
                tags.append('싱크대')
            if has_dishwasher and has_dishwasher == 1:
                tags.append('식기세척기')
            if has_gas_stove and has_gas_stove == 1:
                tags.append('가스레인지')
            if has_induction_stove and has_induction_stove == 1:
                tags.append('인덕션레인지')
            if has_veranda and has_veranda == 1:
                tags.append('베란다')
            if has_private_security and has_private_security == 1:
                tags.append('자체경비원')
            if has_video_phone and has_video_phone == 1:
                tags.append('비디오전화')
            if has_intercom and has_intercom == 1:
                tags.append('인터폰')
            if has_cctv and has_cctv == 1:
                tags.append('cctv')
            if has_security_window and has_security_window == 1:
                tags.append('방범창')
            if has_door_security and has_door_security == 1:
                tags.append('현관보안')
            if has_unmanned_delivery_box and has_unmanned_delivery_box == 1:
                tags.append('무인택배박스')
            if has_elevator and has_elevator == 1:
                tags.append('엘리베이터')
            if has_terrace and has_terrace == 1:
                tags.append('테라스')
            if has_garden and has_garden == 1:
                tags.append('마당')
            if approval_date and int(approval_date) > 20220101:
                tags.append('신축')
            if move_in_date == '즉시입주':
                tags.append('즉시입주')
        return tags

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error: {e}")
        traceback.print_exc()
        
def process_single_ad(product_ad, secrets):
    conn = None
    try:
        conn = connect_db(secrets)
        cursor = conn.cursor()
        # 2. assign_tag 함수를 사용하여 키워드 추출
        product_id, listing_serial_number, ad_description = product_ad
        tags_1 = assign_tag(listing_serial_number, conn, cursor)
        try:
            if ad_description is None:
                tags = tags_1
            else:
                tags_2 = clear_keywords(ad_description, secrets)
            if tags_2 == "없음" or tags_2 == "아무 답변도 내놓지 않습니다.":
                tags = tags_1
            else:
                # 문자열을 리스트로 변환
                tags_2_list = tags_2.split(', ')
                # 중복을 제거하고 합치기
                tags = list(set(tags_1).union(tags_2_list))
                print(tags)
                
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            tags = tags_1        

        # 3. 'dataAnalyze_tag 테이블에 태그 추가 
        tag_ids = []
        for tag in tags:
            # 중복된 tag가 있는지 확인
            cursor.execute('SELECT id FROM dataAnalyze_tag_detail WHERE tagName = %s', (tag,))
            result = cursor.fetchone()  
            if result:
                # 중복된 tag가 있으면 해당 tag_id를 가져옴
                tag_id = result[0]
            else:
                # 중복된 tag가 없으면 새로운 tag를 삽입하고 tag_id를 가져옴
                cursor.execute('INSERT INTO dataAnalyze_tag_detail (tagName) VALUES (%s)', (tag,))
                tag_id = cursor.lastrowid

            tag_ids.append(tag_id)

        # 4. `dataAnalyze_productTag_detail` 테이블에 `id` 및 `tag` 추가
        for tag_id in tag_ids:
            cursor.execute('INSERT INTO dataAnalyze_productTag_detail (product_detail_id, tagId_id) VALUES (%s, %s)', (product_id, tag_id))

        conn.commit()
    except Exception as e:
        print(f"Transaction failed: {e}")
        traceback.print_exc()
    finally:
        if conn:
            conn.close()
        
def detail_and_save_data(room_data, listing_serial_number, conn, cursor):
# MySQL에서는 INTEGER PRIMARY KEY AUTOINCREMENT 대신 INT AUTO_INCREMENT PRIMARY KEY 사용
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dataAnalyze_ProductKB_detail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    매물일련번호 INT,
    단지기본일련번호 INT,
    매물명 TEXT,
    매물도로기본주소 TEXT,
    매물도로상세주소 TEXT,
    해당층수 INT,
    카테고리1 TEXT,
    카테고리2 TEXT,
    지하구분 TEXT,
    지하층수 TEXT,
    총지상층수 INT,
    방향명 TEXT,
    공급면적 REAL,
    전용면적 REAL,
    연면적 REAL,
    대지면적 REAL,
    건축면적 REAL,
    공급면적평 REAL,
    전용면적평 REAL,
    방수 INT,
    욕실수 INT,
    현관구조내용 TEXT,
    입주가능일내용 TEXT,
    입주가능일협의여부 TEXT,
    매매가 INT,
    전세가 INT,
    월세가 INT,
    월세보증금 INT,
    융자금액 INT,
    보증금총액 INT,
    월세금총액 INT,
    기전세금액 INT,
    기월세액 INT,
    전세전환시금액 INT,
    옵션금액 INT,
    분양가 INT,
    권리금액 INT,
    채권금액 INT,
    특징광고내용 TEXT,
    물건특징내용 TEXT,
    제휴중개업소명 TEXT,
    매물주차가능여부 TEXT,
    매물주차대수 INT,
    세대당주차대수비율 REAL,
    난방방식명 TEXT,
    내진설계여부 TEXT,
    방거실형태명 TEXT,
    원룸구조명 TEXT,
    관리비 INT,
    관리비_전기세여부 INT,
    관리비_가스여부 INT,
    관리비_수도여부 INT,
    관리비_인터넷여부 INT,
    관리비_tv여부 INT,
    시스템에어컨여부 INT,
    벽걸이에어컨여부 INT,
    입식에어컨여부 INT,
    침대여부 INT,
    책상여부 INT,
    옷장여부 INT,
    붙박이장여부 INT,
    식탁여부 INT,
    소파여부 INT,
    신발장여부 INT,
    냉장고여부 INT,
    세탁기여부 INT,
    건조기여부 INT,
    샤워부스여부 INT,
    욕조여부 INT,
    비데여부 INT,
    싱크대여부 INT,
    식기세척기여부 INT,
    가스레인지여부 INT,
    인덕션레인지여부 INT,
    베란다여부 INT,
    자체경비원여부 INT,
    비디오전화여부 INT,
    인터폰여부 INT,
    cctv여부 INT,
    방범창여부 INT,
    현관보안여부 INT,
    무인택배박스여부 INT,
    엘리베이터여부 INT,
    테라스여부 INT,
    마당여부 INT,
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
            traceback.print_exc()
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
                매물주차대수, 세대당주차대수비율, 난방방식명, 내진설계여부, 방거실형태명,
                원룸구조명, 관리비, 관리비_전기세여부, 관리비_가스여부, 관리비_수도여부,
                관리비_인터넷여부, 관리비_tv여부, 시스템에어컨여부, 벽걸이에어컨여부, 입식에어컨여부,
                침대여부, 책상여부, 옷장여부, 붙박이장여부, 식탁여부,
                소파여부, 신발장여부, 냉장고여부, 세탁기여부, 건조기여부,
                샤워부스여부, 욕조여부, 비데여부, 싱크대여부, 식기세척기여부,
                가스레인지여부, 인덕션레인지여부, 베란다여부, 자체경비원여부, 비디오전화여부,
                인터폰여부, cctv여부, 방범창여부, 현관보안여부, 무인택배박스여부,
                엘리베이터여부, 테라스여부, 마당여부, 사용승인일, 수정일시
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''',(
            item.get('매물일련번호', None), 
            item.get('단지기본일련번호', None), 
            item.get('매물명', None),
            item.get('매물도로기본주소', None), 
            item.get('매물도로상세주소', None), 
            item.get('해당층수', None),
            item.get('카테고리1', None), 
            item.get('카테고리2', None), 
            item.get('지하구분', None),
            item.get('지하층수', None), 
            item.get('총지상층수', None), 
            item.get('방향명', None),
            item.get('공급면적', None), 
            item.get('전용면적', None), 
            item.get('연면적', None),
            item.get('대지면적', None), 
            item.get('건축면적', None), 
            item.get('공급면적평', None),
            item.get('전용면적평', None), 
            item.get('방수', None), 
            item.get('욕실수', None),
            item.get('현관구조내용', None), 
            item.get('입주가능일내용', None), 
            item.get('입주가능일협의여부', None),
            item.get('매매가', None), 
            item.get('전세가', None), 
            item.get('월세가', None),
            item.get('월세보증금', None), 
            item.get('융자금액', None), 
            item.get('보증금총액', None),
            item.get('월세금총액', None), 
            item.get('기전세금액', None), 
            item.get('기월세액', None),
            item.get('전세전환시금액', None), 
            item.get('옵션금액', None), 
            item.get('분양가', None),
            item.get('권리금액', None), 
            item.get('채권금액', None), 
            item.get('특징광고내용', None),
            item.get('물건특징내용', None), 
            item.get('제휴중개업소명', None), 
            item.get('매물주차가능여부', None),
            item.get('매물주차대수', None), 
            item.get('세대당주차대수비율', None), 
            item.get('난방방식명', None),
            item.get('내진설계여부', None), 
            item.get('방거실형태명', None), 
            item.get('원룸구조명', None),
            management_costs.get("관리비", None), 
            management_costs.get("관리비_전기세여부", None),
            management_costs.get("관리비_가스여부", None), 
            management_costs.get("관리비_수도여부", None),
            management_costs.get("관리비_인터넷여부", None), 
            management_costs.get("관리비_tv여부", None),
            options.get("시스템에어컨여부", None), 
            options.get("벽걸이에어컨여부", None),
            options.get("입식에어컨여부", None), 
            options.get("침대여부", None), 
            options.get("책상여부", None),
            options.get("옷장여부", None), 
            options.get("붙박이장여부", None), 
            options.get("식탁여부", None),
            options.get("소파여부", None), 
            options.get("신발장여부", None), 
            options.get("냉장고여부", None),
            options.get("세탁기여부", None), 
            options.get("건조기여부", None), 
            options.get("샤워부스여부", None),
            options.get("욕조여부", None), 
            options.get("비데여부", None), 
            options.get("싱크대여부", None),
            options.get("식기세척기여부", None), 
            options.get("가스레인지여부", None),
            options.get("인덕션레인지여부", None), 
            options.get("베란다여부", None),
            options.get("자체경비원여부", None), 
            options.get("비디오전화여부", None),
            options.get("인터폰여부", None), 
            options.get("cctv여부", None), 
            options.get("방범창여부", None),
            options.get("현관보안여부", None), 
            options.get("무인택배박스여부", None),
            options.get("엘리베이터여부", None), 
            options.get("테라스여부", None), 
            options.get("마당여부", None),
            item.get('사용승인일', None), 
            item.get('수정일시', None)
        ))
        conn.commit()
        
    except Exception as e:
        if conn:
            conn.rollback()
            print(f"Transaction failed: {e}")
            traceback.print_exc()
            fail_list.append(listing_serial_number)

def get_listing_serial_number(conn, cursor):
# 데이터베이스에서 listing_serial_number 열의 모든 데이터를 가져옴
    cursor.execute('SELECT listing_serial_number FROM dataAnalyze_productKB')
    result = cursor.fetchall()
    # 결과를 리스트로 변환
    listing_serial_numbers = [row[0] for row in result]

    return listing_serial_numbers