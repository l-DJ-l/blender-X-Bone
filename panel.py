# type: ignore
import bpy

class MAIN_PT_XBonePanel(bpy.types.Panel):
    bl_idname = "MAIN_PT_XBonePanel"
    bl_label = "XQFA 工具集"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'XBone'

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)

        # 使用 prop_enum 自动处理高亮状态
        row.prop_enum(context.scene, 'active_xbone_subpanel', 'BoneTools', 
                     text="骨骼工具", icon='BONE_DATA')
        row.prop_enum(context.scene, 'active_xbone_subpanel', 'AttributeTools',
                     text="属性工具", icon='GROUP_VERTEX')
        row.prop_enum(context.scene, 'active_xbone_subpanel', 'OtherTools',
                     text="其他工具", icon='TOOL_SETTINGS')
        

class XBONE_OT_switch_subpanel(bpy.types.Operator):
    """切换子面板"""
    bl_idname = "xbone.switch_subpanel"
    bl_label = "切换子面板"
    
    subpanel_type: bpy.props.StringProperty(
        name="子面板类型",
        description="要切换到的子面板类型"
    )
    
    def execute(self, context):
        # 设置当前激活的子面板
        context.scene.active_xbone_subpanel = self.subpanel_type
        
        # 强制重绘所有区域
        for area in context.screen.areas:
            area.tag_redraw()
            
        return {'FINISHED'}
    

def register():
    # 注册主面板和子面板
    bpy.utils.register_class(MAIN_PT_XBonePanel)
    bpy.utils.register_class(XBONE_OT_switch_subpanel)
    
    # 添加场景属性来跟踪当前激活的子面板
    bpy.types.Scene.active_xbone_subpanel = bpy.props.EnumProperty(
        name="激活的子面板",
        description="当前激活的XBone子面板",
        items=[
            ('BoneTools', '骨骼与顶点组工具', ''),
            ('AttributeTools', '物体属性工具', ''),
            ('OtherTools', '其他工具', '')
        ],
        default='BoneTools'
    )


def unregister():
    # 注销所有类
    bpy.utils.unregister_class(MAIN_PT_XBonePanel)
    bpy.utils.unregister_class(XBONE_OT_switch_subpanel)
    
    # 删除场景属性
    if hasattr(bpy.types.Scene, 'active_xbone_subpanel'):
        del bpy.types.Scene.active_xbone_subpanel
    
