# type: ignore
import bpy
import math
from mathutils import Euler, Matrix, Vector, Quaternion
import os 
import csv
from bpy_extras.io_utils import ImportHelper

########################## Divider ##########################

class PG_BonePoseWorldProps(bpy.types.PropertyGroup):
    #注册切换矩阵显示的布尔值
    pose_matrix: bpy.props.BoolProperty(
        name="矩阵", 
        default=False
    )

    # 新增：用于控制移动操作的轴向开关
    move_x: bpy.props.BoolProperty(
        name="X轴", 
        default=True,
        description="启用X轴方向的移动"
    )
    move_y: bpy.props.BoolProperty(
        name="Y轴", 
        default=True,
        description="启用Y轴方向的移动"
    )
    move_z: bpy.props.BoolProperty(
        name="Z轴", 
        default=True,
        description="启用Z轴方向的移动"
    )

    apply_constraint: bpy.props.BoolProperty(
        name="应用约束",
        default=True,
        description="启用时将应用约束，禁用时只添加约束但不应用（如果骨骼轴向不对，局部Y轴不理想）"
    )

    rotate_mode: bpy.props.EnumProperty(
        name="旋转模式",
        description="选择旋转父级骨骼的轴向",
        items=[
            ('X_AXIS', "X", "绕世界坐标系X轴"),
            ('Y_AXIS', "Y", "绕世界坐标系Y轴"),
            ('Z_AXIS', "Z", "绕世界坐标系Z轴"),
        ],
        default='Y_AXIS',
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


class O_BonePoseYUp(bpy.types.Operator):
    bl_idname = "xbone.pose_y_up"
    bl_label = "90 0 0"
    bl_description = "选中骨骼Y轴向上右手坐标系, 请先应用骨架旋转"

    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'ARMATURE':
            if context.selected_pose_bones:
                order_selected_pose_bones = []
                for bone1 in obj.pose.bones:
                    for bone2 in context.selected_pose_bones:
                        if bone1 == bone2:
                            order_selected_pose_bones.append(bone1)

                for bone in order_selected_pose_bones:
                    # 获取原始缩放
                    original_scale = bone.matrix.to_scale()
                    
                    # 创建新旋转
                    new_rotation = Euler((math.radians(90), math.radians(0), math.radians(0)), 'XYZ')
                    new_matrix = new_rotation.to_matrix().to_4x4()
                    
                    # 应用原始缩放
                    new_matrix @= Matrix.Scale(original_scale[0], 4, (1, 0, 0))
                    new_matrix @= Matrix.Scale(original_scale[1], 4, (0, 1, 0))
                    new_matrix @= Matrix.Scale(original_scale[2], 4, (0, 0, 1))
                    
                    # 保持原始位置
                    new_matrix.translation = bone.matrix.translation
                    
                    bone.matrix = new_matrix
                    bpy.context.view_layer.update()

        return {"FINISHED"}
    
class O_BonePoseZUp(bpy.types.Operator):
    bl_idname = "xbone.pose_z_up"
    bl_label = "0 0 0"
    bl_description = "选中骨骼Z轴向上右手坐标系, 请先应用骨架旋转"

    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'ARMATURE':
            if context.selected_pose_bones:
                order_selected_pose_bones = []
                for bone1 in obj.pose.bones:
                    for bone2 in context.selected_pose_bones:
                        if bone1 == bone2:
                            order_selected_pose_bones.append(bone1)

                for bone in order_selected_pose_bones:
                    # 获取原始缩放
                    original_scale = bone.matrix.to_scale()
                    
                    # 创建新旋转
                    new_rotation = Euler((math.radians(0), math.radians(0), math.radians(0)), 'XYZ')
                    new_matrix = new_rotation.to_matrix().to_4x4()
                    
                    # 应用原始缩放
                    new_matrix @= Matrix.Scale(original_scale[0], 4, (1, 0, 0))
                    new_matrix @= Matrix.Scale(original_scale[1], 4, (0, 1, 0))
                    new_matrix @= Matrix.Scale(original_scale[2], 4, (0, 0, 1))
                    
                    # 保持原始位置
                    new_matrix.translation = bone.matrix.translation
                    
                    bone.matrix = new_matrix
                    bpy.context.view_layer.update()

        return {"FINISHED"}

class O_BonePoseUpRight(bpy.types.Operator):
    bl_idname = "xbone.pose_upright"
    bl_label = "自动摆正"
    bl_description = "选择当前朝向相近的正交方向 by 夜曲"

    def execute(self, context):
        target_angles = [-180, -90, 0, 90, 180]
        obj = context.active_object
        if obj and obj.type == 'ARMATURE':
            if context.selected_pose_bones:
                order_selected_pose_bones = []
                for bone1 in obj.pose.bones:
                    for bone2 in context.selected_pose_bones:
                        if bone1 == bone2:
                            order_selected_pose_bones.append(bone1)

                for bone in order_selected_pose_bones:
                    # 获取原始缩放
                    original_scale = bone.matrix.to_scale()
                    
                    # 计算新旋转
                    angles_radians = bone.matrix.to_euler()
                    angles_degrees = (math.degrees(angles_radians.x), math.degrees(angles_radians.y), math.degrees(angles_radians.z))
                    x, y, z = angles_degrees
                    x = min(target_angles, key=lambda n: abs(n - x))
                    y = min(target_angles, key=lambda n: abs(n - y))
                    z = min(target_angles, key=lambda n: abs(n - z))
                    
                    new_rotation = Euler((math.radians(x), math.radians(y), math.radians(z)), 'XYZ')
                    new_matrix = new_rotation.to_matrix().to_4x4()
                    
                    # 应用原始缩放
                    new_matrix @= Matrix.Scale(original_scale[0], 4, (1, 0, 0))
                    new_matrix @= Matrix.Scale(original_scale[1], 4, (0, 1, 0))
                    new_matrix @= Matrix.Scale(original_scale[2], 4, (0, 0, 1))
                    
                    # 保持原始位置
                    new_matrix.translation = bone.matrix.translation
                    
                    bone.matrix = new_matrix
                    bpy.context.view_layer.update()

        return {"FINISHED"}

class O_BonePoseX90(bpy.types.Operator):
    bl_idname = "xbone.pose_x90"
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
    bl_idname = "xbone.pose_y90"
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
    bl_idname = "xbone.pose_z90"
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
    bl_idname = "xbone.pose_apply"
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
            bpy.ops.object.shape_key_add(from_mix=False) # 创建一个形态键，避免下一句bug
            bpy.ops.object.shape_key_remove(all=True) # 删除所有的形态键
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

class O_SwapPoseRest(bpy.types.Operator):
    """交换所选骨骼的姿态位置和静置位置"""
    bl_idname = "xbone.swap_pose_and_rest"
    bl_label = "交换姿态和静置"
    bl_description = "将当前姿态与静置位置交换\n如果已经在静置位置，就变成静置和静置交换了\n不选中为全选"
    bl_options = {'REGISTER', 'UNDO'}  # 注册操作并支持撤销
    
    @classmethod
    def poll(cls, context):
        """检查是否满足操作条件"""
        # 必须有一个选中的物体，且是骨架类型，并且当前处于姿态模式
        return (context.object and 
                context.object.type == 'ARMATURE' and 
                context.object.mode == 'POSE')
    
    def execute(self, context):
        """执行交换操作"""
        # 获取当前选中的骨架对象
        armature = context.object
        # 获取选中的姿态骨骼，如果没有选中则使用所有姿态骨骼
        pose_bones = context.selected_pose_bones or armature.pose.bones
        
        # 存储原始变换数据
        original_transforms = {}
        for bone in pose_bones:
            # 保存每个骨骼的矩阵和基础矩阵
            original_transforms[bone.name] = {
                'matrix': bone.matrix.copy(),          # 骨骼的全局变换矩阵
                'matrix_basis': bone.matrix_basis.copy()  # 骨骼的局部变换矩阵
            }
        
        # 切换到编辑模式以修改静置位置
        bpy.ops.object.mode_set(mode='EDIT')
        # 获取编辑模式下的骨骼数据
        edit_bones = armature.data.edit_bones
        
        # 遍历所有需要处理的骨骼
        for bone_name, transforms in original_transforms.items():
            edit_bone = edit_bones.get(bone_name)
            if edit_bone:
                # 保存原始的静置位置数据
                original_matrix = edit_bone.matrix.copy()  # 骨骼变换矩阵
                
                # 将静置位置设置为当前姿态位置
                pose_matrix = transforms['matrix']
                edit_bone.matrix = pose_matrix
                
                # 切换回姿态模式设置新的姿态
                bpy.ops.object.mode_set(mode='POSE')
                
                # 将姿态设置为原始的静置位置
                pose_bone = armature.pose.bones[bone_name]
                pose_bone.matrix = original_matrix
                
                # 切换回编辑模式处理下一个骨骼
                bpy.ops.object.mode_set(mode='EDIT')
        
        # 完成后返回姿态模式
        bpy.ops.object.mode_set(mode='POSE')
        
        # 报告操作结果
        self.report({'INFO'}, f"已交换{len(pose_bones)}根骨骼的姿态和静置位置")
        return {'FINISHED'}
    

class O_InCSVSel(bpy.types.Operator, ImportHelper):
    bl_idname = "xbone.csv_bone_sel"
    bl_label = "导入CSV并选择骨骼"
    bl_description = "导入时右上角选择编码格式"
    filename_ext = ".csv"
    filter_glob: bpy.props.StringProperty(
        default="*.csv",
        options={'HIDDEN'},
    )

    # 添加编码选择属性
    encoding: bpy.props.EnumProperty(
        name="文件编码",
        description="选择CSV文件的编码格式",
        items=[
            ('utf-8', "UTF-8", "标准UTF-8编码"),
            ('gbk', "GBK", "简体中文编码"),
        ],
        default='utf-8',
    )

    def execute(self, context):
        csv_file = self.filepath
        bone_sel_col = context.scene.bone_sel_col  # CSV从0开始数列
        bone_sel = []

        if not csv_file or not os.path.exists(csv_file):
            self.report({'ERROR'}, "请选择有效的CSV文件")
            return {'CANCELLED'}

        try:
            # 读取CSV文件
            with open(csv_file, 'r', newline='', encoding=self.encoding) as file:
                reader = csv.reader(file)
                # 跳过标题行，从第二行开始读取数据
                next(reader)  # 跳过第一行
                
                for row in reader:
                    if len(row) <= bone_sel_col:
                        continue  # 跳过列数不足的行
                    value = str(row[bone_sel_col]).strip()
                    if not value or value == "None":
                        continue
                    bone_sel.append(value)

        except UnicodeDecodeError:
            self.report({'ERROR'}, f"无法用{self.encoding}解码文件，请尝试其他编码")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"导入CSV文件时出现错误: {e}")
            return {'CANCELLED'}
        
        # 选择骨骼
        bpy.ops.pose.select_all(action='DESELECT')
        selected_count = 0
        for bone_name in bone_sel:
            # 使用更可靠的选择方式
            if bone_name in context.active_object.pose.bones:
                context.active_object.pose.bones[bone_name].bone.select = True
                selected_count += 1

        self.report({'INFO'}, f"已选择 {selected_count}/{len(bone_sel)} 个骨骼")
        return {'FINISHED'}

