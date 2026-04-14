from django.db import models
from django.conf import settings

class Recipe(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    description = models.TextField(verbose_name="Descripción")
    ingredients = models.TextField(verbose_name="Ingredientes", help_text="Detalle de ingredientes")
    preparation = models.TextField(verbose_name="Preparación")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, limit_choices_to={'role__in': ['chef', 'administrador']})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Menu(models.Model):
    DAYS_OF_WEEK = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
    ]
    
    day_of_week = models.CharField(max_length=15, choices=DAYS_OF_WEEK, verbose_name="Día de la semana")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name="Receta")
    week_number = models.PositiveIntegerField(verbose_name="Número de Semana")
    year = models.PositiveIntegerField(verbose_name="Año")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False, verbose_name="Publicado")

    class Meta:
        unique_together = ['day_of_week', 'week_number', 'year', 'recipe']
        # Una receta se puede servir varias veces un mismo día? Para el MVP asumimos que solo se sirve una u opcionalmente más,
        # pero para simplificar, único por día y receta.

    def __str__(self):
        return f"Menu: {self.recipe.name} - {self.get_day_of_week_display()} (Sem. {self.week_number}/{self.year})"
