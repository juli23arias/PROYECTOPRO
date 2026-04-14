from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from core.decorators import admin_required, student_required, receptionist_required
from core.utils import add_business_days
from .models import Plan, StudentPlan
from .forms import PlanForm, StudentPlanForm

# --- VISTAS DEL ADMINISTRADOR (Gestión de Catálogo) ---

@login_required
@admin_required
def plan_list(request):
    plans = Plan.objects.all()
    # Listado de todas las asignaciones para el admin
    student_plans = StudentPlan.objects.select_related('student', 'plan').all().order_by('-start_date')
    return render(request, 'plans/plan_list.html', {'plans': plans, 'student_plans': student_plans})

@login_required
@admin_required
def plan_create(request):
    if request.method == 'POST':
        form = PlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan creado exitosamente.')
            return redirect('plan_list')
    else:
        form = PlanForm()
    return render(request, 'plans/plan_form.html', {'form': form, 'title': 'Nuevo Plan'})

@login_required
@admin_required
def plan_update(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    if request.method == 'POST':
        form = PlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan actualizado exitosamente.')
            return redirect('plan_list')
    else:
        form = PlanForm(instance=plan)
    return render(request, 'plans/plan_form.html', {'form': form, 'title': 'Editar Plan'})


# --- VISTAS DEL RECEPCIONISTA (Asignación) ---

@login_required
@receptionist_required
def student_plan_assign(request):
    # El recepcionista puede venir desde el buscador de asistencia con un estudiante ya seleccionado
    student_id = request.GET.get('student_id')
    initial_data = {}
    if student_id:
        initial_data['student'] = student_id

    if request.method == 'POST':
        form = StudentPlanForm(request.POST)
        if form.is_valid():
            # Desactivar planes anteriores del estudiante para evitar duplicados activos
            student = form.cleaned_data['student']
            StudentPlan.objects.filter(student=student, active=True).update(active=False)

            student_plan = form.save(commit=False)
            student_plan.active = True  # Asegurar que el nuevo plan esté activo
            # Cálculo automático de fecha de fin basada en el plan seleccionado (Días hábiles)
            plan = student_plan.plan
            student_plan.end_date = add_business_days(student_plan.start_date, plan.duration_days)
            student_plan.save()
            
            messages.success(request, f'Plan "{plan.name}" asignado a {student_plan.student.get_full_name()}. Vencimiento: {student_plan.end_date}')
            
            # Redirigir de vuelta al registro de asistencia para mayor fluidez
            return redirect(f"/asistencias/registrar/?q={student_plan.student.cedula or student_plan.student.username}")
    else:
        form = StudentPlanForm(initial=initial_data)
    
    return render(request, 'plans/student_plan_form.html', {
        'form': form, 
        'title': 'Asignar Plan a Estudiante'
    })


@login_required
@admin_required
def student_plan_delete(request, pk):
    student_plan = get_object_or_404(StudentPlan, pk=pk)
    student_name = student_plan.student.get_full_name()
    plan_name = student_plan.plan.name
    student_plan.delete()
    messages.success(request, f'Se ha eliminado el plan "{plan_name}" de {student_name} correctamente.')
    return redirect('plan_list')


# --- VISTAS DEL ESTUDIANTE ---

@login_required
@student_required
def my_plan(request):
    # Mostrar planes activos y vencidos del estudiante
    all_plans = StudentPlan.objects.filter(student=request.user).order_by('-active', '-end_date')
    active_plan = all_plans.filter(active=True).first()
    past_plans = all_plans.filter(active=False)
    
    context = {
        'active_plan': active_plan,
        'past_plans': past_plans,
    }
    return render(request, 'plans/my_plan.html', context)
