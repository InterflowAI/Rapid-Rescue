from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
from .models import Hospital
import requests
import openrouteservice
import folium
import polyline
import time

api_key = '5b3ce3597851110001cf624892a668326ddc448c91eb298bd7822bfc'
client = openrouteservice.Client(key=api_key)

def find_nearby_hospitals(latitude, longitude):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:7000,{latitude},{longitude});
    );
    out center;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    return data['elements']

def get_route_distance(route_data):
    route_distance = route_data['routes'][0]['summary']['distance']
    route_distance_km = round(route_distance / 1000, 1)
    return route_distance_km

def sort_hospitals_by_distance(hospitals_with_distances):
    sorted_hospitals = sorted(hospitals_with_distances, key=lambda x: x[1])
    return sorted_hospitals

def index(request):
    return render(request, 'index.html')

def find_hospitals(request):
    if request.method == 'POST':
        latitude = float(request.POST.get('latitude'))
        longitude = float(request.POST.get('longitude'))
        user_location = (latitude, longitude)
        
        cache_key = f"hospitals_{latitude}_{longitude}"
        cached_hospitals = cache.get(cache_key)
        
        if cached_hospitals:
            return JsonResponse(cached_hospitals)

        nearby_hospitals = find_nearby_hospitals(latitude, longitude)
        hospitals_list = []
        hospitals = []

        for hospital in nearby_hospitals[:15]:
            name = hospital.get('tags', {}).get('name', 'Unknown Hospital')
            lat = hospital.get('lat', '')
            lon = hospital.get('lon', '')
            coordinates = (lat, lon)
            hospitals.append({"name": name, "coordinates": coordinates})

            route_cache_key = f"route_{latitude}_{longitude}_{lat}_{lon}"
            cached_route = cache.get(route_cache_key)
            
            if cached_route:
                routes = cached_route
            else:
                coords = ((longitude, latitude), (lon, lat))

                routes = None
                for i in range(5):
                    try:
                        routes = client.directions(coords)
                        cache.set(route_cache_key, routes, timeout=3600)
                        break
                    except openrouteservice.exceptions.ApiError as e:
                        if 'Rate limit exceeded' in str(e):
                            time.sleep(2 ** i)
                        else:
                            raise e

            if not routes:
                return JsonResponse({'error': 'Rate limit exceeded. Please try again later.'}, status=429)

            distance = get_route_distance(routes)

            hospital_obj, created = Hospital.objects.update_or_create(
                name=name,
                latitude=lat,
                longitude=lon,
                defaults={'distance': distance}
            )
            hospitals_list.append([name, distance, routes])

        sorted_hospitals = sort_hospitals_by_distance(hospitals_list)
        nearest_hospital = sorted_hospitals[0][2]  # Get the routes of the nearest hospital

        response_data = {
            'user_location': user_location,
            'hospitals': hospitals,
            'nearest_hospital': {
                'name': sorted_hospitals[0][0],
                'distance': sorted_hospitals[0][1],
                'route': nearest_hospital
            }
        }
        
        cache.set(cache_key, response_data, timeout=3600)

        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request'}, status=400)
