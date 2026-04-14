from django.contrib import admin
from .models import Recipe, Menu

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'week_number', 'year', 'recipe', 'is_published')
    list_filter = ('day_of_week', 'week_number', 'year', 'is_published')
    search_fields = ('recipe__name',)
