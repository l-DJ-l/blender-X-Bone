bl_info = {
    "name" : "X-Bone+",
    "author" : "xqfa",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}
import bpy
import random
import math
from mathutils import Euler, Matrix, Vector, Quaternion


class O_VertexGroupsDelAll(bpy.types.Operator):
    bl_idname = "vertex_groups.del_all"
    bl_label = "删除所有顶点组"
    bl_description = "删除选择物体的所有顶点组"
    
    def execute(self, context):
        # 遍历所选物体
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                # 获取物体的所有顶点组
                vertex_groups = obj.vertex_groups

                # 删除每个顶点组
                for group in vertex_groups:
                    obj.vertex_groups.remove(group)
                
                # 更新物体
                obj.update_tag()
            else:
                print("不是网络对象")
        return {'FINISHED'}

class O_VertexGroupsDelNone(bpy.types.Operator):
    bl_idname = "vertex_groups.del_none"
    bl_label = "删除无权重顶点组"
    bl_description = "删除选择物体中没有顶点权重的顶点组"
    
    def execute(self, context):
        # 遍历所选物体
        for obj in context.selected_objects:
            if obj and obj.type == 'MESH':
                
                # 获取所有的顶点组
                vertex_groups = obj.vertex_groups

                # 获取网格数据
                mesh = obj.data

                # 创建一个字典来存储顶点组的信息
                vertex_group_info = {}
                for group in vertex_groups:
                    vertex_group_info[group.name] = []

                # 遍历每个顶点
                for vertex in mesh.vertices:
                    for group in vertex.groups: #遍历单个顶点的顶点组
                        group_index = group.group
                        group_name = vertex_groups[group_index].name
                        weight = group.weight

                        # 将顶点和权重信息添加到字典中
                        vertex_group_info[group_name].append((vertex.index, weight))

                # 删除空的顶点组
                for group_name, vertex_info in vertex_group_info.items():
                    if not vertex_info:
                        # 删除顶点组
                        obj.vertex_groups.remove(obj.vertex_groups[group_name])
                # 打印功能  
                '''      
                for group_name, vertex_info in vertex_group_info.items():
                    print(f"顶点组: {group_name}")
                    for vertex, weight in vertex_info:
                        print(f"  顶点: {vertex}, 权重: {weight}")
                '''
                print("已删除空的顶点组。")
            else:
                print("请先选择一个Mesh对象作为活动对象。")

        return {'FINISHED'}

class O_BoneConnect(bpy.types.Operator):
    bl_idname = "bone.connect"
    bl_label = "选中骨骼取消相连项"
    bl_description = "编辑模式下选择骨骼取消与父级的相连"

    def execute(self, context):

        obj = context.active_object
        if obj and obj.type == 'ARMATURE': # 检查对象是否为骨骼对象
            if context.selected_bones: #编辑模式有选择骨骼
                for bone in context.selected_bones:
                    bone.use_connect = False

        return {"FINISHED"}

class O_BoneAllConnect(bpy.types.Operator):
    bl_idname = "bone.all_connect"
    bl_label = "骨架内所有骨骼取消相连项"
    bl_description = ""

    def execute(self, context):

        obj = context.active_object
        if obj and obj.type == 'ARMATURE': # 检查对象是否为骨骼对象
            save_mode = context.mode
            if save_mode == "EDIT_ARMATURE": save_mode = "EDIT"
            bpy.ops.object.mode_set(mode = 'EDIT') #进入编辑模式
            bpy.ops.armature.select_all(action='SELECT') #取消选择
            for bone in context.selected_bones:
                bone.use_connect = False
            bpy.ops.armature.select_all(action='DESELECT') #取消选择
            bpy.ops.object.mode_set(mode = save_mode) #返回之前的模式
        else:
            print("对象不是骨架")
        return {"FINISHED"}


