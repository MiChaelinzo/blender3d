import requests
import bpy

# Define the DALL-E 2 prompt and API endpoint
prompt = "A fluffy cat sitting on a pillow"
api_url = "https://api.openai.com/v1/images/generations"

# Define the API request headers and parameters
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_KEY"
}
params = {
    "model": "image-alpha-001",
    "prompt": prompt,
    "size": "256x256",
    "response_format": "url"
}

# Send the API request and get the response
response = requests.post(api_url, headers=headers, json=params)
response.raise_for_status()

# Get the URL of the generated image
image_url = response.json()["data"][0]["url"]

# Create a new Blender scene
bpy.ops.wm.read_factory_settings()
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.resolution_x = 256
bpy.context.scene.render.resolution_y = 256
bpy.context.scene.render.resolution_percentage = 100

# Create a background plane
background_obj = bpy.data.objects.new("Background", bpy.data.meshes.new("Background"))
background_obj.data.vertices[0].co = (-1, -1, 0)
background_obj.data.vertices[1].co = (1, -1, 0)
background_obj.data.vertices[2].co = (1, 1, 0)
background_obj.data.vertices[3].co = (-1, 1, 0)
background_obj.data.polygons.new((0, 1, 2, 3))
background_obj.active_material = bpy.data.materials.new(name="BackgroundMaterial")
background_obj.active_material.diffuse_color = (1, 1, 1)
bpy.context.scene.collection.objects.link(background_obj)

# Create an image plane with the DALL-E 2 generated image
image_data = requests.get(image_url).content
image = bpy.data.images.load("DALL-E 2 Generated Image", bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y)
image.pixels = image_data
image.pack()
image_obj = bpy.data.objects.new("Image", bpy.data.meshes.new("Image"))
image_obj.data.vertices[0].co = (-1, -1, 0)
image_obj.data.vertices[1].co = (1, -1, 0)
image_obj.data.vertices[2].co = (1, 1, 0)
image_obj.data.vertices[3].co = (-1, 1, 0)
image_obj.data.polygons.new((0, 1, 2, 3))
image_obj.active_material = bpy.data.materials.new(name="ImageMaterial")
image_obj.active_material.use_nodes = True
image_node = image_obj.active_material.node_tree.nodes.new("ShaderNodeTexImage")
image_node.image = image
image_node.location = (-200, 0)
output_node = image_obj.active_material.node_tree.nodes["Material Output"]
output_node.location = (200, 0)
image_obj.active_material.node_tree.links.new(image_node.outputs["Color"], output_node.inputs["Surface"])
bpy.context.scene.collection.objects.link(image_obj)

#Scale the background and image planes to fit the camera's view
aspect_ratio = bpy.context.scene.render.resolution_y / bpy.context.scene.render.resolution_x
camera_distance = 1 / (2 * aspect_ratio * bpy.context.scene.camera.data.sensor_height)
background_obj.dimensions = (aspect_ratio * camera_distance * 2, camera_distance * 2, 1)
image_obj.dimensions = (aspect_ratio * camera_distance * 0.8, camera_distance * 0.8, 0)

#Position the camera to point at the image plane
bpy.context.scene.camera_obj.location = (0, 0, camera_distance)
bpy.context.scene.camera_obj.rotation_mode = 'QUATERNION'
look_at_point = image_obj.location.copy()
look_at_point.z = 0
camera_direction = (look_at_point - bpy.context.scene.camera_obj.location).normalized()
bpy.context.scene.camera_obj.rotation_quaternion = camera_direction.to_track_quat('-Z', 'Y')

#Render the scene to a 3D model
bpy.ops.export_scene.obj(filepath="dalle2.obj")


