import openrouteservice
from openrouteservice import convert
import time

API_KEY = "5b3ce3597851110001cf6248cafa2e77412c4c10999b08d7a91045df"  # <<< HIER DEIN ORS API-KEY EINTRAGEN

client = openrouteservice.Client(key=API_KEY)

def geocode_address(address):
    geocode = client.pelias_search(text=address)
    coords = geocode['features'][0]['geometry']['coordinates']
    return coords[0], coords[1]  # lon, lat

def optimize_route(addresses):
    coords = []
    for addr in addresses:
        try:
            lon, lat = geocode_address(addr)
            coords.append((lon, lat))
        except Exception as e:
            print(f"Fehler bei Adresse '{addr}': {e}")
            return addresses  # Im Fehlerfall: unbearbeitet zurück

    # Optimierung mit TSP (startpunkt fix: index 0)
    try:
        res = client.optimization(
            jobs=[{"id": i+1, "location": coord} for i, coord in enumerate(coords[1:])],
            vehicles=[{
                "id": 1,
                "start": coords[0],
                "end": coords[0]
            }]
        )
        job_order = [step["id"] for step in res["routes"][0]["steps"][1:-1]]
        ordered = [addresses[0]] + [addresses[i] for i in job_order]
        return ordered
    except Exception as e:
        print(f"Optimierungsfehler: {e}")
        return addresses  # Wenn Fehler, unbearbeitet zurück