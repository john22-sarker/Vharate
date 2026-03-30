from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # -----------------------------
    # Dashboard Home
    # -----------------------------
    path('', views.dashboard_home, name='dashboard_home'),

    # -----------------------------
    # User Management
    # -----------------------------
    path('toggle-user/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),

    # -----------------------------
    # Property Management
    # Using slug instead of ID
    # -----------------------------
    path('toggle-property/<slug:slug>/', views.toggle_property_status, name='toggle_property_status'),
    path('delete-property/<slug:slug>/', views.delete_property, name='delete_property'),

    # -----------------------------
    # City CRUD
    # -----------------------------
    path('cities/', views.manage_cities, name='manage_cities'),
    path('cities/edit/<int:city_id>/', views.edit_city, name='edit_city'),
    path('cities/delete/<int:city_id>/', views.delete_city, name='delete_city'),

    # -----------------------------
    # Area CRUD
    # -----------------------------
    path('areas/', views.manage_areas, name='manage_areas'),
    path('areas/edit/<int:area_id>/', views.edit_area, name='edit_area'),
    path('areas/delete/<int:area_id>/', views.delete_area, name='delete_area'),

    # -----------------------------
    # SubArea CRUD
    # -----------------------------
    path('subareas/', views.manage_subareas, name='manage_subareas'),
    path('subareas/edit/<int:subarea_id>/', views.edit_subarea, name='edit_subarea'),
    path('subareas/delete/<int:subarea_id>/', views.delete_subarea, name='delete_subarea'),

    # -----------------------------
    # Inline dashboard location management
    # -----------------------------
    path('locations/', views.dashboard_locations, name='dashboard_locations'),
]
