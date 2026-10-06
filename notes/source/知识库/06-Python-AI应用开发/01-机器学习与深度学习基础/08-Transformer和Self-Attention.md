# 第 08 课：Transformer 和 Self-Attention

> 本课建立 Transformer 的整体结构与 Self-Attention 的计算直觉，重点理解 $Q$、$K$、$V$、缩放点积注意力、多头注意力、因果掩码和 Transformer Block。
>
> **内容来源说明**：项目现有资料仅提供了本课标题；以下知识整理自本次会话中的课程讲解，并基于通用 Transformer 知识补全，未引用项目中的外部资料。

## 1. 学习目标

完成本课后，应能够：

1. 解释 Transformer 相比 RNN 更容易并行训练的原因；
2. 说明 Self-Attention 如何让一个 Token 汇总其他 Token 的信息；
3. 解释 Query、Key、Value 的职责；
4. 写出并拆解缩放点积注意力公式；
5. 说明为什么要使用 Multi-Head Attention；
6. 区分 Self-Attention、Cross-Attention 和 Causal Self-Attention；
7. 描述 Transformer Block 的主要组成部分；
8. 解释标准 Self-Attention 处理长序列时的主要成本。

---

## 2. Transformer 要解决什么问题

在自然语言中，一个词的含义经常取决于上下文。例如：

> 小明把书放在桌子上，因为它很重。

模型处理“它”时，需要结合其他词的信息判断其所指对象。注意力机制的核心思想是：

> 处理一个 Token 时，计算它与其他 Token 的相关程度，再按相关程度汇总上下文信息。

传统 RNN 按顺序处理序列：

$$
x_1 \rightarrow x_2 \rightarrow x_3 \rightarrow \cdots \rightarrow x_n
$$

这种结构有两个典型限制：

1. **序列内并行困难**：后一个时间步依赖前一个时间步的结果；
2. **长距离信息传递路径较长**：相距很远的两个位置需要经过多个中间状态。

Self-Attention 则允许任意两个位置在同一层中直接建立联系：

$$
x_i \leftrightarrow x_j
$$

这使 Transformer 在训练阶段可以并行处理序列中的多个位置，也更容易建模长距离依赖。

> 注意：大语言模型训练时可以并行处理一个已知序列中的多个位置，但自回归生成时仍通常需要逐 Token 生成。

---

## 3. 输入表示

假设输入序列包含 $n$ 个 Token，每个 Token 的表示维度为 $d_{\text{model}}$，则输入矩阵可写为：

$$
X\in\mathbb{R}^{n\times d_{\text{model}}}
$$

其中每一行对应一个 Token 的向量表示。

Transformer 还必须获得位置信息，因为仅靠 Self-Attention 不能充分区分 Token 的先后顺序。输入通常可以概括为：

$$
H_0=E_{\text{token}}+E_{\text{position}}
$$

其中：

- $E_{\text{token}}$：Token Embedding；
- $E_{\text{position}}$：位置表示。

位置编码的具体实现将在后续课程中展开。本课只需记住：

- Self-Attention 负责建立 Token 之间的联系；
- 位置机制负责向模型提供顺序和距离信息。

---

## 4. Self-Attention 的核心：Q、K、V

模型对输入 $X$ 进行三组不同的线性变换：

$$
Q=XW_Q
$$

$$
K=XW_K
$$

$$
V=XW_V
$$

其中：

- $Q$：Query，查询；
- $K$：Key，键；
- $V$：Value，值；
- $W_Q$、$W_K$、$W_V$：通过训练学习的参数矩阵。

### 4.1 搜索系统类比

可以把注意力过程类比为一次搜索：

- **Query**：当前 Token 想寻找什么信息；
- **Key**：每个 Token 用什么特征参与匹配；
- **Value**：匹配成功后实际提供什么信息。

对某个 Token 来说，计算过程是：

1. 用它的 Query 与所有 Token 的 Key 进行匹配；
2. 将匹配分数转换为注意力权重；
3. 使用权重对所有 Value 进行加权求和。

Q、K、V 并不是人工指定的语义标签，而是模型在训练过程中学出的不同表示。

---

## 5. Scaled Dot-Product Attention

缩放点积注意力的完整公式为：

$$
\operatorname{Attention}(Q,K,V)
=
\operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

