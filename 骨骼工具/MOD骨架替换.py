# type: ignore
import bpy
import os
import csv, json
from bpy_extras.io_utils import ImportHelper

class ObjType(bpy.types.Operator):
    def is_mesh(scene, obj):
        return obj.type == "MESH"
    
    def is_armature(scene, obj):
        return obj.type == "ARMATURE"

class O_ImportCSV(bpy.types.Operator, ImportHelper):
    bl_idname = "xbone.csv_import"
    bl_label = "导入CSV"
    bl_description = "导入时右上角选择编码格式"
    filename_ext = ".csv"
    filter_glob: bpy.props.StringProperty(
        default="*.csv",
        options={'HIDDEN'},
    )

    def execute(self, context):
        csv_file = self.filepath

        if not csv_file or not os.path.exists(csv_file):
            self.report({'ERROR'}, "请选择有效的CSV文件")
            return {'CANCELLED'}

        # 尝试的编码顺序
        encodings = ['utf-8', 'gbk', 'utf-16']
        
        for encoding in encodings:
            try:
                with open(csv_file, 'r', newline='', encoding=encoding) as file:
                    reader = csv.reader(file)
                    csv_data = list(reader)
                    # 存储为 JSON 字符串
                    context.scene["xbone_csv_data"] = json.dumps(csv_data)
                
                self.report({'INFO'}, f"CSV文件已导入({encoding}): {csv_file}")
                return {'FINISHED'}
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.report({'ERROR'}, f"导入CSV文件时出现错误: {e}")
                return {'CANCELLED'}
        
        self.report({'ERROR'}, "无法解码CSV文件，请尝试转换为UTF-8编码")
        return {'CANCELLED'}


class O_BoneSimpleMapping(bpy.types.Operator):
    bl_idname = "xbone.simple_mapping"
    bl_label = "简化骨骼"
    bl_description = ""
    
    def execute(self, context):
        if context.scene.xbone_csv_data == "":
            self.report({'ERROR'}, "似乎没有导入CSV文件") 
            return {'FINISHED'}
        try:
            SourceArmature = bpy.data.objects.get(context.scene.simple_source_armature.name)
        except:
            self.report({'ERROR'}, "似乎没有选择对象") 
            return {'FINISHED'}
        
        csv_data = json.loads(context.scene["xbone_csv_data"])
        simple_main_column = context.scene.simple_main_column #0开始数列
        simple_save_column = context.scene.simple_save_column
        simple_toactive_column = context.scene.simple_toactive_column
        simple_active_column = context.scene.simple_active_column
        bone_main = []
        bone_save = []
        bone_mapping = {}
        
        # 读取CSV的数据，跳过标题行(第一行)
        for row in csv_data[1:]:
            if len(row) <= simple_main_column:
                continue
            value = str(row[simple_main_column])
            if (not value) or (value == "None"):
                continue
            bone_main.append(value)

        for row in csv_data[1:]:
            if len(row) <= simple_save_column:
                continue
            value = str(row[simple_save_column])
            if (not value) or (value == "None"):
                continue
            bone_save.append(value)

        for row in csv_data[1:]:
            if len(row) <= max(simple_toactive_column, simple_active_column):
                continue
            key = str(row[simple_toactive_column])
            value = str(row[simple_active_column])
            if (not key) or (key == "None"):
                continue
            bone_mapping[key] = value

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = SourceArmature
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.reveal() # 全部取消隐藏

        # 创建主骨骼集合
        bpy.ops.pose.select_all(action='DESELECT')
        for bone_name in bone_main:
            bone = SourceArmature.pose.bones.get(bone_name)
            if bone:
                bone.bone.select = True
        
        main_collection = SourceArmature.data.collections.get("主骨骼")
        if not main_collection:
            main_collection = SourceArmature.data.collections.new("主骨骼")
        
        for bone in SourceArmature.data.bones:
            if bone.select:
                main_collection.assign(bone)
                bone.color.palette = 'THEME02'

        # 创建保留骨骼集合
        bpy.ops.pose.select_all(action='DESELECT')
        for bone_name in bone_save:
            bone = SourceArmature.pose.bones.get(bone_name)
            if bone:
                bone.bone.select = True

        save_collection = SourceArmature.data.collections.get("保留骨骼")
        if not save_collection:
            save_collection = SourceArmature.data.collections.new("保留骨骼")
        
        for bone in SourceArmature.data.bones:
            if bone.select:
                save_collection.assign(bone)
                bone.color.palette = 'THEME09'

        bpy.ops.pose.select_all(action='DESELECT')
        # 执行特定合并
        for simple_toactive_name, simple_active_name in bone_mapping.items():
            if simple_active_name == "":
                continue
            SourceArmature.data.bones.active = SourceArmature.data.bones[simple_active_name]
            bpy.ops.xbone.merge_to_active()

        # 剩余合并至父级
        bpy.ops.pose.select_all(action='DESELECT')
        for bone in bone_main:
            bpy.ops.object.select_pattern(pattern=bone)
        for bone in bone_save:
            bpy.ops.object.select_pattern(pattern=bone)
        bpy.ops.pose.select_all(action='INVERT') # 反选
        bpy.ops.xbone.merge_to_parent()
        #删除剩余骨骼
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.delete()
        bpy.ops.object.mode_set(mode='POSE')
        #全选并取消约束
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.constraints_clear()

        return {'FINISHED'}
        

