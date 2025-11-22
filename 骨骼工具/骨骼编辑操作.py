# type: ignore
import bpy 
import math
from mathutils import Euler, Matrix, Vector, Quaternion

########################## Divider ##########################

class PG_BoneEditWorldProps(bpy.types.PropertyGroup):
    #注册切换矩阵显示的布尔值
    edit_matrix: bpy.props.BoolProperty(
        name="矩阵", 
        default=False
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

class O_BoneEditYUp(bpy.types.Operator):
    bl_idname = "xbone.edit_y_up"
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
    bl_idname = "xbone.edit_z_up"
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
    bl_idname = "xbone.edit_upright"
    bl_label = "自动摆正"
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
    bl_idname = "xbone.edit_x90"
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
    bl_idname = "xbone.edit_y90"
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
    bl_idname = "xbone.edit_z90"
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

########################## Divider ##########################

class O_BoneConnect(bpy.types.Operator):
    bl_idname = "xbone.connect"
    bl_label = "选中取消相连"
    bl_description = ""

    def execute(self, context):

        obj = context.active_object
        if obj and obj.type == 'ARMATURE': # 检查对象是否为骨骼对象
            if context.selected_bones: #编辑模式有选择骨骼
                for bone in context.selected_bones:
                    bone.use_connect = False

        return {"FINISHED"}

class O_BoneAllConnect(bpy.types.Operator):
    bl_idname = "xbone.all_connect"
    bl_label = "所有取消相连"
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
         

########################## Divider ##########################

class O_BoneMoveTailToChild(bpy.types.Operator):
    bl_idname = "xbone.move_tail_to_child"
    bl_label = "尾部对齐子级头部"
    bl_description = "将选中骨骼的尾部移动到其唯一被选中的子级骨骼的头部位置"

    def execute(self, context):
        # 确保在编辑模式下
        if context.mode != 'EDIT_ARMATURE':
            self.report({'WARNING'}, "必须在骨骼编辑模式下运行此操作")
            return {'CANCELLED'}
        
        # 获取骨架对象
        armature_obj = context.object
        if not armature_obj or armature_obj.type != 'ARMATURE':
            self.report({'WARNING'}, "未选择骨架对象")
            return {'CANCELLED'}
        
        # 获取当前选中的骨骼
        selected_bones = context.selected_editable_bones
        
        if not selected_bones:
            self.report({'WARNING'}, "没有选中任何骨骼")
            return {'CANCELLED'}
        
        # 创建选中骨骼名称的集合，用于快速查找
        selected_bone_names = {bone.name for bone in selected_bones}
        
        # 获取骨架的世界变换矩阵
        armature_matrix = armature_obj.matrix_world
        
        # 记录成功移动的骨骼数量
        moved_count = 0
        
        # 遍历所有选中的骨骼
        for bone in selected_bones:
            # 获取该骨骼的所有子级
            children = bone.children
            
            if not children:
                continue
            
            # 找出被选中的子级骨骼
            selected_children = [child for child in children if child.name in selected_bone_names]
            
            # 检查被选中的子级数量
            if len(selected_children) == 1:
                child_bone = selected_children[0]
                
                # 将骨骼尾部和子级头部转换到世界坐标系
                bone_tail_world = armature_matrix @ bone.tail
                child_head_world = armature_matrix @ child_bone.head
                
                # 计算在世界坐标系中的移动向量
                move_vector_world = child_head_world - bone_tail_world
                
                # 使用变换操作来移动骨骼尾部
                # 首先取消选择所有骨骼
                bpy.ops.armature.select_all(action='DESELECT')
                
                # 选择当前骨骼（只选择尾部）
                bone.select = True
                bone.select_head = False
                bone.select_tail = True
                
                # 设置当前骨骼为活动骨骼
                context.view_layer.objects.active = armature_obj
                armature_obj.data.edit_bones.active = bone
                
                # 使用transform.translate来移动尾部（在世界坐标系中）
                bpy.ops.transform.translate(value=move_vector_world)
                
                moved_count += 1
        
        # 恢复原始选择状态
        bpy.ops.armature.select_all(action='DESELECT')
        for bone in selected_bones:
            bone.select = True
            bone.select_head = True
            bone.select_tail = True
        
        if moved_count > 0:
            self.report({'INFO'}, f"成功移动了 {moved_count} 个骨骼的尾部")
        else:
            self.report({'WARNING'}, "没有符合条件的骨骼可以移动")
        
        return {'FINISHED'}
    
########################## Divider ##########################

class P_BoneEdit(bpy.types.Panel):
    bl_idname = "X_PT_BoneEdit"
    bl_label = "编辑模式"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'XBone'

    @classmethod
    def poll(cls, context):
        # 只有当主面板激活了此子面板时才显示
        return getattr(context.scene, 'active_xbone_subpanel', '') == 'BoneTools'

    def draw(self, context):
        layout = self.layout
        props = context.scene.bone_edit_world_props # 获取属性组
        if context.mode == "EDIT_ARMATURE":
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator(O_BoneEditYUp.bl_idname, text=O_BoneEditYUp.bl_label)
            row.operator(O_BoneEditZUp.bl_idname, text=O_BoneEditZUp.bl_label)
            row.operator(O_BoneEditUpRight.bl_idname, text=O_BoneEditUpRight.bl_label)
            #摆正后各方向旋转
            row = col.row(align=True)
            row.operator(O_BoneEditX90.bl_idname, text="X 90", icon="DRIVER_ROTATIONAL_DIFFERENCE")
            row.operator(O_BoneEditY90.bl_idname, text="Y 90", icon="DRIVER_ROTATIONAL_DIFFERENCE")
            row.operator(O_BoneEditZ90.bl_idname, text="Z 90", icon="DRIVER_ROTATIONAL_DIFFERENCE")

            row = col.row(align=True)
            row.operator(O_BoneConnect.bl_idname, text=O_BoneConnect.bl_label)       
            row.operator(O_BoneAllConnect.bl_idname, text=O_BoneAllConnect.bl_label)

            # 添加新的尾部对齐操作按钮
            row = col.row(align=True)
            row.operator(O_BoneMoveTailToChild.bl_idname, text=O_BoneMoveTailToChild.bl_label, icon='BONE_DATA')

            # 骨骼矩阵
            row = layout.row()
            row.label(text=f"{context.active_object.name}: {context.active_bone.name}")
            row.prop(props, "edit_matrix", text="", icon='OBJECT_DATA', toggle=True)
            if props.edit_matrix:
                split = layout.split(align=True)
                col = split.column(align=True)
                col.label(text="基于骨架坐标系")
                col.prop(props, "edit_position", text="位置")
                col.prop(props, "edit_euler_rotation", text="欧拉")
                col.prop(props, "edit_quaternion_rotation", text="四元数")
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
    bpy.utils.register_class(O_BoneEditYUp)
    bpy.utils.register_class(O_BoneEditZUp)
    bpy.utils.register_class(O_BoneEditUpRight)
    bpy.utils.register_class(O_BoneEditX90)
    bpy.utils.register_class(O_BoneEditY90)
    bpy.utils.register_class(O_BoneEditZ90)
    bpy.utils.register_class(O_BoneConnect)
    bpy.utils.register_class(O_BoneAllConnect)
    bpy.utils.register_class(O_BoneMoveTailToChild)
    bpy.utils.register_class(P_BoneEdit)
    bpy.utils.register_class(PG_BoneEditWorldProps)
    bpy.types.Scene.bone_edit_world_props = bpy.props.PointerProperty(type=PG_BoneEditWorldProps)


# 注销插件
def unregister():
    bpy.utils.unregister_class(O_BoneEditYUp)
    bpy.utils.unregister_class(O_BoneEditZUp)
    bpy.utils.unregister_class(O_BoneEditUpRight)
    bpy.utils.unregister_class(O_BoneEditX90)
    bpy.utils.unregister_class(O_BoneEditY90)
    bpy.utils.unregister_class(O_BoneEditZ90)
    bpy.utils.unregister_class(O_BoneConnect)
    bpy.utils.unregister_class(O_BoneAllConnect)
    bpy.utils.unregister_class(O_BoneMoveTailToChild)
    bpy.utils.unregister_class(P_BoneEdit)
    bpy.utils.unregister_class(PG_BoneEditWorldProps)
    del bpy.types.Scene.bone_edit_world_props