class O_BonePosePrint(bpy.types.Operator):
    bl_idname = "xbone.pose_print"
    bl_label = ""
    bl_description = "打印并复制选择的骨骼名称到剪贴板"
    
    def execute(self, context):
        selected_bones = context.selected_pose_bones
        if not selected_bones:
            self.report({'WARNING'}, "没有选择任何骨骼")
            return {"CANCELLED"}
        
        # 收集所有骨骼名称
        bone_names = [bone.name for bone in selected_bones]
        output_text = "\n".join(bone_names)
        
        # 打印到控制台
        print("选择的骨骼名称:")
        print(output_text)
        
        # 复制到Blender剪贴板
        try:
            context.window_manager.clipboard = output_text
            self.report({'INFO'}, f"已复制 {len(bone_names)} 个骨骼名称到剪贴板")
        except Exception as e:
            self.report({'ERROR'}, f"复制到剪贴板失败: {str(e)}")
            return {"CANCELLED"}
        
        return {"FINISHED"}

class O_BonePoseMoveToActive(bpy.types.Operator):
    '''
    骨骼移动工具代码说明
    1. 多骨架骨骼处理
    - **问题识别**：选中的骨骼可能来自不同的骨架对象
    - **解决方案**
    - 通过 `pose_bone.id_data` 获取每个骨骼所属的骨架对象
    - 为每个骨骼使用其所属骨架的正确变换矩阵计算世界坐标
    - 分别处理每个骨架中的骨骼移动操作
    2. 世界坐标直接移动获得骨骼的世界坐标后，直接使用 `bpy.ops.transform.translate` API 进行移动
    '''
    bl_idname = "xbone.pose_move_to_active"
    bl_label = "移动到活动骨骼"
    bl_description = "将选中的骨骼移动到活动骨骼的位置（支持多骨架）"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        """检查是否满足操作条件"""
        return (context.object and 
                context.object.type == 'ARMATURE' and 
                context.object.mode == 'POSE' and
                len(context.selected_pose_bones) >= 2 and
                context.active_pose_bone)
    
    def execute(self, context):
        # 获取控制轴向移动的布尔属性
        props = context.scene.bone_pose_world_props
        move_x = props.move_x
        move_y = props.move_y
        move_z = props.move_z
        
        if not (move_x or move_y or move_z):
            self.report({'WARNING'}, "X, Y, Z 轴分量至少要选择一个才能移动")
            return {'CANCELLED'}
        
        # 获取当前选中的姿态骨骼
        selected_pose_bones = context.selected_pose_bones
        
        # 获取活动骨骼
        active_pose_bone = context.active_pose_bone
        
        # 获取活动骨骼所属的骨架对象
        active_armature_obj = active_pose_bone.id_data
        active_armature_matrix = active_armature_obj.matrix_world
        active_bone_matrix_world = active_armature_matrix @ active_pose_bone.matrix
        active_bone_location_world = active_bone_matrix_world.translation
        
        # 记录当前的活动对象和选择状态
        original_active_object = context.view_layer.objects.active
        original_selected_objects = context.selected_objects.copy()
        
        moved_count = 0
        
        # 遍历所有选中的骨骼
        for pose_bone in selected_pose_bones:
            if pose_bone == active_pose_bone:
                continue  # 跳过活动骨骼本身
            
            # 获取当前骨骼所属的骨架对象
            bone_armature_obj = pose_bone.id_data
            
            # 获取当前骨骼的世界坐标位置
            bone_armature_matrix = bone_armature_obj.matrix_world
            bone_matrix_world = bone_armature_matrix @ pose_bone.matrix
            bone_location_world = bone_matrix_world.translation
            
            # 计算需要移动的完整向量（在世界坐标系中）
            move_vector_full_world = active_bone_location_world - bone_location_world
            
            # 根据轴向开关过滤移动向量
            move_vector_filtered_world = Vector((
                move_vector_full_world.x if move_x else 0.0,
                move_vector_full_world.y if move_y else 0.0,
                move_vector_full_world.z if move_z else 0.0
            ))
            
            # 如果过滤后的向量是零向量，则跳过移动
            if move_vector_filtered_world.length_squared < 1e-6:
                continue
            
            # 设置当前骨骼的骨架为活动对象
            context.view_layer.objects.active = bone_armature_obj
            
            # 取消所有骨骼的选择
            bpy.ops.pose.select_all(action='DESELECT')
            
            # 选择当前骨骼
            pose_bone.bone.select = True
            
            # 使用bpy.ops.transform.translate移动骨骼
            # 设置变换方向为全局坐标系
            context.scene.tool_settings.transform_pivot_point = 'ACTIVE_ELEMENT'
            context.scene.tool_settings.use_transform_data_origin = False
            
            # 执行移动操作
            bpy.ops.transform.translate(
                value=move_vector_filtered_world,
                orient_type='GLOBAL',
                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                orient_matrix_type='GLOBAL',
                constraint_axis=(False, False, False),
                mirror=False,
                use_proportional_edit=False
            )
            
            moved_count += 1
        
        # 恢复原始的活动对象和选择状态
        context.view_layer.objects.active = original_active_object
        for obj in context.selected_objects:
            obj.select_set(False)
        for obj in original_selected_objects:
            obj.select_set(True)
        
        # 重新选择原始的姿态骨骼
        bpy.ops.pose.select_all(action='DESELECT')
        for pose_bone in selected_pose_bones:
            pose_bone.bone.select = True
        active_pose_bone.bone.select = True
        
        # 更新场景
        context.view_layer.update()
        
        self.report({'INFO'}, f"已移动 {moved_count} 个骨骼到活动骨骼位置（X:{move_x}, Y:{move_y}, Z:{move_z}）")
        return {'FINISHED'}
    

