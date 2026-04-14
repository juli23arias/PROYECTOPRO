from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.attendance_register, name='attendance_register'),
    path('historial/', views.attendance_history, name='attendance_history'),
    path('historial-completo/', views.attendance_all, name='attendance_all'),
]
