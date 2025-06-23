import bpy # type: ignore
import re

########################## Divider ##########################

class ObjType(bpy.types.Operator):
    def is_mesh(scene, obj):
        return obj.type == "MESH"
    
    def is_armature(scene, obj):
        return obj.type == "ARMATURE"

class O_VertexGroupsDelAll(bpy.types.Operator):
    bl_idname = "vertex_groups.del_all_more"
    bl_label = "删除所有顶点组"
    bl_description = "删除选择的多个物体的所有顶点组"
    
    def invoke(self, context, event): # 确认窗口
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=160)

    def execute(self, context):
        # 遍历所选物体
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                # 删除每个顶点组
                for group in obj.vertex_groups:
                    obj.vertex_groups.remove(group)
                
                # 更新物体
                obj.update_tag()
            else:
                print("不是网络对象")
        self.report({'INFO'}, "已删除选择物体的所有顶点组！")
        return {'FINISHED'}

class O_VertexGroupsDelNone(bpy.types.Operator):
    bl_idname = "vertex_groups.del_none_more"
    bl_label = "删除无权重顶点组"
    bl_description = "删除选择的多个物体中没有顶点权重的顶点组"
    
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

class O_NoVgDelBone(bpy.types.Operator):
    bl_idname = "vertex_groups.no_vg_del_bone"
    bl_label = "删除无对应顶点组的骨骼"
    bl_description = "删除选择的骨骼中无对应顶点组的骨骼"

    def execute(self, context):
        try:
            SourceMesh = bpy.data.objects.get(context.scene.vg_source_mesh.name)
            SourceArmature = bpy.data.objects.get(context.scene.vg_source_armature.name)
        except:
            self.report({'ERROR'}, "似乎没有选择对象") 
            return {'FINISHED'}
        if not context.selected_pose_bones:
            self.report({'ERROR'}, "请进入姿态模式选择骨骼") 
            return {'FINISHED'}
        if SourceArmature != context.active_object:
            self.report({'ERROR'}, "选择的骨架与进入姿态模式的骨架不同") 
            return {'FINISHED'}
        
        del_bones = []
        bpy.ops.object.mode_set(mode='EDIT')
        for bone in context.selected_bones:
            for group in SourceMesh.vertex_groups:
                if bone.name == group.name:
                    break
            else:
                del_bones.append(bone.name)
        
        bpy.ops.armature.select_all(action='DESELECT')
        for bone_name in del_bones:
            bpy.ops.object.select_pattern(pattern=bone_name)
            print(f"已删除{bone_name}骨骼")
        bpy.ops.armature.delete()

        bpy.ops.object.mode_set(mode='POSE')
        self.report({'INFO'}, f"已删除{len(del_bones)}个无对应顶点组的骨骼！")
        return {'FINISHED'}

class O_NoBoneDelVg(bpy.types.Operator):
    bl_idname = "vertex_groups.no_bone_del_vg"
    bl_label = "删除无对应骨骼的顶点组"
    bl_description = "删除顶点组中无对应骨骼的顶点组"
    
    def execute(self, context):
        try:
            SourceMesh = bpy.data.objects.get(context.scene.vg_source_mesh.name)
            SourceArmature = bpy.data.objects.get(context.scene.vg_source_armature.name)
        except:
            self.report({'ERROR'}, "似乎没有选择对象") 
            return {'FINISHED'}
        
        del_groups = []
        for group in SourceMesh.vertex_groups:
            for bone in SourceArmature.data.bones:
                if group.name == bone.name:
                    break
            else:
                del_groups.append(group.name)
                SourceMesh.vertex_groups.remove(group)
        
        for group_name in del_groups:
            print(f"已删除{group_name}顶点组")

        self.report({'INFO'}, f"已删除{len(del_groups)}个无对应骨骼的顶点组！")
        return {'FINISHED'}

########################## Divider ##########################