class O_BonePoseRotateToActive(bpy.types.Operator):
    """
    旋转选中骨骼的父级，使选中骨骼指向活动骨骼。
    选中骨骼A，活动骨骼B，父级P。
    """
    bl_idname = "xbone.pose_rotate_to_active"
    bl_label = "父级转向活动骨骼"
    bl_description = "旋转选中骨骼(A)的父级(P)，使A指向活动骨骼(B)的位置"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        """检查是否满足操作条件：姿态模式，选中骨骼（A），活动骨骼（B），且A有父级（P）"""
        if not (context.object and 
                context.object.type == 'ARMATURE' and 
                context.object.mode == 'POSE' and
                context.active_pose_bone and
                len(context.selected_pose_bones) == 2):
            return False
            
        return True
    
    def execute(self, context):
        # 获取是否应用约束的设置
        props = context.scene.bone_pose_world_props
        apply_constraint = props.apply_constraint
        
        # 1. 识别 A, B, P 骨骼
        selected_non_active_bones = [
            bone for bone in context.selected_pose_bones 
            if bone != context.active_pose_bone
        ]
        pose_bone_A = selected_non_active_bones[0] # 选中骨骼 A
        pose_bone_B = context.active_pose_bone       # 活动骨骼 B
        pose_bone_P = pose_bone_A.parent             # 父级骨骼 P
        
        if not pose_bone_P:
            self.report({'ERROR'}, "选中骨骼没有父级骨骼")
            return {'CANCELLED'}
        
        # 必须设置pose_bone_P骨架骨骼为活动对象，不然无法应用约束
        bpy.ops.pose.select_all(action='DESELECT')
        context.view_layer.objects.active = pose_bone_P.id_data
        pose_bone_P.id_data.data.bones.active = pose_bone_P.bone
        
        # 添加阻尼追踪约束
        damped_track_constraint = pose_bone_P.constraints.new('DAMPED_TRACK')
        damped_track_constraint.name = "temp_rotate_to_active"
        damped_track_constraint.target = pose_bone_B.id_data
        damped_track_constraint.subtarget = pose_bone_B.name
        damped_track_constraint.track_axis = 'TRACK_Y'  # 可以根据需要调整跟踪轴
        
        # 根据设置决定是否应用约束
        if apply_constraint:
            # 应用约束
            bpy.ops.constraint.apply(constraint=damped_track_constraint.name, owner='BONE')
            action_text = "已应用"
        else:
            # 不应用约束，只添加约束
            action_text = "已添加"
        
        # 更新场景
        context.view_layer.update()
        self.report({'INFO'}, f"父级骨骼 '{pose_bone_P.name}' {action_text}阻尼追踪约束指向 '{pose_bone_B.name}'")
        return {'FINISHED'}

