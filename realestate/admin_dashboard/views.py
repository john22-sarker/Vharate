from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
from django import forms
from datetime import timedelta

from properties.models import Property
from locations.models import City, Area, SubArea

# -----------------------------
# Admin Access Decorator
# -----------------------------
def superuser_required(view_func):
    """Decorator to allow only superusers to access a view."""
    return user_passes_test(lambda u: u.is_superuser)(view_func)

# -----------------------------
# Dashboard Home
# -----------------------------
@superuser_required
def dashboard_home(request):
    """Render the admin dashboard with stats and recent objects."""
    # Property stats
    total_properties = Property.objects.count()
    active_properties = Property.objects.filter(is_published=True).count()
    inactive_properties = Property.objects.filter(is_published=False).count()
    recent_properties_list = Property.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=1)
    ).order_by('-created_at')

    # User stats
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()
    all_users = User.objects.all().order_by('-date_joined')

    # Location stats
    total_cities = City.objects.count()
    total_areas = Area.objects.count()
    total_subareas = SubArea.objects.count()

    context = {
        'total_properties': total_properties,
        'active_properties': active_properties,
        'inactive_properties': inactive_properties,
        'recent_properties_list': recent_properties_list,
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'all_users': all_users,
        'total_cities': total_cities,
        'total_areas': total_areas,
        'total_subareas': total_subareas,
    }
    return render(request, 'admin_dashboard/dashboard_home.html', context)

# -----------------------------
# User Management
# -----------------------------
@superuser_required
def toggle_user_status(request, user_id):
    """Activate or deactivate a user (except superusers)."""
    user_obj = get_object_or_404(User, pk=user_id)
    if user_obj.is_superuser:
        messages.error(request, "Cannot deactivate a superuser!")
    else:
        user_obj.is_active = not user_obj.is_active
        user_obj.save()
        status = "activated" if user_obj.is_active else "deactivated"
        messages.success(request, f"User {status} successfully.")
    return redirect('admin_dashboard:dashboard_home')


@superuser_required
def delete_user(request, user_id):
    """Delete a user (except superusers)."""
    user_obj = get_object_or_404(User, pk=user_id)
    if user_obj.is_superuser:
        messages.error(request, "Cannot delete a superuser!")
    else:
        user_obj.delete()
        messages.success(request, f"User '{user_obj.username}' deleted successfully.")
    return redirect('admin_dashboard:dashboard_home')

# -----------------------------
# Property Management
# -----------------------------
@superuser_required
def toggle_property_status(request, slug):
    """Activate or deactivate a property using slug."""
    prop = get_object_or_404(Property, slug=slug)
    prop.is_published = not prop.is_published
    prop.save()
    status = "activated" if prop.is_published else "deactivated"
    messages.success(request, f"Property '{prop.title}' {status} successfully.")
    return redirect('admin_dashboard:dashboard_home')


@superuser_required
def delete_property(request, slug):
    """Delete a property using slug."""
    prop = get_object_or_404(Property, slug=slug)
    prop.delete()
    messages.success(request, f"Property '{prop.title}' deleted successfully.")
    return redirect('admin_dashboard:dashboard_home')

# -----------------------------
# Location Forms
# -----------------------------
class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name']

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['city', 'name']

class SubAreaForm(forms.ModelForm):
    class Meta:
        model = SubArea
        fields = ['area', 'name']

# -----------------------------
# City CRUD
# -----------------------------
@superuser_required
def manage_cities(request):
    cities = City.objects.all()
    form = CityForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "City added successfully!")
        return redirect('admin_dashboard:manage_cities')
    return render(request, 'admin_dashboard/manage_cities.html', {'cities': cities, 'form': form})


@superuser_required
def edit_city(request, city_id):
    city = get_object_or_404(City, id=city_id)
    form = CityForm(request.POST or None, instance=city)
    if form.is_valid():
        form.save()
        messages.success(request, "City updated successfully!")
        return redirect('admin_dashboard:manage_cities')
    return render(request, 'admin_dashboard/edit_city.html', {'form': form})


