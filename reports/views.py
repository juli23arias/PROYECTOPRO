from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.decorators import admin_required
from accounts.models import User
from menu.models import Recipe, Menu
from attendance.models import Attendance
from payments.models import Payment
from plans.models import Plan, StudentPlan
from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay
from django.http import JsonResponse
from datetime import timedelta

@login_required
@admin_required
def admin_dashboard(request):
    today = timezone.localdate()
    
    # Si la petición es AJAX (JSON)
    if request.GET.get('format') == 'json':
        range_type = request.GET.get('range', 'week')
        start_date_str = request.GET.get('start')
        end_date_str = request.GET.get('end')
        
        today = timezone.localdate()
        start_date = today
        end_date = today
        
        if range_type == 'today':
            start_date = today
        elif range_type == 'week':
            start_date = today - timedelta(days=7)
        elif range_type == 'month':
            start_date = today - timedelta(days=30)
        elif range_type == 'year':
            start_date = today - timedelta(days=365)
        elif range_type == 'custom' and start_date_str and end_date_str:
            try:
                start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Ajuste de filtros según el tipo de dato
        p_filter = {'date__range': [start_date, end_date]}
        a_filter = {'date__range': [start_date, end_date]}
        
        # 1. Ingresos por Día
        income_query = Payment.objects.filter(**p_filter).annotate(
            day=TruncDay('date')
        ).values('day').annotate(total=Sum('amount')).order_by('day')
        
        income_data = {
            'labels': [item['day'].strftime('%d/%m') for item in income_query],
            'values': [float(item['total']) for item in income_query]
        }
        
        # 2. Planes Más Vendidos (Histórico en el rango)
        plans_query = Payment.objects.filter(date__gte=start_date, plan__isnull=False).values(
            'plan__name'
        ).annotate(count=Count('id')).order_by('-count')
        
        plans_data = {
            'labels': [item['plan__name'] for item in plans_query],
            'values': [item['count'] for item in plans_query]
        }
        
        # 3. Métodos de Pago
        methods_query = Payment.objects.filter(date__gte=start_date).values(
            'payment_method'
        ).annotate(count=Count('id'))
        
        methods_data = {
            'labels': [item['payment_method'].capitalize() for item in methods_query],
            'values': [item['count'] for item in methods_query]
        }
        
        # 4. Asistencias por Día
        attendance_query = Attendance.objects.filter(date__gte=start_date).annotate(
            day=TruncDay('date')
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        attendance_data = {
            'labels': [item['day'].strftime('%d/%m') for item in attendance_query],
            'values': [item['count'] for item in attendance_query]
        }
        
        # 5. Usuarios por Rol (Filtrar por fecha de registro si no es 'total')
        u_filter = {}
        if range_type != 'total':
            u_filter = {'date_joined__date__range': [start_date, end_date]}
            
        users_data = {
            'labels': [role[1] for role in User.ROLE_CHOICES],
            'values': [User.objects.filter(role=role[0], **u_filter).count() for role in User.ROLE_CHOICES]
        }
        
        # 6. Planes Activos (Suscripciones vigentes en el rango)
        active_plans_query = StudentPlan.objects.filter(
            active=True, 
            end_date__gte=start_date,
            start_date__lte=end_date
        ).values('plan__name').annotate(count=Count('id'))
        
        active_plans_data = {
            'labels': [item['plan__name'] for item in active_plans_query if item['plan__name']],
            'values': [item['count'] for item in active_plans_query if item['plan__name']]
        }

        return JsonResponse({
            'income': income_data,
            'plans': plans_data,
            'methods': methods_data,
            'attendance': attendance_data,
            'users': users_data,
            'active_plans': active_plans_data
        })

    # Estadísticas Generales para la carga inicial (Fuera del if JSON)
    total_students = User.objects.filter(role='estudiante', is_active=True).count()
    total_recipes = Recipe.objects.count()
    todays_attendances = Attendance.objects.filter(date=today).count()
    todays_payments_sum = Payment.objects.filter(date=today).aggregate(Sum('amount'))['amount__sum'] or 0.00
    active_plans_count = StudentPlan.objects.filter(active=True, end_date__gte=today).count()
    
    context = {
        'total_students': total_students,
        'total_recipes': total_recipes,
        'todays_attendances': todays_attendances,
        'todays_payments_sum': todays_payments_sum,
        'active_plans_count': active_plans_count,
        'today': today,
    }
    
    return render(request, 'reports/admin_dashboard.html', context)

@login_required
@admin_required
def get_drilldown_data(request):
    data_type = request.GET.get('type')
    key = request.GET.get('key')
    range_type = request.GET.get('range', 'week')
    
    today = timezone.localdate()
    start_date = today
    end_date = today
    
    if range_type == 'today':
        start_date = today
    elif range_type == 'week':
        start_date = today - timedelta(days=7)
    elif range_type == 'month':
        start_date = today - timedelta(days=30)
    elif range_type == 'year':
        start_date = today - timedelta(days=365)
    elif range_type == 'total':
        start_date = timezone.datetime(2000, 1, 1).date()
        end_date = today + timedelta(days=3650)
        
    results = []
    headers = []

    if data_type == 'income' or data_type == 'methods':
        payments = Payment.objects.all()
        if data_type == 'income':
            # Key is date string dd/mm
            day_str = key.split('/')
            target_date = timezone.datetime(today.year, int(day_str[1]), int(day_str[0])).date()
            payments = payments.filter(date=target_date)
            title = f"Pagos del {key}"
        else:
            # Key is payment method
            payments = payments.filter(payment_method=key.lower(), date__range=[start_date, end_date])
            title = f"Pagos con {key}"
            
        headers = ['Estudiante', 'Plan', 'Monto', 'Método', 'Fecha']
        for p in payments:
            results.append({
                'col1': p.student.get_full_name() or p.student.username,
                'col2': p.plan.name if p.plan else 'N/A',
                'col3': f"${p.amount}",
                'col4': p.payment_method.capitalize(),
                'col5': p.date.strftime('%d/%m/%Y')
            })

    elif data_type == 'plans' or data_type == 'active_plans':
        # Key is plan name
        student_plans = StudentPlan.objects.filter(plan__name=key)
        if data_type == 'active_plans':
            student_plans = student_plans.filter(active=True, end_date__gte=today)
        else:
            # Histórico en rango para Pagos de ese plan
            payments = Payment.objects.filter(plan__name=key, date__range=[start_date, end_date])
            # Extraer estudiantes únicos que pagaron ese plan en el rango
            student_ids = payments.values_list('student_id', flat=True).distinct()
            student_plans = StudentPlan.objects.filter(student_id__in=student_ids, plan__name=key)
            
        title = f"Estudiantes con {key}"
        headers = ['Estudiante', 'Usuario', 'Estado', 'Fecha Inicio', 'Fecha Fin']
        for sp in student_plans:
            results.append({
                'col1': sp.student.get_full_name() or sp.student.username,
                'col2': sp.student.username,
                'col3': 'Activo' if sp.active else 'Inactivo',
                'col4': sp.start_date.strftime('%d/%m/%Y') if sp.start_date else 'N/A',
                'col5': sp.end_date.strftime('%d/%m/%Y') if sp.end_date else 'N/A'
            })

    elif data_type == 'attendance':
        # Key is date string dd/mm
        day_str = key.split('/')
        target_date = today.replace(month=int(day_str[1]), day=int(day_str[0]))
        attendances = Attendance.objects.filter(date=target_date)
        title = f"Asistencias del {key}"
        headers = ['Estudiante', 'Plan', 'Fecha', 'Hora', 'Estado']
        for a in attendances:
            # Obtener el plan del estudiante (más reciente o activo)
            s_plan = StudentPlan.objects.filter(student=a.student, active=True).first()
            plan_name = s_plan.plan.name if s_plan else 'N/A'
            
            results.append({
                'col1': a.student.get_full_name() or a.student.username,
                'col2': plan_name,
                'col3': a.date.strftime('%d/%m/%Y'),
                'col4': timezone.localtime(a.created_at).strftime('%H:%M'),
                'col5': 'Asistió'
            })

    elif data_type == 'users':
        # Key is role name (from choices display)
        role_map = {v: k for k, v in User.ROLE_CHOICES}
        role_code = role_map.get(key)
        users = User.objects.filter(role=role_code)
        if range_type != 'total':
            users = users.filter(date_joined__date__range=[start_date, end_date])
            
        title = f"Usuarios: {key}"
        headers = ['Nombre', 'Usuario', 'Email', 'Fecha Registro', 'Estado']
        for u in users:
            results.append({
                'col1': u.get_full_name() or '--',
                'col2': u.username,
                'col3': u.email or '--',
                'col4': u.date_joined.strftime('%d/%m/%Y'),
                'col5': 'Activo' if u.is_active else 'Inactivo'
            })

    return JsonResponse({
        'title': title,
        'headers': headers,
        'results': results
    })

@login_required
@admin_required
def general_reports(request):
    report_type = request.GET.get('report', 'income')
    export_format = request.GET.get('export', '')
    
    # Filtros comunes
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    queryset = None
    title = ""
    columns = []
    
    if report_type == 'income' or report_type == 'transactions':
        method = request.GET.get('payment_method')
        queryset = Payment.objects.all().order_by('-date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if method:
            queryset = queryset.filter(payment_method=method)
            
        title = "Reporte de Ingresos" if report_type == 'income' else "Reporte de Transacciones"
        columns = ['Fecha', 'Estudiante', 'Plan', 'Método', 'Monto']
        
        data = []
        for p in queryset:
            data.append({
                'Fecha': p.date.strftime('%d/%m/%Y'),
                'Estudiante': p.student.get_full_name() or p.student.username,
                'Plan': p.plan.name if p.plan else 'N/A',
                'Método': p.get_payment_method_display(),
                'Monto': p.amount
            })
        total_sum = queryset.aggregate(Sum('amount'))['amount__sum'] or 0

    elif report_type == 'attendance':
        queryset = Attendance.objects.all().order_by('-date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        title = "Reporte de Asistencias"
        columns = ['Fecha', 'Estudiante', 'Plan']
        
        data = []
        for a in queryset:
            # Obtener plan activo del estudiante en esa fecha
            s_plan = StudentPlan.objects.filter(student=a.student, start_date__lte=a.date, end_date__gte=a.date).first()
            data.append({
                'Fecha': a.date.strftime('%d/%m/%Y'),
                'Estudiante': a.student.get_full_name() or a.student.username,
                'Plan': s_plan.plan.name if s_plan else 'N/A'
            })
        total_sum = queryset.count()

    elif report_type == 'plans':
        plan_id = request.GET.get('plan_type')
        queryset = Payment.objects.filter(plan__isnull=False).order_by('-date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if plan_id:
            queryset = queryset.filter(plan_id=plan_id)
            
        title = "Reporte de Planes Vendidos"
        columns = ['Estudiante', 'Plan', 'Fecha de Compra', 'Monto']
        
        data = []
        for p in queryset:
            data.append({
                'Estudiante': p.student.get_full_name() or p.student.username,
                'Plan': p.plan.name,
                'Fecha de Compra': p.date.strftime('%d/%m/%Y'),
                'Monto': p.amount
            })
        total_sum = queryset.aggregate(Sum('amount'))['amount__sum'] or 0

    elif report_type == 'users':
        role = request.GET.get('role')
        queryset = User.objects.all().order_by('-date_joined')
        if start_date:
            queryset = queryset.filter(date_joined__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date_joined__date__lte=end_date)
        if role:
            queryset = queryset.filter(role=role)
            
        title = "Reporte de Usuarios"
        columns = ['Código/ID', 'Nombre', 'Rol', 'Fecha Registro']
        
        data = []
        for u in queryset:
            data.append({
                'Código/ID': u.id,
                'Nombre': u.get_full_name() or u.username,
                'Rol': u.get_role_display(),
                'Fecha Registro': u.date_joined.strftime('%d/%m/%Y')
            })
        total_sum = queryset.count()

    # Lógica de Exportación
    if export_format == 'excel':
        import pandas as pd
        import io
        from django.http import HttpResponse

        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Reporte')
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={report_type}_report.xlsx'
        return response

    elif export_format == 'pdf':
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from django.http import HttpResponse
        import io

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
        elements = []
        styles = getSampleStyleSheet()

        # Estilo para títulos
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=1, # Center
            spaceAfter=20
        )
        
        # Estilo para metadatos del encabezado
        header_meta_style = ParagraphStyle(
            'HeaderMeta',
            fontSize=10,
            leading=12,
            alignment=0 # Left
        )

        # 1. Encabezado y Título
        elements.append(Paragraph("Restaurante Universitario", title_style))
        elements.append(Paragraph(f"<b>Reporte:</b> {title}", styles['Normal']))
        elements.append(Paragraph(f"<b>Generado por:</b> {request.user.get_full_name() or request.user.username}", styles['Normal']))
        elements.append(Paragraph(f"<b>Fecha de Generación:</b> {timezone.localtime(timezone.now()).strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        
        rango_str = f"{start_date or 'Inicio'} al {end_date or 'Fin'}"
        elements.append(Paragraph(f"<b>Rango del Reporte:</b> {rango_str}", styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))

        # 2. Preparar datos para la tabla
        table_data = [columns] # Encabezados
        for row in data:
            row_values = []
            for col_name in columns:
                val = row.get(col_name, '')
                # Formatear montos con separador de miles
                if col_name == 'Monto':
                    try:
                        val = f"${float(val):,.2f}"
                    except:
                        pass
                row_values.append(val)
            table_data.append(row_values)

        # 3. Crear y estilar la tabla
        # Ajustar anchos de columna proporcionalmente si es necesario
        col_widths = [None] * len(columns)
        table = Table(table_data, hAlign='LEFT', colWidths=col_widths)
        
        # Estilo de la tabla
        ts = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C41E3A')), # Rojo KFC/Docencia
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ])

        # Alternar colores de filas
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                ts.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f9fa'))

        # Alinear montos a la derecha si existe la columna Monto
        if 'Monto' in columns:
            m_idx = columns.index('Monto')
            ts.add('ALIGN', (m_idx, 1), (m_idx, -1), 'RIGHT')

        table.setStyle(ts)
        elements.append(table)
        elements.append(Spacer(1, 0.2 * inch))

        # 4. Resumen Final
        summary_text = ""
        if report_type in ['income', 'plans', 'transactions']:
            summary_text = f"<b>Total de Registros:</b> {len(data)} | <b>Total Recaudado:</b> ${total_sum:,.2f}"
        else:
            summary_text = f"<b>Total de Registros:</b> {len(data)}"
        
        elements.append(Paragraph(summary_text, styles['Normal']))

        # Construir PDF
        doc.build(elements)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={report_type}_report.pdf'
        response.write(buffer.getvalue())
        buffer.close()
        return response

    context = {
        'report_type': report_type,
        'title': title,
        'columns': columns,
        'data': data,
        'total_sum': total_sum,
        'start_date': start_date,
        'end_date': end_date,
        'payment_methods': Payment.PAYMENT_METHODS,
        'roles': User.ROLE_CHOICES,
        'plans_list': Plan.objects.all(),
        'today': timezone.localdate(),
    }
    
    return render(request, 'reports/general_reports.html', context)