class O_BonePoseXYZRotateToActive(bpy.types.Operator):
    bl_idname = "xbone.pose_xyz_rotate_to_active"
    bl_label = "父级特定轴向转向活动骨骼"
    bl_description = "旋转选中骨骼(A)的父级(P)，使A指向活动骨骼(B)的位置"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        """检查是否满足操作条件：姿态模式，选中骨骼（A），活动骨骼（B），且A有父级（P）"""
        if not (context.object and 
                context.object.type == 'ARMATURE' and 
                context.object.mode == 'POSE' and
                context.active_pose_bone and
                len(context.selected_pose_bones) == 2):
            return False
            
        return True
    
    def execute(self, context):
        props = context.scene.bone_pose_world_props

        # 1. 识别 A, B, P 骨骼
        selected_non_active_bones = [
            bone for bone in context.selected_pose_bones 
            if bone != context.active_pose_bone
        ]
        pose_bone_A = selected_non_active_bones[0] # 选中骨骼 A
        pose_bone_B = context.active_pose_bone       # 活动骨骼 B
        pose_bone_P = pose_bone_A.parent             # 父级骨骼 P
        
        if not pose_bone_P:
            self.report({'ERROR'}, "选中骨骼没有父级骨骼")
            return {'CANCELLED'}
        
        # 2. 获取 A, B, P 的世界坐标
        def get_bone_world_matrix(pose_bone):
            armature_obj = pose_bone.id_data
            return armature_obj.matrix_world @ pose_bone.matrix

        loc_A_world = get_bone_world_matrix(pose_bone_A).translation
        loc_B_world = get_bone_world_matrix(pose_bone_B).translation
        loc_P_world = get_bone_world_matrix(pose_bone_P).translation

        # 检查目标距离是否过近
        if (loc_B_world - loc_P_world).length_squared < 1e-6:
            self.report({'WARNING'}, "活动骨骼与父级骨骼位置过于接近，无法确定方向")
            return {'CANCELLED'}
        
        rotate_mode = props.rotate_mode
        rotate_axis_char = rotate_mode[0]  # 取第一个字符 'X', 'Y', 'Z'
        
         # 根据旋转模式计算投影向量
        if rotate_mode == 'Y_AXIS':
            # Y 模式：绕世界 Y 轴旋转（X-Z平面投影）
            axis_name = 'Y'
            vec_PA = Vector((loc_A_world.x - loc_P_world.x, 0, loc_A_world.z - loc_P_world.z))
            vec_PB = Vector((loc_B_world.x - loc_P_world.x, 0, loc_B_world.z - loc_P_world.z))
            axis_vector = Vector((0, 1, 0))

        elif rotate_mode == 'X_AXIS':
            # X 模式：绕世界 X 轴旋转（Y-Z平面投影）
            axis_name = 'X'
            vec_PA = Vector((0, loc_A_world.y - loc_P_world.y, loc_A_world.z - loc_P_world.z))
            vec_PB = Vector((0, loc_B_world.y - loc_P_world.y, loc_B_world.z - loc_P_world.z))
            axis_vector = Vector((1, 0, 0))

        elif rotate_mode == 'Z_AXIS':
            # Z 模式：绕世界 Z 轴旋转（X-Y平面投影）
            axis_name = 'Z'
            vec_PA = Vector((loc_A_world.x - loc_P_world.x, loc_A_world.y - loc_P_world.y, 0))
            vec_PB = Vector((loc_B_world.x - loc_P_world.x, loc_B_world.y - loc_P_world.y, 0))
            axis_vector = Vector((0, 0, 1))

        # 检查向量长度
        if vec_PA.length_squared < 1e-6 or vec_PB.length_squared < 1e-6:
            self.report({'WARNING'}, f"在{axis_name}模式投影后向量过短，无法旋转")
            return {'CANCELLED'}
        
        # 归一化向量
        vec_PA.normalize()
        vec_PB.normalize()
        
        # 计算角度（使用点积和叉积确定符号）
        dot = max(-1.0, min(1.0, vec_PA.dot(vec_PB)))  # 限制在[-1,1]范围内
        angle = math.acos(dot)
        
        # 使用叉积确定旋转方向
        cross = vec_PA.cross(vec_PB)
        if cross.dot(axis_vector) < 0:
            angle = -angle
        
        print(f"计算的角度: {math.degrees(angle):.2f}°")
        
        # 保存当前活动骨架
        original_active = context.view_layer.objects.active

        # 设置正确的活动对象和骨骼选择
        bpy.ops.pose.select_all(action='DESELECT')
        context.view_layer.objects.active = pose_bone_P.id_data
        pose_bone_P.id_data.data.bones.active = pose_bone_P.bone

        # 使用bpy.ops.transform.rotate执行旋转
        bpy.ops.transform.rotate(
            value=angle,
            orient_axis=rotate_axis_char,
            orient_type='GLOBAL',
            orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            orient_matrix_type='GLOBAL',
            constraint_axis=(rotate_axis_char == 'X', rotate_axis_char == 'Y', rotate_axis_char == 'Z'),
            mirror=False,
            use_proportional_edit=False,
            release_confirm=True,
        )

        # 恢复原始选择状态
        bpy.ops.pose.select_all(action='DESELECT')
        pose_bone_A.bone.select = True
        context.view_layer.objects.active = pose_bone_B.id_data
        pose_bone_B.id_data.data.bones.active = pose_bone_B.bone
        # 恢复原始活动骨架
        context.view_layer.objects.active = original_active
        
        self.report({'INFO'}, f"父级骨骼 '{pose_bone_P.name}' 绕世界{axis_name}轴旋转 {math.degrees(angle):.2f}°")
        return {'FINISHED'}


