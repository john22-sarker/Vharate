from django.urls import path
from .views import (
    signup_view,
    login_view,
    logout_view,
    user_dashboard,

    # 🔥 Property Actions
    delete_property,
    toggle_property,
    edit_property_redirect,
)

app_name = 'accounts'

from django.urls import path
from .views import (
    signup_view,
    login_view,
    logout_view,
    user_dashboard,
    delete_property,
    toggle_property,
    edit_property_redirect,
)

app_name = 'accounts'

urlpatterns = [
    # =============================
    # AUTHENTICATION
    # =============================
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # =============================
    # USER DASHBOARD
    # =============================
    path('dashboard/', user_dashboard, name='user_dashboard'),

    # =============================
    # PROPERTY MANAGEMENT
    # =============================
    path('property/delete/<int:id>/', delete_property, name='delete_property'),
    path('property/toggle/<int:id>/', toggle_property, name='toggle_property'),
    path('property/edit/<int:id>/', edit_property_redirect, name='edit_property'),
]