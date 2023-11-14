import bpy # type: ignore
import math
from mathutils import Euler, Matrix, Vector, Quaternion # type: ignore

########################## Divider ##########################

class O_BonePoseYUp(bpy.types.Operator):
    bl_idname = "bone.pose_y_up"
    bl_label = "90 0 0"
    bl_description = "选中骨骼Y轴向上右手坐标系, 请先应用骨架旋转"

    def execute(self, context):

        obj = context.active_object
        if obj and obj.type == 'ARMATURE': # 检查对象是否为骨骼对象
            if context.selected_pose_bones: #有选择骨骼

                order_selected_pose_bones = []
                for bone1 in obj.pose.bones: #遍历骨架中的每一根骨骼，若被选中则加入list, 保证顺序正确
                    for bone2 in context.selected_pose_bones:
                        if bone1 == bone2 :
                            order_selected_pose_bones.append(bone1)

                for bone in order_selected_pose_bones:
                    new_rotation = Euler((math.radians(90), math.radians(0), math.radians(0)), 'XYZ')
                    new_matrix = new_rotation.to_matrix().to_4x4()
                    new_matrix.translation = bone.matrix.translation
                    bone.matrix = new_matrix
                    # 刷新
                    bpy.context.view_layer.update()

        return {"FINISHED"}
    
class O_BonePoseZUp(bpy.types.Operator):
    bl_idname = "bone.pose_z_up"
    bl_label = "0 0 0"
    bl_description = "选中骨骼Z轴向上右手坐标系, 请先应用骨架旋转"

    def execute(self, context):

        obj = context.active_object
        if obj and obj.type == 'ARMATURE': # 检查对象是否为骨骼对象
            if context.selected_pose_bones: #有选择骨骼

                order_selected_pose_bones = []
                for bone1 in obj.pose.bones: #遍历骨架中的每一根骨骼，若被选中则加入list, 保证顺序正确
                    for bone2 in context.selected_pose_bones:
                        if bone1 == bone2 :
                            order_selected_pose_bones.append(bone1)

                for bone in order_selected_pose_bones:
                    new_rotation = Euler((math.radians(0), math.radians(0), math.radians(0)), 'XYZ')
                    new_matrix = new_rotation.to_matrix().to_4x4()
                    new_matrix.translation = bone.matrix.translation
                    bone.matrix = new_matrix
                    # 刷新
                    bpy.context.view_layer.update()

        return {"FINISHED"}

class O_BonePoseUpRight(bpy.types.Operator):
    bl_idname = "bone.pose_upright"
    bl_label = "自动摆正骨骼"
    bl_description = "选择当前朝向相近的正交方向 by 夜曲"

    def execute(self, context):

        target_angles = [-180, -90, 0, 90, 180]
        obj = context.active_object
        if obj and obj.type == 'ARMATURE': # 检查对象是否为骨骼对象
            if context.selected_pose_bones: #有选择骨骼

                order_selected_pose_bones = []
                for bone1 in obj.pose.bones: #遍历骨架中的每一根骨骼，若被选中则加入list, 保证顺序正确
                    for bone2 in context.selected_pose_bones:
                        if bone1 == bone2 :
                            order_selected_pose_bones.append(bone1)

                for bone in order_selected_pose_bones:
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

class O_BonePoseX90(bpy.types.Operator):
    bl_idname = "bone.pose_x90"
    bl_label = "绕x旋转90°"
    bl_description = ""

    def execute(self, context):

        obj = context.active_object
        if obj and obj.type == 'ARMATURE': # 检查对象是否为骨骼对象
            if context.selected_pose_bones: #有选择骨骼

                order_selected_pose_bones = []
                for bone1 in obj.pose.bones: #遍历骨架中的每一根骨骼，若被选中则加入list, 保证顺序正确
                    for bone2 in context.selected_pose_bones:
                        if bone1 == bone2 :
                            order_selected_pose_bones.append(bone1)

                for bone in order_selected_pose_bones:
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

class O_BonePoseY90(bpy.types.Operator):
    bl_idname = "bone.pose_y90"
    bl_label = "绕y旋转90°"
    bl_description = ""
    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'ARMATURE': # 检查对象是否为骨骼对象
            if context.selected_pose_bones: #有选择骨骼
                order_selected_pose_bones = []
                for bone1 in obj.pose.bones: #遍历骨架中的每一根骨骼，若被选中则加入list, 保证顺序正确
                    for bone2 in context.selected_pose_bones:
                        if bone1 == bone2 :
                            order_selected_pose_bones.append(bone1)
                for bone in order_selected_pose_bones:
                    original_matrix = bone.matrix.copy()
                    new_rotation = Euler((math.radians(0), math.radians(90), math.radians(0)), 'XYZ')
                    rotation_matrix = new_rotation.to_matrix().to_4x4()
                    new_matrix = rotation_matrix @ original_matrix
                    new_matrix.translation = bone.matrix.translation
                    bone.matrix = new_matrix
                    bpy.context.view_layer.update()
        return {"FINISHED"}
    
