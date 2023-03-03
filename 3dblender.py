import bpy
import requests
import json
import base64

# Define the DALL-E 2 prompt and generate the image
prompt = "a cute cat playing with a ball of yarn"
response = requests.post("https://api.openai.com/v1/images/generations", 
                         headers={"Authorization": "Bearer YOUR_API_KEY"}, 
                         json={"model": "image-alpha-001", "prompt": prompt})

# Check if the request was successful
if response.status_code == 200:

# Extract the image URL from the response
    image_url = response.json()["data"][0]["url"]

# Download the image and encode it as base64
    image_content = requests.get(image_url).content
    image_base64 = base64.b64encode(image_content).decode('ascii')

# Create a new Blender scene and camera
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.context.scene.camera = bpy.data.cameras.new("Camera")
    bpy.context.scene.camera_obj = bpy.data.objects.new("Camera", bpy.context.scene.camera)
    bpy.context.scene.collection.objects.link(bpy.context.scene.camera_obj)

# Create a new plane to use as the background
    background = bpy.data.meshes.new('Plane')
    background_obj = bpy.data.objects.new('Plane', background)
    bpy.context.scene.collection.objects.link(background_obj)
    bpy.context.view_layer.objects.active = background_obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=True)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.delete(type='ONLY_FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = None

# Create a new material for the background
    background_mat = bpy.data.materials.new(name="Background")
    background_mat.use_nodes = True
    bsdf = background_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (1, 1, 1, 1)
    output = background_mat.node_tree.nodes["Material Output"]
    background_mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    background_obj.data.materials.append(background_mat)

# Create a new plane to use as the image
    image = bpy.data.meshes.new('Image')
    image_obj = bpy.data.objects.new('Image', image)
    bpy.context.scene.collection.objects.link(image_obj)
    bpy.context.view_layer.objects.active = image_obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=True)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.delete(type='ONLY_FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = None

# Create a new material for the image
    image_mat = bpy.data.materials.new(name="Image")
    image_mat.use_nodes = True
    image_tex = bpy.data.textures.new(name="Image", type='IMAGE')
    image_tex.image = bpy.data.images.load(image_url)
    tex_coord = image_mat.node_tree.nodes.new("ShaderNodeTexCoord")
    tex_image = image_mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex_image.image = image_tex.image
    output = image_mat.node_tree.nodes["Material Output"]
    image_mat.node_tree.links.new(tex_coord.outputs['UV'], tex_image.inputs['Vector'])
    image_mat.node_tree.links.new(tex_image.outputs['Color'], output.inputs['Surface'])
    image_obj.data.materials.append(image_mat)

# Position the camera and objects
    bpy.context.scene.camera_obj.location = (0, 0, camera_distance)
    background_obj.location = (0, 0, -camera_distance)
    image_obj.location = (0, 0, camera_distance - 0.01) # Offset the image plane slightly to avoid z-fighting

# Set the camera to look at the image plane
    bpy.context.scene.camera_obj.rotation_mode = 'XYZ'
    bpy.context.scene.camera_obj.rotation_euler = (0, 0, 0)
    bpy.context.scene.camera_obj.data.lens = 50 # Set the camera focal length
    bpy.ops.object.select_all(action='DESELECT')
    image_obj.select_set(True)
    bpy.context.view_layer.objects.active = image_obj
    bpy.ops.view3d.camera_to_view_selected()

# Render the scene to a file
    bpy.context.scene.render.filepath = "C:/Users/micha/Documents/image3d.png"
    bpy.ops.render.render(write_still=True)
    

