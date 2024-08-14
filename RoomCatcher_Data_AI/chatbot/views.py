from django.shortcuts import render
from django.urls import reverse
import requests, json, os
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from .characters import system_role, instruction
from chatbot.chatbot import Chatbot
from .common import model
from .serializers import ChatRequestSerializer
from convert_to_plaintext import convert_to_plaintext
from type_explain import type_1_money, type_2_option, type_3_structure, type_4_transport, type_5_nature, type_6_emotion, type_7_business, type_8_student
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
                
                # chatbot.handle_token_limit(response)      얘 때문에 자꾸 챗봇이 대화 마무리를 못하는 것 같음. 
                chatbot.clean_context()
                
                # 대화를 종료하는 특정 텍스트가 포함된 경우 세션에서 챗봇 인스턴스를 제거
                if "사용자님의 부동산 소비 유형을 알려드리기 위해 분석 중이에요!" in response_message:
                    # 이 시점에서 인스턴스(chatbot)에 남아있는 context 전부 긁어서 다른 API로 넘김. 
                    context_list = response.get('chatbot', {}).get('context', [])
                # 'context' 리스트를 순회하며 'role'이 'user'인 항목을 평문으로 변환
                    for item in context_list:
                        if item.get('role') == 'user':
                            # 여기서 평문으로 변환하는 로직을 추가
                            # 예를 들어, 'content' 필드를 평문으로 변환
                            item['content'] = convert_to_plaintext(item['content'])
                    del request.session[session_key]
                    return HttpResponseRedirect(reverse('chatbot_get'))
                else:
                    request.session[session_key] = chatbot.to_dict()
                
                return JsonResponse({"response_message": response_message,
                                     "chatbot": chatbot.to_dict()})
            else:
                return JsonResponse(serializer.errors, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def get(self, request, *args, **kwargs):
# - response[’chatbot’][context’][’role’] == “user” 인 응답들을 평문으로 바꿈.
# - 평문으로 바꾼 문장과 사용자 유형 문장들을 유사도 분석하여 가장 유사도가 높은 유형을 보여준다.
# - 평문으로 바꾼 문장과 DB의 키워드를 유사도 분석
#     - 키워드들을 보고 챗봇을 좀 더 자세하게 만들어야 함.
# - tag DB에서 가장 유사한 태그 n개를 뽑아냄.
# - 이 태그 n개를 사용자 유형 페이지에 같이 줌.
# - 맞춤 매물 검색을 누른다면 그 태그를 가장 많이 가지고 있고 특정 개수 이상 태그를 가지고 있는 매물들을 가져옴.
#     - 태그를 실시간으로 삭제, 추가해서 조회하면 바로 DB에서 가져올 수 있게 설정.

        try:
            data = JSONParser().parse(request)  
            user_type_list = [type_1_money, type_2_option, type_3_structure, type_4_transport, type_5_nature, type_6_emotion, type_7_business, type_8_student]

            for user_type in user_type_list:
             #    data['content']와 user_type를 유사도 분석 후 가장 높은 유형을 보여줌.
                pass
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)