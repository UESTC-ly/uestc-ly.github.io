# Prompt Tuning / Prefix Tuning / P-Tuning v2 横向对比笔记

## 1. 这篇笔记要解决什么问题

在参数高效微调（PEFT）里，最容易混淆的一组方法就是：

- `Prompt Tuning`
- `Prefix Tuning`
- `P-Tuning v2`

它们看起来都像“学一段 prompt”，所以很多人会产生几个误解：

- 这三个其实差不多，只是名字不同
- 它们都是在输入前面拼几个向量
- Prefix Tuning 就是 Prompt Tuning 的另一个名字
- P-Tuning v2 只是 Prompt Tuning 的升级版，没有本质差异

这些理解都不准确。

这篇笔记的目标是把三者放到同一张地图里，帮你回答：

- 它们的共同点到底是什么
- 它们真正的区别在哪里
- 控制信号分别进入模型的哪个位置
- 参数量、训练稳定性、表达能力、适用任务有什么差异
- 工程上什么时候优先选哪一种

如果只先记一句话，可以先记这个版本：

> Prompt Tuning、Prefix Tuning、P-Tuning v2 都属于“软提示”类 PEFT，但它们把可训练提示注入模型的层级不同：Prompt Tuning 最浅，Prefix Tuning 更深入注意力内部，P-Tuning v2 则进一步走向深层、多层注入。

## 2. 三者的共同点是什么

先讲共同点，再讲差异，不然很容易把它们看成完全无关的方法。

这三种方法都属于 PEFT 家族中的“软提示”路线，核心共同点是：

- 冻结大模型主体参数
- 不直接更新全部权重
- 学习一小组可训练的连续向量
- 利用这些向量去引导模型适配任务

这里的关键是“连续向量”，不是自然语言文本。

也就是说，这三种方法学到的都不是：

- `"你现在是一个客服助手"`
- `"请输出 JSON"`

这种人类可读 prompt。

它们学到的是：

- 模型内部可以直接消费的向量表示
- 常被叫作 virtual tokens、soft prompts、continuous prompts

所以从大类上说，三者确实是亲戚。  
但它们最大的差异是：

> 这段可训练提示，究竟被放在模型的哪一层、以什么形式参与计算。

## 3. 为什么“注入位置”这么重要

理解这三个方法，最关键不是记名字，而是记住一句话：

> 提示进入模型越浅，方法越轻；进入模型越深，控制力通常越强，但结构也更复杂。

这是因为 Transformer 是分层结构：

- 输入层
- 多层注意力和 MLP
- 输出层

如果你的可训练提示只在输入层起作用，它对后续深层表征的控制就更弱。  
如果你的提示能作用到每一层，甚至直接进入注意力内部，它对模型行为的影响通常会更强。

所以三者的差异，本质上就是“提示进入模型深度”的差异。

## 4. 一张先导图：三者最核心的区别

先看最短版对比表。

| 方法 | 可训练提示放在哪里 | 作用深度 | 参数量 | 常见特点 |
|---|---|---|---:|---|
| Prompt Tuning | 输入 embedding 前面 | 浅 | 最少 | 最轻量，但控制力偏弱 |
| Prefix Tuning | 每层注意力的 K/V 前缀 | 中 | 低 | 比 Prompt Tuning 更强 |
| P-Tuning v2 | 深层多层 prompt / deep prompt | 深 | 低到中 | 更通用，更接近深层适配 |

这张表可以先背下来，后面再展开每一项。

## 5. Prompt Tuning：最浅层的软提示

### 5.1 它的核心思想

Prompt Tuning 的思路是：

- 学习一小组虚拟 token embedding
- 把它们接到输入序列前面
- 和真实输入一起送进模型

如果用符号写，可以理解成原始输入：

```text
[x1, x2, x3, ...]
```

变成：

```text
[p1, p2, p3, ..., x1, x2, x3, ...]
```

其中：

