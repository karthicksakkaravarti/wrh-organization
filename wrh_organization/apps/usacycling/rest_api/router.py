from rest_framework import routers
from . import views

rest_router = routers.DefaultRouter()
rest_router.register('event', views.USACEventView)
rest_router.register('club', views.USACClubView)
rest_router.register('rider', views.USARiderView)