class O_AddBoneNumber(bpy.types.Operator):
    bl_idname = "vertex_groups.add_bone_number"
    bl_label = "添加骨骼编号"
    bl_description = "对有权重骨添加骨骼编号"
    
    def execute(self, context):
        try:
            SourceMesh = bpy.data.objects.get(context.scene.vg_source_mesh.name)
            SourceArmature = bpy.data.objects.get(context.scene.vg_source_armature.name)
        except:
            self.report({'ERROR'}, "似乎没有选择对象") 
            return {'FINISHED'}
        # 创建一个字典来存储顶点组的信息
        vertex_group_info = {}
        for group in SourceMesh.vertex_groups:
            vertex_group_info[group.name] = []

        # 遍历每个顶点
        for vertex in SourceMesh.data.vertices:
            for group in vertex.groups: #遍历单个顶点的顶点组
                group_index = group.group
                group_name = SourceMesh.vertex_groups[group_index].name
                weight = group.weight

                # 将顶点和权重信息添加到字典中
                vertex_group_info[group_name].append((vertex.index, weight))

        # 添加编号
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = SourceArmature
        bpy.ops.object.mode_set(mode='POSE')
        bone_number = 0
        for bone in SourceArmature.pose.bones:
            for group_name, vertex_info in vertex_group_info.items():
                if bone.name == group_name and vertex_info: #如果有对应顶点组且有权重
                    # 正则判断是否已经有编号
                    pattern = re.compile(r'^b\d+:')
                    if pattern.match(bone.name):
                        bone.name = re.sub(r'^b\d+:', '', bone.name)
                    bone_number = bone_number + 1
                    bone.name = "b" + "{:03d}".format(bone_number) + ":" + bone.name
                    print(f"{bone.name}")
                    break

        self.report({'INFO'}, f"已添加{bone_number}个骨骼编号！")
        return {'FINISHED'}
    
class O_RemoveBoneNumber(bpy.types.Operator):
    bl_idname = "vertex_groups.remove_bone_number"
    bl_label = "移除骨骼编号"
    bl_description = ""
    
    def execute(self, context):
        try:
            SourceMesh = bpy.data.objects.get(context.scene.vg_source_mesh.name)
            SourceArmature = bpy.data.objects.get(context.scene.vg_source_armature.name)
        except:
            self.report({'ERROR'}, "似乎没有选择对象") 
            return {'FINISHED'}
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = SourceArmature
        bpy.ops.object.mode_set(mode='POSE')
        for bone in SourceArmature.pose.bones:
            bone.name = re.sub(r'^b\d+:', '', bone.name)
            print(f"{bone.name}")


        self.report({'INFO'}, "已移除骨骼编号！")
        return {'FINISHED'}

########################## Divider ##########################

class P_VertexGroups(bpy.types.Panel):
    bl_idname = "X_PT_VertexGroups"
    bl_label = "骨骼与顶点组"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bone+'  # 这里设置自定义标签的名称

    def draw(self, context):
        layout = self.layout
        layout.operator(O_VertexGroupsDelAll.bl_idname, text=O_VertexGroupsDelAll.bl_label, icon="GROUP_VERTEX")       
        layout.operator(O_VertexGroupsDelNone.bl_idname, text=O_VertexGroupsDelNone.bl_label, icon="GROUP_VERTEX")
        box = layout.box()
        col = box.column(align=True)
        col.prop(context.scene, "vg_source_mesh", text="", icon="MESH_DATA")
        col.prop(context.scene, "vg_source_armature", text="", icon="ARMATURE_DATA")
        row = box.row()
        row.label(text="顶点组数量:")
        if context.scene.vg_source_mesh:
            row.label(text=f"{len(context.scene.vg_source_mesh.vertex_groups)}")
        box.operator(O_NoVgDelBone.bl_idname, text=O_NoVgDelBone.bl_label, icon="BONE_DATA")       
        box.operator(O_NoBoneDelVg.bl_idname, text=O_NoBoneDelVg.bl_label, icon="GROUP_VERTEX")
        row = box.row(align=True)
        row.operator(O_AddBoneNumber.bl_idname, text=O_AddBoneNumber.bl_label)
        row.operator(O_RemoveBoneNumber.bl_idname, text=O_RemoveBoneNumber.bl_label)


########################## Divider ##########################

def register():
    bpy.utils.register_class(O_VertexGroupsDelAll)
    bpy.utils.register_class(O_VertexGroupsDelNone)
    bpy.utils.register_class(O_NoVgDelBone)
    bpy.utils.register_class(O_NoBoneDelVg)
    bpy.utils.register_class(O_AddBoneNumber)
    bpy.utils.register_class(O_RemoveBoneNumber)
    bpy.utils.register_class(P_VertexGroups)

    bpy.types.Scene.vg_source_mesh = bpy.props.PointerProperty(type=bpy.types.Object, poll=ObjType.is_mesh)
    bpy.types.Scene.vg_source_armature = bpy.props.PointerProperty(type=bpy.types.Object, poll=ObjType.is_armature)

def unregister():
    bpy.utils.unregister_class(O_VertexGroupsDelAll)
    bpy.utils.unregister_class(O_VertexGroupsDelNone)
    bpy.utils.unregister_class(O_NoVgDelBone)
    bpy.utils.unregister_class(O_NoBoneDelVg)
    bpy.utils.unregister_class(O_AddBoneNumber)
    bpy.utils.unregister_class(O_RemoveBoneNumber)
    bpy.utils.unregister_class(P_VertexGroups)

    del bpy.types.Scene.vg_source_mesh
    del bpy.types.Scene.vg_source_armature