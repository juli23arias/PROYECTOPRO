from django.urls import path
from . import views

urlpatterns = [
    # Recipes
    path('recetas/', views.recipe_list, name='recipe_list'),
    path('recetas/nueva/', views.recipe_create, name='recipe_create'),
    path('recetas/<int:pk>/editar/', views.recipe_update, name='recipe_update'),
    path('recetas/<int:pk>/eliminar/', views.recipe_delete, name='recipe_delete'),
    
    # Menus
    path('semanal/gestionar/', views.menu_weekly, name='menu_weekly'),
    path('semanal/historial/', views.menu_history, name='menu_history'),
    path('semanal/<int:pk>/eliminar/', views.menu_delete, name='menu_delete'),
    path('semanal/', views.menu_view, name='menu_view'),
]
