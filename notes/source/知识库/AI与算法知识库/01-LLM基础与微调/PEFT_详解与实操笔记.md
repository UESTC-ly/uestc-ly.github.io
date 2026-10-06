# PEFT 详解与实操笔记

## 1. 这份笔记会讲什么

如果你最近在看大模型微调，几乎一定会遇到 `PEFT` 这个词。

它经常和这些词一起出现：

- LoRA
- QLoRA
- Prefix Tuning
- Prompt Tuning
- Adapter
- Full Fine-Tuning

但很多资料会直接从某个方法开讲，导致你虽然会用 API，却不清楚它们之间的关系。  
这份笔记的目标，是先建立一张完整地图，再把主流方法放回这张地图里。

读完这篇，你应该能回答：

- PEFT 到底是什么
- 它为什么会成为大模型时代的主流微调路线之一
- 它和全量微调相比，真正节省了什么
- LoRA、QLoRA、Prefix Tuning、Prompt Tuning、IA3 的核心差异是什么
- 工程上什么时候该用 PEFT，什么时候不该用
- 如何用 Hugging Face `peft` 库跑通一个最小可用示例

一句话先给结论：

> `PEFT`（Parameter-Efficient Fine-Tuning）就是在尽量不改动大模型原始权重的前提下，只训练一小部分新增参数或极少数可更新参数，用较低成本完成任务适配。

## 2. 什么是 PEFT

`PEFT` 全称是：

```text
Parameter-Efficient Fine-Tuning
```

中文通常翻译为：

- 参数高效微调
- 参数高效调优

它的核心思想很简单：

- 不去更新整个模型的所有参数
- 只训练极少的一部分参数
- 让模型适配新任务或新领域

注意，这里的“高效”主要不是指算法优雅，而是指：

- 更少的可训练参数
- 更低的显存占用
- 更少的存储成本
- 更快的实验迭代

## 3. 为什么会需要 PEFT

### 3.1 全量微调的问题

在小模型时代，全量微调是很自然的默认选项：

- 把预训练模型拿来
- 在你的数据集上继续训练
- 更新所有参数

但到了大模型时代，这条路迅速变贵。

假设你面对的是一个 7B、13B、70B 模型，全量微调会带来几个现实问题。

#### 问题 1：显存成本高

训练时不仅要放模型参数，还要放：

- 梯度
- 优化器状态
- 激活值

所以显存远远不只是“模型大小”本身。

#### 问题 2：存储成本高

如果你对同一个基础模型做 10 个任务的全量微调，你通常需要保存 10 份完整权重。

这意味着：

- 模型越大，存储越贵
- 模型分发越慢
- 版本管理越麻烦

#### 问题 3：迭代慢

每试一个新数据集、一个新任务、一个新超参数，都要重新更新整套参数。  
这对实验效率非常不友好。

#### 问题 4：多任务部署不经济

你明明只是基于同一个底座模型做不同任务适配，却要维护很多份巨大模型权重。

这时 PEFT 就变得非常有吸引力。

### 3.2 PEFT 提供了什么

PEFT 的价值可以概括成一句话：

> 让你用很小的参数代价，获得一份“任务特化能力”。

你不再保存整份模型，而是保存：

- 一小块 adapter
- 一套 LoRA 权重
- 一段 prefix 参数
- 一些软提示向量

这样就能做到：

- 基座模型共享
- 任务适配分离
- 快速切换
- 低成本部署

## 4. PEFT 的核心直觉

理解 PEFT，先抓住一个关键前提：

> 大模型本身已经学到了大量通用能力。

这些能力包括：

- 基本语言建模
- 语法和语义理解
- 常识知识
- 一定程度的推理模式
- 文本生成能力

所以很多下游任务，并不需要你把整颗“大脑”重写一遍。  
你需要的往往只是：

- 给它一点偏置
- 给它一点适配
- 给它一点任务结构
- 让它把已有能力往某个方向用得更好

PEFT 就是在做这件事。

