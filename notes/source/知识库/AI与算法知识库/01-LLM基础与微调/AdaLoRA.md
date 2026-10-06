# AdaLoRA 学习与实战入门

## 你会学到什么

读完这份笔记，你应该能回答下面几个问题：

- AdaLoRA 要解决什么问题
- 它和普通 LoRA、QLoRA 的差别是什么
- `init_r`、`target_r`、`tinit`、`tfinal`、`deltaT` 分别控制什么
- 怎样在 Hugging Face PEFT 里写出一个最小可用的 AdaLoRA 配置
- 训练时常见的不收敛、效果差、模块名不匹配等问题该怎么排查

这份文档面向已经知道“微调大模型”大概在做什么，但还没有系统理解 AdaLoRA 的读者。

---

## 1. 为什么会有 AdaLoRA

LoRA 的核心思想是：不要更新整套大模型权重，而是在某些线性层旁边挂上低秩矩阵，只训练这些额外参数。

它的优点很明显：

- 显存占用低
- 训练参数少
- 训练和保存都便宜
- 可以针对不同任务保存多个 adapter

但标准 LoRA 有一个天然限制：**每个被注入的层，通常都用同一个 rank `r`**。

这会带来两个问题：

1. 不同层的重要性并不一样，但 LoRA 往往给它们分配一样多的参数预算。
2. 你事先选的 `r` 往往是拍脑袋的，太小容易欠拟合，太大又浪费预算。

AdaLoRA 的思路就是：**不要把 rank 当成固定常数，而是让模型在训练过程中动态决定“哪些层更值得高 rank，哪些层可以降 rank”。**

所以，AdaLoRA 不是在推翻 LoRA，而是在 LoRA 的框架上做“参数预算的动态分配”。

---

## 2. 一句话理解 AdaLoRA

如果把 LoRA 看成“给每一层都发一样多的训练经费”，那么 AdaLoRA 就是“先给得宽松一点，再根据训练中观察到的价值，逐步把经费重新分配给更重要的层”。

它通常会经历三个阶段：

1. 先用较高的初始 rank 开始训练，让各层都有表达能力。
2. 训练过程中定期评估各层的重要性，削减不那么重要的方向，把预算让给更关键的层。
3. 到某个时间点后停止 rank 调整，固定最终预算，继续把模型收敛好。

这也是为什么 AdaLoRA 配置里会有：

- `init_r`：一开始给多少 rank
- `target_r`：最后平均想收缩到多少 rank
- `tinit`：从第几步之后开始做自适应裁剪
- `tfinal`：到第几步停止裁剪，进入最终收敛阶段
- `deltaT`：每隔多少步更新一次 rank 分配

---

## 3. AdaLoRA、LoRA、QLoRA 有什么区别

| 方法 | 核心目标 | 主要节省什么 | rank 是否固定 | 典型场景 |
|---|---|---|---|---|
| LoRA | 少量参数微调 | 可训练参数、显存 | 是 | 通用起点，先做 baseline |
| AdaLoRA | 动态分配低秩预算 | 参数预算利用率 | 否 | 想在有限预算下榨出更高效果 |
| QLoRA | 量化底座再做 LoRA | 底座显存 | 通常固定 | 大模型装不进显存时优先考虑 |

要注意一件事：

- **LoRA / AdaLoRA** 主要在回答“adapter 怎么设计”
- **QLoRA** 主要在回答“底座模型怎么更省显存地加载”

所以它们关注的不是同一个层面。实际工程里，大家通常先拿 LoRA 做基线，再决定是否要切到 AdaLoRA；如果显存本身就不够，则先考虑 QLoRA 路线。

---

## 4. 什么时候适合用 AdaLoRA，什么时候不适合

### 适合

- 你已经会跑标准 LoRA，但怀疑统一 rank 分配不够合理
- 训练预算比较紧，希望把有限参数尽量放到更关键的层
- 模型较大、层数较多，不同层对任务的贡献很可能不均匀
- 你愿意为更好的参数分配，多接受一点训练配置复杂度

