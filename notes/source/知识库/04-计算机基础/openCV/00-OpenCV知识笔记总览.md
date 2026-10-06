# OpenCV 知识笔记总览

> 本目录是一套从图像矩阵基础到三维视觉、视频分析、DNN 部署和工程优化的系统学习笔记。

## 1. 版本与语言口径

- 主线版本：**OpenCV 5.x**。
- 兼容说明：保留常见 **OpenCV 4.12** API 和模块差异提示。
- Python 示例：以 Python 3、`numpy` 和 `cv2` 为主。
- C++ 示例：以 C++17 和 OpenCV 5 模块化头文件为主，同时说明 4.x 常见写法。
- 扩展模块：涉及跟踪器、条码等能力时，会明确是否需要 `opencv_contrib` 或特定构建选项。
- 后端能力：CUDA、OpenCL、Vulkan、ONNX Runtime、GUI 和编解码器是否可用，必须以当前安装包的构建信息为准。

可以用下面的代码确认运行时版本和构建能力：

```python
import cv2 as cv

print("OpenCV version:", cv.__version__)
print(cv.getBuildInformation())
```

## 2. 章节目录

| 章节 | 主要内容 | 建议基础 |
| --- | --- | --- |
| [01 环境安装与核心数据结构](01-环境安装与核心数据结构.md) | 安装、模块、`ndarray`、`cv::Mat`、颜色、坐标、I/O、ROI、掩膜 | Python/C++ 基础 |
| [02 图像处理与形态学](02-图像处理与形态学.md) | 颜色空间、滤波、梯度、边缘、阈值、直方图、形态学 | 第 1 章 |
| [03 轮廓形状与几何变换](03-轮廓形状与几何变换.md) | 轮廓、矩、凸包、Hough、仿射、透视、文档扫描 | 第 1～2 章 |
| [04 特征检测匹配与图像拼接](04-特征检测匹配与图像拼接.md) | SIFT、ORB、AKAZE、匹配、RANSAC、单应、拼接 | 第 1～3 章 |
| [05 相机标定与三维视觉](05-相机标定与三维视觉.md) | 内外参、畸变、PnP、双目、极线、视差、三角化 | 线性代数、几何 |
| [06 视频处理、光流与目标跟踪](06-视频处理光流与目标跟踪.md) | 视频 I/O、时间戳、背景建模、光流、跟踪、实时延迟 | 第 1～4 章 |
| [07 DNN 推理与模型部署](07-DNN推理与模型部署.md) | ONNX、张量、预处理、检测后处理、NMS、推理后端 | 深度学习基础 |
| [08 性能优化、工程实践与排障](08-性能优化工程实践与排障.md) | 基准、复制、并行、SIMD、OpenCL/CUDA/Vulkan、构建部署 | 任一实战项目 |
| [09 综合实战与练习路线](09-综合实战与练习路线.md) | 8 个递进项目、验收指标、调试方法、练习和术语表 | 按项目选择前章 |
| [10 传统机器学习与实用视觉模块](10-传统机器学习与实用视觉模块.md) | KNN、SVM、树模型、HOG、级联、GrabCut、二维码、图像修复 | 第 1～3 章 |

## 3. 推荐学习路线

### 3.1 图像处理基础路线

`01 → 02 → 03 → 09 中的图像批处理、颜色分割和文档扫描`

这条路线重点掌握像素数据、颜色空间、卷积、二值化、形态学、轮廓和几何变换。完成后应能够独立设计传统图像处理流水线，并通过中间结果定位参数问题。

### 3.2 特征与三维视觉路线

`01 → 02 → 03 → 04 → 05`

这条路线需要补充线性代数、齐次坐标、最小二乘和鲁棒估计知识。学习重点不是记忆函数，而是理解从像素观测到几何约束、从匹配点到相机位姿或三维结构的推导关系。

### 3.3 视频与实时系统路线

`01 → 02 → 04 → 06 → 08`

除了算法，还要关注帧率、时间戳、缓冲队列、编解码、线程和端到端延迟。实时系统的目标通常不是“单帧最快”，而是在吞吐、延迟、稳定性和资源占用之间取得平衡。

### 3.4 视觉 AI 部署路线

`01 → 02 → 07 → 08 → 09 中的 ONNX 检测项目`

需要把模型训练侧的张量定义完整迁移到部署侧，包括尺寸、颜色顺序、归一化、布局、动态形状、输出解析和坐标还原。模型能运行并不代表结果正确，必须用已知输入与训练框架结果对齐。

### 3.5 轻量传统方案路线

`01 → 02 → 03 → 10 → 08`

当数据量小、规则稳定、硬件受限或需要强可解释性时，传统特征、SVM、HOG、模板匹配和规则流水线仍然有价值。应使用独立验证集和业务指标比较传统方案与 DNN，而不是根据算法年代做选择。

## 4. 阅读代码时的统一约定

- OpenCV Python 通常使用 `import cv2 as cv`。
- 图像坐标写作 `(x, y)`，NumPy 索引写作 `image[y, x]`。
- OpenCV 彩色图默认通常是 BGR；Matplotlib 等工具通常按 RGB 显示。
- `uint8` 运算要关注饱和、截断和溢出；梯度、中间计算和归一化经常需要浮点类型。
- 任何读取操作后都应检查图像、视频帧、描述子或模型是否为空。
- 图像处理流水线应保存或显示关键中间结果，而不是只观察最终输出。
- 所有阈值、核大小、插值方法和置信度参数都应记录在配置中，并使用代表性数据验证。
- 性能优化前先测量；先确认瓶颈位于计算、内存搬运、同步、I/O 还是模型本身。

## 5. 最小运行示例

```python
from pathlib import Path
import cv2 as cv

input_path = Path("input.jpg")
image = cv.imread(str(input_path), cv.IMREAD_COLOR)
if image is None:
    raise FileNotFoundError(f"无法读取图像：{input_path.resolve()}")

gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
blurred = cv.GaussianBlur(gray, (5, 5), 0)
edges = cv.Canny(blurred, 50, 150)

output_path = Path("edges.png")
if not cv.imwrite(str(output_path), edges):
    raise OSError(f"无法写入图像：{output_path.resolve()}")

print("input:", image.shape, image.dtype)
print("output:", edges.shape, edges.dtype)
```

## 6. 学习与验证方法

1. 为每个实验保留原图、参数、OpenCV 版本和输出结果。
2. 使用合成图像验证几何、阈值和坐标逻辑，再使用真实数据测试鲁棒性。
3. 对算法参数做小范围扫描，并记录正确率、误检率、耗时和内存，而不是只凭肉眼选择。
4. 对视频和 DNN 流水线区分预处理、推理、后处理和 I/O 耗时。
5. 遇到异常先打印 `shape`、`dtype`、数值范围、通道顺序和构建信息。
6. 查阅 API 时使用与本地版本对应的官方文档，特别注意 OpenCV 4→5 的模块迁移。

## 7. 官方资料

- [OpenCV 5.0 官方文档](https://docs.opencv.org/5.0/)
- [OpenCV 4.12 官方文档](https://docs.opencv.org/4.12.0/)
- [OpenCV 官方发布页](https://opencv.org/releases/)
- [OpenCV 官方源码仓库](https://github.com/opencv/opencv)
- [OpenCV 4→5 迁移说明](https://github.com/opencv/opencv/wiki/OpenCV-4-to-5-migration)
- [opencv_contrib 官方仓库](https://github.com/opencv/opencv_contrib)

