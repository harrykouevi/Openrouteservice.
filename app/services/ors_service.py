import openrouteservice
import os

client = openrouteservice.Client(key=os.getenv("ORS_API_KEY"))

def get_route(start, end):
    coords = (start, end)
    return client.directions(coords)