其中 $d_k$ 是 Key 和 Query 的维度。

### 5.1 第一步：计算匹配分数

$$
S=QK^T
$$

若：

$$
Q\in\mathbb{R}^{n\times d_k},\qquad
K^T\in\mathbb{R}^{d_k\times n}
$$

则：

$$
S\in\mathbb{R}^{n\times n}
$$

矩阵元素 $S_{ij}$ 表示第 $i$ 个 Token 的 Query 与第 $j$ 个 Token 的 Key 的匹配分数。

注意力矩阵的每一行因此表示：

> 一个 Token 对序列中所有 Token 的关注分数。

### 5.2 第二步：缩放分数

$$
\tilde{S}=\frac{QK^T}{\sqrt{d_k}}
$$

当 $d_k$ 较大时，点积的数值幅度也可能变大。若直接送入 Softmax，输出可能过度接近 0 或 1，使梯度变小并影响训练稳定性。

除以 $\sqrt{d_k}$ 可以将分数控制在更合适的尺度，这也是“Scaled Dot-Product Attention”名称中“Scaled”的来源。

### 5.3 第三步：得到注意力权重

$$
A=\operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)
$$

Softmax 通常沿矩阵的最后一个维度逐行计算，因此：

$$
\sum_j A_{ij}=1
$$

例如，一个 Token 对三个位置的注意力权重可能是：

$$
[0.1,\ 0.7,\ 0.2]
$$

这表示第二个位置对当前 Token 的信息汇总贡献最大。

### 5.4 第四步：汇总 Value

$$
O=AV
$$

对第 $i$ 个 Token 而言：

$$
o_i=\sum_j A_{ij}v_j
$$

因此，输出 $o_i$ 不再只包含第 $i$ 个 Token 自身的信息，而是融合了上下文中其他 Token 的信息。

### 5.5 简化示例

假设输入为：

> 我 爱 AI

模型为“爱”得到的注意力权重为：

| Query：爱 | 我 | 爱 | AI |
|---|---:|---:|---:|
| 注意力权重 | 0.1 | 0.2 | 0.7 |

则“爱”的新表示可以近似写成：

$$
o_{\text{爱}}
=0.1v_{\text{我}}+0.2v_{\text{爱}}+0.7v_{\text{AI}}
$$

这些权重由模型根据输入动态计算，而不是由人工预先设置。

---

## 6. 为什么叫 Self-Attention

在 Self-Attention 中，Q、K、V 都来自同一个输入序列：

$$
Q=XW_Q,\qquad K=XW_K,\qquad V=XW_V
$$

也就是说，序列中的 Token 在序列内部相互关注，因此称为 **Self-Attention**。

如果 Query 来自一个序列，而 Key 和 Value 来自另一个序列，则称为 **Cross-Attention**。例如在经典的 Encoder-Decoder 翻译模型中：

- Decoder 当前状态提供 Query；
- Encoder 的输出提供 Key 和 Value；
- Decoder 借此读取源语言序列的信息。

---

## 7. Multi-Head Attention

单次注意力只能在一组投影空间中计算关系。Multi-Head Attention 使用多组独立投影并行计算：

$$
\operatorname{head}_i
=
\operatorname{Attention}(Q_i,K_i,V_i)
$$

然后拼接各个头的输出并再次进行线性变换：

$$
\operatorname{MultiHead}(Q,K,V)
=
\operatorname{Concat}(\operatorname{head}_1,\ldots,\operatorname{head}_h)W_O
$$

不同注意力头可以学习不同类型的关系，例如：

- 相邻位置关系；
- 长距离依赖；
- 指代关系；
- 句法或语义关系。

这些分工只是可能出现的学习结果，并非人为固定，也不能保证每个头都有容易解释的单一职责。

### 7.1 维度示例

假设：

$$
d_{\text{model}}=512,\qquad h=8
$$

常见配置是每个头的维度为：

$$
d_k=d_v=\frac{512}{8}=64
$$

8 个头分别输出 64 维表示，拼接后恢复为 512 维，再经过输出投影 $W_O$。

---

## 8. Causal Self-Attention 与 Mask

自回归语言模型预测当前位置时不能看到未来 Token，否则训练时会发生答案泄漏。因此 Decoder-only 模型通常使用 **Causal Mask**。

长度为 4 的序列，其可见关系可以表示为：

