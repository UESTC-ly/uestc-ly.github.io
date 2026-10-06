# Quantization 详解与实操教程

## 1. 这篇文档讲什么

你提到的 `quanzition`，在大模型工程里通常指的是 `quantization`。

中文一般翻译为：

- 量化
- 模型量化
- 低比特量化

如果你最近在看大模型部署、显存优化、本地推理或者 `QLoRA`，几乎一定会遇到这个词。

很多资料会直接给你一段代码：

- `load_in_8bit=True`
- `load_in_4bit=True`
- `GPTQ`
- `AWQ`
- `GGUF`

但如果没有先建立一张完整地图，你很容易出现这些困惑：

- 量化到底是在压什么
- 它和微调是不是一回事
- 4-bit、8-bit、INT4、NF4 到底有什么关系
- `bitsandbytes`、`GPTQ`、`AWQ`、`GGUF`、`HQQ` 分别适合什么场景
- 为什么有的量化适合训练，有的只适合推理

这篇文档的目标，是先把这些问题讲清楚，再给你一条可执行的工程路线。

读完后，你应该能回答：

- 什么是 quantization
- 为什么量化能显著降低显存和存储成本
- 量化有哪些主流路线，它们的边界是什么
- 什么时候该用 `bitsandbytes`
- 什么时候该用 `GPTQ` 或 `AWQ`
- 什么时候该用 `GGUF + llama.cpp`
- 如何从“我只有一张消费级显卡”出发，选对自己的方案

一句话先给结论：

> `Quantization` 的本质，是把模型参数从高精度表示压缩成更低精度表示，以更少的显存、存储和带宽成本完成推理，必要时也为低成本微调创造条件。

---

## 2. 什么是 Quantization

先从最朴素的定义开始。

神经网络里的权重，本来通常用高精度浮点数表示，比如：

- `FP32`
- `FP16`
- `BF16`

这些表示方式精度高，但也更占内存。

量化做的事，就是把这些高精度数，映射到更低精度的表示里，比如：

- `INT8`
- `INT4`
- `NF4`
- 更激进的 `3-bit`、`2-bit`

这样做的直接结果是：

- 模型更小
- 显存占用更低
- 内存带宽压力更小
- 推理速度通常更快

你可以把它理解成：

- 原始模型：用“高清格式”存参数
- 量化模型：用“压缩格式”存参数

关键在于：

> 压缩之后，模型还能不能保持足够可用的质量。

这就是量化方法之间真正竞争的地方。

---

## 3. 为什么大模型这么依赖量化

在小模型时代，全精度部署往往还能接受。

但到了大模型时代，参数量一上去，问题立刻变得现实。

例如一个 `7B` 模型，如果用 `FP16` 存储：

- 每个参数约 2 字节
- 总大小大约 `14 GB`

这还只是“权重本体”。

如果你要运行推理，还要考虑：

- KV Cache
- 中间激活
- 框架额外开销
- batch 带来的显存增长

这意味着很多情况下：

- `7B` 模型对普通显卡已经不轻松
- `13B`、`30B`、`70B` 更是很快超出消费级显卡上限

量化的价值，就在这里非常直接：

- `8-bit` 大约把权重内存减半
- `4-bit` 大约把权重内存降到原来的四分之一

举个非常直观的数量级：

| 精度 | 7B 模型权重大致体积 |
|------|---------------------|
| FP16 | 14 GB |
| INT8 | 7 GB |
| INT4 | 3.5 GB |

这还没算不同方法的元数据开销，但数量级基本就是这个意思。

所以量化不是“可选优化”，而是很多部署场景里的前置条件。

---

## 4. 量化到底压缩了什么

很多初学者会把“量化”理解成“把整个模型都变成整数”。

这个理解太粗了。

更准确的说法是：

> 量化是在用更少 bit 数去近似表示模型里的数值信息。

通常最常见的是量化下面这些内容：

- 权重 `weights`
- 有时也包括激活 `activations`
- 极少数场景会进一步碰缓存或优化器状态

在大模型工程里，最常见的是：

- **权重量化**：最主流
- **权重为主，计算保留更高精度**：非常常见

也就是说，工程里大量方案并不是“所有计算都用 4-bit”。

更常见的做法是：

