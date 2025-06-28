# type: ignore
import bpy

class DATA_PT_vertex_group_tools(bpy.types.Panel):
    bl_label = "顶点组扩展操作"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_parent_id = "DATA_PT_vertex_groups"  # 设置为顶点组面板的ID
    bl_options = {'HIDE_HEADER'}  # 隐藏标题栏

    @classmethod
    def poll(cls, context):
        return (context.object is not None and 
                context.object.type in {'MESH', 'LATTICE', 'CURVE', 'SURFACE'})

    def draw(self, context):
        layout = self.layout

        obj = context.object
        count0 = len(obj.vertex_groups)
        
        # 获取存储的统计信息，如果没有则显示默认值
        stats = obj.get("vertex_group_stats", {
            "total": count0,
            "with_weight": "N/A",
            "zero_weight": "N/A"
        })
        
        row = layout.row()
        row.label(text=f"数量: {stats['total']}")
        row.label(text=f"有权重: {stats['with_weight']}")
        row.label(text=f"无权重: {stats['zero_weight']}")

        row = layout.row(align=True)
        row.operator(O_VertexGroupsCount.bl_idname, text=O_VertexGroupsCount.bl_label, icon="GROUP_VERTEX")
        row.operator(O_VertexGroupsDelNoneActive.bl_idname, text=O_VertexGroupsDelNoneActive.bl_label, icon="GROUP_VERTEX")

        row = layout.row(align=True)
        row.operator(O_VertexGroupsMatchRename.bl_idname, text=O_VertexGroupsMatchRename.bl_label, icon="SORTBYEXT")
        row.operator(O_VertexGroupsSortMatch.bl_idname, text=O_VertexGroupsSortMatch.bl_label, icon="SORTSIZE")

class O_VertexGroupsCount(bpy.types.Operator):
    bl_idname = "vertex_groups.count"
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
    bl_idname = "vertex_groups.del_none_active"
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
    bl_idname = "vertex_groups.match_rename"
    bl_label = "匹配重命名顶点组"
    bl_description = "基于权重匹配重命名活动物体的顶点组（需选择2个网格物体）\n我用来给鸣潮提取的模型按解包的模型骨骼重命名，这样顶点组有名称意义也可以操控"
    
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
                
            obj_b = active_obj
            obj_a = next(obj for obj in selected_objs if obj != active_obj)
            
            if obj_a.type != 'MESH' or obj_b.type != 'MESH':
                self.report({'ERROR'}, "两个物体都必须是网格类型")
                return {'CANCELLED'}
                
            # 检查顶点数
            if len(obj_a.data.vertices) != len(obj_b.data.vertices):
                self.report({'ERROR'}, "两个物体的顶点数不相同")
                return {'CANCELLED'}
                
            # 执行匹配重命名并获取详细结果
            result = self._rename_matching_vertex_groups(obj_a, obj_b)
            renamed_count = result['renamed_count']
            
            # 打印详细结果到控制台
            self._print_detailed_results(obj_a, obj_b, result)
            
            if renamed_count > 0:
                self.report({'INFO'}, f"成功匹配重命名 {renamed_count} 个顶点组 (详见控制台)")
            else:
                self.report({'WARNING'}, "没有找到匹配的顶点组 (详见控制台)")
                
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
    
    def _rename_matching_vertex_groups(self, obj_a, obj_b):
        import numpy as np
        
        # 获取非空顶点组的排序权重
        def get_sorted_weights(obj):
            weights_data = {}
            mesh = obj.data
            
            for vg in obj.vertex_groups:
                weights = np.zeros(len(mesh.vertices))
                has_weights = False
                
                for vid, vert in enumerate(mesh.vertices):
                    try:
                        weight = vg.weight(vert.index)
                        weights[vid] = weight
                        if weight > 0:
                            has_weights = True
                    except RuntimeError:
                        pass
                
                if has_weights:
                    sorted_weights = np.sort(weights)
                    weights_data[vg.name] = (vg, sorted_weights)
            
            return weights_data
        
        weights_a = get_sorted_weights(obj_a)
        weights_b = get_sorted_weights(obj_b)
        
        if not weights_a:
            raise Exception("A物体没有非空顶点组")
        if not weights_b:
            raise Exception("B物体没有非空顶点组")
        
        # 匹配并重命名
        renamed_count = 0
        matched_a_groups = set()
        matches = []
        
        for b_name, (vg_b, b_weights) in weights_b.items():
            best_match = None
            best_match_name = None
            
            for a_name, (vg_a, a_weights) in weights_a.items():
                if a_name in matched_a_groups:
                    continue
                    
                if np.allclose(a_weights, b_weights, atol=1e-4):
                    best_match = vg_a
                    best_match_name = a_name
                    break
            
            if best_match and best_match_name:
                original_name = vg_b.name
                vg_b.name = best_match_name
                matched_a_groups.add(best_match_name)
                renamed_count += 1
                matches.append((original_name, best_match_name))
            else:
                matches.append((b_name, None))
        
        return {
            'renamed_count': renamed_count,
            'matches': matches,
            'total_a': len(weights_a),
            'total_b': len(weights_b)
        }
    
    def _print_detailed_results(self, obj_a, obj_b, result):
        print("\n" + "="*50)
        print(f"顶点组匹配与重命名详细结果 (A物体: {obj_a.name}, B物体: {obj_b.name}):")
        print("="*50)
        print(f"{'B物体原始名称':<30} {'重命名为':<30}")
        print("-"*75)
        
        unmatched = 0
        for b_name, a_name in result['matches']:
            if a_name:
                print(f"{b_name:<30} → {a_name:<30}")
            else:
                print(f"{b_name:<30} → {'保留原名称':<30}")
                unmatched += 1
        
        print("="*50)
        print(f"总结:")
        print(f"  A物体非空顶点组数量: {result['total_a']}")
        print(f"  B物体非空顶点组数量: {result['total_b']}")
        print(f"  匹配并重命名数量: {result['renamed_count']}")
        print(f"  未匹配数量: {unmatched}")
        print("="*50)