- `x` 是真实 token
- `p` 是可训练的 soft prompt

### 5.2 它的特点

它最大的特点是简单。

你可以把 Prompt Tuning 理解成：

- 不改模型内部结构
- 只在输入端加几个可训练 embedding

所以它：

- 参数量极少
- 实现最轻
- 训练成本很低

但代价是：

- 控制信号只在输入层出现
- 后续深层是否能持续保留这种影响，要看模型自己传播

### 5.3 它的优势

- 最轻量
- 最容易理解
- 最接近“把 prompt 从文本换成可训练向量”

### 5.4 它的局限

- 对复杂任务的表达能力有限
- 训练效果对模型规模和任务类型更敏感
- 对一些任务来说，效果可能不如更深层的提示方法稳定

## 6. Prefix Tuning：把提示送进注意力内部

### 6.1 它的核心思想

Prefix Tuning 比 Prompt Tuning 更进一步。

它不是只在输入 embedding 前面加提示，而是让提示进入每层注意力的 `K/V` 路径。

也就是说，它学习的是一组“前缀表示”，这些前缀会作为注意力里的额外 `Key/Value` 参与计算。

### 6.2 为什么它更强

因为模型在做注意力时，不只看真实输入的 `K/V`，还会看这些可训练前缀的 `K/V`。

这意味着：

- 这组前缀不是只在最开始提醒一下模型
- 而是被放进了每层注意力的检索空间里

从控制力角度看，这显然比 Prompt Tuning 更深。

### 6.3 直觉类比

如果 Prompt Tuning 是：

- 在试卷前加一张提示卡

那 Prefix Tuning 更像是：

- 在每一轮思考时，都给模型塞一组隐藏参考条目

### 6.4 它的特点

- 参数量仍然很低
- 控制力通常强于 Prompt Tuning
- 更偏“生成控制”和深一点的任务适配

### 6.5 它的代价

- 结构上比 Prompt Tuning 更复杂
- 工程生态没有 LoRA 那么主流
- 不同任务上的收益差异可能更明显

## 7. P-Tuning v2：深层 Prompt 的路线

### 7.1 名字最容易让人误解

`P-Tuning v2` 最容易让人误以为只是“Prompt Tuning 第二版”，但它的关键变化不是版本号，而是：

> 它把 prompt 从输入层推进到了深层、多层。

也就是说，它不满足于“只在开头给一段软提示”，而是让深层网络中也有可训练提示参与。

### 7.2 核心思想

P-Tuning v2 通常可以理解为：

- deep prompt tuning
- multi-layer prompt injection

它的重点是：

- 提示不只存在于输入层
- 而是在多个 Transformer 层都发挥作用

这让它比原始 Prompt Tuning 更有表达能力，也更接近一种真正的深层参数高效适配。

### 7.3 为什么会出现它

原始 Prompt Tuning 很轻，但一个典型问题是：

- 提示太浅
- 难以稳定影响深层表示

于是 P-Tuning v2 的思路就是：

- 如果浅层 prompt 不够，那就把 prompt 往深层推进

因此它在理念上更接近：

- 保留“软提示”的轻量思路
- 但提升提示的作用深度

### 7.4 它和 Prefix Tuning 的关系

它们不是同一个方法，但都属于“把控制信号送进更深层”的路线。

可以粗略理解为：

- Prompt Tuning：输入层软提示
- Prefix Tuning：注意力 K/V 前缀
- P-Tuning v2：深层多层 prompt

所以 P-Tuning v2 和 Prefix Tuning 会显得比 Prompt Tuning 更像“进化方向”。

## 8. 用“进入模型的深度”来重新理解三者

如果你想真正不混淆这三者，建议用下面这条连续光谱来记。

```text
Prompt Tuning  ->  Prefix Tuning  ->  P-Tuning v2
   最浅               更深               最深
```

更准确地说：

