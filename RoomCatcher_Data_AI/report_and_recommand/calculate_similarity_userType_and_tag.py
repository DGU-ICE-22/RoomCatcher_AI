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
from transformers import ElectraModel, ElectraTokenizer
import torch, numpy as np 
from sklearn.metrics.pairwise import cosine_similarity
from django.core.exceptions import ImproperlyConfigured
import numpy as np
from .common import connect_db

# KoELECTRA 모델과 토크나이저 로드
tokenizer = ElectraTokenizer.from_pretrained("monologg/koelectra-base-v3-discriminator")
model = ElectraModel.from_pretrained("monologg/koelectra-base-v3-discriminator")
def get_secret(setting, secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        traceback.print_exc()
        raise ImproperlyConfigured(error_msg)

def ensure_same_dimension(embedding, target_dim):
    # 임베딩의 차원이 target_dim과 다르면, 차원을 맞추는 함수
    current_dim = embedding.shape[0]
    if current_dim > target_dim:
        # 차원이 큰 경우 차원 축소 (앞에서 자름)
        return embedding[:target_dim]
    elif current_dim < target_dim:
        # 차원이 작은 경우 차원 확장 (0으로 패딩)
        return np.pad(embedding, (0, target_dim - current_dim), 'constant')
    return embedding

# 텍스트 임베딩 생성 함수
def get_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state[:, 0, :]
    return embeddings.squeeze().numpy()

# 유저 입력에 대한 임베딩 생성 함수
def get_user_input_embedding(user_input, client):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[user_input]
    )
    return np.array(response.data[0].embedding)

# 유저 입력을 받아와서 가장 유사한 태그들을 찾는 함수
def find_best_match_tags(user_input):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        secret_file = os.path.join(base_dir, '..', 'secret.json')

        with open(secret_file) as f:
            secrets = json.loads(f.read())

        client = openai.OpenAI(api_key=get_secret('OPENAI_API_KEY', secrets), timeout=30, max_retries=1)

        user_embedding = get_user_input_embedding(user_input, client)
        
        # 임베딩의 목표 차원 
        target_dim = 1536

        # 유저 임베딩 차원을 맞춤
        user_embedding = ensure_same_dimension(user_embedding, target_dim)
        
        # DB에서 tags들의 임베딩값을 가져옴
        conn = connect_db(secrets)
        cursor = conn.cursor()
        
        cursor.execute('SELECT tag_name, embedding FROM data_analyze_tag_detail')
        tags_embeddings = cursor.fetchall()
        
        # 임베딩을 numpy 배열로 변환하고 차원 맞춤
        embeddings = [ensure_same_dimension(np.frombuffer(embedding, dtype=np.float32), target_dim) for _, embedding in tags_embeddings]
        tags = [tag for tag, _ in tags_embeddings]
        
        # 모든 특징 유형 설명과 유저 입력 간의 유사도 계산
        similarities = cosine_similarity(user_embedding.reshape(1, -1), np.vstack(embeddings)).flatten()
        
        # 가장 높은 유사도를 가진 태그의 인덱스를 찾음
        sorted_indices = np.argsort(similarities)[::-1]
        
        return [tags[i] for i in sorted_indices] 
    
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None
    
