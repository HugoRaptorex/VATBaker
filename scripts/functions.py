# Copyright (C) 2026 Piotr Charchut

#############################-GPL-LICENSE-#############################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#
#######################################################################

import bpy
import bmesh
import mathutils

def bake_vat(objs, props):
    """Main functionality. Create VAT textures and set meshes UVs"""

    # Get start/end of the animation.
    start_frame = props.frame_start
    end_frame = props.frame_end + 1

    # Set animation range.
    if props.flip_vertically:
        frames_range = range(end_frame - 1, start_frame - 1, -props.step)
    else:
        frames_range = range(start_frame, end_frame, props.step)

    # Set texture width and height.
    texture_height = abs(start_frame - end_frame) // props.step
    texture_width = 0
    if props.bake_mode == 'OPT_VERTS':
        for obj in objs:
            texture_width += len(obj.data.vertices)
    elif props.bake_mode == 'OPT_TRANS':
        texture_width = len(objs)

    # Get texture data.
    pixels_pos = []
    pixels_nor = []
    if props.bake_mode == 'OPT_VERTS':
        create_texture_data_vertex_mode(pixels_pos, pixels_nor, objs, props, frames_range)
    elif props.bake_mode == 'OPT_TRANS':
        create_texture_data_transform_mode(pixels_pos, pixels_nor, objs, props, frames_range)

    # Reset frame to base frame.
    bpy.context.scene.frame_set(props.frame_base)

    # Handle auto-looping feature.
    if props.looping_frame_count:
        loop_animation(props, pixels_pos, pixels_nor, texture_width, texture_height)

    # Save textures to disk.
    if props.include_position:
        full_path = get_path(props.path) + props.filename_prefix + props.filename + props.positon_suffix
        save_image(pixels_pos, texture_width, texture_height, full_path)
    if props.include_rotation:
        full_path = get_path(props.path) + props.filename_prefix + props.filename + props.rotation_suffix
        save_image(pixels_nor, texture_width, texture_height, full_path)

    # Set UV sets.
    if props.bake_mode == 'OPT_VERTS':
        create_uvs_vertex_mode(objs, props)
    elif props.bake_mode == 'OPT_TRANS':
        create_uvs_transform_mode(objs, props)

def create_base_objects(objs, base_frame):
    """Create an array of base (reference) objects and their world matrices"""
    base_objects = []
    base_objects_world_matrices = []
    for obj in objs:
        original, matrix = new_object_from_frame(obj, base_frame)
        base_objects.append(original)
        base_objects_world_matrices.append(matrix)

    return base_objects, base_objects_world_matrices

def destroy_base_objects(base_objects):
    """Destroy previously created base object/objects."""
    for obj in base_objects:
        bpy.data.meshes.remove(obj.data)

def create_texture_data_vertex_mode(pixels_pos, pixels_nor, objs, props, frames_range):
    """Create texture data for vertices mode. Gets vertex positions of every mesh in every frame in a specified range and stores them in lists."""
    base_objects, base_objects_world_matrices = create_base_objects(objs, props.frame_base)

    # Get texture data
    for frame in frames_range:
        for i, obj in enumerate(objs):
            temp_obj, temp_matrix = new_object_from_frame(obj, frame)
            normal_matrix = temp_matrix.inverted().transposed().to_3x3()
            for vert, base_vert in zip(temp_obj.data.vertices, base_objects[i].data.vertices):
                
                # Apply world matrix to get the world coordinate (to handle transforms on top of deformers) 
                current_position = temp_matrix @ vert.co.copy()
                base_position = base_objects_world_matrices[i] @ base_vert.co.copy()
                
                # Position
                vert_delta_position = current_position - base_position
                value_x = (vert_delta_position.x / props.max_range) * 0.5 + 0.5
                value_y = (-vert_delta_position.y / props.max_range) * 0.5 + 0.5
                value_z = (vert_delta_position.z / props.max_range) * 0.5 + 0.5
                pixels_pos.extend((value_x, value_y, value_z, 1.0))
            
                # Normal
                vert_normal = normal_matrix @ vert.normal.copy()
                vert_normal.normalize()
                vert_normal.x = vert_normal.x * 0.5 + 0.5
                vert_normal.y = -vert_normal.y * 0.5 + 0.5
                vert_normal.z = vert_normal.z * 0.5 + 0.5
                pixels_nor.extend((vert_normal.x, vert_normal.y, vert_normal.z, 1.0))
            bpy.data.meshes.remove(temp_obj.data)
    
    #Cleanup
    destroy_base_objects(base_objects)

