# 第 7 章 DNN 推理与模型部署

本章讨论 OpenCV 的 `cv.dnn` 模块：它不是训练框架，而是面向部署的深度神经网络推理组件。它读取训练框架导出的模型，把图像整理成网络需要的张量，执行前向推理，再把输出张量还原为分类、检测或分割结果。学习重点是输入张量形状、预处理一致性、坐标还原、置信度和 NMS。

官方第一方资料入口：OpenCV DNN 模块文档、DNN engine selection、`cv::dnn::Net`、`blobFromImage`、`NMSBoxes`、`getPerfProfile`、OpenCV 5.0 迁移说明和 DNN 后端/目标枚举。OpenCV 5 文档区分新的 DNN engine 与 4.x classic engine，并列出 CPU/OpenCL/CUDA/Vulkan/ONNX Runtime 等路径；实际可用后端取决于构建，不能只凭枚举常量判断。

## 1. cv.dnn 的定位

传统 OpenCV 算法通常直接处理 `Mat`：边缘、轮廓、特征点、几何变换的中间结果都能用图像或点集解释。DNN 模型内部则是张量计算图，节点包括卷积、归一化、激活、矩阵乘法、上采样、重排、检测头或分割头。`cv.dnn` 把这些计算封装成统一的 `Net`，让 OpenCV 工程不用引入完整训练框架就能执行推理。

它适合部署端推理、原型验证、传统视觉和深度模型混合流水线。它不负责训练、数据增强、反向传播、优化器或自动微分。微调模型应使用训练框架；在 OpenCV 5 工程中主讲 ONNX、TFLite、TensorFlow/OpenVINO IR 等当前支持路径，并完成前处理、推理、后处理。Caffe 和 Darknet parser 属于 OpenCV 4.12 classic DNN engine 的历史兼容路径，不应作为 OpenCV 5 新项目的可用主线。

OpenCV 4.12 的常见体验是 classic DNN engine：`readNet` 读入模型，设置后端和目标，`setInput` 后 `forward`。OpenCV 5 官方文档引入新的 DNN engine，面向更现代的图表示、动态形状和外部执行后端集成。兼容代码仍应先检测版本和构建信息，再设置可用后端。

## 2. ONNX 导入与 Net 生命周期

ONNX 是常用中间模型格式。训练端将 PyTorch 或其他框架模型导出为 `.onnx`，部署端用 `cv.dnn.readNetFromONNX(path)` 或通用 `cv.dnn.readNet(path)` 加载。它把网络结构和权重放在一个文件中，并能表达多数现代视觉模型的推理计算图。

`Net` 的生命周期可以分成五步：加载模型、选择后端和目标、准备输入 blob、执行 forward、解释输出。最小调用链是 `readNetFromONNX`、`setPreferableBackend`、`setPreferableTarget`、`setInput`、`forward`。但输入尺寸、`1/255`、RGB/BGR 和均值必须来自训练时的预处理说明。预处理错了，推理通常不会报错，只会输出低置信度、类别混乱或坐标漂移。

## 3. 张量形状：从 HWC 到 NCHW

OpenCV 读入彩色图像后，Python 中 `img.shape` 通常是 `(H, W, C)`，即高度、宽度、通道，通道顺序是 BGR。大多数卷积网络输入是 `(N, C, H, W)`，即批量、通道、高度、宽度。`blobFromImage` 的核心作用就是把一张或多张图像转换成 4 维 blob。单张 `640x640` 彩色图经过转换后通常是 `(1, 3, 640, 640)`。

四个维度的语义必须固定：`N` 是 batch size；`C` 是通道数，灰度为 1，RGB/BGR 为 3；`H` 和 `W` 是网络输入空间尺寸，不一定等于原图尺寸。很多错误来自把 `(x, y)` 与 `(row, col)`、`W/H` 与 `H/W` 混用。OpenCV 图像 shape 是 `(height, width)`，而 `blobFromImage(size=(w, h))` 的 `size` 参数写成 `(width, height)`。

输出张量没有统一形状，因为不同模型头部不同。分类常见输出是 `(1, num_classes)`；检测可能输出 `(1, num_boxes, 4 + num_classes)`、`(1, anchors, attributes)`、多个尺度特征图，或已解码候选框；分割可能输出 `(1, num_classes, mask_h, mask_w)` 或 `(1, 1, mask_h, mask_w)`。后处理第一步是打印每个输出的 `shape`、`dtype`、最小最大值和样本，确认它到底表示什么。

