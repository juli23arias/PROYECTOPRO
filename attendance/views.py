from django.shortcuts import render, redirect, get_object_or_404, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from core.decorators import receptionist_required, student_required
from .models import Attendance
from .forms import AttendanceForm
from accounts.models import User
from plans.models import StudentPlan
from datetime import timedelta

@login_required
@receptionist_required
def attendance_register(request):
    today = timezone.localdate()
    search_query = request.GET.get('q', '').strip()
    
    selected_student = None
    active_plan = None
    already_registered = False
    student_history = []
    
    if search_query:
        # Buscar por cédula exacta primero, luego por coincidencia parcial si es necesario
        selected_student = User.objects.filter(
            Q(cedula=search_query) | Q(username=search_query),
            role='estudiante', 
            is_active=True
        ).first()
        
        if not selected_student:
            # Búsqueda más amplia si no hay exacta
            selected_student = User.objects.filter(
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query),
                role='estudiante', 
                is_active=True
            ).first()

        if selected_student:
            # Verificar plan activo
            active_plan = StudentPlan.objects.filter(
                student=selected_student, 
                active=True,
                start_date__lte=today,
                end_date__gte=today
            ).first()
            
            if today.weekday() >= 5:
                active_plan = None
                messages.warning(request, "Hoy es fin de semana. El restaurante universitario solo opera de lunes a viernes.")
            elif not active_plan:
                messages.warning(request, "El estudiante no tiene un plan activo. Debe registrar un pago primero.")
            
            # Verificar si ya registró asistencia hoy
            already_registered = Attendance.objects.filter(
                student=selected_student, 
                date=today
            ).exists()
            
            # Historial reciente (últimas 5)
            student_history = Attendance.objects.filter(
                student=selected_student
            ).order_by('-date')[:5]

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        if student_id:
            student_to_register = get_object_or_404(User, id=student_id, role='estudiante')
            
            # Verificar plan activo (Doble verificación en servidor)
            has_active_plan = StudentPlan.objects.filter(
                student=student_to_register,
                active=True,
                start_date__lte=today,
                end_date__gte=today
            ).exists()
            
            if today.weekday() >= 5:
                messages.error(request, "No se puede registrar asistencia en fin de semana.")
                return redirect(f"{request.path}?q={student_to_register.cedula or student_to_register.username}")

            if not has_active_plan:
                messages.error(request, f'No se puede registrar asistencia: {student_to_register.get_full_name()} no tiene un plan activo.')
                return redirect(f"{request.path}?q={student_to_register.cedula or student_to_register.username}")

            # Doble verificación de seguridad (Ya registró hoy)
            exists_today = Attendance.objects.filter(student=student_to_register, date=today).exists()
            if exists_today:
                messages.error(request, f'El estudiante {student_to_register.get_full_name()} ya registró asistencia hoy.')
            else:
                Attendance.objects.create(
                    student=student_to_register,
                    date=today,
                    registered_by=request.user
                )
                messages.success(request, f'Asistencia registrada correctamente para {student_to_register.get_full_name()}.')
            
            return redirect(f"{request.path}?q={student_to_register.cedula or student_to_register.username}")

    today_attendances = Attendance.objects.filter(date=today).order_by('-created_at')
    
    context = {
        'selected_student': selected_student,
        'active_plan': active_plan,
        'already_registered': already_registered,
        'student_history': student_history,
        'today_attendances': today_attendances,
        'today': today,
        'search_query': search_query,
    }
    return render(request, 'attendance/attendance_register.html', context)

@login_required
@student_required
def attendance_history(request):
    today = timezone.localdate()
    
    # Obtener el plan activo del estudiante
    active_plan = StudentPlan.objects.filter(
        student=request.user, 
        active=True
    ).select_related('plan').first()
    
    attendance_data = []
    summary = {
        'attended': 0,
        'pending': 0,
        'missed': 0,
        'total_days': 0
    }
    
    if active_plan:
        # Obtener todas las asistencias registradas en el rango del plan
        attendances = Attendance.objects.filter(
            student=request.user,
            date__range=[active_plan.start_date, active_plan.end_date]
        ).values_list('date', flat=True)
        attendances_set = set(attendances)
        
        # Generar lista de todas las fechas del plan (de más reciente a más antigua)
        current_date = active_plan.end_date
        while current_date >= active_plan.start_date:
            # Solo procesar días hábiles (Lunes a Viernes)
            if current_date.weekday() < 5:
                summary['total_days'] += 1
                
                status = 'pendiente'
                if current_date in attendances_set:
                    status = 'asistio'
                    summary['attended'] += 1
                elif current_date < today:
                    status = 'no_asistio'
                    summary['missed'] += 1
                else:
                    summary['pending'] += 1
                    
                attendance_data.append({
                    'date': current_date,
                    'status': status
                })
            current_date -= timedelta(days=1)
            
    context = {
        'active_plan': active_plan,
        'attendance_data': attendance_data,
        'summary': summary,
        'today': today
    }
    return render(request, 'attendance/attendance_history.html', context)

@login_required
@receptionist_required
def attendance_all(request):
    attendances = Attendance.objects.all().order_by('-date', '-created_at')
    return render(request, 'attendance/attendance_all.html', {'attendances': attendances})
