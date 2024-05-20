import requests
import openrouteservice
import folium
import polyline

# Specify your personal API key
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
    # Convert distance to kilometers and round to 1 decimal place
    route_distance_km = round(route_distance / 1000, 1)
    return route_distance_km

def sort_hospitals_by_distance(hospitals_with_distances):
    # Sort the list based on the distance (second element in each inner list)
    sorted_hospitals = sorted(hospitals_with_distances, key=lambda x: x[1])
    return sorted_hospitals

def plot_hospitals(user_location, hospitals,route_data, client):
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
    folium.Marker(user_location, tooltip="My Location", icon=folium.Icon(color="blue")).add_to(hospital_map)
    
    # Add hospital markers with directions link
    for hospital in hospitals:
        hospital_name = hospital['name']
        hospital_coords = hospital['coordinates']
        
        # Add marker with a popup containing a link to get directions
        iframe = folium.IFrame(f'''
        <b>{hospital_name}</b><br>
        <a href="javascript:void(0)" onclick="getDirections({hospital_coords[0]}, {hospital_coords[1]})">Get Directions</a>
        ''')
        popup = folium.Popup(iframe, min_width=300, max_width=300)
        folium.Marker(hospital_coords, tooltip=(hospital_name,hospital_coords), popup=popup, icon=folium.Icon(color="red")).add_to(hospital_map)
    
    # Add JavaScript to handle clicking on the "Get Directions" link
    hospital_map.get_root().html.add_child(folium.Element('''
    <script>
        function getDirections(lat, lon) {
            // Replace this URL with the actual URL or method to get directions
            fetch(`https://api.openrouteservice.org/v2/directions/driving-car?api_key=5b3ce3597851110001cf624892a668326ddc448c91eb298bd7822bfc&start=76.944877,11.0899198&end=${hospital_coords[0]},${hospital_coords[1]}`)

            .then(response => response.json())
            .then(data => {
                // Remove existing polyline if any
                if (window.routePolyline) {
                    window.routePolyline.remove();
                }
                
                // Decode the polyline
                let routeCoordinates = L.Polyline.fromEncoded(data.routes[0].geometry).getLatLngs();
                
                // Add new polyline to the map
                window.routePolyline = L.polyline(routeCoordinates, {color: 'blue', weight: 2.5, opacity: 1}).addTo(map);
                
                // Fit the map bounds to the new polyline
                map.fitBounds(window.routePolyline.getBounds());
            });
        }
    </script>
    '''))
    hospital_map.save('hospital_map.html')
    return hospital_map

# Example usage
user_location = (11.091968, 76.9523712)
nearby_hospitals = find_nearby_hospitals(user_location[0], user_location[1])
hospitals = []
hospitals_list=[]
for hospital in nearby_hospitals:
    name = hospital.get('tags', {}).get('name', 'Unknown Hospital')
    latitude = hospital.get('lat', '')
    longitude = hospital.get('lon', '')
    coordinates = (latitude, longitude)
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
hospital_map = plot_hospitals(user_location,hospitals,sorted_hospitals[0][2],client)
hospital_map.save('hospital_map.html')
