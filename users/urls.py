from django.urls import path

from users.views import UserDetailApi

urlpatterns = [
    path('user-detail/', UserDetailApi.as_view(), name='user-detail'),
]
