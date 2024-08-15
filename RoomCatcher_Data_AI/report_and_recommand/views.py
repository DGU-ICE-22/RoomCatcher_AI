from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .calculate_similarity_userType_and_tag import find_best_match
from .type_explain import type_1_money, type_2_option, type_3_structure, type_4_transport, type_5_nature, type_6_emotion, type_7_business, type_8_student

# - response[’chatbot’][context’][’role’] == “user” 인 응답들을 평문으로 바꿈.
# - 평문으로 바꾼 문장과 사용자 유형 문장들을 유사도 분석하여 가장 유사도가 높은 유형을 보여준다.
# - 평문으로 바꾼 문장과 DB의 키워드를 유사도 분석
#     - 키워드들을 보고 챗봇을 좀 더 자세하게 만들어야 함.
# - tag DB에서 가장 유사한 태그 n개를 뽑아냄.
# - 이 태그 n개를 사용자 유형 페이지에 같이 줌.
# - 맞춤 매물 검색을 누른다면 그 태그를 가장 많이 가지고 있고 특정 개수 이상 태그를 가지고 있는 매물들을 가져옴.
#     - 태그를 실시간으로 삭제, 추가해서 조회하면 바로 DB에서 가져올 수 있게 설정.

@method_decorator(csrf_exempt, name='dispatch')
class ReportView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            content = request.GET.getlist('content')
            #content 리스트를 평문으로 바꾸기 
            print(content)
            # content = content[0]
            user_type_list = [type_1_money, type_2_option, type_3_structure, type_4_transport, type_5_nature, type_6_emotion, type_7_business, type_8_student]

            best_match_index, similarity_score = find_best_match(content, user_type_list)            
            
            return JsonResponse({'userType': user_type_list[best_match_index],
                                 'similarity_score' : similarity_score}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)