你可以把它理解为：

- 全量微调：重新训练整个专家
- PEFT：给专家外挂一个小的任务模块

## 5. PEFT 和全量微调的根本区别

### 5.1 全量微调

全量微调是：

- 模型大部分甚至全部参数都参与更新
- 优化空间最大
- 资源成本也最大

### 5.2 PEFT

PEFT 是：

- 原模型绝大部分参数冻结
- 只训练新增的小参数块，或极少量特定参数
- 优化空间变小
- 成本大幅下降

这意味着：

- PEFT 不一定永远比全量微调效果更好
- 但它通常以很低成本换来“足够好”的效果

在工程里，这个 tradeoff 往往非常划算。

## 6. PEFT 主要节省了什么

PEFT 通常会节省三样东西。

### 6.1 节省训练参数量

一个 7B 模型，全量微调要更新 70 亿级参数。  
LoRA 这类 PEFT 方法，可能只更新千万级甚至更少。

很多时候可训练参数占比只有：

- `0.1%`
- `0.5%`
- `1%`

### 6.2 节省显存

因为可训练参数少，所以：

- 梯度少
- 优化器状态少
- 训练开销明显降低

如果再叠加量化，比如 `QLoRA`，显存需求还能进一步下降。

### 6.3 节省存储与分发成本

你保存的是 adapter，不是整份模型。

这意味着：

- 任务模型更轻
- 版本管理更方便
- 多任务共存更自然

## 7. PEFT 不是一种方法，而是一类方法

这一点非常重要。

`PEFT` 不是某一个单独算法，它是一整个家族。  
常见成员包括：

- LoRA
- QLoRA
- Prefix Tuning
- Prompt Tuning
- P-Tuning v2
- IA3
- AdaLoRA
- 各类 Adapter 方法

所以你看到别人说“我用 PEFT 训练模型”，本质上是在说：

- 我没有做 full fine-tuning
- 我用的是某种参数高效路线

但具体是哪种，要继续往下问。

## 8. 常见 PEFT 方法全景图

你可以粗略把常见 PEFT 方法分成三类：

### 8.1 软提示类

代表方法：

- Prompt Tuning
- Prefix Tuning
- P-Tuning v2

特点：

- 不直接改模型主权重
- 学习一段“可训练提示”
- 从输入层或多层表示引导模型

### 8.2 Adapter / 插件类

代表方法：

- 传统 Adapter
- LoRA
- AdaLoRA
- IA3

特点：

- 在模型层内部插入或附加少量模块
- 通过小规模新增参数实现适配

### 8.3 量化结合类

代表方法：

- QLoRA

特点：

- 不是独立于 LoRA 的另一大类思想
- 而是在 LoRA 基础上，配合低比特量化降低训练显存

## 9. 主流方法一：LoRA

### 9.1 LoRA 是什么

`LoRA` 全称：

```text
Low-Rank Adaptation
```

它的核心思想是：

- 不直接更新原始大权重矩阵
- 而是学习一个低秩增量
- 用低秩分解去逼近权重更新

如果原始权重是：

```text
W
```

LoRA 不直接把它更新成 `W'`，而是写成：

```text
W' = W + ΔW
```

并让：

```text
ΔW = BA
```

其中：

- `A` 和 `B` 是低秩小矩阵
- 训练时只更新 `A/B`
- 原始 `W` 保持冻结

### 9.2 为什么 LoRA 很流行

因为它同时满足了几个条件：

- 参数少
- 工程实现简单
- 适用模型广
- 效果通常稳定
- 社区生态成熟

所以今天如果你说“PEFT 的默认工程路线是什么”，答案通常就是：

> 先试 LoRA。

### 9.3 LoRA 常见注入位置

通常会加在 Transformer 的线性层上，比如：

- `q_proj`
- `k_proj`
- `v_proj`
- `o_proj`
- `gate_proj`
- `up_proj`
- `down_proj`

