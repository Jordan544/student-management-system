from django.core.exceptions import PermissionDenied

def role_required(allowed_roles=[]):
    """
    Decorator for views that checks whether a user belongs to a specific group,
    redirecting or raising PermissionDenied if not.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                # Superusers automatically pass(create superuser jordan)
                if request.user.is_superuser:
                    return view_func(request, *args, **kwargs)
                
                # Check if user is in any of the allowed groups
                if request.user.groups.filter(name__in=allowed_roles).exists():
                    return view_func(request, *args, **kwargs)
                    
            raise PermissionDenied
        return _wrapped_view
    return decorator