# QLoRA 学习与实战入门

## 你会学到什么

这份笔记的目标不是只告诉你“QLoRA 是 4-bit + LoRA”，而是让你真正知道它为什么有用、代码里每一步在干什么，以及出问题时该先查哪里。

读完后，你应该能回答这些问题：

- QLoRA 到底解决了什么问题
- 它和普通 LoRA、全参数微调的核心差异是什么
- 为什么大家默认用 `NF4`、`double quant`、`prepare_model_for_kbit_training`
- 怎样写出一份最小可用的 QLoRA 训练骨架
- 显存还是爆、dtype 不对、merge 失败时该怎么排查

这份文档面向已经知道 LoRA 是什么，但还没有系统上手 QLoRA 的读者。

---

## 1. 为什么会有 QLoRA

普通 LoRA 已经很省了，因为它只训练少量 adapter，而不是更新整套大模型权重。

但它还有一个现实问题：**底座模型本身仍然要以较高精度加载到显存里。**

这意味着：

- 7B 模型还能勉强接受
- 13B、34B、70B 很快就会被显存卡死
- 你明明只训练几百万到几千万 adapter 参数，却还得为整个底座模型支付高精度显存成本

QLoRA 的核心思路是：

1. 把底座模型以 `4-bit` 量化形式加载，显著降低显存占用。
2. 底座权重冻结，不直接更新。
3. 在量化底座上挂 LoRA adapter，只训练这些 adapter。
4. 反向传播可以穿过量化底座，把学习信号传给 LoRA 参数。

所以，QLoRA 本质上是：**量化底座 + LoRA 训练**。

它不是在替代 LoRA，而是在让 LoRA 能够在更大模型、更小显存上落地。

---

## 2. 一句话理解 QLoRA

如果把普通 LoRA 理解为“底座模型不动，只训练旁边的小 adapter”，那 QLoRA 就是：

**把底座模型压缩到 4-bit 存起来，再在这个压缩底座上训练 LoRA adapter。**

你真正省下来的主要不是 adapter 的开销，而是底座权重的显存。

---

## 3. QLoRA、LoRA、全参数微调的区别

| 方法 | 底座权重 | 可训练部分 | 显存压力 | 适合场景 |
|---|---|---|---|---|
| 全参数微调 | 高精度加载并更新 | 全部参数 | 最高 | 小模型或大算力环境 |
| LoRA | 高精度加载但冻结 | LoRA adapter | 中等 | 7B 到 13B 常规 PEFT |
| QLoRA | 4-bit 加载并冻结 | LoRA adapter | 最低 | 显存紧张但仍想训大模型 |

这里要特别分清楚两个概念：

- **LoRA** 解决的是“训练哪些参数”
- **QLoRA** 解决的是“底座模型怎么以更省显存的方式参与训练”

所以，QLoRA 不是另一个 adapter 算法，它更像是 LoRA 的显存优化训练方案。

---

## 4. 什么时候适合用 QLoRA，什么时候不适合

### 适合

- 你想微调 7B、13B、34B 甚至更大的模型，但显存有限
- 你接受少量精度损失，换取更低训练成本
- 你要做的是指令微调、领域适配、风格迁移这类典型 PEFT 任务
- 你想先快速验证一个方向，而不是立刻投入全参数微调成本

### 不太适合

- 你的模型很小，完全没必要上 4-bit 训练链路
- 你追求极致上限，算力和显存都很充足
- 你的目标只是做推理部署，而不是训练
- 你当前连普通 LoRA 流程都没跑通

一句实务建议：

**显存是第一瓶颈时，优先看 QLoRA；显存不是问题时，先从普通 LoRA 开始更稳。**

---

## 5. 核心心智模型

理解 QLoRA，抓住下面四件事就够了。

### 5.1 底座模型是量化加载的

QLoRA 通常使用 `bitsandbytes` 把底座模型以 4-bit 形式加载，而不是 FP16/BF16 全精度。

