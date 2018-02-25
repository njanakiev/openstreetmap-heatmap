import bpy
import bmesh
import os
import sys
import numpy as np
from pyproj import Proj
from mathutils import Matrix, Vector
from matplotlib import cm
from bpy.app.handlers import persistent
import utils
import load_osm_data
from math import sin, cos, pi
TAU = 2*pi


def normalize_points(points):
    """Normalize points while preserving aspect ratio"""

    data = np.array(points)

    minX, minY = np.min(data, axis=0)
    maxX, maxY = np.max(data, axis=0)
    rangeX, rangeY = maxX - minX, maxY - minY

    if rangeX > rangeY:
        data[:, 0] = (data[:, 0] - minX - 0.5*rangeX) / rangeX + 0.5
        data[:, 1] = (data[:, 1] - minY - 0.5*rangeY) / rangeX + 0.5
    else:
        data[:, 0] = (data[:, 0] - minX - 0.5*rangeX) / rangeY + 0.5
        data[:, 1] = (data[:, 1] - minY - 0.5*rangeY) / rangeY + 0.5

    return data


def heatmap_grid(data, sigmaSq=0.0001, n=20, m=2):
    """Create n by n grid with heatmap from data with gaussian distribution of input data set"""

    X = np.ndarray((n, n), dtype=object)
    for idx in np.arange(len(points)):
        x, y = data[idx]
        i, j = int(x * (n - 1)), int(y * (n - 1))
        if X[i, j] is None:
            X[i, j] = [(x, y)]
        else:
            X[i, j].append((x, y))

    grid = np.zeros((n, n))

    for i0 in range(n):
        for j0 in range(n):
            x0, y0 = i0 / (n - 1), j0 / (n - 1)

            # Sum all available neighboring elements
            for i in range(max(0, i0 - m), min(i0 + m, n)):
                for j in range(max(0, j0 - m), min(j0 + m, n)):
                    if X[i, j] is not None:
                        for x, y in X[i, j]:
                            grid[i0][j0] += np.exp(- ((x0 - x)**2)/
                                (2*sigmaSq) - ((y0 - y)**2)/(2*sigmaSq))

    return grid


def heatmap_barplot(grid, h=4, width=10, bar_scale=0.9, num_colors=10, colormap=cm.summer, bevel_width=0.015, logarithmic=False):
    """Create 3D barplot from heatmap grid"""

    # Logarithmic scale
    if logarithmic:
        grid = np.log(grid + 1)

    # Find maximum value
    z_max = np.max(grid)

    n, m = grid.shape
    bar_width = bar_scale * width / max(n, m)

    # List of bmesh elements for each color group
    bmList = [bmesh.new() for i in range(num_colors)]

    # Iterate over grid
    for i in range(n):
        for j in range(m):
            x, y, z = i / (n - 1), j / (m - 1), grid[i][j]
            if z > 0.001:
                bar_height = ((h - bar_width) * z / z_max) + bar_width
                t = 1 - np.exp(-(z / z_max)/0.2)
                k = min(int(num_colors*t), num_colors - 1)
                bm = bmList[k]

                T = Matrix.Translation((
                    width*(x - 0.5),
                    width*(y - 0.5),
                    bar_height / 2))

                S = Matrix.Scale(bar_height / bar_width, 4, (0, 0, 1))
                bmesh.ops.create_cube(bm, size=bar_width, matrix=T*S)

    objList = []
    for i, bm in enumerate(bmList):
        # Create object
        obj = utils.bmeshToObject(bm)

        # Create material with colormap
        color = colormap(i / num_colors)
        mat = utils.simpleMaterial(color[:3])
        obj.data.materials.append(mat)
        objList.append(obj)

        # Add bevel modifier
        bevel = obj.modifiers.new('Bevel', 'BEVEL')
        bevel.width = bevel_width


if __name__ == '__main__':
    # Settings
    iso_a2, tag_key, tag_value = 'DE', 'amenity', 'biergarten'
    res_x, res_y = 768, 432
    #res_x, res_y =  600, 600
    #res_x, res_y =  640, 480
    #res_x, res_y =  640, 360
    #res_x, res_y = 1280, 720
    num_frames = 40
    #r, camera_z = 10, 7
    r, camera_z = 12, 10
    target_z = 0.1
    #target_z = 0.8
    #camera_type, ortho_scale = 'ORTHO', 15
    camera_type, ortho_scale = 'PERSP', 18
    render_idx = 0


    # Remove all elements in scene
    bpy.ops.object.select_by_layer()
    bpy.ops.object.delete(use_global=False)

    # Create scene
    target = utils.createTarget((0, 0, target_z))
    camera = utils.createCamera(target=target,
        camera_type=camera_type, ortho_scale=ortho_scale, lens=28)
        #type='ORTHO', ortho_scale=12)
    sun = utils.createLamp((-5, 5, 10), 'SUN', target=target)

    # Set background color
    bpy.context.scene.world.horizon_color = (0.7, 0.7, 0.7)

    # Ambient occlusion
    bpy.context.scene.world.light_settings.use_ambient_occlusion = True
    bpy.context.scene.world.light_settings.samples = 8

    # Load points from geojson
    filepath = 'data/points_{}_{}_{}.json'.format(iso_a2, tag_key, tag_value)
    points, names = load_osm_data.load_points(filepath)

    p = Proj(init="epsg:3785")  # Popular Visualisation CRS / Mercator
    points = np.apply_along_axis(lambda x : p(*x), 1, points)

    data = normalize_points(points)
    hist = heatmap_grid(data, sigmaSq=0.00005, n=80)
    heatmap_barplot(hist)

    print("Number of points : {}".format(points.shape[0]))

    # Animate rotation of camera
    for frame in range(1, num_frames):
        t = frame / num_frames
        x, y = r*cos(TAU*t), r*sin(TAU*t)
        camera.location = (x, y, camera_z)
        camera.keyframe_insert(data_path="location", index=-1, frame=frame)

    # Render result
    frames_folder = '{}_{}_{}_{}_{}_{}_{:0>3}'.format(
        iso_a2, tag_key, tag_value, camera_type, res_x, res_y, render_idx)

    utils.renderToFolder(frames_folder, res_x=res_x, res_y=res_y, animation=True, frame_end=num_frames, render_opengl=False)
