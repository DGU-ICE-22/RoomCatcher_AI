import csv
import json
import requests
import os 

# 요청 헤더 설정
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Referer": "https://www.dabangapp.com/search/map?filters=%7B%22multi_room_type%22%3A%5B0%2C1%2C2%5D%2C%22selling_type%22%3A%5B0%2C1%5D%2C%22deposit_range%22%3A%5B0%2C999999%5D%2C%22price_range%22%3A%5B0%2C999999%5D%2C%22trade_range%22%3A%5B0%2C999999%5D%2C%22maintenance_cost_range%22%3A%5B0%2C999999%5D%2C%22room_size%22%3A%5B0%2C999999%5D%2C%22supply_space_range%22%3A%5B0%2C999999%5D%2C%22room_floor_multi%22%3A%5B1%2C2%2C3%2C4%2C5%2C6%2C7%2C-1%2C0%5D%2C%22division%22%3Afalse%2C%22duplex%22%3Afalse%2C%22room_type%22%3A%5B1%2C2%5D%2C%22use_approval_date_range%22%3A%5B0%2C999999%5D%2C%22parking_average_range%22%3A%5B0%2C999999%5D%2C%22household_num_range%22%3A%5B0%2C999999%5D%2C%22parking%22%3Afalse%2C%22short_lease%22%3Afalse%2C%22full_option%22%3Afalse%2C%22elevator%22%3Afalse%2C%22balcony%22%3Afalse%2C%22safety%22%3Afalse%2C%22pano%22%3Afalse%2C%22is_contract%22%3Afalse%2C%22deal_type%22%3A%5B0%2C1%5D%7D&position=%7B%22location%22%3A%5B%5B126.7398098%2C37.3487658%5D%2C%5B127.2891262%2C37.6396855%5D%5D%2C%22center%22%3A%5B127.01446798508894%2C37.494367328004216%5D%2C%22zoom%22%3A11%7D&search=%7B%22id%22%3A%22%22%2C%22type%22%3A%22%22%2C%22name%22%3A%22%22%7D&tab=all",
    "Connection": "keep-alive",
    "Pragma": "no-cache"
}

def get_rooms(page):
    url = (
        f"https://www.dabangapp.com/api/3/room/new-list/multi-room/bbox?api_version=3.0.1&call_type=web&filters=%7B%22multi_room_type%22%3A%5B0%2C1%2C2%5D%2C%22selling_type%22%3A%5B0%2C1%5D%2C%22deposit_range%22%3A%5B0%2C999999%5D%2C%22price_range%22%3A%5B0%2C999999%5D%2C%22trade_range%22%3A%5B0%2C999999%5D%2C%22maintenance_cost_range%22%3A%5B0%2C999999%5D%2C%22room_size%22%3A%5B0%2C999999%5D%2C%22supply_space_range%22%3A%5B0%2C999999%5D%2C%22room_floor_multi%22%3A%5B1%2C2%2C3%2C4%2C5%2C6%2C7%2C-1%2C0%5D%2C%22division%22%3Afalse%2C%22duplex%22%3Afalse%2C%22room_type%22%3A%5B1%2C2%5D%2C%22use_approval_date_range%22%3A%5B0%2C999999%5D%2C%22parking_average_range%22%3A%5B0%2C999999%5D%2C%22household_num_range%22%3A%5B0%2C999999%5D%2C%22parking%22%3Afalse%2C%22short_lease%22%3Afalse%2C%22full_option%22%3Afalse%2C%22elevator%22%3Afalse%2C%22balcony%22%3Afalse%2C%22safety%22%3Afalse%2C%22pano%22%3Afalse%2C%22is_contract%22%3Afalse%2C%22deal_type%22%3A%5B0%2C1%5D%7D&location=%5B%5B126.7398098%2C37.3487658%5D%2C%5B127.2891262%2C37.6396855%5D%5D&page={page}&version=1&zoom=11"
    )
    response = requests.get(url, headers=headers)
    return response.json()

room_list_result = []

page = 1
while True:
    data = get_rooms(page)
    if "rooms" in data:
        room_list_result.extend(data["rooms"])
        if not data.get("has_more"):
            break
    else:
        print(f"No 'rooms' key found in response for page {page}. Response: {data}")
        break
    page += 1

# 결과를 CSV 파일로 저장
with open('./results/room_lists.csv', mode='w', newline='', encoding='utf-8') as room_lists:
    room_writer = csv.writer(room_lists)
    room_writer.writerow(['id', 'room_type', 'selling_type', 'is_quick', 'price_title', 'location', 'is_contract', 'title', 'room_more_info', 'img_url', 'img_urls'])
    for index, room in enumerate(room_list_result, start=1):
        room_writer.writerow([
            index  ,
            room.get('room_type_str'), 
            room.get('selling_type_str'),
            room.get('is_quick'), 
            room.get('price_title'), 
            room.get('location'),
            room.get('is_contract'),
            room.get('title'),
            room.get('room_desc2'),
            room.get('img_url'),
            room.get('img_urls')         
        ])
        room_writer.writerow([])  # 빈 행 추가
        
