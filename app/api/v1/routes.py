from fastapi import APIRouter, Query , Request
from app.services.ors_service import get_route
from fastapi.responses import JSONResponse
import openrouteservice
import os
from shapely.geometry import  Point, shape, mapping
from dotenv import load_dotenv
import requests
from app.api.geo import point_to_polygon ,filter_from_point
from app.api.traffic import get_all_road_issues ,extract_road_issue_points ,get_geo_json_from_issues

load_dotenv()

router = APIRouter()

client = openrouteservice.Client(key=os.getenv("ORS_API_KEY"))

@router.get("/route")
def get_routes(
    start: str = Query(..., description="Latitude,Longitude"),
    end: str = Query(..., description="Latitude,Longitude"),
    alternatives: int = 3
):
    try:
        latA, lonA = map(float, start.split(","))
        latB, lonB = map(float, end.split(","))
        coords = [(lonA, latA), (lonB, latB)]


        avoid_zone_1 = {
            "type": "Polygon",
            "coordinates": [
                [
                    [1.2245, 6.1684],
                    [1.2265, 6.1684],
                    [1.2265, 6.1696],
                    [1.2245, 6.1696],
                    [1.2245, 6.1684]
                ]
            ]
        }

        avoid_zone_2 = {
            "type": "Polygon",
            "coordinates": [
                [
                    [1.2180, 6.1811],
                    [1.2190, 6.1811],
                    [1.2190, 6.1822],
                    [1.2180, 6.1822],
                    [1.2180, 6.1811]
                ]
            ]
        }

        # Liste des zones à éviter
        avoid_zones = [avoid_zone_1, avoid_zone_2]

        


        
        result = client.directions(
            coordinates=coords,
            profile='driving-car',
            format='geojson',
            alternative_routes={'share_factor': 0.6, 'target_count': alternatives},
            options = {
                "avoid_polygons": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [[[1.2245, 6.1684], [1.2265, 6.1684], [1.2265, 6.1696], [1.2245, 6.1696], [1.2245, 6.1684]]],
                        [[[1.2180, 6.1811], [1.2190, 6.1811], [1.2190, 6.1822], [1.2180, 6.1822], [1.2180, 6.1811]]]
                    ]
                }
            }
        )

        routes = []
        for feature in result['features']:
            coords = feature['geometry']['coordinates']
            coords_latlon = [[lat, lon] for lon, lat in coords]
            routes.append({'coordinates': coords_latlon})

        return JSONResponse({"routes": routes})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@router.get("/directions")
def get_routes(
    start: str = Query(..., description="Latitude,Longitude"),
    end: str = Query(..., description="Latitude,Longitude"),
    alternatives: int = 3
):
    try:
        #transforme les données de la requete en coordonnée
        latA, lonA = map(float, start.split(","))
        latB, lonB = map(float, end.split(","))
        coords = [(lonA, latA), (lonB, latB)]

        all_issues = get_all_road_issues(latA,lonA,1000)
        # Liste des incidents dans le polygone isochrone 
        nearby_issues = filter_from_point(all_issues,{'lat': latA,'lng': lonA,})
        # Liste des incidents à éviter
        points_to_avoid = extract_road_issue_points(nearby_issues)
        # geojson des incidents à éviter
        geojson_points_to_avoid = get_geo_json_from_issues(nearby_issues)
        # Générer les polygones à partir des points
        avoid_polygons = [point_to_polygon(lng, lat) for (lng, lat) in points_to_avoid]
        # Aplatir pour en faire un multipolygon valide
        multi_polygon = {
            "type": "MultiPolygon",
            "coordinates": avoid_polygons
        }

        # calcul d'itinéraire en voiture (driving-car) avec recupartion d'un GeoJSON
        result = client.directions(
            coordinates=coords,
            profile='driving-car',
            format='geojson',
            alternative_routes={'share_factor': 0.6, 'target_count': alternatives},
            options = {
                "avoid_polygons": multi_polygon
            }
        )

        # recuperation des coordonnées de routes dans le format [longitude, latitude].
        routes = []
        for feature in result['features']:
            coords = feature['geometry']['coordinates']
            coords_latlon = [[lat, lon] for lon, lat in coords]
            routes.append({'coordinates': coords_latlon})

        return JSONResponse({"routes": routes , "avoid_polygons": geojson_points_to_avoid})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)



@router.get("/zone")
def get_zones(
    lat: float = Query(...),     # Latitude du point de référence
    lng: float = Query(...),     # Longitude du point de référence
    radius: int = Query(10000),  # Rayon de recherche en mètres (par défaut 10 km)
):
    try:
        
        geojson = client.isochrones(
            locations=[[lng, lat]],      # Attention : ORS attend [lon, lat]
            range=[radius],              # Rayon en mètres
            profile='driving-car',  
            range_type='distance',       # Type de rayon : distance au lieu du temps
            units='m'                    # Unité : mètres
        )

        # Convertir la géométrie GeoJSON en polygone utilisable avec shapely
        isochrone_polygon = shape(geojson["features"][0]["geometry"])
        print(isochrone_polygon)

        # Convertit le polygone shapely en format GeoJSON (dict)
        geojson_polygon = mapping(isochrone_polygon)

        return {
            "zones": geojson_polygon
        }

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@router.get("/road-issues")
def get_issues_in_zone(
    request: Request,
    lat: float = Query(...),     # Latitude du point de référence
    lng: float = Query(...),     # Longitude du point de référence
    radius: int = Query(10000),  # Rayon de recherche en mètres (par défaut 10 km)
):
    
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]

    # Préparer l'en-tête pour la requête vers l'API ORS
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    all_issues = get_all_road_issues( lat,lng,radius,headers)
    print(all_issues)
    print(os.getenv("ORS_API_KEY"))

    # all_issues = get_all_road_issues( lat,lng,radius)
    
    geojson = client.isochrones(
        locations=[[lng, lat]],      # Attention : ORS attend [lon, lat]
        range=[radius],              # Rayon en mètres
        profile='driving-car',  
        range_type='distance',       # Type de rayon : distance au lieu du temps
        units='m'                    # Unité : mètres
    )

    # Convertir la géométrie GeoJSON en polygone utilisable avec shapely
    isochrone_polygon = shape(geojson["features"][0]["geometry"])
    
    # Liste des incidents dans le polygone isochrone 
    nearby_issues = filter_from_point(all_issues,isochrone_polygon)
    return {
        "count": len(nearby_issues),
        "data": nearby_issues
    }


