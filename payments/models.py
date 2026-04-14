from django.db import models
from django.conf import settings
from django.utils import timezone

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'estudiante'}, related_name='payments')
    plan = models.ForeignKey('plans.Plan', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Plan Adquirido")
    amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Monto")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='efectivo', verbose_name="Método de Pago")
    start_date = models.DateField(default=timezone.localdate, verbose_name="Fecha de Inicio del Plan")
    date = models.DateField(default=timezone.localdate, verbose_name="Fecha de Pago")
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='registered_payments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        plan_name = self.plan.name if self.plan else "Suelto"
        return f"Pago {plan_name} - {self.student.get_full_name()} (${self.amount})"

class CashClosing(models.Model):
    date = models.DateField(unique=True, default=timezone.localdate, verbose_name="Fecha de Cierre")
    total_payments = models.PositiveIntegerField(verbose_name="Número de Pagos")
    total_cash = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Efectivo")
    total_transfer = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Transferencia")
    total_card = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Tarjeta")
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total General")
    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Cerrado por")
    closed_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha/Hora de Cierre")

    class Meta:
        verbose_name = "Cierre de Caja"
        verbose_name_plural = "Cierres de Caja"
        ordering = ['-date']

    def __str__(self):
        return f"Cierre {self.date} - ${self.grand_total}"
