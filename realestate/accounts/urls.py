from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [

    # =============================
    # AUTHENTICATION
    # =============================
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # =============================
    # EMAIL VERIFICATION
    # =============================
    path('verify-code/', views.verify_code_view, name='verify_code'),

    # =============================
    # PASSWORD RESET
    # =============================
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-reset-otp/', views.verify_reset_otp_view, name='verify_reset_otp'),
    path('reset-password/', views.reset_password_view, name='reset_password'),

    # =============================
    # DASHBOARD
    # =============================
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    # =============================
    # PROPERTY MANAGEMENT
    # =============================
    # path('property/delete/<int:id>/', views.delete_property, name='delete_property'),
    path('property/toggle/<int:id>/', views.toggle_property, name='toggle_property'),
    path('property/edit/<int:id>/', views.edit_property_redirect, name='edit_property'),
]
