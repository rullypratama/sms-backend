from django.contrib import admin

from healthfacility import models

@admin.register(models.HealthFacility)
class HealthFacilityAdmin(admin.ModelAdmin):
    search_fields = ('name', 'code',)
    list_display = ('name', 'code', 'facility_level', 'linked_facility')


