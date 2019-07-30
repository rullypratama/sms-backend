from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.template.response import TemplateResponse
from django.urls import reverse

from users import models


class UserForm(UserChangeForm):

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

    def save(self, commit=False):
        instance = super(UserForm, self).save(commit=commit)
        instance.save()
        return instance


class UserExt(UserAdmin):
    search_fields = ('email', 'phone_number',)
    form = UserForm
    list_display = [
        'email',
        'phone_number',
        'health_facility'
    ]

    fieldsets = UserAdmin.fieldsets + (
        ('Properties', {'fields': ('health_facility',
                                   'phone_number')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
         ),
    )


user_ext = UserExt

admin.site.register(models.User, UserExt)