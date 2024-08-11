from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('account/', views.account_summary, name='account_summary'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('transfer/', views.transfer, name='transfer'),
    path('nomoney/', views.nomoney, name='nomoney'),
    path('profile/<int:account_id>/', views.profile, name='profile'),
    path('set_upi_id/', views.set_upi_id, name='set_upi_id'),


]