这一步解决的是“模型装不进显存”的问题。

### 5.2 真正训练的仍然是 LoRA adapter

QLoRA 不是训练量化权重本身，而是在量化后的底座上继续挂 LoRA adapter。

所以训练时更新的是：

- `lora_A`
- `lora_B`
- 以及必要时少量额外可训练模块

底座权重本身通常仍然冻结。

### 5.3 量化格式和计算精度不是一回事

很多初学者会把下面两件事混在一起：

- **存储精度**：比如 4-bit
- **计算精度**：比如 `torch.bfloat16`

QLoRA 常见配置是：

- 用 `4-bit` 存底座
- 用 `BF16` 或 `FP16` 做计算

所以你会同时看到：

- `load_in_4bit=True`
- `bnb_4bit_compute_dtype=torch.bfloat16`

### 5.4 QLoRA 是训练技巧，不是最终部署格式

很多人第一次接触 QLoRA 会误以为：

- 训练时是 4-bit
- 部署时也必须维持同样格式

其实不一定。训练完后你保存的是 adapter。部署时你可以：

- 保持 adapter 形式加载
- 或者把 adapter merge 到一个非量化底座
- 或者走你自己的推理量化路线

QLoRA 的重点是**让训练阶段更省显存**。

---

## 6. 为什么大家默认用 NF4 和 Double Quant

QLoRA 代码里最常见的一段通常是：

```python
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True
)
```

这四行不是模板咒语，而是有明确原因的。

### 6.1 `load_in_4bit=True`

表示底座模型按 4-bit 量化形式加载。相比 16-bit，显存占用可以大幅下降。

### 6.2 `bnb_4bit_quant_type="nf4"`

`NF4` 是给接近正态分布权重设计的 4-bit 量化格式，对 Transformer 权重通常更合适。

和 `FP4` 相比，经验上：

- `NF4` 更适合 LLM
- `FP4` 更像备选项

一个简单结论就够用了：**做 Transformer/LLM，先默认用 `NF4`。**

### 6.3 `bnb_4bit_compute_dtype=torch.bfloat16`

这控制的是实际计算精度，不是底座存储精度。

常见选择：

| 配置 | 说明 |
|---|---|
| `torch.bfloat16` | 更稳，通常是首选 |
| `torch.float16` | 也常见，但更容易数值不稳定 |
| `torch.float32` | 调试时可用，训练太慢 |

如果硬件支持，优先考虑 `BF16`。

### 6.4 `bnb_4bit_use_double_quant=True`

这表示对量化过程中的缩放常数再做一次量化，进一步节省显存。

它不是“效果增强器”，更像是额外的显存优化。对大模型时通常值得开。

---

## 7. `prepare_model_for_kbit_training` 到底在干什么

这一步经常被直接复制，但不理解它，后面排错会很痛苦。

```python
from peft import prepare_model_for_kbit_training

model = prepare_model_for_kbit_training(model)
```

它的作用可以粗略理解为：

- 把模型调整到适合低比特训练的状态
- 处理一些需要保持更高稳定性的模块
- 配合梯度检查点等手段，让训练更稳、更省

实践上，你几乎可以把这一步当成 QLoRA 流程的标准动作。省掉它，不一定立刻报错，但常常会让后续训练更脆弱。

---

## 8. 一个最小可用的 QLoRA 示例

下面是一份可以直接改造成你项目脚本的骨架代码。它没有绑定特定数据集格式，但核心步骤是完整的。

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, TaskType, get_peft_model, prepare_model_for_kbit_training

model_name = "Qwen/Qwen2.5-7B-Instruct"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.bfloat16
)

model.gradient_checkpointing_enable()
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
    target_modules="all-linear"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
```

这段代码里最值得注意的是：

- 底座是 4-bit 加载的
- 训练目标仍然是 LoRA adapter
- `target_modules="all-linear"` 是 QLoRA 中很常见的起点
- `gradient_checkpointing` 和 `prepare_model_for_kbit_training` 通常配合使用

如果你要接 Trainer，可以继续这样写：

```python
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir="./qlora_output",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    num_train_epochs=3,
    warmup_steps=100,
    bf16=True,
    logging_steps=10,
    save_steps=200,
    optim="paged_adamw_8bit",
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset
)

