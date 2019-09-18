from django.urls import path

from masterdata.views import ProvinceListAPI, CityListAPI, DistrictListAPI, SubDistrictListAPI

urlpatterns = [
    path('province-list/', ProvinceListAPI.as_view(), name='province_list'),
    path('city-list/', CityListAPI.as_view(), name='city_list'),
    path('district-list/', DistrictListAPI.as_view(), name='district_list'),
    path('sub-district-list/', SubDistrictListAPI.as_view(), name='sub_district_list'),
]