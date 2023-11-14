import bpy # type: ignore
import math
from mathutils import Euler, Matrix, Vector, Quaternion # type: ignore

########################## Divider ##########################

class O_BoneEditYUp(bpy.types.Operator):
    bl_idname = "bone.edit_y_up"
    bl_label = "90 0 0"
    bl_description = "选中骨骼Y轴向上右手坐标系, 请先应用骨架旋转"

    def execute(self, context):

        obj = context.active_object
        if obj and obj.type == 'ARMATURE': # 检查对象是否为骨骼对象
            if context.selected_bones: #有选择骨骼

                order_selected_bones = []
                for bone1 in obj.data.bones: #遍历骨架中的每一根骨骼，若被选中则加入list, 保证顺序正确
                    for bone2 in context.selected_bones:
                        if bone1.name == bone2.name :
                            order_selected_bones.append(bone2)

                for bone in order_selected_bones:
                    new_rotation = Euler((math.radians(90), math.radians(0), math.radians(0)), 'XYZ')
                    new_matrix = new_rotation.to_matrix().to_4x4()
                    new_matrix.translation = bone.matrix.translation
                    bone.matrix = new_matrix
                    # 刷新
                    bpy.context.view_layer.update()
        return {"FINISHED"}
    
class O_BoneEditZUp(bpy.types.Operator):
    bl_idname = "bone.edit_z_up"
    bl_label = "0 0 0"
    bl_description = "选中骨骼Y轴向上右手坐标系, 请先应用骨架旋转"

    def execute(self, context):

        obj = context.active_object
        if obj and obj.type == 'ARMATURE': # 检查对象是否为骨骼对象
            if context.selected_bones: #有选择骨骼

                order_selected_bones = []
                for bone1 in obj.data.bones: #遍历骨架中的每一根骨骼，若被选中则加入list, 保证顺序正确
                    for bone2 in context.selected_bones:
                        if bone1.name == bone2.name :
                            order_selected_bones.append(bone2)

                for bone in order_selected_bones:
                    new_rotation = Euler((math.radians(0), math.radians(0), math.radians(0)), 'XYZ')
                    new_matrix = new_rotation.to_matrix().to_4x4()
                    new_matrix.translation = bone.matrix.translation
                    bone.matrix = new_matrix
                    # 刷新
                    bpy.context.view_layer.update()
        return {"FINISHED"}

class O_BoneEditUpRight(bpy.types.Operator):
    bl_idname = "bone.edit_upright"
    bl_label = "自动摆正骨骼"
    bl_description = "选择当前朝向相近的正交方向 by 夜曲"

    def execute(self, context):

        target_angles = [-180, -90, 0, 90, 180]
        obj = context.active_object
        if obj and obj.type == 'ARMATURE': # 检查对象是否为骨骼对象
            if context.selected_bones: #有选择骨骼

                order_selected_bones = []
                for bone1 in obj.data.bones: #遍历骨架中的每一根骨骼，若被选中则加入list, 保证顺序正确
                    for bone2 in context.selected_bones:
                        if bone1.name == bone2.name :
                            order_selected_bones.append(bone2)

                for bone in order_selected_bones:
                    angles_radians = bone.matrix.to_euler()
                    angles_degrees = (math.degrees(angles_radians.x),math.degrees(angles_radians.y),math.degrees(angles_radians.z))

                    x, y, z = angles_degrees
                    x = min(target_angles, key=lambda n: abs(n - x))
                    y = min(target_angles, key=lambda n: abs(n - y))
                    z = min(target_angles, key=lambda n: abs(n - z))
                    
                    new_rotation = Euler((math.radians(x), math.radians(y), math.radians(z)), 'XYZ')
                    new_matrix = new_rotation.to_matrix().to_4x4()
                    new_matrix.translation = bone.matrix.translation
                    bone.matrix = new_matrix
                    # 刷新
                    bpy.context.view_layer.update()

        return {"FINISHED"}

class O_BoneEditX90(bpy.types.Operator):
    bl_idname = "bone.edit_x90"
    bl_label = "绕x旋转90°"
    bl_description = ""

    def execute(self, context):

        obj = context.active_object
        if obj and obj.type == 'ARMATURE': # 检查对象是否为骨骼对象
            if context.selected_bones: #有选择骨骼

                order_selected_bones = []
                for bone1 in obj.data.bones: #遍历骨架中的每一根骨骼，若被选中则加入list, 保证顺序正确
                    for bone2 in context.selected_bones:
                        if bone1.name == bone2.name :
                            order_selected_bones.append(bone2)

                for bone in order_selected_bones:
                    # 获取骨骼的原始矩阵
                    original_matrix = bone.matrix.copy()
                    # 变换矩阵
                    new_rotation = Euler((math.radians(90), math.radians(0), math.radians(0)), 'XYZ')
                    rotation_matrix = new_rotation.to_matrix().to_4x4()
                    # 相乘
                    new_matrix = rotation_matrix @ original_matrix
                    # 使用原坐标
                    new_matrix.translation = bone.matrix.translation
                    # 赋值
                    bone.matrix = new_matrix
                    # 刷新
                    bpy.context.view_layer.update()

        return {"FINISHED"}

