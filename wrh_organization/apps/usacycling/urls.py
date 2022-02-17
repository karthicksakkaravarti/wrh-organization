from .rest_api import router

app_name = 'usacycling'

urlpatterns = [
]

urlpatterns += router.rest_router.urls
