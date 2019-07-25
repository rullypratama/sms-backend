from django.urls import path

from sms.views import CaseInformationListAPI, CaseInformationDetailAPI

urlpatterns = [
    path('case-information-list/', CaseInformationListAPI.as_view(), name='case_information_list'),
    path('case-information-list/<int:pk>', CaseInformationDetailAPI.as_view(), name='case_information_details'),
]