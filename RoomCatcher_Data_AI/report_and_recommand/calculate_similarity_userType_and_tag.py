# - response[’chatbot’][context’][’role’] == “user” 인 응답들을 평문으로 바꿈.
# - 평문으로 바꾼 문장과 사용자 유형 문장들을 유사도 분석하여 가장 유사도가 높은 유형을 보여준다.
# - 평문으로 바꾼 문장과 DB의 키워드를 유사도 분석
#     - 키워드들을 보고 챗봇을 좀 더 자세하게 만들어야 함.
# - tag DB에서 가장 유사한 태그 n개를 뽑아냄.
# - 이 태그 n개를 사용자 유형 페이지에 같이 줌.
import json
import os
import traceback
import openai
from sklearn.metrics.pairwise import cosine_similarity
from django.core.exceptions import ImproperlyConfigured
import numpy as np

def get_secret(setting, secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        traceback.print_exc()
        raise ImproperlyConfigured(error_msg)

# 유저 입력에 대한 임베딩 생성 함수
def get_user_input_embedding(user_input, client):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[user_input]
    )
    return np.array(response.data[0].embedding)

    
# 유저 입력을 받아와서 가장 유사한 유형을 찾는 함수
def find_best_match(user_input, user_type_list):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        secret_file = os.path.join(base_dir, '..', '..', 'secret.json')

        with open(secret_file) as f:
            secrets = json.loads(f.read())

        client = openai.OpenAI(api_key=get_secret('OPENAI_API_KEY', secrets), timeout=30, max_retries=1)

        # 8가지 특징 유형 설명

        # 특징 유형 설명을 임베딩으로 변환
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=user_type_list
        )
        characteristic_embeddings = np.array([item.embedding for item in response.data])
        user_embedding = get_user_input_embedding(user_input, client)
        
        # 모든 특징 유형 설명과 유저 입력 간의 유사도 계산
        similarities = cosine_similarity(user_embedding.reshape(1, -1), characteristic_embeddings).flatten()
        
        # 가장 높은 유사도를 가진 유형의 인덱스를 찾음
        best_match_index = np.argmax(similarities)
        
        return best_match_index, similarities[best_match_index]
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None, None
# from type_explain import type_1_money, type_2_option, type_3_structure, type_4_transport, type_5_nature, type_6_emotion, type_7_business, type_8_student

# user_type_list = [type_1_money, type_2_option, type_3_structure, type_4_transport, type_5_nature, type_6_emotion, type_7_business, type_8_student]

# print(find_best_match(user_input="나는 충무로역 근처의 집을 원해. 월세는 상관없는데 옵션 가구들이 많았으면 좋겠고 지하철역이 하나정도 있었으면 좋겠어.", user_type_list=user_type_list))