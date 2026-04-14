from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_reports_dashboard'),
    path('drilldown/', views.get_drilldown_data, name='drilldown_data'),
    path('general/', views.general_reports, name='general_reports'),
]
