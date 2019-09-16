
from django.contrib import admin
from django.urls import path, include

from users.views import obtain_jwt_token

urlpatterns = [
    path('admin/', admin.site.urls),

    path('auth/', obtain_jwt_token, name='user-login'),
    path('', include('healthfacility.urls')),
    path('', include('sms.urls')),
    path('', include('users.urls')),
    path('', include('masterdata.urls')),

]
