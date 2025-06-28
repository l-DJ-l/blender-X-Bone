# type: ignore
bl_info = {
    "name" : "X-Bone+",
    "author" : "xqfa",
    "description" : "",
    "blender" : (4, 4, 0),
    "version" : (1, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy
import math
from mathutils import Euler, Matrix, Vector, Quaternion 
########################## Divider ##########################
from .骨骼扩展操作 import 骨骼与顶点组, 骨骼姿态操作, 骨骼编辑操作
from .原生界面扩展 import 骨骼矩阵四元数, 顶点组, 测试
from .MOD操作 import MOD骨架替换


# 注册插件
def register():
    骨骼与顶点组.register()
    骨骼姿态操作.register()
    骨骼编辑操作.register()
    骨骼矩阵四元数.register()
    MOD骨架替换.register()
    顶点组.register()

# 注销插件
def unregister():
    骨骼与顶点组.unregister()
    骨骼姿态操作.unregister()
    骨骼编辑操作.unregister()
    骨骼矩阵四元数.unregister()
    MOD骨架替换.unregister()
    顶点组.unregister()


if __name__ == "__main__":
    register()

