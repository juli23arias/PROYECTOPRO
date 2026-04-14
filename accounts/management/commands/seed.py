from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        users = [
            ('admin', 'administrador'),
            ('chef', 'chef'),
            ('recepcionista', 'recepcionista'),
            ('estudiante', 'estudiante'),
        ]

        for username, role in users:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    password='123456',
                    role=role
                )
                self.stdout.write(f"Usuario {username} creado con rol {role}")