class O_BonePosMapping(bpy.types.Operator):
    bl_idname = "xbone.pos_mapping"
    bl_label = "复制位置"
    bl_description = "将源骨骼按csv对应, 添加复制位置约束并应用约束、骨架、姿态"

    def execute(self, context):
        if context.scene.xbone_csv_data == "":
            self.report({'ERROR'}, "似乎没有导入csv")
            return {'FINISHED'}
        try:
            SourceArmature = bpy.data.objects.get(context.scene.source_armature.name)
            TargetArmature = bpy.data.objects.get(context.scene.target_armature.name)
        except:
            self.report({'ERROR'}, "似乎没有选择对象") 
            return {'FINISHED'}
        
        csv_data = json.loads(context.scene["xbone_csv_data"])
        key_column = context.scene.key_column
        value_column = context.scene.value_column
        bone_mapping = {}
        # 读取CSV数据
        for row in csv_data[1:]:  # 跳过标题行
            if len(row) <= max(key_column, value_column):
                continue  # 确保行有足够的列
            key = str(row[key_column])
            value = str(row[value_column])
            if (key == "None") or (value == "None"):
                continue
            bone_mapping[key] = value

        # 遍历源骨骼名称映射
        for source_bone_name, target_bone_name in bone_mapping.items():
            # 获取源骨骼和目标骨骼
            source_bone = SourceArmature.pose.bones.get(source_bone_name)
            target_bone = TargetArmature.pose.bones.get(target_bone_name)
            
            # 检查是否找到了源骨骼和目标骨骼
            if source_bone and target_bone:
                # 为源骨骼添加“复制位置”约束
                constraint = source_bone.constraints.new('COPY_LOCATION')
                constraint.target = TargetArmature
                constraint.subtarget = target_bone_name

        # 应用约束
        bpy.context.view_layer.objects.active = SourceArmature
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        for bone in SourceArmature.pose.bones:
            SourceArmature.data.bones.active = SourceArmature.data.bones[bone.name]
            # 遍历并应用骨骼上的约束
            for constraint in SourceArmature.pose.bones[bone.name].constraints:
                if constraint.type == "COPY_LOCATION":
                    bpy.ops.constraint.apply(constraint=constraint.name, owner='BONE')
        # 调用，应用骨架和姿态
        bpy.ops.xbone.pose_apply()
        bpy.ops.object.mode_set(mode='OBJECT')     

        return {'FINISHED'}


