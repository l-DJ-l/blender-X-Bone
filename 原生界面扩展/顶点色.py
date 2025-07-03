# type: ignore
import bpy
import bmesh
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       CollectionProperty)
from bpy.types import PropertyGroup

# 调色板颜色项
class PaletteColorItem(PropertyGroup):
    color: FloatVectorProperty(
        name="颜色",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0)
    )

class DATA_PT_color_attribute_tools(bpy.types.Panel):
    bl_label = "颜色属性工具"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_parent_id = "DATA_PT_vertex_colors"
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and 
                context.object.type in {'MESH'})

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        
        # 颜色属性管理
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(scene, "color_attr_add_count", text="数量")
        row.operator(O_AddRenameColorAttributes.bl_idname, text="添加并重命名", icon='ADD')
        
        

        # 添加颜色按钮
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator(O_AddColor.bl_idname, text="添加颜色", icon='ADD')
        
        # 调色板颜色列表
        for i, color_item in enumerate(scene.palette_colors):
            row = col.row(align=True)
            row.prop(color_item, "color", text="")
            
            # 应用颜色按钮
            op = row.operator(O_ApplyColor.bl_idname, text="", icon='BRUSH_DATA')
            op.color_index = i

            # 删除颜色按钮
            op = row.operator(O_RemoveColor.bl_idname, text="", icon='X')
            op.color_index = i
        

class O_AddRenameColorAttributes(bpy.types.Operator):
    bl_idname = "xmod.color_attr_add_rename"
    bl_label = "添加并重命名"
    bl_description = "添加颜色属性并重命名为COLOR, COLOR1, COLOR2...格式"
    
    def execute(self, context):
        scene = context.scene
        target_count = scene.color_attr_add_count
        
        if target_count < 1:
            self.report({'ERROR'}, "数量必须大于0")
            return {'CANCELLED'}
            
        processed_objects = 0
        added_attrs = 0
        renamed_attrs = 0
        
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue
                
            processed_objects += 1
            color_attrs = [attr for attr in obj.data.color_attributes 
                         if attr.domain == 'CORNER' and attr.data_type == 'BYTE_COLOR']
            current_count = len(color_attrs)
            
            # 添加不足的数量
            if current_count < target_count:
                for i in range(current_count, target_count):
                    new_attr = obj.data.color_attributes.new(
                        name=f"COLOR{i}" if i > 0 else "COLOR",
                        type='BYTE_COLOR',
                        domain='CORNER'
                    )
                    added_attrs += 1
            
            # 重命名所有颜色属性
            color_attrs = [attr for attr in obj.data.color_attributes 
                         if attr.domain == 'CORNER' and attr.data_type == 'BYTE_COLOR']
            color_attrs.sort(key=lambda x: x.name)
            
            for i, attr in enumerate(color_attrs):
                new_name = f"COLOR{i}" if i > 0 else "COLOR"
                if attr.name != new_name:
                    attr.name = new_name
                    renamed_attrs += 1
        
        self.report({'INFO'}, 
                   f"处理完成: {processed_objects}个物体, 添加{added_attrs}个, 重命名{renamed_attrs}个")
        return {'FINISHED'}


# 调色板操作
class O_AddColor(bpy.types.Operator):
    bl_idname = "xmod.color_attr_add_color"
    bl_label = "添加颜色"
    bl_description = "向调色板添加新颜色"
    
    def execute(self, context):
        scene = context.scene
        new_color = scene.palette_colors.add()
        new_color.name = f"颜色 {len(scene.palette_colors)}"
        new_color.color = (1, 1, 1, 1)
        return {'FINISHED'}

class O_RemoveColor(bpy.types.Operator):
    bl_idname = "xmod.color_attr_remove_color"
    bl_label = "删除颜色"
    bl_description = "从调色板中删除颜色"
    
    color_index: IntProperty()
    
    def execute(self, context):
        scene = context.scene
        if scene.palette_colors:
            scene.palette_colors.remove(self.color_index)
        return {'FINISHED'}

