from django.contrib import admin

from users import models

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ('email', 'phone_number',)
    list_display = ('email', 'phone_number', 'health_facility')

