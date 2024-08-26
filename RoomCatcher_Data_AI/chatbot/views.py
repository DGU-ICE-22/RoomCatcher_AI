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
import hashlib
@method_decorator(csrf_exempt, name='dispatch')
class ChatApiView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = JSONParser().parse(request)  
            serializer = ChatRequestSerializer(data=data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                auth_info = request.META.get('HTTP_AUTHORIZATION', None)
                if not auth_info or not auth_info.startswith('Bearer '):
                    auth_info = request.headers.get('Authorization', None)
                    if not auth_info and not auth_info.startswith('Bearer ') and not request.headers.get('Authorization'):
                        return JsonResponse({'error': 'Auth information is missing or invalid'}, status=400)
                    token = auth_info
                else:
                    # Bearer 토큰에서 접두사 제거
                    token = auth_info.split(' ')[1]
                    
                print(auth_info)

                
                
                # 토큰을 해싱하여 세션 키 생성
                session_key = f'chatbot_{hashlib.sha256(token.encode()).hexdigest()}'
                print(request.session.keys())
                print(session_key in request.session)
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
                    context_list = chatbot.context
                    # 'context' 리스트를 순회하며 'role'이 'user'인 항목을 평문으로 변환
                    content = [item['content'] for item in context_list if item['role'] == 'user']

                    # 이걸 다른 API로 넘겨서 사용자 유형을 분석하고, 그 결과를 다시 챗봇에 넣어서 보여줄 지 아니면 다른 방식으로 보여줄 지 결정해야 함.
                    params = {'content': content}
                    print(params)
                    # Report 앱의 CBV에 GET 요청 보내기
                    report_url = reverse('report_view')
                    report_response = requests.get(request.build_absolute_uri(report_url), params=params)
                    if report_response.status_code == 200:
                        report_data = report_response.json()
                        del request.session[session_key]

                        # report_data를 사용하여 추가 로직을 구현할 수 있습니다.
                    else :
                        report_data = None
                        print(report_response.json())
                    return JsonResponse({"response_message": response_message,
                                        "chatbot": chatbot.to_dict(),
                                        "report_data": report_data
                                        })
                else:
                    request.session[session_key] = chatbot.to_dict()
                    request.session.modified = True  # 세션이 수정되었음을 Django에 알립니다.
                    request.session.save()

                print("request", request.session.keys())
                print(session_key in request.session)
                return JsonResponse({"response_message": response_message,
                                     "chatbot": chatbot.to_dict(),
                                     "report_data": None
                                     })
            else:
                return JsonResponse(serializer.errors, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)