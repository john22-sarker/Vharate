from django.contrib import admin
from .models import City, Area, SubArea

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')
    list_filter = ('city',)
    search_fields = ('name',)


@admin.register(SubArea)
class SubAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'area', 'city')
    list_filter = ('area__city', 'area',)
    search_fields = ('name',)
    
    # Show city column dynamically
    def city(self, obj):
        return obj.area.city
