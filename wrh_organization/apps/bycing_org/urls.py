from .rest_api import router

app_name = 'bycing_org'

urlpatterns = [
]

urlpatterns += router.rest_router.urls
