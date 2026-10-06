# LoRA（Low-Rank Adaptation）系统性教程

> 目标：把 LoRA 从“知道是什么”讲到“真正理解为什么这样设计、在 Transformer 里怎么工作、工程上怎么落地、训练时怎么调、有哪些变种与边界”。
>
> 适合对象：
> - 想系统理解参数高效微调（PEFT）的人
> - 想做 LLM 微调实践的人
> - 想把 LoRA 讲清楚、写清楚、用于面试或教学的人

---

# 目录

1. 为什么需要 LoRA
2. LoRA 想解决什么问题
3. 从全量微调到低秩更新
4. 什么是“低秩”
5. LoRA 的核心公式
6. 为什么拆成两个小矩阵可以降低开销
7. LoRA 在 Transformer 里的具体注入方式
8. 为什么 LoRA 通常加在 Q / V，而不是优先加 K
9. LoRA 的前向、反向与参数更新机制
10. 训练时到底省了什么
11. 推理时怎么办：动态加载 vs merge
12. LoRA 的超参数详解
13. 实战：使用 Hugging Face PEFT 训练 LoRA
14. 实战：从零实现一个最小 LoRA Linear
15. 数据、训练策略与调参经验
16. LoRA 的优势、局限与适用边界
17. LoRA 与 Full Fine-tune / Adapter / Prompt Tuning 对比
18. QLoRA：为什么 4bit 量化下仍能训练
19. 常见变种：AdaLoRA、DoRA、LoRA+ 等
20. 常见坑与排查清单
21. 一套完整的 LoRA 学习路径
22. 总结

---

# 1. 为什么需要 LoRA

大模型微调的第一现实问题不是“会不会调”，而是“调不调得起”。

对于一个典型的大语言模型（LLM），参数量可能是：

- 7B
- 13B
- 34B
- 70B
- 更大

如果对整个模型做 full fine-tuning（全量微调），你会遇到几个直接问题：

## 1.1 参数量太大

全量微调意味着：

- 所有参数都要参与训练
- 所有参数都要保存梯度
- optimizer（如 Adam）还要为每个参数维护额外状态

这会直接推高显存和训练成本。

## 1.2 显存开销巨大

训练时显存不仅存模型权重，还要存：

- forward 中间激活
- 梯度
- optimizer state（Adam 通常有一阶矩、二阶矩）
- 有时还会有 master weights

因此，同样一个模型：

- 推理能跑
- 不代表能全量训练

## 1.3 每个任务都复制一份模型，不经济

如果你对多个任务分别全量微调，那么通常会得到多份完整模型：

- 法律问答模型
- 医疗问答模型
- 客服模型
- 代码模型

这会带来：

- 存储成本高
- 版本管理复杂
- 部署麻烦

## 1.4 工业场景需要更灵活的任务适配方式

企业往往希望：

- 基座模型统一
- 不同任务只加载不同小模块
- 训练便宜
- 推理切换快速

LoRA 正是在这个背景下变得流行。

---

# 2. LoRA 想解决什么问题

LoRA 想回答的不是“如何重新训练一个模型”，而是：

> **当一个大模型已经学会大量通用知识后，如何以极低成本把它适配到一个具体任务？**

这里有一个关键观察：

> 大模型在适配下游任务时，并不一定需要所有参数都自由更新。

换句话说：

- 模型已经会语言了
- 模型已经有广泛知识了
- 下游任务更多是在“调整行为方式”
- 这个调整可能只发生在一个低维子空间中

于是就有了 LoRA 的核心思想：

> 不直接训练整个大矩阵的更新量 ΔW，而是让更新量只存在于一个低秩空间中。

---

# 3. 从全量微调到低秩更新

先看最普通的线性层。

假设某一层权重是：

W ∈ ℝ^(d×k)

输入是：

x ∈ ℝ^k

输出为：

y = Wx

如果做全量微调，训练后权重变成：

W′ = W + ΔW

其中：

ΔW ∈ ℝ^(d×k)

这表示：

- 你允许整个矩阵的每个元素都自由变化
- 更新空间非常大
- 参数量就是 d × k

LoRA 的想法是：

> 不直接学习完整的 ΔW，而是把它写成两个小矩阵的乘积。

即：

ΔW = BA

注意不同资料里会写成 AB 或 BA，本质一样，只取决于输入输出维度怎么定义。为了和工程实现对齐，我们这里统一写成：

- A ∈ ℝ^(r×k)
- B ∈ ℝ^(d×r)