- Prompt Tuning：主要作用在输入端
- Prefix Tuning：作用到每层注意力的 K/V
- P-Tuning v2：作用到多层深层表示

这是整篇最重要的记忆主轴。

## 9. 三者的参数量对比

一般来说，这三种方法的参数量都远小于 LoRA 和 full fine-tuning，但内部仍有差异。

### 9.1 Prompt Tuning

参数通常最少，因为它只训练：

- 一小组虚拟 token embedding

因此它常常是这三者里最轻的。

### 9.2 Prefix Tuning

参数通常比 Prompt Tuning 多一点，因为：

- 它要为注意力结构提供 prefix 表示
- 有时还会加 projection MLP

### 9.3 P-Tuning v2

参数通常比 Prompt Tuning 更高，有时也可能接近或超过 Prefix Tuning，原因是：

- 它走的是多层深提示路线
- 深层注入意味着更多可训练提示参数

所以从“纯轻量”角度看，顺序通常是：

```text
Prompt Tuning < Prefix Tuning ≈ P-Tuning v2
```

但具体值会依赖：

- prompt 长度
- 层数
- hidden size
- 是否有 projection/encoder

## 10. 三者的表达能力对比

如果只看表达能力和任务适配能力，通常可以粗略认为：

```text
Prompt Tuning < Prefix Tuning < P-Tuning v2
```

为什么？

- Prompt Tuning 只在输入层插入提示
- Prefix Tuning 进入了注意力内部
- P-Tuning v2 进一步把提示做深做多层

但这里要加一个重要限定：

> 这不是绝对性能排行榜，而是“控制信号介入深度”的一般趋势。

实际效果还会受到：

- 基座模型规模
- 数据量
- 任务类型
- 优化设置

的强烈影响。

## 11. 训练稳定性和优化难度

这是很多教程不会强调，但工程上很关键的一点。

### 11.1 Prompt Tuning

因为太轻，所以它有一个典型特征：

- 参数少得惊人
- 但也可能意味着优化空间受限

你会感觉：

- 好处是省
- 坏处是有时不太“顶得住”复杂任务

### 11.2 Prefix Tuning

它比 Prompt Tuning 更有控制力，因此在某些任务上会更稳定一些。  
但它也更复杂，调试成本略高。

### 11.3 P-Tuning v2

它是“让软提示真正深入网络”的路线，因此往往在表达能力上更强。  
但相应地：

- 结构更复杂
- 理解门槛更高
- 工程实现也没有 LoRA 那么普及

所以如果你问“哪一个最简单”，答案是 Prompt Tuning；  
如果你问“哪一个通常最有潜力”，很多时候答案会更偏向 P-Tuning v2 或 Prefix Tuning。

## 12. 三者分别更适合什么任务

### 12.1 Prompt Tuning 更适合

- 你想做极轻量实验
- 任务本身不复杂
- 你更关心成本而不是极致表现
- 你想快速验证软提示路线是否可行

### 12.2 Prefix Tuning 更适合

- 生成控制任务
- 需要比 Prompt Tuning 更强的行为引导
- 你希望提示直接影响注意力检索过程

### 12.3 P-Tuning v2 更适合

- 你想做更通用的深层软提示适配
- 任务不只是表层风格控制
- 你希望在不走 LoRA 的情况下，提高软提示方法的表达能力

## 13. 如果放到 PEFT 家族里，它们处于什么位置

把它们放回 PEFT 地图，会更清楚。

PEFT 大体可以分成两条思路：

### 路线 A：改“提示”

代表：

- Prompt Tuning
- Prefix Tuning
- P-Tuning v2

这条路线的核心是：

- 不去直接改主干权重
- 而是学习如何“喂模型一个更好的内部提示”

### 路线 B：改“层映射”

代表：

- LoRA
- AdaLoRA
- IA3

这条路线的核心是：

- 不只改输入提示
- 而是直接给网络层加可学习适配器

所以如果从哲学上说：

