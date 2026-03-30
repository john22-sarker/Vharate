from django.http import JsonResponse
from .models import Area, SubArea

def get_areas(request, city_id):
    areas = Area.objects.filter(city_id=city_id).order_by('name')
    data = [{'id': area.id, 'name': area.name} for area in areas]
    return JsonResponse(data, safe=False)


def get_subareas(request, area_id):
    subareas = SubArea.objects.filter(area_id=area_id).order_by('name')
    data = [{'id': subarea.id, 'name': subarea.name} for subarea in subareas]
    return JsonResponse(data, safe=False)
