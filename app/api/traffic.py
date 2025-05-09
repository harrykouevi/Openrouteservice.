import requests
from typing import List, Dict
from fastapi.responses import JSONResponse
from app.api.geo import point_to_polygon


def get_all_road_issues(   lat: float ,     # Latitude du point de référence
                            lng: float ,     # Longitude du point de référence
                            radius: int = 1000,
                            headers={}
    ) -> List[Dict]:
   
    url = "http://traffic-service:80/api/road-issues"
    try:
        
        response = requests.get(url , headers=headers , params={
            'lat': lat,
            'lng': lng,
            'radius': 1000
        })
        response.raise_for_status()
        data = response.json()
        return data.get('data', []) 

    except requests.RequestException as e:
        return JSONResponse(content={"error": str(e)}, status_code=502)


def extract_road_issue_points(issues_data: dict) -> list[tuple[float, float]]:
    """
    Transforme la réponse JSON du service Traffic en une liste de points (lng, lat).
    """
    return [
        (issue["longitude"], issue["latitude"])
        for issue in issues_data
    ]
    
def get_geo_json_from_issues(data: dict)-> dict:
    features = []
    
    nearby_issues = []
    for issue in data:
        point = Point(issue["longitude"], issue["latitude"])   # Crée un point shapely
        if isochrone_polygon.contains(point):           # Vérifie s'il est dans la zone
            nearby_issues.append({
                "id": issue["id"],
                "description": issue["description"],
                "latitude": issue["latitude"],
                "longitude": issue["longitude"]
            })
    for i, point in enumerate(data, start=1):
        polygon = point_to_polygon(point["longitude"], point["latitude"])
        feature = {
            "type": "Feature",
            "properties": {
                "id": point["id"],
                "description": point["description"],
                "name": point["description"]
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": polygon
            }
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }