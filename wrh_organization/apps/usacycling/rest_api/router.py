from rest_framework import routers
from . import views

rest_router = routers.DefaultRouter()
rest_router.register('event', views.USAEventView)
rest_router.register('address', views.AddressView)
rest_router.register('usaclubs', views.USACyclingClubsView)
rest_router.register('usarider', views.USARiderView)
