# 第 09 课：Token、Tokenizer、Embedding

> 本课解释文本如何进入语言模型：Tokenizer 将文本切分为 Token 并映射为 Token ID，Embedding 再将离散 ID 转换为 Transformer 可以处理的连续向量。
>
> **内容来源说明**：项目现有资料检索结果仅提供本课标题和课程大纲；本笔记的具体知识、示例与代码整理自本次会话中的课程讲解，并结合通用大语言模型知识补全，未引用项目中的其他外部资料。
>
> **相关课程**：[[08-Transformer和Self-Attention]]

## 1. 学习目标

完成本课后，应能够：

1. 解释 Token 与字符、单词、子词之间的区别；
2. 说明 Tokenizer、Token ID 和 Embedding 各自的职责；
3. 理解子词 Tokenization 和 BPE 的基本思想；
4. 解释特殊 Token、Padding Mask 与 Causal Mask 的作用；
5. 说明 Token Embedding、位置表示和上下文 Embedding 的区别；
6. 使用 Python 查看文本的 Token、Token ID 和 Attention Mask；
7. 理解 Token 数量对上下文长度、成本和推理速度的影响。

## 2. 从文本到 Transformer 的完整流程

语言模型不能直接对原始字符串进行矩阵计算，通常需要经过以下步骤：

```text
原始文本
  ↓
Tokenizer 分词
  ↓
Token
  ↓
Token ID
  ↓
Token Embedding + 位置表示
  ↓
向量序列
  ↓
Transformer / Self-Attention
```

生成模型还会把模型预测出的 Token ID 解码回文本：

```text
Transformer 输出 logits
  ↓
选择下一个 Token ID
  ↓
Tokenizer Decode
  ↓
生成文本
```

## 3. 什么是 Token

Token 是模型处理文本时使用的基本单位，但它不一定等于一个汉字、一个英文单词或一个完整句子。它可能是：

- 一个字符；
- 一个完整单词；
- 单词的一部分或子词；
- 标点符号；
- 空格或其他特殊符号。

例如，`I love AI` 可能被切分为：

```text
["I", " love", " AI"]
```

也可能被切分为：

```text
["I", " ", "love", " ", "AI"]
```

中文也不一定严格按照“一字一个 Token”切分。例如 `人工智能很有趣` 可能被切分为：

```text
["人工", "智能", "很", "有趣"]
```

也可能被切分为：

```text
["人", "工", "智", "能", "很", "有", "趣"]
```

具体结果由模型使用的词表和 Tokenizer 决定。因此，Token 是一种**模型专用的文本切分单位**，不能简单等同于“单词”。

## 4. 为什么现代模型常用子词切分

### 4.1 直接使用完整单词的问题

如果每个完整单词都单独进入词表，会遇到两个主要问题：

1. **词表规模过大**：词形变化会产生大量不同形式，例如 `play`、`plays`、`played`、`playing`；
2. **未知词问题**：生僻词、拼写错误和新词可能不在词表中，只能被替换为未知标记，如 `[UNK]`，造成信息损失。

### 4.2 子词 Tokenization

子词切分把词拆成常见的词根、词缀或片段。例如：

```text
unhappiness
```

可能被切分为：

```text
["un", "happiness"]
```

或：

```text
["un", "happy", "ness"]
```

这样，即使模型没有见过完整的 `unhappiness`，也可以利用已知子词组合出部分结构信息。现代语言模型常见的子词方法包括：

- BPE（Byte Pair Encoding）；
- WordPiece；
- Unigram；
- SentencePiece 相关方案。

## 5. Tokenizer 的职责

Tokenizer 负责把文本转换成模型可处理的离散表示，常见步骤包括：

1. 文本规范化；
2. 按模型词表切分文本；
3. 处理空格、标点和特殊字符；
4. 添加必要的特殊 Token；
5. 将 Token 映射成 Token ID；
6. 生成 `attention_mask` 等辅助信息；
7. 在生成阶段把 Token 或 Token ID 解码回字符串。

例如，示意过程如下：

```text
文本：我喜欢 AI
Tokens：["我", "喜欢", " AI"]
Token IDs：[103, 2456, 7821]
```

其中数字仅用于说明，不代表任何特定模型的真实词表。