class P_BonePose(bpy.types.Panel):
    bl_idname = "X_PT_BonePose"
    bl_label = "姿态模式"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'XBone'  # 这里设置自定义标签的名称

    @classmethod
    def poll(cls, context):
        # 只有当主面板激活了此子面板时才显示
        # 使用getattr避免属性不存在时报错
        return getattr(context.scene, 'active_xbone_subpanel', '') == 'BoneTools'

    def draw(self, context):
        layout = self.layout
        props = context.scene.bone_pose_world_props # 获取属性组
        if context.mode == "POSE":
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator(O_BonePoseYUp.bl_idname, text=O_BonePoseYUp.bl_label)
            row.operator(O_BonePoseZUp.bl_idname, text=O_BonePoseZUp.bl_label)
            row.operator(O_BonePoseUpRight.bl_idname, text=O_BonePoseUpRight.bl_label)
            #摆正后各方向旋转
            row = col.row(align=True)
            row.operator(O_BonePoseX90.bl_idname, text="X 90", icon="DRIVER_ROTATIONAL_DIFFERENCE")
            row.operator(O_BonePoseY90.bl_idname, text="Y 90", icon="DRIVER_ROTATIONAL_DIFFERENCE")
            row.operator(O_BonePoseZ90.bl_idname, text="Z 90", icon="DRIVER_ROTATIONAL_DIFFERENCE")
            #快速应用为静止姿态，而物体不形变（先物体应用骨骼修改器）
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator(O_BonePoseApply.bl_idname, text=O_BonePoseApply.bl_label)
            row.operator(O_SwapPoseRest.bl_idname, text=O_SwapPoseRest.bl_label)

            col = layout.column(align=True)
            row = col.row(align=True)
            row.prop(context.scene, "bone_sel_col", text="索引")
            row.operator(O_InCSVSel.bl_idname, text=O_InCSVSel.bl_label)
            row.operator(O_BonePosePrint.bl_idname, text=O_BonePosePrint.bl_label, icon='COPYDOWN')

            # 移动功能
            col = layout.column(align=True)
            row = col.row(align=True)
            # 将行分割为两部分，第一部分占50%，第二部分占50%
            split = row.split(factor=0.5, align=True)
            # 第一部分：操作符按钮，占一半宽度
            split.operator(O_BonePoseMoveToActive.bl_idname, text=O_BonePoseMoveToActive.bl_label, icon='BONE_DATA')
            # 第二部分：三个轴向开关，平分另一半宽度
            row_axes = split.row(align=True)
            row_axes.prop(props, "move_x", text="X", toggle=True)
            row_axes.prop(props, "move_y", text="Y", toggle=True)
            row_axes.prop(props, "move_z", text="Z", toggle=True)
            
            # 旋转功能 (新增)
            row = col.row(align=True)
            row.operator(O_BonePoseRotateToActive.bl_idname, text=O_BonePoseRotateToActive.bl_label, icon='BONE_DATA')
            row.prop(props, "apply_constraint", text="应用约束")
            row = col.row(align=True)
            split = row.split(factor=0.5, align=True)
            split.operator(O_BonePoseXYZRotateToActive.bl_idname, text=O_BonePoseXYZRotateToActive.bl_label, icon='BONE_DATA')
            row_axes = split.row(align=True)
            row_axes.prop(props, "rotate_mode", expand=True)


            # 骨骼矩阵
            row = layout.row()
            row.label(text=f"{context.active_object.name}: {context.active_pose_bone.name}")
            row.prop(props, "pose_matrix", text="", icon='OBJECT_DATA', toggle=True)
            if props.pose_matrix:
                split = layout.split(align=True)
                col = split.column(align=True)
                col.label(text="基于骨架坐标系")
                row = col.row()
                row.label(text="位置")
                col.prop(props, "position", text="")
                row = col.row()
                row.label(text="欧拉")
                col.prop(props, "euler_rotation", text="")
                col.prop(props, "quaternion_rotation", text="四元数")
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
            if props.pose_matrix:
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





