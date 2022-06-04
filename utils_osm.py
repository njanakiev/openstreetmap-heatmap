import requests
import json

OVERPASS_URL = "http://overpass-api.de/api/interpreter"


def overpass_load_points(iso_a2, tag_key='amenity', tag_value='cafe'):
    """Load OSM points from Overpass API"""
    
    overpass_query = """
        [out:json];
        ( area["ISO3166-1"="{0}"][admin_level=2]; )->.searchArea;
        ( node[{1}={2}]( area.searchArea );
          way[{1}={2}]( area.searchArea );
          relation[{1}={2}]( area.searchArea );
        );
        out center;""".format(iso_a2, tag_key, tag_value)
    response = requests.get(OVERPASS_URL, params={'data': overpass_query})
    data = response.json()

    coords, names = [], []
    for e in data['elements']:
        names.append(e.get('name'))
        if e['type'] == 'node':
            coords.append((e['lon'], e['lon']))
        else:
            coords.append((e['center']['lon'], e['center']['lat']))

    return coords, names


def save_points(filepath, coords, names=None, wgs84=True):
    """Save points to GeoJSON file"""

    features = []
    for coord, name in zip(coords, names):
        feature = {}
        feature['type'] = 'Feature'
        feature['geometry'] = {}
        feature['geometry']['type'] = 'Point'
        feature['geometry']['coordinates'] = coord

        if names is not None and name is not None:
            feature['properties'] = {}
            feature['properties']['name'] = name

        features.append(feature)

    geojson = {}
    geojson['type'] = 'FeatureCollection'
    geojson['features'] = features

    if wgs84:
        # Set CRS as WGS84
        geojson['crs'] = { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } }

    with open(filepath, 'w') as f:
        json.dump(geojson, f, indent=4)


def load_points(filepath):
    """Load points from GeoJSON"""

    coords, names = [], []
    with open(filepath, 'r') as f:
        data = json.load(f)
        if data['type'] == 'MultiPoint':
            coords = data['coordinates']
            names = [None] * len(coords)
        elif data['type'] == 'FeatureCollection':
            for feature in data['features']:
                coords.append(feature['geometry']['coordinates'])
                if 'properties' in feature and 'name' in feature['properties']:
                    names.append(feature['properties']['name'])
                else:
                    names.append(None)
        else:
            raise ValueError('Type \'' + data['type'] + '\' not supported')

    return coords, names


if __name__ == '__main__':
    iso_a2, tag_key, tag_value = 'DE', 'amenity', 'biergarten'
    print(iso_a2, tag_key, tag_value)

    coords, names = overpass_load_points(iso_a2, tag_key, tag_value)
    print('Number of points : {}'.format(len(coords)))

    filepath = 'data/points_{}_{}_{}.json'.format(iso_a2, tag_key, tag_value)
    save_points(filepath, coords, names)
