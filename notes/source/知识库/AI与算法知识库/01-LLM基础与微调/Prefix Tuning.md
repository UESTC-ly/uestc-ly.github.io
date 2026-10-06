# Prefix Tuning 详解与实操教程

## 1. 这份教程会讲什么

这是一份面向初学者到中级读者的 `Prefix Tuning` 教程，目标是让你在读完后能够回答下面几个问题：

- `Prefix Tuning` 到底是什么
- 它为什么能在冻结大模型参数的前提下完成任务适配
- 它和 `Prompt Tuning`、`P-Tuning v2`、`LoRA` 有什么区别
- 它在 Transformer 里具体作用在什么位置
- 如何用 Hugging Face `PEFT` 快速跑通一个可工作的 Prefix Tuning 实验
- 训练时常见的问题有哪些，应该怎么调

这份教程聚焦 `Causal LM` 场景，也就是最常见的自回归语言模型微调。如果你已经熟悉全量微调、LoRA、QLoRA，这篇教程可以把 `Prefix Tuning` 放到整个参数高效微调的地图里；如果你之前几乎没有接触过 PEFT，这篇教程也会先建立必要的直觉。

## 2. Prefix Tuning 是什么

一句话定义：

`Prefix Tuning` 是一种参数高效微调方法。它冻结原始大模型的参数，只训练一小段可学习的“前缀表示”，让模型在生成时把这段前缀当作额外上下文，从而改变输出行为。

这里最容易误解的地方在于“前缀”这个词。它不是单纯在输入文本前面拼几个自然语言 token，而是学习一组连续向量表示。更准确地说，在经典 Prefix Tuning 设定里，这些向量会进入每一层 Transformer 的注意力计算，作为额外的 `key/value` 前缀参与注意力。

所以它不是：

- 手写一段 prompt
- 把 prompt 固定住
- 然后希望模型自己学会适应

它是：

- 冻结基础模型
- 新增少量可训练参数
- 用这些参数生成各层共享或各层使用的 prefix 表示
- 让模型在每次推理时都“看到”这段可学习前缀

你可以把它理解为：不给老师换脑子，只给老师在每次答题前塞一份高度压缩、机器可读的“隐藏提示”。

## 3. 为什么会有 Prefix Tuning

在大模型时代，全量微调有三个明显问题：

1. 成本高  
   模型越大，需要更新和存储的参数越多，显存、训练时间、存储空间都会快速上涨。

2. 多任务部署不经济  
   如果你对同一个 7B 或 70B 基座模型做 10 个任务的全量微调，就要保存 10 份完整权重。

3. 迁移和实验慢  
   每次尝试一个新任务，都要改一整套权重，试错成本太高。

于是参数高效微调（PEFT, Parameter-Efficient Fine-Tuning）出现了。它的核心思想是：

- 尽量不改原模型
- 只训练一小部分新增参数
- 用很小的代价换取可接受的任务适配效果

`Prefix Tuning` 就是 PEFT 家族中的一条路线。它的思路和 LoRA 不同：LoRA 是给线性层加低秩增量；Prefix Tuning 是给注意力机制加可学习前缀。

## 4. 先建立一个直觉模型

假设你有一个已经很强的基础模型，它本身已经会：

- 理解自然语言
- 做基本推理
- 生成通顺文本

但是你希望它更偏向某种行为，比如：

- 用客服风格回答
- 输出更结构化
- 更偏摘要任务
- 更适应某个小领域的数据分布

一种办法是改模型内部权重。另一种办法是：不改原权重，只给它一个稳定、可学习的“开场信号”。

这个“开场信号”就是 Prefix Tuning 里的 prefix。

如果用人类类比：

- 全量微调像是重新训练一个专家
- LoRA 像是在专家脑内加几个小的专门模块
- Prefix Tuning 像是每次开会前先给专家看一页高度浓缩的 briefing

区别在于，这份 briefing 不是自然语言写的，而是一组模型能直接读懂的连续向量。

## 5. Prefix Tuning 在 Transformer 里作用在哪里

### 5.1 先回顾自注意力

标准自注意力里，输入隐藏状态会被映射成：

- `Q`：Query
- `K`：Key
- `V`：Value

然后计算：

