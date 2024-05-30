bl_info = {
    "name": "Runescape Export",
    "blender": (3, 00, 0),
    "category": "Object",
}

import json
from json import JSONEncoder
import bpy
import bmesh
import colorsys
import codecs


class ModelDictionary():
    def __init__(self, useVertexColours, vertices, faces, vertexColours, vertexColourIndex, faceColours,
                 faceColourIndex, priorities, clientTicks, animVertices):
        self.useVertexColours = useVertexColours
        self.vertices = vertices
        self.faces = faces
        self.vertexColours = vertexColours
        self.vertexColourIndex = vertexColourIndex
        self.faceColours = faceColours
        self.faceColourIndex = faceColourIndex
        self.priorities = priorities
        self.clientTicks = clientTicks
        self.animVertices = animVertices


class Encoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def write_some_data(context, filepath):
    f = open(filepath, 'w', encoding='utf-8')
    f.write(context)
    f.close()
    return {'FINISHED'}


from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportSomeData(Operator, ExportHelper):
    bl_idname = "export_test.some_data"
    bl_label = "RS Model Export"
    filename_ext = ".json"
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,
    )

    scale_up: BoolProperty(
        name='Scale Up',
        description='Scale the model up by 128',
        default=True,
    )

    vertex_colours: BoolProperty(
        name='Vertex Colours',
        description='Export with Vertex Colours instead of Face Colours',
        default=False,
    )

    def execute(self, context):
        mode = bpy.context.active_object.mode
        if mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        ob = bpy.context.active_object
        md = ModelDictionary(self.vertex_colours, [], [], [], [], [], [], [], [], [])
        me = ob.data
        bm = bmesh.new()
        bm.from_mesh(me)

        if self.scale_up:
            for v in bm.verts:
                x = int(v.co[0] * 128)
                y = int(v.co[1] * 128)
                z = int(-1 * v.co[2] * 128)
                list = [x, z, y]
                md.vertices.append(list)
        else:
            for v in bm.verts:
                x = int(v.co[0])
                y = int(v.co[1])
                z = int(-1 * v.co[2])
                list = [x, z, y]
                md.vertices.append(list)

        for f in bm.faces:
            v_list = f.verts
            f1 = v_list[0].index
            f2 = v_list[1].index
            f3 = v_list[2].index
            it_list = [f1, f2, f3]
            md.faces.append(it_list)

        has_vertex_colours = len(me.vertex_colors) > 0
        if self.vertex_colours and has_vertex_colours:
            color_layer = me.vertex_colors[0]
            converted_colours = []
            vert_cols = []
            for f in range(len(me.polygons)):
                poly = me.polygons[f]
                for vert_i_poly, vert_i_mesh in enumerate(poly.vertices):
                    vert_i_loop = poly.loop_indices[vert_i_poly]
                    loop_color = color_layer.data[vert_i_loop].color
                    vert_cols.append((loop_color[0], loop_color[1], loop_color[2], loop_color[3]))

            for v in range(len(vert_cols)):
                vert_col = vert_cols[v]

                already_contains = False
                for c in range(len(converted_colours)):
                    col = converted_colours[c]
                    if col == vert_col:
                        already_contains = True
                        md.vertexColourIndex.append(c)
                        break

                if already_contains:
                    continue

                converted_colours.append(vert_col)
                color_hls = colorsys.rgb_to_hls(vert_col[0], vert_col[2], vert_col[1])
                color_hls_list = (color_hls[0], color_hls[1], color_hls[2], vert_col[3])
                md.vertexColours.append(color_hls_list)
                md.vertexColourIndex.append(len(md.vertexColours) - 1)

        else:
            for slot in ob.material_slots:
                mat = slot.material
                principled = mat.node_tree.nodes["Principled BSDF"].inputs
                color = principled["Base Color"].default_value
                color_hls = colorsys.rgb_to_hls(color[0], color[2], color[1])
                alpha = principled["Alpha"].default_value
                color_hls_list = [color_hls[0], color_hls[1], color_hls[2], alpha]
                md.faceColours.append(color_hls_list)

            for f in bm.faces:
                md.faceColourIndex.append(f.material_index)

        if bpy.app.version < (4, 00, 0):
            fm = bm.faces.layers.face_map.verify()
            max = 0
            for f in bm.faces:
                map_idx = f[fm]
                if map_idx >= 10:
                    max = 10
                    break
                if map_idx > max:
                    max = map_idx

            for f in bm.faces:
                map_idx = f[fm]
                if map_idx > 10:
                    map_idx = 10
                if map_idx < 0:
                    map_idx = 0
                map_idx = max - map_idx
                md.priorities.append(map_idx)
        else:
            for f in bm.faces:
                md.priorities.append(0)

        dump = json.dumps(md, separators=(',', ':'), cls=Encoder)
        return write_some_data(dump, self.filepath)


def menu_func(self, context):
    self.layout.operator(ExportSomeData.bl_idname)


addon_keymaps = []


def register():
    bpy.utils.register_class(ExportSomeData)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(ExportSomeData.bl_idname, 'E', 'PRESS', ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    bpy.utils.unregister_class(ExportSomeData)


if __name__ == "__main__":
    register()
    bpy.ops.export_test.some_data('INVOKE_DEFAULT')