于是：

ΔW = BA，且 BA ∈ ℝ^(d×k)

新的输出变成：

y = Wx + BAx

或者写成：

y = (W + BA)x

这里的关键约束是：

r ≪ min(d, k)

其中 r 称为 rank，也叫 LoRA rank。

---

# 4. 什么是“低秩”

很多人第一次看 LoRA，会对“低秩”这个词感觉抽象。这里给你一个尽量直观的解释。

## 4.1 矩阵秩的直观理解

矩阵的秩（rank）可以粗略理解为：

> 这个矩阵能够表达多少个彼此独立的变化方向。

如果一个矩阵秩很高，说明它能表达复杂而丰富的变化。

如果一个矩阵秩很低，说明它虽然仍然能表达变化，但这些变化被限制在较少的独立方向中。

## 4.2 LoRA 的隐含假设

LoRA 的核心假设是：

> 对于一个已经预训练好的大模型，下游任务所需要的参数更新，并不需要充满整个高维空间，而是集中在少数几个主要方向上。

这句话非常重要。

它意味着：

- 任务适配不是从零学语言
- 不是让模型重建全部知识
- 而是在已有能力上做定向偏移

所以，LoRA 相当于说：

> “我只允许模型沿着少数几个方向去改变行为。”

这就是“低秩更新”的本质。

## 4.3 类比理解

想象你有一个非常复杂的控制台，上面有 10000 个旋钮。

全量微调：
- 你允许这 10000 个旋钮全都独立调整

LoRA：
- 你说，其实真正有用的控制自由度可能只要 8 个、16 个、32 个
- 于是只提供少量“高级控制杆”
- 这些控制杆通过映射影响全部旋钮

这就相当于：

- 表达能力仍然存在
- 但优化空间被强约束
- 成本大幅下降

---

# 5. LoRA 的核心公式

现在更正式地写一下。

设原始线性层为：

y = Wx

LoRA 注入后，变为：

y = Wx + (α/r)BAx

其中：

- W：原始预训练权重，冻结不训练
- A ∈ ℝ^(r×k)
- B ∈ ℝ^(d×r)
- r：低秩维度
- α：缩放系数（lora_alpha）

有时也写作：

y = Wx + s·BAx，其中 s = α/r

## 5.1 为什么需要缩放系数

因为不同 rank 下，BA 的量级会变。

为了让：

- rank 变大或变小时
- LoRA 分支的输出尺度相对稳定

通常会引入：

α/r

这让 rank 和更新强度之间更容易调节。

## 5.2 初始化方式

LoRA 通常会这样初始化：

- A：随机初始化
- B：初始化为 0

这样做的好处是：

训练刚开始时：

BA ≈ 0

因此：

y ≈ Wx

也就是：

- 刚注入 LoRA 时，不会立刻破坏原模型行为
- 模型从预训练状态平滑开始适配

这是一个非常实用的工程细节。

---

# 6. 为什么拆成两个小矩阵可以降低开销

这是理解 LoRA 的第一核心问题。

## 6.1 参数量减少

原始更新矩阵：

ΔW ∈ ℝ^(d×k)

参数量为：

d × k

LoRA 用两个矩阵：

- A ∈ ℝ^(r×k)
- B ∈ ℝ^(d×r)

参数量变为：

r × k + d × r = r(d + k)

如果 r ≪ d, k，那么：

r(d + k) ≪ d × k

### 例子

如果：

- d = 4096
- k = 4096
- r = 8

那么：

原始：

4096 × 4096 = 16,777,216

LoRA：

8 × (4096 + 4096) = 65,536

二者相比，LoRA 只需要原来的极小一部分参数。

## 6.2 不只是参数少，训练状态也少

训练时不仅有参数本身，还有：

- 梯度
- Adam 的一阶矩
- Adam 的二阶矩

所以参数减少，会同时带来：

- 梯度存储下降
- optimizer state 下降
- 通信成本下降（分布式训练中特别明显）

## 6.3 计算上为什么也更便宜

你可能会想：

BAx

不还是要做矩阵乘法吗？

对，但关键在于顺序。

LoRA 并不会真的先算大矩阵 BA，再乘 x。

而是按结合律写成：

B(Ax)

也就是：

1. 先把 x 从 k 维投影到 r 维
2. 再从 r 维映射到 d 维

因为 r 很小，所以计算更便宜。

### 复杂度对比

原始一个完整更新分支如果直接用 ΔWx：

- 复杂度约为 O(dk)

