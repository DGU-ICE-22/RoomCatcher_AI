import json
import requests
import transpose_location_to_address
def get_rooms(page, headers):
        url = (
            f"https://www.dabangapp.com/api/3/room/new-list/multi-room/bbox?api_version=3.0.1&call_type=web&filters=%7B%22multi_room_type%22%3A%5B0%2C1%2C2%5D%2C%22selling_type%22%3A%5B0%2C1%5D%2C%22deposit_range%22%3A%5B0%2C999999%5D%2C%22price_range%22%3A%5B0%2C999999%5D%2C%22trade_range%22%3A%5B0%2C999999%5D%2C%22maintenance_cost_range%22%3A%5B0%2C999999%5D%2C%22room_size%22%3A%5B0%2C999999%5D%2C%22supply_space_range%22%3A%5B0%2C999999%5D%2C%22room_floor_multi%22%3A%5B1%2C2%2C3%2C4%2C5%2C6%2C7%2C-1%2C0%5D%2C%22division%22%3Afalse%2C%22duplex%22%3Afalse%2C%22room_type%22%3A%5B1%2C2%5D%2C%22use_approval_date_range%22%3A%5B0%2C999999%5D%2C%22parking_average_range%22%3A%5B0%2C999999%5D%2C%22household_num_range%22%3A%5B0%2C999999%5D%2C%22parking%22%3Afalse%2C%22short_lease%22%3Afalse%2C%22full_option%22%3Afalse%2C%22elevator%22%3Afalse%2C%22balcony%22%3Afalse%2C%22safety%22%3Afalse%2C%22pano%22%3Afalse%2C%22is_contract%22%3Afalse%2C%22deal_type%22%3A%5B0%2C1%5D%7D&location=%5B%5B126.7398098%2C37.3487658%5D%2C%5B127.2891262%2C37.6396855%5D%5D&page={page}&version=1&zoom=11"
        )
        response = requests.get(url, headers=headers)
        return response.json()
    
def product_crawling(secrets):
    # 요청 헤더 설정
    headers = transpose_location_to_address.get_secret('headersCrawling', secrets)

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
        
if __name__ == "__main__":
    product_crawling()