## 4. 预处理：缩放、均值、通道与布局

`blobFromImage` 的计算可以近似理解为：先 resize/crop 到目标尺寸，再按通道减均值，乘缩放系数，必要时交换 B/R 通道，最后从 HWC 转成 NCHW。常见参数：

- `scalefactor`：像素缩放。图像原始值是 `0~255`，许多模型训练时使用 `1/255` 归一化到 `0~1`，也有模型保持 `0~255` 或使用 `1/127.5`。
- `mean`：逐通道均值。若训练使用 ImageNet 归一化，要确认均值是在 `0~255` 空间还是 `0~1` 空间，并确认通道顺序。
- `swapRB`：OpenCV 读图是 BGR，许多训练框架用 RGB。若训练端是 RGB，通常设为 `True`；若模型本身按 BGR 训练，设为 `False`。
- `size`：网络输入尺寸。固定输入模型必须匹配导出尺寸；动态输入模型也可能有 stride 对齐要求，例如高宽是 32 的倍数。
- `crop`：为 `True` 时会按短边缩放再中心裁剪，常用于分类；检测和分割通常不希望中心裁剪，因为它会改变坐标覆盖范围，更多使用直接 resize 或 letterbox。

工程上建议把预处理写成单独函数，并把原图尺寸、缩放比例、padding、输入尺寸一并返回。后处理需要这些信息把模型坐标还原到原图。

## 5. 分类后处理

分类是最简单的输出解释。假设输出为 `(1, K)`，第 `k` 个数是类别分数。这个分数可能是 softmax 之后的概率，也可能是 logits。若模型末尾已经包含 softmax，就直接取最大值；若没有 softmax，可在后处理里计算：

```python
scores = np.asarray(outs[0]).reshape(-1)
exp = np.exp(scores - scores.max())
prob = exp / exp.sum()
class_id = int(prob.argmax())
confidence = float(prob[class_id])
```

如果模型用于多标签分类，不能用 softmax，因为多个类别可以同时成立，应对每个类别使用 sigmoid，并按阈值筛选。多分类是“选一个”，多标签是“每个类别独立判断”。

分类模型常用中心裁剪，输出没有坐标还原问题；若把分类结果叠加到原图上，要记住 OpenCV 文字坐标是左下角基线位置，颜色是 BGR。

## 6. 检测后处理：框、置信度与坐标还原

目标检测输出通常由候选框、目标性分数和类别分数组成。通用候选可以抽象为：

```text
box = (cx, cy, w, h) 或 (x1, y1, x2, y2)
objectness = 这个候选是否含目标
class_scores = 每个类别的条件分数
confidence = objectness * max(class_scores)  或 直接使用模型给出的类别置信度
class_id = argmax(class_scores)
```

不同模型对置信度的定义不同。有的输出 `objectness` 和 `class_scores`，最终置信度常取乘积；有的输出已经是每类最终分数；有的输出框和类别分开。写后处理必须先看模型说明和输出 shape，不能把所有检测头都当成一种格式。

坐标还原是检测部署的核心。若预处理是直接把原图 `orig_w x orig_h` resize 到 `input_w x input_h`，模型输出坐标在输入图尺度中，则：

```python
scale_x = orig_w / input_w
scale_y = orig_h / input_h
x1_orig = x1_input * scale_x
y1_orig = y1_input * scale_y
x2_orig = x2_input * scale_x
y2_orig = y2_input * scale_y
```

若输出是归一化坐标 `0~1`，应先乘输入尺寸或直接乘原图尺寸，取决于归一化是相对输入图还是原图。若输出是 `(cx, cy, w, h)`，先转成角点：

```python
x1 = cx - w / 2
y1 = cy - h / 2
x2 = cx + w / 2
y2 = cy + h / 2
```

若预处理使用 letterbox，即保持长宽比缩放后在两边补边，不能只用 `orig_w / input_w`。应保存缩放比例 `r = min(input_w / orig_w, input_h / orig_h)`，以及左右/上下 padding：

```python
new_w, new_h = round(orig_w * r), round(orig_h * r)
pad_x = (input_w - new_w) / 2
pad_y = (input_h - new_h) / 2

x1_orig = (x1_input - pad_x) / r
y1_orig = (y1_input - pad_y) / r
x2_orig = (x2_input - pad_x) / r
y2_orig = (y2_input - pad_y) / r
```

