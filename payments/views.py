from django.shortcuts import render, redirect
from django.db.models import Q, Sum
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from core.decorators import receptionist_required, student_required
from .models import Payment, CashClosing
from .forms import PaymentForm
from accounts.models import User
from plans.models import Plan, StudentPlan
from core.utils import add_business_days

@login_required
@receptionist_required
def payment_register(request):
    today = timezone.localdate()
    is_closed = CashClosing.objects.filter(date=today).exists()
    
    if is_closed and request.method == 'POST':
        messages.error(request, "No se pueden registrar pagos: La caja de este día ya está cerrada.")
        return redirect('payment_register')

    search_query = request.GET.get('q', '').strip()
    
    selected_student = None
    if search_query:
        # Búsqueda exacta por cédula o username
        selected_student = User.objects.filter(
            Q(cedula=search_query) | Q(username=search_query),
            role='estudiante', 
            is_active=True
        ).first()
        
        if not selected_student:
            messages.error(request, f'No se encontró ningún estudiante con el código: {search_query}')

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.registered_by = request.user
            payment.date = today  # Fecha de pago es hoy siempre
            payment.save()
            
            # Activar el plan del estudiante si se seleccionó uno
            if payment.plan:
                # Desactivar planes anteriores del estudiante para evitar duplicados activos
                StudentPlan.objects.filter(student=payment.student, active=True).update(active=False)
                
                # Calcular fecha de fin basada en la duración del plan (Solo días hábiles)
                end_date = add_business_days(payment.start_date, payment.plan.duration_days)
                
                # Crear la asignación del plan
                StudentPlan.objects.create(
                    student=payment.student,
                    plan=payment.plan,
                    start_date=payment.start_date,
                    end_date=end_date,
                    active=True
                )
                messages.success(request, f'Pago registrado y Plan "{payment.plan.name}" ACTIVADO para {payment.student.get_full_name()}. Expira el {end_date}.')
            else:
                messages.success(request, f'Pago de ${payment.amount} registrado para {payment.student.get_full_name()}.')
            
            return redirect('payment_register')
        else:
            # Si el formulario es inválido, recuperamos el estudiante para no perder el contexto en la UI
            student_id = request.POST.get('student')
            if student_id:
                selected_student = User.objects.filter(id=student_id).first()
            print(f"DEBUG: Form invalid. Errors: {form.errors}")
            messages.error(request, f"Error al registrar el pago: {form.errors.as_text()}")
    else:
        # Inicializar form con el estudiante seleccionado si existe
        initial_data = {
            'date': today, 
            'start_date': today, # Sugerimos hoy como inicio
            'amount': 0.00
        }
        if selected_student:
            initial_data['student'] = selected_student
            
        form = PaymentForm(initial=initial_data)

    if selected_student:
        # Si hay un estudiante seleccionado (sea por GET o por re-render de POST inválido)
        # limitamos el queryset del form a ese estudiante
        form.fields['student'].queryset = User.objects.filter(id=selected_student.id)

    recent_payments = Payment.objects.all().select_related('student', 'plan').order_by('-created_at')[:20]
    plans = Plan.objects.filter(active=True)
    import json
    plans_json = json.dumps({p.id: {'price': float(p.price), 'duration': p.duration_days} for p in plans})
    
    context = {
        'form': form,
        'payments': recent_payments,
        'plans_json': plans_json,
        'selected_student': selected_student,
        'search_query': search_query,
        'is_closed': is_closed,
    }
    return render(request, 'payments/payment_register.html', context)

@login_required
@student_required
def payment_history(request):
    # Obtener el plan activo actual
    active_plan = StudentPlan.objects.filter(
        student=request.user,
        active=True
    ).select_related('plan').first()
    
    payments = Payment.objects.filter(student=request.user).select_related('plan').order_by('-date', '-created_at')
    
    total_amount = sum(p.amount for p in payments)
    
    context = {
        'active_plan': active_plan,
        'payments': payments,
        'total_amount': total_amount,
    }
    return render(request, 'payments/payment_history.html', context)

@login_required
@receptionist_required
def payment_all(request):
    payments = Payment.objects.all().order_by('-date', '-created_at')
    total_amount = sum(p.amount for p in payments)
    
    context = {
        'payments': payments,
        'total_amount': total_amount,
    }
    return render(request, 'payments/payment_all.html', context)

@login_required
@receptionist_required
def daily_cash(request):
    today = timezone.localdate()
    is_closed = CashClosing.objects.filter(date=today).exists()
    
    # Cálculos dinámicos del día
    day_payments = Payment.objects.filter(date=today)
    
    stats = {
        'total_count': day_payments.count(),
        'cash': day_payments.filter(payment_method='efectivo').aggregate(total=Sum('amount'))['total'] or 0,
        'transfer': day_payments.filter(payment_method='transferencia').aggregate(total=Sum('amount'))['total'] or 0,
        'card': day_payments.filter(payment_method='tarjeta').aggregate(total=Sum('amount'))['total'] or 0,
    }
    stats['grand_total'] = stats['cash'] + stats['transfer'] + stats['card']
    
    context = {
        'today': today,
        'stats': stats,
        'is_closed': is_closed,
        'recent_payments': day_payments.select_related('student', 'plan').order_by('-created_at')
    }
    return render(request, 'payments/daily_cash.html', context)

@login_required
@receptionist_required
def close_cash(request):
    if request.method == 'POST':
        today = timezone.localdate()
        
        if CashClosing.objects.filter(date=today).exists():
            messages.warning(request, "La caja de hoy ya se encuentra cerrada.")
            return redirect('daily_cash')
            
        # Calcular totales finales
        day_payments = Payment.objects.filter(date=today)
        total_payments = day_payments.count()
        
        if total_payments == 0:
            messages.error(request, "No se puede cerrar una caja sin transacciones.")
            return redirect('daily_cash')
            
        total_cash = day_payments.filter(payment_method='efectivo').aggregate(total=Sum('amount'))['total'] or 0
        total_transfer = day_payments.filter(payment_method='transferencia').aggregate(total=Sum('amount'))['total'] or 0
        total_card = day_payments.filter(payment_method='tarjeta').aggregate(total=Sum('amount'))['total'] or 0
        grand_total = total_cash + total_transfer + total_card
        
        CashClosing.objects.create(
            date=today,
            total_payments=total_payments,
            total_cash=total_cash,
            total_transfer=total_transfer,
            total_card=total_card,
            grand_total=grand_total,
            closed_by=request.user
        )
        
        messages.success(request, f"¡Caja cerrada correctamente! Total recaudado: ${grand_total}")
        return redirect('cash_history')
        
    return redirect('daily_cash')

@login_required
@receptionist_required
def cash_history(request):
    history = CashClosing.objects.all().select_related('closed_by')
    return render(request, 'payments/cash_history.html', {'history': history})