class P_Optimization(bpy.types.Panel):
    bl_idname = "PT_Optimization"
    bl_label = "快捷操作"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bone+'  # 这里设置自定义标签的名称
    bl_options = {'DEFAULT_CLOSED'} #默认折叠

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator(O_VertexGroupsDelAll.bl_idname, text=O_VertexGroupsDelAll.bl_label)       
        row.operator(O_VertexGroupsDelNone.bl_idname, text=O_VertexGroupsDelNone.bl_label)

        row = layout.row(align=True)
        row.operator(O_BoneConnect.bl_idname, text=O_BoneConnect.bl_label)       
        row.operator(O_BoneAllConnect.bl_idname, text=O_BoneAllConnect.bl_label)

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


        # 将骨架设为活动对象
        bpy.context.view_layer.objects.active = armature
        # 进入姿态模式
        bpy.ops.object.mode_set(mode='POSE')
        # 应用姿态
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
        # 进入姿态模式
        bpy.ops.object.mode_set(mode='POSE')
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


# 自定义属性类
class PG_BoneWorldMatrix(bpy.types.PropertyGroup):
    #注册切换矩阵显示的布尔值
    pose_matrix: bpy.props.BoolProperty(
        name="矩阵", 
        default=True
    )
    edit_matrix: bpy.props.BoolProperty(
        name="矩阵", 
        default=True
    )

    #姿态全局
    def get_position(self):
        active_bone = bpy.context.active_pose_bone
        if active_bone:
            return active_bone.matrix.translation
        return (0.0, 0.0, 0.0)
    def set_position(self, value):
        active_bone = bpy.context.active_pose_bone
        if active_bone:
            active_bone.matrix.translation = value

    def get_euler_rotation(self):
        active_bone = bpy.context.active_pose_bone
        if active_bone:
            return active_bone.matrix.to_euler()
        return (0.0, 0.0, 0.0)
    def set_euler_rotation(self, value):
        active_bone = bpy.context.active_pose_bone
        if active_bone:
            new_rotation = Euler(value, 'XYZ')
            new_matrix = new_rotation.to_matrix().to_4x4()
            new_matrix.translation = active_bone.matrix.translation
            active_bone.matrix = new_matrix
            
    def get_quaternion_rotation(self):
        active_bone = bpy.context.active_pose_bone
        if active_bone:
            return active_bone.matrix.to_quaternion()
        return Quaternion()
    def set_quaternion_rotation(self, value):
        active_bone = bpy.context.active_pose_bone
        if active_bone:
            new_quat = Quaternion(value)
            new_matrix = new_quat.to_matrix().to_4x4()
            new_matrix.translation = active_bone.matrix.translation
            active_bone.matrix = new_matrix
                        
    position: bpy.props.FloatVectorProperty(
        name="Position",
        get=get_position,
        set=set_position,
        subtype='TRANSLATION',
        unit='LENGTH',
        size=3,
        precision=3,
    )
    
    euler_rotation: bpy.props.FloatVectorProperty(
        name="Euler Rotation",
        get=get_euler_rotation,
        set=set_euler_rotation,
        subtype='EULER',
        unit='ROTATION',
        size=3,
        precision=3,
    )
    
    quaternion_rotation: bpy.props.FloatVectorProperty(
        name="Quaternion Rotation",
        get=get_quaternion_rotation,
        set=set_quaternion_rotation,
        subtype='QUATERNION',
        unit='NONE',
        size=4,  # 四元数具有四个分量
        precision=3,
    )    

    #编辑模式
    def get_edit_position(self):
        active_bone = bpy.context.active_bone
        if active_bone:
            return active_bone.matrix.translation
        return (0.0, 0.0, 0.0)
    def set_edit_position(self, value):
        active_bone = bpy.context.active_bone
        if active_bone:
            new_matrix = active_bone.matrix
            new_matrix.translation = value
            active_bone.matrix = new_matrix

    def get_edit_euler_rotation(self):
        active_bone = bpy.context.active_bone
        if active_bone:
            return active_bone.matrix.to_euler()
        return (0.0, 0.0, 0.0)
    def set_edit_euler_rotation(self, value):
        active_bone = bpy.context.active_bone
        if active_bone:
            new_rotation = Euler(value, 'XYZ')
            new_matrix = new_rotation.to_matrix().to_4x4()
            new_matrix.translation = active_bone.matrix.translation
            active_bone.matrix = new_matrix
            
    def get_edit_quaternion_rotation(self):
        active_bone = bpy.context.active_bone
        if active_bone:
            return active_bone.matrix.to_quaternion()
        return Quaternion()
    def set_edit_quaternion_rotation(self, value):
        active_bone = bpy.context.active_bone
        if active_bone:
            new_quat = Quaternion(value)
            new_matrix = new_quat.to_matrix().to_4x4()
            new_matrix.translation = active_bone.matrix.translation
            active_bone.matrix = new_matrix
                        
    edit_position: bpy.props.FloatVectorProperty(
        name="Edit Position",
        get=get_edit_position,
        set=set_edit_position,
        subtype='TRANSLATION',
        unit='LENGTH',
        size=3,
        precision=3,
    )
    
    edit_euler_rotation: bpy.props.FloatVectorProperty(
        name="Edit Euler Rotation",
        get=get_edit_euler_rotation,
        set=set_edit_euler_rotation,
        subtype='EULER',
        unit='ROTATION',
        size=3,
        precision=3,
    )
    
    edit_quaternion_rotation: bpy.props.FloatVectorProperty(
        name="Edit Quaternion Rotation",
        get=get_edit_quaternion_rotation,
        set=set_edit_quaternion_rotation,
        subtype='QUATERNION',
        unit='NONE',
        size=4,  # 四元数具有四个分量
        precision=3,
    )    