还原后要裁剪到图像边界：`x` 限制在 `[0, orig_w - 1]`，`y` 限制在 `[0, orig_h - 1]`。画框时使用整数坐标，但计算 NMS 前最好保留浮点，避免小目标因过早取整而 IoU 失真。

## 7. NMS：从很多候选到最终框

检测模型常会对同一个目标输出多个相近框。NMS（非极大值抑制）的目标是保留高置信度框，删除与它高度重叠的低置信度框。流程是按置信度降序排序，取最高分框，计算它与剩余框的 IoU，抑制 IoU 大于阈值的低分框，再继续处理下一个未被抑制框。

IoU 是两个框交集面积除以并集面积。阈值越低，抑制越严格，漏检风险更高；阈值越高，重复框保留更多。常见起点是 `score_threshold=0.25~0.5`、`nms_threshold=0.45~0.6`，但这不是定律。密集小目标场景需要更谨慎，过低 NMS 阈值会把相邻目标误删。

OpenCV 提供 `cv.dnn.NMSBoxes`：

```python
boxes = []        # [x, y, w, h]，通常是原图坐标
confidences = []  # float
class_ids = []

indices = cv.dnn.NMSBoxes(
    bboxes=boxes,
    scores=confidences,
    score_threshold=0.35,
    nms_threshold=0.50,
)

for i in np.array(indices).reshape(-1):
    x, y, w, h = boxes[int(i)]
    cls = class_ids[int(i)]
    conf = confidences[int(i)]
```

类别相关 NMS 与类别无关 NMS要分清。类别相关 NMS 是每个类别内部单独抑制，适合多数通用检测；类别无关 NMS 把所有类别混在一起，可能把重叠但不同类别的对象误删。没有 batched NMS 接口时，可以按 `class_id` 分组调用 `NMSBoxes`。

## 8. 分割后处理

语义分割输出常是 `(1, C, Mh, Mw)`，每个像素位置有 `C` 个类别分数。后处理通常沿类别维取 `argmax` 得到类别图，再 resize 回原图：

```python
logits = outs[0][0]              # C, Mh, Mw
mask_small = logits.argmax(axis=0).astype(np.uint8)
mask = cv.resize(mask_small, (orig_w, orig_h), interpolation=cv.INTER_NEAREST)
```

二分类分割可能输出 `(1, 1, Mh, Mw)`，每个位置是前景 logit 或概率。如果是 logit，需要 sigmoid 后再阈值化；如果已是概率，可直接 `prob > threshold`。分割 resize 必须注意插值：类别 ID 图用最近邻，概率图可以用线性插值后再阈值化。若预处理使用 letterbox，还要先去掉 padding 区域，再缩放回原图，否则边缘会偏移。

实例分割比语义分割多一步：每个检测框对应一个 mask 原型或小 mask，需要按框裁剪、缩放、阈值并贴回原图。原则仍是先弄清输出张量含义，再按预处理记录还原坐标。

## 9. 动态形状与批处理

OpenCV 5 新 DNN engine 更强调动态形状支持，但模型、算子、后端和构建选项共同决定它能否工作。动态输入不等于任意尺寸都安全。很多视觉模型有 stride 约束，输入高宽需要是 8、16 或 32 的倍数；有些 ONNX 图虽然标了动态维度，内部常量仍隐含固定尺寸。

批处理把输入从 `(1, C, H, W)` 变成 `(N, C, H, W)`。`blobFromImages` 可以把多张同尺寸预处理后的图组成一个 batch。批处理能提高吞吐，但会增加延迟和显存/内存占用；实时摄像头场景常更关心单帧延迟。后处理必须按 batch 维拆开输出，不能把所有候选框混在一起做 NMS。

动态形状调试建议：先用固定示例尺寸跑通；再只改变 batch；最后改变空间尺寸。每次改变后打印输入 blob shape、输出 shape 和前向耗时。如果某个后端失败，先切回 CPU/OpenCV 后端验证模型语义，再判断是模型不兼容还是加速后端限制。

## 10. 后端与目标：能力取决于构建

