from django.urls import include, path, re_path
from rest_framework import routers

from apps.account.rest_api.views import SessionView, ProfileView

rest_router = routers.DefaultRouter()
rest_router.trailing_slash = "/?"  # added to support both / and slashless
rest_router.register(r'session', SessionView, basename='session')
rest_router.register(r'me', ProfileView, basename='profile')
