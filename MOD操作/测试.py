# type: ignore
import bpy
import random

class ObjType(bpy.types.Operator):
    def is_mesh(scene, obj):
        return obj.type == "MESH"
    
    def is_armature(scene, obj):
        return obj.type == "ARMATURE"

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

        box = layout.box()
        col = box.column(align=True)
        col.prop(context.scene, "sk_source_mesh", text = "", icon="MESH_DATA")
        if context.scene.sk_source_mesh:
            armature_mod = None
            armature_modifiers = [mod for mod in context.scene.sk_source_mesh.modifiers if mod.type == 'ARMATURE']
            
            if armature_modifiers:
                if len(armature_modifiers) == 1:
                    armature_mod = armature_modifiers[0]
                    col.label(text=f"骨架: {armature_mod.object.name if armature_mod.object else '无'}", icon='ARMATURE_DATA')
                else:
                    col.label(text="错误: 物体有多个骨架修改器", icon='ERROR')
            else:
                col.label(text="错误: 物体没有骨架修改器", icon='ERROR')
        col.operator(ApplyAsShapekey.bl_idname, icon="SHAPEKEY_DATA")


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
    
class ApplyAsShapekey(bpy.types.Operator):
    bl_idname = "xbone.apply_as_shapekey"
    bl_label = "应用为形态键"
    bl_description = "将当前骨架的姿态应用为目标物体的形态键"
    bl_options = {'REGISTER', 'UNDO'}
    
    def find_armature_modifier(self, obj):
        """查找物体的骨架修改器"""
        armature_modifiers = [mod for mod in obj.modifiers if mod.type == 'ARMATURE']
        
        if not armature_modifiers:
            self.report({'ERROR'}, "物体没有骨架修改器")
            return None
            
        if len(armature_modifiers) > 1:
            self.report({'ERROR'}, "物体有多个骨架修改器")
            return None
            
        return armature_modifiers[0]
    
    def execute(self, context):
        # 检查目标物体
        try:
            obj = bpy.data.objects.get(context.scene.sk_source_mesh.name)
        except:
            self.report({'ERROR'}, "似乎没有选择对象") 
            return {'FINISHED'}
            
        
        # 查找骨架修改器
        armature_mod = self.find_armature_modifier(obj)
        if not armature_mod:
            return {'CANCELLED'}
            
        armature = armature_mod.object
        if not armature:
            self.report({'ERROR'}, "骨架修改器没有指定骨架")
            return {'CANCELLED'}
            
        # 切换到物体模式
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = obj

        # 确保物体有形态键
        if not obj.data.shape_keys:
            obj.shape_key_add(name="Basis", from_mix=False)
            
        # 使用骨架修改器的保存为形态键功能
        try:
            bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=True, modifier=armature_mod.name)
            self.report({'INFO'}, f"已为 {obj.name} 从骨架修改器创建形态键")
        except Exception as e:
            self.report({'ERROR'}, f"应用形态键失败: {str(e)}")
            return {'CANCELLED'}
        finally:
            # 切换回姿态模式并清空变换
            bpy.context.view_layer.update()
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.transforms_clear()
        
        return {'FINISHED'}
    

def register():
    bpy.utils.register_class(P_DEMO)
    bpy.utils.register_class(MiniPlaneOperator)
    bpy.utils.register_class(RenameToComponents)
    bpy.utils.register_class(ApplyAsShapekey)
    bpy.types.Scene.sk_source_mesh = bpy.props.PointerProperty(
        description="选择编辑形态键的物体",
        type=bpy.types.Object, 
        poll=ObjType.is_mesh
        )

def unregister():
    bpy.utils.unregister_class(P_DEMO)
    bpy.utils.unregister_class(MiniPlaneOperator)
    bpy.utils.unregister_class(RenameToComponents)
    bpy.utils.unregister_class(ApplyAsShapekey)
    del bpy.types.Scene.sk_source_mesh