def create_texture_data_transform_mode(pixels_pos, pixels_nor, objs, props, frames_range):
    """Create texture data for transforms mode. Gets transforms of every mesh in every frame in a specified range and stores them in lists as position (translation XYZ) and quaternion (rotation XYZW)."""
    
    # Cache the rigid body sim. The Bake All Dynamic and Calculate to Frame cache operators don't seem 
    # to work without hacks, so we're just going through the frames and cache it by hand.
    for f in range(props.frame_start, props.frame_end):
        bpy.context.scene.frame_set(f)

    base_objects, base_objects_world_matrices = create_base_objects(objs, props.frame_base)
    prev_quats = [None] * len(objs)

    for frame in frames_range:
        for i, obj in enumerate(objs):

            # Get object's transforms at that frame and from base frame.
            temp_obj, temp_matrix = new_object_from_frame(obj, frame)
            pos, quat, scale = temp_matrix.decompose()
            base_pos, base_quat, base_scale = base_objects_world_matrices[i].decompose()
            
            delta_pos = pos - base_pos
            value_x = (delta_pos.x / props.max_range) * 0.5 + 0.5
            value_y = (-delta_pos.y / props.max_range) * 0.5 + 0.5
            value_z = (delta_pos.z / props.max_range) * 0.5 + 0.5
            pixels_pos.extend((value_x, value_y, value_z, 1.0))

            quat_delta = quat @ base_quat.inverted()
            quat = quat_delta

            # Fix quaternion hemisphere flip.
            if prev_quats[i] is not None:
                if quat.dot(prev_quats[i]) < 0:
                    quat = -quat
            prev_quats[i] = quat.copy()

            quat.x = quat.x * 0.5 + 0.5
            quat.y = -quat.y * 0.5 + 0.5
            quat.z = quat.z * 0.5 + 0.5
            quat.w = -quat.w * 0.5 + 0.5
            pixels_nor.extend((quat.x, quat.y, quat.z, quat.w))

            # Cleanup.
            bpy.data.meshes.remove(temp_obj.data)

    destroy_base_objects(base_objects)

def new_object_from_frame(obj, frame):
    """Create a duplicate of object at a frame."""
    
    bpy.context.scene.frame_set(frame)
    evaluated_obj = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    world_mat = evaluated_obj.matrix_world.copy()
    
    # Create new object with a mesh from evaluated object. Transform is zeroed so we export is separately
    copied_object = bpy.data.objects.new("vat_frame.001", bpy.data.meshes.new_from_object(evaluated_obj))
    return copied_object, world_mat

