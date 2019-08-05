from django.urls import path

from sms.views import CaseInformationListAPI, CaseInformationDetailAPI, CaseInformationReceivedListAPI, \
    CaseInformationSentListAPI

urlpatterns = [
    path('case-information-list/', CaseInformationListAPI.as_view(), name='case_information_list'),
    path('case-information-list/<int:pk>', CaseInformationDetailAPI.as_view(), name='case_information_details'),
    path('received-case-list/', CaseInformationReceivedListAPI.as_view(), name='received_case_list'),
    path('sent-case-list/', CaseInformationSentListAPI.as_view(), name='sent_case_list'),
]