@superuser_required
def delete_city(request, city_id):
    city = get_object_or_404(City, id=city_id)
    city.delete()
    messages.success(request, "City deleted successfully!")
    return redirect('admin_dashboard:manage_cities')

# -----------------------------
# Area CRUD
# -----------------------------
@superuser_required
def manage_areas(request):
    areas = Area.objects.all()
    form = AreaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Area added successfully!")
        return redirect('admin_dashboard:manage_areas')
    return render(request, 'admin_dashboard/manage_areas.html', {'areas': areas, 'form': form})


@superuser_required
def edit_area(request, area_id):
    area = get_object_or_404(Area, id=area_id)
    form = AreaForm(request.POST or None, instance=area)
    if form.is_valid():
        form.save()
        messages.success(request, "Area updated successfully!")
        return redirect('admin_dashboard:manage_areas')
    return render(request, 'admin_dashboard/edit_area.html', {'form': form})


@superuser_required
def delete_area(request, area_id):
    area = get_object_or_404(Area, id=area_id)
    area.delete()
    messages.success(request, "Area deleted successfully!")
    return redirect('admin_dashboard:manage_areas')

# -----------------------------
# SubArea CRUD
# -----------------------------
@superuser_required
def manage_subareas(request):
    subareas = SubArea.objects.all()
    form = SubAreaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Sub-Area added successfully!")
        return redirect('admin_dashboard:manage_subareas')
    return render(request, 'admin_dashboard/manage_subareas.html', {'subareas': subareas, 'form': form})


@superuser_required
def edit_subarea(request, subarea_id):
    subarea = get_object_or_404(SubArea, id=subarea_id)
    form = SubAreaForm(request.POST or None, instance=subarea)
    if form.is_valid():
        form.save()
        messages.success(request, "Sub-Area updated successfully!")
        return redirect('admin_dashboard:manage_subareas')
    return render(request, 'admin_dashboard/edit_subarea.html', {'form': form})


@superuser_required
def delete_subarea(request, subarea_id):
    subarea = get_object_or_404(SubArea, id=subarea_id)
    subarea.delete()
    messages.success(request, "Sub-Area deleted successfully!")
    return redirect('admin_dashboard:manage_subareas')

# -----------------------------
# Inline Dashboard Location Management
# -----------------------------
@superuser_required
def dashboard_locations(request):
    """Add cities, areas, or subareas directly from the dashboard."""
    cities = City.objects.all()
    areas = Area.objects.all()
    subareas = SubArea.objects.all()

    if request.method == 'POST':
        # Add city
        if 'add_city' in request.POST:
            name = request.POST.get('city_name')
            if name:
                City.objects.create(name=name)
                messages.success(request, f'City "{name}" added successfully.')
                return redirect('admin_dashboard:dashboard_locations')

        # Add area
        if 'add_area' in request.POST:
            name = request.POST.get('area_name')
            city_id = request.POST.get('area_city')
            if name and city_id:
                city = get_object_or_404(City, id=city_id)
                Area.objects.create(name=name, city=city)
                messages.success(request, f'Area "{name}" added under "{city.name}".')
                return redirect('admin_dashboard:dashboard_locations')

        # Add subarea
        if 'add_subarea' in request.POST:
            name = request.POST.get('subarea_name')
            area_id = request.POST.get('subarea_area')
            if name and area_id:
                area = get_object_or_404(Area, id=area_id)
                SubArea.objects.create(name=name, area=area)
                messages.success(request, f'Sub-Area "{name}" added under "{area.name}".')
                return redirect('admin_dashboard:dashboard_locations')

    context = {'cities': cities, 'areas': areas, 'subareas': subareas}
    return render(request, 'admin_dashboard/dashboard_locations.html', context)