```text
Token 1：✓ × × ×
Token 2：✓ ✓ × ×
Token 3：✓ ✓ ✓ ×
Token 4：✓ ✓ ✓ ✓
```

在 Softmax 之前，把未来位置的分数设置为负无穷：

$$
S_{ij}=-\infty,\qquad j>i
$$

经过 Softmax 后，这些位置的权重变成 0：

$$
\operatorname{softmax}(-\infty)=0
$$

因此，预测第 $t$ 个 Token 时，模型只能使用此前的 Token：

$$
P(x_t\mid x_1,x_2,\ldots,x_{t-1})
$$

GPT 类模型的核心可以概括为：

> 堆叠多层使用 Causal Self-Attention 的 Transformer Block，并以自回归方式预测下一个 Token。

---

## 9. Transformer Block

一个典型的 Transformer Block 主要包含：

1. Multi-Head Self-Attention；
2. 残差连接；
3. Layer Normalization；
4. Feed-Forward Network；
5. 第二组残差连接和归一化。

简化结构如下：

```text
输入
  │
  ├── Multi-Head Self-Attention
  │
  ├── Residual + LayerNorm
  │
  ├── Feed-Forward Network
  │
  └── Residual + LayerNorm
  │
输出
```

原始 Transformer 常用 Post-Norm，而很多现代模型使用 Pre-Norm。Pre-Norm 的简化流程为：

```text
输入
  │
LayerNorm
  │
Attention
  │
残差相加
  │
LayerNorm
  │
Feed-Forward
  │
残差相加
```

### 9.1 残差连接

残差连接的形式为：

$$
Y=X+F(X)
$$

它有助于：

- 保留原始信息；
- 改善梯度传播；
- 训练更深的网络。

### 9.2 Layer Normalization

LayerNorm 对单个样本中每个 Token 的特征维度进行归一化，帮助稳定训练。

与 BatchNorm 相比：

- BatchNorm 通常依赖批次统计量；
- LayerNorm 不依赖其他样本的批次统计量；
- Transformer 通常使用 LayerNorm 或其变体。

### 9.3 Feed-Forward Network

注意力模块之后，每个 Token 的表示还会独立通过同一组前馈网络：

$$
\operatorname{FFN}(x)=\sigma(xW_1+b_1)W_2+b_2
$$

常见结构是先升维再降维：

$$
d_{\text{model}}\rightarrow d_{\text{ff}}\rightarrow d_{\text{model}}
$$

例如：

$$
768\rightarrow3072\rightarrow768
$$

可以用下面的方式理解二者分工：

- **Attention**：在不同 Token 之间交换和汇总信息；
- **FFN**：对每个 Token 已汇总的表示进一步进行非线性加工。

---

## 10. Encoder、Decoder 与常见模型

### 10.1 Encoder

Encoder 通常使用非因果的双向 Self-Attention，每个 Token 可以关注其前后位置。

常见用途包括：

- 文本理解；
- 文本分类；
- Token 分类；
- 生成语义向量。

BERT 是典型的 Encoder-only 模型。

### 10.2 Decoder

Decoder 在自回归生成时使用 Causal Self-Attention，每个位置只能读取自己及之前的位置。

GPT 类模型是典型的 Decoder-only 模型。

### 10.3 Encoder-Decoder

经典 Transformer 同时包含 Encoder 和 Decoder：

- Encoder 读取并编码输入序列；
- Decoder 使用因果自注意力读取已生成内容；
- Decoder 再通过 Cross-Attention 读取 Encoder 输出。

这类结构适合翻译、摘要等输入到输出的序列转换任务。T5 是常见的 Encoder-Decoder 模型。

---

## 11. PyTorch 手动实现单头 Self-Attention

下面的代码展示 Self-Attention 的核心计算步骤：

```python
import math

import torch
import torch.nn as nn


class SelfAttention(nn.Module):
    def __init__(self, d_model: int, d_k: int):
        super().__init__()

        self.d_k = d_k
        self.w_q = nn.Linear(d_model, d_k)
        self.w_k = nn.Linear(d_model, d_k)
        self.w_v = nn.Linear(d_model, d_k)

    def forward(self, x, mask=None):
        # x: [batch_size, seq_len, d_model]
        q = self.w_q(x)
        k = self.w_k(x)
        v = self.w_v(x)

        # [batch_size, seq_len, seq_len]
        scores = torch.matmul(q, k.transpose(-2, -1))
        scores = scores / math.sqrt(self.d_k)

        # mask 中 True 表示可见，False 表示屏蔽
        if mask is not None:
            scores = scores.masked_fill(~mask, float("-inf"))

        # 对 Key 所在的最后一个维度进行 Softmax
        attention_weights = torch.softmax(scores, dim=-1)

        # [batch_size, seq_len, d_k]
        output = torch.matmul(attention_weights, v)

        return output, attention_weights


batch_size = 2
seq_len = 4
d_model = 8
d_k = 8

x = torch.randn(batch_size, seq_len, d_model)
attention = SelfAttention(d_model, d_k)

output, weights = attention(x)

print("输入形状：", x.shape)
print("输出形状：", output.shape)
print("注意力权重形状：", weights.shape)
```

预期形状为：

```text
输入形状：       [2, 4, 8]
输出形状：       [2, 4, 8]
注意力权重形状： [2, 4, 4]
```

注意力权重最后两个维度都是 `seq_len`，分别表示 Query 位置和 Key 位置。

### 11.1 加入因果 Mask

```python
causal_mask = torch.tril(
    torch.ones(seq_len, seq_len, dtype=torch.bool)
)

# 扩展为 [1, seq_len, seq_len]，可在 batch 维广播
causal_mask = causal_mask.unsqueeze(0)

output, weights = attention(x, mask=causal_mask)
print(weights[0])
```

`torch.tril` 生成下三角矩阵：

```text
1 0 0 0
1 1 0 0
1 1 1 0
1 1 1 1
```

因此每个位置只能关注自己和之前的位置。

> 实际工程中还可能同时使用 Padding Mask，以屏蔽补齐序列长度所产生的 Padding Token。因果 Mask 与 Padding Mask 解决的是不同问题。

---

## 12. Transformer 的优势

### 12.1 训练并行度高

在已知完整训练序列时，多个 Token 的表示可以同时计算，不必像 RNN 那样严格逐时间步执行。

### 12.2 长距离位置可直接交互

任意两个 Token 可以在一层注意力中直接建立联系，信息传递路径较短。

### 12.3 扩展能力强

Transformer 可以通过增加数据、参数、层数、隐藏维度和计算量扩展模型能力。

### 12.4 适用范围广

Transformer 不只用于文本，还可用于：

- 图像；
- 语音；
- 视频；
- 多模态任务；
- 时间序列。

---

## 13. Transformer 的局限

### 13.1 标准注意力的长序列成本较高

长度为 $n$ 的序列会产生一个 $n\times n$ 的注意力分数矩阵，因此注意力矩阵的时间和显存开销通常包含近似二次项：

$$
O(n^2)
$$

更完整地看，注意力计算还与特征维度有关，但序列长度带来的核心问题是 $n^2$ 项。若序列长度从 1,000 增加到 2,000，注意力矩阵的元素数量约变为原来的 4 倍。

### 13.2 必须显式提供位置信息

Self-Attention 本身不具备足够的顺序感知能力，需要位置编码、位置 Embedding 或旋转位置编码等机制。

### 13.3 注意力权重不等于完整解释

注意力权重可以帮助观察某一层、某个头关注了哪些位置，但不能直接当作模型决策的完整因果解释。最终输出还受到以下因素影响：

- 多个注意力头；
- 多层 Transformer Block；
- 残差连接；
- FFN；
- 输出层及其他模块。

---

## 14. 常见误区

### 误区一：注意力权重由人工设置

错误。权重由输入对应的 Q、K 动态计算，而生成 Q、K、V 的投影矩阵通过训练学习。

### 误区二：Self-Attention 只关注距离较近的词

错误。标准 Self-Attention 可以直接比较序列中的任意两个位置；是否重点关注近邻由训练结果和输入共同决定。

### 误区三：Transformer 在任何阶段都完全并行

错误。训练阶段可以并行处理已知序列中的多个位置，但自回归生成通常仍按 Token 逐步进行。

### 误区四：每个注意力头都有固定、明确的人类语义

不一定。不同头可能学习不同模式，但这些模式不由人工固定，也不保证都能用单一语义解释。

### 误区五：注意力权重就是模型决策原因

