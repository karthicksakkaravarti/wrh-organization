from django.urls import include, path, re_path
from rest_framework import routers

from .views import MemberView, OrganizationView, UserRegistrationView

rest_router = routers.DefaultRouter()
rest_router.trailing_slash = "/?"  # added to support both / and slashless
rest_router.register(r'member', MemberView)
rest_router.register(r'organization', OrganizationView)
rest_router.register(r'users/registration', UserRegistrationView, basename='user_registration')
