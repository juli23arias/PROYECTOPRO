from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.payment_register, name='payment_register'),
    path('historial/', views.payment_history, name='payment_history'),
    path('registros/', views.payment_all, name='payment_all'),
    path('caja-diaria/', views.daily_cash, name='daily_cash'),
    path('cerrar-caja/', views.close_cash, name='close_cash'),
    path('historial-cierres/', views.cash_history, name='cash_history'),
]
