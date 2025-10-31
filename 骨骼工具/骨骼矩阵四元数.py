# type: ignore
import bpy 
import math
from mathutils import Euler, Matrix, Vector, Quaternion

########################## Divider ##########################

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

class P_BonePoseMatrix(bpy.types.Panel):
    bl_label = "骨骼变换-姿态"
    bl_idname = "X_PT_BonePoseMatrix"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'XBone' #出现在item面板
    bl_context = "posemode" #只在姿态模式出现

    @classmethod
    def poll(cls, context):
        # 只有当主面板激活了此子面板时才显示
        return context.scene.active_xbone_subpanel == 'BoneTools'

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
                row.label(text="位置")
                col.prop(context.scene.bone_world_matrix, "position", text="")
                row = col.row()
                row.label(text="欧拉")
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
    bl_idname = "X_PT_BoneEditMatrix"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'XBone'
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
    bpy.utils.register_class(PG_BoneWorldMatrix)
    bpy.types.Scene.bone_world_matrix = bpy.props.PointerProperty(type=PG_BoneWorldMatrix)
    bpy.utils.register_class(P_BonePoseMatrix)
    bpy.utils.register_class(P_BoneEditMatrix)

# 注销插件
def unregister():
    bpy.utils.unregister_class(PG_BoneWorldMatrix)
    del bpy.types.Scene.bone_world_matrix
    bpy.utils.unregister_class(P_BonePoseMatrix)
    bpy.utils.unregister_class(P_BoneEditMatrix)