不同模型命名不同，但思路一致：  
在关键线性变换上挂低秩适配器。

## 10. 主流方法二：QLoRA

### 10.1 QLoRA 是什么

`QLoRA` 可以理解为：

> 量化过的基座模型 + LoRA 微调

它通常会：

- 把基础模型以 4-bit 形式加载
- 冻结量化后的基座权重
- 在其上训练 LoRA adapter

### 10.2 它解决了什么问题

LoRA 已经很省，但大模型基座本身还是很大。  
QLoRA 进一步减少了“基座模型驻留显存”的开销。

因此它特别适合：

- 单卡显存有限
- 仍想微调更大模型
- 追求成本可控

### 10.3 典型场景

例如：

- 24GB 显卡
- 想训练比平时更大的模型
- 不想走全量微调

这时 QLoRA 往往是首选。

### 10.4 QLoRA 的代价

它不是完全免费：

- 训练流程更复杂
- 量化可能带来一定精度损失
- 某些情况下吞吐和数值稳定性需要更仔细调试

但从成本收益比看，它非常有价值。

## 11. 主流方法三：Prefix Tuning

### 11.1 Prefix Tuning 的位置

Prefix Tuning 属于“软提示”路线。

它做的不是：

- 直接改模型权重

而是：

- 学习一小段连续前缀表示
- 让这些表示参与注意力计算

### 11.2 它的核心直觉

不是改模型脑子，而是给模型塞一段机器可读的“隐藏前缀”，让模型在生成时带着这段前缀思考。

### 11.3 它和 LoRA 的区别

LoRA：

- 改的是线性层的有效映射

Prefix Tuning：

- 改的是注意力上下文中的前缀信息

它们都属于 PEFT，但控制信号进入模型的位置不同。

## 12. 主流方法四：Prompt Tuning

Prompt Tuning 比 Prefix Tuning 更轻。

它通常是：

- 学习少量虚拟 token embedding
- 把它们接到输入前面

它和 Prefix Tuning 的区别在于：

- Prompt Tuning 更偏输入层
- Prefix Tuning 更偏多层注意力内部

因此：

- Prompt Tuning 更轻
- 但控制力通常也更弱一些

## 13. 主流方法五：IA3

`IA3` 是一种非常省参数的方法。  
它不是像 LoRA 那样加低秩矩阵，而是通过更轻量的缩放方式调节模型内部路径。

它的特点通常是：

- 训练参数更少
- 推理开销也很低
- 在某些任务上很高效

但工程生态和“默认首选”地位通常不如 LoRA。

## 14. 方法之间怎么选

如果你只想先拿一个简单结论，可以记这张表。

| 方法 | 核心思路 | 参数量 | 工程主流度 | 常见用途 |
|---|---|---:|---|---|
| Full Fine-Tuning | 更新全部参数 | 最大 | 高 | 极致效果、资源充足 |
| LoRA | 低秩权重增量 | 低 | 很高 | 默认首选 |
| QLoRA | 量化基座 + LoRA | 很低 | 很高 | 显存受限 |
| Prefix Tuning | 学习注意力前缀 | 低 | 中 | 生成控制、研究理解 |
| Prompt Tuning | 学习输入软提示 | 很低 | 中 | 简单适配 |
| IA3 | 轻量缩放适配 | 极低 | 中 | 超低参数场景 |

### 14.1 如果你是第一次做项目

建议优先顺序：

1. LoRA
2. QLoRA
3. 再看 Prefix Tuning / Prompt Tuning / IA3

### 14.2 如果你是做研究或教学

你应该同时理解：

- 低秩路线
- 软提示路线
- 缩放控制路线

因为它们代表了 PEFT 的几种不同哲学。

## 15. PEFT 的优势

### 15.1 更低训练门槛

以前做微调可能要多卡大显存，现在很多任务可以：

- 单卡
- 小显存
- 较短实验周期

### 15.2 更容易做多任务

一个基座模型可以挂多个 adapter：