LoRA 用：

- Ax：O(rk)
- B(Ax)：O(dr)

总复杂度：

O(rk + dr) = O(r(d + k))

只要 r 小，就比 O(dk) 小得多。

## 6.4 更深一层：LoRA 不是“压缩矩阵”，而是在“限制优化空间”

这是非常重要的一句。

很多人以为 LoRA 的本质是：

> “把大矩阵分解成小矩阵，减少参数。”

这句话不完整。

更本质的说法是：

> **LoRA 通过低秩约束，把参数更新限制在一个低维子空间中。**

也就是说，它不是单纯为了省存储，而是从优化角度假设：

- 下游任务需要的更新，不需要整个高维自由度
- 少数方向足够表达任务偏移

---

# 7. LoRA 在 Transformer 里的具体注入方式

LoRA 不是对整个 Transformer 统一加一个模块，而是通常插入到 Transformer 内部的某些线性层中。

先回顾 Transformer 里最关键的几个线性映射。

## 7.1 Self-Attention 中的四个核心投影

对于输入隐状态 x，Attention 通常会计算：

Q = W<sub>q</sub>x
K = W<sub>k</sub>x
V = W<sub>v</sub>x
O = W<sub>o</sub>h

其中：

- W<sub>q</sub>：query 投影
- W<sub>k</sub>：key 投影
- W<sub>v</sub>：value 投影
- W<sub>o</sub>：attention 输出投影

## 7.2 在某个投影上加 LoRA

例如只给 W<sub>q</sub> 加 LoRA：

Q = W<sub>q</sub>x + (α/r)B<sub>q</sub>A<sub>q</sub>x

给 W<sub>v</sub> 加 LoRA：

V = W<sub>v</sub>x + (α/r)B<sub>v</sub>A<sub>v</sub>x

如果同时加在多个矩阵上，那么每个矩阵各自有一组独立的 LoRA 参数。

## 7.3 工程上通常怎么写

一个原始 linear 层：

y = Wx

变成：

y = Wx + s·B(Ax)

这里：

- 主分支：原始线性层
- 辅分支：LoRA 分支
- 最后两者相加

你可以把 LoRA 理解为：

> 在原始 linear 上外挂一个低秩残差分支。

## 7.4 只训练 LoRA 分支

关键点在于：

- 原始线性层的 W 冻结
- 只有 LoRA 的 A、B 可训练

因此 LoRA 不会破坏基座模型的主干参数结构。

## 7.5 除了 Attention，还可以加在哪些层

除了 q、k、v、o 投影外，Transformer 里还有 FFN（前馈网络）部分，例如：

- up_proj
- gate_proj
- down_proj

这些本质上也是线性层，所以理论上都可以加 LoRA。

实践中常见配置有：

- 只加 q_proj, v_proj
- 加 q_proj, k_proj, v_proj, o_proj
- 再额外加 FFN 的若干投影

不同任务和模型会有不同选择。

---

# 8. 为什么 LoRA 通常加在 Q / V，而不是优先加 K

这是理解 LoRA 与 Attention 关系的第二核心问题。

我们先看 Attention 公式：

Attention(Q, K, V) = softmax(QKᵀ / √d)V

这个式子可以分成两步理解：

## 8.1 第一步：Q 和 K 决定“看哪里”

softmax(QKᵀ / √d)

这部分决定注意力权重，也就是：

- 当前 token 关注哪些 token
- 关注强度如何分配

## 8.2 第二步：V 决定“拿什么内容”

αV

其中 α 是注意力权重。

这部分决定最终传出的语义内容。

## 8.3 Q、K、V 的角色分工

可以用“搜索系统”类比：

- Q：搜索词（我想找什么）
- K：索引（数据库如何组织）
- V：文档内容（最终返回什么）

这时你会发现：

### Q 更像主动控制端

Q 表示：

> 当前 token 想要什么信息

它决定查询方向，直接影响注意力模式。

### V 决定内容输出

即使注意力权重固定，只要 V 变了，最终输出也会明显变化。

### K 更像被动匹配端

K 当然也重要，但它更像是：

> “我是什么类型的信息，供别人来匹配”

相比之下，Q 和 V 往往更直接控制模型行为。

## 8.4 为什么优先改 Q

改 Q 等于改“查询方式”。

这会直接影响：

- 模型关注什么上下文
- 如何路由信息
- 哪些模式被激活

因此 Q 是非常强的“控制点”。

## 8.5 为什么优先改 V

