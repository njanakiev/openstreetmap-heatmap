import overpy
import json


def load_overpass_points(iso_a2, tag_key='amenity', tag_value='cafe'):
    api = overpy.Overpass()
    r = api.query("""
        ( area["ISO3166-1"="{0}"][admin_level=2]; )->.searchArea;

        ( node[{1}={2}]( area.searchArea );
          way[{1}={2}]( area.searchArea );
          relation[{1}={2}]( area.searchArea );
        );

        out center;""".format(iso_a2, tag_key, tag_value))

    print("Nodes : {}, Ways : {}, Relations : {}".format(
        len(r.nodes), len(r.ways), len(r.relations)))

    coordinates, names = [], []
    for node in r.nodes:
        coordinates.append((float(node.lon), float(node.lat)))
        if 'name' in node.tags:
            names.append(node.tags['name'])
        else:
            names.append(None)

    for way in r.ways:
        coordinates.append((float(way.center_lon), float(way.center_lat)))
        if 'name' in way.tags:
            names.append(way.tags['name'])
        else:
            names.append(None)

    for rel in r.relations:
        coordinates.append((float(rel.center_lon), float(rel.center_lat)))
        if 'name' in rel.tags:
            names.append(rel.tags['name'])
        else:
            names.append(None)

    return coordinates, names


def save_points(filepath, coordinates, names=None, wgs84=True):
    features = []
    for coordinate, name in zip(coordinates, names):
        feature = {}
        feature['type'] = 'Feature'
        feature['geometry'] = {}
        feature['geometry']['type'] = 'Point'
        feature['geometry']['coordinates'] = coordinate

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
    coordinates, names = [], []
    with open(filepath, 'r') as f:
        data = json.load(f)
        if data['type'] == 'MultiPoint':
            coordinates = data['coordinates']
            names = [None] * len(coordinates)
        elif data['type'] == 'FeatureCollection':
            for feature in data['features']:
                coordinates.append(feature['geometry']['coordinates'])
                if 'properties' in feature and 'name' in feature['properties']:
                    names.append(feature['properties']['name'])
                else:
                    names.append(None)
        else:
            raise ValueError('Type \'' + data['type'] + '\' not supported')

    return coordinates, names


if __name__ == '__main__':
    iso_a2, tag_key, tag_value = 'US', 'amenity', 'biergarten'
    print(iso_a2, tag_key, tag_value)

    coordinates, names = load_overpass_points(iso_a2, tag_key, tag_value)
    print('Number of points : {}'.format(len(coordinates)))

    filepath = 'data/points_{}_{}_{}.json'.format(iso_a2, tag_key, tag_value)
    save_points(filepath, coordinates, names)
    #coordinates, names = load(filepath)
    print(len(coordinates))
