# blender-X-Bone+
blender版本我不知道，反正基于3.1开发
## 提供姿态模式/编辑模式下的骨骼的相对骨架的变换信息，包含：
- 位置
- 欧拉旋转
- 四元数
- 4x4矩阵

## 在姿态模式下提供一些功能：
- 自动摆正骨骼，同时改变正交朝向
- 应用骨架和姿态
- 通过导入excel来选择骨骼
- 打印选择的骨骼名称，方便excel编辑
- 快速合并删减骨骼层

## 在编辑模式下提供一些功能：
- 自动摆正骨骼，同时改变正交朝向
- 批量解除骨骼相连

## 对骨骼和顶点组的一些操作：
- 删除无任何权重的顶点组
- 对于选定的物体和骨架
  - 删除选择骨骼中无对应顶点组的骨骼
  - 删除顶点组中无对应骨骼的顶点组
- 对于有权重骨骼（顶点组）添加/移除 骨骼编号

## 便于moder使用的骨架替换的分解流程（灵感来自小威廉伯爵）：
- 简化骨骼：excel中的第一行作为标题将不会被读取，选择主要的躯干骨、物理骨，一些需要特殊对待的合并骨和被合并骨，其余骨骼将会被合并至父级，此功能调用cats实现
- 复制位置：excel中的第一行作为标题将不会被读取，源骨架将会复制目标骨架的位置，请让两个骨架尽量形态一致（如T字）以减少旋转偏移，如需要旋转跟踪，请手动约束添加
- 重命名换绑：excel中的第一行作为标题将不会被读取，源物体顶点组将会重命名为目标骨架，并绑定至目标骨架，可以选择保留物理骨