class O_BoneRenameMapping(bpy.types.Operator):
    bl_idname = "xbone.rename_mapping"
    bl_label = "重命名换绑"
    bl_description = "将源骨架骨骼按csv对应, 重命名至目标骨架并绑定"

    
    def execute(self, context):
        if context.scene.xbone_csv_data == "":
            self.report({'ERROR'}, "似乎没有导入csv")
            return {'FINISHED'}
        try:
            SourceMesh = bpy.data.objects.get(context.scene.rename_source_mesh.name)
            SourceArmature = bpy.data.objects.get(context.scene.rename_source_armature.name)
            TargetArmature = bpy.data.objects.get(context.scene.rename_target_armature.name)
        except:
            self.report({'ERROR'}, "似乎没有选择对象") 
            return {'FINISHED'}
        
        csv_data = json.loads(context.scene["xbone_csv_data"])
        rename_key_column = context.scene.rename_key_column
        rename_value_column = context.scene.rename_value_column
        rename_save_column = context.scene.rename_save_column
        rename_target_save_column = context.scene.rename_target_save_column
        bone_mapping = {}
        bone_save = []
        bone_save_parent = {}
        bone_target_save = []
        # 读取CSV文件中的数据
        for row in csv_data[1:]:  # 跳过标题行
            # 第一部分映射
            if len(row) > max(rename_key_column, rename_value_column):
                key = str(row[rename_key_column])
                value = str(row[rename_value_column])
                if (key == "None") or (value == "None"):
                    continue
                bone_mapping[key] = value

            # 第二部分保存列表
            if len(row) > rename_save_column:
                value = str(row[rename_save_column])
                if (not value) or (value == "None"):
                    continue
                bone_save.append(value)

            # 第三部分目标保存列表
            if len(row) > rename_target_save_column:
                value = str(row[rename_target_save_column])
                if (not value) or (value == "None"):
                    continue
                bone_target_save.append(value)
            
        # 应用两个骨架姿态
        bpy.context.view_layer.objects.active = SourceArmature
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.xbone.pose_apply()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = TargetArmature
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.xbone.pose_apply()

        # 姿态模式重命名
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = SourceArmature
        bpy.ops.object.mode_set(mode='POSE')
        for source_bone_name, target_bone_name in bone_mapping.items():
            #SourceArmature.data.bones.active = SourceArmature.data.bones[source_bone_name]
            #bpy.context.active_bone.name = target_bone_name
            try:
                SourceArmature.data.bones[source_bone_name].name = target_bone_name
            except:
                print(f"{source_bone_name}不存在")

        # 保留骨骼的父级记录
        for bone in bone_save:
            SourceArmature.data.bones.active = SourceArmature.data.bones[bone]
            bpy.ops.pose.select_hierarchy(direction='PARENT', extend=True)
            for bone_exist in bone_save:
                if context.active_pose_bone.name == bone_exist:
                    break
            else: # 遍历正常完成的最后执行
                key = bone
                value = context.active_pose_bone.name
                bone_save_parent[key] = value

        # 应用原骨架
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = SourceMesh
        for now_modifier in SourceMesh.modifiers:
            if now_modifier.type == 'ARMATURE':
                bpy.ops.object.modifier_apply(modifier=now_modifier.name) #应用
        # 取消父级保持变换结果
        bpy.ops.object.select_all(action='DESELECT')
        SourceArmature.select_set(True)
        SourceMesh.select_set(True)
        bpy.context.view_layer.objects.active = SourceArmature
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

               
        # 添加骨架修改器
        now_modifier = SourceMesh.modifiers.new(name=TargetArmature.name, type='ARMATURE')
        now_modifier.object = TargetArmature

        # 清理原骨架
        bpy.context.view_layer.objects.active = SourceArmature
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')
        for bone in bone_save:
            bpy.ops.object.select_pattern(pattern=bone)
        bpy.ops.armature.select_all(action='INVERT') # 反选
        bpy.ops.armature.delete()

       # 骨架合并
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        SourceArmature.select_set(True) #bpy.ops.object.select_pattern(pattern=SourceArmature.name)
        TargetArmature.select_set(True) #bpy.ops.object.select_pattern(pattern=TargetArmature.name)
        bpy.context.view_layer.objects.active = TargetArmature
        bpy.ops.object.join()
        # 指定父级
        bpy.ops.object.select_all(action='DESELECT')
        SourceMesh.select_set(True)
        TargetArmature.select_set(True)
        bpy.context.view_layer.objects.active = TargetArmature
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True) 

        # 保留骨骼重新指定父级
        bpy.context.view_layer.objects.active = TargetArmature
        bpy.ops.object.mode_set(mode='EDIT')
        print(bone_save_parent)
        for bone_save_name, bone_parent_name in bone_save_parent.items():
            bpy.ops.armature.select_all(action='DESELECT') #取消选择
            bpy.ops.object.select_pattern(pattern=bone_save_name) #选择
            bpy.ops.object.select_pattern(pattern=bone_parent_name) #选择
            # 指定活动骨,取消相连项
            TargetArmature.data.edit_bones.active = TargetArmature.data.edit_bones[bone_save_name]
            context.active_bone.use_connect = False
            # 指定活动骨,创建父级
            TargetArmature.data.edit_bones.active = TargetArmature.data.edit_bones[bone_parent_name]
            bpy.ops.armature.parent_set(type='OFFSET')

        # 主骨骼集合
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')  # 取消选择
        for source_bone_name, target_bone_name in bone_mapping.items():
            bone = TargetArmature.pose.bones.get(target_bone_name)
            if bone:
                bone.bone.select = True
        # 创建或获取主骨骼集合（无需手动 append）
        main_collection = TargetArmature.data.collections.get("主骨骼")
        if not main_collection:
            main_collection = TargetArmature.data.collections.new("主骨骼")  # 自动添加到骨架
        # 添加骨骼到集合并设置颜色
        for bone in TargetArmature.data.bones:
            if bone.select:
                main_collection.assign(bone)
                bone.color.palette = 'THEME02'
        
        # 源保留骨骼集合
        bpy.ops.pose.select_all(action='DESELECT')
        for bone_name in bone_save:
            bone = TargetArmature.pose.bones.get(bone_name)
            if bone:
                bone.bone.select = True
        # 创建或获取源保留骨骼集合
        source_collection = TargetArmature.data.collections.get("源保留骨骼")
        if not source_collection:
            source_collection = TargetArmature.data.collections.new("源保留骨骼")  # 自动添加
        # 添加骨骼到集合并设置颜色
        for bone in TargetArmature.data.bones:
            if bone.select:
                source_collection.assign(bone)
                bone.color.palette = 'THEME09'
        
        # 目标保留骨骼集合
        bpy.ops.pose.select_all(action='DESELECT')
        for bone_name in bone_target_save:
            bone = TargetArmature.pose.bones.get(bone_name)
            if bone:
                bone.bone.select = True
        # 创建或获取目标保留骨骼集合
        target_collection = TargetArmature.data.collections.get("目标保留骨骼")
        if not target_collection:
            target_collection = TargetArmature.data.collections.new("目标保留骨骼")  # 自动添加
        # 添加骨骼到集合并设置颜色
        for bone in TargetArmature.data.bones:
            if bone.select:
                target_collection.assign(bone)
                bone.color.palette = 'THEME07'
        
        # 其余骨骼集合
        bpy.ops.pose.select_all(action='DESELECT')
        # 先选择所有已分类的骨骼
        for coll in [main_collection, source_collection, target_collection]:
            for bone in coll.bones:
                bone.select = True
        # 反选得到未分类的骨骼
        bpy.ops.pose.select_all(action='INVERT')
        # 创建或获取其余骨骼集合
        other_collection = TargetArmature.data.collections.get("其余骨骼")
        if not other_collection:
            other_collection = TargetArmature.data.collections.new("其余骨骼")  # 自动添加
        # 添加骨骼到集合并设置颜色
        for bone in TargetArmature.data.bones:
            if bone.select:
                other_collection.assign(bone)
                bone.color.palette = 'THEME03'
        
        return {'FINISHED'}
    
