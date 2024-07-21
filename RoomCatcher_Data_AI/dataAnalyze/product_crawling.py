import json
from time import sleep
from django.core.exceptions import ImproperlyConfigured
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_rooms(page, headers):
        url = (
            f"https://www.dabangapp.com/api/3/room/new-list/multi-room/bbox?api_version=3.0.1&call_type=web&filters=%7B%22multi_room_type%22%3A%5B0%2C1%2C2%5D%2C%22selling_type%22%3A%5B0%2C1%5D%2C%22deposit_range%22%3A%5B0%2C999999%5D%2C%22price_range%22%3A%5B0%2C999999%5D%2C%22trade_range%22%3A%5B0%2C999999%5D%2C%22maintenance_cost_range%22%3A%5B0%2C999999%5D%2C%22room_size%22%3A%5B0%2C999999%5D%2C%22supply_space_range%22%3A%5B0%2C999999%5D%2C%22room_floor_multi%22%3A%5B1%2C2%2C3%2C4%2C5%2C6%2C7%2C-1%2C0%5D%2C%22division%22%3Afalse%2C%22duplex%22%3Afalse%2C%22room_type%22%3A%5B1%2C2%5D%2C%22use_approval_date_range%22%3A%5B0%2C999999%5D%2C%22parking_average_range%22%3A%5B0%2C999999%5D%2C%22household_num_range%22%3A%5B0%2C999999%5D%2C%22parking%22%3Afalse%2C%22short_lease%22%3Afalse%2C%22full_option%22%3Afalse%2C%22elevator%22%3Afalse%2C%22balcony%22%3Afalse%2C%22safety%22%3Afalse%2C%22pano%22%3Afalse%2C%22is_contract%22%3Afalse%2C%22deal_type%22%3A%5B0%2C1%5D%7D&location=%5B%5B126.7398098%2C37.3487658%5D%2C%5B127.2891262%2C37.6396855%5D%5D&page={page}&version=1&zoom=11"
        )
        response = requests.get(url, headers=headers)
        return response.json()
    
def get_secret(setting, secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)
    
def product_crawling(secrets):
    # 요청 헤더 설정
    headers = get_secret('headersCrawling', secrets)

    room_list_result = []

    page = 1
    while True:
        data = get_rooms(page, headers)
        #data example
        # {'seq': 44885607, 'id': '66820d51c939ee04cf59dac5', 'status': 1, 'room_type': 0, 'room_type_str': '원룸', 'selling_type_str': '월세', 'address': None, 'location': [126.786442313304, 37.4838940935949], 'random_location': [126.786441188063, 37.4840135406642], 'complex_name': None, 'title': '부천역세권', 'price_title': '500/35', 'confirm_type': None, 'confirm_date_str': None, 'img_url': 'https://d1774jszgerdmk.cloudfront.net/512/Tf0qT8pHeSHdwDBq-Ulm-', 'img_urls': ['https://d1774jszgerdmk.cloudfront.net/512/Tf0qT8pHeSHdwDBq-Ulm-', 'https://d1774jszgerdmk.cloudfront.net/512/VFDDK6IyQA-mHIQ5yFatx', 'https://d1774jszgerdmk.cloudfront.net/512/93lfNCTXqW3X0CR68LOSK', 'https://d1774jszgerdmk.cloudfront.net/512/z0n-FOCWT2ibdzFKysB1n'], 'is_extend_ui': False, 'is_favorited': None, 'is_sign_verified': False, 'is_contract': False, 'is_pano': False, 'is_quick': False, 'is_direct': False, 'deleted': False, 'selling_type': 0, 'is_owner': False, 'is_naver_verify': False, 'naver_verify_date_str': None, 'is_icon_focus': False, 'icon_focus_type': None, 'room_desc2': '3층, 17.22m², 관리비 없음'}
        if "rooms" in data:
            for room in data["rooms"]:
                room_data = [
                    room.get('room_type'), 
                    room.get('selling_type_str'),
                    room.get('is_quick'), 
                    room.get('price_title'), 
                    room.get('location'),
                    room.get('is_contract'),
                    room.get('title'),
                    room.get('room_desc2'),
                    room.get('img_url'),
                    room.get('img_urls')
                ]
                room_list_result.append((data["rooms"].index(room), room_data))            
            if not data.get("has_more"):
                break
        else:
            print(f"No 'rooms' key found in response for page {page}. Response: {data}")
            break
        page += 1
        
    return room_list_result
        
    
    # # 결과를 CSV 파일로 저장
    # with open('./results/room_lists.csv', mode='w', newline='', encoding='utf-8') as room_lists:
    #     room_writer = csv.writer(room_lists)
    #     room_writer.writerow(['id', 'room_type', 'selling_type', 'is_quick', 'price_title', 'location', 'is_contract', 'title', 'room_more_info', 'img_url', 'img_urls'])
    #     for index, room in enumerate(room_list_result, start=1):
    #         room_writer.writerow([
    #             index  ,
    #             room.get('room_type_str'), 
    #             room.get('selling_type_str'),
    #             room.get('is_quick'), 
    #             room.get('price_title'), 
    #             room.get('location'),
    #             room.get('is_contract'),
    #             room.get('title'),
    #             room.get('room_desc2'),
    #             room.get('img_url'),
    #             room.get('img_urls')         
    #         ])
    #         room_writer.writerow([])  # 빈 행 추가

