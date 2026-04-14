from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'plan', 'amount', 'start_date', 'date', 'registered_by')
    list_filter = ('plan', 'date', 'start_date')
    search_fields = ('student__username', 'student__first_name', 'student__last_name')
    date_hierarchy = 'date'
