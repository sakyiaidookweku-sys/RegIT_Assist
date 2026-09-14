from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Automatically redirect http://127.0.0.1:8000/ to the staff login page
    path('', RedirectView.as_view(url='/staff/login/', permanent=False)),

    # Include your app URLs so all your dashboard and login routes work
    path('', include('support_app.urls')),
    
    # Built-in Django admin panel
    path('django-admin/', admin.site.urls), 
]