from django.contrib.auth.decorators import user_passes_test

def is_admin_or_cashier(user):
    return user.is_authenticated and (
        user.is_superuser or
        (hasattr(user, 'profile') and user.profile.role in ['admin', 'cashier'])
    )

def admin_or_cashier_required(view_func):
    return user_passes_test(is_admin_or_cashier, login_url='users:login')(view_func)