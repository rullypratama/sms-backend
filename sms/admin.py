from django.contrib import admin

from sms import models

@admin.register(models.CaseInformation)
class CaseInformationAdmin(admin.ModelAdmin):
    search_fields = ('name', 'patient_contact',)
    list_display = ('name', 'patient_contact', 'disease_type', 'case_report_type', 'classification_case')

