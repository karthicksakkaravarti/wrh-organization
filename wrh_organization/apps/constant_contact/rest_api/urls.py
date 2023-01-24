from django.urls import path
from .views import CCContactListView, CCContactListDetailView

app_name = 'constant_contact'


urlpatterns = [
    # API's
    path('contact_list', CCContactListView.as_view()),
    path('contact_list_detail/<uuid:list_id>/', CCContactListDetailView.as_view()),
]