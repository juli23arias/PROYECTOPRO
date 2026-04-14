from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('estudiante', 'Estudiante'),
        ('chef', 'Chef'),
        ('recepcionista', 'Recepcionista'),
        ('administrador', 'Administrador'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='estudiante')
    cedula = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="Cédula/ID")
    
    # Perfil Estudiante Info
    career = models.CharField(max_length=150, blank=True, null=True, verbose_name="Carrera")
    semester = models.PositiveIntegerField(blank=True, null=True, verbose_name="Semestre")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    @property
    def is_student(self):
        return self.role == 'estudiante'
    
    @property
    def is_chef(self):
        return self.role == 'chef'

    @property
    def is_receptionist(self):
        return self.role == 'recepcionista'

    @property
    def is_admin_role(self):
        return self.role == 'administrador'