- 客服 adapter
- 摘要 adapter
- 代码 adapter
- 医疗术语 adapter

这对生产系统很有吸引力。

### 15.3 版本管理更轻

保存的是 adapter，而不是整份巨型权重。

### 15.4 更适合快速试错

你可以更快地尝试：

- 新数据
- 新模板
- 新超参数
- 新任务定义

## 16. PEFT 的局限

### 16.1 它不是永远替代 full fine-tuning

如果你需要：

- 极致性能
- 大规模领域迁移
- 深度改变模型知识结构

那 full fine-tuning 仍然可能更强。

### 16.2 不同任务敏感度不同

有些任务：

- LoRA 很稳
- Prefix Tuning 一般

有些任务则反过来更偏行为控制。

不能把一种方法套所有场景。

### 16.3 仍然需要好数据

PEFT 省的是参数，不是省数据质量。

如果你的数据：

- 模板混乱
- 标注噪声大
- 样本太少又不成体系

那 PEFT 一样会学歪。

### 16.4 可能存在上限

因为可训练参数少，所以表达能力天花板也可能更低。  
这是一种明确的 tradeoff。

## 17. PEFT 最适合哪些场景

适合：

- 你要在大模型上做任务适配
- 显存或预算有限
- 需要快速迭代多个任务版本
- 需要多 adapter 共用一个基座模型
- 你更看重成本收益比而不是理论最优

不太适合：

- 你有很充足资源，追求最强上限
- 任务和基础模型差异极大
- 你需要深度重塑模型能力，而不仅是适配

## 18. PEFT 的工程视角：它改变了什么工作流

在没有 PEFT 时，常见工作流是：

1. 选基座模型
2. 全量微调
3. 保存整份模型
4. 部署整份模型

有了 PEFT 后，工作流往往变成：

1. 选一个通用基座模型
2. 为每个任务训练一个 adapter
3. 保存 adapter
4. 推理时加载基座模型 + 指定 adapter

这会让模型工程更接近“平台化”：

- 一套基座
- 多个任务插件

## 19. Hugging Face `peft` 库是什么

在 Python 生态里，最常见的 PEFT 实践入口就是 Hugging Face 的 `peft` 库。

它做的事情很直接：

- 定义各种 PEFT 配置
- 把 adapter 注入基础模型
- 冻结不该训练的参数
- 提供保存、加载、切换 adapter 的统一接口

典型安装：

```bash
pip install peft transformers accelerate datasets
```

如果你要做 QLoRA，再加上：

```bash
pip install bitsandbytes
```

## 20. 第一个最小可运行示例：LoRA

先从最实用的 LoRA 开始。

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import Dataset
from peft import LoraConfig, get_peft_model, TaskType
import torch

model_name = "gpt2"

tokenizer = AutoTokenizer.from_pretrained(model_name)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(model_name)

lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules=["c_attn", "c_proj"],
    bias="none",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

samples = [
    {"text": "### Instruction:\n解释什么是神经网络。\n\n### Response:\n神经网络是一类通过多层参数变换学习输入到输出映射的模型。"},
    {"text": "### Instruction:\n解释什么是过拟合。\n\n### Response:\n过拟合是模型过度记住训练数据细节，导致泛化能力下降。"},
]

dataset = Dataset.from_list(samples)

def preprocess(example):
    encoded = tokenizer(
        example["text"],
        truncation=True,
        max_length=256,
        padding="max_length",
    )
    encoded["labels"] = encoded["input_ids"].copy()
    return encoded

tokenized_dataset = dataset.map(preprocess, remove_columns=dataset.column_names)

