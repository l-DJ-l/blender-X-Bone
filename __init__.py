# type: ignore
bl_info = {
    "name" : "XBone",
    "author" : "xqfa",
    "description" : "",
    "blender" : (4, 4, 0),
    "version" : (1, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

########################## Divider ##########################
from . import panel
from .骨骼工具 import 骨骼与顶点组, 骨骼姿态操作, 骨骼编辑操作, MOD骨架替换
from .属性工具 import 顶点组, 形态键, UV贴图, 顶点色
from .其他工具 import 其他



# 注册插件
def register():
    panel.register()
    骨骼与顶点组.register()
    骨骼姿态操作.register()
    骨骼编辑操作.register()
    MOD骨架替换.register()
    顶点组.register()
    形态键.register()
    UV贴图.register()
    顶点色.register()
    其他.register()

# 注销插件
def unregister():
    panel.unregister()
    骨骼与顶点组.unregister()
    骨骼姿态操作.unregister()
    骨骼编辑操作.unregister()
    MOD骨架替换.unregister()
    顶点组.unregister()
    形态键.unregister()
    UV贴图.unregister()
    顶点色.unregister()
    其他.unregister()


if __name__ == "__main__":
    register()