class O_only_BoneRenameMapping(bpy.types.Operator):
    bl_idname = "xbone.only_rename_mapping"
    bl_label = "仅重命名"
    bl_description = "将源骨架骨骼按csv对应, 重命名"

    def execute(self, context):
        if context.scene.xbone_csv_data == "":
            self.report({'ERROR'}, "似乎没有导入csv")
            return {'FINISHED'}
        try:
            TargetArmature = bpy.data.objects.get(context.scene.rename_armature.name)
        except:
            self.report({'ERROR'}, "似乎没有选择对象") 
            return {'FINISHED'}
        
        csv_data = json.loads(context.scene["xbone_csv_data"])
        current_skel_column = context.scene.current_skel_column
        change_skel_column = context.scene.change_skel_column
        bone_mapping = {}
        # 读取CSV文件中的数据
        for row in csv_data[1:]:  # 跳过标题行
            if len(row) <= max(current_skel_column, change_skel_column):
                continue  # 确保行有足够的列
            key = str(row[current_skel_column])
            value = str(row[change_skel_column])
            if (key == "None") or (value == "None"):
                continue
            O_only_BoneRenameMapping.bone_mapping[key] = value

        # 姿态模式重命名
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = TargetArmature
        bpy.ops.object.mode_set(mode='POSE')
        for current_bone_name, change_bone_name in bone_mapping.items():
            try:
                TargetArmature.data.bones[current_bone_name].name = change_bone_name
            except:
                print(f"{current_bone_name}不存在")

        return {'FINISHED'}