# 添加一个操作类用于关键帧插入
class O_InsertKeyframe(bpy.types.Operator):
    bl_idname = "object.insert_keyframe"
    bl_label = "插入关键帧"
    bl_description = "这里其实并不支持关键帧，看看就好"
    
    active_property: bpy.props.StringProperty()  # 新增一个属性

    def execute(self, context):
        if self.active_property == 'position':
            bpy.ops.anim.keyframe_insert(type='Location')      
        elif self.active_property == 'euler_rotation':
            bpy.ops.anim.keyframe_insert(type='Rotation')               
        return {'FINISHED'}

class P_BonePoseMatrix(bpy.types.Panel):
    bl_label = "骨骼变换-姿态"
    bl_idname = "PT_BonePoseMatrix"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item' #出现在item面板
    bl_context = "posemode" #只在姿态模式出现

    def draw(self, context):
        layout = self.layout

        obj = bpy.context.active_object
        if obj and obj.type == 'ARMATURE': # 检查对象是否为骨骼对象
            if context.mode == 'POSE' and context.active_pose_bone: # 检查当前模式是否为姿态模式      

                row = layout.row()
                row.label(text=f"{context.active_object.name}: {context.active_pose_bone.name}")
                row.prop(context.scene.bone_world_matrix, "pose_matrix", text="", icon='OBJECT_DATA', toggle=True)

                # 全局
                split = layout.split(align=True)
                col = split.column(align=True)
                col.label(text="基于骨架坐标系")
                row = col.row()
                row.label(text="位置"); row.operator("object.insert_keyframe", text="", icon="KEY_HLT").active_property = 'position'
                col.prop(context.scene.bone_world_matrix, "position", text="")
                row = col.row()
                row.label(text="欧拉"); row.operator("object.insert_keyframe", text="", icon="KEY_HLT").active_property = 'euler_rotation'
                col.prop(context.scene.bone_world_matrix, "euler_rotation", text="")
                col.prop(context.scene.bone_world_matrix, "quaternion_rotation", text="四元数")
                if context.scene.bone_world_matrix.pose_matrix:
                    #col.prop(context.active_pose_bone, "matrix", text="矩阵")
                    #blender按列读取，但又按行填充，需要手动转置
                    col.label(text="矩阵:")
                    row = col.row(align=True) #align消除间距
                    row.prop(context.active_pose_bone, "matrix", index=0, text="")
                    row.prop(context.active_pose_bone, "matrix", index=4, text="")
                    row.prop(context.active_pose_bone, "matrix", index=8, text="")
                    row.prop(context.active_pose_bone, "matrix", index=12, text="")
                    row = col.row(align=True)
                    row.prop(context.active_pose_bone, "matrix", index=1, text="")
                    row.prop(context.active_pose_bone, "matrix", index=5, text="")
                    row.prop(context.active_pose_bone, "matrix", index=9, text="")
                    row.prop(context.active_pose_bone, "matrix", index=13, text="")
                    row = col.row(align=True)
                    row.prop(context.active_pose_bone, "matrix", index=2, text="")
                    row.prop(context.active_pose_bone, "matrix", index=6, text="")
                    row.prop(context.active_pose_bone, "matrix", index=10, text="")
                    row.prop(context.active_pose_bone, "matrix", index=14, text="")
                    row = col.row(align=True)
                    row.prop(context.active_pose_bone, "matrix", index=3, text="")
                    row.prop(context.active_pose_bone, "matrix", index=7, text="")
                    row.prop(context.active_pose_bone, "matrix", index=11, text="")
                    row.prop(context.active_pose_bone, "matrix", index=15, text="")

                #局部矩阵
                if context.scene.bone_world_matrix.pose_matrix:
                    #col.prop(context.active_pose_bone, "matrix_basis", text="矩阵")
                    col.label(text="局部姿态矩阵:")
                    row = col.row(align=True) #align消除间距
                    row.prop(context.active_pose_bone, "matrix_basis", index=0, text="")
                    row.prop(context.active_pose_bone, "matrix_basis", index=4, text="")
                    row.prop(context.active_pose_bone, "matrix_basis", index=8, text="")
                    row.prop(context.active_pose_bone, "matrix_basis", index=12, text="")
                    row = col.row(align=True)
                    row.prop(context.active_pose_bone, "matrix_basis", index=1, text="")
                    row.prop(context.active_pose_bone, "matrix_basis", index=5, text="")
                    row.prop(context.active_pose_bone, "matrix_basis", index=9, text="")
                    row.prop(context.active_pose_bone, "matrix_basis", index=13, text="")
                    row = col.row(align=True)
                    row.prop(context.active_pose_bone, "matrix_basis", index=2, text="")
                    row.prop(context.active_pose_bone, "matrix_basis", index=6, text="")
                    row.prop(context.active_pose_bone, "matrix_basis", index=10, text="")
                    row.prop(context.active_pose_bone, "matrix_basis", index=14, text="")
                    row = col.row(align=True)
                    row.prop(context.active_pose_bone, "matrix_basis", index=3, text="")
                    row.prop(context.active_pose_bone, "matrix_basis", index=7, text="")
                    row.prop(context.active_pose_bone, "matrix_basis", index=11, text="")
                    row.prop(context.active_pose_bone, "matrix_basis", index=15, text="")