class O_BoneEditY90(bpy.types.Operator):
    bl_idname = "bone.edit_y90"
    bl_label = "绕y旋转90°"
    bl_description = ""

    def execute(self, context):

        obj = context.active_object
        if obj and obj.type == 'ARMATURE': # 检查对象是否为骨骼对象
            if context.selected_bones: #有选择骨骼

                order_selected_bones = []
                for bone1 in obj.data.bones: #遍历骨架中的每一根骨骼，若被选中则加入list, 保证顺序正确
                    for bone2 in context.selected_bones:
                        if bone1.name == bone2.name :
                            order_selected_bones.append(bone2)

                for bone in order_selected_bones:
                    original_matrix = bone.matrix.copy()
                    new_rotation = Euler((math.radians(0), math.radians(90), math.radians(0)), 'XYZ')
                    rotation_matrix = new_rotation.to_matrix().to_4x4()
                    new_matrix = rotation_matrix @ original_matrix
                    new_matrix.translation = bone.matrix.translation
                    bone.matrix = new_matrix
                    bpy.context.view_layer.update()

        return {"FINISHED"}

class O_BoneEditZ90(bpy.types.Operator):
    bl_idname = "bone.edit_z90"
    bl_label = "绕z旋转90°"
    bl_description = ""

    def execute(self, context):

        obj = context.active_object
        if obj and obj.type == 'ARMATURE': # 检查对象是否为骨骼对象
            if context.selected_bones: #有选择骨骼

                order_selected_bones = []
                for bone1 in obj.data.bones: #遍历骨架中的每一根骨骼，若被选中则加入list, 保证顺序正确
                    for bone2 in context.selected_bones:
                        if bone1.name == bone2.name :
                            order_selected_bones.append(bone2)

                for bone in order_selected_bones:
                    original_matrix = bone.matrix.copy()
                    new_rotation = Euler((math.radians(0), math.radians(0), math.radians(90)), 'XYZ')
                    rotation_matrix = new_rotation.to_matrix().to_4x4()
                    new_matrix = rotation_matrix @ original_matrix
                    new_matrix.translation = bone.matrix.translation
                    bone.matrix = new_matrix
                    bpy.context.view_layer.update()

        return {"FINISHED"}

class P_BoneEdit(bpy.types.Panel):
    bl_idname = "PT_BoneEdit"
    bl_label = "编辑模式"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bone+'  # 这里设置自定义标签的名称
    #bl_options = {'DEFAULT_CLOSED'} #默认折叠

    def draw(self, context):
        layout = self.layout
        if context.mode == "EDIT_ARMATURE":
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator(O_BoneEditYUp.bl_idname, text=O_BoneEditYUp.bl_label)
            row.operator(O_BoneEditZUp.bl_idname, text=O_BoneEditZUp.bl_label)
            col.operator(O_BoneEditUpRight.bl_idname, text=O_BoneEditUpRight.bl_label)
            #摆正后各方向旋转
            row = col.row(align=True)
            row.operator(O_BoneEditX90.bl_idname, text="X 90", icon="DRIVER_ROTATIONAL_DIFFERENCE")
            row.operator(O_BoneEditY90.bl_idname, text="Y 90", icon="DRIVER_ROTATIONAL_DIFFERENCE")
            row.operator(O_BoneEditZ90.bl_idname, text="Z 90", icon="DRIVER_ROTATIONAL_DIFFERENCE")

# 注册插件
def register():
    bpy.utils.register_class(O_BoneEditYUp)
    bpy.utils.register_class(O_BoneEditZUp)
    bpy.utils.register_class(O_BoneEditUpRight)
    bpy.utils.register_class(O_BoneEditX90)
    bpy.utils.register_class(O_BoneEditY90)
    bpy.utils.register_class(O_BoneEditZ90)
    bpy.utils.register_class(P_BoneEdit)

# 注销插件
def unregister():
    bpy.utils.unregister_class(O_BoneEditYUp)
    bpy.utils.unregister_class(O_BoneEditZUp)
    bpy.utils.unregister_class(O_BoneEditUpRight)
    bpy.utils.unregister_class(O_BoneEditX90)
    bpy.utils.unregister_class(O_BoneEditY90)
    bpy.utils.unregister_class(O_BoneEditZ90)
    bpy.utils.unregister_class(P_BoneEdit)