class P_BoneMapping(bpy.types.Panel):
    bl_label = "MOD骨架替换"
    bl_idname = "X_PT_BoneMapping"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'XBone'
    bl_options = {'DEFAULT_CLOSED'} #默认折叠

    @classmethod
    def poll(cls, context):
        # 只有当主面板激活了此子面板时才显示
        return getattr(context.scene, 'active_xbone_subpanel', '') == 'BoneTools'
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.operator(O_ImportCSV.bl_idname, icon="IMPORT")
        # 选择骨架
        box.prop(context.scene, "simple_source_armature", text="目标骨架", icon="ARMATURE_DATA")
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(context.scene, "simple_main_column")
        row.prop(context.scene, "simple_save_column")
        row = col.row(align=True)
        row.prop(context.scene, "simple_toactive_column")
        row.prop(context.scene, "simple_active_column")
        # 添加按钮
        col.operator(O_BoneSimpleMapping.bl_idname, icon="PLAY")


        box = layout.box()
        # 选择源骨架
        col = box.column(align=True)
        col.prop(context.scene, "source_armature", text="源骨架", icon="ARMATURE_DATA")
        # 选择目标骨架
        col.prop(context.scene, "target_armature", text="目标骨架", icon="ARMATURE_DATA")
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(context.scene, "key_column")
        row.prop(context.scene, "value_column")
        # 添加按钮
        col.operator(O_BonePosMapping.bl_idname, icon="PLAY")
        

        box = layout.box()
        # 选择源物体、源骨架
        col = box.column(align=True)
        col.prop(context.scene, "rename_source_mesh", text="源物体", icon="MESH_DATA")
        col.prop(context.scene, "rename_source_armature", text="源骨架", icon="ARMATURE_DATA")
        # 选择目标骨架
        col = box.column(align=True)
        col.prop(context.scene, "rename_target_armature", text="目标骨架", icon="ARMATURE_DATA")
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(context.scene, "rename_key_column")
        row.prop(context.scene, "rename_value_column")
        row = col.row(align=True)
        row.prop(context.scene, "rename_save_column")
        row.prop(context.scene, "rename_target_save_column")
        # 添加按钮
        col.operator(O_BoneRenameMapping.bl_idname, icon="PLAY")


        box = layout.box()
        # 批量重命名 选择目标骨架
        col = box.column(align=True)
        col.prop(context.scene, "rename_armature", text="目标骨架", icon="ARMATURE_DATA")
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(context.scene, "current_skel_column")
        row.prop(context.scene, "change_skel_column")
        # 添加按钮
        col.operator(O_only_BoneRenameMapping.bl_idname, icon="PLAY")

        