### 不太适合

- 你还没有跑通过普通 LoRA baseline
- 你的任务非常小，数据量也很小，先把流程跑通比“动态 rank”更重要
- 你需要最稳定、最容易复现的方案，暂时不想引入额外调度逻辑
- 你的主要瓶颈是底座显存，而不是 adapter 预算利用率

实务建议很简单：**先有 LoRA baseline，再考虑 AdaLoRA。**

---

## 5. 核心心智模型

理解 AdaLoRA，抓住下面三点就够了。

### 5.1 LoRA 更新本质上是低秩增量

标准微调是直接更新原始权重 `W`。LoRA 则把更新写成一个低秩增量：

```text
W' = W + ΔW
ΔW = B @ A
```

这里的 rank `r` 决定了这个增量的容量。`r` 越大，表达能力通常越强，但可训练参数也越多。

### 5.2 标准 LoRA 的 rank 通常是固定的

如果你给每个目标层都设置 `r=8`，那它们就全都用 8。问题在于：

- 有些层可能值得 `r=16`
- 有些层可能 `r=4` 就够了

固定 rank 的好处是简单，坏处是容易平均主义。

### 5.3 AdaLoRA 的关键是“预算重分配”

AdaLoRA 会从比较高的初始 rank 出发，然后根据训练中估计出的重要性，逐步把预算压缩到目标平均 rank。

这意味着：

- 它不是一开始就知道哪层重要
- 它需要训练一段时间后再开始调 rank
- 它通常比固定 LoRA 更依赖合适的训练步数设置

如果训练还没热起来就开始大幅裁剪，效果往往会掉得很明显。

---

## 6. 关键参数怎么理解

下面这些是你最需要会调的参数。

| 参数 | 作用 | 怎么理解 |
|---|---|---|
| `init_r` | 初始 rank | 先给足一些容量，方便模型自己“证明”哪些层重要 |
| `target_r` | 最终平均 rank | 训练后期希望压缩到的预算水平 |
| `tinit` | 开始自适应的步数 | 训练前期的 warmup，太早会误判层重要性 |
| `tfinal` | 停止裁剪的步数 | 到这里之后不再改 rank，只做最终收敛 |
| `deltaT` | rank 更新间隔 | 每隔多少步重新做一次预算调整 |
| `beta1` / `beta2` | 平滑系数 | 用来平滑重要性估计，减少抖动 |
| `orth_reg_weight` | 正交正则强度 | 约束低秩方向，帮助训练更稳定 |
| `target_modules` | 注入哪些层 | 需要和模型结构名字对上 |

一个实用的经验是：

- `init_r` 通常要明显大于 `target_r`
- `tinit` 不要太早
- `tfinal` 不要太晚，否则 rank 一直在变，最后收敛阶段不够

如果你完全没有经验，可以先从下面这个思路起步：

- `init_r = 4 x target_r` 左右作为起点
- `tinit` 放在训练前期
- `tfinal` 放在总步数的中后段
- `deltaT` 用一个中等频率，不要每步都更新

这只是起始经验，不是硬规则。总训练步数、数据规模、模型大小都会影响最佳设置。

---

## 7. 一个最小可用的 PEFT 示例

下面这段代码演示如何在 Hugging Face PEFT 里启用 AdaLoRA。示例偏“骨架代码”，你可以直接替换成自己的模型、数据集和 Trainer。

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import AdaLoraConfig, TaskType, get_peft_model

model_name = "Qwen/Qwen2.5-1.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto"
)

adalora_config = AdaLoraConfig(
    task_type=TaskType.CAUSAL_LM,
    init_r=32,
    target_r=8,
    tinit=200,
    tfinal=1000,
    deltaT=10,
    beta1=0.85,
    beta2=0.85,
    orth_reg_weight=0.5,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
)