```text
Attention(Q, K, V) = softmax(QK^T / sqrt(d)) V
```

直观来说：

- `Q` 表示“我现在在找什么”
- `K` 表示“每个位置提供了什么线索”
- `V` 表示“每个位置真正携带的信息”

### 5.2 Prefix Tuning 做了什么

Prefix Tuning 会额外引入一组可训练前缀向量，把它们变成前缀 `K_p` 和 `V_p`，再和原始序列的 `K`、`V` 拼接：

```text
K' = [K_p ; K]
V' = [V_p ; V]
```

然后注意力变成：

```text
Attention(Q, K', V') = softmax(QK'^T / sqrt(d)) V'
```

这意味着什么？

- 模型在看原始输入之前，先多了一批“额外可参考的位置”
- 这些位置不是用户文本，而是训练出来的向量
- 它们会影响每个 token 的注意力分配
- 于是生成行为发生偏移

这个偏移不需要修改原模型参数，只需要训练这批前缀参数。

### 5.3 为什么说它比 Prompt Tuning 更“深入”

`Prompt Tuning` 通常是在输入 embedding 层面加虚拟 token。它主要影响输入起点。

`Prefix Tuning` 则是直接给注意力层提供额外的 `K/V`。这相当于把控制信号插进了 Transformer 的内部计算路径，而不只是输入端，因此通常比单纯的 prompt embedding 更有控制力。

## 6. 数学上怎么理解 Prefix Tuning

下面给一个足够用的数学版本，不追求论文式严密推导，但要让你知道训练目标到底是什么。

设基础模型参数为：

```text
θ
```

在 Prefix Tuning 中，`θ` 冻结不动，只训练 prefix 参数：

```text
φ
```

对每个任务样本 `(x, y)`，训练目标仍然是最小化条件语言模型损失：

```text
L(φ) = - Σ log P(y_t | x, y_<t ; θ, φ)
```

注意这里：

- `θ` 是固定的
- 只有 `φ` 更新
- `φ` 决定了 prefix 的表示
- prefix 会参与各层注意力，进而影响输出概率分布

因此它本质上仍然是标准监督学习，只是“可训练的对象”从全模型权重，变成了一小段 prefix 参数。

### 6.1 Prefix 参数从哪里来

最直接的方式是：

- 设定 `m` 个虚拟 token
- 给每个虚拟 token 一个可训练 embedding
- 再通过一个小 MLP 投影成每层所需的 prefix `K/V`

这就是很多实现里的 `prefix_projection=True` 背后的想法。

### 6.2 为什么要 projection

如果直接把一组小 embedding 拿去当所有层的 prefix，表达能力可能不够。加一个小 MLP 投影后：

- 容量更强
- 优化更稳定
- 更容易适配不同层的表示空间

代价是多一点点训练参数，但通常仍然非常小。

## 7. Prefix Tuning、Prompt Tuning、P-Tuning v2、LoRA 的区别

这几个名字很容易混。先给结论，再解释。

| 方法 | 核心做法 | 改动位置 | 参数量 | 常见特点 |
|---|---|---|---:|---|
| Prompt Tuning | 学习少量虚拟输入 token | 输入 embedding | 极少 | 最轻量，但控制力偏弱 |
| Prefix Tuning | 学习注意力前缀 | 注意力 `K/V` 路径 | 很少 | 比 Prompt Tuning 更强 |
| P-Tuning v2 | 深层 prompt/prefix 化 | 多层表示 | 很少 | 常用于增强稳定性和效果 |
| LoRA | 学习权重增量的低秩分解 | 线性层权重 | 很少 | 现在最常用，效果稳 |

### 7.1 Prompt Tuning vs Prefix Tuning

相同点：

- 都冻结大模型
- 都训练很少的参数
- 都可以视为“软提示”

不同点：

- Prompt Tuning 更接近“只在输入层学几个 embedding”
- Prefix Tuning 更接近“把可学习信号送进每层注意力”

因此 Prefix Tuning 往往更适合需要更强控制力的场景。

### 7.2 Prefix Tuning vs LoRA

这是最有实际价值的比较。

Prefix Tuning：

- 不改原线性层权重
- 通过前缀影响注意力
- 在某些生成控制任务上很自然

