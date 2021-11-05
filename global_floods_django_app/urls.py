
from django.urls import path

from . import views

app_name = 'global_floods_django_app'
urlpatterns = [
    path('home/', views.home, name='home'),
    path('map/', views.mapview, name='map'),
]
