import bpy
import os
import sys
import importlib

# Specify the script to be executed
scriptFile = "render_osm_data.py"

# Check if script is executed in Blender and get absolute path of current folder
if bpy.context.space_data is not None:
    cwd = os.path.dirname(bpy.context.space_data.text.filepath)
else:
    cwd = os.path.dirname(os.path.abspath(__file__))

# Get scripts folder and add it to the search path for modules
sys.path.append(cwd)
# Change current working directory to scripts folder
os.chdir(cwd)

# Compile and execute script file
file = os.path.join(cwd, scriptFile)

# Reload the previously imported modules
if 'utils' in locals():
    importlib.reload(utils)
if 'load_osm_data' in locals():
    importlib.reload(load_osm_data)

exec(compile(open(file).read(), scriptFile, 'exec'))