- 权重以 4-bit 存储
- 真正矩阵乘法时，用更高精度做一部分计算
- 最终在“存储成本”和“计算稳定性”之间取平衡

这也是为什么你会同时看到这些词：

- `weight-only quantization`
- `compute dtype`
- `dequantization`
- `mixed precision`

---

## 5. 理解量化，先区分 4 个核心概念

### 5.1 比特宽度

这是最直观的指标。

- `8-bit`：压缩较温和，质量通常更稳
- `4-bit`：压缩更激进，是当前大模型工程里的高频甜点位
- `3-bit` / `2-bit`：更省，但更容易掉质量

### 5.2 量化对象

你是在量化：

- 权重
- 激活
- 两者都量化

大模型部署里，最常见的是“只量化权重”。

### 5.3 量化时机

这是一个很重要的分类。

- **训练后量化** `PTQ, Post-Training Quantization`
- **量化感知训练** `QAT, Quantization-Aware Training`

目前 LLM 工程中，你最常见到的是 **PTQ**。

因为：

- 成本低
- 操作简单
- 适合直接把已有大模型压缩后部署

### 5.4 量化格式和生态

这是最容易混淆的一点。

有些词是“方法”，有些词是“工具链或格式”。

例如：

- `GPTQ`：量化方法
- `AWQ`：量化方法
- `HQQ`：量化方法
- `GGUF`：更像是文件格式与生态路线
- `bitsandbytes`：更像是工程库与运行时集成方案

所以它们不是同一层级的概念，不能完全并列理解。

---

## 6. 为什么量化后模型还能工作

这是最值得建立直觉的部分。

表面上看，量化是“丢精度”。

那为什么模型没有直接坏掉？

核心原因有三个。

### 6.1 神经网络对小扰动往往有一定鲁棒性

模型参数不是每一位小数都同等重要。

很多权重即使被近似，模型整体功能仍然能维持。

### 6.2 参数分布里存在冗余

大模型参数量极大，其中很多参数对最终输出的影响并不是线性决定性的。

这意味着：

- 允许适度近似
- 允许局部误差
- 只要关键结构保住，整体能力就能保住

### 6.3 好的量化方法不是“瞎压”

像 `GPTQ`、`AWQ` 这类方案，并不是粗暴地把所有权重统一压成低精度。

它们会尽量做这些事：

- 分组量化
- 根据误差或激活重要性决定怎么压
- 给不同组使用不同缩放参数
- 尽量保护更敏感的权重

所以真正的工程问题不是：

“能不能量化”

而是：

“用什么方法量化，才能在你当前硬件和任务目标下最划算”

---

## 7. Quantization 和 Fine-Tuning 是什么关系

这也是最容易被混淆的地方。

先给一句非常重要的话：

> 量化不等于微调。

两者解决的问题不同。

### 7.1 微调解决什么

微调是在改模型能力：

- 让模型适配新任务
- 让模型适配新领域
- 让模型学会新的输出风格

### 7.2 量化解决什么

量化是在压缩部署成本：

- 更省显存
- 更省存储
- 更方便推理

### 7.3 为什么它们经常一起出现

因为像 `QLoRA` 这样的路线会把两者连起来：

- 先把基础模型做 4-bit 加载
- 再在这个低成本底座上挂 LoRA adapter 训练

也就是说：

- 基座模型：量化后冻结
- 新增参数：继续训练

这就是为什么你在学习 PEFT 时，会频繁看到量化。

但概念上一定要分开：

- `LoRA` 是微调方法
- `Quantization` 是压缩/部署方法
- `QLoRA` 是把二者结合起来的工程路径

---

## 8. 主流量化路线总览

先给你一张大图。

| 路线 | 核心定位 | 最适合的场景 |
|------|----------|--------------|
| `bitsandbytes` | 最容易接入 Hugging Face 的 8-bit/4-bit 方案 | 快速上手、受限显存推理、QLoRA |
| `GPTQ` | 经典训练后 4-bit 权重量化 | NVIDIA GPU 推理、已有量化模型生态 |
| `AWQ` | 关注激活重要性的 4-bit 量化 | 指令模型、聊天模型、生产推理、vLLM |
| `GGUF` | `llama.cpp` 生态的量化格式与部署路线 | CPU、本地推理、Apple Silicon、Ollama/LM Studio |
| `HQQ` | 无需校准数据的快速量化方案 | 需要快速实验、没有校准集、尝试极低比特 |