class O_VertexGroupsSortMatch(bpy.types.Operator):
    bl_idname = "vertex_groups.sort_match"
    bl_label = "匹配排序顶点组"
    bl_description = ("严格按照选择物体的顶点组顺序重新排列活动物体的顶点组\n"
                     "操作逻辑:\n"
                     "1. 按选择物体的顶点组顺序依次处理\n"
                     "2. 将活动物体的对应顶点组移动到匹配位置\n"
                     "3. 缺少的顶点组会新建空组\n"
                     "4. 多余的顶点组会保留在最后\n"
                     "我用来给解包的模型按提取的模型排序，方便导出时顺序正确")

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
                
            # 执行精确排序
            result = self._reorder_vertex_groups(source_obj, target_obj)
            
            self.report({'INFO'}, 
                       f"排序完成: 匹配 {result['matched']}个, "
                       f"新建 {result['added']}个, "
                       f"保留 {result['kept']}个")
            
            # 打印详细结果到控制台
            print(f"\n顶点组排序结果 [{target_obj.name} → {source_obj.name}]:")
            for i, vg in enumerate(target_obj.vertex_groups):
                prefix = "  ✓ " if vg.name in [x.name for x in source_obj.vertex_groups] else "  ✕ "
                print(f"{i+1:2d}.{prefix}{vg.name}")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
    
    def _reorder_vertex_groups(self, source_obj, target_obj):
        source_vgs = source_obj.vertex_groups
        target_vgs = target_obj.vertex_groups
        
        # 备份目标物体所有顶点组权重数据
        weight_backup = {}
        for vg in target_vgs:
            weight_backup[vg.name] = self._get_vertex_weights(target_obj, vg)
        
        # 记录已处理的顶点组
        processed = set()
        new_order = []
        added_count = 0
        
        # 第一步：按源物体顺序处理
        for src_vg in source_vgs:
            if src_vg.name in target_vgs:
                # 移动现有顶点组
                new_order.append((src_vg.name, False))
                processed.add(src_vg.name)
            else:
                # 添加新顶点组
                new_order.append((src_vg.name, True))
                added_count += 1
        
        # 第二步：添加目标物体独有的顶点组
        kept_count = 0
        for tgt_vg in target_vgs:
            if tgt_vg.name not in processed:
                new_order.append((tgt_vg.name, False))
                kept_count += 1
        
        # 重建顶点组列表
        target_vgs.clear()
        
        # 按新顺序创建顶点组并恢复权重
        for name, is_new in new_order:
            vg = target_vgs.new(name=name)
            if not is_new and name in weight_backup:
                for v_idx, weight in weight_backup[name].items():
                    vg.add([v_idx], weight, 'REPLACE')
        
        return {
            'matched': len(source_vgs) - added_count,
            'added': added_count,
            'kept': kept_count
        }
    
    def _get_vertex_weights(self, obj, vg):
        """获取顶点组中所有顶点的权重"""
        weights = {}
        mesh = obj.data
        
        for v in mesh.vertices:
            try:
                weight = vg.weight(v.index)
                if weight > 0:
                    weights[v.index] = weight
            except RuntimeError:
                pass
                
        return weights

def register():
    bpy.utils.register_class(DATA_PT_vertex_group_tools)
    bpy.utils.register_class(O_VertexGroupsCount)
    bpy.utils.register_class(O_VertexGroupsDelNoneActive)
    bpy.utils.register_class(O_VertexGroupsMatchRename)
    bpy.utils.register_class(O_VertexGroupsSortMatch)

def unregister():
    bpy.utils.unregister_class(DATA_PT_vertex_group_tools)
    bpy.utils.unregister_class(O_VertexGroupsCount)
    bpy.utils.unregister_class(O_VertexGroupsDelNoneActive)
    bpy.utils.unregister_class(O_VertexGroupsMatchRename)
    bpy.utils.unregister_class(O_VertexGroupsSortMatch)
