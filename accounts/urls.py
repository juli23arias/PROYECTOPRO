from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from .views import CustomLoginView, dashboard, register_view, landing_page, user_list, user_create, user_update

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('registro/', register_view, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    
    # Password Reset Flow
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),

    path('usuarios/', user_list, name='user_list'),
    path('usuarios/nuevo/', user_create, name='user_create'),
    path('usuarios/editar/<int:pk>/', user_update, name='user_update'),
    path('', landing_page, name='landing'),
]
