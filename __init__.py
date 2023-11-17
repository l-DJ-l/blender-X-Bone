bl_info = {
    "name" : "X-Bone+",
    "author" : "xqfa",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy # type: ignore
import math
from mathutils import Euler, Matrix, Vector, Quaternion # type: ignore
########################## Divider ##########################
from .杂项 import 骨骼与顶点组,MOD骨架替换#,demo
from .骨骼双模式 import 姿态模式,编辑模式
from .骨骼变换 import 骨骼变换


# 注册插件
def register():
    骨骼与顶点组.register()
    MOD骨架替换.register()
    #demo.register()
    姿态模式.register()
    编辑模式.register()
    骨骼变换.register()

# 注销插件
def unregister():
    骨骼与顶点组.unregister()
    MOD骨架替换.unregister()
    #demo.unregister()
    姿态模式.unregister()
    编辑模式.unregister()
    骨骼变换.unregister()


if __name__ == "__main__":
    register()