def register():
    bpy.utils.register_class(O_ImportCSV)
    bpy.utils.register_class(O_BoneSimpleMapping)
    bpy.utils.register_class(O_BonePosMapping)
    bpy.utils.register_class(O_BoneRenameMapping)
    bpy.utils.register_class(O_only_BoneRenameMapping)
    bpy.utils.register_class(P_BoneMapping)
    ########################## Divider ##########################
    bpy.types.Scene.xbone_csv_data = bpy.props.StringProperty(
        name="CSV Data",
        description="Stores imported CSV data as JSON",
        default=""
    )

    bpy.types.Scene.simple_source_armature = bpy.props.PointerProperty(
        description="选择将被作用的骨架",
        type=bpy.types.Object, 
        poll=ObjType.is_armature
        )
    bpy.types.Scene.source_armature = bpy.props.PointerProperty(
        description="选择将被作用的骨架",
        type=bpy.types.Object, 
        poll=ObjType.is_armature
        )
    bpy.types.Scene.target_armature = bpy.props.PointerProperty(
        description="选择一个骨架作为数据目标",
        type=bpy.types.Object, 
        poll=ObjType.is_armature
        )
    bpy.types.Scene.rename_source_mesh = bpy.props.PointerProperty(
        description="选择将被作用的网格",
        type=bpy.types.Object, 
        poll=ObjType.is_mesh
        )
    bpy.types.Scene.rename_source_armature = bpy.props.PointerProperty(
        description="选择将被作用的骨架",
        type=bpy.types.Object, 
        poll=ObjType.is_armature
        )
    bpy.types.Scene.rename_target_armature = bpy.props.PointerProperty(
        description="选择一个骨架作为数据目标",
        type=bpy.types.Object, 
        poll=ObjType.is_armature
        )
    bpy.types.Scene.rename_armature = bpy.props.PointerProperty(
        description="选择将被作用的骨架",
        type=bpy.types.Object, 
        poll=ObjType.is_armature
        )
    ########################## Divider ##########################
    bpy.types.Scene.simple_main_column = bpy.props.IntProperty(
        name="主骨骼",
        description="主要骨骼的列索引\n0是第1列",
        default=1,
        min=0,
    )
    bpy.types.Scene.simple_save_column = bpy.props.IntProperty(
        name="保留骨",
        description="可以后续调整物理的骨骼列索引\n0是第1列",
        default=2,
        min=0,
    )
    bpy.types.Scene.simple_toactive_column = bpy.props.IntProperty(
        name="被合并骨",
        description="会被合并至父级的骨骼\n0是第1列",
        default=3,
        min=0,
    )
    bpy.types.Scene.simple_active_column = bpy.props.IntProperty(
        name="活动骨",
        description="不用填，这功能我没写\n0是第1列",
        default=4,
        min=0,
    )
    ########################## Divider ##########################
    bpy.types.Scene.key_column = bpy.props.IntProperty(
        name="源骨架",
        description="源骨架将复制目标骨架位置\n0是第1列",
        default=0,
        min=0,
    )
    bpy.types.Scene.value_column = bpy.props.IntProperty(
        name="目标骨架",
        description="源骨架将复制目标骨架位置\n0是第1列",
        default=1,
        min=0,
    )
    ########################## Divider ##########################
    bpy.types.Scene.rename_key_column = bpy.props.IntProperty(
        name="源骨架",
        description="源骨架将重命名为目标骨架名称\n0是第1列",
        default=1,
        min=0,
    )
    bpy.types.Scene.rename_value_column = bpy.props.IntProperty(
        name="目标骨架",
        description="源骨架将重命名为目标骨架名称\n0是第1列",
        default=0,
        min=0,
    )
    bpy.types.Scene.rename_save_column = bpy.props.IntProperty(
        name="源保留骨",
        description="可以后续调整物理的骨骼\n0是第1列",
        default=2,
        min=0,
    )
    bpy.types.Scene.rename_target_save_column = bpy.props.IntProperty(
        name="目标保留骨",
        description="比如左右手后背的武器骨\n0是第1列",
        default=5,
        min=0,
    )
    ########################## Divider ##########################
    bpy.types.Scene.current_skel_column = bpy.props.IntProperty(
        name="源名称",
        description="源名称改为目标名称\n0是第1列",
        default=1,
        min=0,
    )
    bpy.types.Scene.change_skel_column = bpy.props.IntProperty(
        name="目标名称",
        description="源名称改为目标名称\n0是第1列",
        default=0,
        min=0,
    )    

def unregister():
    bpy.utils.unregister_class(O_ImportCSV)
    bpy.utils.unregister_class(O_BoneSimpleMapping)
    bpy.utils.unregister_class(O_BonePosMapping)
    bpy.utils.unregister_class(O_BoneRenameMapping)
    bpy.utils.unregister_class(O_only_BoneRenameMapping)    
    bpy.utils.unregister_class(P_BoneMapping)

    del bpy.types.Scene.xbone_csv_data

    del bpy.types.Scene.simple_source_armature
    del bpy.types.Scene.source_armature
    del bpy.types.Scene.target_armature
    del bpy.types.Scene.rename_source_mesh
    del bpy.types.Scene.rename_source_armature
    del bpy.types.Scene.rename_target_armature
    del bpy.types.Scene.rename_armature
    

    del bpy.types.Scene.simple_main_column
    del bpy.types.Scene.simple_save_column
    del bpy.types.Scene.simple_toactive_column
    del bpy.types.Scene.simple_active_column

    del bpy.types.Scene.key_column
    del bpy.types.Scene.value_column
    del bpy.types.Scene.rename_key_column
    del bpy.types.Scene.rename_value_column
    del bpy.types.Scene.rename_save_column
    del bpy.types.Scene.rename_target_save_column
    del bpy.types.Scene.current_skel_column
    del bpy.types.Scene.change_skel_column

