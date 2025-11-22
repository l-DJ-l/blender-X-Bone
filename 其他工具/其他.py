# type: ignore
import bpy
from bpy.props import IntProperty
import mathutils
from mathutils import Vector
import math

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

    @classmethod
    def poll(cls, context):
        # 只有当主面板激活了此子面板时才显示
        return getattr(context.scene, 'active_xbone_subpanel', '') == 'OtherTools'
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator(MiniPlaneOperator.bl_idname, icon="MESH_CUBE")
        col.operator(RenameToComponents.bl_idname, icon="OUTLINER_OB_EMPTY")
        col.operator(TANGENTSPACE_OCTAHEDRAL_UV_OT_operator.bl_idname, icon='UV')

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
    
class NODE_OT_add_packed_image(bpy.types.Operator):
    """创建已打包图像"""
    bl_idname = "xbone.add_packed_image"
    bl_label = "创建已打包图像"
    bl_options = {'REGISTER', 'UNDO'}

    # 添加分辨率属性
    width: IntProperty(
        name="宽度",
        description="图像的宽度",
        default=2048,
        min=1,
        max=16384
    )
    
    height: IntProperty(
        name="高度",
        description="图像的高度",
        default=2048,
        min=1,
        max=16384
    )

    def execute(self, context):
        # 检查是否有活动对象和材质
        if not context.active_object or not context.active_object.active_material:
            self.report({'ERROR'}, "请先选择带有材质的对象")
            return {'CANCELLED'}
        
        mat = context.active_object.active_material
        nodes = mat.node_tree.nodes
        
        # 创建新图像
        image_name = "已打包图像"
            
        image = bpy.data.images.new(
            name=image_name,
            width=self.width,
            height=self.height,
            alpha=True,
            float_buffer=False,
            is_data=False,
            tiled=False
        )
        
        # 获取鼠标位置
        mouse_x = context.space_data.cursor_location[0]
        mouse_y = context.space_data.cursor_location[1]
        
        # 创建图像纹理节点并放置在鼠标位置
        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.image = image
        tex_node.location = (mouse_x, mouse_y)
        
        # 修改第一个像素点为白色（RGBA=1,1,1,1）确保被修改能够打包
        pixels = list(image.pixels)
        pixels[0] = 1.0  # R
        pixels[1] = 1.0  # G
        pixels[2] = 1.0  # B
        pixels[3] = 1.0  # A
        image.pixels = pixels
        
        # 更新图像
        image.update()
        
        # 打包图像到.blend文件
        image.pack()
        
        self.report({'INFO'}, f"已创建打包图像纹理 {self.width}x{self.height}")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # 设置鼠标位置
        context.space_data.cursor_location_from_region(event.mouse_region_x, event.mouse_region_y)
        # 弹出对话框让用户设置分辨率
        return context.window_manager.invoke_props_dialog(self)


class NODE_PT_add_packed_image(bpy.types.Panel):
    """在节点编辑器侧边栏中添加面板"""
    bl_label = "图像"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "XBone"
    
    def draw(self, context):
        layout = self.layout
        layout.operator(NODE_OT_add_packed_image.bl_idname)


