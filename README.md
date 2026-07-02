# CK to Blender Import

To import Blender Model .json files from Creator's Kit -> Blender:

1) Download the most recent CK_to_Blender_addon.py file
2) Open Blender, go Edit -> Preferences -> Addons tab
3) Hit "Install." Find the CK_to_Blender_addon.py file you downloaded and select it
4) Enable the Runescape Import addon by checking the checkbox

To use the importer, use the hotkey Ctrl + Shift + I. Select the .json file you exported from Creator's Kit. You can choose whether to Scale Down from a size that Runescape understands to one more appropriate to Blender (scales by 1/128).

# Blender to CK Export

To export Blender files from Blender -> Creator's Kit:

1) Download the most recent Blender_to_CK_addon.py file
2) Open Blender, go Edit -> Preferences -> Addons tab
3) Hit "Install." Find the Blender_to_CK_addon.py file you downloaded and select it
4) Enable the Runescape Export addon by checking the checkbox

To use the exporter, use the hotkey Ctrl + Shift + E. Select the .json file you exported from Creator's Kit. Then, once in Creator's Kit, you can use the "Load Blender Model" option in the Model Organizer tab in the Toolbox to import a *static* model.

Note that this export feature in particular is quite primitive and restrictive:

1) In-game animations do not work on imported Blender models

2) The only material types used should be Principled BDSF. You may use the Alpha factor to apply transparency to the model

3) Make sure the model you're importing is only composed of triangles, no other polys. Add and Apply the Triangulate modifier if you're unsure if your model is only triangles

4) You may have to recalculate normals because Java only renders faces on one side, unlike Blender (switch to Edit mode, select the faces that are inverted/backwards, hit Ctrl + Shift + N to recalculate normals).

5) Runescape's scale is way, way larger than what you're used to in Blender. You may have to scale up your models by 100x for them to be visible in-game (and remember to go Ctrl + A and hit Apply All Transforms after scaling)