class O_ApplyColor(bpy.types.Operator):
    bl_idname = "xmod.color_attr_apply_color"
    bl_label = "应用颜色"
    bl_description = "将颜色应用到当前活动的顶点色层"
    
    color_index: IntProperty()
    
    def execute(self, context):
        scene = context.scene
        obj = context.object
        
        # 基础检查
        if not obj:
            self.report({'ERROR'}, "未选中任何物体")
            return {'CANCELLED'}
            
        if obj.type != 'MESH':
            self.report({'ERROR'}, "所选对象不是网格类型")
            return {'CANCELLED'}
            
        if self.color_index >= len(scene.palette_colors):
            self.report({'ERROR'}, "调色板颜色索引无效")
            return {'CANCELLED'}
        
        # 获取调色板颜色（转换为0-1范围的RGBA）
        color_item = scene.palette_colors[self.color_index]
        color = color_item.color
        
        # 检查顶点色层
        mesh = obj.data
        if not mesh.vertex_colors:
            self.report({'ERROR'}, "该网格没有顶点色层")
            return {'CANCELLED'}
            
        if not mesh.vertex_colors.active:
            self.report({'ERROR'}, "没有激活的顶点色层")
            return {'CANCELLED'}
        
        # 使用bmesh高效修改
        bm = bmesh.new()
        bm.from_mesh(mesh)
        
        # 获取激活的顶点色层
        color_layer = mesh.vertex_colors.active
        color_layer_bm = bm.loops.layers.color.get(color_layer.name)
        
        if not color_layer_bm:
            bm.free()
            self.report({'ERROR'}, "无法访问顶点色层数据")
            return {'CANCELLED'}
        
        # 应用颜色到所有顶点
        for face in bm.faces:
            for loop in face.loops:
                loop[color_layer_bm] = color
        
        # 更新网格
        bm.to_mesh(mesh)
        bm.free()

        # 更新依赖图（确保所有相关数据更新）
        bpy.context.view_layer.update()
        
        self.report({'INFO'}, f"颜色 '{color_item.name}' 应用到顶点色层 '{color_layer.name}'")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(PaletteColorItem)
    bpy.utils.register_class(DATA_PT_color_attribute_tools)
    bpy.utils.register_class(O_AddRenameColorAttributes)
    bpy.utils.register_class(O_AddColor)
    bpy.utils.register_class(O_RemoveColor)
    bpy.utils.register_class(O_ApplyColor)
    
    # 场景属性
    bpy.types.Scene.color_attr_add_count = IntProperty(
        name="目标数量",
        description="要达到的颜色属性数量",
        default=1,
        min=1,
        max=32
    )
    
    bpy.types.Scene.palette_colors = CollectionProperty(
        type=PaletteColorItem
    )

    # 延迟添加默认颜色
    def add_default_colors():
        # 确保在正确的上下文中
        if hasattr(bpy.context, 'scene'):
            scene = bpy.context.scene
            # 只在调色板为空时添加默认颜色
            if len(scene.palette_colors) == 0:
                green = scene.palette_colors.add()
                green.color = (0.0, 0.352, 0.0, 1.0)
                
                orange = scene.palette_colors.add()
                orange.color = (1.0, 0.352, 0.0, 1.0)
                
                black = scene.palette_colors.add()
                black.color = (0.0, 0.0, 0.0, 1.0)
    
    # 使用计时器延迟执行，确保在正确的上下文中
    bpy.app.timers.register(add_default_colors, first_interval=0.1)


def unregister():
    bpy.utils.unregister_class(PaletteColorItem)
    bpy.utils.unregister_class(DATA_PT_color_attribute_tools)
    bpy.utils.unregister_class(O_AddRenameColorAttributes)
    bpy.utils.unregister_class(O_AddColor)
    bpy.utils.unregister_class(O_RemoveColor)
    bpy.utils.unregister_class(O_ApplyColor)
    
    del bpy.types.Scene.color_attr_add_count
    del bpy.types.Scene.palette_colors