OpenCV 5 先在加载模型时选择 DNN engine，再用 `setPreferableBackend` 和 `setPreferableTarget` 选择 classic/ORT 能使用的执行后端与设备。engine 不能在 `Net` 加载后切换；要换 engine 必须用新的 `engine=` 参数重新加载模型。`ENGINE_NEW` 是 OpenCV 5 的新引擎，5.0 中只支持 CPU；CUDA 应使用 `ENGINE_CLASSIC` 再设置 CUDA backend/target；ONNX Runtime 应使用 `ENGINE_ORT`，并要求构建时 `WITH_ONNXRUNTIME=ON`。CPU 是最可靠的基线。OpenCL 依赖 OpenCV 的 OpenCL 支持和可用设备；CUDA 需要 OpenCV 使用 CUDA、cuDNN 等组件编译；Vulkan 需要 Vulkan 后端和运行环境；ONNX Runtime 要看 OpenCV 是否启用对应集成。

常见写法：

```python
print(cv.__version__)
print(cv.getBuildInformation())

net = cv.dnn.readNetFromONNX("model.onnx", engine=cv.dnn.ENGINE_NEW)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

# CUDA 需要重新加载为 classic engine，不能在上面的 net 上切换 engine。
cuda_net = cv.dnn.readNetFromONNX("model.onnx", engine=cv.dnn.ENGINE_CLASSIC)
cuda_net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
cuda_net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)

# ORT 需要 OpenCV 构建时 WITH_ONNXRUNTIME=ON。
ort_net = cv.dnn.readNetFromONNX("model.onnx", engine=cv.dnn.ENGINE_ORT)
```

不要把“Python 中有常量”理解为“当前机器可执行该 engine 或后端”。正确验证方式是打印构建信息、用目标 engine 重新加载模型、设置后端/目标、跑最小输入、记录完整错误。生产部署应在启动时 warmup 和健康检查，失败时降级到 CPU 或停止服务。

OpenCV 5 与 4.12 的实用差异可以这样记：4.12 的稳定主线是 classic DNN engine、OpenCV 后端以及 Caffe/Darknet 等历史 parser；5.0 引入新的 DNN engine、更多动态形状和外部后端集成方向，并将 ONNX Runtime 纳入官方 DNN 说明。课程代码应优先写成“ONNX/TFLite 当前格式 + CPU 可运行 + 可选加速后端”的结构。

## 11. 性能计时

DNN 推理计时要分清预处理、前向、后处理和可视化。`net.getPerfProfile()` 取得网络层级计时信息，适合分析前向阶段；端到端延迟则用 `time.perf_counter()` 包住完整流水线。

```python
import time

for _ in range(3):  # warmup
    net.setInput(blob)
    net.forward()

t0 = time.perf_counter()
net.setInput(blob)
out = net.forward()
t1 = time.perf_counter()

ticks, layer_times = net.getPerfProfile()
freq = cv.getTickFrequency()
print(f"forward wall time: {(t1 - t0) * 1000:.2f} ms")
print(f"dnn profile time: {ticks / freq * 1000:.2f} ms")
```

第一次推理可能包含图初始化、内存分配、内核选择或后端编译，不能代表稳定性能。评估时先 warmup，再统计多次均值、P50、P95。实时系统还要统计采集、解码、显示和队列等待时间。

## 12. 通用 Python ONNX 推理骨架

下面骨架刻意不绑定单个模型，只保留分类、检测、分割都需要的结构。真实项目应把 `decode_outputs` 按模型输出格式补完。

