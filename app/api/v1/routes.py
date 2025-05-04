from fastapi import APIRouter, Query
from app.services.ors_service import get_route
from fastapi.responses import JSONResponse
import openrouteservice
import os
from dotenv import load_dotenv

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
            # options={
            #     "avoid_polygons": {
            #         "type": "MultiPolygon",
            #         "coordinates": [
            #             [[[1.2280, 6.1750], [1.2300, 6.1750], [1.2300, 6.1780], [1.2280, 6.1780], [1.2280, 6.1750]]]
            #         ]
            #     }
            # }
        )

        routes = []
        for feature in result['features']:
            coords = feature['geometry']['coordinates']
            coords_latlon = [[lat, lon] for lon, lat in coords]
            routes.append({'coordinates': coords_latlon})

        return JSONResponse({"routes": routes})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
