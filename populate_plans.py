import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurante_project.settings')
django.setup()

from plans.models import Plan

plans_to_create = [
    {
        'name': 'Plan Diario',
        'duration_days': 1,
        'price': 5000,
        'active': True,
        'description': 'Permite consumir el almuerzo del restaurante universitario durante un día.'
    },
    {
        'name': 'Plan Semanal',
        'duration_days': 5,
        'price': 20000,
        'active': True,
        'description': 'Permite consumir el almuerzo de lunes a viernes durante una semana.'
    },
    {
        'name': 'Plan Mensual',
        'duration_days': 20,
        'price': 75000,
        'active': True,
        'description': 'Permite consumir el almuerzo durante 20 días hábiles del mes.'
    }
]

for plan_data in plans_to_create:
    plan, created = Plan.objects.get_or_create(
        name=plan_data['name'],
        defaults=plan_data
    )
    if created:
        print(f"Plan creado: {plan.name}")
    else:
        print(f"El plan ya existe: {plan.name}")