改 V 等于改“输出内容表示”。

这会直接影响：

- attention 聚合后输出的语义方向
- 当前层传给后续层的内容特征

所以 V 是非常强的“内容点”。

## 8.6 为什么 K 通常不是第一优先级

不是说 K 不能改，而是说：

- 改 K 的收益常常不如 Q/V 明显
- K 更偏向“被查询的索引空间”
- 改 K 往往更全局、更间接
- 在一些场景中收敛或稳定性未必优于改 Q/V

因此工程上最常见的折中是：

- 先改 q_proj + v_proj
- 如果不够，再考虑加 k_proj / o_proj / FFN

## 8.7 一个更抽象的总结

可以把 Attention 理解成：

- Q：控制信息流向
- V：承载信息内容
- K：定义被检索空间

那么 LoRA 优先放在：

- 控制流（Q）
- 内容流（V）

这就解释了为什么 q_proj / v_proj 是最经典的 LoRA 注入位置。

---

# 9. LoRA 的前向、反向与参数更新机制

这一节回答一个很常见但容易糊涂的问题：

> W 冻结不训练，那梯度是怎么传的？LoRA 分支怎么学到东西？

## 9.1 前向传播

对于一个带 LoRA 的线性层：

y = Wx + s·B(Ax)

其中：

- W 是冻结参数
- A、B 是可训练参数
- s = α/r

前向时：

1. 原始主分支计算 Wx
2. LoRA 分支计算 B(Ax)
3. 二者相加得到输出

## 9.2 反向传播

损失对输出 y 的梯度会继续往回传。

虽然 W 在图里参与了前向计算，但因为它被设置为 `requires_grad=False`，所以：

- 梯度不会用于更新 W
- 但会继续流经 LoRA 分支，更新 A 和 B

因此，LoRA 不是“阻断反向传播”，而是“冻结主干，只让辅助低秩分支吸收任务信号”。

## 9.3 为什么这仍然能学到有效东西

因为 LoRA 分支虽然参数少，但它直接作用于：

- 注意力投影
- FFN 投影
- 层内信息变换

这些位置对模型行为影响很强。

也就是说：

- 你没改整个系统
- 但你改了几个关键控制阀门

这通常就足以完成任务适配。

---

# 10. 训练时到底省了什么

很多人说 LoRA “省显存”，但到底省在哪里？这里拆开说。

## 10.1 省训练参数

显然，LoRA 只训练极少数参数。

## 10.2 省梯度存储

因为只有 A/B 需要梯度。

## 10.3 省 optimizer state

Adam 要为每个可训练参数维护一阶矩和二阶矩。

LoRA 可训练参数少，因此 optimizer state 也少。

## 10.4 省分布式通信开销

多卡训练中，需要同步梯度。

如果训练参数量从上亿缩到几百万甚至更少，那么：

- all-reduce 压力下降
- 通信开销下降

## 10.5 不一定省激活显存

这是一个容易误解的点。

LoRA 主要减少的是：

- 可训练参数相关开销
- optimizer 相关开销

但对 activation memory（激活显存）的帮助不一定像参数显存那样巨大。

因为：

- 你仍然要跑整张网络的 forward
- 中间激活依然存在

所以如果模型太大，LoRA 虽然比全量微调省很多，但仍可能需要：

- gradient checkpointing
- 混合精度
- 分布式并行
- 量化训练（如 QLoRA）

---

# 11. 推理时怎么办：动态加载 vs merge

LoRA 训练好后，推理有两种常见方式。

## 11.1 动态加载

推理时直接保留两条分支：

y = Wx + s·B(Ax)

优点：

- 灵活
- 可以快速切换不同 adapter
- 适合多任务服务

缺点：

- 推理时多一个 LoRA 分支计算
- 框架兼容性要处理好

## 11.2 合并（merge）

把 LoRA 权重直接合到原始权重里：

W′ = W + s·BA

然后推理用：

y = W′x

优点：

- 推理路径和普通模型完全一样
- 不额外增加 LoRA 分支开销

缺点：

- 不如 adapter 热插拔灵活
- 多任务切换不如动态加载方便

## 11.3 工程上怎么选

- 多任务、经常切换 adapter：动态加载更方便
- 固化为一个任务模型上线：merge 更方便

---

# 12. LoRA 的超参数详解

LoRA 虽然轻量，但超参数仍然会显著影响效果。

## 12.1 rank（r）

这是最核心参数。

它控制低秩空间的维度，也就是 LoRA 分支的容量。