class O_BonePoseZ90(bpy.types.Operator):
    bl_idname = "bone.pose_z90"
    bl_label = "绕z旋转90°"
    bl_description = ""
    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'ARMATURE': # 检查对象是否为骨骼对象
            if context.selected_pose_bones: #有选择骨骼
                order_selected_pose_bones = []
                for bone1 in obj.pose.bones: #遍历骨架中的每一根骨骼，若被选中则加入list, 保证顺序正确
                    for bone2 in context.selected_pose_bones:
                        if bone1 == bone2 :
                            order_selected_pose_bones.append(bone1)
                for bone in order_selected_pose_bones:
                    original_matrix = bone.matrix.copy()
                    new_rotation = Euler((math.radians(0), math.radians(0), math.radians(90)), 'XYZ')
                    rotation_matrix = new_rotation.to_matrix().to_4x4()
                    new_matrix = rotation_matrix @ original_matrix
                    new_matrix.translation = bone.matrix.translation
                    bone.matrix = new_matrix
                    bpy.context.view_layer.update()
        return {"FINISHED"}

class O_BonePoseApply(bpy.types.Operator):
    bl_idname = "bone.pose_apply"
    bl_label = "应用骨架和姿态"
    bl_description = ""
    def execute(self, context):
        # 获取当前骨架的名称
        armature_name = bpy.context.active_object.name
        # 退出姿态模式，进入物体模式
        bpy.ops.object.mode_set(mode='OBJECT')
        # 获取当前骨架对象
        armature = bpy.data.objects[armature_name]

        # 创建一个列表来存储满足条件的对象
        objects_to_modify = []
        # 遍历骨架的子级物体
        for child in armature.children:
            # 将子级物体设为活动对象
            bpy.context.view_layer.objects.active = child
            # 检查子级物体上是否有骨架修改器
            armature_modifier = None
            for modifier in child.modifiers:
                if modifier.type == 'ARMATURE' and modifier.object == armature:
                    # 确保骨架修改器的绑定对象是之前保存的骨架名称
                    if modifier.object.name == armature_name:
                        armature_modifier = modifier
                        # 如果存在骨架修改器，应用它
                        bpy.ops.object.modifier_apply(modifier=armature_modifier.name)
                        objects_to_modify.append(child)  # 将满足条件的对象添加到列表中


        # 将骨架设为活动对象，进入姿态模式 应用姿态
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.armature_apply(selected=False)
        
        # 回到物体模式
        bpy.ops.object.mode_set(mode='OBJECT')
        # 遍历满足条件的对象的列表，为它们添加骨架修改器
        for obj in objects_to_modify:
            bpy.context.view_layer.objects.active = obj
            modifier = obj.modifiers.new(name="Armature", type='ARMATURE')
            modifier.object = armature
            
        # 将骨架设为活动对象
        bpy.context.view_layer.objects.active = armature
        try:
            for fc in armature.animation_data.action.fcurves:
                # 删除关键帧
                armature.animation_data.action.fcurves.remove(fc)
        except:
            self.report({'INFO'}, "没有可删除的关键帧")
        # 进入姿态模式
        bpy.ops.object.mode_set(mode='POSE')

        return {"FINISHED"}

class O_BonePosePrint(bpy.types.Operator):
    bl_idname = "bone.pose_print"
    bl_label = "打印骨骼名称"
    bl_description = ""
    def execute(self, context):
        for bone in context.selected_pose_bones:
            print(bone.name)

        return {"FINISHED"}

class P_BonePose(bpy.types.Panel):
    bl_idname = "PT_BonePose"
    bl_label = "姿态模式"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bone+'  # 这里设置自定义标签的名称
    #bl_options = {'DEFAULT_'} #默认折叠

    def draw(self, context):
        layout = self.layout
        if context.mode == "POSE":
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator(O_BonePoseYUp.bl_idname, text=O_BonePoseYUp.bl_label)
            row.operator(O_BonePoseZUp.bl_idname, text=O_BonePoseZUp.bl_label)
            col.operator(O_BonePoseUpRight.bl_idname, text=O_BonePoseUpRight.bl_label)
            #摆正后各方向旋转
            row = col.row(align=True)
            row.operator(O_BonePoseX90.bl_idname, text="X 90", icon="DRIVER_ROTATIONAL_DIFFERENCE")
            row.operator(O_BonePoseY90.bl_idname, text="Y 90", icon="DRIVER_ROTATIONAL_DIFFERENCE")
            row.operator(O_BonePoseZ90.bl_idname, text="Z 90", icon="DRIVER_ROTATIONAL_DIFFERENCE")
            #快速应用为静止姿态，而物体不形变（先物体应用骨骼修改器）
            layout.operator(O_BonePoseApply.bl_idname, text=O_BonePoseApply.bl_label)
            # 打印选择骨骼的名称
            layout.operator(O_BonePosePrint.bl_idname, text=O_BonePosePrint.bl_label)




# 注册插件
def register():
    bpy.utils.register_class(O_BonePoseYUp)
    bpy.utils.register_class(O_BonePoseZUp)
    bpy.utils.register_class(O_BonePoseUpRight)
    bpy.utils.register_class(O_BonePoseX90)
    bpy.utils.register_class(O_BonePoseY90)
    bpy.utils.register_class(O_BonePoseZ90)
    bpy.utils.register_class(O_BonePoseApply)
    bpy.utils.register_class(O_BonePosePrint)
    bpy.utils.register_class(P_BonePose)

# 注销插件
def unregister():
    bpy.utils.unregister_class(O_BonePoseYUp)
    bpy.utils.unregister_class(O_BonePoseZUp)
    bpy.utils.unregister_class(O_BonePoseUpRight)
    bpy.utils.unregister_class(O_BonePoseX90)
    bpy.utils.unregister_class(O_BonePoseY90)
    bpy.utils.unregister_class(O_BonePoseZ90)
    bpy.utils.unregister_class(O_BonePoseApply)
    bpy.utils.unregister_class(O_BonePosePrint)
    bpy.utils.unregister_class(P_BonePose)