model = get_peft_model(model, adalora_config)
model.print_trainable_parameters()
```

这段代码里最重要的不是语法，而是配置背后的意思：

- `init_r=32`：开始时给足表达能力
- `target_r=8`：最终希望收缩到更省的预算
- `tinit=200`：先训练 200 步再开始动 rank
- `tfinal=1000`：到 1000 步后停止 rank 调整
- `deltaT=10`：每 10 步更新一次预算分配

如果你把它接到 Trainer 或 SFT 训练循环里，流程和普通 PEFT 没有本质差异：

```python
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir="./adalora_output",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    num_train_epochs=3,
    logging_steps=10,
    save_steps=200,
    bf16=True,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset
)

trainer.train()
model.save_pretrained("./adalora_adapter")
tokenizer.save_pretrained("./adalora_adapter")
```

如果你的环境报错 `ModuleNotFoundError: No module named 'peft'`，先安装：

```bash
pip install peft transformers accelerate
```

---

## 8. `target_modules` 应该怎么选

这一步经常比调 `init_r` 更容易踩坑，因为很多失败根本不是 AdaLoRA 本身，而是模块名没对上。

常见写法如下：

### Llama / Qwen / Mistral 一类

```python
target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"]
```

如果你想把 MLP 也纳入，可以继续加：

```python
target_modules = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj"
]
```

### GPT 风格模型

常见名字可能像这样：

```python
target_modules = ["c_attn", "c_proj"]
```

### 如何确认自己模型的模块名

最稳妥的办法是打印模块名看一遍：

```python
for name, module in model.named_modules():
    if "proj" in name or "attn" in name:
        print(name)