### 5.1 Token ID 只是索引

Token ID 是 Token 在词表中的整数编号。假设词表如下：

| Token | ID |
|---|---:|
| `[PAD]` | 0 |
| `[UNK]` | 1 |
| `我` | 103 |
| `喜欢` | 2456 |
| `AI` | 7821 |

则文本可能被表示为：

```text
[103, 2456, 7821]
```

Token ID 只是查表索引：

- ID 较大不代表语义更重要；
- ID 之间的数值差距不代表语义距离；
- 不同模型的词表和编号可能完全不同。

因此，不能把 Token ID 本身直接当作语义向量，也不能随意混用不同模型的 Tokenizer 与 Token ID。

## 6. BPE 的基本直觉

BPE 可以粗略理解为：

> 从较小的片段开始，反复合并语料中频繁出现的相邻片段。

例如，初始字符片段可能是：

```text
l o w
l o w e r
```

如果 `l` 和 `o` 经常相邻，算法可能先合并为：

```text
lo
```

随后继续合并为：

```text
low
```

最终词表可能同时包含：

```text
["l", "o", "lo", "low", "er"]
```

常见词可以使用较完整的 Token，陌生词则可以拆分为多个已经存在的片段，在词表规模与未知词处理能力之间取得平衡。

## 7. 特殊 Token

Tokenizer 可能使用特殊 Token 表示序列结构或特殊状态：

| 特殊 Token | 常见作用 |
|---|---|
| `[PAD]` | 将不同长度的序列填充到相同长度 |
| `[UNK]` | 表示词表无法识别的 Token |
| `[CLS]` | 一些 Encoder 模型的序列起始标记 |
| `[SEP]` | 分隔句子或表示序列边界 |
| `<BOS>` | Beginning of Sequence，序列开始 |
| `<EOS>` | End of Sequence，序列结束 |
| `<MASK>` | 掩码语言模型中的遮盖标记 |

不同模型对特殊 Token 的名称、是否使用以及具体语义可能不同。例如，BERT 常见：

```text
[CLS] 我喜欢 AI [SEP]
```

GPT 类模型则可能使用另一套开始、结束或填充 Token。使用模型时，应始终使用与模型匹配的 Tokenizer。

## 8. 什么是 Embedding

Tokenizer 输出的 Token ID 是离散整数，例如：

```text
[103, 2456, 7821]
```

神经网络需要连续向量作为输入，因此 Embedding 的作用是：

> 将离散的 Token ID 映射为连续向量。

假设：

- 词表大小为 $V$；
- Embedding 维度为 $d$。

Embedding 矩阵为：

$$
E\in\mathbb{R}^{V\times d}
$$

其中每一行对应一个 Token 的向量。对于 Token ID $i$，其向量为：

$$
e_i=E[i]
$$

这本质上是对 Embedding 矩阵进行查表，而不是把整数机械地复制或缩放。向量中的数值由模型训练学习得到。

### 8.1 PyTorch Embedding 示例

```python
import torch
import torch.nn as nn

vocab_size = 10_000
d_model = 768

embedding = nn.Embedding(
    num_embeddings=vocab_size,
    embedding_dim=d_model,
)

input_ids = torch.tensor([
    [103, 2456, 7821],
    [103, 891, 4567],
])

vectors = embedding(input_ids)

print(vectors.shape)
```

输出形状：

```text
torch.Size([2, 3, 768])
```

形状含义：

- `2`：批次中有两条文本；
- `3`：每条文本包含三个 Token；
- `768`：每个 Token 被表示为 768 维向量。

## 9. Token Embedding、位置表示与上下文 Embedding

Transformer 需要同时知道 Token 的内容和位置。输入表示通常可以概括为：

$$
H_0=E_{\text{token}}+E_{\text{position}}
$$

其中：

- $E_{\text{token}}$：表示 Token 内容的向量；
- $E_{\text{position}}$：表示 Token 所处位置的向量或其他位置机制。

例如，`我喜欢 AI` 与 `AI喜欢我` 可能包含相同的 Token，但顺序不同。位置机制帮助模型区分 Token 出现的位置。在现代模型中，位置机制还可能采用 RoPE 等方法，不一定是简单的可学习位置 Embedding。

还要区分两种表示：