### rank 小

优点：
- 参数少
- 显存低
- 训练快

缺点：
- 表达能力可能不足
- 容易欠拟合

### rank 大

优点：
- 表达更强
- 更接近 full fine-tuning 的灵活度

缺点：
- 参数增加
- 显存增加
- 更容易过拟合

### 常见经验值

- 4：非常轻量
- 8：常用入门值
- 16：比较稳妥
- 32 / 64：更复杂任务或更高拟合需求

### 如何理解 rank

可以把它理解为：

> 允许任务更新沿多少个独立方向发生变化。

## 12.2 lora_alpha

通常使用缩放：

s = α/r

因此 alpha 本质上影响 LoRA 分支的输出强度。

经验上常见：

- 16
- 32
- 64

alpha 太小：
- LoRA 分支作用弱

alpha 太大：
- 训练不稳定
- 容易干扰原模型

## 12.3 lora_dropout

这是加在 LoRA 分支上的 dropout。

作用：

- 抑制过拟合
- 增强泛化

常见值：

- 0.0
- 0.05
- 0.1

如果数据量少，适当 dropout 会更稳。

## 12.4 target_modules

决定 LoRA 注入哪些层。

不同模型的命名不同，例如：

- LLaMA / Mistral 常见：`q_proj`, `k_proj`, `v_proj`, `o_proj`
- FFN 里可能有：`up_proj`, `down_proj`, `gate_proj`
- GPT 某些实现里可能是合并投影，例如 `c_attn`

这是实践中最容易踩坑的地方之一：

> 模块名写错，LoRA 可能根本没注入成功。

## 12.5 bias

有些实现允许同时训练 bias：

- `none`
- `all`
- `lora_only`

多数场景下 `none` 是常见选择。

## 12.6 学习率

LoRA 的学习率通常会比 full fine-tuning 更高。

常见范围：

- 1e-4
- 2e-4
- 5e-5（更保守）

为什么能更高？

因为：

- 可训练参数少
- 更新目标更集中
- 主干被冻结，不容易全局漂移

但数据很小或任务很敏感时，也要防止学习率过高导致不稳定。

---

# 13. 实战：使用 Hugging Face PEFT 训练 LoRA

这一节给一个较完整的 LoRA 训练流程框架。

## 13.1 安装依赖

```bash
pip install transformers peft accelerate datasets
```

如果需要量化训练，还常配合：

```bash
pip install bitsandbytes
```

## 13.2 基本代码骨架

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType

model_name = "meta-llama/Llama-2-7b-hf"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
```

`print_trainable_parameters()` 很有用，它能让你确认：

- LoRA 是否真的注入成功
- 当前可训练参数比例是多少

## 13.3 训练前要先确认什么

### 1）tokenizer 配置正确

比如 causal LM 场景中：

- `pad_token` 是否设置
- `eos_token` 是否合理

### 2）target_modules 是否匹配当前模型

例如不同模型类里层名不一样。

### 3）数据格式与任务范式一致

例如：

- 指令微调（instruction tuning）
- 续写（causal LM）
- 分类
- 序列标注

## 13.4 Trainer 示例

```python
from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./lora_out",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    num_train_epochs=3,
    logging_steps=10,
    save_steps=200,
    fp16=True,
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

trainer.train()
```

## 13.5 保存与加载

保存 adapter：

```python
model.save_pretrained("./lora_adapter")
tokenizer.save_pretrained("./lora_adapter")
```

加载时：

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM

base_model = AutoModelForCausalLM.from_pretrained(model_name)
model = PeftModel.from_pretrained(base_model, "./lora_adapter")
```

## 13.6 merge 权重

```python
merged_model = model.merge_and_unload()
```

这会把 LoRA 权重并回主模型中。

---

# 14. 实战：从零实现一个最小 LoRA Linear

要真正理解 LoRA，最好自己实现一次最小版本。

下面给一个简化版 PyTorch 实现。

