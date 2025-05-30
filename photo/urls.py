"""
URL configuration for photo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.contrib.staticfiles.views import serve
from django.contrib import admin
from django.http import FileResponse
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

from catalog.views import PhotoViewSet, some_endpoint


def serve_manifest(request):
    # React 빌드 폴더 내 manifest.json 위치 지정
    file_path = os.path.join(settings.BASE_DIR, '/front/public/manifest.json')
    return FileResponse(open(file_path, 'rb'), content_type='application/json')

def serve_logo(request, filename=None):
    # If filename is not provided in the URL, use the default
    if filename is None:
        if 'spamlogo.png' in request.path:
            filename = 'spamlogo.png'
        elif 'spamlogo2.png' in request.path:
            filename = 'spamlogo2.png'
        else:
            from django.http import Http404
            raise Http404("No filename specified")
    
    # Print current directory and files for debugging
    import os
    import logging
    logger = logging.getLogger(__name__)
    
    # Log current working directory
    cwd = os.getcwd()
    logger.error(f"Current working directory: {cwd}")
    
    # Log files in current directory
    try:
        files = os.listdir(cwd)
        logger.error(f"Files in current directory: {files}")
    except Exception as e:
        logger.error(f"Error listing files: {e}")
    
    # Try multiple possible locations
    possible_paths = [
        '/front/public/' + filename,
        '/app/front/public/' + filename,
        os.path.join(cwd, 'front', 'public', filename),
        os.path.join(cwd, '..', 'front', 'public', filename),
        os.path.join(cwd, '..', '..', 'front', 'public', filename),
    ]
    
    # Log all possible paths
    logger.error(f"Trying paths: {possible_paths}")
    
    # Check each path
    for path in possible_paths:
        if os.path.exists(path):
            logger.error(f"Found file at: {path}")
            return FileResponse(open(path, 'rb'))
        else:
            logger.error(f"File not found at: {path}")
    
    from django.http import Http404
    raise Http404(f"Image file {filename} not found. Tried multiple locations.")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('catalog.urls')),  # API 경로

    re_path(r'^(?P<path>manifest\.json|favicon\.ico|logo192\.png|logo512\.png|robots\.txt|spamlogo\.ico)$',
            TemplateView.as_view(template_name='index.html')),
    
    path('manifest.json', 
        TemplateView.as_view(
            template_name='manifest.json', 
            content_type='application/json'
        )),
    *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
    path('manifest.json', serve_manifest),
    path('spamlogo.png', serve_logo, {'filename': 'spamlogo.png'}),
    path('spamlogo2.png', serve_logo, {'filename': 'spamlogo2.png'}),
    path('<str:filename>', serve_logo, name='serve_logo'),

    path('api/some-endpoint/', some_endpoint, name='some-endpoint'),

    path('api/photos/', PhotoViewSet.as_view({'get': 'list', 'post': 'create'}), name='photo-list'),

]

# 개발 환경에서 미디어 파일 서빙 설정
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()

# /api/ 경로는 제외하고 나머지만 React SPA로 라우팅
urlpatterns.append(re_path(r'^(?!api/)(?!admin/).*$', TemplateView.as_view(template_name='index.html')))