```python
import cv2 as cv
import numpy as np


def make_blob(img, input_size):
    h, w = img.shape[:2]
    blob = cv.dnn.blobFromImage(
        img, 1.0 / 255.0, input_size, (0, 0, 0), swapRB=True, crop=False
    )
    meta = {
        "orig_size": (w, h),
        "input_size": input_size,
        "scale_x": w / input_size[0],
        "scale_y": h / input_size[1],
    }
    return blob, meta


def decode_outputs(outputs, meta, score_thr=0.35, nms_thr=0.50):
    # 按模型说明解析 outputs。这里演示检测后处理的公共收口。
    boxes, scores, class_ids = [], [], []

    # 在此处按模型说明解码为输入图坐标中的 x1,y1,x2,y2/conf/class_id。
    decoded = []

    sx, sy = meta["scale_x"], meta["scale_y"]
    for x1, y1, x2, y2, conf, cls in decoded:
        if conf < score_thr:
            continue
        ox1, oy1 = x1 * sx, y1 * sy
        ox2, oy2 = x2 * sx, y2 * sy
        x = max(0, int(round(ox1)))
        y = max(0, int(round(oy1)))
        w = max(0, int(round(ox2 - ox1)))
        h = max(0, int(round(oy2 - oy1)))
        boxes.append([x, y, w, h])
        scores.append(float(conf))
        class_ids.append(int(cls))

    keep = cv.dnn.NMSBoxes(boxes, scores, score_thr, nms_thr)
    keep = np.array(keep).reshape(-1) if len(keep) else []
    return [(boxes[i], scores[i], class_ids[i]) for i in keep]


net = cv.dnn.readNetFromONNX("model.onnx")
net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

img = cv.imread("image.jpg")
if img is None:
    raise RuntimeError("failed to read image")

blob, meta = make_blob(img, (640, 640))
net.setInput(blob)
outputs = net.forward(net.getUnconnectedOutLayersNames())
results = decode_outputs(outputs, meta)
```

## 13. 关键 C++ 对照

C++ 端的结构与 Python 一致，只是类型更显式：

```cpp
#include <opencv2/dnn.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>
#include <iostream>
#include <vector>

int main() {
    cv::dnn::Net net = cv::dnn::readNetFromONNX("model.onnx");
    net.setPreferableBackend(cv::dnn::DNN_BACKEND_OPENCV);
    net.setPreferableTarget(cv::dnn::DNN_TARGET_CPU);

    cv::Mat img = cv::imread("image.jpg");
    if (img.empty()) {
        std::cerr << "failed to read image\n";
        return 1;
    }

    cv::Size inputSize(640, 640);
    cv::Mat blob = cv::dnn::blobFromImage(
        img, 1.0 / 255.0, inputSize, cv::Scalar(), true, false
    );

    net.setInput(blob);
    std::vector<cv::Mat> outs;
    net.forward(outs, net.getUnconnectedOutLayersNames());

    std::vector<cv::Rect> boxes;
    std::vector<float> scores;
    std::vector<int> keep;
    cv::dnn::NMSBoxes(boxes, scores, 0.35f, 0.50f, keep);

    double freq = cv::getTickFrequency();
    std::vector<double> layerTimes;
    int64 ticks = net.getPerfProfile(layerTimes);
    std::cout << "DNN profile: " << ticks / freq * 1000.0 << " ms\n";
    return 0;
}
```

C++ 部署还要关注动态库路径、运行时依赖和编译选项。OpenCV 5 要求 C++17；如果使用 CUDA、Vulkan、ONNX Runtime 等能力，还要确保编译期和运行期依赖可见。

## 14. 模型兼容诊断

模型导入失败时，先不要急着改代码。按顺序检查：ONNX 是否能被训练框架加载；模型 opset 是否过新；是否包含 OpenCV DNN 或当前后端不支持的算子；输入名称、输入数量、动态维度是否符合预期；权重文件是否完整；路径是否正确。

运行失败常见现象：`readNetFromONNX` 报 parse error，说明导入阶段不兼容；`forward` 报 shape error，常见于输入尺寸、动态维度或 reshape 常量不匹配；输出全是 NaN 或极端值，常见于预处理错、精度后端不兼容或模型导出问题；CPU 能跑而 CUDA/OpenCL/Vulkan 跑不了，通常是加速后端算子覆盖或构建问题。

最低成本的诊断脚本应打印：`cv.__version__`、`cv.getBuildInformation()`、模型路径、输入 blob shape/dtype/min/max、输出张量数量和每个输出 shape/dtype/min/max、后端/目标设置、完整异常文本。

## 15. 传统视觉 + DNN 混合流水线

OpenCV 的优势不是只跑 DNN，而是把传统视觉和 DNN 组合。常见方案：用 ROI、运动检测或颜色阈值缩小候选区域后分类；用 DNN 检测目标，再用光流或跟踪器在中间帧追踪；用分割模型得到粗 mask，再用形态学、轮廓和几何约束清理边界；先校正畸变再检测，减少坐标误差。

混合流水线的关键是维护坐标链。每次裁剪、缩放、旋转、透视变换都要保存从局部坐标回到原图或世界坐标的映射。对 ROI 跑检测时，输出框先还原到 ROI 坐标，再加 ROI 左上角偏移，最后才是原图坐标。

