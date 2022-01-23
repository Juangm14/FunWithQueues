from django.urls import path
from . import views


urlpatterns = [
    #path('', views.bienvenida, name='bienvenida'),  
    #path('home', views.home, name='home'),  
    #path('signup', views.signup, name='signup'),  
    #path('login', views.login, name='login'),  
    #path('dashboard', views.dashboard, name='dashboard'),  
    path('map', views.map, name='map'),  
    path('usuarios', views.usuarios, name='usuarios'),
    path('usuario/<str:alias>', views.usuario, name='usuario')
    #path('update', views.update, name='update'),  
    #path('enter_park', views.enterPark, name='enterPark'),  
    #path('leave_park', views.leavePark, name='leavePark'),  
    #path('logout', views.logout, name='logout'),  
]