from django.contrib import admin
from .models import Plan, StudentPlan

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'active')
    search_fields = ('name',)

@admin.register(StudentPlan)
class StudentPlanAdmin(admin.ModelAdmin):
    list_display = ('student', 'plan', 'start_date', 'end_date', 'active')
    list_filter = ('active', 'plan')
    search_fields = ('student__username', 'student__first_name', 'student__last_name')