trainer.train()
model.save_pretrained("./qlora_adapter")
tokenizer.save_pretrained("./qlora_adapter")
```

这里的 `optim="paged_adamw_8bit"` 也是 QLoRA 训练里常见的选择，因为它能进一步减轻优化器状态的显存压力。

---

## 9. `target_modules` 怎么选

QLoRA 和普通 LoRA 一样，也需要决定把 adapter 挂到哪些层。

### 一个常见起点

```python
target_modules = "all-linear"
```

这是很多 QLoRA 配置喜欢的默认项，因为它对不同 Transformer 架构的覆盖更直接。

### 如果你想手动指定

对 Llama / Qwen / Mistral 这类模型，常见写法是：

```python
target_modules = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj"
]
```

如果你只想先做保守尝试，也可以只挂注意力投影层：

```python
target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"]
```

### 怎么确认模型实际层名

```python
for name, module in model.named_modules():
    if "proj" in name or "linear" in name:
        print(name)
```

这一步很重要。很多“QLoRA 没效果”的根因，最后都不是量化问题，而是 `target_modules` 根本没匹配上。

---

## 10. QLoRA 的完整训练时间线

把训练过程按顺序拆开，你就不会被代码里一堆配置吓到。

### 步骤一：准备量化配置

目标是用 `BitsAndBytesConfig` 指定：

- 4-bit 加载
- `NF4`
- 计算 dtype
- 是否启用 double quant

### 步骤二：加载量化底座

这一步决定你能不能把目标模型装进显存。

### 步骤三：做 k-bit 训练准备

也就是 `prepare_model_for_kbit_training`。它不是可有可无的美化步骤，而是 QLoRA 稳定训练的重要一环。

### 步骤四：注入 LoRA adapter

这时才进入 PEFT 的核心阶段。底座仍冻结，真正训练的是 adapter。

### 步骤五：常规训练

从 Trainer 视角看，这一步和普通 LoRA 已经很像了：

- 喂数据
- 前向
- 反向
- 更新 adapter 参数

### 步骤六：保存 adapter

训练结束后，通常先保存 adapter，而不是一上来就 merge 整个模型。

---

## 11. 怎么计算训练资源开销

这一章给你一套够实用的估算框架。它不是论文级精确建模，但足够回答这些工程问题：

- 这张卡大概能不能训得动
- 为什么全参数微调和 LoRA 显存差这么多
- 为什么 QLoRA 能把 7B/13B 模型塞进消费级显卡
- 训练一轮大概要多少 step、多少 GPU 小时

先给一个最重要的结论：

**训练资源开销通常由四部分组成：权重、梯度、优化器状态、激活值。**

可以写成：

```text
总显存 ≈ 权重显存 + 梯度显存 + 优化器状态显存 + 激活值显存 + 其他开销
```

这里的“其他开销”包括：

- CUDA kernel workspace
- 临时张量
- dataloader / padding 带来的波动
- 分布式通信缓冲

所以你手工算出来的数，通常应该被当成**下界**，不是最终实测值。

### 11.1 先算权重显存

最基础的公式是：

```text
权重显存 ≈ 参数量 × 每个参数所占字节数
```

常见精度对应关系：

| 精度 | 每参数字节数 |
|---|---|
| FP32 | 4 bytes |
| FP16 / BF16 | 2 bytes |
| INT8 | 1 byte |
| INT4 / 4-bit | 0.5 byte |

例如一个 `7B` 模型：

- FP16 / BF16 权重约 `7 × 2 = 14 GB`
- INT8 权重大约 `7 GB`
- 4-bit 权重大约 `3.5 GB`

但要注意，QLoRA 里的 4-bit 不是完全“裸 0.5 byte/param”，因为还要存量化相关的缩放信息。工程上更稳妥的说法是：

- **理论下界**：`参数量 × 0.5 byte`
- **实际占用**：通常会比理论值略高一点

### 11.2 再算梯度显存

梯度只为**可训练参数**保存，所以：

```text
梯度显存 ≈ 可训练参数量 × 梯度字节数
```

如果是：

- 全参数微调：可训练参数量约等于全模型参数量
- LoRA / QLoRA：可训练参数量只是 adapter 参数

这也是 LoRA 类方法省显存的关键原因之一。

### 11.3 再算优化器状态显存

如果你用 AdamW，一般至少会维护：

- 一阶矩 `m`
- 二阶矩 `v`

粗略估算：

```text
AdamW 状态显存 ≈ 可训练参数量 × 8 bytes
```

这里的 `8 bytes` 指的是两个 FP32 状态：

- `m`：4 bytes
- `v`：4 bytes

如果你的实现里还有 master weights 或额外状态，实际占用会更高。所以工程上可以把它理解为：

```text
AdamW 优化器状态 ≈ 可训练参数量 × 8~12 bytes
```

如果改成 8-bit optimizer，比如：

```python
optim="paged_adamw_8bit"
```

那么优化器状态开销通常还能继续下降。

### 11.4 最容易被低估的是激活值显存

很多人只会算“模型参数占多少 GB”，但训练时真正经常把你显存打爆的是激活值。

激活值显存与下面几个因素高度相关：

- `per_device_train_batch_size`
- `max_seq_length`
- 模型层数
- hidden size
- 是否开启 `gradient_checkpointing`

工程上不需要死背复杂公式，先记住这几个趋势：

- batch size 翻倍，激活显存通常近似翻倍
- sequence length 增大，激活显存会上升很快
- 长上下文任务里，激活值经常比 LoRA adapter 本身贵得多
- 开启 `gradient_checkpointing` 会降低激活显存，但会增加一点计算时间

所以你看到“QLoRA 明明只训练少量参数，为什么还是 OOM”，答案往往不是 adapter 太大，而是：

- batch 太大
- seq 太长
- 没开 checkpointing

### 11.5 一套实用的显存估算公式

把上面几项合起来，可以用下面这套近似公式。

#### 全参数微调

```text
总显存 ≈
全模型权重 +
全模型梯度 +
全模型优化器状态 +
激活值
```

如果底座是 BF16，且优化器是 AdamW，可以先用：

```text
总显存 ≈ 参数量 × (2 + 2 + 8~12) bytes + 激活值
       ≈ 参数量 × 12~16 bytes + 激活值
