from django.urls import path
from . import views

app_name = 'locations'

urlpatterns = [
    path('areas/<int:city_id>/', views.get_areas, name='get_areas'),
    path('subareas/<int:area_id>/', views.get_subareas, name='get_subareas'),
]
