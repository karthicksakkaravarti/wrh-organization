"""wrh_photos URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf import settings
from django.urls import include, re_path, path
from django.contrib import admin
from django.views.generic import RedirectView
from django.views.static import serve
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.cycling_org.views import ckeditor_upload_file

VERSION_PARAM = settings.REST_FRAMEWORK.get('VERSION_PARAM', 'version')
DEFAULT_VERSION = settings.REST_FRAMEWORK.get('DEFAULT_VERSION', 'v1')
API_ENDPOINT = 'api/(?P<{}>v\d+)'.format(VERSION_PARAM)


urlpatterns = [
    re_path(r'^$', RedirectView.as_view(url=settings.VUE_STATIC_INDEX), name='index'),
    re_path(r'^{}/account/'.format(API_ENDPOINT), include('apps.account.urls', namespace='account_rest_api')),
    re_path(r'^{}/cycling_org/'.format(API_ENDPOINT), include('apps.cycling_org.urls', namespace='cycling_org_rest_api')),
    re_path(r'^{}/usacycling/'.format(API_ENDPOINT), include('apps.usacycling.urls', namespace='usacycling_rest_api')),
    re_path(r'^admin/', admin.site.urls),
    re_path('^ckeditor5/image_upload/', ckeditor_upload_file, name="ck_editor_5_upload_file"),
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^token/auth/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path(r'^token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
