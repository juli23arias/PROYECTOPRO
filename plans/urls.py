from django.urls import path
from . import views

urlpatterns = [
    path('gestion/', views.plan_list, name='plan_list'),
    path('gestion/nuevo/', views.plan_create, name='plan_create'),
    path('gestion/editar/<int:pk>/', views.plan_update, name='plan_edit'),
    path('gestion/asignar/', views.student_plan_assign, name='student_plan_assign'),
    path('gestion/asignaciones/eliminar/<int:pk>/', views.student_plan_delete, name='student_plan_delete'),
    path('mi-plan/', views.my_plan, name='my_plan'),
]