下面逐个讲。

---

## 9. bitsandbytes：最适合入门和 QLoRA 的路线

`bitsandbytes` 的特点不是“理论最强”，而是“工程接入最顺手”。

它非常适合这些场景：

- 你已经在用 Hugging Face `transformers`
- 你想快速把模型降到 `8-bit` 或 `4-bit`
- 你显卡不够大，但想先跑起来
- 你准备做 `QLoRA`

### 9.1 它的核心优势

- 接入简单
- 生态成熟
- 适合直接 `from_pretrained`
- 非常适合和 `PEFT` 联合使用

### 9.2 它最典型的两种模式

#### 8-bit

特点：

- 压缩幅度温和
- 质量通常更稳
- 比 4-bit 更保守

#### 4-bit

特点：

- 更省显存
- 是 `QLoRA` 的基础路线
- 通常会配合 `NF4` 和更高精度计算 dtype

### 9.3 一个最小 4-bit 加载示例

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

model_name = "meta-llama/Llama-2-7b-hf"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
```

这段代码背后的意思是：

- 权重以 4-bit 形式加载
- 计算时仍保留更稳定的高精度 dtype
- `nf4` 是 4-bit 下常见的推荐量化类型

### 9.4 bitsandbytes 最适合什么时候

如果你满足下面任意一点，优先从它开始：

- 想最快理解“量化到底怎么用”
- 想在 Hugging Face 体系里少折腾
- 想做 `QLoRA`
- 只想先把 7B/13B 模型塞进显卡里

---

## 10. GPTQ：经典的训练后 4-bit 量化

`GPTQ` 可以理解成“大模型 4-bit PTQ 时代的重要代表方案”。

它的核心思路是：

- 对权重做分组量化
- 尽量最小化量化误差
- 在较低 bit 数下保持尽可能好的精度

### 10.1 你需要抓住的关键词

- `Post-Training Quantization`
- `group-wise quantization`
- `4-bit`
- 面向推理部署

### 10.2 它适合什么场景

- 你要把模型压成高质量的 4-bit 推理版本
- 你主要在 NVIDIA GPU 上运行
- 你会使用已有的 GPTQ 量化模型
- 你更关注“推理部署质量”而不是“最简单接入”

### 10.3 GPTQ 的核心直觉

不是所有权重都必须用同一个尺度去压。

所以 GPTQ 常做的事是：

- 把一大块权重矩阵切成很多组
- 每组单独量化
- 通过误差最小化思路，尽量减少精度损失

### 10.4 为什么很多资料会提 `group_size=128`

因为它往往是一个工程上比较均衡的默认值：

- 精度还不错
- 速度也比较合适
- 生态支持广

组太小：

- 精度可能更好
- 但额外开销更高

组太大：

- 速度可能更快
- 但量化误差更容易变大

### 10.5 一个典型加载示例

```python
from transformers import AutoTokenizer
from auto_gptq import AutoGPTQForCausalLM

model_name = "TheBloke/Llama-2-7B-Chat-GPTQ"