```

#### LoRA

```text
总显存 ≈
全模型权重 +
LoRA 参数梯度 +
LoRA 参数优化器状态 +
激活值
```

也就是：

```text
总显存 ≈
全模型参数量 × 底座字节数 +
LoRA参数量 × (梯度字节数 + 优化器状态字节数) +
激活值
```

底座仍然很贵，只是梯度和优化器状态只保留在 LoRA adapter 上。

#### QLoRA

```text
总显存 ≈
量化底座权重 +
LoRA 参数梯度 +
LoRA 参数优化器状态 +
激活值
```

和 LoRA 最大的差异就是第一项：

- LoRA：底座可能是 BF16，约 `2 bytes/param`
- QLoRA：底座是 4-bit，理论约 `0.5 bytes/param`

这就是 QLoRA 最核心的节省来源。

#### AdaLoRA

AdaLoRA 的估算思路与 LoRA 相同，只是 LoRA 参数量不再由固定 rank 决定，而是由动态 rank 分配决定。

粗略上可以把它当成：

```text
AdaLoRA 开销 ≈ LoRA 开销
```

只是把 LoRA 参数量里的固定 `r`，换成“训练中或最终平均 rank”。

### 11.6 LoRA / AdaLoRA 参数量怎么粗估

如果某个线性层从 `d_in` 映射到 `d_out`，LoRA 新增参数大致是：

```text
LoRA 参数量 ≈ r × (d_in + d_out)
```

如果这个层本身近似是方阵，也就是 `d_in ≈ d_out ≈ d`，那么可以近似成：

```text
LoRA 参数量 ≈ 2rd
```

如果一共有 `L` 个目标层，则：

```text
总 LoRA 参数量 ≈ Σ r × (d_in + d_out)
```

或者更粗糙一点：

```text
总 LoRA 参数量 ≈ 目标层数 × 2rd
```

这也是为什么：

- `r` 翻倍，adapter 参数量近似翻倍
- `target_modules` 扩大，adapter 参数量也会跟着明显上升

### 11.7 一个 7B 模型的粗略对比

假设：

- 模型大小：`7B`
- 底座精度：BF16 或 4-bit
- LoRA / QLoRA adapter：`20M` 可训练参数
- AdamW 类优化器
- 不把激活值写死，只单独看“模型状态显存”

那么可以得到一个很粗的量级估算：

| 策略 | 底座权重 | 梯度 | 优化器状态 | 模型状态总量级 |
|---|---:|---:|---:|---:|
| 全参数微调 BF16 | ~14 GB | ~14 GB | ~56-84 GB | ~84-112 GB |
| LoRA BF16 | ~14 GB | ~40 MB | ~160-240 MB | ~14.2-14.3 GB |
| QLoRA 4-bit | ~3.5-4.5 GB | ~40 MB | ~160-240 MB | ~3.7-4.8 GB |
| AdaLoRA BF16 | 与 LoRA 类似 | 取决于平均 rank | 取决于平均 rank | 通常接近或略低于 LoRA |

这张表最重要的不是绝对数字，而是结构差异：

- **全参数微调**：梯度和优化器状态跟着全模型走，极贵
- **LoRA**：底座贵，但训练态开销只落在 adapter 上
- **QLoRA**：连底座也便宜了，所以整体显存进一步下降
- **AdaLoRA**：本质还是 LoRA 路线，只是 adapter 预算会动态变化

### 11.8 如何理解图里的 `5.2 bit per parameter`

你给的这张图非常适合建立直觉，因为它把 QLoRA 的优势压缩成了一个核心问题：

**如果把训练开销平均分摊到“每个底座参数”，QLoRA 大概只需要 `5.2 bits/parameter`。**

先看图左边的四项：

- `Weight: 4 bit`
- `Weight gradient: ~0.4 bit`
- `Optimizer state: ~0.8 bit`
- `Adapter weights: ~0.4 bit`

它们加起来就是：

```text
4 + 0.4 + 0.8 + 0.4 = 5.2 bit per parameter
```

这里最容易误解的一点是：

**这不是说模型里的每个参数真的都同时存着 5.2 bit 的同构结构，而是把总训练内存平均摊到了“每个底座参数”上。**

也就是说，这是一种“归一化后的平均成本”表达。

你可以把它写成：

```text
平均每个底座参数的训练开销
≈ 底座权重位宽
+ adapter参数占比 × (adapter权重位宽 + 梯度位宽 + 优化器状态位宽)
```

如果记：

- `N_base`：底座参数量
- `N_adapter`：LoRA adapter 参数量
- `ρ = N_adapter / N_base`

那么更形式化一点：

```text
bits_per_base_param
≈ b_base + ρ × (b_adapter + b_grad + b_opt)
```

图里的 `0.4 / 0.8 / 0.4` 本质上就是把 adapter 相关状态，按 `ρ` 折算到了整个底座模型上。

换句话说：

- adapter 本身很小
- 但为了便于和全参数微调比较，作者把它的开销均摊到了每个底座参数

这样不同策略就能放在同一张表里直接比较。

#### 为什么 LoRA 是 `17.6 bits/parameter`

图里 LoRA 的逻辑和 QLoRA 一样，只不过底座还是 16-bit：

```text
16 + 0.4 + 0.8 + 0.4 = 17.6 bits/parameter
```

所以从 LoRA 到 QLoRA，最关键的变化不是 adapter 变了，而是：

```text
底座权重: 16 bit -> 4 bit
```

也就是只改了第一项，其他 adapter 相关项基本保留原来的量级。

这就是 QLoRA 显存大幅下降的根本原因。

#### 为什么 70B 模型会落到约 `46 GB`

图里最后一行写的是：

```text
70B model -> 46 GB of GPU memory
```

按这张图的算法，直接算就行：

```text
70e9 × 5.2 bits / 8
= 45.5e9 bytes
≈ 45.5 GB
```

四舍五入后就是图里的 `46 GB`。

这也解释了为什么它说：

- 全参数微调：太贵
- LoRA：虽然便宜很多，但 70B 仍然偏重
- QLoRA：开始接近“多张消费级 GPU 可承受”的范围

#### 图右边三列到底在画什么

右侧三个小图其实是在对比三种训练方式的显存构成：

##### Full Finetuning

- 底座模型是 `16-bit Transformer`
- 所有参数都要更新
- 所以需要完整的梯度和大块优化器状态

这就是为什么左边 full finetuning 会高到 `96 bits/parameter`。

##### LoRA

- 底座仍然是 `16-bit Transformer`
- 但只训练上面那几个 adapter 小块
- 优化器状态也只为 adapter 保存

所以它比全参数微调已经轻很多，但底座还是 16-bit，模型一大仍然会重。

##### QLoRA

- 底座变成 `4-bit Transformer`
- adapter 仍然保留用于训练
- 红色箭头表示 `paged optimizer` 的分页流动，必要时会在 CPU 和 GPU 之间搬运状态

这一步的意义不是“让训练变便宜一点点”，而是把最贵的底座权重从 16-bit 直接砍到 4-bit。

#### 红色箭头为什么指向 CPU

图右边 QLoRA 模块旁边有一个 CPU 虚线框，红色箭头连过去，这表示：

- 某些优化器状态不一定一直常驻 GPU
- 当显存出现瞬时峰值时，可以利用分页机制把部分状态放到 CPU
- 在真正需要做 optimizer step 时，再取回 GPU

这也是 QLoRA 论文里 `paged optimizers` 的直觉图示。

它主要解决的是：

- 长序列
- 大 batch
- 某些 step 出现的显存尖峰

而不是替代 4-bit 量化本身。

#### 这张图最值得记住的结论

如果你只记一句话，那就是：

**QLoRA 之所以省，不是因为 LoRA 本身突然更小了，而是因为“占大头的底座权重”从 16-bit 变成了 4-bit。**

也因此，这张图最核心的对比不是：

- LoRA vs QLoRA 的 adapter 部分

而是：

- `16-bit base model` vs `4-bit base model`

#### 为什么有时会看到 `5.6 bits` 而不是 `5.2 bits`

你在不同讲义或二手资料里，有时会看到：

- `5.2 bits/parameter`
- `5.6 bits/parameter`

这通常不是“谁完全错了”，而是因为不同资料会在下面几件事上做不同近似：

- 是否把量化常数的额外开销单列
- 是否把 double quant 的收益计入最终数字
- adapter 参数占比 `ρ` 采用什么近似
- 是否做了四舍五入

所以阅读时更重要的是理解结构：

- QLoRA 的基座大约是 `4-bit`
- 额外训练态开销来自 adapter、梯度和优化器状态
- 总平均成本远低于 16-bit 底座的 LoRA，更远低于全参数微调

### 11.9 GPU 小时怎么估算

除了显存，你通常还关心训练要跑多久、花多少钱。

先定义几个量：

- `N_tokens`：总训练 token 数
- `global_batch_tokens`：每一步全局处理 token 数
- `step_time`：每个 step 花费秒数
- `num_gpus`：GPU 数量

那么：

```text
训练步数 ≈ N_tokens / global_batch_tokens
```

其中：

```text
global_batch_tokens ≈
per_device_train_batch_size ×
gradient_accumulation_steps ×
num_gpus ×
平均有效序列长度
```

于是：

```text
总训练时间 ≈ 训练步数 × step_time
GPU小时 ≈ 总训练时间(小时) × num_gpus
训练成本 ≈ GPU小时 × 单卡时价
```

举个例子，假设：

- 总训练 token：`20B`
- 单卡 batch size：`2`
- gradient accumulation：`8`
- GPU 数量：`1`
- 平均有效序列长度：`1024`

那么：

```text
global_batch_tokens ≈ 2 × 8 × 1 × 1024 = 16384
训练步数 ≈ 20,000,000,000 / 16,384 ≈ 1,220,703
```

如果平均每 step 是 `0.8s`，则：

```text
总时间 ≈ 976,562 秒 ≈ 271.3 小时
GPU小时 ≈ 271.3
```

如果单卡每小时 `¥12`，那训练成本大约就是：

```text
271.3 × 12 ≈ ¥3256
```

当然，真实训练里：

- padding 会降低有效 token 利用率
- eval、save checkpoint、数据预处理会额外耗时
- QLoRA 虽然省显存，但单 step 不一定总比 LoRA 更快

所以时间和成本估算通常也应留一点冗余。

### 11.10 不同 fine-tuning 策略下，应该重点看什么开销

如果你要快速判断选哪种策略，可以直接看这张表：

| 策略 | 最主要瓶颈 | 你最该算的东西 |
|---|---|---|
| 全参数微调 | 权重 + 梯度 + 优化器状态 | 总参数量、优化器状态倍数 |
| LoRA | 底座权重 + 激活值 | 底座精度、seq length、batch size |
| QLoRA | 激活值 + 量化底座 + adapter 状态 | 4-bit 底座、batch、seq、checkpointing |
| AdaLoRA | 激活值 + 动态 adapter 预算 | 平均 rank、target modules、训练步数 |

工程上最实用的决策逻辑通常是：

1. 如果卡根本装不下 BF16 底座，优先 QLoRA。
2. 如果 BF16 底座能装下，但全参训不起，优先 LoRA。
3. 如果 LoRA 已经能训，想进一步优化 adapter 预算，再看 AdaLoRA。
4. 如果你追求极致效果且算力充足，再考虑全参数微调。

---

## 12. 调参建议

下面这些建议不是唯一正确答案，但足够作为第一版实验起点。

### 12.1 先保守，再激进

第一版建议先这样起：

- `r=16`
- `lora_alpha=32`
- `lora_dropout=0.05`
- `target_modules="all-linear"`
- `bnb_4bit_quant_type="nf4"`
- `bnb_4bit_use_double_quant=True`

等 baseline 跑稳后，再去尝试更高 rank 或更广的 target modules。

### 12.2 BF16 优先于 FP16

如果你的硬件支持 BF16，优先用：

```python
bnb_4bit_compute_dtype=torch.bfloat16
```

因为它通常更稳，尤其是在长序列和较大模型时。

### 12.3 显存还是紧时，先动这些旋钮

优先级通常是：

1. 降低 `per_device_train_batch_size`
2. 增大 `gradient_accumulation_steps`
3. 开启 `gradient_checkpointing`
4. 缩短 `max_seq_length`
5. 确保 `double quant` 已打开

很多人一上来就怀疑 QLoRA 失效，其实只是 batch 或序列长度设置过大。

### 12.4 别忽略数据质量

QLoRA 省的是显存，不会自动修复差数据。如果：

- 指令模板混乱
- 输出字段脏
- 任务定义本身不一致

那么 LoRA、QLoRA、全参微调都会一起变差。

---

## 13. 常见错误与排查

### 13.1 环境里没有 `bitsandbytes` 或 `peft`

先安装基础依赖：

```bash
pip install bitsandbytes transformers peft accelerate datasets
```

如果还要用 TRL：

```bash
pip install trl
```

### 13.2 4-bit 了还是 OOM

先查下面几件事：

- batch size 是否过大
- 序列长度是否过长
- 是否开了梯度检查点
- 是否启用了 `bnb_4bit_use_double_quant=True`
- 是否把 `device_map`、`max_memory` 设得过于理想化

必要时可以显式限制显存预算：

```python
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    max_memory={0: "20GB", "cpu": "80GB"}
)
```

### 13.3 报 dtype 相关错误

典型现象包括：

- `expected scalar type BFloat16 but found Float`
- matmul 相关 dtype 不一致

优先检查：

- `bnb_4bit_compute_dtype`
- `torch_dtype`
- 训练参数里的 `bf16=True` / `fp16=True`

最稳的做法通常是统一成 BF16 路线。

### 13.4 merge adapter 失败

这类问题经常发生在你直接拿量化底座去 merge 时。

更稳妥的流程是：

1. 重新以更高精度加载原始底座
2. 再加载训练好的 adapter
3. 最后执行 `merge_and_unload()`

示例：

```python
from transformers import AutoModelForCausalLM
from peft import PeftModel
import torch