def product_crawling_kb(cluster_id):
    url = "https://api.kbland.kr/land-property/propList/filter"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://kbland.kr",
        "Referer": "https://kbland.kr/",
        "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    data = {
        "endLat": 37.7013,  # 서울의 북동쪽 끝 위도
        "endLng": 127.1838,  # 서울의 북동쪽 끝 경도
        "honeyYn": "0",
        "selectCode": "2",
        "startLat": 37.4283,  # 서울의 남서쪽 끝 위도
        "startLng": 126.7647,  # 서울의 남서쪽 끝 경도
        "webCheck": "Y",
        "zoomLevel": 16,
        "거래유형": "2,3",
        "건폐율시작값": "",
        "건폐율종료값": "",
        "관리비시작값": "",
        "관리비종료값": "",
        "구조": "",
        "매매시작값": "",
        "매매전세차시작값": "",
        "매매전세차종료값": "",
        "매매종료값": "",
        "매물": "",
        "면적시작값": "",
        "면적종료값": "",
        "물건종류": "34,35",
        "방수": "",
        "보안옵션": "",
        "보증금시작값": "",
        "보증금종료값": "",
        "분양단지구분코드": "X",
        "분양진행단계코드": "S01,S11,S12",
        "사진있는매물순": True,
        "세대수시작값": "",
        "세대수종료값": "",
        "엘리베이터": "",
        "옵션": "",
        "욕실수": "",
        "용도지역": "",
        "용적률시작값": "",
        "용적률종료값": "",
        "월세수익률시작값": "",
        "월세수익률종료값": "",
        "월세시작값": "",
        "월세종료값": "",
        "융자금": "",
        "일반분양여부": "1,0",
        "전세가율시작값": "",
        "전세가율종료값": "",
        "전자계약여부": "0",
        "점포수시작값": "",
        "점포수종료값": "",
        "정렬타입": "date",
        "주차": "",
        "준공년도시작값": "",
        "준공년도종료값": "",
        "중복타입": "01",
        "지목": "",
        "지상층": "",
        "지하층": "",
        "추진현황": "",
        "클러스터식별자": cluster_id,
        "페이지목록수": 30,
        "페이지번호": 1
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve data for cluster {cluster_id}. Status code: {response.status_code}")
        return None

def main():
    cluster_ids = (range(5102230000, 5102240000))  # 클러스터 식별자 목록
    all_data = []
    result_ids = []
    for cluster_id in cluster_ids:
        data = product_crawling_kb(str(cluster_id))
        if data and data["dataBody"]["resultCode"]!=30500 and data["dataBody"]["resultCode"]!=30210:
            all_data.append(data)
            result_ids.append(cluster_id)
    # all_data를 처리하거나 파일로 저장하는 등의 작업을 수행
    print(all_data)
    print(result_ids)

if __name__ == "__main__":
    main()