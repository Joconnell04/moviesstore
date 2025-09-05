from django.urls import path
from . import views, include
urlpatterns = [
    path('', views.index, name='home.index'),
    path('', include('home.urls')),
]

###
"""
from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
]
"""