LoRA：

- 直接对线性变换加低秩增量
- 适用范围更广
- 社区生态更成熟
- 工程上通常更常用

如果你问“今天实际项目里优先学哪个”，答案通常是 `LoRA`。  
如果你问“想理解 PEFT 的不同路线、知道软前缀是怎么回事”，那 `Prefix Tuning` 很值得学。

## 8. Prefix Tuning 的优点与局限

### 8.1 优点

#### 参数少

它只训练 prefix 相关参数，通常远小于全量微调。

#### 适合多任务切换

同一个基座模型可以挂多个不同 prefix，用很小的存储代价切换任务。

#### 不破坏基础模型

基础模型权重不改，管理更简单，也更利于复用和回滚。

#### 训练成本低

对显存和算力的要求明显低于全量微调。

### 8.2 局限

#### 表达能力有上限

如果任务变化很大，仅靠 prefix 可能不足以获得最优结果。

#### 工程主流度不如 LoRA

今天大多数开源实践和教程更偏 LoRA/QLoRA，因此 Prefix Tuning 的资料和经验相对少一些。

#### 推理时会有额外前缀开销

虽然很小，但并不是完全零成本。

#### 对任务类型更敏感

不是所有任务都能从 prefix 路线中获得和 LoRA 一样稳定的收益。

## 9. 什么场景适合 Prefix Tuning

适合：

- 你想理解软提示和 PEFT 的内部机制
- 你只想训练非常少的参数
- 你更关注“引导生成行为”而不是大规模改写模型知识
- 你要在一个基座模型上挂多个轻量适配器

不太适合：

- 任务和原模型能力差异非常大
- 你追求当前最主流、最稳妥的工程路线
- 你需要最强的泛化效果，而不是最小参数量

## 10. Prefix Tuning 的核心超参数

### 10.1 `num_virtual_tokens`

这是最关键的超参数之一，表示前缀长度，也就是虚拟 token 的数量。

你可以粗略理解为：给模型的“隐藏 briefing”有多长。

- 太小：表达能力不够
- 太大：训练更慢，也可能更难优化

常见起点：

- 小模型或简单任务：`10 ~ 20`
- 稍复杂任务：`20 ~ 50`

### 10.2 `prefix_projection`

是否用一个小 MLP 把 prefix embedding 投影成更适合各层使用的表示。

一般建议：

- 先开：`True`
- 如果你明确想要最轻量实验，再试 `False`

### 10.3 学习率

因为只训练少量参数，学习率往往会比全量微调大一些。一个常见起点是：

```text
1e-4 ~ 5e-4
```

如果训练不稳定，可以从 `1e-4` 开始。

### 10.4 训练轮数

Prefix 参数少，收敛可能会比较快。常见做法：

- 先跑 1 到 3 个 epoch 看验证集趋势
- 不要一开始就堆很多 epoch

## 11. 实操前的环境准备

本教程使用 Hugging Face 生态里的 `transformers + peft + datasets`。

建议环境：

- Python 3.10+
- PyTorch 2.x
- `transformers`
- `peft`
- `datasets`
- `accelerate`

安装命令：

```bash
pip install torch transformers peft datasets accelerate
```

如果你后续要混合量化或更复杂的 PEFT 方案，再补装 `bitsandbytes`。  
但纯 Prefix Tuning 的最小实验，前面的依赖通常就够了。

## 12. 第一个可运行的 Prefix Tuning 示例

下面给一个尽量简洁但完整的最小可运行例子。这个例子用的是 `gpt2`，不是因为它最强，而是因为：

- 体量小
- API 简单
- 适合先跑通流程

如果你后面要上生产或做更像样的中文任务，可以换成更合适的基础模型。

### 12.1 完整训练脚本

