# type: ignore
import bpy
import numpy as np
import time
from typing import Dict, Tuple, Set, List, Optional

class DATA_PT_vertex_group_tools(bpy.types.Panel):
    bl_label = "顶点组"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'XBone'

    @classmethod
    def poll(cls, context):
        # 只有当主面板激活了此子面板时才显示
        return getattr(context.scene, 'active_xbone_subpanel', '') == 'AttributeTools'

    def draw(self, context):
        layout = self.layout

        obj = context.object
        # 添加安全检查，确保物体存在且是网格物体
        if obj is None or obj.type != 'MESH':
            layout.label(text="请选择一个网格物体")
            return
        count0 = len(obj.vertex_groups)
        
        # 获取存储的统计信息，如果没有则显示默认值
        stats = obj.get("vertex_group_stats", {
            "total": count0,
            "with_weight": "N/A",
            "zero_weight": "N/A"
        })
        
        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text=f"数量: {stats['total']}")
        row.label(text=f"有权重: {stats['with_weight']}")
        row.label(text=f"无权重: {stats['zero_weight']}")

        row = col.row(align=True)
        row.operator(O_VertexGroupsCount.bl_idname, text=O_VertexGroupsCount.bl_label, icon="GROUP_VERTEX")
        row.operator(O_VertexGroupsDelNoneActive.bl_idname, text=O_VertexGroupsDelNoneActive.bl_label, icon="GROUP_VERTEX")

        row = col.row(align=True)
        row.prop(context.scene, "similarity_threshold")
        row.operator(O_VertexGroupsMatchRename.bl_idname, text=O_VertexGroupsMatchRename.bl_label, icon="SORTBYEXT")
        row.separator()  # 添加分割线
        row.operator(O_VertexGroupsSortMatch.bl_idname, text=O_VertexGroupsSortMatch.bl_label, icon="SORTSIZE")


class O_VertexGroupsCount(bpy.types.Operator):
    bl_idname = "xbone.vertex_groups_count"
    bl_label = "统计有无权重数量"
    bl_description = "统计活动物体顶点组中有权重和无权重的数量"
    
    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            vertex_groups = obj.vertex_groups
            mesh = obj.data
            
            # 使用更高效的方法检查顶点组是否有权重
            count_with_weight = 0
            count_zero_weight = 0
            
            # 为每个顶点组创建一个标记，初始为False(无权重)
            has_weights = [False] * len(vertex_groups)
            
            # 遍历所有顶点
            for vertex in mesh.vertices:
                for group in vertex.groups:
                    group_index = group.group
                    # 如果找到至少一个顶点有该组的权重，标记为True
                    if group.weight > 0:
                        has_weights[group_index] = True
            
            # 统计结果
            for has_weight in has_weights:
                if has_weight:
                    count_with_weight += 1
            count_zero_weight = len(vertex_groups) - count_with_weight
            
            # 将结果存储在对象属性中
            obj["vertex_group_stats"] = {
                "total": len(vertex_groups),
                "with_weight": count_with_weight,
                "zero_weight": count_zero_weight
            }
            
            self.report({'INFO'}, f"统计完成: 总数 {len(vertex_groups)}, 有权重 {count_with_weight}, 无权重 {count_zero_weight}")
        else:
            self.report({'ERROR'}, "请先选择一个Mesh对象作为活动对象。")
            return {'CANCELLED'}

        return {'FINISHED'}


