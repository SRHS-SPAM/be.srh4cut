"""
Django REST API 서버 URL 설정
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def api_root(request):
    """API 루트 엔드포인트"""
    return JsonResponse({
        'message': 'Django REST API 서버',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'photos': '/api/photos/',
            'upload': '/api/upload/',
            'current_date': '/api/current-date/',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('catalog.urls')),
    path('', api_root, name='api_root'),  # API 루트
]

# 개발 환경에서 미디어 파일 서빙 설정
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
