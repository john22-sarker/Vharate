from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse

from .models import Property
from .forms import PropertyForm
from locations.models import City, Area, SubArea


# =============================
# HOME PAGE
# =============================
def home(request):
    properties = Property.objects.filter(
        is_published=True
    ).select_related('city', 'area').order_by('-created_at')[:6]

    cities = City.objects.all()

    top_cities = City.objects.annotate(
        property_count=Count('properties')
    ).order_by('-property_count')[:5]

    property_types = Property.objects.values('property_type').annotate(
        count=Count('id')
    ).order_by('-count')

    context = {
        'properties': properties,
        'cities': cities,
        'top_cities': top_cities,
        'property_types': property_types,
    }
    return render(request, 'home.html', context)


# =============================
# PROPERTY LIST
# =============================
def property_list(request):
    properties = Property.objects.filter(
        is_published=True
    ).select_related('city', 'area', 'subarea').order_by('-created_at')

    query = request.GET.get('q', '')
    if query:
        properties = properties.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(contact_name__icontains=query)
        )

    property_type = request.GET.get('property_type')
    city_id = request.GET.get('city')
    area_id = request.GET.get('area')
    subarea_id = request.GET.get('subarea')

    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')

    bedrooms = request.GET.get('bedrooms')
    bathrooms = request.GET.get('bathrooms')

    if property_type:
        properties = properties.filter(property_type=property_type)

    if city_id:
        properties = properties.filter(city_id=city_id)

    if area_id:
        properties = properties.filter(area_id=area_id)

    if subarea_id:
        properties = properties.filter(subarea_id=subarea_id)

    if price_min:
        properties = properties.filter(price__gte=price_min)

    if price_max:
        properties = properties.filter(price__lte=price_max)

    if bedrooms:
        properties = properties.filter(rooms=bedrooms)

    if bathrooms:
        properties = properties.filter(bathrooms=bathrooms)

    cities = City.objects.all()
    areas = Area.objects.filter(city_id=city_id) if city_id else Area.objects.none()
    subareas = SubArea.objects.filter(area_id=area_id) if area_id else SubArea.objects.none()

    paginator = Paginator(properties, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'properties': page_obj,
        'page_obj': page_obj,
        'cities': cities,
        'areas': areas,
        'subareas': subareas,
        'query': query,
        'filters': {
            'property_type': property_type or '',
            'city': city_id or '',
            'area': area_id or '',
            'subarea': subarea_id or '',
            'price_min': price_min or '',
            'price_max': price_max or '',
            'bedrooms': bedrooms or '',
            'bathrooms': bathrooms or '',
        }
    }

    return render(request, 'property_list.html', context)


# =============================
# AJAX
# =============================
def load_areas(request):
    city_id = request.GET.get('city_id')
    areas = Area.objects.filter(city_id=city_id).values('id', 'name')
    return JsonResponse(list(areas), safe=False)


def load_subareas(request):
    area_id = request.GET.get('area_id')
    subareas = SubArea.objects.filter(area_id=area_id).values('id', 'name')
    return JsonResponse(list(subareas), safe=False)


# =============================
# PROPERTY DETAIL
# =============================
def property_detail(request, slug):
    property_obj = get_object_or_404(Property, slug=slug)

    # unpublished হলে owner ছাড়া কেউ দেখতে পারবে না
    if not property_obj.is_published and property_obj.owner != request.user:
        return render(request, '404.html')

    return render(request, 'property_detail.html', {'property': property_obj})


# =============================
# ADD PROPERTY (🔥 UPDATED)
# =============================
@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user

            # 🔥 AUTO DATA FROM PROFILE
            profile = request.user.profile

            if not property_obj.contact_name:
                property_obj.contact_name = profile.full_name

            if not property_obj.contact_phone:
                property_obj.contact_phone = profile.phone_number

            if not property_obj.contact_email:
                property_obj.contact_email = request.user.email

            property_obj.save()

            messages.success(request, 'Property added successfully.')
            return redirect('properties:property_detail', slug=property_obj.slug)

        else:
            messages.error(request, 'Please fix the errors below.')

    else:
        form = PropertyForm(user=request.user)

    return render(request, 'add_property.html', {'form': form})


# =============================
# USER DASHBOARD
# =============================
@login_required
def user_dashboard(request):
    properties = Property.objects.filter(
        owner=request.user
    ).select_related('city', 'area').order_by('-created_at')

    context = {
        'properties': properties,
        'total_properties': properties.count(),
        'active_properties': properties.filter(is_published=True).count(),
        'inactive_properties': properties.filter(is_published=False).count(),
    }

    return render(request, 'dashboard.html', context)


# =============================
# EDIT PROPERTY
# =============================
@login_required
def edit_property(request, slug):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        owner=request.user
    )

    if request.method == 'POST':
        form = PropertyForm(
            request.POST,
            request.FILES,
            instance=property_obj,
            user=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Property updated successfully.')
            return redirect('accounts:user_dashboard')

    else:
        form = PropertyForm(instance=property_obj, user=request.user)

    context = {
        'form': form,
        'property': property_obj,
    }

    return render(request, 'edit_property.html', context)


# =============================
# DELETE PROPERTY
# =============================
@login_required
def delete_property(request, slug):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        owner=request.user
    )

    if request.method == 'POST':
        property_obj.delete()
        messages.success(request, 'Property deleted successfully.')
        return redirect('accounts:user_dashboard')

    return render(request, 'delete_property.html', {'property': property_obj})


# =============================
# TOGGLE STATUS
# =============================
@login_required
def toggle_property_status(request, slug):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        owner=request.user
    )

    property_obj.is_published = not property_obj.is_published
    property_obj.save()

    status = 'activated' if property_obj.is_published else 'deactivated'
    messages.success(request, f'Property {status} successfully.')

    return redirect('accounts:user_dashboard')