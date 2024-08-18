import json
from time import sleep
from django.core.exceptions import ImproperlyConfigured
import requests, os
from concurrent.futures import ThreadPoolExecutor, as_completed
    
def get_secret(setting, secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

def product_crawling_detail(listing_id, secrets):
        # 기본 URL
    base_url = "https://api.kbland.kr/land-property/property/dtailInfo"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    secret_file = os.path.join(base_dir, '..', '..','..','secret.json')

    with open(secret_file) as f:
        secrets = json.loads(f.read())
        
    # 결과 저장용 리스트
    results = []

    # 쿼리문에 매물일련번호값을 추가하여 URL 구성
    params = {
        '매물일련번호': listing_id
    }
    headers = get_secret('headersCrawling_kb', secrets)
    
    try:
        # GET 요청 보내기
        response = requests.get(base_url, headers=headers, params=params)
        
        # 요청이 성공적인지 확인
        response.raise_for_status()
        # 응답 데이터 처리 (예: JSON 데이터 파싱)
        data = response.json()
        results.append(data)  # 결과 저장
        return data
    
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data for serial number {listing_id}: {e}")
        return None
    
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    secret_file = os.path.join(base_dir, '..', '..', '..','secret.json')

    with open(secret_file) as f:
        secrets = json.loads(f.read())
    print(product_crawling_detail(127665083, secrets))