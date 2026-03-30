from django.contrib import admin
from .models import Property

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'property_type',
        'price',
        'city',
        'area',
        'subarea',
        'owner',
        'contact_name',
        'contact_phone',
        'wifi_available',
        'dog_allowed',
        'smoking_allowed',
        'garage_available',
        'music_allowed',
        'gate_close_time',
        'created_at',
        'is_published',
    )
    
    list_filter = (
        'property_type',
        'city',
        'area',
        'subarea',
        'is_published',
        'wifi_available',
        'dog_allowed',
        'smoking_allowed',
        'garage_available',
        'music_allowed',
    )
    
    search_fields = (
        'title',
        'description',
        'address',
        'contact_name',
        'contact_phone',
    )