- Prompt / Prefix / P-Tuning v2 是“提示派”
- LoRA / IA3 是“层适配派”

## 14. 为什么现在工程里更常听到 LoRA，而不是这三者

这是一个现实问题。

因为在今天的工程实践中，LoRA 往往更容易成为默认首选，原因包括：

- 效果通常稳定
- 生态成熟
- 文档多
- 框架支持完善
- 对很多任务泛用性强

相比之下，Prompt Tuning / Prefix Tuning / P-Tuning v2：

- 更适合理解 PEFT 的不同思路
- 也适合某些特定研究和任务
- 但在“默认工业路线”里的优先级通常没 LoRA 高

这不代表它们不重要。恰恰相反：

> 它们是理解软提示类 PEFT 的关键台阶。

## 15. 一个统一的直觉类比

这三种方法可以用同一个类比来理解。

假设模型是一个专家团队。

### Prompt Tuning

像是在会议开始前，给团队一页短 briefing。

团队看过这页 brief 后开始工作，但之后是否持续受影响，要靠自己记住。

### Prefix Tuning

像是在每轮讨论中，都往桌上放几张固定参考卡片，让大家每次注意力检索时都能看到。

### P-Tuning v2

像是不只在会议开头给 briefing，也不只是放桌面卡片，而是把提示嵌进多个工作流程节点里，让团队在不同环节都被持续引导。

这个类比不严格，但很适合记忆。

## 16. 三者的最关键差异总结表

下面这张表是全文最值得反复看的部分。

| 维度 | Prompt Tuning | Prefix Tuning | P-Tuning v2 |
|---|---|---|---|
| 核心思想 | 学输入层软提示 | 学注意力前缀 | 学深层多层 prompt |
| 提示注入位置 | 输入 embedding 前 | 每层 attention 的 K/V | 多层 Transformer 表示 |
| 作用深度 | 浅 | 中 | 深 |
| 参数量 | 最低 | 低 | 低到中 |
| 表达能力 | 偏弱 | 较强 | 更强 |
| 工程复杂度 | 最低 | 中 | 较高 |
| 适合场景 | 轻量实验、简单适配 | 生成控制、增强引导 | 更通用、更深层任务适配 |
| 常见短板 | 太浅，控制力有限 | 结构更复杂 | 理解和实现门槛更高 |

## 17. 怎么选：给一个实用决策树

### 问题 1：你是不是只是想做最轻量的软提示实验？

如果是：

- 先 `Prompt Tuning`

### 问题 2：你觉得只在输入层加提示不够，需要更强控制力？

如果是：

- 看 `Prefix Tuning`

### 问题 3：你希望保持“软提示路线”，但想让提示深入多层网络？

如果是：

- 看 `P-Tuning v2`

### 问题 4：你不是执着于“提示路线”，你只是想要一个稳妥工程方案？

那大多数情况下：

- 直接优先 `LoRA`

这就是一个非常现实的选择逻辑。

## 18. 术语上的一个重要提醒

这部分一定要说清楚，因为很多资料会把名字用乱。

### 18.1 Prompt Tuning

一般是指：

- 输入层 soft prompt

### 18.2 Prefix Tuning

一般是指：

- attention prefix
- 往每层注意力里加可训练前缀

### 18.3 P-Tuning v2

一般强调：

- deep prompt tuning
- multi-layer prompt

### 18.4 现实中的混用问题

很多库或文章会把这些概念写得不完全统一。  
尤其在某些实现里：

- “prompt encoder”
- “deep prompt”
- “p-tuning”

可能会有术语重叠。

所以你在看框架文档时，最可靠的判断方法不是只看名字，而是看：

> 它的可训练提示到底被注入到了哪里。

这条判断标准永远更靠谱。

## 19. 在 Hugging Face PEFT 里怎么对应理解

在 `peft` 生态里，你通常会看到：

- `PromptTuningConfig`
- `PrefixTuningConfig`
- `PromptEncoderConfig`

