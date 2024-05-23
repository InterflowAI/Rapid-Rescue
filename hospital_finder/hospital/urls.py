from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('find_hospitals/', views.find_hospitals, name='find_hospitals'),
]