# 태그와 사용자 유형 간의 유사도를 계산해서 해당 사용자 유형에서 가장 유사한 태그들을 순서대로 반환한다. 
def bring_tags_to_user_type(index):
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    secret_file = os.path.join(base_dir, '..', 'secret.json')

    with open(secret_file) as f:
        secrets = json.loads(f.read())
        
    conn = connect_db(secrets)
    cursor = conn.cursor()
    
    cursor.execute('''
                   SELECT embedding FROM report_and_recommand_user_type
                   ''')
    user_type_list_embedding = cursor.fetchall() 
    
    user_type_list_embedding = [np.frombuffer(embedding[0], dtype=np.float32) for embedding in user_type_list_embedding]
    
    try:
        cursor.execute("SELECT id, tag_name, embedding FROM data_analyze_tag_detail")
        tag_embeddings = {tagName: np.frombuffer(embedding, dtype=np.float32) for _, tagName, embedding in cursor.fetchall()}

        # User type embedding dimension (assuming all user type embeddings have the same dimension)
        user_type_dim = user_type_list_embedding[0].shape[0]

        # Adjust all tag embeddings to have the same dimension as user type embeddings
        tag_embeddings = {tag: ensure_same_dimension(embedding, user_type_dim) for tag, embedding in tag_embeddings.items()}
        
        sorted_tags = sorted(tag_embeddings.keys(), 
                             key=lambda tag: 
                                 cosine_similarity(tag_embeddings[tag].reshape(1, -1),
                                                   user_type_list_embedding[index].reshape(1, -1)).flatten()[0],
                             reverse=True)
        
        return sorted_tags[:int(len(sorted_tags)/8)]
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None
    
def select_best_index(index_list, index_list_v2):
    # 두 리스트의 길이
    len_index_list = len(index_list)
    len_index_list_v2 = len(index_list_v2)

    # 점수를 저장할 딕셔너리 초기화
    scores = {}

    # index_list에 대해 점수를 매김
    for i, index in enumerate(index_list):
        # index_list의 순서에 따라 점수를 매김 (0에 가까울수록 높은 점수)
        score = len_index_list - i
        if index in scores:
            scores[index] += score
        else:
            scores[index] = score

    # index_list_v2에 대해 점수를 매김
    for i, index in enumerate(index_list_v2):
        # index_list_v2의 순서에 따라 점수를 매김 (0에 가까울수록 높은 점수)
        score = len_index_list_v2 - i
        if index in scores:
            scores[index] += score
        else:
            scores[index] = score

    # 가장 높은 점수를 가진 인덱스를 반환
    best_index = max(scores, key=scores.get)
    return best_index
    
# 유저 입력을 받아와서 가장 유사한 유형을 찾는 함수
def find_best_match_type(user_input, user_type_list):
    
    #OpenAI API를 사용한 유사도 계산
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        secret_file = os.path.join(base_dir, '..', 'secret.json')

        with open(secret_file) as f:
            secrets = json.loads(f.read())

        client = openai.OpenAI(api_key=get_secret('OPENAI_API_KEY', secrets), timeout=30, max_retries=1)

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
        sorted_indices = np.argsort(similarities)[::-1]
        
        return similarities, sorted_indices 
    
    except Exception as e:
        
        print(e)
        traceback.print_exc()
        return None, None
    
    # # KoELECTRA를 사용한 유사도 계산
    # try:
    #     characteristic_embeddings = [get_embedding(user_type) for user_type in user_type_list]
    #     user_embedding = get_embedding(user_input)
        
    #     similarities = cosine_similarity(user_embedding.reshape(1, -1), characteristic_embeddings).flatten()
    #     best_match_index = np.argmax(similarities)
    #     print(similarities)
    #     return best_match_index, float(similarities[best_match_index])
    
    # except Exception as e:
    #     print(e)
    #     traceback.print_exc()
    #     return None, None
    
# from type_explain import type_1_money, type_2_option, type_3_structure, type_4_transport, type_5_nature, type_6_emotion, type_7_business, type_8_student

# user_type_list = [type_1_money, type_2_option, type_3_structure, type_4_transport, type_5_nature, type_6_emotion, type_7_business, type_8_student]

# print(find_best_match(user_input="나는 충무로역 근처의 집을 원해. 월세는 상관없는데 옵션 가구들이 많았으면 좋겠고 지하철역이 하나정도 있었으면 좋겠어.", user_type_list=user_type_list))\
if __name__ == '__main__':
    find_best_match_tags("나는 충무로역 근처의 집을 원해. 월세는 상관없는데 옵션 가구들이 많았으면 좋겠고 지하철역이 하나정도 있었으면 좋겠어.")    