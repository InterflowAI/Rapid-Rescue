import requests
import math
import openrouteservice
import folium 
import polyline
api_key = '5b3ce3597851110001cf624892a668326ddc448c91eb298bd7822bfc'
client = openrouteservice.Client(key=api_key)
def find_nearby_hospitals(latitude, longitude):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:3000,{latitude},{longitude});
      
    );
    out center;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    return data['elements']

def get_route_distance(route_data):
    # Extract the distance from the route summary
    route_distance = route_data['routes'][0]['summary']['distance']
    # print(f"Route distance: {route_distance} meters")
    # Convert distance to kilometers and round to 1 decimal place
    route_distance_km = round(route_distance / 1000, 1)
    # print(f"Route distance: {route_distance_km} kilometers")
    return route_distance_km

def sort_hospitals_by_distance(hospitals_with_distances):
    # Sort the list based on the distance (second element in each inner list)
    sorted_hospitals = sorted(hospitals_with_distances, key=lambda x: x[1])
    return sorted_hospitals
def plot_hospitals(user_location,hospitals,route_data):
    # Create a map centered around the user's location
    hospital_map = folium.Map(location=user_location, zoom_start=14)
    encoded_geometry = route_data['routes'][0]['geometry']
    decoded_geometry = polyline.decode(encoded_geometry)
    # Create a map centered around the route
    # Add the route as a polyline
    folium.PolyLine(decoded_geometry, color="blue", weight=2.5, opacity=1).add_to(hospital_map)
    # Add markers for start and end points
    start_point = decoded_geometry[0]
    end_point = decoded_geometry[-1]
    folium.Marker(start_point, tooltip="Start Point", icon=folium.Icon(color="green")).add_to(hospital_map)
    folium.Marker(end_point, tooltip="End Point", icon=folium.Icon(color="red")).add_to(hospital_map)
    # Add user location marker
    folium.Marker(user_location, tooltip="my location", icon=folium.Icon(color="blue")).add_to(hospital_map)
    # Add hospital markers
    for hospital in hospitals:
        folium.Marker(hospital['coordinates'], tooltip=hospital['name'], icon=folium.Icon(color="red")).add_to(hospital_map)
    
    return hospital_map
nearby_hospitals = find_nearby_hospitals(11.091968,76.9523712)
hospitals_list=[]
hospitals=[]
for hospital in nearby_hospitals:
    name = hospital.get('tags', {}).get('name', 'Unknown Hospital')
    latitude = hospital.get('lat', '')
    longitude = hospital.get('lon', '')
    coordinates=latitude,longitude
    user_location=11.091968,76.9523712
    hospitals.append({"name": name, "coordinates": coordinates})
    # distance_km = haversine((11.091968, 76.95237124),( latitude, longitude))
    coords = ((76.9523712,11.091968,),(  longitude,latitude))
 # Specify your personal API key
    routes = client.directions(coords)
    distance=get_route_distance(routes)
    min_distance=0
    if distance<min_distance:
        min_distance=distance
    hospitals_list.append([name,distance,routes])

sorted_hospitals = sort_hospitals_by_distance(hospitals_list)
print("Sorted Hospitals by Distance:")
for hospital in sorted_hospitals:
    print(f"{hospital[0]}: {hospital[1]} km")
# Plot hospitals on the map
hospital_map = plot_hospitals(user_location,hospitals,sorted_hospitals[0][2])
hospital_map.save('hospital_map.html')