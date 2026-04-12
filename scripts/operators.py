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

import bpy, os, subprocess, platform
from .functions import *

class VATBAKER_OT_export_selected(bpy.types.Operator):
    bl_idname      = "vatbaker.export_selected"
    bl_label       = "VAT Export Selected"
    bl_description = "Opens an export window with VAT preset."
    bl_options     = { "REGISTER" }

    @classmethod
    def poll(cls, context):
        if not context.selected_objects:
            return False
        if not all(obj.type == "MESH" for obj in context.selected_objects):
            return False
        if context.mode != "OBJECT":
            return False

        return True
    
    def execute(self, context):
        props = context.scene.vatbaker_props
        path = get_path(props.path)

        context.scene.frame_set(props.frame_base)
        bpy.context.view_layer.update()
        
        # Simple export
        if props.bake_mode == 'OPT_VERTS':
            bpy.ops.export_scene.fbx("INVOKE_DEFAULT", use_selection=True, filepath=path, bake_anim=False)
            return {"FINISHED"}
        elif props.bake_mode == 'OPT_TRANS':
            
            # Copy objects
            selected_objs = bpy.context.selected_objects
            copied_objs = []

            for obj in selected_objs:
                obj_copy = obj.copy()
                obj_copy.data = obj.data.copy()
                matrix = obj_copy.matrix_world.copy()
                bpy.context.collection.objects.link(obj_copy)

                if obj_copy.rigid_body is not None:
                    bpy.context.view_layer.objects.active = obj_copy
                    bpy.ops.rigidbody.object_remove()

                obj_copy.matrix_world = matrix

                copied_objs.append(obj_copy)

            # Select correct objects
            for obj in bpy.context.selected_objects:
                obj.select_set(False)
            for obj in copied_objs:
                obj.select_set(True)

            # Join and reset pivot, export
            bpy.context.view_layer.objects.active = copied_objs[0]
            bpy.ops.object.join()
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bpy.ops.export_scene.fbx("INVOKE_DEFAULT", use_selection=True, filepath=path, bake_anim=False)
            return {"FINISHED"}



class VATBAKER_OT_open_selected_directory(bpy.types.Operator):
    bl_idname      = "vatbaker.open_selected_directory"
    bl_label       = "VAT Open Directory File Explorer"
    bl_description = "Open selected directory."
    bl_options     = { "REGISTER" }

    @classmethod
    def poll(cls, context):
        props = context.scene.vatbaker_props

        if not os.path.exists(get_path(props.path)):
            return False
        if not props.path and not bpy.data.filepath:
            return False

        return True

    def execute(self, context):
        props = context.scene.vatbaker_props
        path_to_open = get_path(props.path)
        system = platform.system()

        if system == "Windows":
            os.startfile(path_to_open)
        elif system == "Darwin":  
            # TODO(piotr): Didn't test on Mac
            subprocess.Popen(["open", path_to_open])
        else:  
            # TODO(piotr): Didn't test on Linux
            subprocess.Popen(["xdg-open", path_to_open])

        return {"FINISHED"}


class VATBAKER_OT_bake_textures(bpy.types.Operator):
    bl_idname      = "vatbaker.bake_textures"
    bl_label       = "Bake VAT Textures"
    bl_description = "Bake selected meshes animation to textures and create VAT UV sets. Processing might take a while when baking a lot of frames."
    bl_options     = { "REGISTER" }

    @classmethod
    def poll(cls, context):
        if not context.selected_objects:
            return False
        if not all(obj.type == "MESH" for obj in context.selected_objects):
            return False
        if context.mode != "OBJECT":
            return False

        return True
    
    def execute(self, context):
        # Get the settings.
        props = context.scene.vatbaker_props
        objs = context.selected_objects
        warning = False

        # Check if anything is selected.
        if not objs:
            self.report({"ERROR"}, "No objects selected!")
            return {"CANCELLED"}        

        # Check if path specified.
        if not props.path and not bpy.data.filepath:
            self.report({"ERROR"}, "Set an existing output directory or save the blend file before baking!")
            return {"CANCELLED"}
        
        # Check if it has a valid way to determine a true path.
        if not os.path.exists(get_path(props.path)):
            self.report({"ERROR"}, "Set an existing output directory or save the blend file before baking!")
            return {"CANCELLED"}
        
        # Check if any include is selected.
        if not (props.include_position or props.include_rotation):
            warning = True
            self.report({"WARNING"}, "No texture is being included in baking. Is this what you wanted?")
        
        # FIXME(piotr): Handle all the edge cases like the nth frame step and start_frame > end_frame. 
        # Also consider a scenario where there is more blending frames then half of the total frames. What happens then?
        if props.looping_frame_count > props.frame_end + 1 - props.frame_start:
            self.report({"ERROR"}, "Too many frames to blend! Blending frames count can't exceed the total number of frames!")
            return {"CANCELLED"}

        # Do the thing.
        bake_vat(objs, props)

        # Report if success.
        if not warning:
            self.report({"INFO"}, "Baking process successful! Remember to export the mesh with it's VAT UVs!")
        
        return {"FINISHED"}
    