# 注册插件
def register():
    bpy.types.Scene.bone_sel_col = bpy.props.IntProperty(
        name="骨骼列",
        default=0,
        min=0,
    )
    bpy.utils.register_class(PG_BonePoseWorldProps)
    bpy.types.Scene.bone_pose_world_props = bpy.props.PointerProperty(type=PG_BonePoseWorldProps)
    
    bpy.utils.register_class(O_BonePoseYUp)
    bpy.utils.register_class(O_BonePoseZUp)
    bpy.utils.register_class(O_BonePoseUpRight)
    bpy.utils.register_class(O_BonePoseX90)
    bpy.utils.register_class(O_BonePoseY90)
    bpy.utils.register_class(O_BonePoseZ90)
    bpy.utils.register_class(O_BonePoseApply)
    bpy.utils.register_class(O_SwapPoseRest)
    bpy.utils.register_class(O_InCSVSel)
    bpy.utils.register_class(O_BonePosePrint)
    bpy.utils.register_class(O_BonePoseMoveToActive)
    bpy.utils.register_class(O_BonePoseRotateToActive)
    bpy.utils.register_class(O_BonePoseXYZRotateToActive)
    bpy.utils.register_class(P_BonePose)




# 注销插件
def unregister():
    del bpy.types.Scene.bone_sel_col

    bpy.utils.unregister_class(PG_BonePoseWorldProps)
    del bpy.types.Scene.bone_pose_world_props

    bpy.utils.unregister_class(O_BonePoseYUp)
    bpy.utils.unregister_class(O_BonePoseZUp)
    bpy.utils.unregister_class(O_BonePoseUpRight)
    bpy.utils.unregister_class(O_BonePoseX90)
    bpy.utils.unregister_class(O_BonePoseY90)
    bpy.utils.unregister_class(O_BonePoseZ90)
    bpy.utils.unregister_class(O_BonePoseApply)
    bpy.utils.unregister_class(O_SwapPoseRest)
    bpy.utils.unregister_class(O_InCSVSel)
    bpy.utils.unregister_class(O_BonePosePrint)
    bpy.utils.unregister_class(O_BonePoseMoveToActive)
    bpy.utils.unregister_class(O_BonePoseRotateToActive)
    bpy.utils.unregister_class(O_BonePoseXYZRotateToActive)
    bpy.utils.unregister_class(P_BonePose)