### 9.1 Token Embedding

这是输入层从 Embedding 矩阵查表得到的基础向量：

$$
X=E[\text{input\_ids}]
$$

同一个 Token 在输入层通常对应同一个基础向量。

### 9.2 Contextual Embedding

经过多层 Transformer、Self-Attention 和 FFN 处理后，Token 的表示会结合当前上下文而变化。例如“苹果”在下列句子中的语境不同：

```text
我喜欢吃苹果。
苹果公司发布了新产品。
```

可以用下面的直觉区分：

```text
Token Embedding：这个 Token 通常是什么
Contextual Embedding：这个 Token 在当前句子中是什么意思
```

## 10. Attention Mask 与 Padding

为了将不同长度的文本组成一个批次，通常需要对较短序列补齐 `[PAD]`：

```text
[我, 喜欢, AI, [PAD], [PAD]]
[今, 天, 天, 气, 很, 好]
```

对应的 `attention_mask` 可以是：

```text
[1, 1, 1, 0, 0]
[1, 1, 1, 1, 1, 1]
```

通常：

- `1` 表示真实 Token；
- `0` 表示 Padding，不应参与有效注意力计算。

Padding Mask 与 Causal Mask 的目的不同：

| Mask | 解决的问题 |
|---|---|
| Padding Mask | 忽略为了对齐长度而添加的 `[PAD]` |
| Causal Mask | 阻止当前位置读取未来 Token |

## 11. 使用 Hugging Face 查看 Token

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")

text = "我喜欢人工智能。"

encoded = tokenizer(
    text,
    return_tensors="pt",
)

print("Token IDs：")
print(encoded["input_ids"])

print("Attention Mask：")
print(encoded["attention_mask"])

tokens = tokenizer.convert_ids_to_tokens(
    encoded["input_ids"][0]
)

print("Tokens：")
print(tokens)
```

可能得到类似结果：

```text
['[CLS]', '我', '喜', '欢', '人', '工', '智', '能', '。', '[SEP]']
```

具体切分结果取决于实际使用的模型与词表，不应把示例输出当成所有模型的固定行为。

可以用以下方式查看 Token 数量：

```python
token_count = len(encoded["input_ids"][0])
print("Token 数量：", token_count)
```

## 12. Token 数量为什么重要

### 12.1 上下文长度

模型通常有最大上下文长度限制。如果输入超过限制，可能被截断，或者需要分段处理。

### 12.2 成本

许多模型 API 会根据输入和输出 Token 数量计费。Token 数量越多，费用通常越高。

### 12.3 推理速度与显存

标准 Self-Attention 会产生长度为 $n$ 的 $n\times n$ 注意力矩阵，因此序列长度增加会带来显著的计算和显存压力：

$$
O(n^2)
$$

这与第 08 课中的标准注意力复杂度结论相连接。

### 12.4 编码效率

相同字符长度的内容不一定产生相同数量的 Token。代码、URL、表格、特殊符号以及不同语言的文本，Token 数量可能差异很大。

## 13. GPT 类模型中的 Token 生成流程

GPT 类模型通常以自回归方式逐步预测下一个 Token：

```text
用户输入文本
  ↓
Tokenizer
  ↓
input_ids
  ↓
Token Embedding + 位置表示
  ↓
Transformer
  ↓
输出 logits
  ↓
选择下一个 Token ID
  ↓
重复生成
  ↓
Tokenizer Decode
  ↓
文本
```

模型建模的目标可以表示为：

$$
P(x_t\mid x_1,x_2,\ldots,x_{t-1})
$$

例如：

```text
输入：今天天气
预测：很
再预测：好
再预测：。
```

模型实际逐步处理的是 Token 序列，而不是一次性直接输出完整句子。

## 14. 常见误区

### 误区一：Token 就是单词

不一定。Token 可能是字符、子词、标点、空格或特殊符号。

### 误区二：Token ID 越大越重要

错误。Token ID 只是词表索引，不表示重要性或语义距离。

### 误区三：Embedding 就是 Tokenizer

不是：

- Tokenizer：文本 $ightarrow$ Token / Token ID；
- Embedding：Token ID $ightarrow$ 连续向量。

### 误区四：同一个 Token 在任何句子中意义完全一样

Token Embedding 可以相同，但经过 Transformer 后的上下文表示会受到周围 Token 影响。

### 误区五：不同模型可以共用同一个 Token ID

通常不可以。不同模型的词表、特殊 Token 和编号规则可能不同。

### 误区六：Token 越少，模型一定越聪明

不一定。Token 数量主要反映编码效率，还需要结合模型结构、训练数据、上下文和任务能力判断模型效果。

### 误区七：Padding Mask 和 Causal Mask 是同一种 Mask

错误。前者屏蔽补齐位置，后者屏蔽未来位置，服务于不同场景。

## 15. 核心知识链

```text
原始文本
  ↓
