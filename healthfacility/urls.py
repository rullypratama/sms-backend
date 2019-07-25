from django.urls import path

from healthfacility.views import HealthFacilityListAPI

urlpatterns = [
    path('health-facility-list/', HealthFacilityListAPI.as_view(), name='health_facility_list'),
]