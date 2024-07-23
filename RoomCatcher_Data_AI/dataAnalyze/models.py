from django.db import models

# Create your models here.
class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    productName = models.CharField(max_length=30)
    productRoomType = models.CharField(max_length=30)
    productSellingType = models.CharField(max_length=30)
    productPrice = models.CharField(max_length=30)
    productAddr = models.CharField(max_length=50)
    productInfo = models.CharField(max_length=200)
    productImage = models.CharField(max_length=200)
    productIsContract = models.BooleanField()
    productIsQuick = models.BooleanField()
    
    class Meta:
        db_table = 'dataAnalyze_product'

class Tag(models.Model):
    id = models.IntegerField(primary_key=True)
    tagName = models.CharField(max_length=30)

class ProductTag(models.Model):
    id = models.IntegerField(primary_key=True)
    productId = models.ForeignKey(Product, on_delete=models.CASCADE)
    tagId = models.ForeignKey(Tag, on_delete=models.CASCADE)
    
class ProductKB(models.Model):
    floor_type = models.CharField(max_length=10, blank=True, null=True)  # 해당층구분
    total_area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # 연면적
    num_bathrooms = models.IntegerField(blank=True, null=True)  # 욕실수
    rent_ratio = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # 전세가율
    house_type = models.CharField(max_length=255, blank=True, null=True)  # 주택형타입내용
    min_rent_price = models.IntegerField(blank=True, null=True)  # 최소월세가
    listing_source = models.CharField(max_length=10, blank=True, null=True)  # 매물유입구분
    sale_price = models.IntegerField(blank=True, null=True)  # 매매일반거래가
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)  # wgs84위도
    building_area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # 건축면적
    false_listing_result = models.CharField(max_length=10, blank=True, null=True)  # 허위매물처리결과구분명
    building_usage_code = models.CharField(max_length=50, blank=True, null=True)  # 건축물용도코드명
    complex_name = models.CharField(max_length=255, blank=True, null=True)  # 단지명
    rent_deposit = models.IntegerField(blank=True, null=True)  # 월세보증금
    num_rooms = models.IntegerField(blank=True, null=True)  # 방수
    usage_month = models.CharField(max_length=2, blank=True, null=True)  # 사용월
    exclusive_area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # 전용면적
    agent_address = models.CharField(max_length=255, blank=True, null=True)  # 중개업소주소
    registration_date = models.DateField(blank=True, null=True)  # 등록년월일
    listing_status = models.CharField(max_length=10, blank=True, null=True)  # 매물상태구분
    years_used = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)  # 사용년차
    building_coverage_ratio = models.CharField(max_length=10, blank=True, null=True)  # 건폐율내용
    listing_serial_number = models.BigIntegerField()  # 매물일련번호
    ad_description = models.CharField(max_length=255, blank=True, null=True)  # 특징광고내용
    num_images = models.IntegerField(blank=True, null=True)  # 매물이미지개수
    net_supply_area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # 순공급면적
    listing_type = models.CharField(max_length=50, blank=True, null=True)  # 매물종별구분명
    net_exclusive_area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # 순전용면적
    source_name = models.CharField(max_length=50, blank=True, null=True)  # 매물유입구분명
    max_rent_price = models.IntegerField(blank=True, null=True)  # 최대전세가
    transaction_type = models.CharField(max_length=50, blank=True, null=True)  # 매물거래구분명
    floor_area_ratio = models.CharField(max_length=10, blank=True, null=True)  # 용적률내용
    mortgage = models.CharField(max_length=255, blank=True, null=True)  # 융자금
    agent_name = models.CharField(max_length=255, blank=True, null=True)  # 중개업소명
    max_loan_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # 최대대출가능금액
    total_floors = models.IntegerField(blank=True, null=True)  # 총층수
    listing_name = models.CharField(max_length=255, blank=True, null=True)  # 매물명
    complex_serial_number = models.BigIntegerField(blank=True, null=True)  # 단지기본일련번호
    supply_area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # 공급면적
    move_in_date = models.CharField(max_length=10, blank=True, null=True)  # 입주가능일내용
    sale_price_comparison = models.IntegerField(blank=True, null=True)  # 실거래가대비
    floor_number = models.CharField(max_length=10, blank=True, null=True)  # 해당층수
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)  # wgs84경도
    usage_year = models.CharField(max_length=4, blank=True, null=True)  # 사용년
    cluster_id = models.CharField(max_length=20, blank=True, null=True)  # 클러스터식별자
    district_address = models.CharField(max_length=255, blank=True, null=True)  # 시군구주소
    price_per_pyeong = models.IntegerField(blank=True, null=True)  # 평당단가
    orientation = models.CharField(max_length=10, blank=True, null=True)  # 방향구분명
    has_elevator = models.BooleanField(default=False)  # 승강기유무
    listing_type_code = models.CharField(max_length=10, blank=True, null=True)  # 매물종별구분
    category = models.CharField(max_length=10, blank=True, null=True)  # 카테고리2
    group_type = models.CharField(max_length=10, blank=True, null=True)  # 매물종별그룹구분명
    detailed_address = models.CharField(max_length=10, blank=True, null=True)  # 상세번지내용
    building_name = models.CharField(max_length=255, blank=True, null=True)  # 건물명
    land_area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # 대지면적
    transaction_type_code = models.CharField(max_length=10, blank=True, null=True)  # 매물거래구분
    image_url = models.CharField(max_length=255, blank=True, null=True) # 이미지 주소
    door_structure = models.CharField(max_length=255, blank=True, null=True)  # 현관구조내용
    product_address = models.CharField(max_length=255, blank=True, null=True)  # 매물주소내용
    def __str__(self):
        return self.listing_name
    
# totalCnt
# wgs84경도
# wgs84위도
# 건물명
# 건축면적
# 건축물용도코드명
# 건폐율내용
# 공급면적
# 단지기본일련번호
# 단지명
# 대지면적
# 등록년월일
# 매매일반거래가
# 매물거래구분
# 매물거래구분명
# 매물명
# 매물상태구분
# 매물유입구분
# 매물유입구분명
# 매물이미지개수
# 매물이미지디렉토리경로내용
# 매물일련번호
# 매물종별구분
# 매물종별구분명
# 매물종별그룹구분명
# 매물주소내용
# 방수
# 방향구분명
# 사용년
# 사용년차
# 사용월
# 상세번지내용
# 순공급면적
# 순전용면적
# 승강기유무
# 시군구주소
# 실거래가대비
# 연면적
# 욕실수
# 용적률내용
# 월세보증금
# 융자금
# 이미지디렉토리경로내용
# 입주가능일내용
# 전세가율
# 전용면적
# 주택형타입내용
# 중개업소명
# 중개업소주소
# 총층수
# 최대대출가능금액
# 최대전세가
# 최소월세가
# 카테고리2
# 클러스터식별자
# 특징광고내용
# 평당단가
# 해당층구분
# 해당층수
# 허위매물처리결과구분명
# 현관구조내용 