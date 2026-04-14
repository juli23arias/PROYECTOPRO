import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurante_project.settings')
django.setup()

from accounts.models import User

def create_users():
    # Admin
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        admin.role = 'administrador'
        admin.first_name = 'Admin'
        admin.last_name = 'Sistema'
        admin.save()
        print("Creado admin: admin / admin123")
        
    # Chef
    if not User.objects.filter(username='chef').exists():
        chef = User.objects.create_user('chef', 'chef@example.com', 'chef123')
        chef.role = 'chef'
        chef.first_name = 'Juan'
        chef.last_name = 'Cocinero'
        chef.save()
        print("Creado chef: chef / chef123")
        
    # Recepcionista
    if not User.objects.filter(username='recepcion').exists():
        rec = User.objects.create_user('recepcion', 'recep@example.com', 'recepcion123')
        rec.role = 'recepcionista'
        rec.first_name = 'Maria'
        rec.last_name = 'Recepcionista'
        rec.save()
        print("Creada recepcionista: recepcion / recepcion123")

    # Estudiante
    if not User.objects.filter(username='estudiante1').exists():
        est = User.objects.create_user('estudiante1', 'est1@example.com', 'estudiante123')
        est.role = 'estudiante'
        est.first_name = 'Pedro'
        est.last_name = 'Perez'
        est.save()
        print("Creado estudiante: estudiante1 / estudiante123")

if __name__ == '__main__':
    create_users()
    print("Usuarios de prueba creados exitosamente.")
