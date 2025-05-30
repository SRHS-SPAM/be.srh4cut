import os
from django.http import FileResponse
from django.urls import path, include, re_path
from . import views
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
import logging

logger = logging.getLogger(__name__)

# DefaultRouter 설정 (중복 제거)
router = DefaultRouter()
router.register(r'photos', views.PhotoViewSet)
logger.error(f"Router URLs: {router.urls}")  # 등록된 URL 패턴 로깅

# 파일 서빙 함수
def serve_manifest(request):
    file_path = os.path.join(settings.BASE_DIR, 'front/public/manifest.json')
    return FileResponse(open(file_path, 'rb'), content_type='application/json')

def serve_logo(request, filename):
    file_paths = [
        os.path.join(settings.BASE_DIR, 'front/public', filename),
        os.path.join(settings.BASE_DIR, '..', 'front', 'public', filename),
    ]
    
    for path in file_paths:
        if os.path.exists(path):
            return FileResponse(open(path, 'rb'))
    
    from django.http import Http404
    raise Http404(f"Image file {filename} not found.")

urlpatterns = [
    # Photo API
    path('api/photos/', views.PhotoViewSet.as_view({'get': 'list', 'post': 'create'}), name='photo-list'),
    path('api/photos/<int:pk>/', views.PhotoViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='photo-detail'),
    path('api/', include(router.urls)),
    
    # Upload API
    path('api/upload/', views.upload_photo, name='upload_photo'),
    
    # 기타 API
    path('api/date/', views.get_current_date, name='get_current_date'),
    path('api/current-date/', views.get_current_date, name='current_date'),
    path('api/some-endpoint/', views.some_endpoint, name='some_endpoint'),
    
    # 정적 파일 서빙
    path('manifest.json', serve_manifest),
    path('spamlogo.png', serve_logo, {'filename': 'spamlogo.png'}),
    path('spamlogo2.png', serve_logo, {'filename': 'spamlogo2.png'}),
    
    # 기본 뷰
    path('', views.photo_list, name='photo_list'),
    path('photo/<uuid:pk>/', views.photo_detail, name='photo_detail'),
    path('photo/<int:pk>/', views.photo_detail, name='photo_detail'),
    path('photo/create/', views.photo_create, name='photo_create'),
    
    # React SPA 지원을 위한 catch-all 패턴
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]

# 정적 파일 설정
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()