from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('find_hospitals/', views.find_hospitals, name='find_hospitals'),
    path('get_route/', views.get_route, name='get_route')
]