```python
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

class LoRALinear(nn.Module):
    def __init__(self, in_features, out_features, r=8, alpha=16, dropout=0.0, bias=True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.r = r
        self.alpha = alpha
        self.scaling = alpha / r if r > 0 else 1.0

        # 原始权重
        self.weight = nn.Parameter(torch.empty(out_features, in_features))
        self.bias = nn.Parameter(torch.zeros(out_features)) if bias else None

        # 冻结原始权重
        self.weight.requires_grad = False
        if self.bias is not None:
            self.bias.requires_grad = False

        # LoRA 参数
        if r > 0:
            self.lora_A = nn.Parameter(torch.empty(r, in_features))
            self.lora_B = nn.Parameter(torch.zeros(out_features, r))
            self.lora_dropout = nn.Dropout(dropout)
        else:
            self.lora_A = None
            self.lora_B = None
            self.lora_dropout = nn.Identity()

        self.reset_parameters()

    def reset_parameters(self):
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        if self.bias is not None:
            fan_in, _ = nn.init._calculate_fan_in_and_fan_out(self.weight)
            bound = 1 / math.sqrt(fan_in)
            nn.init.uniform_(self.bias, -bound, bound)

        if self.r > 0:
            nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))
            nn.init.zeros_(self.lora_B)

    def forward(self, x):
        base_out = F.linear(x, self.weight, self.bias)
        if self.r > 0:
            lora_out = F.linear(self.lora_dropout(x), self.lora_A)
            lora_out = F.linear(lora_out, self.lora_B)
            return base_out + self.scaling * lora_out
        return base_out
```

## 14.1 这个实现里最重要的几个点

### 冻结原始权重

```python
self.weight.requires_grad = False
```

### A 随机初始化，B 初始化为 0

```python
nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))
nn.init.zeros_(self.lora_B)
```

### forward 时加低秩残差

```python
base_out + scaling * lora_out
```

## 14.2 为什么实现里是两次 linear

因为：

- 第一次 `F.linear(x, lora_A)` 相当于 `A x`
- 第二次 `F.linear(..., lora_B)` 相当于 `B (A x)`

这对应 LoRA 的先降维、再升维。

---

# 15. 数据、训练策略与调参经验

LoRA 成败很大程度上不只取决于方法本身，还取决于数据与训练策略。

## 15.1 数据质量通常比 rank 更重要

如果数据：

- 指令风格混乱
- 答案不一致
- 噪声大
- 格式不统一

那么你就算把 rank 从 8 调到 64，也未必有效。

对 LoRA 来说，优先级通常是：

1. 数据质量
2. 模板一致性
3. 训练目标是否合理
4. rank / alpha 等超参数

## 15.2 指令微调时要保证格式统一

例如统一采用：

- system
- user
- assistant

或者统一采用某种 prompt template。

因为 LoRA 学到的往往不只是知识，也包括：

- 响应格式
- 语气
- 输出风格
- 推理路径偏好

## 15.3 数据量小时，LoRA 很容易“学风格大于学能力”

这是实践中常见现象。

当数据很少时，LoRA 可能更快学会：

- 固定措辞
- 模板模式
- 特定表达方式

而不一定真正提升任务泛化能力。

所以：

- 少量高质量数据仍然有价值
- 但要通过验证集看是否真提升任务表现

## 15.4 学习率通常别太低

很多初学者把 LoRA 学习率设成和 full FT 一样小，例如 1e-5，结果模型几乎不学。

LoRA 常见学习率更高，例如：

- 1e-4
- 2e-4

因为可训练参数少，需要足够的更新强度。

## 15.5 batch size 与 gradient accumulation

LoRA 虽然节省参数显存，但激活显存仍然存在。

常见策略：

- 减小 per-device batch size
- 增加 gradient_accumulation_steps
- 开启 gradient checkpointing

## 15.6 什么时候该加更多 target modules

如果你发现：

- q_proj + v_proj 效果不足
- 任务较复杂
- 风格迁移之外还需要较强能力改造

可以尝试：

- 加上 o_proj
- 加上 k_proj
- 加 FFN 层

代价是：

- 参数更多
- 训练更重
- 调参更复杂

---

# 16. LoRA 的优势、局限与适用边界

任何方法都有边界，LoRA 也不例外。

## 16.1 LoRA 的优势

### 1）训练成本低

相比 full fine-tune，参数和 optimizer 开销显著下降。

### 2）存储方便

一个 adapter 通常很小，可以为不同任务保存不同 adapter。

### 3）易于多任务切换

同一个 base model 可以挂不同 LoRA adapter。

### 4）工程生态成熟

Hugging Face PEFT、bitsandbytes 等生态已经很完善。

## 16.2 LoRA 的局限

### 1）能力改造有上限

如果任务要求模型发生非常深层的行为重构，仅靠少量低秩更新可能不够。

### 2）不是所有任务都适合超小 rank

一些复杂任务在 rank 太小时会明显欠拟合。

### 3）对数据质量仍然敏感

