"""Fetch coordinates of transit hubs, malls and beaches from OpenStreetMap (Nominatim lookup).

Places are fixed by OSM id, so the output is reproducible and each row can be checked on
openstreetmap.org. Used by notebooks/02_cross_validation.ipynb to build place-based measures.
Hartono Mall is missing because Nominatim returned no mall object for it (Nov 2026).

Run: python src/fetch_places.py
"""
import json
import urllib.parse
import urllib.request

import pandas as pd

from config import PLACES_CSV

# (group, name, OSM id with type prefix N/W/R)
PLACES = [
    ("transit", "Stasiun Yogyakarta (Tugu)", "W292847500"),
    ("transit", "Stasiun Lempuyangan", "W578712069"),
    ("transit", "Terminal Giwangan", "W263174151"),
    ("transit", "Terminal Jombor", "W121297861"),
    ("transit", "Bandara Adisutjipto", "N10700969429"),
    ("transit", "Yogyakarta International Airport (rail station at terminal)", "N9155303920"),
    ("mall", "Malioboro Mall", "W1327171506"),
    ("mall", "Plaza Ambarrukmo", "R14251989"),
    ("mall", "Jogja City Mall", "W608602428"),
    ("mall", "Galeria Mall", "W120410763"),
    ("mall", "Pakuwon Mall Jogja", "N13114928013"),
    ("beach", "Pantai Parangtritis", "W364274285"),
    ("beach", "Pantai Depok", "W364634472"),
    ("beach", "Pantai Baron", "W310361685"),
    ("beach", "Pantai Drini", "W310371252"),
    ("beach", "Pantai Indrayanti", "W310371954"),
    ("beach", "Pantai Glagah", "N5534390312"),
]
URL = "https://nominatim.openstreetmap.org/lookup?"
USER_AGENT = "student-mobility-project/0.1"


def main() -> None:
    ids = ",".join(p[2] for p in PLACES)
    req = urllib.request.Request(URL + urllib.parse.urlencode({"osm_ids": ids, "format": "jsonv2"}),
                                 headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req) as r:
        found = {f"{x['osm_type'][0].upper()}{x['osm_id']}": x for x in json.load(r)}
    missing = [p[2] for p in PLACES if p[2] not in found]
    if missing:
        raise ValueError(f"OSM ids not returned by Nominatim: {missing}")

    df = pd.DataFrame([{"group": g, "name": n, "osm_id": i,
                        "lat": float(found[i]["lat"]), "lon": float(found[i]["lon"]),
                        "osm_name": found[i]["display_name"]} for g, n, i in PLACES])
    df.to_csv(PLACES_CSV, index=False)
    print(f"saved {len(df)} places -> {PLACES_CSV.name}")


if __name__ == "__main__":
    main()
