from django.urls import path
from .views import CCContactListView, CCContactListDetailView, CCStatusView, CCSignOutView

app_name = 'constant_contact'


urlpatterns = [
    # API's
    path('cc_status', CCStatusView.as_view()),
    path('sign_out', CCSignOutView.as_view()),
    path('contact_list', CCContactListView.as_view()),
    path('contact_list_detail/<uuid:list_id>/', CCContactListDetailView.as_view()),
]