一个很实用的理解方式是：

- `PromptTuningConfig` 对应最直接的 Prompt Tuning
- `PrefixTuningConfig` 对应 Prefix Tuning
- `PromptEncoderConfig` 常用于 P-Tuning 类路线

但这里要加一个谨慎说明：

> 工程库中的实现接口，不一定和原始论文版本逐字逐句完全等价。

所以写代码时要以具体实现为准，做概念理解时要抓住“注入层级”这个核心。

## 20. 一个极简代码对照

下面不是为了让你马上训练，而是为了让你直观看到：同样是 PEFT，它们的配置入口怎么不同。

### 20.1 Prompt Tuning

```python
from peft import PromptTuningConfig, get_peft_model, TaskType

config = PromptTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=20,
)

model = get_peft_model(model, config)
```

### 20.2 Prefix Tuning

```python
from peft import PrefixTuningConfig, get_peft_model, TaskType

config = PrefixTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=20,
    prefix_projection=True,
)

model = get_peft_model(model, config)
```

### 20.3 P-Tuning 类配置

```python
from peft import PromptEncoderConfig, get_peft_model, TaskType

config = PromptEncoderConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=20,
    encoder_hidden_size=128,
)

model = get_peft_model(model, config)
```

你可以看到：

- 三者都属于“给模型挂一段可训练提示”
- 但配置类不同
- 背后的提示生成方式和介入深度也不同

## 21. 常见误区

### 21.1 “三者只是不同名字，本质一样”

不对。  
它们的共同点是“软提示”，但区别在于提示注入的层级和形式。

### 21.2 “Prompt Tuning 就够了，深层方法没必要”

不一定。  
如果任务更复杂、需要更强控制力，浅层 prompt 可能不够。

### 21.3 “Prefix Tuning 和 P-Tuning v2 完全一样”

不对。  
两者都比 Prompt Tuning 更深，但它们的设计路径并不相同。

### 21.4 “P-Tuning v2 一定碾压前两者”

也不对。  
它通常更强，但实际结果仍然依赖：

- 模型规模
- 数据质量
- 任务类型
- 超参数

### 21.5 “只要是软提示，就一定比 LoRA 差”

这也太粗暴了。  
LoRA 的确更主流，但软提示路线在某些研究和任务上依然很有价值。

## 22. 一条建议的学习顺序

如果你想把这三者真正学明白，建议顺序是：

1. 先学 `Prompt Tuning`  
   因为它最简单，最容易建立“soft prompt”直觉。

2. 再学 `Prefix Tuning`  
   因为它能帮你理解“提示如何进入注意力内部”。

3. 最后学 `P-Tuning v2`  
   因为这时你已经能理解“深层 prompt”为什么会出现。

这条顺序非常自然：

```text
输入层 -> 注意力层 -> 深层多层
```

## 23. 最后的结论

这三种方法最值得记住的，不是名字，而是下面这条主线：

- `Prompt Tuning`：在输入层学软提示
- `Prefix Tuning`：在注意力层学前缀
- `P-Tuning v2`：在深层多层学提示

如果只保留一句话，就保留这句：

> 它们都属于软提示 PEFT，但本质差异在于“提示进入模型的深度”：Prompt Tuning 最浅，Prefix Tuning 更深，P-Tuning v2 最强调深层注入。

如果按工程决策压缩成一句话，则是：

- 想做最轻量实验：`Prompt Tuning`
- 想要更强控制力：`Prefix Tuning`
- 想走深层软提示路线：`P-Tuning v2`
- 只是想先拿稳妥方案：通常还是先 `LoRA`

如果你愿意，我下一步可以继续接着写：

1. `LoRA vs Prefix Tuning` 专题对比  
2. `Prompt Tuning / Prefix Tuning / LoRA / IA3` 四方法总表  
3. 一篇“软提示路线 vs LoRA 路线”的决策笔记