class O_VertexGroupsDelNoneActive(bpy.types.Operator):
    bl_idname = "xbone.vertex_groups_del_none_active"
    bl_label = "删除无权重顶点组"
    bl_description = "删除活动物体中没有顶点权重的顶点组"
    
    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            vertex_groups = obj.vertex_groups
            mesh = obj.data
            
            # 使用更高效的方法检查顶点组是否有权重
            has_weights = [False] * len(vertex_groups)
            
            # 遍历所有顶点
            for vertex in mesh.vertices:
                for group in vertex.groups:
                    group_index = group.group
                    if group.weight > 0:
                        has_weights[group_index] = True
            
            # 收集要删除的顶点组名称（逆序以便安全删除）
            groups_to_remove = []
            for i, has_weight in reversed(list(enumerate(has_weights))):
                if not has_weight:
                    groups_to_remove.append(vertex_groups[i].name)
            
            # 删除无权重顶点组
            for group_name in groups_to_remove:
                vertex_groups.remove(vertex_groups[group_name])
            
            # 更新统计信息
            if "vertex_group_stats" in obj:
                remaining_count = len(vertex_groups)
                obj["vertex_group_stats"] = {
                    "total": remaining_count,
                    "with_weight": remaining_count,  # 删除后剩下的都是有权重的
                    "zero_weight": 0
                }
            
            self.report({'INFO'}, f"已删除 {len(groups_to_remove)} 个无权重顶点组：{groups_to_remove}")
        else:
            self.report({'ERROR'}, "请先选择一个Mesh对象作为活动对象。")
            return {'CANCELLED'}

        return {'FINISHED'}