class P_BoneEditMatrix(bpy.types.Panel):
    bl_label = "骨骼变换-编辑"
    bl_idname = "PT_BoneEditMatrix"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    bl_context = "armature_edit" #只在骨架编辑模式可见

    def draw(self, context):
        layout = self.layout

        obj = bpy.context.active_object
        if obj and obj.type == 'ARMATURE': # 检查对象是否为骨骼对象
            if context.mode == 'EDIT_ARMATURE' and context.active_bone: # 检查当前模式是否为编辑模式
                
                row = layout.row()
                row.label(text=f"{context.active_object.name}: {context.active_bone.name}")
                row.prop(context.scene.bone_world_matrix, "edit_matrix", text="", icon='OBJECT_DATA', toggle=True)

                split = layout.split(align=True)
                col = split.column(align=True)
                col.label(text="基于骨架坐标系")
                col.prop(context.scene.bone_world_matrix, "edit_position", text="位置")
                col.prop(context.scene.bone_world_matrix, "edit_euler_rotation", text="欧拉")
                col.prop(context.scene.bone_world_matrix, "edit_quaternion_rotation", text="四元数")
                if context.scene.bone_world_matrix.edit_matrix:
                    #col.prop(context.active_bone, "matrix", text="矩阵")
                    col.label(text="矩阵:")
                    row = col.row(align=True) #align消除间距
                    row.prop(context.active_bone, "matrix", index=0, text="")
                    row.prop(context.active_bone, "matrix", index=4, text="")
                    row.prop(context.active_bone, "matrix", index=8, text="")
                    row.prop(context.active_bone, "matrix", index=12, text="")
                    row = col.row(align=True)
                    row.prop(context.active_bone, "matrix", index=1, text="")
                    row.prop(context.active_bone, "matrix", index=5, text="")
                    row.prop(context.active_bone, "matrix", index=9, text="")
                    row.prop(context.active_bone, "matrix", index=13, text="")
                    row = col.row(align=True)
                    row.prop(context.active_bone, "matrix", index=2, text="")
                    row.prop(context.active_bone, "matrix", index=6, text="")
                    row.prop(context.active_bone, "matrix", index=10, text="")
                    row.prop(context.active_bone, "matrix", index=14, text="")
                    row = col.row(align=True)
                    row.prop(context.active_bone, "matrix", index=3, text="")
                    row.prop(context.active_bone, "matrix", index=7, text="")
                    row.prop(context.active_bone, "matrix", index=11, text="")
                    row.prop(context.active_bone, "matrix", index=15, text="")

