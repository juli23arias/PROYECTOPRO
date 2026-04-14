import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from menu.models import Recipe, Menu
from accounts.models import User

class Command(BaseCommand):
    help = 'Crea datos de prueba para el menú semanal si la base de datos está vacía.'

    def handle(self, *args, **kwargs):
        if Menu.objects.exists():
            self.stdout.write(self.style.SUCCESS('El menú ya tiene datos. No se realizaron cambios.'))
            return

        # Obtener un usuario para asociar las creaciones (preferiblemente un chef o admin)
        creator = User.objects.filter(role__in=['chef', 'administrador']).first()
        if not creator:
            creator = User.objects.first()
        
        if not creator:
            self.stdout.write(self.style.ERROR('No hay usuarios en el sistema. Crea un usuario antes de ejecutar este comando.'))
            return

        today = timezone.now().date()
        year = today.year
        week = today.isocalendar()[1]

        data = [
            ('lunes', 'Pollo a la plancha', 'Arroz', 'Jugo de naranja'),
            ('martes', 'Carne guisada', 'Papa cocida', 'Limonada'),
            ('miercoles', 'Pasta', 'Ensalada', 'Jugo de mango'),
            ('jueves', 'Pollo al horno', 'Puré de papa', 'Jugo de mora'),
            ('viernes', 'Arroz chino', 'Ensalada', 'Té frío'),
        ]

        for day_code, main, side, drink in data:
            # Crear la receta
            recipe_name = f"{main} con {side}"
            recipe, created = Recipe.objects.get_or_create(
                name=recipe_name,
                defaults={
                    'description': f"Plato principal: {main}. Acompañamiento: {side}. Bebida: {drink}.",
                    'ingredients': f"{main}, {side}, {drink}",
                    'preparation': "Preparación estándar de alta calidad.",
                    'created_by': creator
                }
            )

            # Crear el menú para esta semana
            Menu.objects.get_or_create(
                day_of_week=day_code,
                week_number=week,
                year=year,
                recipe=recipe,
                defaults={
                    'created_by': creator,
                    'is_published': True
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Datos de prueba creados para la semana {week} del año {year}.'))