base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)

model = PeftModel.from_pretrained(base_model, "./qlora_adapter")
merged_model = model.merge_and_unload()
```

### 13.5 训练在跑，但指标几乎不动

优先排查：

- `target_modules` 是否命中
- 数据是否正确格式化
- 学习率是否过低或过高
- LoRA rank 是否太小

不要把所有问题都归咎于“量化损伤太大”。

---

## 14. QLoRA 的真实 trade-off

QLoRA 很强，但不是免费的午餐。

### 优点

- 显存需求显著降低
- 能在消费级 GPU 上训练更大的模型
- 和 LoRA 训练流程兼容度高
- 往往是“想训大模型但预算有限”时最现实的方案

### 代价

- 训练链路更复杂
- dtype、量化配置、硬件支持更容易踩坑
- 不是所有模型和环境都能无脑复制同一份配置
- 在极致质量追求下，仍可能不如高精度训练

所以工程上最稳的判断标准是：

**如果没有 QLoRA 你根本训不起来，那它的价值就非常直接；如果你本来就训得动高精度 LoRA，那就需要权衡额外复杂度是否值得。**

---

## 15. 一个简单的上手流程

如果你现在就要在项目里试 QLoRA，可以按这个顺序：

1. 先选一个你确实能加载成功的基座模型。
2. 用 `NF4 + BF16 + double quant` 起步，不要一开始就魔改配置。
3. 先跑一个小数据子集，确认 loss 在动、显存没炸、保存正常。
4. 再扩大数据量和训练步数。
5. 只在 baseline 稳定后，再去调 rank、target modules、优化器和序列长度。

这比一开始就堆满高级技巧更有效。

---

## 16. 总结

QLoRA 的核心不是“把 LoRA 变成另一个算法”，而是：

**用 4-bit 量化把底座显存压下来，同时保留 LoRA 这种低成本训练方式。**

你真正要记住的是下面四句话：

- QLoRA = 量化底座 + LoRA adapter。
- 4-bit 是存储方式，`BF16/FP16` 是计算方式。
- `NF4` 通常是 Transformer/LLM 的默认首选。
- `prepare_model_for_kbit_training` 和梯度检查点通常是标准动作。

---

## 17. 下一步建议

如果你准备继续深入，建议下一步做下面几件事：

1. 在同一数据集上对比 `LoRA` 和 `QLoRA` 的显存与效果。
2. 记录 `r`、batch size、seq length 对显存和指标的影响。
3. 再决定是否要结合 `TRL`、`FSDP`、`DeepSpeed` 或更复杂的训练栈。

如果你愿意，我下一步可以继续帮你补：

- `QLoRA + TRL/SFTTrainer` 的完整训练脚本
- `LoRA / QLoRA / AdaLoRA` 的对比笔记
- `Qwen / Llama / Mistral` 的 `target_modules` 速查表
