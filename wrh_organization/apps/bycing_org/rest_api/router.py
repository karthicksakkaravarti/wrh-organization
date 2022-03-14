from django.urls import include, path, re_path
from rest_framework import routers

from . import views

rest_router = routers.DefaultRouter()
rest_router.trailing_slash = "/?"  # added to support both / and slashless
rest_router.register(r'member', views.MemberView)
# rest_router.register(r'organization_member', views.OrganizationMemberView)
rest_router.register(r'organization', views.OrganizationView)
rest_router.register(r'organization/(?P<org_id>[^/.]+)/members', views.OrganizationMemberView,
                     basename='organization_members')
rest_router.register(r'organization/(?P<org_id>[^/.]+)/member_orgs', views.OrganizationMemberOrgView,
                     basename='organization_member_orgs')
rest_router.register(r'users/registration', views.UserRegistrationView, basename='user_registration')
rest_router.register(r'fields_tracking', views.FieldsTrackingView)
