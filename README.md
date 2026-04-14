# VATBaker
A small tool I built for baking Vertex Animation Textures (VAT) directly in Blender.

Currently the plugin supports:
- Blender 4.5.3 LTS
- Unreal Engine 5.7

# Modes
The plugin operates in two modes: **Vertex** and **Transform**.

**Vertex mode** bakes detailed per-vertex data into textures. This makes it suitable for complex deformations, skeletal animations, blendshapes, and any effects that rely on individual vertex movement. This mode requires one UV channel to store VAT data.

**Transform mode** bakes only object-level transformations, making it ideal for rigid body simulations, destruction fragments, particle systems, and other scenarios where only position and rotation are needed. Since it does not store per-vertex data, the typical vertex count limit (usually around 8k) is no longer a constraint. This mode requires two UV channels to store VAT data.

# How to Use
Get the newest release [here.](https://github.com/HugoRaptorex/VATBaker/releases) To install follow the instalation guide in the release notes.

## In Blender
1. Choose a baking mode
2. Select a mesh (or meshes) that has some sort of animation applied to it - depending on the mode can be modifiers, bones, blendshapes or transforms, rigid body simualtions etc.
3. Set Start and End Frames - it's the range of frames to bake.
4. Set Base Frame - it's a base pose. The mesh has to be exported from this frame later.
5. Set Output Directory - leave empty if you want to export at the blend file location.
6. Set other optional settings if needed.
7. When you're done click Export Textures. This will trigger the baking process. The textures will be saved on your disk and the selected meshes will have the VAT UV channels created.
8. Then click Export Mesh which will prepare the mesh and open an export window. In Transform mode it will create and export a proxy mesh of all the selected meshes combined, with base frame transformations applied to them. You can delete that proxy mesh after.

## Unreal Engine
If you have the Unreal Engine VATBakerUtils plugin (get it in the realeases).

1. Import the textures and meshes into the engine.
3. You can use the Scripted Asset Action on the imported assets to quickly set some basic settings. You can also create a quick test materials with those.
4. Create a Material and use one of the provided Material Functions to sample the VAT textures - MF_VAT_SamplerVertex or MF_VAT_SamplerTransforms. You can also create a quick test material by selecting both position and rotation textures in the content browser and using a matching scripted action.

The scripted actions might not work with custom naming conventions.

## Other engines
Here's some notes on how to decode and handle VAT textures in different engines.
- Textures need to be either not compressed or compressed with some high quality compression. If you're using 8bit compression then remember to scale the sampled data with the correct range.
- To encode the data you have to remap the data to -1..1 with ``vat_texture.rgba * 2.0 - 1.0``. Then apply a range multiplier that matches the one in the Blender plugin's settings.
- All the deformations are baked in objects local space.
- Vertex mode's rotation texture holds raw local space normals and Tranform's mode - rotation quaternions.
- IDs are saved as integer values along U coordinate.
- For the Transform mode the object's pivots are saved in UVs. By default UV2.uv is XY and UV1.v is Z. You might need to addjust the values to cover the correct coordinate system of your engine.

# Additional Notes
- Autolooping feature might be buggy. I want to update it in some future update.
- Multiple meshes can be selected and the bake will combine them into one texture.
