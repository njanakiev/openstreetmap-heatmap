# Openstreetmap Heatmap
This project is a visualization of OpenStreetMap data with Blender and Python as a 3D barplot. It creates an occurence heatmap of all points that are collected within a country with a certain tag.

OpenStreetMap (OSM) has a vast geospatial data set containing various tags and attributes besides the geometry. By using the [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API) we can query for specific tags, filter specific areas and various other kinds of queries. In this case we want to query for tags within the boundary of a country. We are using the two-letter [country codes](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) and filter for a single [OSM tag](https://wiki.openstreetmap.org/wiki/Tags) across all available [OSM elements](https://wiki.openstreetmap.org/wiki/Elements). You can see the various [Map Features](https://wiki.openstreetmap.org/wiki/Map_Features) to get a grasp of the variety.

![DE_biergarten_animation](/assets/DE_biergarten_animation.gif)

# Requirements

- Blender 2.5+
- [overpy](https://python-overpy.readthedocs.io/en/latest/)

In order to run this script you need to run

```
blender -b -P run_script.py
```

which runs the rendering in the background. You can also load [run_script.py](/run_script.py) into Blender as a script and execute the program from there. You need to have the overpy package available in your Python distribution which is accessed by Blender. I described in this [article](http://til.janakiev.com/using-anaconda-in-blender/) how to use [Anaconda](https://www.anaconda.com/download/) in Blender, which is handy for installing and using additional python packages.

You can edit the settings within the [render_osm_data.py](/render_osm_data.py) under the `# Settings` part. The script can do both render frames of an animation (rotation around the barplot) or render a single frame. You can also load and save the points as a [GeoJSON](https://en.wikipedia.org/wiki/GeoJSON) with the [utils_osm.py](/utils_osm.py) script.

# Gallery

### All Biergarten in Germany

![DE_biergarten](/assets/DE_biergarten.png)

### All Swiss Banks

![CH_bank](/assets/CH_bank.png)

### All Pubs in Great Britain

![GB_pub](/assets/GB_pub.png)