training_args = TrainingArguments(
    output_dir="./lora_demo_output",
    per_device_train_batch_size=2,
    num_train_epochs=5,
    learning_rate=2e-4,
    logging_steps=1,
    report_to="none",
    fp16=torch.cuda.is_available(),
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

trainer.train()
model.save_pretrained("./lora_demo_adapter")
tokenizer.save_pretrained("./lora_demo_adapter")
```

### 20.1 这段代码在做什么

这段代码的关键有四步。

#### 第一步：加载基础模型

```python
model = AutoModelForCausalLM.from_pretrained(model_name)
```

#### 第二步：定义 LoRA 配置

```python
lora_config = LoraConfig(...)
```

这里定义：

- `r`：低秩维度
- `lora_alpha`：缩放系数
- `lora_dropout`：正则化
- `target_modules`：把 LoRA 挂到哪些层

#### 第三步：把模型转换成 PEFT 模型

```python
model = get_peft_model(model, lora_config)
```

这一句之后：

- 原始模型大部分参数被冻结
- 只有 LoRA 相关参数会被训练

#### 第四步：正常训练

之后的训练流程和普通 `Trainer` 类似，只是可训练参数变少了。

## 21. QLoRA 最小配置示意

如果你显存更紧，可以把 LoRA 和量化结合。

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype="bfloat16",
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "你的模型",
    quantization_config=bnb_config,
    device_map="auto",
)

model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules="all-linear",
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
```

这个流程的重点是：

- 基座模型以低比特形式驻留
- LoRA adapter 仍然正常训练

它是今天非常常见的低成本微调路线。

## 22. Prefix Tuning 在 `peft` 里的最小配置

这也能帮助你把“PEFT 是家族不是单方法”这件事真正看懂。

```python
from peft import PrefixTuningConfig, get_peft_model, TaskType

prefix_config = PrefixTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=20,
    prefix_projection=True,
)

model = get_peft_model(model, prefix_config)
```

你会发现：

- 同样是 `get_peft_model`
- 但换了不同的配置类

这正是 `peft` 库的统一接口价值所在。

## 23. 保存与加载：PEFT 为什么适合多任务

训练完之后，你通常保存的是 adapter，而不是整份大模型。

### 23.1 保存

```python
model.save_pretrained("./my_adapter")
```

### 23.2 加载

```python
from transformers import AutoModelForCausalLM
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained("基础模型")
model = PeftModel.from_pretrained(base_model, "./my_adapter")
```

### 23.3 多 adapter 切换

你甚至可以在同一个基座模型上加载多个 adapter：

```python
model.load_adapter("./adapter_task2", adapter_name="task2")
model.load_adapter("./adapter_task3", adapter_name="task3")
model.set_adapter("task2")
```

这就是 PEFT 很适合做“一个底座，多套能力”的原因。

## 24. LoRA 最重要的几个超参数

如果你开始实际做项目，最先要理解的是 LoRA 的几个核心参数。

### 24.1 `r`

LoRA 的秩，决定 adapter 容量。

经验上：

- `4`：更轻
- `8`：常用起点
- `16`：更常见的稳妥选择
- `32 / 64`：更高容量，但更贵

### 24.2 `lora_alpha`

缩放系数，常见经验是：

```text
alpha ≈ 2 × r
```

例如：

- `r=8, alpha=16`
- `r=16, alpha=32`

### 24.3 `target_modules`

决定把 LoRA 挂在哪些层。

这很关键，因为：

- 挂的位置少，参数更省
- 挂的位置多，表达能力更强

常见起点：

- attention 相关层先挂
- 再视任务复杂度决定是否扩展到 MLP 层

### 24.4 `lora_dropout`

用于正则化，一般不需要太大，`0.05` 是常见起点。

## 25. PEFT 和数据质量的关系

这是实践里最容易被忽略的一点。

很多人以为：

- 只要我选了 LoRA / QLoRA
- 就能在小数据上轻松出效果

这不准确。

PEFT 省的是参数，不是省数据设计。  
你仍然需要：

- 统一的数据模板
- 清晰的任务定义
- 足够稳定的标注风格
- 合理的训练/验证切分

尤其是 instruction tuning 场景，格式漂移和风格不一致会明显影响结果。

## 26. PEFT 什么时候不够用

这也是必须说清楚的。

### 26.1 大规模领域迁移

如果你的目标是让模型深度适应某个非常不同的领域，比如：

- 极端专业语料
- 大规模风格迁移
- 复杂行为重塑

PEFT 可能不如 full fine-tuning 有上限。

### 26.2 模型本身能力不够

PEFT 是“适配器”，不是“魔法”。

如果基座模型本身就不擅长某项任务，PEFT 很难凭空创造能力。  
它更像是把已有潜力更好地引导出来。

### 26.3 你追求的是最强结果而不是最优成本比

如果资源充足、目标是极致性能，全量微调仍可能值得考虑。

## 27. PEFT 的典型项目决策流程

如果你要在真实项目中选路线，可以按下面思路。

### 情况 A：资源有限，想先快速做出结果

建议：

- 先 LoRA
- 如果显存更紧，再 QLoRA

### 情况 B：你在做教学、研究、方法比较

建议：

- LoRA
- Prefix Tuning
- Prompt Tuning
- IA3

最好都理解

### 情况 C：任务要求很强，资源也够

建议：

- 先用 PEFT 验证任务可行性
- 再决定是否上 full fine-tuning

这是很务实的流程：先低成本验证，再决定是否重投入。

## 28. PEFT 与推理部署的关系

PEFT 不只是训练问题，它也改变部署方式。

### 28.1 不合并 adapter

你可以：

- 基座模型单独存在
- 推理时动态挂 adapter

优点：

- 灵活
- 多任务切换方便

缺点：

- 部署链路稍复杂

### 28.2 合并 adapter

有些情况下可以把 adapter merge 回基座模型：

```python
merged_model = model.merge_and_unload()
```

优点：

- 推理更像普通模型
- 简化部署

缺点：

- 失去“一个基座多个 adapter”的灵活性

## 29. 常见误区

### 29.1 “PEFT 就等于 LoRA”

不对。LoRA 只是 PEFT 里最流行的方法之一。

### 29.2 “PEFT 一定比 full fine-tuning 差很多”

不一定。很多任务上，PEFT 的效果已经足够接近，成本却低很多。

### 29.3 “有了 PEFT，小显卡就什么都能训”

不对。显存压力虽然下降，但：

- 基座模型还是要装下
- 序列长度还是要考虑
- batch size 还是有限

### 29.4 “PEFT 不需要调参”

不对。尤其 LoRA 的：

- `r`
- `alpha`
- `target_modules`
- 学习率

都很重要。

### 29.5 “PEFT 可以替代高质量数据”

不能。数据质量始终是核心变量。

## 30. 一个建议的学习顺序

如果你是系统学习 PEFT，建议顺序如下：

1. Full Fine-Tuning 是什么  
2. PEFT 的问题意识  
3. LoRA  
4. QLoRA  
5. Prefix Tuning  
6. Prompt Tuning  
7. IA3  
8. 多 adapter 管理与部署

这样你会形成很清晰的层次：

- 为什么要 PEFT
- PEFT 有哪些路线
- 工程上默认路线是什么

## 31. 最后的总结

你可以把 PEFT 浓缩成这几句话：

- PEFT 是参数高效微调，不是某一种单独方法
- 它的目标是在冻结大部分基座权重的前提下完成任务适配
- 它主要节省训练参数、显存和存储成本
- LoRA 是今天最主流的 PEFT 工程方案
- QLoRA 是显存受限时非常实用的扩展
- Prefix Tuning、Prompt Tuning、IA3 代表了不同的 PEFT 设计路线
- PEFT 的成功依赖于基座模型能力、任务类型和数据质量

如果你只保留一句话，就保留这句：

> `PEFT` 的本质，是不重写整个大模型，而是用一个很小的可训练模块去“拨动”它已有的能力。

如果你愿意，我下一步可以继续接着补这几个方向中的任意一个：

1. `LoRA` 专题笔记  
2. `QLoRA` 专题笔记  
3. `Adapter / Prefix / Prompt Tuning` 横向对比笔记
