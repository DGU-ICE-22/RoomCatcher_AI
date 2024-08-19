import traceback
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .calculate_similarity_userType_and_tag import find_best_match_tags, find_best_match_type, bring_tags_to_user_type, select_best_index
from .type_explain import type_1_money, type_2_option, type_3_structure, type_4_transport, type_5_nature, type_6_emotion, type_7_business, type_8_student
from .convert_to_plaintext import convert_to_plaintext

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
            clear_content = convert_to_plaintext(content)['choices'][0]['message']['content']
            
            if clear_content == None:
                return JsonResponse({'error': 'Failed to convert to plaintext'}, status=500)
            
            user_type_list = [type_1_money, type_2_option, type_3_structure, type_4_transport, type_5_nature, type_6_emotion, type_7_business, type_8_student]

            
            #1. clear_content를 이용해서 DB에 있는 키워드와 유사도 분석 후 가장 유사한 키워드들 n개 가져오기 
            tags = find_best_match_tags(clear_content)
            tags = tags[:int(len(tags)/8)]
            #2. 사용자 유형에 할당된 태그들과 비교하여 가장 유사한 사용자 유형을 찾아 점수를 매기기 
            
            dummy_tags = [bring_tags_to_user_type(index) for index in range(len(user_type_list))]
# 각 dummy_tags 항목에 대해 원래 인덱스와 함께 저장
            indexed_dummy_tags = list(enumerate(dummy_tags))
# dummy_tags를 정렬하면서 원래 인덱스도 함께 보존
            sorted_indexed_dummy_tags = sorted(
                indexed_dummy_tags,
                key=lambda dt: len([tag for sublist in dt[1] for tag in sublist if tag in tags]),
                reverse=True
            )       
            # 정렬된 리스트에서 인덱스 순서를 추출     
            index_list = [index for index, _ in sorted_indexed_dummy_tags]
            # sorted_dummy_tags 추출
            sorted_dummy_tags = [dt for _, dt in sorted_indexed_dummy_tags]
                        
            # 사용자의 응답과 사용자 유형설명을 유사도 분석한 결과 유사한 순서대로 반환
            _ , index_list_v2 = find_best_match_type(clear_content, user_type_list)
            
            #사용자 유형 인덱스 
            max_index = select_best_index(index_list_v2, index_list) 
            
            correct_type_name, correct_type_explain = user_type_list[max_index].split('\n', 1)        # 사용자의 유형
                        
            user_tags = []
            for tag in tags:
                if tag in sorted_dummy_tags[0] and tag not in user_tags:
                    user_tags.append(tag)    
                            
            if len(user_tags) < 10:
                print("user_tags 교집합 부족")

                # sorted_dummy_tags[0]에서 중복되지 않는 항목을 user_tags에 추가
                for tag in sorted_dummy_tags[0]:
                    if tag not in user_tags and len(user_tags) < 10:
                        user_tags.append(tag)
                
                # 이 시점에서 User 엔티티에 사용자 유형과 사용자 태그를 저장.
                
                #3. 도출된 사용자 유형에 해당하는 태그들 중 1번에서 가져왔던 태그들과 중복되는 태그들을 response로 보내줌. 
                return JsonResponse({'userTypeName':  correct_type_name,
                                    'userTypeExplain' : correct_type_explain,
                                    'user_tags': user_tags}, status=200)
            else:
                
                # 이 시점에서 User 엔티티에 사용자 유형과 사용자 태그를 저장.

                 #3. 도출된 사용자 유형에 해당하는 태그들 중 1번에서 가져왔던 태그들과 중복되는 태그들을 response로 보내줌. 
                return JsonResponse({'userTypeName':  correct_type_name,
                                    'userTypeExplain' : correct_type_explain,
                                    'user_tags': user_tags[:10]}, status=200)
            
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
        
class productRecommandView(APIView):
    def get(self, request, *args, **kwargs):
        return