```python
import torch
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    default_data_collator,
)
from peft import PrefixTuningConfig, get_peft_model, TaskType


model_name = "gpt2"

tokenizer = AutoTokenizer.from_pretrained(model_name)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(model_name)

prefix_config = PrefixTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=20,
    prefix_projection=True,
)

model = get_peft_model(model, prefix_config)
model.print_trainable_parameters()


samples = [
    {
        "text": "### Instruction:\n请用一句话解释什么是机器学习。\n\n### Response:\n机器学习是让模型从数据中学习规律并用于预测或决策的方法。"
    },
    {
        "text": "### Instruction:\n请解释什么是梯度下降。\n\n### Response:\n梯度下降是一种通过沿损失函数下降方向更新参数来最小化误差的优化方法。"
    },
    {
        "text": "### Instruction:\n什么是过拟合？\n\n### Response:\n过拟合是模型过度记住训练数据细节，导致在新数据上表现变差的现象。"
    },
]

dataset = Dataset.from_list(samples)


def preprocess(example):
    result = tokenizer(
        example["text"],
        truncation=True,
        max_length=256,
        padding="max_length",
    )
    result["labels"] = result["input_ids"].copy()
    return result


tokenized_dataset = dataset.map(preprocess, remove_columns=dataset.column_names)


training_args = TrainingArguments(
    output_dir="./prefix_tuning_output",
    per_device_train_batch_size=2,
    num_train_epochs=10,
    learning_rate=1e-4,
    logging_steps=1,
    save_strategy="epoch",
    fp16=torch.cuda.is_available(),
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=default_data_collator,
)

trainer.train()

model.save_pretrained("./prefix_tuning_adapter")
tokenizer.save_pretrained("./prefix_tuning_adapter")
```

### 12.2 这段代码在做什么

#### 第一步：加载基础模型

```python
model = AutoModelForCausalLM.from_pretrained(model_name)
```

这里载入一个普通的自回归语言模型。

#### 第二步：定义 Prefix Tuning 配置

```python
prefix_config = PrefixTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=20,
    prefix_projection=True,
)
```

关键点：

- `task_type=TaskType.CAUSAL_LM` 表示这是自回归生成任务
- `num_virtual_tokens=20` 指定前缀长度
- `prefix_projection=True` 让 prefix 通过一个小投影层

#### 第三步：把 PEFT 包到模型上

```python
model = get_peft_model(model, prefix_config)
```

执行完这一步之后：

- 原模型权重被冻结
- prefix 相关参数变成可训练
- 后续 `Trainer` 更新的就是这些 prefix 参数

#### 第四步：准备训练数据

例子里用了一个非常小的 toy dataset，只是为了让你能跑通流程。

真正做任务时，你应该：

- 换成真实数据集
- 保持统一的指令模板
- 做训练集 / 验证集划分

#### 第五步：训练和保存

保存的不是整份基础模型，而是 prefix adapter。

这正是 PEFT 的核心价值之一：轻量。

## 13. 如何加载训练好的 Prefix Adapter

训练完后，你通常会得到一份很小的 adapter 目录。推理时可以把它重新加载到基础模型上。

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base_model_name = "gpt2"
adapter_path = "./prefix_tuning_adapter"

tokenizer = AutoTokenizer.from_pretrained(adapter_path)
base_model = AutoModelForCausalLM.from_pretrained(base_model_name)
model = PeftModel.from_pretrained(base_model, adapter_path)

prompt = "### Instruction:\n请解释什么是反向传播。\n\n### Response:\n"
inputs = tokenizer(prompt, return_tensors="pt")

with torch.no_grad():
    output = model.generate(
        **inputs,
        max_new_tokens=80,
        do_sample=True,
        top_p=0.9,
        temperature=0.8,
    )

print(tokenizer.decode(output[0], skip_special_tokens=True))
```

这段代码的含义是：

- 先加载基础模型
- 再把 prefix adapter 附着上去
- 推理时模型会自动使用 prefix

## 14. 如何把最小例子改成真实项目

一个 toy 脚本跑通后，下一步通常是把它变成真实训练流程。建议按下面顺序做。

### 14.1 换成真实数据集

例如你的数据可能长这样：

```json
{"instruction": "请概括这段文本", "input": "......", "output": "......"}
{"instruction": "把这段客服对话改写为工单摘要", "input": "......", "output": "......"}
```

然后统一拼装成训练文本：

```python
def format_example(example):
    return (
        f"### Instruction:\n{example['instruction']}\n\n"
        f"### Input:\n{example['input']}\n\n"
        f"### Response:\n{example['output']}"
    )