Tokenizer 按模型词表切分
  ↓
Token
  ↓
Token ID（词表索引）
  ↓
Embedding 查表
  ↓
Token Embedding
  ↓
加入位置表示
  ↓
Transformer / Self-Attention
  ↓
Contextual Embedding 或下一个 Token 的概率
  ↓
生成时逐 Token 解码为文本
```

必须掌握的两个表达式是：

$$
X=E[\text{input\_ids}]
$$

以及 Transformer 输入的概念表示：

$$
H_0=E_{\text{token}}+E_{\text{position}}
$$

## 16. 自测题

### 1. Token 和单词有什么区别？

<details>
<summary>参考答案</summary>

Token 是模型专用的文本切分单位，可能是字符、完整单词、子词、标点或特殊符号，不一定对应一个自然语言单词。

</details>

### 2. 为什么 Token ID 不能直接作为语义向量？

<details>
<summary>参考答案</summary>

Token ID 只是词表中的离散索引，数字大小和差值没有语义含义。模型需要通过 Embedding 将它查表转换为连续向量。

</details>

### 3. Tokenizer 和 Embedding 的职责分别是什么？

<details>
<summary>参考答案</summary>

Tokenizer 将文本切分并映射为 Token ID；Embedding 将 Token ID 映射为神经网络可以处理的连续向量。

</details>

### 4. 为什么同一个“苹果”在不同句子中的最终表示可能不同？

<details>
<summary>参考答案</summary>

输入层的 Token Embedding 可以相同，但经过 Self-Attention、FFN 和多层 Transformer 后，表示会融合不同上下文，因此形成不同的上下文相关表示。

</details>

### 5. Padding Mask 和 Causal Mask 有什么区别？

<details>
<summary>参考答案</summary>

Padding Mask 用于忽略批处理对齐时添加的 Padding Token；Causal Mask 用于阻止自回归模型读取当前位置之后的未来 Token。

</details>

### 6. 为什么 Token 数量会影响上下文长度、成本和速度？

<details>
<summary>参考答案</summary>

Token 数量决定输入占用的上下文空间，也常影响 API 计费；标准 Self-Attention 会生成 $n\times n$ 的关系矩阵，因此序列变长会增加计算和显存开销。

</details>

## 17. 课后练习

1. 使用一个实际模型的 Tokenizer，比较中文、英文、代码和 URL 的 Token 数量；
2. 打印一段文本的 Tokens、Token IDs 和 `attention_mask`，观察特殊 Token 是否被自动添加；
3. 修改 PyTorch Embedding 示例中的 `input_ids`，确认输出形状只由批次大小、序列长度和 Embedding 维度决定；
4. 对比同一个 Token 在不同句子中的输入层向量与 Transformer 输出，理解基础 Embedding 和上下文表示的区别；
5. 将本课流程与第 08 课的 Self-Attention 公式连接起来，说明 Token ID 为什么必须先转换为向量。

## 18. 本课小结

Token 是模型处理文本的基本单位，但不一定等于字或词。Tokenizer 负责将文本切分为 Token 并转换成 Token ID；Token ID 只是词表索引，不能直接代表语义。Embedding 通过可训练矩阵查表，将离散 ID 转换为连续向量；再结合位置表示后，向量序列才能进入 Transformer。经过 Self-Attention 和多层 Transformer 加工，同一个 Token 会形成依赖上下文的表示。生成模型则在此基础上逐 Token 预测并解码为文本。

一句话概括：

> Tokenizer 把文本变成模型词表中的编号，Embedding 把编号变成向量，Transformer 再利用上下文加工这些向量。