model = AutoGPTQForCausalLM.from_quantized(
    model_name,
    device="cuda:0",
    use_triton=False,
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
```

### 10.6 GPTQ 适合什么时候优先考虑

当你想要的是：

- 经典 4-bit 权重量化
- 较成熟的量化模型分发生态
- 面向 GPU 的高质量推理

那么 GPTQ 是一个很自然的选择。

---

## 11. AWQ：更强调“重要权重保护”的 4-bit 路线

`AWQ` 全称是 `Activation-aware Weight Quantization`。

这个名字里最重要的词，是 `Activation-aware`。

它的核心观点是：

> 不是所有权重都同等重要，某些和激活模式强相关的“关键权重”，更值得被保护。

### 11.1 它为什么受欢迎

因为它在工程上往往表现出很好的平衡：

- 仍然是 4-bit
- 压缩效果强
- 对指令模型、聊天模型往往比较友好
- 在生产推理生态里很常见

### 11.2 它和 GPTQ 的差别，怎么用人话理解

你可以这样记：

- `GPTQ`：更强调“从误差最小化角度把权重量化好”
- `AWQ`：更强调“把真正重要的那部分权重保护好”

这不是严格数学定义，但对建立直觉很有帮助。

### 11.3 AWQ 的典型适用场景

- 你部署的是聊天模型或指令微调模型
- 你想要高质量 4-bit 推理
- 你准备用 `vLLM`
- 你有比较现代的 GPU

### 11.4 一个典型示例

```python
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

model_name = "TheBloke/Mistral-7B-Instruct-v0.2-AWQ"

model = AutoAWQForCausalLM.from_quantized(
    model_name,
    fuse_layers=True,
)
tokenizer = AutoTokenizer.from_pretrained(model_name)
```

### 11.5 什么时候优先 AWQ

如果你更偏向下面这些目标：

- 部署而不是训练
- 4-bit 高质量聊天推理
- `vLLM` 生产化路线
- 想要比传统方案更激进但仍稳的 4-bit 推理体验

那 `AWQ` 往往比 `GPTQ` 更值得优先试。

---

## 12. GGUF：不是单纯“一个算法”，而是一条本地部署路线

很多人第一次看到 `GGUF` 时会把它和 `GPTQ`、`AWQ` 当成完全同类。

这会导致理解混乱。

更准确地说：

> `GGUF` 更像是 `llama.cpp` 生态的模型格式与量化部署路线。

它非常适合：

- 本地推理
- CPU 推理
- Apple Silicon
- 桌面工具生态

例如这些工具经常围绕这条路线：

- `llama.cpp`
- `Ollama`
- `LM Studio`
- 一些本地 GUI 客户端

### 12.1 GGUF 为什么这么重要

因为它解决的不是“只在 Python 里怎么压缩模型”，而是：

- 如何把模型变成更容易在本地设备运行的格式
- 如何在 CPU、Mac、轻量 GPU 上高效推理
- 如何在 C/C++ 推理栈里更稳定地跑起来

### 12.2 常见量化档位

在 GGUF 生态里，你经常会看到这些名字：

- `Q4_K_M`
- `Q5_K_M`
- `Q6_K`
- `Q8_0`

对初学者来说，一个很实用的记法是：

- `Q4_K_M`：常见默认档，性价比较高
- `Q5_K_M`：更偏质量
- `Q6_K` / `Q8_0`：更接近原始质量，但更大

### 12.3 一个典型工作流

1. 先把 Hugging Face 模型转换到 GGUF
2. 再选择一个量化档位
3. 用 `llama.cpp` 或上层工具运行

### 12.4 GGUF 最适合谁

如果你满足下面任意一点，GGUF 很可能是你的第一选择：

- 你主要做本地运行，不想依赖完整 Python 推理栈
- 你在 Mac 上跑模型
- 你想跑在 CPU 或轻量 GPU 上
- 你准备用 Ollama 或 LM Studio

这时你就不要优先纠结 `AWQ` 和 `GPTQ`，而是优先进入 `GGUF` 这条生态。

---

## 13. HQQ：没有校准数据时的快速量化方案

`HQQ` 的亮点很明确：

- 不需要校准数据
- 量化速度快
- 可以尝试更激进的低 bit

### 13.1 它什么时候有吸引力

很多 PTQ 方法会涉及校准样本。

但真实工程里，你未必总有一套合适的校准集，或者你只是想快速试一下：

- 这个模型压成 4-bit 会怎么样
- 能不能再压到 3-bit 或 2-bit

这时 `HQQ` 的价值就出来了。

### 13.2 它适合什么场景

- 快速实验
- 无校准数据
- 做方法探索
- 尝试极低比特

### 13.3 什么时候不要先用它

如果你的目标非常明确是：

- 最稳定的主流部署
- 某个成熟生产栈
- 最常见社区分发版本

那通常还是先试：

- `bitsandbytes`
- `AWQ`
- `GPTQ`
- `GGUF`

`HQQ` 更像是一个“灵活、实验友好”的选项。

---

## 14. 一张表看懂它们的边界

| 方案 | 主要目标 | 是否适合训练 | 是否适合推理 | 典型生态 |
|------|----------|--------------|--------------|----------|
| `bitsandbytes` | 低成本加载与训练集成 | 是，特别适合 `QLoRA` | 是 | `transformers` |
| `GPTQ` | 高质量 4-bit PTQ | 通常不是首选训练路线 | 是 | NVIDIA GPU 推理 |
| `AWQ` | 激活感知的高质量 4-bit 推理 | 不是主打训练 | 是 | `transformers`、`vLLM` |
| `GGUF` | 本地设备部署与跨硬件运行 | 不是主打训练 | 是 | `llama.cpp`、`Ollama` |
| `HQQ` | 无校准快速量化 | 可与 PEFT 配合，但更偏实验 | 是 | HF / vLLM 方向 |

这里最容易记混的点再重复一次：

- 想训练或做 `QLoRA`：先看 `bitsandbytes`
- 想高质量 GPU 推理：先看 `AWQ` / `GPTQ`
- 想本地 CPU/Mac/Ollama：先看 `GGUF`
- 想无校准快速试验：看 `HQQ`

---

## 15. 从工程角度，应该怎么选

下面给你一个实用决策树。

### 15.1 我想做 QLoRA 微调

优先：

- `bitsandbytes 4-bit`

原因：

- 和 Hugging Face、PEFT 集成最顺
- 社区教程最多
- 这是很多人真正进入量化世界的第一站

### 15.2 我只想把模型塞进显卡并先跑起来

优先：

- `bitsandbytes 8-bit` 或 `4-bit`

原因：

- 最省时间
- 代码改动最小

### 15.3 我想要比较正式的 4-bit GPU 推理部署

优先：

- `AWQ`
- 其次 `GPTQ`

如果你的场景是：

- 聊天模型
- 指令模型
- 生产推理

那通常先试 `AWQ`。

### 15.4 我想在 Mac、CPU、本地桌面环境里运行

优先：

- `GGUF`

原因：

- 这是最自然的生态路径
- 别把时间浪费在不适合本地部署的 GPU 路线上

### 15.5 我没有校准数据，但想快速做低比特实验

优先：

- `HQQ`

---

## 16. 一个最实用的入门路线

如果你是第一次系统学习量化，我建议按下面顺序走。

### 第一步：先用 bitsandbytes 跑通 4-bit 加载

目标不是追求最强性能，而是先建立最基本的直觉：

- 量化模型可以像普通模型一样加载
- 显存明显下降
- 质量并不会立刻崩掉

### 第二步：再理解 QLoRA

这一步你会真正明白：

- 为什么量化和微调经常一起出现
- 为什么 4-bit 底座 + LoRA 是一条极其实用的工程路径

### 第三步：再看 GPTQ 和 AWQ

这一步你开始从“能跑”进入“怎么部署得更好”。

重点理解：

- 两者都偏推理部署
- 两者都不是单纯的“HF 一键 4-bit”
- 它们更像是专业化量化路线

### 第四步：如果你做本地应用，再进入 GGUF

这一步你会理解：

- 量化不只是 Python 里的一个配置项
- 它也可以是一整条模型分发和部署路线

---

## 17. 最小可用实战：4-bit 推理

下面给一个最小可用示例。这个例子不是为了覆盖所有高级参数，而是为了让你第一次真正跑通量化模型。

### 17.1 安装

```bash
pip install bitsandbytes transformers accelerate
```

### 17.2 代码

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

model_name = "meta-llama/Llama-2-7b-hf"

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)

tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=quant_config,
    device_map="auto",
)

prompt = "请用通俗语言解释什么是模型量化。"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

outputs = model.generate(
    **inputs,
    max_new_tokens=200,
    temperature=0.7,
)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### 17.3 你应该观察什么

跑通后，不要只盯着回答内容。

更应该观察：

- 模型是否成功加载
- 显存是否明显下降
- 推理速度是否可接受
- 输出质量是否还能满足你的任务

这四件事，才是量化的核心评估维度。

---

## 18. 最小可用实战：QLoRA 的基本结构

如果你已经学过 PEFT，这一节会把两块知识接起来。

### 18.1 典型结构

```python
import torch
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_config,
    device_map="auto",
)