LoRA 不是“便宜就一定有效”。

### 4）对架构与注入位置有依赖

不同模型命名不同、模块结构不同，实践时要仔细检查。

## 16.3 什么时候 LoRA 特别适合

- 指令微调
- 风格适配
- 领域问答
- 多任务小成本部署
- 算力有限的实验

## 16.4 什么时候可能考虑 full fine-tune

- 任务规模很大
- 需要最大性能
- 资源充足
- 需要深入改变模型内部表征

---

# 17. LoRA 与 Full Fine-tune / Adapter / Prompt Tuning 对比

## 17.1 LoRA vs Full Fine-tune

### Full FT

优点：
- 自由度最大
- 上限最高

缺点：
- 成本最高
- 显存最高
- 每个任务都要存完整模型

### LoRA

优点：
- 便宜
- 快
- 易切换任务

缺点：
- 表达自由度低于 full FT

## 17.2 LoRA vs Adapter

Adapter 通常是在网络中插入新的小模块（如 bottleneck 层）。

LoRA 则是：

- 不额外改变主干层结构太多
- 直接对线性变换加低秩更新

一般来说，LoRA 更轻、更简洁，推理合并也更方便。

## 17.3 LoRA vs Prompt Tuning / Prefix Tuning

Prompt Tuning / Prefix Tuning 更偏向：

- 不改模型内部权重
- 通过额外提示向量引导行为

优点：
- 更轻
- 更少参数

缺点：
- 能力边界可能更窄
- 对复杂适配的效果未必如 LoRA 稳

LoRA 在“轻量”和“有效”之间取得了很强平衡，这也是它流行的重要原因。

---

# 18. QLoRA：为什么 4bit 量化下仍能训练

如果说 LoRA 解决的是“训练参数太多”，那么 QLoRA 解决的是：

> **基座模型本身太大，连加载都很贵。**

QLoRA 的核心思路是：

- 基座模型权重量化到 4bit 存储
- 前向时用量化权重参与计算
- 主模型仍冻结
- 只训练 LoRA adapter

## 18.1 直觉理解

LoRA 已经让“可训练参数”很少了，但你仍然要把整个 base model 放进显存。

如果 base model 还是 FP16 / BF16，那么对于 7B、13B 甚至更大模型，依然很重。

QLoRA 的想法就是：

- 主模型用低比特存储，减少显存占用
- LoRA 负责可训练更新

于是你得到：

- 低内存加载
- 低成本训练
- 还保持不错效果

## 18.2 为什么量化不会阻断训练

因为训练的不是量化权重本身，而是 LoRA 参数。

也就是说：

- 量化主模型提供前向基础能力
- LoRA 分支吸收梯度并更新

主模型虽然被冻结，但仍然是计算图的一部分，LoRA 可以在其上“叠加可学习偏移”。

## 18.3 QLoRA 的工程关键点

常见包括：

- 4-bit NormalFloat（NF4）
- Double Quantization
- Paged Optimizers

这里不展开到论文级细节，但你至少要知道：

> QLoRA = 量化基座模型 + LoRA 微调

它不是普通 LoRA 的替代，而是 LoRA 的“更省显存版本”。

---

# 19. 常见变种：AdaLoRA、DoRA、LoRA+ 等

LoRA 之后出现了很多变种，目的是进一步提升：

- 性能
- 稳定性
- 参数利用效率

## 19.1 AdaLoRA

核心思想：

- 不同层的重要性不同
- rank 不一定应该固定分配

AdaLoRA 会动态分配不同层的 rank 预算。

直觉上：

- 重要层给更多容量
- 不重要层给更少容量

## 19.2 DoRA

DoRA（Weight-Decomposed Low-Rank Adaptation）试图把权重更新进一步拆成更细的结构，例如把方向与幅值分开建模。

它的目标是：

- 提升低秩更新表达力
- 在相似参数预算下取得更好效果

## 19.3 LoRA+

LoRA+ 主要关注训练优化层面，例如让不同 LoRA 参数组使用不同学习率或更合理的更新方式，从而提升训练稳定性和收敛效率。

## 19.4 为什么会不断有新变种

因为标准 LoRA 虽然很成功，但仍有两个天然问题：

1. 固定 rank 不一定最优
2. 低秩结构可能仍有表达瓶颈

这些变种本质上都在回答同一个问题：

> 如何在不显著增加成本的前提下，让参数高效微调更强。

---

# 20. 常见坑与排查清单

这一节非常实用，建议直接收藏。