# 注册插件
def register():

    bpy.utils.register_class(O_VertexGroupsDelAll)
    bpy.utils.register_class(O_VertexGroupsDelNone)
    bpy.utils.register_class(O_BoneConnect)
    bpy.utils.register_class(O_BoneAllConnect)
    bpy.utils.register_class(P_Optimization)
    
    bpy.utils.register_class(O_BonePoseYUp)
    bpy.utils.register_class(O_BonePoseZUp)
    bpy.utils.register_class(O_BonePoseUpRight)
    bpy.utils.register_class(O_BonePoseX90)
    bpy.utils.register_class(O_BonePoseY90)
    bpy.utils.register_class(O_BonePoseZ90)
    bpy.utils.register_class(O_BonePoseApply)
    bpy.utils.register_class(P_BonePose)

    bpy.utils.register_class(O_BoneEditYUp)
    bpy.utils.register_class(O_BoneEditZUp)
    bpy.utils.register_class(O_BoneEditUpRight)
    bpy.utils.register_class(O_BoneEditX90)
    bpy.utils.register_class(O_BoneEditY90)
    bpy.utils.register_class(O_BoneEditZ90)
    bpy.utils.register_class(P_BoneEdit)

    bpy.utils.register_class(O_InsertKeyframe)
    bpy.utils.register_class(PG_BoneWorldMatrix)
    bpy.types.Scene.bone_world_matrix = bpy.props.PointerProperty(type=PG_BoneWorldMatrix)
    bpy.utils.register_class(P_BonePoseMatrix)
    bpy.utils.register_class(P_BoneEditMatrix)

# 注销插件
def unregister():

    bpy.utils.unregister_class(O_VertexGroupsDelAll)
    bpy.utils.unregister_class(O_VertexGroupsDelNone)
    bpy.utils.unregister_class(O_BoneConnect)
    bpy.utils.unregister_class(O_BoneAllConnect)
    bpy.utils.unregister_class(P_Optimization)

    bpy.utils.unregister_class(O_BonePoseYUp)
    bpy.utils.unregister_class(O_BonePoseZUp)
    bpy.utils.unregister_class(O_BonePoseUpRight)
    bpy.utils.unregister_class(O_BonePoseX90)
    bpy.utils.unregister_class(O_BonePoseY90)
    bpy.utils.unregister_class(O_BonePoseZ90)
    bpy.utils.unregister_class(O_BonePoseApply)
    bpy.utils.unregister_class(P_BonePose)

    bpy.utils.unregister_class(O_BoneEditYUp)
    bpy.utils.unregister_class(O_BoneEditZUp)
    bpy.utils.unregister_class(O_BoneEditUpRight)
    bpy.utils.unregister_class(O_BoneEditX90)
    bpy.utils.unregister_class(O_BoneEditY90)
    bpy.utils.unregister_class(O_BoneEditZ90)
    bpy.utils.unregister_class(P_BoneEdit)

    bpy.utils.unregister_class(O_InsertKeyframe)
    bpy.utils.unregister_class(PG_BoneWorldMatrix)
    del bpy.types.Scene.bone_world_matrix
    bpy.utils.unregister_class(P_BonePoseMatrix)
    bpy.utils.unregister_class(P_BoneEditMatrix)


if __name__ == "__main__":
    register()

