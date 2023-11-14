import bpy # type: ignore
import math
from mathutils import Euler, Matrix, Vector, Quaternion # type: ignore

########################## Divider ##########################

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
    
########################## Divider ##########################

class P_BoneConnect(bpy.types.Panel):
    bl_idname = "PT_BoneConnect"
    bl_label = "骨骼相连项"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bone+'  # 这里设置自定义标签的名称

    def draw(self, context):
        layout = self.layout
        layout.operator(O_BoneConnect.bl_idname, text=O_BoneConnect.bl_label)       
        layout.operator(O_BoneAllConnect.bl_idname, text=O_BoneAllConnect.bl_label)

########################## Divider ##########################

def register():
    bpy.utils.register_class(O_BoneConnect)
    bpy.utils.register_class(O_BoneAllConnect)
    bpy.utils.register_class(P_BoneConnect)

def unregister():
    bpy.utils.unregister_class(O_BoneConnect)
    bpy.utils.unregister_class(O_BoneAllConnect)
    bpy.utils.unregister_class(P_BoneConnect)