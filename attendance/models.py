from django.db import models
from django.conf import settings
from django.utils import timezone

class Attendance(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'estudiante'}, related_name='attendances')
    date = models.DateField(default=timezone.localdate, verbose_name="Fecha")
    signed = models.BooleanField(default=False, verbose_name="Firmado")
    signature_data = models.TextField(blank=True, null=True, verbose_name="Firma (Base64)", help_text="Datos de la firma electrónica")
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='registered_attendances')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'date']

    def __str__(self):
        return f"Asistencia: {self.student.get_full_name()} - {self.date}"
