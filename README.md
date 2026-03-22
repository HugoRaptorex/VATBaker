# VATBaker
A small tool I built for baking Vertex Animation Textures (VAT) directly in Blender.

# Installation Guide
1. Download repository as a zip file
2. In Blender go to Preferences > Add-ons > click on the v arrow and select "Install from Disk..."
3. Select the zip and open
Now the Add-on should be installed and you can enable/disable it.

The addon panel is located on the "N panel".

# How to use
1. Select a mesh that has some sort of animating deformations applied to it - can be modifiers, bones, blendshapes etc.
2. Set Bake Range - it's the range of frames to bake
3. Set Base Frame - it's a base pose (the mesh has to be exported from this frame as well)
4. Set Output Directory - leave empty if you want to export at the .blend file location
5. Set other optional settings
6. When you're done click Export Textures. This will trigger the baking process.

# Additional Notes
- Some features are still half baked and might be a bit buggy.
- It's good to have transforms of the meshes applied. (This needs waterproofing)
- Multiple meshes can be selected and the bake will combine them into one texture.
- At the moment when using Transforms Mode the exported meshes need to have the origin set at the world center. It's best to use the Export Mesh button - in that mode it will combine the meshes and copy them.  
