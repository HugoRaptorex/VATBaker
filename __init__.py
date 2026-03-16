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
from .scripts.properties import *
from .scripts.operators import *
from .scripts.panels import *

bl_info = {
    "name": "VAT Baker",
    "author": "Piotr Charchut",
    "version": (1, 1),
    "blender": (4, 5, 3),
    "location": "View3D > Sidebar panel > VAT Baker",
    "description": "Simple Vertex Animation Textures baking utility.",
    "category": "Export",
}

classes_to_register = [
    VatBakerProperties,
    VATBAKER_OT_bake_textures,
    VATBAKER_OT_open_selected_directory,
    VATBAKER_OT_export_selected,
    VATBAKER_PT_main_panel,
    VATBAKER_PT_additional_settings,
    VATBAKER_PT_info,
]

def register():
    for cls in classes_to_register:
        bpy.utils.register_class(cls)

    bpy.types.Scene.vatbaker_props = bpy.props.PointerProperty(type=VatBakerProperties)

def unregister():
    for cls in reversed(classes_to_register):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.vatbaker_props
    
if __name__ == "__main__":
    register()