class O_VertexGroupsMatchRename(bpy.types.Operator):
    bl_idname = "xbone.vertex_groups_match_rename"
    bl_label = "匹配重命名"
    bl_description = ("基于顶点平均位置匹配重命名活动物体的顶点组（需选择2个网格物体）\n"
                     "我用来给鸣潮提取的模型按解包的模型骨骼重命名，这样顶点组有名称意义也可以操控")
    
    def execute(self, context: bpy.types.Context) -> Set[str]:
        self.similarity_threshold = context.scene.similarity_threshold
        """主执行函数"""
        start_time = time.time()  # 记录开始时间
        
        try:
            # 验证输入并获取目标物体
            obj_a, obj_b = self._validate_input(context)
            
            # 执行匹配重命名并获取详细结果
            result = self._rename_matching_vertex_groups(obj_a, obj_b)
            
            # 打印详细结果到控制台
            self._print_detailed_results(obj_a, obj_b, result)
            
            # 计算总耗时
            elapsed_time = time.time() - start_time
            time_msg = f"总耗时: {elapsed_time:.2f}秒"
            
            # 根据结果返回适当的消息
            if result['renamed_count'] > 0:
                self.report({'INFO'}, f"成功匹配重命名 {result['renamed_count']} 个顶点组 ({time_msg})")
            else:
                self.report({'WARNING'}, f"没有找到匹配的顶点组 ({time_msg})")
                
            return {'FINISHED'}
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.report({'ERROR'}, f"{str(e)} (耗时: {elapsed_time:.2f}秒)")
            return {'CANCELLED'}
    
    def _validate_input(self, context: bpy.types.Context) -> Tuple[bpy.types.Object, bpy.types.Object]:
        """验证输入并返回两个网格物体"""
        selected_objs = context.selected_objects
        active_obj = context.active_object
        
        # 验证选择数量
        if len(selected_objs) != 2:
            raise ValueError("请选择2个网格物体")
            
        # 验证活动物体
        if active_obj not in selected_objs:
            raise ValueError("活动物体必须是选中的物体之一")
            
        # 获取两个物体
        obj_b = active_obj
        obj_a = next(obj for obj in selected_objs if obj != active_obj)
        
        # 验证物体类型
        if obj_a.type != 'MESH' or obj_b.type != 'MESH':
            raise ValueError("两个物体都必须是网格类型")
            
            
        return obj_a, obj_b
    
    def _get_vertex_group_centers(self, obj: bpy.types.Object) -> Dict[str, np.ndarray]:
        """获取每个顶点组的中心位置（平均位置）"""
        centers = {}
        mesh = obj.data
        global_verts = np.zeros((len(mesh.vertices), 3))
        
        # 获取所有顶点的局部坐标
        mesh.vertices.foreach_get('co', global_verts.ravel())
        
        # 转换为全局坐标
        matrix = np.array(obj.matrix_world)
        global_verts = np.dot(global_verts, matrix[:3, :3].T) + matrix[:3, 3]
        
        for vg in obj.vertex_groups:
            vertex_indices = []
            
            # 获取顶点组中的所有顶点索引
            for vid in range(len(mesh.vertices)):
                try:
                    if vg.weight(vid) > 0:
                        vertex_indices.append(vid)
                except RuntimeError:
                    pass
            
            if vertex_indices:
                # 计算这些顶点的平均位置
                centers[vg.name] = np.mean(global_verts[vertex_indices], axis=0)
        
        return centers
    
    def _calculate_similarity(self, pos_a: np.ndarray, pos_b: np.ndarray) -> float:
        """计算两个位置之间的相似度（基于距离）"""
        distance = np.linalg.norm(pos_a - pos_b)
        # 将距离转换为相似度（距离越小，相似度越高）
        # 使用简单的转换：相似度 = 1 / (1 + 距离)
        return 1.0 / (1.0 + distance)
    
    def _rename_matching_vertex_groups(self, 
                                     obj_a: bpy.types.Object, 
                                     obj_b: bpy.types.Object) -> Dict[str, any]:
        """匹配并重命名顶点组"""
        centers_a = self._get_vertex_group_centers(obj_a)
        centers_b = self._get_vertex_group_centers(obj_b)
        
        # 检查非空顶点组
        if not centers_a:
            raise Exception("A物体没有非空顶点组")
        if not centers_b:
            raise Exception("B物体没有非空顶点组")
        
        renamed_count = 0
        matched_a_groups: Set[str] = set()
        matches: List[Tuple[str, Optional[str], str]] = []  # (b_name, a_name, similarity)
        
        for b_name, b_center in centers_b.items():
            best_match_name = None
            best_similarity = 0.0
            
            # 寻找最佳匹配
            for a_name, a_center in centers_a.items():
                if a_name in matched_a_groups:
                    continue
                    
                similarity = self._calculate_similarity(a_center, b_center)
                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    best_similarity = similarity
                    best_match_name = a_name
            
            # 执行重命名
            if best_match_name:
                obj_b.vertex_groups[b_name].name = best_match_name
                matched_a_groups.add(best_match_name)
                renamed_count += 1
                matches.append((b_name, best_match_name, f"{best_similarity:.3f}"))
            else:
                matches.append((b_name, None, "no match"))
        
        return {
            'renamed_count': renamed_count,
            'matches': matches,
            'total_a': len(centers_a),
            'total_b': len(centers_b)
        }
    
    def _print_detailed_results(self, 
                              obj_a: bpy.types.Object, 
                              obj_b: bpy.types.Object, 
                              result: Dict[str, any]) -> None:
        """打印详细结果到控制台"""
        header = f"顶点组匹配与重命名详细结果 (A物体: {obj_a.name}, B物体: {obj_b.name})"
        separator = "=" * len(header)
        
        print(f"\n{separator}")
        print(header)
        print(separator)
        print(f"相似度阈值: {self.similarity_threshold:.3f}")
        print(f"{'B物体原始名称':<30} {'重命名为':<30} {'相似度':<20}")
        print("-" * 80)
        
        matched = 0 
        unmatched = 0
        
        for b_name, a_name, similarity in result['matches']:
            if a_name:
                matched += 1
                print(f"{b_name:<30} → {a_name:<30} {similarity:<20}")
            else:
                print(f"{b_name:<30} → {'保留原名称':<30} {'(未匹配)':<20}")
                unmatched += 1
        
        print(separator)
        print("总结:")
        print(f"  A物体非空顶点组数量: {result['total_a']}")
        print(f"  B物体非空顶点组数量: {result['total_b']}")
        print(f"  匹配数量: {matched}")
        print(f"  未匹配数量: {unmatched}")
        print(f"  总重命名数量: {result['renamed_count']}")
        print(separator)


