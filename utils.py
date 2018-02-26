import os
import bpy
import bmesh


def simple_material(diffuse_color):
    mat = bpy.data.materials.new('Material')

    # Diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 0.9
    mat.diffuse_color = diffuse_color

    # Specular
    mat.specular_intensity = 0

    return mat

def bmesh_to_object(bm, name='Object'):
    mesh = bpy.data.meshes.new(name+'Mesh')
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.objects.link(obj)
    bpy.context.scene.update()

    return obj

def track_to_constraint(obj, target):
    constraint = obj.constraints.new('TRACK_TO')
    constraint.target = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

def create_target(origin=(0,0,0)):
    tar = bpy.data.objects.new('Target', None)
    bpy.context.scene.objects.link(tar)
    tar.location = origin

    return tar

def create_camera(origin=(0,0,0), target=None, lens=35, clip_start=0.1, clip_end=200, camera_type='PERSP', ortho_scale=6):
    # Create object and camera
    camera = bpy.data.cameras.new("Camera")
    camera.lens = lens
    camera.clip_start = clip_start
    camera.clip_end = clip_end
    camera.type = camera_type # 'PERSP', 'ORTHO', 'PANO'
    if camera_type == 'ORTHO':
        camera.ortho_scale = ortho_scale

    # Link object to scene
    obj = bpy.data.objects.new("CameraObj", camera)
    obj.location = origin
    bpy.context.scene.objects.link(obj)
    bpy.context.scene.camera = obj # Make this the current camera

    if target: track_to_constraint(obj, target)
    return obj

def create_lamp(origin, type='POINT', energy=1, color=(1,1,1), target=None):
    # Lamp types: 'POINT', 'SUN', 'SPOT', 'HEMI', 'AREA'
    bpy.ops.object.add(type='LAMP', location=origin)
    obj = bpy.context.object
    obj.data.type = type
    obj.data.energy = energy
    obj.data.color = color

    if target: track_to_constraint(obj, target)
    return obj

def render_to_folder(render_folder='render', render_name='render', res_x=800, res_y=800, res_percentage=100, animation=False, frame_end=None, render_opengl=False):
    print('renderToFolder called')
    print('render_folder : {}'.format(render_folder))
    print('render_name   : {}'.format(render_name))

    scene = bpy.context.scene
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = res_percentage
    if frame_end:
        scene.frame_end = frame_end

    # Check if script is executed inside Blender
    if (bpy.context.space_data is None) or render_opengl:
        # Specify folder to save rendering and check if it exists
        render_folder = os.path.join(os.getcwd(), render_folder)
        if(not os.path.exists(render_folder)):
            os.mkdir(render_folder)

        if animation:
            # Render animation
            scene.render.filepath = os.path.join(render_folder,
                render_name)
            if render_opengl:
                bpy.ops.render.opengl(animation=True, view_context=False)
            else:
                bpy.ops.render.render(animation=True)
        else:
            # Render still frame
            scene.render.filepath = os.path.join(render_folder,
                render_name + '.png')
            if render_opengl:
                bpy.ops.render.opengl(write_still=True, view_context=False)
            else:
                bpy.ops.render.render(write_still=True)
