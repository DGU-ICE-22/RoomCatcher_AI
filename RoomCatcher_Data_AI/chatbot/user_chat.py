# 필요한 라이브러리 설치
# pip install nltk transformers

import nltk
from transformers import pipeline

# nltk 데이터 다운로드
nltk.download('punkt')

class ChatBot:
    def __init__(self):
        self.question_generator = pipeline('text-generation', model='gpt-4o')
        self.history = []

    def get_response(self, user_input):
        self.history.append(user_input)
        response = self.generate_question(user_input)
        return response

    def generate_question(self, user_input):
        # 간단한 질문 생성 로직
        prompt = f"User: {user_input}\nBot:"
        generated_text = self.question_generator(prompt, max_length=50, num_return_sequences=1)[0]['generated_text']
        question = generated_text.split('User:')[-1].split('Bot:')[-1].strip()
        return question

if __name__ == "__main__":
    chatbot = ChatBot()
    print("챗봇과 대화를 시작하세요. 종료하려면 'exit'를 입력하세요.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        response = chatbot.get_response(user_input)
        print(f"Bot: {response}")