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
from .operators import *

class VATBAKER_common_panel_labels():
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "VAT Baker"

class VATBAKER_PT_main_panel(VATBAKER_common_panel_labels, bpy.types.Panel):
    bl_idname = "VATBAKER_PT_main_panel"
    bl_label = "VAT Baker Settings"

    def draw(self, context):
        props = context.scene.vatbaker_props
        display_frames_range = props.frame_end + 1 - props.frame_start
        
        layout = self.layout

        col = layout.column(align=True)
        col.label(text="Check the tooltips for important info!", icon='MONKEY')
        
        layout.separator()

        col = layout.column(align=True)
        col.prop(props, "bake_mode", text="Mode")

        col = layout.column(align=True)
        col.label(text=f"Bake Range ({display_frames_range} frames):")
        col.prop(props, "frame_start", text="Start")
        col.prop(props, "frame_end", text="End")
        col.prop(props, "frame_base", text="Base Frame")
        
        col = layout.column(align=True)
        col.prop(props, "uv_channel", text="UV Channel Index")
        
        layout.separator()
        
        col = layout.column(align=True)
        col.label(text="Output Directory:")
        col.prop(props, "path", text="")
        col.operator(VATBAKER_OT_open_selected_directory.bl_idname, text="Open in File Explorer", icon="WINDOW")

        col = layout.column(align=True)
        col.label(text="File Name:")
        split = layout.split(factor=0.25, align=True)
        split.prop(props, "filename_prefix", text="")
        split.prop(props, "filename", text="")

        layout.separator()
    
        col = layout.column(align=True)
        col.label(text="Position")
        col.prop(props, "include_position")
        col.prop(props, "position_is_hdr")
        col.prop(props, "positon_suffix")

        layout.separator()

        col = layout.column(align=True)
        col.label(text="Rotation")
        col.prop(props, "include_rotation")
        col.prop(props, "rotation_is_hdr")
        col.prop(props, "rotation_suffix")

        layout.separator()

        col = layout.column(align=True)
        col.operator(VATBAKER_OT_bake_textures.bl_idname, text="Export Textures", icon="NODE_TEXTURE")
        col.operator(VATBAKER_OT_export_selected.bl_idname, text="Export Mesh", icon="CUBE")

class VATBAKER_PT_additional_settings(VATBAKER_common_panel_labels, bpy.types.Panel):
    bl_label = "Additional Settings"
    bl_parent_id = "VATBAKER_PT_main_panel"

    def draw(self, context):
        layout = self.layout
        props = context.scene.vatbaker_props

        col = layout.column(align=True)
        col.prop(props, "flip_vertically")
        col.prop(props, "step", text="Step Every:")
        col.prop(props, "looping_frame_count", text="Auto-Looping Range:")

class VATBAKER_PT_info(VATBAKER_common_panel_labels, bpy.types.Panel):
    bl_label = "Info"
    bl_parent_id = "VATBAKER_PT_main_panel"

    def draw(self, context):
        layout = self.layout
        objs = context.selected_objects
        props = context.scene.vatbaker_props

        display_frames_range = abs(props.frame_end - props.frame_start) + 1
        display_stats_count = display_frames_range - props.looping_frame_count
        display_collumns_count = 0
        
        if props.bake_mode == 'OPT_VERTS':
            for obj in objs:
                if obj.type == "MESH":
                    display_collumns_count += len(obj.data.vertices)
        elif props.bake_mode == 'OPT_TRANS':
            display_collumns_count = len(objs)

        col = layout.column(align=True)
        col.label(text="Texture Size:")
        col.label(text=f"{display_collumns_count} x {display_stats_count} px")
        
        col = layout.column(align=True)
        col.label(text="Outputs List:")
        if props.include_position:
            col.label(text=f"{props.filename_prefix}{props.filename}{props.positon_suffix}")
        if props.include_rotation:
            col.label(text=f"{props.filename_prefix}{props.filename}{props.rotation_suffix}")