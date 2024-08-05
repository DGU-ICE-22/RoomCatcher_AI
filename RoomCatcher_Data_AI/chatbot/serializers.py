from rest_framework import serializers
from .chatbot import Chatbot
from .common import model
from .characters import system_role, instruction

class ChatRequestSerializer(serializers.Serializer):
    request_message = serializers.CharField(required=True)
    chatbot = serializers.JSONField(required=False)
    
    def create(self, validated_data):
        chatbot_data = validated_data.get('chatbot')
        if chatbot_data:
            chatbot = Chatbot.from_dict(chatbot_data)
        else:
            chatbot = Chatbot(
                model = model.basic,
                system_role = system_role,
                instruction = instruction
            )
        request_message = validated_data['request_message']
        chatbot.add_user_message(request_message)
        response = chatbot.send_request()
        chatbot.add_response(response)
        response_message = chatbot.get_response_content()
        chatbot.handle_token_limit(response)
        chatbot.clean_context()
        return {
            'response_message': response_message,
            'chatbot': chatbot.to_dict()
        }