from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from core.decorators import admin_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from .models import User
from .forms import StudentRegistrationForm

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/landing.html')

@login_required
def dashboard(request):
    user = request.user
    
    # Redirección profesional directa por rol si es Admin
    if user.is_admin_role:
        return redirect('admin_reports_dashboard')
        
    context = {}
    
    if user.is_student:
        # Aquí se cargarán después datos del menú del día, plan activo, etc.
        context['role_title'] = "Panel de Estudiante"
    elif user.is_chef:
        context['role_title'] = "Panel de Cocina"
    elif user.is_receptionist:
        context['role_title'] = "Panel de Recepción"
    elif user.is_admin_role:
        context['role_title'] = "Panel de Administración"
        
    return render(request, 'accounts/dashboard.html', context)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Registro exitoso! Ahora puedes iniciar sesión como estudiante.')
            return redirect('login')
    else:
        form = StudentRegistrationForm()
        
    return render(request, 'accounts/register.html', {'form': form})

@login_required
@admin_required
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
@admin_required
def user_create(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST) 
        if form.is_valid():
            user = form.save(commit=False)
            user.role = request.POST.get('role', 'estudiante')
            user.cedula = form.cleaned_data.get('cedula')
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f'Usuario {user.username} creado con éxito.')
            return redirect('user_list')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'accounts/user_form.html', {
        'form': form, 
        'title': 'Crear Usuario',
        'roles': User.ROLE_CHOICES
    })

@login_required
@admin_required
def user_update(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        role = request.POST.get('role')
        user_obj.role = role
        user_obj.cedula = request.POST.get('cedula', user_obj.cedula)
        user_obj.first_name = request.POST.get('first_name', user_obj.first_name)
        user_obj.last_name = request.POST.get('last_name', user_obj.last_name)
        user_obj.email = request.POST.get('email', user_obj.email)
        user_obj.save()
        messages.success(request, f'Usuario {user_obj.username} actualizado.')
        return redirect('user_list')
    
    return render(request, 'accounts/user_form.html', {
        'user_obj': user_obj,
        'title': 'Editar Usuario',
        'roles': User.ROLE_CHOICES
    })

