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
from .杂项 import 顶点组,骨骼相连项,顶点组所有权重,骨架对应#,demo
from .骨骼摆正 import 姿态摆正,编辑摆正
from .骨骼变换 import 骨骼变换


# 注册插件
def register():
    顶点组.register()
    顶点组所有权重.register()
    骨骼相连项.register()
    骨架对应.register()
    #demo.register()
    姿态摆正.register()
    编辑摆正.register()
    骨骼变换.register()

# 注销插件
def unregister():
    顶点组.unregister()
    顶点组所有权重.unregister()
    骨骼相连项.unregister()
    骨架对应.unregister()
    #demo.unregister()
    姿态摆正.unregister()
    编辑摆正.unregister()
    骨骼变换.unregister()


if __name__ == "__main__":
    register()

