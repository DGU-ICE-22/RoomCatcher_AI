import json
from time import sleep
from django.core.exceptions import ImproperlyConfigured
import requests, os
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_rooms(headers):
        # kb 부동산 url
        url = f"https://api.kbland.kr/land-property/propList/filter"
        response = requests.post(url, headers=headers)
        return response.json()
    
def get_secret(setting, secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)
    
def product_crawling(cluster_id, secrets):
    url = "https://api.kbland.kr/land-property/propList/filter"
    headers = get_secret('headersCrawling_kb', secrets)

    data = {
        "endLat": 37.7013,  # 서울의 북동쪽 끝 위도
        "endLng": 127.1838,  # 서울의 북동쪽 끝 경도
        "honeyYn": "0",
        "selectCode": "1,2,3",
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

def extract_enable_clusterId(secret, cluster_ids, mode=False, start=0, end=0):
    if mode:
        cluster_ids = range(start, end)
    all_data = []
    result_ids = []
    for cluster_id in cluster_ids:
        data = product_crawling(str(cluster_id), secret)
        if data and data["dataBody"]["resultCode"] != 30500 and data["dataBody"]["resultCode"] != 30210:
            all_data.append(data)
            result_ids.append(cluster_id)
    if mode:
        # 먼저 파일의 현재 내용을 읽어서 기존에 있는 ID인지 확인
        with open("cluster_ids.txt", "r") as file:
            existing_ids = file.readlines()
        for cluster_id in result_ids:
            # 현재 result_id가 파일에 없는 경우에만 추가
            if f"{cluster_id}\n" not in existing_ids:
                with open("cluster_ids.txt", "a") as file:
                    file.write(f"{cluster_id}\n")
        
    return all_data

def product_crawling_v2(secret):
    # txt 파일에서 클러스터 ID 리스트를 읽어옴
    with open("cluster_ids.txt", "r") as file:
        num_list = [int(line.strip()) for line in file.readlines()]
        
    #mode가 True이면 사용 가능한 클러스터 ID를 txt 파일에 저장. 뒤의 숫자들은 범위를 찾고자 하는 id의 범위를 나타냄.
    data = extract_enable_clusterId(secret, num_list, False, 5102231000, 5102232000)
    
    return(data)
    
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    secret_file = os.path.join(base_dir, '..', '..','secret.json')

    with open(secret_file) as f:
        secrets = json.loads(f.read())
    print(product_crawling_v2(secrets))