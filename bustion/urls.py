from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('bustion/', include('app.urls')),
    path('admin/', admin.site.urls),
]