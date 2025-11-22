# type: ignore
import bpy

class DATA_PT_uv_map_tools(bpy.types.Panel):
    bl_label = "UV贴图"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'XBone'

    @classmethod
    def poll(cls, context):
        # 只有当主面板激活了此子面板时才显示
        return getattr(context.scene, 'active_xbone_subpanel', '') == 'AttributeTools'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # 添加操作按钮
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(scene, "uv_map_target_count", text="数量")
        row.operator(O_AddRenameUVMaps.bl_idname, 
                    text=O_AddRenameUVMaps.bl_label, 
                    icon="ADD")
        
        row = col.row(align=True)
        row.prop(scene, "uv_map_target_index", text="索引")
        row.operator(O_SetActiveUVMaps.bl_idname, text=O_SetActiveUVMaps.bl_label, icon="RESTRICT_SELECT_OFF")
        row.operator(O_SetRenderUVMaps.bl_idname, text=O_SetRenderUVMaps.bl_label, icon="RESTRICT_RENDER_OFF")
        row.operator(O_RemoveUVMaps.bl_idname, text=O_RemoveUVMaps.bl_label, icon="TRASH")


class O_AddRenameUVMaps(bpy.types.Operator):
    bl_idname = "xbone.uv_map_add_rename"
    bl_label = "添加并重命名"
    bl_description = "添加UV贴图并重命名为TEXCOORD.xy格式"
    
    def execute(self, context):
        scene = context.scene
        target_count = scene.uv_map_target_count
        
        if target_count < 1:
            self.report({'ERROR'}, "数量必须大于0")
            return {'CANCELLED'}
            
        processed_objects = 0
        added_maps = 0
        renamed_maps = 0
        
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue
                
            processed_objects += 1
            uv_layers = obj.data.uv_layers
            current_count = len(uv_layers)
            
            # 添加不足的数量
            if current_count < target_count:
                for i in range(current_count, target_count):
                    new_uv = uv_layers.new(name=f"TEXCOORD{i}.xy" if i > 0 else "TEXCOORD.xy")
                    added_maps += 1
            
            # 重命名所有UV贴图
            for i, uv_layer in enumerate(uv_layers):
                new_name = f"TEXCOORD{i}.xy" if i > 0 else "TEXCOORD.xy"
                if uv_layer.name != new_name:
                    uv_layer.name = new_name
                    renamed_maps += 1
        
        self.report({'INFO'}, 
                   f"处理完成: {processed_objects}个物体, 添加{added_maps}个, 重命名{renamed_maps}个")
        return {'FINISHED'}

class O_SetActiveUVMaps(bpy.types.Operator):
    bl_idname = "xbone.uv_map_set_active"
    bl_label = "设置活动"
    bl_description = "将所有选中物体的活动UV设置为指定索引"
    
    def execute(self, context):
        scene = context.scene
        target_index = scene.uv_map_target_index
        
        processed_objects = 0
        set_active_count = 0
        
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue
                
            processed_objects += 1
            uv_layers = obj.data.uv_layers
            
            if target_index < 0 or target_index >= len(uv_layers):
                self.report({'WARNING'}, f"物体 {obj.name} 的UV索引 {target_index} 超出范围")
                continue
                
            uv_layers.active = uv_layers[target_index]
            set_active_count += 1
        
        self.report({'INFO'}, 
                   f"处理完成: {processed_objects}个物体, 设置了{set_active_count}个活动UV")
        return {'FINISHED'}

class O_SetRenderUVMaps(bpy.types.Operator):
    bl_idname = "xbone.uv_map_set_render"
    bl_label = "设置渲染"
    bl_description = "将所有选中物体的渲染UV设置为指定索引"
    
    def execute(self, context):
        scene = context.scene
        target_index = scene.uv_map_target_index
        
        processed_objects = 0
        set_render_count = 0
        
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue
                
            processed_objects += 1
            uv_layers = obj.data.uv_layers
            
            if target_index < 0 or target_index >= len(uv_layers):
                self.report({'WARNING'}, f"物体 {obj.name} 的UV索引 {target_index} 超出范围")
                continue
                
            uv_layers[target_index].active_render = True
            # 确保其他UV层不激活渲染
            for i, uv_layer in enumerate(uv_layers):
                if i != target_index:
                    uv_layer.active_render = False
            set_render_count += 1
        
        self.report({'INFO'}, 
                   f"处理完成: {processed_objects}个物体, 设置了{set_render_count}个渲染UV")
        return {'FINISHED'}

class O_RemoveUVMaps(bpy.types.Operator):
    bl_idname = "xbone.uv_map_remove"
    bl_label = "删除"
    bl_description = "删除指定索引的UV贴图"
    
    def execute(self, context):
        scene = context.scene
        target_index = scene.uv_map_target_index
        
        processed_objects = 0
        removed_maps = 0
        
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue
                
            processed_objects += 1
            uv_layers = obj.data.uv_layers
            
            if target_index < 0 or target_index >= len(uv_layers):
                self.report({'WARNING'}, f"物体 {obj.name} 的UV索引 {target_index} 超出范围")
                continue
                
            # 删除指定索引的UV贴图
            uv_layer_to_remove = uv_layers[target_index]
            uv_layers.remove(uv_layer_to_remove)
            removed_maps += 1
            
            # 确保活动UV和渲染UV有效
            if len(uv_layers) > 0:
                if uv_layers.active is None:
                    uv_layers.active = uv_layers[0]
                # 确保至少有一个渲染UV
                if not any(uv.active_render for uv in uv_layers):
                    uv_layers[0].active_render = True
        
        self.report({'INFO'}, 
                   f"处理完成: {processed_objects}个物体, 删除了{removed_maps}个UV贴图")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(DATA_PT_uv_map_tools)
    bpy.utils.register_class(O_AddRenameUVMaps)
    bpy.utils.register_class(O_SetActiveUVMaps)
    bpy.utils.register_class(O_SetRenderUVMaps)
    bpy.utils.register_class(O_RemoveUVMaps)
    
    # 添加场景属性用于存储UV贴图数量
    bpy.types.Scene.uv_map_target_count = bpy.props.IntProperty(
        name="UV贴图添加数量",
        description="要添加的UV贴图数量",
        default=3,
        min=1,
        max=32
    )
    
    # 添加场景属性用于存储目标UV索引
    bpy.types.Scene.uv_map_target_index = bpy.props.IntProperty(
        name="目标UV索引",
        description="要设置的活动/渲染UV的索引",
        default=0,
        min=0,
        max=31
    )

def unregister():
    bpy.utils.unregister_class(DATA_PT_uv_map_tools)
    bpy.utils.unregister_class(O_AddRenameUVMaps)
    bpy.utils.unregister_class(O_SetActiveUVMaps)
    bpy.utils.unregister_class(O_SetRenderUVMaps)
    bpy.utils.unregister_class(O_RemoveUVMaps)
    
    del bpy.types.Scene.uv_map_target_count
    del bpy.types.Scene.uv_map_target_index