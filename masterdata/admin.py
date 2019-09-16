from django.contrib import admin

from masterdata import models


@admin.register(models.Province)
class ProvinceAdmin(admin.ModelAdmin):
    search_fields = ('name', 'code',)
    list_display = ('name', 'code', 'is_active')


@admin.register(models.City)
class CityAdmin(admin.ModelAdmin):
    search_fields = ('name', 'code',)
    list_display = ('name', 'code', 'is_active', 'province')


@admin.register(models.District)
class DistrictAdmin(admin.ModelAdmin):
    search_fields = ('name', 'code',)
    list_display = ('name', 'code', 'is_active', 'city')


@admin.register(models.SubDistrict)
class SubDistrictAdmin(admin.ModelAdmin):
    search_fields = ('name', 'code',)
    list_display = ('name', 'code', 'is_active', 'district')