class NODE_OT_add_material(bpy.types.Operator):
    bl_idname = "xbone.add_material"
    bl_label = "新建3贴图材质"
    bl_options = {'REGISTER', 'UNDO'}

    # 分辨率属性
    width: IntProperty(
        name="宽度",
        description="图像的宽度",
        default=2048,
        min=1,
        max=16384
    )
    
    height: IntProperty(
        name="高度",
        description="图像的高度",
        default=2048,
        min=1,
        max=16384
    )

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "请先选择对象")
            return {'CANCELLED'}
        
        # 获取或创建材质
        mat = obj.active_material
        if not mat:
            mat = bpy.data.materials.new(name=obj.name)
            obj.data.materials.append(mat)
        
        # 确保使用节点
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # 查找原理化BSDF节点
        bsdf = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
        if not bsdf:
            bsdf = nodes.new('ShaderNodeBsdfPrincipled')
            bsdf.location = (0, 0)
        
        # 创建三张图像纹理
        base_color_name = f"{obj.name}基础色"
        metallic_name = f"{obj.name}金属度"
        roughness_name = f"{obj.name}糙度"
        
        # 基于BSDF节点位置布局
        bsdf_x, bsdf_y = bsdf.location
        offset_x = -400  # 纹理节点在BSDF左侧
        
        # 创建基础色纹理
        base_color_image = bpy.data.images.new(
            name=base_color_name,
            width=self.width,
            height=self.height,
            alpha=True,
            float_buffer=False,
            is_data=False,
            tiled=False
        )
        self.set_default_pixels(base_color_image, (0.8, 0.8, 0.8, 1.0))
        base_color_node = self.create_image_node(
            nodes, base_color_image, 
            (bsdf_x + offset_x, bsdf_y + 300)
        )
        links.new(base_color_node.outputs['Color'], bsdf.inputs['Base Color'])
        
        # 创建金属度纹理
        metallic_image = bpy.data.images.new(
            name=metallic_name,
            width=self.width,
            height=self.height,
            alpha=False,
            float_buffer=False,
            is_data=True,
            tiled=False
        )
        self.set_default_pixels(metallic_image, (0.0, 0.0, 0.0, 1.0))
        metallic_node = self.create_image_node(
            nodes, metallic_image, 
            (bsdf_x + offset_x, bsdf_y)
        )
        links.new(metallic_node.outputs['Color'], bsdf.inputs['Metallic'])
        
        # 创建糙度纹理
        roughness_image = bpy.data.images.new(
            name=roughness_name,
            width=self.width,
            height=self.height,
            alpha=False,
            float_buffer=False,
            is_data=True,
            tiled=False
        )
        self.set_default_pixels(roughness_image, (0.5, 0.5, 0.5, 1.0))
        roughness_node = self.create_image_node(
            nodes, roughness_image, 
            (bsdf_x + offset_x, bsdf_y - 300)
        )
        links.new(roughness_node.outputs['Color'], bsdf.inputs['Roughness'])
        
        self.report({'INFO'}, f"已创建材质 {self.width}x{self.height}")
        return {'FINISHED'}
    
    def set_default_pixels(self, image, color):
        """设置图像的默认像素颜色"""
        pixels = [color[0], color[1], color[2], color[3]] * (image.size[0] * image.size[1])
        image.pixels = pixels
        image.update()
        image.pack()
    
    def create_image_node(self, nodes, image, location):
        """创建图像纹理节点"""
        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.image = image
        tex_node.location = location
        return tex_node
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class NODE_PT_add_material(bpy.types.Panel):
    """在材质属性中创建面板"""
    bl_label = "材质工具"
    bl_idname = "NODE_PT_add_material"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        if obj:
            row = layout.row()
            row.operator(NODE_OT_add_material.bl_idname)

def unit_vector_to_octahedron(n):
    """
    Converts a unit vector to octahedron coordinates.
    n is a mathutils.Vector
    """
    # 确保输入是单位向量
    if n.length_squared > 1e-10:
        n.normalize()
    else:
        return Vector((0.0, 0.0))
    
    # 计算L1范数
    l1_norm = abs(n.x) + abs(n.y) + abs(n.z)
    if l1_norm < 1e-10:
        return Vector((0.0, 0.0))
    
    # 投影到八面体平面
    x = n.x / l1_norm
    y = n.y / l1_norm
    
    # 负半球映射（仅在z<0时应用）
    if n.z < 0:
        # 使用精确的符号函数
        sign_x = math.copysign(1.0, x)
        sign_y = math.copysign(1.0, y)
        
        # 原始映射公式（保留在z=0处的良好行为）
        new_x = (1.0 - abs(y)) * sign_x
        new_y = (1.0 - abs(x)) * sign_y
        
        # 直接应用新坐标（移除过渡插值）
        x = new_x
        y = new_y
    
    return Vector((x, y))

def calc_smooth_normals(mesh):
    """计算平滑法线（角度加权平均）"""
    vertex_normals = {}
    
    # 使用顶点索引作为键（避免浮点精度问题）
    for i, vert in enumerate(mesh.vertices):
        vertex_normals[i] = Vector((0, 0, 0))
    
    # 计算每个面的法线并加权累加到顶点
    for poly in mesh.polygons:
        verts = [mesh.vertices[i] for i in poly.vertices]
        face_normal = poly.normal
        
        for i, vert in enumerate(verts):
            # 获取相邻边向量
            v1 = verts[(i+1) % len(verts)].co - vert.co
            v2 = verts[(i-1) % len(verts)].co - vert.co
            
            # 计算角度权重
            v1_len = v1.length
            v2_len = v2.length
            if v1_len > 1e-6 and v2_len > 1e-6:
                v1.normalize()
                v2.normalize()
                weight = math.acos(max(-1.0, min(1.0, v1.dot(v2))))
            else:
                weight = 0.0
            
            # 累加加权法线
            vertex_normals[vert.index] += face_normal * weight
    
    # 归一化法线
    for idx in vertex_normals:
        if vertex_normals[idx].length > 1e-6:
            vertex_normals[idx].normalize()
    
    return vertex_normals