model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
```

### 18.2 这段代码真正表达了什么

- 基座模型以 4-bit 形式加载
- 基座模型本体不做全量训练
- 在上面挂 LoRA adapter
- 真正训练的是很小的一部分新增参数

这就是 `QLoRA` 的工程直觉。

---

## 19. 常见误区

### 19.1 误区一：4-bit 一定比 8-bit 更划算

不一定。

如果你的任务对输出质量很敏感，或者显存其实还够，那么：

- `8-bit` 可能更稳
- 你未必需要上来就冲 `4-bit`

### 19.2 误区二：所有量化方法是同一类东西

不是。

再强调一次：

- `AWQ` / `GPTQ` / `HQQ` 更像方法
- `bitsandbytes` 更像工程接入方案
- `GGUF` 更像格式与部署生态

### 19.3 误区三：量化后速度一定更快

也不一定。

是否更快，受很多因素影响：

- 具体 kernel
- GPU 架构
- batch size
- 上下文长度
- 框架实现

很多时候：

- 显存更省是确定的
- 速度更快是“通常如此，但依赖实现”

### 19.4 误区四：量化后质量下降就说明方法不行

不一定。

你要先检查：

- 量化档位是否过激
- 任务是否本身对精度高度敏感
- 模型是否适合这个量化路线
- 运行时 kernel 是否正确

---

## 20. 常见排障

### 20.1 模型能加载，但输出明显变差

先排查：

- 是不是压得太狠了，例如从可接受的 4-bit 继续压到更低
- 是否用了不适合该模型的量化版本
- 聊天模板、tokenizer、generation 配置是否匹配

### 20.2 显存还是爆

先排查：

- 你压的是权重，但 `KV Cache` 仍然会涨
- 上下文长度是否过大
- batch 是否过大
- 生成长度是否过长

很多人第一次做量化时，只盯着“模型权重体积”，却忽略了运行时开销。

### 20.3 推理比预期慢

先排查：

- 当前硬件是否适合该量化后端
- 是否启用了更高性能 kernel
- 是否选择了不适合当前 batch 的版本
- 是否其实受限于 CPU、磁盘或数据传输

### 20.4 本地部署一堆格式看不懂

记住这个最简化原则：

- Python + HF + 训练/实验：先看 `bitsandbytes`
- GPU 推理模型分发：先看 `AWQ` / `GPTQ`
- Ollama / Mac / CPU：先看 `GGUF`

不要一开始就同时啃所有生态。

---

## 21. 学习顺序建议

如果你要把量化真正学扎实，我建议按下面顺序：

1. 先理解“为什么需要量化”
2. 再理解“权重量化”和“计算 dtype”不是一回事
3. 用 `bitsandbytes` 跑一个 4-bit 推理例子
4. 再跑一个 `QLoRA` 例子
5. 然后比较 `GPTQ` 和 `AWQ`
6. 最后根据你的硬件进入 `GGUF` 路线

这个顺序的好处是：

- 先建立直觉
- 再进入工程
- 最后按场景细分

而不是一上来被各种格式名淹没。

---

## 22. 一页总结

把整篇文档压缩成最重要的几句话，就是下面这些。

### 22.1 Quantization 是什么

它是把模型参数从高精度表示压缩到低精度表示，以降低显存、存储和带宽成本。

### 22.2 它主要解决什么问题

- 大模型太大
- 显卡放不下
- 本地跑不动
- 部署成本太高

### 22.3 它和微调的关系

- 量化不是微调
- 量化解决压缩与部署
- 微调解决任务适配
- `QLoRA` 把两者结合起来

### 22.4 方案怎么选

- 想快速入门或做 `QLoRA`：`bitsandbytes`
- 想做高质量 GPU 4-bit 推理：`AWQ` / `GPTQ`
- 想在 Mac、CPU、本地桌面工具上跑：`GGUF`
- 没有校准数据、想快速实验：`HQQ`

### 22.5 对初学者最实用的建议

不要先追求“最先进量化方法”。

先回答三个问题：

- 你是要训练，还是要推理
- 你用的是显卡，还是 CPU / Mac
- 你最紧张的是显存，还是质量，还是接入复杂度

量化不是一个单点技巧，而是一整套工程权衡。

当你开始用“场景”来选量化路线，而不是用“名词热度”来选，你就真正入门了。

---

## 23. 下一步可以学什么

如果你准备继续往下学，我建议顺着这条线：

1. 先亲手跑一个 `bitsandbytes 4-bit` 推理示例
2. 再跑一个 `QLoRA` 微调示例
3. 对比同一个模型的 `AWQ`、`GPTQ`、`GGUF` 版本
4. 观察它们在下面四个维度的差异：

- 显存
- 速度
- 输出质量
- 接入复杂度

真正的理解，不来自记住术语，而来自亲手比较。