```

如果模块名没匹配上，最常见的现象是：

- 训练参数数量异常少
- `get_peft_model` 后几乎没挂上 adapter
- 训练看起来在跑，但指标基本不动

---

## 9. 训练时到底发生了什么

很多人用 AdaLoRA 时，代码能跑，但脑中没有时间轴。其实把训练过程按时间拆开，就没那么抽象。

### 阶段一：高 rank 热身

训练刚开始时，模型还不知道哪些层重要，所以先用 `init_r` 提供比较宽松的容量。

这时候的重点不是省参数，而是让不同层有机会表现出价值。

### 阶段二：动态预算分配

从 `tinit` 开始，AdaLoRA 会按 `deltaT` 的频率更新 rank 分配。

这一阶段的目标是：

- 保留更重要的方向
- 压缩不那么关键的方向
- 逐步逼近 `target_r`

### 阶段三：固定预算做最终收敛

到了 `tfinal` 之后，rank 分配不再变化，训练进入稳定收敛阶段。

如果没有这个阶段，模型一直在边变结构边训练，最后往往收不稳。

---

## 10. 调参建议

下面不是唯一正确答案，但足够当起点。

### 10.1 先确定普通 LoRA baseline

先用固定 rank 的 LoRA 跑出一个可接受结果，再把同样的数据、训练步数、学习率迁移到 AdaLoRA。

这样你能判断：

- 是 AdaLoRA 带来了提升
- 还是数据和训练流程本身就没跑通

### 10.2 `init_r` 和 `target_r` 不要贴得太近

如果二者太接近，AdaLoRA 的自适应空间就很小，最后和普通 LoRA 的差别也不会太大。

常见起点：

- 小实验：`init_r=16`，`target_r=8`
- 中等实验：`init_r=32`，`target_r=8` 或 `16`
- 更重视表达能力：`init_r=64`，`target_r=16`

### 10.3 `tinit` 太早通常不好

训练太早时，层的重要性估计还不稳定。你如果在模型刚热身时就开始裁剪，容易把本来后面会变重要的方向提前砍掉。

### 10.4 给 `tfinal` 留出收尾空间

如果你到训练最后几步还在改 rank，最终很容易出现：

- loss 还在波动
- eval 指标不稳定
- 不同 seed 差异变大

所以通常要让 `tfinal` 早于训练结束，给模型留一段“结构固定”的收敛区间。

### 10.5 不要把所有问题都归因于 AdaLoRA

很多效果差的根因其实是：

- 数据格式不对
- 指令模板不一致
- 学习率太高
- `target_modules` 没选对
- batch 太小导致训练噪声过大

先排这些，再怀疑算法本身。

---

## 11. 常见错误与排查

### 11.1 报错：找不到 `AdaLoraConfig`

可能原因：

- 没装 `peft`
- 安装的 `peft` 版本太旧

处理方式：

```bash
pip install -U peft transformers accelerate
```

### 11.2 训练参数数量不符合预期

通常是 `target_modules` 没命中。

检查方法：

- 打印 `model.print_trainable_parameters()`
- 检查 `named_modules()` 里的真实层名
- 先只挂注意力层，确认流程没问题，再扩大范围

### 11.3 loss 下降慢，或者效果不如固定 LoRA

先检查：

- `target_r` 是否压得过低
- `tinit` 是否太早
- `tfinal` 是否太晚
- 数据量是否太少，不足以支撑动态预算学习

如果数据很少，固定 LoRA 往往更稳。

### 11.4 训练不稳定，波动大

可以尝试：

- 降低学习率
- 增大有效 batch size
- 把 `deltaT` 调大，让 rank 更新不要太频繁
- 适度调整 `orth_reg_weight`

### 11.5 保存后推理效果不对

确认下面几件事：

- 推理时加载的是 adapter 而不是裸底座
- tokenizer 与底座模型匹配
- 训练和推理用的是同一套 prompt 模板

---

## 12. 和普通 LoRA 相比，AdaLoRA 的真实 trade-off

AdaLoRA 的优点不是“无脑更强”，而是**更聪明地使用有限预算**。这意味着它天然带着 trade-off：

### 优点

- 相同预算下，可能比固定 rank 更有效
- 能自动学到不同层的重要性差异
- 比手工为每层分别设 rank 更省人力

### 代价

- 配置更复杂
- 对训练步数更敏感
- 调参空间更大
- 如果 baseline 都没跑稳，问题定位更麻烦

所以工程上最稳的策略通常是：

1. 先用普通 LoRA 建基线
2. 再用 AdaLoRA 做“预算分配优化”
3. 最后再看是否值得和量化、分布式训练等手段叠加

---

## 13. 一个简单的上手流程

如果你现在就要在项目里试 AdaLoRA，可以按这个顺序：

1. 先跑通普通 LoRA，确认数据、模板、评测流程没问题。
2. 选一版能工作的 `target_modules`。
3. 把 LoRA 换成 AdaLoRA，先用保守配置，例如 `init_r=32`、`target_r=8`。
4. 观察训练曲线和验证集指标，不要只看 loss。
5. 如果效果差，先查模块名和训练步数，再调 rank 调度参数。
6. 只有在 baseline 稳定后，才去尝试更激进的压缩。

---

## 14. 总结

AdaLoRA 可以看成 LoRA 的“动态 rank 版本”。

它解决的核心问题不是“能不能低成本微调”，因为 LoRA 已经解决了这个问题；它解决的是：**在同样有限的 adapter 预算下，能不能把参数更合理地分给更重要的层。**

你真正要记住的是这三句话：

- LoRA 是固定 rank，AdaLoRA 是动态分配 rank。
- AdaLoRA 的关键不在语法，而在预算调度时间轴。
- 没有稳定 baseline 时，先别急着上 AdaLoRA。

---

## 15. 下一步建议

如果你准备继续深入，建议按这个顺序：

1. 先把普通 LoRA 和 AdaLoRA 在同一数据集上做一次对照实验。
2. 记录不同 `init_r / target_r / tinit / tfinal` 的效果差异。
3. 再决定是否要和 QLoRA、FSDP、DeepSpeed、TRL 等训练栈结合。

如果你愿意，我下一步可以继续帮你补一份：

- `AdaLoRA + PEFT` 的完整训练脚本
- `AdaLoRA 和 LoRA/QLoRA 的对比表`
- `适配 Qwen / Llama / Mistral 的 target_modules 速查表`