class O_VertexGroupsSortMatch(bpy.types.Operator):
    bl_idname = "xbone.vertex_groups_sort_match"
    bl_label = "名称排序"
    bl_description = ("严格按照选择物体的顶点组顺序重新排列活动物体的顶点组\n"
                     "操作逻辑:\n"
                     "1. 按选择物体的顶点组顺序依次处理\n"
                     "2. 缺少的顶点组会新建空组\n"
                     "3. 已有的顶点组会移动到对应位置\n"
                     "4. 多余的顶点组会自动保留在最后")

    def execute(self, context):
        try:
            selected_objs = context.selected_objects
            active_obj = context.active_object
            
            # 验证选择
            if len(selected_objs) != 2:
                self.report({'ERROR'}, "请选择2个网格物体")
                return {'CANCELLED'}
                
            if active_obj not in selected_objs:
                self.report({'ERROR'}, "活动物体必须是选中的物体之一")
                return {'CANCELLED'}
                
            source_obj = next(obj for obj in selected_objs if obj != active_obj)
            target_obj = active_obj

            if source_obj.type != 'MESH' or target_obj.type != 'MESH':
                self.report({'ERROR'}, "两个物体都必须是网格类型")
                return {'CANCELLED'}
                
            # 执行排序
            result = self._sort_vertex_groups(context, source_obj, target_obj)
            
            self.report({'INFO'}, 
                       f"排序完成: 匹配 {result['matched']}个, "
                       f"新建 {result['added']}个")
            
            # 打印结果到控制台
            print(f"\n顶点组排序结果 [{target_obj.name} → {source_obj.name}]:")
            for i, vg in enumerate(target_obj.vertex_groups):
                prefix = "  ✓ " if vg.name in [x.name for x in source_obj.vertex_groups] else "  + "
                print(f"{i+1:2d}.{prefix}{vg.name}")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
    
    def _sort_vertex_groups(self, context, source_obj, target_obj):
        source_vgs = source_obj.vertex_groups
        target_vgs = target_obj.vertex_groups
        
        added_count = 0
        matched_count = 0
        
        # 保存当前活动顶点组索引
        original_active_index = target_obj.vertex_groups.active_index
        
        # 遍历源物体顶点组顺序
        for desired_index, src_vg in enumerate(source_vgs):
            if src_vg.name in target_vgs:
                # 已有顶点组，移动到正确位置
                current_index = target_vgs.find(src_vg.name)
                
                # 设置活动顶点组
                target_obj.vertex_groups.active_index = current_index
                
                # 计算需要移动的次数
                move_count = current_index - desired_index
                
                # 向上移动
                for _ in range(move_count):
                    bpy.ops.object.vertex_group_move(direction='UP')
                
                matched_count += 1
            else:
                # 新建顶点组
                new_vg = target_vgs.new(name=src_vg.name)
                added_count += 1
                
                # 设置活动顶点组为新创建的组
                target_obj.vertex_groups.active_index = len(target_vgs) - 1
                
                # 移动到正确位置
                move_count = len(target_vgs) - 1 - desired_index
                for _ in range(move_count):
                    bpy.ops.object.vertex_group_move(direction='UP')
        
        # 恢复原始活动顶点组
        if original_active_index < len(target_vgs):
            target_obj.vertex_groups.active_index = original_active_index
        
        return {
            'matched': matched_count,
            'added': added_count
        }


def register():
    bpy.utils.register_class(DATA_PT_vertex_group_tools)
    bpy.utils.register_class(O_VertexGroupsCount)
    bpy.utils.register_class(O_VertexGroupsDelNoneActive)
    bpy.utils.register_class(O_VertexGroupsMatchRename)
    bpy.utils.register_class(O_VertexGroupsSortMatch)

    bpy.types.Scene.similarity_threshold = bpy.props.FloatProperty(
        name="顶点组相似度阈值",
        description="匹配顶点组时的最小相似度(0-1)",
        default=0.94,
        min=0.9,
        max=1.0,
        step=0.01,
        precision=3
    )

def unregister():
    bpy.utils.unregister_class(DATA_PT_vertex_group_tools)
    bpy.utils.unregister_class(O_VertexGroupsCount)
    bpy.utils.unregister_class(O_VertexGroupsDelNoneActive)
    bpy.utils.unregister_class(O_VertexGroupsMatchRename)
    bpy.utils.unregister_class(O_VertexGroupsSortMatch)

    del bpy.types.Scene.similarity_threshold
