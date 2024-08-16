import json
import os
import traceback
from openai import OpenAI
from django.core.exceptions import ImproperlyConfigured

def get_secret(setting, secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        traceback.print_exc()
        raise ImproperlyConfigured(error_msg)
    
def convert_to_plaintext(content):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        secret_file = os.path.join(base_dir, '..', '..', 'secret.json')

        with open(secret_file) as f:
            secrets = json.loads(f.read())
            
        user_messages = [{"role": "user", "content": sentence} for sentence in content]

        client = OpenAI(api_key=get_secret('OPENAI_API_KEY', secrets))
        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": "너는 들어온 문장을 토대로 해당 문장들을 평문으로 만들어주고 들어온 문장을 토대로 사용자의 성격 유형을 알려줘야 해. 들어오는 문장 유형은 사용자의 응답을 차례대로 줄거야. 이 리스트 안에 있는 텍스트들을 모아 평문으로 만드는데, 주의할 점이 있어.\n[!IMPORTANT]평문으로 만든 문장은 부동산과 관련한 성격 유형 설명과 유사도 검사하기에 적합해야 함. 예를 들어, 부동산과 전혀 관계가 없는 오늘 날씨가 좋아서 기분이 좋아! 와 같은 문장은 평문으로 만들지 않을 것.\n또한, 말투는 존댓말을 사용하고 응답 내용에는 다음과 같은 내용이 들어가도록 해야 해. \n1. 사용자가 선호하는 부동산의 특징(전세, 월세, 매매 등)과 사용자의 예산 혹은 원하는 금액 등이 들어가야 한다.\n2. 사용자가 원하는 가구나 집의 크기, 구조와 같은 내용이 들어가야 한다. \n3. 사용자가 집에 대해 구체적으로 원하는 내용들이 들어가야 한다.\n4. 사용자가 원하는 교통 편의성들에 대한 내용이 들어가야 한다. \n5. 사용자의 직업과 성격 유형이 들어가야 한다. "
                }
            ]
            },
            *user_messages
        ],
        temperature=0.30,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "text"
        }
        ).model_dump()

        return response
    except Exception as e:
        print(f"Failed to convert to plaintext: {e}")
        return None