class TANGENTSPACE_OCTAHEDRAL_UV_OT_operator(bpy.types.Operator):
    """生成切线空间的八面体UV映射"""
    bl_idname = "xbone.octahedral_uv"
    bl_label = "平滑法线-八面体UV"
    bl_description = ("对所有选中物体\n"
    "平滑法线在切线空间的坐标，投射八面体展开平面\n"
    "存储在TEXCOORD1")
    bl_options = {'REGISTER', 'UNDO'}
    
    
    @classmethod
    def poll(cls, context):
        """检查是否可以选择网格物体"""
        return context.selected_objects is not None and len(context.selected_objects) > 0
    
    def execute(self, context):
        """执行操作"""
        selected_objects = context.selected_objects
        processed_count = 0
        
        for obj in selected_objects:
            if self.process_object(obj):
                processed_count += 1
        
        # 更新显示
        context.view_layer.update()
        
        if processed_count > 0:
            self.report({'INFO'}, f"切线空间八面体UV映射完成！共处理 {processed_count} 个网格物体")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "没有处理任何网格物体，请确保选中了网格物体")
            return {'CANCELLED'}
    
    def process_object(self, obj):
        """处理单个网格物体"""
        if obj.type != 'MESH':
            return False
            
        mesh = obj.data
        
        # 确保在对象模式（数据一致）
        if bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # 操作前将活动UV设置为第一个（索引0）
        if len(mesh.uv_layers) > 0:
            mesh.uv_layers.active_index = 0
        
        # 计算平滑法线
        smooth_normals = calc_smooth_normals(mesh)
        
        # 确保网格有UV层（计算切线需要）
        if len(mesh.uv_layers) == 0:
            mesh.uv_layers.new(name="UVMap")
        
        # 计算切线空间（TBN矩阵）
        mesh.calc_tangents()
        
        # 创建/获取UV层
        uv_layer_name = "TEXCOORD1.xy"
        if uv_layer_name in mesh.uv_layers:
            uv_layer = mesh.uv_layers[uv_layer_name]
        else:
            uv_layer = mesh.uv_layers.new(name=uv_layer_name)
        
        # 处理每个面的每个顶点
        for poly in mesh.polygons:
            for loop_idx in range(poly.loop_start, poly.loop_start + poly.loop_total):
                loop = mesh.loops[loop_idx]
                vertex_idx = loop.vertex_index
                
                # 获取平滑法线
                normal = smooth_normals[vertex_idx]

                # 构建TBN矩阵（切线空间到模型空间的变换）
                tbn_matrix = mathutils.Matrix((
                    loop.tangent,
                    loop.bitangent,
                    loop.normal
                )).transposed() # 转置以从行向量变为列向量
                
                # 检查矩阵是否可逆
                try:
                    # 尝试计算逆矩阵
                    tbn_inverse = tbn_matrix.inverted()
                    
                    # 将法线从模型空间转换到切线空间
                    tangent_normal = tbn_inverse @ normal
                    tangent_normal.normalize()
                except ValueError:
                    # 矩阵不可逆时的回退方案
                    print(f"警告: 顶点 {vertex_idx} 的TBN矩阵不可逆，使用默认法线")
                    
                    tangent_normal = Vector((0, 0, 1))  # 默认使用Z轴作为法线
                
                # 八面体投影
                oct_coords = unit_vector_to_octahedron(tangent_normal)
                
                # 设置UV
                u = oct_coords.x
                v = oct_coords.y + 1.0
                uv_layer.data[loop_idx].uv = (u, v)
        
        # 释放切线数据
        mesh.free_tangents()
        
        return True


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
    
    bpy.utils.register_class(NODE_OT_add_packed_image)
    bpy.utils.register_class(NODE_PT_add_packed_image)

    bpy.utils.register_class(NODE_OT_add_material)
    bpy.utils.register_class(NODE_PT_add_material)
    bpy.utils.register_class(TANGENTSPACE_OCTAHEDRAL_UV_OT_operator)


def unregister():
    bpy.utils.unregister_class(P_DEMO)
    bpy.utils.unregister_class(MiniPlaneOperator)
    bpy.utils.unregister_class(RenameToComponents)
    bpy.utils.unregister_class(ApplyAsShapekey)
    del bpy.types.Scene.sk_source_mesh

    bpy.utils.unregister_class(NODE_OT_add_packed_image)
    bpy.utils.unregister_class(NODE_PT_add_packed_image)

    bpy.utils.unregister_class(NODE_OT_add_material)
    bpy.utils.unregister_class(NODE_PT_add_material)
    bpy.utils.unregister_class(TANGENTSPACE_OCTAHEDRAL_UV_OT_operator)


