

def _get_feature(data):
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [
                data["latitudeE7"] / 1e7,
                data["longitudeE7"] / 1e7,
            ]
        },
        "properties": {
            "timestamp": data["timestampMs"]
        }
    }


def to_geojson(j):
    # print(len(json_file['locations']))

    geojson = {
        "type": "FeatureCollection",
        "features": [_get_feature(point) for point in j["locations"]][:1000]
    }

    return geojson
