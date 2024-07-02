import pandas as pd
import requests
import os 
import json
from django.core.exceptions import ImproperlyConfigured

base_dir = os.path.dirname(os.path.abspath(__file__))
input_file_path = os.path.join(base_dir, '..', 'results', 'room_lists.csv')
output_file_path = os.path.join(base_dir, '..', 'results', 'room_lists_with_address.csv')
secret_file = os.path.join(base_dir, '..', '..','secret.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

# CSV 파일 읽기
room_data = pd.read_csv(input_file_path)

#API 키 설정
API_KEY = get_secret('API_KEY')

# 주소 변환 함수
def get_address_from_coordinates(x, y):
    url = f'https://api.vworld.kr/req/address?service=address&request=getAddress&version=2.0&crs=epsg:4326&point={x},{y}&format=json&type=both&zipcode=true&simple=false&key={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['response']['status'] == 'OK':
            return data['response']['result'][0]['text']
    return None

# 주소 열 추가
addresses = []
for index, row in room_data.iterrows():
    location = eval(row['location'])
    x, y = location[0], location[1]
    address = get_address_from_coordinates(x, y)
    addresses.append(address)

room_data['address'] = addresses

# 새로운 CSV 파일로 저장
room_data.to_csv(output_file_path, index=False, encoding='utf-8')

print("CSV 파일이 성공적으로 저장되었습니다.")