from django import forms
from .models import Attendance

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'signed', 'signature_data']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'signed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'signature_data': forms.HiddenInput()
        }
