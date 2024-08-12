from django.shortcuts import render
import requests, json, os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from .characters import system_role, instruction
from chatbot.chatbot import Chatbot
from .common import model
from .serializers import ChatRequestSerializer

@method_decorator(csrf_exempt, name='dispatch')
class ChatApiView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = JSONParser().parse(request)  
            serializer = ChatRequestSerializer(data=data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                auth_info = request.META.get('HTTP_AUTHORIZATION', None)
                if not auth_info:
                    return JsonResponse({'error': 'Auth information is missing'}, status=400)
                
                session_key = f'chatbot_{auth_info}'
                user_name = validated_data.get('user_name', '사용자')

                if session_key in request.session:
                    chatbot = Chatbot.from_dict(request.session[session_key])
                    request_message = validated_data.get('request_message')

                else:
                    chatbot = Chatbot(
                        model=model.basic,
                        system_role=system_role,
                        instruction=instruction
                    )
                    request_message = "안녕!"
                    first_message = {
                        "choices": [{
                            "message": {
                                "role": "assistant",
                                "content": f"{user_name}님, 만나서 반가워요! 제가 {user_name}님께 맞는 유형의 집을 찾아드리고 싶어요☺️"
                            }
                        }]
                    }
                    second_message = {
                        "choices": [{
                            "message": {
                                "role": "assistant",
                                "content": f"저와 자연스레 대화하다보면 {user_name}님에게 딱 맞는 집을 찾으실 수 있으실거에요!"
                            }
                        }]
                    }
                    chatbot.add_response(first_message)
                    chatbot.add_response(second_message)
                
                
                chatbot.add_user_message(request_message)
                response = chatbot.send_request()
                chatbot.add_response(response)
                response_message = chatbot.get_response_content()
                
                chatbot.handle_token_limit(response)
                chatbot.clean_context()
                
                # 대화를 종료하는 특정 텍스트가 포함된 경우 세션에서 챗봇 인스턴스를 제거
                if "사용자님의 부동산 소비 유형을 알려드리기 위해 분석 중이에요!" in response_message:
                    # 이 시점에서 인스턴스(chatbot)에 남아있는 context 전부 긁어서 다른 API로 넘김. 
                    del request.session[session_key]
                else:
                    request.session[session_key] = chatbot.to_dict()
                
                return JsonResponse({"response_message": response_message,
                                     "chatbot": chatbot.to_dict()})
            else:
                return JsonResponse(serializer.errors, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)