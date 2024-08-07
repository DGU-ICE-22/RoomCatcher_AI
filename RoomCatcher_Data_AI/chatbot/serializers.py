from rest_framework import serializers
from .chatbot import Chatbot
from .common import model
from .characters import system_role, instruction

class ChatRequestSerializer(serializers.Serializer):
    request_message = serializers.CharField(required=False, allow_blank=True)
    chatbot = serializers.JSONField(required=False)
    user_name = serializers.CharField(required=False)
    
    def create(self, validated_data):
        chatbot_data = validated_data.get('chatbot', None)
        if chatbot_data:
            chatbot = Chatbot.from_dict(chatbot_data)
            request_message = validated_data.get('request_message', "안녕!")
            print("exist")
        else:
            chatbot = Chatbot(
                model=model.basic,
                system_role=system_role,
                instruction=instruction
            )
            user_name = validated_data.get('user_name', '사용자')
            first_message = {
                "choices": [{
                    "message": {
                        "role": "system",
                        "content": f"{user_name}님, 만나서 반가워요! 제가 {user_name}님께 맞는 유형의 집을 찾아드리고 싶어요☺️"
                    }
                }]
            }
            second_message = {
                "choices": [{
                    "message": {
                        "role": "system",
                        "content": f"저와 자연스레 대화하다보면 {user_name}님에게 딱 맞는 집을 찾으실 수 있으실거에요!"
                    }
                }]
            }
            request_message = "안녕!"
            chatbot.add_response(first_message)
            chatbot.add_response(second_message)
        chatbot.add_user_message(request_message)
        response = chatbot.send_request()
        chatbot.add_response(response)
        response_message = chatbot.get_response_content()
        chatbot.handle_token_limit(response)
        chatbot.clean_context()  # instruction을 지우는 역할을 함. 
        
        if "사용자님의 부동산 소비 유형을 알려드리기 위해 분석 중이에요!" in response_message:
            return {
                'response_message': response_message,
                'chatbot': None
            }
        print("check")
        return {
            'response_message': response_message,
            'chatbot': chatbot.to_dict()
        }