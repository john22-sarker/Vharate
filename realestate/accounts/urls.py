from django.urls import path
from .views import (
    signup_view,
    login_view,
    logout_view,
    user_dashboard,
    delete_property,
    toggle_property,
    edit_property_redirect,

    # 🔥 NEW (OTP VERIFY)
    verify_code_view,
)

app_name = 'accounts'

urlpatterns = [
    # =============================
    # AUTHENTICATION
    # =============================
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-reset-otp/', views.verify_reset_otp_view, name='verify_reset_otp'),
    path('reset-password/', views.reset_password_view, name='reset_password'),

    # 🔥 EMAIL OTP VERIFY
    path('verify-code/', verify_code_view, name='verify_code'),

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