## 20.1 target_modules 写错

症状：

- 训练正常跑
- 但参数几乎没变
- 效果非常差

排查：

- 打印模型结构
- 确认真实层名
- 使用 `model.print_trainable_parameters()`

## 20.2 LoRA 没真正注入

症状：

- 可训练参数数量异常少或为 0

排查：

- 注入后检查模块类型
- 检查框架版本兼容性

## 20.3 学习率太低

症状：

- loss 几乎不降
- 生成风格变化很小

处理：

- 从 1e-4 或 2e-4 试起

## 20.4 rank 太小

症状：

- 训练集也学不动
- 模型改造能力不足

处理：

- 8 → 16 → 32 逐步增大

## 20.5 数据模板不统一

症状：

- 模型输出格式飘忽
- 任务行为不稳定

处理：

- 统一 prompt 模板
- 清理脏数据

## 20.6 忽略验证集

症状：

- 训练 loss 很好
- 实际推理效果很差

处理：

- 固定验证样本
- 观察泛化，不只看训练 loss

## 20.7 误以为 LoRA 一定优于全量微调

不是。

正确理解是：

- LoRA 是一个高性价比方案
- 不是任何场景下的绝对最优方案

---

# 21. 一套完整的 LoRA 学习路径

如果你想真正把 LoRA 吃透，可以按这个顺序学习：

## 第一步：先彻底理解 Attention

必须真正明白：

- Q、K、V 的作用
- Attention 输出如何形成
- 为什么改 Q/V 会有效

## 第二步：理解线性层与矩阵乘法

至少要熟悉：

- 线性映射
- 维度变化
- 矩阵乘法顺序
- 为什么 `B(Ax)` 比先算 `BA` 更合理

## 第三步：理解低秩分解与 rank

要建立：

- 秩 = 独立变化方向数
- LoRA = 低维子空间更新

## 第四步：理解 PEFT 思想

LoRA 不只是一个技巧，它属于更大的 PEFT（Parameter-Efficient Fine-Tuning）范式。

## 第五步：做一次完整实战

至少亲手做过：

- 加载 base model
- 注入 LoRA
- 训练
- 保存 adapter
- 加载 adapter 推理
- merge 权重

## 第六步：再看 QLoRA 和其他变种

这时你会对：

- 量化训练
- 显存优化
- 不同 LoRA 变体

有更扎实的理解。

---

# 22. 总结

最后用几句话，把 LoRA 的本质重新压缩一下。

## 22.1 一句话定义

> **LoRA 是一种参数高效微调方法：通过把权重更新限制为低秩矩阵乘积，只训练极少量参数，就能让大模型适配下游任务。**

## 22.2 它为什么有效

因为：

- 预训练模型已经拥有大量通用能力
- 下游适配更多是“行为偏移”而不是“重学一切”
- 这种偏移往往可以在低维子空间中表达

## 22.3 它为什么省

因为：

- 不训练完整 `Delta W`
- 只训练 `A, B`
- 减少参数、梯度、optimizer state、通信成本

## 22.4 它在 Transformer 中怎么工作

因为：

- Transformer 的核心操作大量依赖线性层
- LoRA 可以直接加到这些线性层上
- 特别是 Attention 中的 Q / V 投影，对模型行为影响显著

## 22.5 它的工程意义

LoRA 让我们第一次非常实用地做到：

- 用较低成本微调大模型
- 为不同任务维护小型 adapter
- 让多任务适配、实验迭代和部署变得更可行

---

# 附录：一组最容易记住的核心句子

1. **LoRA 不是训练整个更新矩阵，而是训练一个低秩更新。**
2. **LoRA 本质上是在低维子空间中做参数更新。**
3. **它通常加在线性层上，特别是 Attention 的 q_proj / v_proj。**
4. **Q 决定“关注哪里”，V 决定“输出什么”，所以它们是很强的控制点。**
5. **LoRA 省的不只是参数，还有梯度、optimizer state 和通信成本。**
6. **QLoRA = 量化基座模型 + LoRA 微调。**
7. **LoRA 是高性价比方案，不是任何场景下都绝对优于 full fine-tuning。**

---

如果要继续扩展，这份教程下一步最值得补充的方向有：

- LoRA 的数学推导再深入一层（含梯度推导）
- QLoRA 的 NF4 / double quantization 细讲
- 面向工程的完整训练脚本模板
- LoRA 在分类、SFT、RAG 场景中的使用差异
- 面试版高频问答整理
