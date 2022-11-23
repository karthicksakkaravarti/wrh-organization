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
rest_router.register(r'event', views.EventView)
rest_router.register(r'race', views.RaceView)
rest_router.register(r'race_result', views.RaceResultView)
rest_router.register(r'category', views.CategoryView)
rest_router.register(r'race_series', views.RaceSeriesView)
rest_router.register(r'race_series_result', views.RaceSeriesResultView)
rest_router.register(r'fields_tracking', views.FieldsTrackingView)
rest_router.register(r'global_conf', views.GlobalConfView, basename='global_conf')

public_rest_router = routers.DefaultRouter()
public_rest_router.trailing_slash = "/?"  # added to support both / and slashless
public_rest_router.register(r'member', views.PublicMemberView)
public_rest_router.register(r'organization', views.PublicOrganizationView)