```

重点不是模板长什么样，而是：

- 保持一致
- 让训练格式和推理格式尽量一致
- 不要今天一种模板，明天又换一套

### 14.2 加验证集

只看训练损失是不够的。至少要有：

- `train split`
- `validation split`

否则你很难判断：

- 模型是真的学会了
- 还是只是记住了训练样本

### 14.3 加评估样本

准备一批固定评估输入，每次训练后都生成结果做对比。  
Prefix Tuning 的参数很少，训练虽然轻，但行为变化未必直观。固定评估样本可以帮你快速判断模型到底学到了什么。

## 15. 调参建议

Prefix Tuning 的调参空间不算大，但几个关键参数影响很明显。

### 15.1 先调 `num_virtual_tokens`

建议顺序：

1. 从 `10` 或 `20` 开始
2. 如果效果明显不够，再试 `30`、`50`
3. 不要一开始就拉很大

经验上：

- 简单风格控制任务：小一点就可能够用
- 复杂任务适配：通常需要更长 prefix

### 15.2 学习率从中等偏大开始

因为只训练小量参数，所以常见学习率会比全量微调大一些。

推荐起点：

```text
1e-4
```

如果收敛慢，可以试：

```text
2e-4 或 5e-4
```

如果训练不稳定、loss 震荡明显，再往下调。

### 15.3 训练轮数别贪多

参数少不代表一定要训很久。建议：

- 先跑 1 到 3 epoch 看趋势
- 用验证集判断是否继续

### 15.4 batch size 不够就用梯度累积

如果显存紧张：

```python
gradient_accumulation_steps=4
```

通常比盲目减小上下文长度更合适。

## 16. Prefix Tuning 的常见坑

### 16.1 把它当成“自然语言 prompt 优化”

这是最常见误区。

Prefix Tuning 学的不是一段人类可读文本，而是一组连续参数。它虽然叫 prefix，但本质是软前缀，不是手写 prompt engineering。

### 16.2 训练数据模板不一致

如果训练时样本格式混乱，Prefix Tuning 这种小参数方法更容易学歪，因为它本身容量有限，对格式漂移更敏感。

建议：

- 固定模板
- 固定分隔符
- 固定指令风格

### 16.3 期望它替代全量微调

Prefix Tuning 很强，但它不是万能的。

如果任务需要：

- 大幅改变模型知识结构
- 适应极强领域偏移
- 提升复杂推理深度

那 Prefix Tuning 可能不是最优选。

### 16.4 只看 loss，不看生成质量

Prefix Tuning 最终作用在生成行为上，所以一定要看生成样例。  
训练 loss 下降，不代表输出就一定符合预期。

### 16.5 忽略基座模型本身的能力边界

Prefix Tuning 不是给弱模型“凭空加脑子”。  
它更像是在已有能力基础上做引导、偏置和适配。

如果基础模型本身就不擅长某类任务，只靠 prefix 很难逆天改命。

## 17. Prefix Tuning 与 LoRA 的实战选择建议

如果你是第一次真正做 PEFT 项目，可以这样判断：

### 选 Prefix Tuning，当你：

- 想学习软前缀机制
- 想做非常轻量的行为引导
- 想研究注意力前缀对生成的影响
- 想在论文复现或教学场景里理解 PEFT 分支

### 选 LoRA，当你：

- 想尽快落地项目
- 想获得更稳妥的工程效果
- 想复用最多社区经验
- 需要更常见的生产部署路径

换句话说：

- `Prefix Tuning` 很适合学原理、做研究、做轻量适配
- `LoRA` 更像今天的默认工程答案

## 18. 一个更贴近真实任务的训练模板

下面给一个更像真实项目的训练骨架，保留关键部分，方便你自己扩展。

```python
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    default_data_collator,
)
from peft import PrefixTuningConfig, get_peft_model, TaskType


model_name = "你的基础模型"
dataset_path = "train.jsonl"

tokenizer = AutoTokenizer.from_pretrained(model_name)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
)

peft_config = PrefixTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=30,
    prefix_projection=True,
)

model = get_peft_model(model, peft_config)

dataset = load_dataset("json", data_files={"train": dataset_path})


