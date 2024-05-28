bl_info = {
    "name": "Runescape Import",
    "blender": (3, 00, 0),
    "category": "Object",
}

import bpy
import json
import os
import colorsys

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from pathlib import Path

class OT_TestOpenFilebrowser(Operator, ImportHelper):
    bl_idname = "test.open_filebrowser" 
    bl_label = "Open Json File"
    
    filter_glob: StringProperty(default='*.json', options={'HIDDEN'} )
    scale_down: BoolProperty( name='Scale Down', description='Scale the model down by 128', default=True, )
    
    def execute(self, context):

        filename, extension = os.path.splitext(self.filepath)
        path = filename + extension
        file = open(path)
        data = json.load(file)
        name = Path(path).stem
        file.close
        
        use_vertex_colours = data['useVertexColours']
        verts = data['vertices']
        edges = []
        faces = data['faces']
        vertex_colours = data['vertexColours']
        vertex_colour_index = data['vertexColourIndex']
        face_colours = data['faceColours']
        face_colour_index = data['faceColourIndex']
        priorities = data['priorities']
        client_ticks = data['clientTicks']
        anim_verts = data['animVertices']
        
        vertices = []
        if self.scale_down:
            for i in range(len(verts)):
                v = verts[i]
                vX = v[0] / 128
                vY = v[2] / 128
                vZ = v[1] * -1 / 128
                vertices.append([vX, vY, vZ])
        else:
            for i in range(len(verts)):
                v = verts[i]
                vX = v[0]
                vY = v[2]
                vZ = v[1] * -1
                vertices.append([vX, vY, vZ])

        anim_vertices = []
        if self.scale_down:
            for i in range(len(anim_verts)):
                model = anim_verts[i]
                anim_vertices_model = []
                for m in range(len(model)):
                    v = model[m]
                    vX = v[0] / 128
                    vY = v[2] / 128
                    vZ = v[1] * -1 / 128
                    anim_vertices_model.append([vX, vY, vZ])
                anim_vertices.append(anim_vertices_model)
        else:
            for i in range(len(anim_verts)):
                model = anim_verts[i]
                anim_vertices_model = []
                for m in range(len(model)):
                    v = model[m]
                    vX = v[0]
                    vY = v[2]
                    vZ = v[1] * -1
                    anim_vertices_model.append([vX, vY, vZ])
                anim_vertices.append(anim_vertices_model)

        me = bpy.data.meshes.new("me")
        me.from_pydata(vertices, edges, faces)
        ob = bpy.data.objects.new("Object", me)
        bpy.context.collection.objects.link(ob)
        ob.name = name
        
        mats = []
        
        fPrio = []
        for f in priorities:
            if f not in fPrio:
                fPrio.append(f)
        
        has_priorities = False
        if bpy.app.version < (4, 00, 0) and len(fPrio) > 1:
            has_priorities = True
            fPrio = sorted(fPrio)
            for f in range(len(priorities)):
                for i in range(len(fPrio)):
                    if priorities[f] == fPrio[i]:
                        priorities[f] = i

            max = len(fPrio) - 1
            for f in range(len(priorities)):
                priorities[f] = max - priorities[f]
            
            for f in range(len(fPrio)):
                ob.face_maps.new(name=str(max - f))

        if use_vertex_colours:
            vertex_colors_name = "vert_colors"
            me.vertex_colors.new(name=vertex_colors_name)
            color_layer = me.vertex_colors[vertex_colors_name]

            converted_colours = []
            # Convert hlsa to rgba
            for i in range(len(vertex_colours)):
                faceVerts = vertex_colours[i]
                rgb = colorsys.hls_to_rgb(faceVerts[0], faceVerts[1], faceVerts[2])
                converted_colours.append([rgb[0], rgb[2], rgb[1], faceVerts[3]])

            for f in range(len(me.polygons)):
                poly = me.polygons[f]
                for v in range(len(poly.vertices)):
                    vert_i_loop = poly.loop_indices[v]
                    convert_idx = vertex_colour_index[f * 3 + v]
                    color_layer.data[vert_i_loop].color = converted_colours[convert_idx]

            mat = bpy.data.materials.new(name="Material")
            mat.use_nodes = True
            ob.data.materials.append(mat)
            principled = mat.node_tree.nodes["Principled BSDF"]
            principled.inputs["Roughness"].default_value = 1
            vertex_shader = mat.node_tree.nodes.new(type='ShaderNodeVertexColor')
            vertex_shader.location = (-200, 300)
            links = mat.node_tree.links
            links.new(vertex_shader.outputs[0], principled.inputs[0])
            
        else:
            for f in range(len(face_colours)):
                c = face_colours[f]
                h = c[0]
                l = c[1]
                s = c[2]
                a = c[3]

                mat = bpy.data.materials.new(name="Material")
                mat.use_nodes = True
                ob.data.materials.append(mat)
                mats.append(mat)
                
                rgb = colorsys.hls_to_rgb(h, l, s)
                
                principled = mat.node_tree.nodes["Principled BSDF"]
                principled.inputs["Base Color"].default_value = (rgb[0], rgb[2], rgb[1], 1)
                principled.inputs["Alpha"].default_value = a
                principled.inputs["Roughness"].default_value = 1
                if a < 1:
                    mat.blend_method = 'BLEND'
                ob.data.polygons[f].material_index = len(mats) - 1

            for f in range(len(face_colour_index)):
                index = face_colour_index[f]
                ob.data.polygons[f].material_index = index
            
        if has_priorities:
            for f in range(len(faces)):
                p = priorities[f]
                i = [f]
                ob.face_maps[p].add(i)

        data_verts = ob.data.vertices
        frame_rate = bpy.context.scene.render.fps / bpy.context.scene.render.fps_base

        for e in range(len(client_ticks)):
            vert_series = anim_vertices[e]
            client_tick = client_ticks[e] * 0.02 * frame_rate
            for i in range(len(data_verts)):
                v = data_verts[i]
                v.co.x = vert_series[i][0]
                v.co.y = vert_series[i][1]
                v.co.z = vert_series[i][2]
                v.keyframe_insert("co", frame = client_tick)

        for obj in bpy.data.objects:
            obj.select_set(False)
        
        ob.select_set(True)

        return {'FINISHED'}
    
addon_keymaps = []

def register(): 
    bpy.utils.register_class(OT_TestOpenFilebrowser) 
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(OT_TestOpenFilebrowser.bl_idname, 'I', 'PRESS', ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))
    
def unregister(): 
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    bpy.utils.unregister_class(OT_TestOpenFilebrowser) 
    
if __name__ == "__main__": 
    register()
    bpy.ops.test.open_filebrowser('INVOKE_DEFAULT')