不准确。它只反映特定层和特定头中的信息混合权重，不是模型全部计算过程的完整解释。

### 误区六：Mask 只有一种

错误。常见 Mask 至少包括：

- Causal Mask：防止当前位置看到未来 Token；
- Padding Mask：防止模型关注补齐长度的 Padding Token。

---

## 15. 核心知识链

```text
Token
  ↓
Token Embedding + Position
  ↓
线性投影得到 Q、K、V
  ↓
Q 与 K 计算匹配分数
  ↓
除以 √d_k 进行缩放
  ↓
必要时应用 Mask
  ↓
Softmax 得到注意力权重
  ↓
使用权重汇总 V
  ↓
多个注意力头拼接并投影
  ↓
残差连接、LayerNorm、FFN
  ↓
重复堆叠多个 Transformer Block
```

必须掌握的两个公式是：

$$
Q=XW_Q,\qquad K=XW_K,\qquad V=XW_V
$$

$$
\operatorname{Attention}(Q,K,V)
=
\operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

---

## 16. 自测题

### 1. 为什么要将 $QK^T$ 除以 $\sqrt{d_k}$？

<details>
<summary>参考答案</summary>

当维度较大时，点积结果的幅度可能变大，使 Softmax 输出过度饱和并影响梯度。缩放可以改善数值范围和训练稳定性。

</details>

### 2. Q、K、V 分别承担什么职责？

<details>
<summary>参考答案</summary>

- Query 表示当前 Token 想匹配什么信息；
- Key 表示每个 Token 用什么特征参与匹配；
- Value 表示匹配后实际参与加权汇总的信息。

</details>

### 3. 为什么需要 Multi-Head Attention？

<details>
<summary>参考答案</summary>

它让模型在多个投影子空间中并行学习不同类型的 Token 关系，再将多个头的信息进行整合。

</details>

### 4. Self-Attention 与 Cross-Attention 的区别是什么？

<details>
<summary>参考答案</summary>

Self-Attention 的 Q、K、V 来自同一个序列；Cross-Attention 的 Query 与 Key、Value 来自不同序列或不同模块。

</details>

### 5. Causal Mask 有什么作用？

<details>
<summary>参考答案</summary>

它屏蔽未来位置，保证自回归模型预测当前位置时只能使用当前及此前的信息，避免看到未来答案。

</details>

### 6. Attention 与 FFN 的主要分工是什么？

<details>
<summary>参考答案</summary>

Attention 在不同 Token 之间交换和汇总信息；FFN 对每个 Token 已汇总的表示独立进行非线性加工。

</details>

### 7. 标准 Self-Attention 的主要长序列问题是什么？

<details>
<summary>参考答案</summary>

长度为 $n$ 的序列会产生 $n\times n$ 的注意力矩阵，时间和显存开销中包含近似 $O(n^2)$ 的序列长度项。

</details>

### 8. GPT 为什么属于 Decoder-only 模型？

<details>
<summary>参考答案</summary>

GPT 堆叠带有 Causal Self-Attention 的 Transformer Block，根据已有 Token 自回归地预测下一个 Token，不使用单独的双向 Encoder。

</details>

---

## 17. 课后练习

1. 运行单头 Self-Attention 代码，检查注意力矩阵每一行的和是否接近 1；
2. 分别在有、无 Causal Mask 时打印注意力权重，观察未来位置是否变为 0；
3. 将 `seq_len` 从 4 增加到 8，观察注意力矩阵形状如何变化；
4. 尝试将 `d_model` 与 `d_k` 设为不同值，确认输入、Q/K/V 和输出的形状；
5. 用自己的语言解释为什么“训练可并行”不等于“自回归生成也可完全并行”。

---

## 18. 本课小结

Transformer 使用 Self-Attention 计算 Token 之间的相关性，并按注意力权重汇总 Value，从而为每个 Token 构造包含上下文的信息表示。Multi-Head Attention 使模型能在多个表示子空间中学习关系；位置机制补充顺序信息；Causal Mask 防止自回归模型读取未来 Token；残差连接、LayerNorm 和 FFN 则共同组成可深度堆叠的 Transformer Block。

一句话概括：

> Transformer 的核心是让每个 Token 动态选择并汇总上下文信息，再通过多头机制和多层 Block 逐步加工这些表示。
