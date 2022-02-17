from .rest_api import router

app_name = 'account'

urlpatterns = [
]

urlpatterns += router.rest_router.urls
