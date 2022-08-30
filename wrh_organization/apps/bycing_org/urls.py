from django.urls import path, include

from .rest_api import router

app_name = 'bycing_org'

urlpatterns = [
    path('', include(router.rest_router.urls)),
    path('public/', include(router.public_rest_router.urls)),
]
