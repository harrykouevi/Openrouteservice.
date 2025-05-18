from shapely.geometry import  Point
import openrouteservice
import os
from shapely.geometry import  Point, shape, mapping , Polygon
from typing import List, Dict , Union

client = openrouteservice.Client(key=os.getenv("ORS_API_KEY"))

def point_to_polygon(lng: float, lat: float, delta=0.00018):
    """
    Convertit un point (lat, lng) en un petit polygone carré (zone à éviter).
    delta : ~0.00018 ≈ 20 mètres
    Retourne une liste de coordonnées formatée pour un polygone GeoJSON.
    """
    return [[
        [lng - delta, lat - delta],
        [lng + delta, lat - delta],
        [lng + delta, lat + delta],
        [lng - delta, lat + delta],
        [lng - delta, lat - delta]
    ]]
    
def _filter_from_point_(data_issue: List[Dict], position: Dict[str, str], radius: int = 1000) -> List[Dict]:
    print(position)
    geojson = client.isochrones(
        locations=[[position['lng'], position['lat']]],      # Attention : ORS attend [lon, lat]
        range=[radius],              # Rayon en mètres
        profile='driving-car',  
        range_type='distance',       # Type de rayon : distance au lieu du temps
        units='m'                    # Unité : mètres
    )

    # Convertir la géométrie GeoJSON en polygone utilisable avec shapely
    isochrone_polygon = shape(geojson["features"][0]["geometry"])
    # Liste des incidents dans le polygone isochrone 
    if len(data_issue) == 0:
        print("Aucun incident trouvé.") 
        nearby_issues = []
    else:
        nearby_issues = []
        for issue in data_issue:
            point = Point(issue["longitude"], issue["latitude"])   # Crée un point shapely
            if isochrone_polygon.contains(point):           # Vérifie s'il est dans la zone
                nearby_issues.append({
                    "id": issue["id"],
                    "description": issue["description"],
                    "latitude": issue["latitude"],
                    "longitude": issue["longitude"]
                })
    return nearby_issues

def filter_from_point(data_issue: List[Dict], polygon:  Union[Polygon, Dict]) -> List[Dict]:
    # Si le polygone est un dictionnaire GeoJSON, on le transforme
    if isinstance(polygon, dict):
        print(polygon)
      
        geojson = client.isochrones(
            locations=[[polygon['lng'], polygon['lat']]],      # Attention : ORS attend [lon, lat]
            range=[2000],              # Rayon en mètres
            profile='driving-car',  
            range_type='distance',       # Type de rayon : distance au lieu du temps
            units='m'                    # Unité : mètres
        )
        # Convertir la géométrie GeoJSON en polygone utilisable avec shapely
        polygon = shape(geojson["features"][0]["geometry"])

    if not isinstance(polygon, Polygon):
        raise ValueError("Le paramètre 'polygon' doit être un Polygon ou un GeoJSON valide.")

    nearby_issues = []
    for issue in data_issue:
        point = Point(issue["longitude"], issue["latitude"])
        if polygon.contains(point):
            nearby_issues.append({
                "id": issue["id"],
                "description": issue["description"],
                "latitude": issue["latitude"],
                "longitude": issue["longitude"]
            })

    return nearby_issues
    

