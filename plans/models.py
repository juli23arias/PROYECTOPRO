from django.db import models
from django.conf import settings
from django.utils import timezone

class Plan(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre del Plan")
    description = models.TextField(verbose_name="Descripción")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Precio")
    duration_days = models.PositiveIntegerField(default=1, verbose_name="Duración (Días)")
    active = models.BooleanField(default=True, verbose_name="Estado Activo")
    
    def __str__(self):
        return f"{self.name} (${self.price}) - {self.duration_days} días"

class StudentPlan(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'estudiante'}, related_name='plans')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, verbose_name="Plan")
    start_date = models.DateField(default=timezone.localdate, verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    active = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Plan de Estudiante"
        verbose_name_plural = "Planes de Estudiantes"

    def __str__(self):
        return f"{self.plan.name} - {self.student.get_full_name()} ({'Activo' if self.active else 'Inactivo'})"
