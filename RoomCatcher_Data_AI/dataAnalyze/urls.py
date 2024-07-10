from django.urls import path, include
from .views import ProductViewSet, ProductFilterView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("products/filter", ProductFilterView.as_view()),
    path("products/", ProductViewSet.as_view({'get': 'list'}))
]
