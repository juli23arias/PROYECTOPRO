from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User

class StudentRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        validators=[validate_password]
    )
    password_confirm = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'cedula', 'email', 'username', 'career', 'semester', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 1234567890'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@universidad.edu'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Identificación / Matrícula'}),
            'career': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Ing. en Sistemas'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 7'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+52 ...'}),
        }
        labels = {
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'cedula': 'Cédula (Código Único)',
            'email': 'Correo (Institucional o Personal)',
            'username': 'Nombre de Usuario / Matrícula',
            'career': 'Carrera',
            'semester': 'Semestre',
            'phone': 'Teléfono',
        }

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if not cedula:
            raise ValidationError("La cédula es obligatoria.")
        if User.objects.filter(cedula=cedula).exists():
            raise ValidationError("Esta cédula ya está registrada en el sistema.")
        return cedula

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un usuario con este correo electrónico.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Este nombre de usuario / matrícula ya está registrado.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Las contraseñas no coinciden.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'estudiante'
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
