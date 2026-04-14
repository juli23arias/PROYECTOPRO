from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'signed', 'registered_by', 'created_at')
    list_filter = ('date', 'signed')
    search_fields = ('student__username', 'student__first_name', 'student__last_name')
    date_hierarchy = 'date'
