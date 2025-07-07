# type: ignore
import bpy
import random

class P_DEMO(bpy.types.Panel):
    bl_label = "测试"
    bl_idname = "X_PT_DEMO"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'XBone'
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator(MiniPlaneOperator.bl_idname, icon="MESH_CUBE")
        col.operator(RenameToComponents.bl_idname, icon="OUTLINER_OB_EMPTY")


class MiniPlaneOperator(bpy.types.Operator):
    bl_idname = "xbone.mini_plane"
    bl_label = "创建空模"
    bl_description = "创建一个极小的平面网格，并将其分配到两个顶点组中"
    bl_options = {'REGISTER', 'UNDO'}

    plane_size: bpy.props.FloatProperty(
        name="平面大小",
        description="平面的尺寸",
        default=0.0001,
        min=0.00001,
        max=0.001
    )

    primary_weight: bpy.props.FloatProperty(
        name="主权重",
        description="第一个顶点组的权重值",
        default=0.99,
        min=0.0,
        max=1.0
    )

    secondary_weight: bpy.props.FloatProperty(
        name="次权重",
        description="第二个顶点组的权重值",
        default=0.02,
        min=0.0,
        max=1.0
    )

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        # 获取当前选中的物体
        selected_objects = context.selected_objects

        for obj in selected_objects:
            # 确保物体是网格类型
            if obj.type != 'MESH':
                self.report({'WARNING'}, f"物体 {obj.name} 不是网格类型，已跳过")
                continue

            # 只选择当前物体
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')

            # 选择所有顶点并删除
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.delete(type='VERT')

            # 添加平面网格
            bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=True)

            # 缩放平面到极小尺寸
            bpy.ops.transform.resize(value=(self.plane_size, self.plane_size, self.plane_size))

            # 返回对象模式
            bpy.ops.object.mode_set(mode='OBJECT')

            # 确保至少有两个顶点组
            if len(obj.vertex_groups) < 2:
                # 清除现有顶点组
                for vg in obj.vertex_groups:
                    obj.vertex_groups.remove(vg)
                
                # 创建两个新的顶点组
                vg1 = obj.vertex_groups.new(name="0")
                vg2 = obj.vertex_groups.new(name="1")

            # 获取顶点组引用
            vg1 = obj.vertex_groups[0]
            vg2 = obj.vertex_groups[1]

            # 获取网格数据
            mesh = obj.data
            vertices = mesh.vertices

            # 将四个顶点分配到两个顶点组
            for v in vertices:
                vg1.add([v.index], self.primary_weight, 'REPLACE')
                vg2.add([v.index], self.secondary_weight, 'REPLACE')

            self.report({'INFO'}, 
                f"已处理物体: {obj.name}\n"
                f"顶点组1({vg1.name})权重: {self.primary_weight}\n"
                f"顶点组2({vg2.name})权重: {self.secondary_weight}"
            )

        return {'FINISHED'}

class RenameToComponents(bpy.types.Operator):
    bl_idname = "xbone.rename_to_components"
    bl_label = "重命名为Components格式"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}
        
        sorted_objects = sorted(selected_objects, key=lambda obj: obj.name)
        
        for index, obj in enumerate(sorted_objects, start=0):
            old_name = obj.name
            new_name = f"Component {index}"
            obj.name = new_name
            print(f"Renamed '{old_name}' to '{new_name}'")
        
        self.report({'INFO'}, f"Renamed {len(selected_objects)} objects")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(P_DEMO)
    bpy.utils.register_class(MiniPlaneOperator)
    bpy.utils.register_class(RenameToComponents)
    

def unregister():
    bpy.utils.unregister_class(P_DEMO)
    bpy.utils.unregister_class(MiniPlaneOperator)
    bpy.utils.unregister_class(RenameToComponents)
    
