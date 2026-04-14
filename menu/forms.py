from django import forms
from .models import Recipe, Menu

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'ingredients', 'preparation']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ingredients': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'preparation': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['day_of_week', 'recipe', 'week_number', 'year', 'is_published']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'recipe': forms.Select(attrs={'class': 'form-select'}),
            'week_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
