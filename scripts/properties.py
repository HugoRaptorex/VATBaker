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

class VatBakerProperties(bpy.types.PropertyGroup):
    frame_base:             bpy.props.IntProperty(name="Base Frame", default=1, description="This is the frame of the animation that is going to be treated as a resting position of the mesh. Export the mesh from this frame to match the baked data offsets.")
    frame_start:            bpy.props.IntProperty(name="First Frame", default=1, description="This value will set the first frame to start baking the animation.")
    frame_end:              bpy.props.IntProperty(name="Last Frame", default=100, description="This value will set the last frame to end baking the animation (including this one).")
    filename:               bpy.props.StringProperty(name="Textures Name", default="baked_texture", description="Name of the outputted texture files.")
    filename_prefix:        bpy.props.StringProperty(name="Texture Name Prefix", default="T_")
    path:                   bpy.props.StringProperty(name="Output Directory", default="", subtype='DIR_PATH', description="Path to the output directory. Leave empty or enter // to set to the blend file directory. The blend file needs to be saved before baking to handle that.")
    include_position:       bpy.props.BoolProperty(name="Enable Position Bake", default=True, description="Bake position VAT texture")
    include_rotation:       bpy.props.BoolProperty(name="Enable Rotation Bake", default=True, description="Bake normal VAT texture")
    positon_suffix:         bpy.props.StringProperty(name="Suffix", default="_VAT_Position", description="Suffix that will be appended to the output file.")
    rotation_suffix:        bpy.props.StringProperty(name="Suffix", default="_VAT_Rotation", description="Suffix that will be appended to the output file.")
    flip_vertically:        bpy.props.BoolProperty(name="Invert Animation (Flip Y)", default=True, description="Effectively inverts the animation. Handy when exporting for Unreal or other DirectX based engines (flipped V coordinates).")
    step:                   bpy.props.IntProperty(name="Step", default=1, min=1, soft_max=20, description="Step every Nth frame to skip frames and save texture resolution. Can be useful for very long animations. Keep in mind thta when skipping many frames the final baked animation might differ, it might miss some important keyframes.")
    looping_frame_count:    bpy.props.IntProperty(name="Frames to blend", default=0, min=0, description="Amount of frames to blend. If this value is more than 0 the baker will blend the animation's end with beginning so that the looping is baked into the texture itself.")
    uv_channel_vert_id:     bpy.props.IntProperty(name="UV Vert ID", default=1, min=0, soft_max=4, description="UV channel index that will hold the vertex ID data.")
    uv_channel_trans_id:    bpy.props.IntProperty(name="UV Trans ID ", default=1, min=0, soft_max=4, description="UV channel index that will hold the object ID data.")
    uv_channel_trans_pivot: bpy.props.IntProperty(name="UV Trans Pivot", default=2, min=0, soft_max=4, description="UV channel index that will hold the object pivot data.")
    bake_mode:              bpy.props.EnumProperty(name="Bake Mode", default='OPT_VERTS', description="Select baking mode.",
                                                    items=[('OPT_VERTS', "Vertex", "Bakes vertex data into textures. Useful for deformations, skeletal animations and blend shapes."),
                                                           ('OPT_TRANS', "Transforms", "Bakes transforms into textures. Useful when baking many objects like rigid body simulation or particles.")])
    max_range:             bpy.props.FloatProperty(name="Max Range", default=1, description="Maximum range of the animation to use for LDR positions textures. If you want to use LDR textures (use different compression for position vat textures) you have to specify this value. Then, you have to set the same value in the shader to properly decode the values.")