def loop_animation(props, pixels_pos, pixels_nor, texture_width, texture_height):
    """Grabs already baked pixels and blends the beginning with the end to create smooth transition. Overrides the inputed pixel data"""

    # Get parameters
    num_of_elements_to_affect = props.looping_frame_count * texture_width * 4
    texture_height -= props.looping_frame_count

    # Position texture
    if props.include_position:
        for i, (original_pixels, pixels_from_top) in enumerate(zip(pixels_pos, pixels_pos[-num_of_elements_to_affect:])):
                alpha = (i // (texture_width * 4)) / props.looping_frame_count
                pixels_pos[i] = pixels_from_top * (1.0 - alpha) + original_pixels * alpha
        
        pixels_pos = pixels_pos[:-num_of_elements_to_affect]

    # Rotation texture
    if props.include_rotation:
        frames_ending = pixels_nor[-num_of_elements_to_affect:]
        for i in range(0, num_of_elements_to_affect, 4):
            alpha = (i // (texture_width * 4)) / props.looping_frame_count
            
            vec3_original = mathutils.Vector((pixels_nor[i + 0], pixels_nor[i + 1], pixels_nor[i + 2]))
            vec3_rotated = mathutils.Vector((frames_ending[i + 0], frames_ending[i + 1], frames_ending[i + 2]))
            vec3_lerped = vec3_rotated.lerp(vec3_original, alpha)
            vec3_lerped.normalize()
            
            pixels_nor[i + 0] = vec3_lerped.x
            pixels_nor[i + 1] = vec3_lerped.y
            pixels_nor[i + 2] = vec3_lerped.z
        
        pixels_nor = pixels_nor[:-num_of_elements_to_affect]

def get_path(in_path):
    """Get corrected export path."""
    final_path = in_path

    if not final_path and bpy.data.filepath:
        final_path = bpy.path.abspath("//")
        
    if "//" in final_path:
        blend_file_path = bpy.path.abspath("//")
        final_path = final_path.replace("//", blend_file_path)

    if not final_path.endswith("\\"):
        final_path += "\\"

    return final_path

def save_image(pixel_list, width, height, file_path_and_name):
    """Save selected pixel list to disk as a exr or png file."""

    image = bpy.data.images.new("temp_vat_image", width, height, is_data=True, float_buffer=True, alpha=True)
    image.pixels = pixel_list
    image.filepath_raw = file_path_and_name + ".exr"
    image.file_format = 'OPEN_EXR'
    image.save()
    bpy.data.images.remove(image)

def create_or_get_correct_uv_channel(bmesh, selected_channel, new_channel_name):
    '''Get the UV channel by index or create one if it doesn't exist.'''
    uv_channels = bmesh.loops.layers.uv
    number_of_channels = len(uv_channels)

    if number_of_channels > selected_channel:
        return uv_channels[selected_channel]

    # Fill empty slots to reach to the specified UV channel index.
    for _ in range(selected_channel - number_of_channels): 
        bmesh.loops.layers.uv.new("UVMap")
    
    return bmesh.loops.layers.uv.new(new_channel_name)

def create_uvs_vertex_mode(objs, props):
    """Make UVs for meshes for the vertex mode."""
    # We save the vertex ID in U component (UV channel 1 by default). Those are integer values.

    for obj in objs:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        uv_layer = create_or_get_correct_uv_channel(bm, props.uv_channel_vert_id, "VATID")

        for id, v in enumerate(bm.verts):
            for l in v.link_loops:
                l[uv_layer].uv = mathutils.Vector((id, 0.0))
        
        bm.to_mesh(obj.data)

def create_uvs_transform_mode(objs, props):
    """Create rigind body UV channels and set UVs to correct values."""
    # To handle rigid body type of Vertex Animations we need to have some sort of way to pass the origin position
    # to the shader. Maybe there's a better way to do that but for now to achieve that I'm creating additional UV channel.
    # First one handles Vertex ID + Z coordinate of the origin position, and the second one will hold the X and Y coordinated.
    # I can retreive them in the shader later on to create a pivot representation in the shader.
     
    for id, obj in enumerate(objs):
        bm = bmesh.new()
        bm.from_mesh(obj.data)

        uv_layer_idz = create_or_get_correct_uv_channel(bm, props.uv_channel_trans_id, "VATID_PIVOTZ")
        uv_layer_xy = create_or_get_correct_uv_channel(bm, props.uv_channel_trans_pivot, "PIVOTX_PIVOTY")

        for v in bm.verts:
            for l in v.link_loops:
                l[uv_layer_idz].uv = mathutils.Vector((id, 1.0 - obj.matrix_world.translation.z))
                l[uv_layer_xy].uv = mathutils.Vector((obj.matrix_world.translation.x, 1.0 - obj.matrix_world.translation.y * -1.0))
        
        bm.to_mesh(obj.data)