from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('/messages/inbox/')),
    path('admin/', admin.site.urls),
    path('messages/', include('messages_app.urls')),
]
