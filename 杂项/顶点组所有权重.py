import bpy # type: ignore

class VertexGroupEditorPanel(bpy.types.Panel):
    bl_label = "Vertex Group Editor"
    bl_idname = "PT_VertexGroupEditor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        if obj and obj.type == 'MESH':
            vertex_group = obj.vertex_groups.active

            if vertex_group:
                layout.label(text="活动顶点组: " + vertex_group.name)
                layout.label(text="顶点权重:")

                for vertex in obj.data.vertices:
                    for group in vertex.groups:
                        if group.group == vertex_group.index:
                            row = layout.row()
                            row.label(text=f"顶点 {vertex.index}:")
                            row.prop(group, "weight", text="")

def register():
    bpy.utils.register_class(VertexGroupEditorPanel)

def unregister():
    bpy.utils.unregister_class(VertexGroupEditorPanel)

if __name__ == "__main__":
    register()
