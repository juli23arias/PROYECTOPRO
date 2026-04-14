# Restaurante Universitario - MVP

Sistema de gestión web para un restaurante universitario, desarrollado con Django, Bootstrap 5 y SQLite.
Permite gestionar usuarios (Estudiantes, Chefs, Recepcionistas, Administradores), publicar menús semanales, controlar asistencias, registrar pagos y asignar planes de alimentación.

## Tecnologías Utilizadas
- **Python 3**
- **Django 5**
- **SQLite** (Base de datos por defecto)
- **Bootstrap 5** (Frontend y UI responsiva)
- **Bootstrap Icons**

## Requisitos Previos
- Python 3.10 o superior

## Instrucciones de Instalación y Ejecución Local

1. **Clonar/Abrir el Proyecto**
   Abre la carpeta del proyecto en tu terminal o editor de código.

2. **Crear y Activar el Entorno Virtual**
   ```bash
   # En Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # En macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar Dependencias**
   ```bash
   pip install django
   ```

4. **Aplicar Migraciones**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Poblar la Base de Datos con Usuarios de Prueba**
   Existe un script que crea un superusuario y usuarios con distintos roles para probar la plataforma rápidamente:
   ```bash
   python populate_users.py
   ```
   *Usuarios creados:*
   - **Administrador:** admin / admin123
   - **Chef:** chef / chef123
   - **Recepcionista:** recepcion / recepcion123
   - **Estudiante:** estudiante1 / est123

6. **Iniciar el Servidor de Desarrollo**
   ```bash
   python manage.py runserver
   ```
   Abre tu navegador en `http://127.0.0.1:8000/`.

## Características Clave del MVP
- **Autenticación Basada en Roles:** Permisos específicos para chefs, recepcionistas, estudiantes y administradores.
- **Gestión de Menús:** Los chefs pueden crear recetas y asignarlas a los días de la semana.
- **Control de Asistencia:** Recepción registra a los estudiantes que asisten a comer.
- **Módulo de Caja/Pagos:** Registro y visualización de pagos de estudiantes.
- **Planes de Alimentación:** Venta y gestión de planes activos de comidas para estudiantes.
- **Dashboard de Reportes:** Métricas clave para administradores del restaurante.

---
*Desarrollado como Proyecto Integrador (PROYECTOPRO).*