def format_and_tokenize(example):
    text = (
        f"### Instruction:\n{example['instruction']}\n\n"
        f"### Input:\n{example.get('input', '')}\n\n"
        f"### Response:\n{example['output']}"
    )
    encoded = tokenizer(
        text,
        truncation=True,
        max_length=512,
        padding="max_length",
    )
    encoded["labels"] = encoded["input_ids"].copy()
    return encoded


train_dataset = dataset["train"].map(
    format_and_tokenize,
    remove_columns=dataset["train"].column_names,
)

args = TrainingArguments(
    output_dir="./prefix_run",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    learning_rate=1e-4,
    warmup_ratio=0.03,
    logging_steps=10,
    save_strategy="epoch",
    bf16=torch.cuda.is_available(),
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    data_collator=default_data_collator,
)

trainer.train()
model.save_pretrained("./prefix_adapter")
tokenizer.save_pretrained("./prefix_adapter")
```

这份模板已经足够改成真实项目脚手架：

- 换模型名
- 换数据文件
- 增加验证集和评估逻辑
- 加日志和实验记录

## 19. 如何判断训练是否成功

不要只问“有没有报错”。真正要判断的是：prefix 是否真的把模型行为推向了你想要的方向。

建议用下面三层判断标准。

### 19.1 第一层：训练是否正常收敛

观察：

- loss 是否下降
- 是否出现 NaN
- 是否明显震荡

### 19.2 第二层：固定样本输出是否改善

准备一套固定 prompt，例如 20 条，然后比较：

- 基座模型输出
- 加 prefix 后输出

重点看：

- 是否更符合任务格式
- 是否更贴近目标风格
- 是否更稳定

### 19.3 第三层：真实任务指标是否提升

如果是摘要任务，可能看：

- ROUGE
- BERTScore
- 人工评审

如果是分类或抽取任务，可能看：

- Accuracy
- F1
- Exact Match

Prefix Tuning 的成败，不是看你训没训完，而是看这些指标和样例是否真的变好。

## 20. 常见问题解答

### Q1：Prefix Tuning 会修改基础模型参数吗？

不会。标准 Prefix Tuning 会冻结基础模型，只训练 prefix 相关参数。

### Q2：Prefix Tuning 学出来的是自然语言吗？

不是。它学出来的是连续向量表示，不是人类可读文本。

### Q3：它和系统提示词有什么关系？

可以类比成“更底层、可训练、不可读的系统提示词”，但两者不等价。Prefix Tuning 直接作用于模型内部注意力路径，系统提示词只是普通文本输入。

### Q4：Prefix Tuning 一定比 Prompt Tuning 好吗？

不一定，但通常控制力更强，因为它不只作用在输入层。

### Q5：Prefix Tuning 和 LoRA 谁更好？

没有绝对答案。工程上 LoRA 更常用；学习机制和做轻量实验时，Prefix Tuning 很有价值。

## 21. 学完 Prefix Tuning 之后下一步该学什么

推荐顺序：

1. `Prompt Tuning`  
   先看最简单的软提示思路。

2. `Prefix Tuning`  
   理解如何把控制信号送进注意力内部。

3. `P-Tuning v2`  
   看深层软提示如何改进表现。

4. `LoRA / QLoRA`  
   进入今天最主流的工程路线。

如果你的目标是“真正做项目”，建议下一站直接去学 `LoRA`。  
如果你的目标是“彻底理解 PEFT 家族”，那就继续比较这些方法的结构差异。

## 22. 总结

`Prefix Tuning` 的核心思想可以浓缩成一句话：

> 冻结基础模型，只训练一小段可学习前缀，把它送进注意力机制，借此改变模型的生成行为。

你可以记住以下四点：

- 它是 PEFT，不是全量微调
- 它学习的是连续前缀，不是自然语言 prompt
- 它主要通过注意力的 `K/V` 路径发挥作用
- 它是理解软提示类方法的重要一环，但工程主流通常仍然是 LoRA

如果你只是想“知道它是什么”，到这里已经够了。  
如果你想真正会用它，建议你下一步做两件事：

1. 用本教程的最小示例先跑通一遍
2. 再把 toy dataset 换成你自己的真实数据，开始做小规模验证

当你能稳定比较“基座输出”和“prefix 输出”的差异时，你就真正掌握 Prefix Tuning 了。
