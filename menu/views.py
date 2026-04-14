from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import datetime
from core.decorators import chef_required
from .models import Recipe, Menu
from .forms import RecipeForm, MenuForm

@login_required
@chef_required
def recipe_list(request):
    recipes = Recipe.objects.all().order_by('-created_at')
    return render(request, 'menu/recipe_list.html', {'recipes': recipes})

@login_required
@chef_required
def recipe_create(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.created_by = request.user
            recipe.save()
            messages.success(request, 'Receta creada exitosamente.')
            return redirect('recipe_list')
    else:
        form = RecipeForm()
    return render(request, 'menu/recipe_form.html', {'form': form, 'title': 'Nueva Receta'})

@login_required
@chef_required
def recipe_update(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        form = RecipeForm(request.POST, instance=recipe)
        if form.is_valid():
            form.save()
            messages.success(request, 'Receta actualizada exitosamente.')
            return redirect('recipe_list')
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'menu/recipe_form.html', {'form': form, 'title': 'Editar Receta'})

@login_required
@chef_required
def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        recipe.delete()
        messages.success(request, 'Receta eliminada exitosamente.')
        return redirect('recipe_list')
    return render(request, 'menu/recipe_confirm_delete.html', {'recipe': recipe})

@login_required
@chef_required
def menu_weekly(request):
    # Obtener el año y la semana actual, o permitirlos por GET param
    today = timezone.now().date()
    today_year = today.year
    today_week = today.isocalendar()[1]
    
    year = int(request.GET.get('year', today_year))
    week = int(request.GET.get('week', today_week))
    
    # Lógica de navegación de semanas
    current_date = datetime.date.fromisocalendar(year, week, 1)
    prev_week_date = current_date - datetime.timedelta(weeks=1)
    next_week_date = current_date + datetime.timedelta(weeks=1)
    
    prev_year, prev_week, _ = prev_week_date.isocalendar()
    next_year, next_week, _ = next_week_date.isocalendar()

    # Etiquetas dinámicas (requerimiento de optimización)
    if year == today_year and week == today_week:
        week_label = "Semana Actual"
    elif year == today_year and week == today_week - 1:
        week_label = "Semana Pasada"
    elif year == today_year and week < today_week - 1:
        week_label = "Semanas Pasadas"
    elif year == today_year and week == today_week + 1:
        week_label = "Semana Próxima"
    elif year == today_year and week > today_week + 1:
        week_label = "Semanas Futuras"
    else:
        week_label = f"Archivo {year}"

    menus_qs = Menu.objects.filter(year=year, week_number=week)
    menus_dict = {m.day_of_week: m for m in menus_qs}
    
    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.created_by = request.user
            # Manejar la duplicidad
            Menu.objects.filter(day_of_week=menu_item.day_of_week, week_number=menu_item.week_number, year=menu_item.year).delete()
            menu_item.save()
            messages.success(request, f'Menú de {menu_item.get_day_of_week_display()} guardado.')
            return redirect(f"{request.path}?year={year}&week={week}")
    else:
        form = MenuForm(initial={'year': year, 'week_number': week})
    
    context = {
        'menus': menus_dict,
        'form': form,
        'year': year,
        'week': week,
        'week_label': week_label,
        'prev_year': prev_year,
        'prev_week': prev_week,
        'next_year': next_year,
        'next_week': next_week,
        'is_today_week': (year == today_year and week == today_week),
        'days': Menu.DAYS_OF_WEEK,
        'recipes': Recipe.objects.all().order_by('name'),
    }
    return render(request, 'menu/menu_weekly.html', context)

@login_required
@chef_required
def menu_delete(request, pk):
    menu_item = get_object_or_404(Menu, pk=pk)
    year, week = menu_item.year, menu_item.week_number
    if request.method == 'POST':
        menu_item.delete()
        messages.success(request, 'Menú eliminado correctamente.')
    return redirect(f"{reverse_lazy('menu_weekly')}?year={year}&week={week}")

@login_required
@chef_required
def menu_history(request):
    # Agrupar menús por año y semana
    history_distinct = Menu.objects.values('year', 'week_number').distinct().order_by('-year', '-week_number')
    
    history_data = []
    for item in history_distinct:
        y, w = item['year'], item['week_number']
        count = Menu.objects.filter(year=y, week_number=w).count()
        # Obtener un nombre de receta ejemplo para el listado
        sample = Menu.objects.filter(year=y, week_number=w).first()
        history_data.append({
            'year': y,
            'week': w,
            'count': count,
            'sample_recipe': sample.recipe.name if sample else "Vacio"
        })

    return render(request, 'menu/menu_history.html', {'history': history_data})

@login_required
def menu_view(request):
    today = timezone.now().date()
    today_year = today.year
    today_week = today.isocalendar()[1]
    
    year = int(request.GET.get('year', today_year))
    week = int(request.GET.get('week', today_week))
    
    # Lógica de navegación de semanas
    current_date = datetime.date.fromisocalendar(year, week, 1)
    prev_week_date = current_date - datetime.timedelta(weeks=1)
    next_week_date = current_date + datetime.timedelta(weeks=1)
    
    prev_year, prev_week, _ = prev_week_date.isocalendar()
    next_year, next_week, _ = next_week_date.isocalendar()

    # Etiquetas dinámicas
    if year == today_year and week == today_week:
        week_label = "Semana Actual"
    elif year == today_year and week == today_week - 1:
        week_label = "Semana Pasada"
    elif year == today_year and week < today_week - 1:
        week_label = "Semanas Pasadas"
    elif year == today_year and week == today_week + 1:
        week_label = "Semana Próxima"
    elif year == today_year and week > today_week + 1:
        week_label = "Semanas Futuras"
    else:
        week_label = f"Archivo {year}"
    
    # Obtener menús publicados y convertirlos a diccionario para el filtro get_item
    menus_qs = Menu.objects.filter(year=year, week_number=week, is_published=True)
    menus_dict = {m.day_of_week: m for m in menus_qs}
    
    context = {
        'menus': menus_dict,
        'days': Menu.DAYS_OF_WEEK,
        'year': year,
        'week': week,
        'week_label': week_label,
        'prev_year': prev_year,
        'prev_week': prev_week,
        'next_year': next_year,
        'next_week': next_week,
        'is_today_week': (year == today_year and week == today_week),
        'current_year': year, # Para compatibilidad con template si usa otros nombres
        'current_week': week,
    }
    return render(request, 'menu/menu_view.html', context)
