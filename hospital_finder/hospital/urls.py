from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('index', views.index, name='index'),
    path('find_hospitals/', views.find_hospitals, name='find_hospitals'),
    path('get_route/', views.get_route, name='get_route'),
    path('contactus/',views.contactus,name='contact'),
    path('aboutus/',views.aboutus,name='about'),
    path('pronezone/',views.pronezone,name='pronezone'),
    path("login/", views.login_request, name="login"),
    path("register/", views.register_request, name="register"),
    path("logout/", views.logout_request, name= "logout"),
]
