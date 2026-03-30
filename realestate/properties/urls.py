from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [

    # =============================
    # HOME PAGE
    # =============================
    path('', views.home, name='home'),

    # =============================
    # PROPERTY LIST & DETAIL
    # =============================
    path('properties/', views.property_list, name='property_list'),
    path('properties/add/', views.add_property, name='add_property'),
    path('properties/<slug:slug>/', views.property_detail, name='property_detail'),

    # =============================
    # USER DASHBOARD
    # =============================
    # path('dashboard/', views.user_dashboard, name='user_dashboard'),

    # Property Management
    path('dashboard/property/<slug:slug>/edit/', views.edit_property, name='edit_property'),
    path('dashboard/property/<slug:slug>/delete/', views.delete_property, name='delete_property'),
    path('dashboard/property/<slug:slug>/toggle/', views.toggle_property_status, name='toggle_property_status'),

    # =============================
    # AJAX (DYNAMIC DROPDOWNS)
    # =============================
    path('ajax/load-areas/', views.load_areas, name='ajax_load_areas'),
    path('ajax/load-subareas/', views.load_subareas, name='ajax_load_subareas'),
]