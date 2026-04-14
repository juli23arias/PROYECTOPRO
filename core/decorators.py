from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles):
    """
    Decorador para verificar si el usuario tiene un rol específico.
    allowed_roles puede ser un string o una lista de strings con los roles permitidos.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
                
            roles = allowed_roles if isinstance(allowed_roles, list) else [allowed_roles]
            
            # El administrador siempre tiene acceso a todo si se configuran así los permisos
            # Puedes quitar esta linea si deseas restricciones más estrictas incluso para el admin.
            if request.user.is_admin_role or request.user.role in roles:
                return view_func(request, *args, **kwargs)
                
            raise PermissionDenied
        return _wrapped_view
    return decorator

# Helpers para uso rápido
def student_required(view_func):
    return role_required(['estudiante'])(view_func)

def chef_required(view_func):
    return role_required(['chef'])(view_func)

def receptionist_required(view_func):
    return role_required(['recepcionista'])(view_func)

def admin_required(view_func):
    return role_required(['administrador'])(view_func)
