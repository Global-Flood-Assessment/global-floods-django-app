from django.urls import path
from . import views

urlpatterns = [
  path('', views.index,name='index'),
  path('pick/', views.pick, name='pick'),
  path('draw/', views.draw, name='draw'),
  path('upload/', views.upload, name='upload'),
  path('result/', views.result, name='result')]
