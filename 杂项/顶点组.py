import bpy # type: ignore
import math
from mathutils import Euler, Matrix, Vector, Quaternion # type: ignore

########################## Divider ##########################

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
                        print(f"已删除顶点组：{group_name}")
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
    
########################## Divider ##########################

class P_VertexGroups(bpy.types.Panel):
    bl_idname = "PT_VertexGroups"
    bl_label = "顶点组"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bone+'  # 这里设置自定义标签的名称

    def draw(self, context):
        layout = self.layout
        layout.label(text=f"顶点组数量: {len(context.active_object.vertex_groups)}")
        layout.operator(O_VertexGroupsDelAll.bl_idname, text=O_VertexGroupsDelAll.bl_label)       
        layout.operator(O_VertexGroupsDelNone.bl_idname, text=O_VertexGroupsDelNone.bl_label)


########################## Divider ##########################

def register():
    bpy.utils.register_class(O_VertexGroupsDelAll)
    bpy.utils.register_class(O_VertexGroupsDelNone)
    bpy.utils.register_class(P_VertexGroups)

def unregister():
    bpy.utils.unregister_class(O_VertexGroupsDelAll)
    bpy.utils.unregister_class(O_VertexGroupsDelNone)
    bpy.utils.unregister_class(P_VertexGroups)