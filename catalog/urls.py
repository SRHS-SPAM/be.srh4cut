from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# REST API 라우터 설정
router = DefaultRouter()
router.register(r'photos', views.PhotoViewSet)

urlpatterns = [
    # REST API 라우터 (UUID 지원)
    path('', include(router.urls)),
    
    # 추가 API 엔드포인트
    path('upload/', views.upload_photo, name='upload_photo'),
    path('current-date/', views.get_current_date, name='current_date'),
    path('get-csrf/', views.get_csrf, name='get_csrf'),
    
    # UUID 기반 download 엔드포인트 명시적 추가
    path('photos/<uuid:pk>/download/', views.PhotoViewSet.as_view({'get': 'download'}), name='photo-download'),
]