## 16. 部署清单

部署前至少检查这些项：模型版本固定；输入尺寸、缩放、均值、通道顺序有文档；输出 shape 和后处理写入单元测试；标签顺序一致；坐标还原覆盖 direct resize 和 letterbox；NMS 和置信度阈值可配置；CPU 路径可运行；加速后端有自检和降级；延迟、吞吐和内存峰值有记录；错误日志含版本、构建信息、模型路径和输出 shape；服务启动时 warmup；异常图像、空图、灰度图、超大图都有边界处理。

交付到不同机器时，必须记录 OpenCV 版本、构建方式、第三方依赖、模型 opset、设备驱动版本和系统架构。很多 DNN 部署问题不是算法错误，而是训练端假设、导出端图结构、运行端构建能力没有对齐。

## 17. 常见错误排查

第一，颜色反了。表现为分类结果离谱、检测置信度很低。检查 `swapRB`、均值通道顺序和训练端输入。

第二，输入尺寸错。固定输入模型可能直接报 shape error；动态模型可能能跑但输出无意义。先使用训练或导出文档中的标准尺寸。

第三，坐标还原错。框整体偏右、偏下、变宽或变窄，通常是把 `H/W`、`x/y`、padding 或 letterbox 比例弄错。打印一张带网格的测试图最容易定位。

第四，NMS 误删。相邻目标消失时降低抑制强度或改成按类别 NMS；重复框太多时提高 score 阈值或降低 NMS 阈值。

第五，CPU 能跑，GPU 后端失败。先确认 `getBuildInformation()` 中确实启用了目标后端，再查错误算子。不要把 PyPI wheel 默认视为 CUDA/Vulkan/ORT 构建。

第六，输出解析套错模型。不同检测头输出字段顺序不同，不能凭 “第 5 位是 objectness” 之类经验硬套。打印 shape 和样本值，回到模型官方说明核对。

## 18. 练习

1. 编写脚本加载任意 ONNX 分类模型，打印输入 blob shape、输出 shape、top-5 类别分数，并比较是否需要 softmax。
2. 构造一张 `1280x720` 图，分别用 direct resize 和 letterbox 映射一个已知框到 `640x640`，再还原回原图，验证误差。
3. 手写 IoU 和简单 NMS，再与 `cv.dnn.NMSBoxes` 的结果对比，观察阈值变化。
4. 对一个分割输出张量分别用最近邻和线性插值还原 mask，比较边缘类别是否被污染。
5. 打印 `cv.getBuildInformation()`，记录本机 DNN 后端、OpenCL、CUDA、Vulkan、ONNX Runtime 相关信息，并写出可用性结论。
6. 设计一个“运动检测筛 ROI + DNN 分类”的流水线，说明每个 ROI 如何映射回原图坐标。

## 19. 本章小结

`cv.dnn` 的主线不是“调用 forward 就结束”，而是模型导入、预处理、推理、后处理、诊断、部署组成的链路。输入张量形状决定模型是否能跑，预处理决定结果是否可信，坐标还原决定检测和分割是否能落回原图，置信度和 NMS 决定最终输出是否稳定。OpenCV 5 带来新的 DNN engine 和更丰富的后端方向，但工程代码仍要以当前构建为准：CPU 基线先跑通，再逐步启用 OpenCL、CUDA、Vulkan 或 ONNX Runtime。

## 20. 官方参考链接

- OpenCV DNN module：https://docs.opencv.org/5.x/d6/d0f/group__dnn.html
- OpenCV 5 DNN engine selection：https://docs.opencv.org/5.0/main_modules/dnn_engine_selection.html
- OpenCV DNN samples and model zoo：https://docs.opencv.org/5.x/d4/db9/samples_2dnn_2README_8md.html
- `cv::dnn::Net` class：https://docs.opencv.org/5.x/db/d30/classcv_1_1dnn_1_1Net.html
- Image blob helpers：https://docs.opencv.org/5.x/d6/d0f/group__dnn.html
- OpenCV 5.0 transition guide：https://docs.opencv.org/5.0/tutorials/introduction/transition_guide/transition_guide.html
- Legacy OpenCV 3.0 transition guide：https://docs.opencv.org/4.12.0/db/dfa/tutorial_transition_guide.html
