# KV Cache 详解与实操笔记

## 1. 这份笔记要解决什么问题

很多人第一次接触大模型推理时，都会听到一句话：

> 开启 `KV Cache` 之后，推理会快很多。

这句话没错，但如果只停留在这里，实际做推理优化时还是会糊涂。你很容易继续问：

- 为什么它会变快
- 到底缓存了什么
- 它和训练有什么关系
- 为什么开了缓存以后显存又变大了
- 长上下文为什么会把显存吃光
- `MQA`、`GQA`、`PagedAttention` 和它是什么关系
- 为什么流式生成和多轮对话基本都离不开它

这份笔记的目标就是把这些问题讲透。

如果你只想先记一句话，可以先记这个版本：

> `KV Cache` 是在自回归生成时，把历史 token 的注意力 `Key` 和 `Value` 缓存下来，后续每生成一个新 token 时不再重复计算旧 token 的 `K/V`，从而显著减少重复计算、提升解码速度。

但这只是结论。真正重要的是你要知道它为什么成立，代价是什么，以及在工程里如何正确理解。

## 2. 先给一个最短定义

`KV Cache` 全称通常写作 `Key-Value Cache`，也叫：

- attention cache
- past key values
- past kv

本质上，它是 Transformer 解码阶段的一种缓存机制：

- 对已经处理过的 token
- 把每一层注意力里的 `K` 和 `V` 保存起来
- 后续生成新 token 时直接复用
- 不再重复为历史 token 重新计算这些 `K/V`

它只在 **推理** 中特别重要，尤其是 **自回归生成** 场景。

## 3. 为什么会需要 KV Cache

### 3.1 自回归生成的基本流程

大语言模型生成文本，不是一次性把整段答案全算出来，而是按 token 一个接一个生成：

1. 输入 prompt
2. 预测下一个 token
3. 把这个 token 接到上下文后面
4. 再预测下一个 token
5. 重复直到结束

也就是说，模型在第 `t` 步生成时，看到的是前面全部历史 token。

### 3.2 如果没有 KV Cache，会发生什么

假设当前上下文已经有 1000 个 token，你现在要生成第 1001 个 token。

如果 **没有 KV Cache**，模型在这一轮前向时通常要把这 1000 个 token 全部重新过一遍注意力计算。  
等你再生成第 1002 个 token 时，又要把 1001 个 token 再重新过一遍。

也就是说，历史越长，重复计算越多。

这会导致：

- 解码越来越慢
- 同一段历史被一遍又一遍重新编码
- 算力浪费非常明显

### 3.3 KV Cache 的核心思想

历史 token 已经算过的 `K/V`，没必要再算第二遍。

因为在推理时：

- 历史 token 的表示已经固定
- 这些 token 对应的 `K/V` 也已经固定
- 下一步只需要为“新来的那个 token”计算 `Q/K/V`
- 然后把新 token 的 `Q` 去和“历史缓存中的 K”做注意力

所以，缓存旧 token 的 `K/V` 是完全合理的。

## 4. 回到注意力：到底缓存的是哪一部分

先看标准自注意力：

```text
Q = XW_Q
K = XW_K
V = XW_V

Attention(Q, K, V) = softmax(QK^T / sqrt(d))V
```

这里：

- `X` 是隐藏状态
- `Q` 是 Query
- `K` 是 Key
- `V` 是 Value

在解码时，我们关注的是“新 token 怎么看历史 token”。

当一个新 token 到来时：

- 它自己的 `Q` 需要重新算，因为这是新的位置
- 它自己的 `K/V` 也要算，因为它现在也进入历史了
- 但旧 token 的 `K/V` 不需要重算，可以直接从缓存里拿

所以缓存的重点是：

- 每一层的 `K`
- 每一层的 `V`

通常不缓存 `Q`，因为 `Q` 是当前步特有的查询。

## 5. 没有 KV Cache 和有 KV Cache 的区别

### 5.1 没有 KV Cache

第 1 步：输入长度 1000，算 1000 个 token  
第 2 步：输入长度 1001，再算 1001 个 token  
第 3 步：输入长度 1002，再算 1002 个 token

你会不断重复处理旧 token。

### 5.2 有 KV Cache

先把 prompt 做一次完整前向，拿到所有历史 token 的 `K/V`。  
之后每一步只做：

- 计算新 token 的表示
- 计算新 token 的 `Q/K/V`
- 用新 token 的 `Q` 去和缓存里的历史 `K` 做注意力
- 把新 token 的 `K/V` 追加到缓存

于是每一步不再重复重算整段历史。

### 5.3 一个直觉类比

可以把它理解成会议纪要：

- 没有 KV Cache：每次新成员发言，你都要求大家把前面所有发言完整重说一遍
- 有 KV Cache：前面说过的话已经记录好了，新成员只需要读记录，再补一句自己的内容

前者当然极其低效。

## 6. 在推理流程里，KV Cache 对应哪两个阶段

理解 KV Cache，最好把推理拆成两个阶段：

- `Prefill`
- `Decode`

### 6.1 Prefill 阶段

`Prefill` 就是把用户输入的 prompt 一次性送进模型，让模型先把整段上下文编码出来。

在这个阶段：

- 整个 prompt 都要跑一遍
- 各层的 `K/V` 会被建立起来
- 最终得到首个可用于解码的缓存

特点：

- 计算量大
- 并行性高
- 更像“吞 prompt”

### 6.2 Decode 阶段

`Decode` 是从第一个生成 token 开始，一步一步往后生成。

在这个阶段：

- 每步通常只处理 1 个新 token
- 历史 `K/V` 来自 cache
- 每步把新 token 的 `K/V` 追加进去

特点：

- 单步计算小
- 并行性差
- 对延迟非常敏感

KV Cache 的价值主要就是体现在 `decode` 阶段。

## 7. 为什么 KV Cache 能提速

### 7.1 关键不是“注意力消失了”

要避免一个误区：KV Cache 并不是让注意力计算消失，而是让 **重复构造历史 `K/V` 的成本消失**。

每步生成时，模型仍然要做：

- 当前 token 的前向传播
- 当前 token 对历史上下文的注意力

只是历史部分不再重新编码。

### 7.2 节省的主要是什么

节省的是：

- 历史 token 的线性投影 `W_K / W_V`
- 历史 token 的层间重复传递
- 历史 token 的重复 attention 前处理

换句话说，节省的是“重复前向”的大头。

### 7.3 为什么长上下文下收益更明显

上下文越长，历史 token 越多。

如果没有 cache：

- 每一步都要把越来越长的上下文重算一遍

如果有 cache：

- 历史长度虽然还在增长
- 但历史 `K/V` 已经保存
- 新增成本只和“新 token”有关，以及它与历史做 attention 的代价有关

所以，长上下文场景下 KV Cache 的意义更大。

## 8. 一个半定量的复杂度直觉

这里不做严苛论文推导，只给工程上足够用的直觉。

### 8.1 没有 KV Cache

生成长度为 `T` 时，你每一步都要对已有上下文重新前向。  
总成本会随着历史长度累加，重复计算非常明显。

### 8.2 有 KV Cache

有了 KV Cache 之后：

- 每步只新增 1 个 token 的投影与层计算
- 但新 token 仍需要和历史所有 cached `K` 做注意力

所以它不是把每步计算降到常数，而是把“整段重算”变成了“只算新 token + 看历史缓存”。

实践里，这个差异已经足以带来非常显著的速度提升。

## 9. KV Cache 的代价：显存

天下没有免费的午餐。KV Cache 提速的代价，是要占显存。

### 9.1 为什么会占显存

因为你要把每一层、每个位置的 `K/V` 都存下来。

缓存包含这些维度：

- batch size
- sequence length
- layer 数
- head 数
- head dimension
- 数据类型（fp16 / bf16 / fp8 等）

上下文越长，缓存越大。

### 9.2 一个常见的显存估算思路

粗略地说，KV Cache 大小近似和下面这些量成正比：

```text
2 × batch × seq_len × num_layers × num_kv_heads × head_dim × dtype_size
```

这里前面的 `2` 来自：

- 一份 `K`
- 一份 `V`

注意是 `num_kv_heads`，不是一定等于 `num_attention_heads`。  
如果模型用了 `MQA` 或 `GQA`，KV 头数可能更少，缓存会显著缩小。

### 9.3 为什么长上下文特别贵

因为 cache 是按序列长度线性增长的。

如果你从：

- 4K 上下文
- 扩到 32K 上下文

那 KV Cache 体积也会近似按长度倍数增长。

这就是为什么：

- 长上下文模型推理难
- 高并发更难
- 推理服务经常被 KV Cache 卡住，而不是被参数权重卡住

## 10. 一个具体的显存直觉例子

假设你有一个模型：

- `32` 层
- `32` 个 attention heads
- 每个 head dim 是 `128`
- batch size = `1`
- sequence length = `4096`
- dtype = `fp16`，每个数 `2` 字节

如果是普通多头注意力，并且 `num_kv_heads = 32`，那单层的 KV 大小大概是：

```text
2 × 1 × 4096 × 32 × 128 × 2 bytes
```

算下来约为：

```text
67,108,864 bytes ≈ 64 MB / layer
```

再乘以 `32` 层，大约就是：

```text
2 GB
```

这还只是：

- batch = 1
- seq_len = 4096

如果 batch 上来、上下文继续拉长，显存就会非常快地膨胀。

这也是为什么服务端推理经常要精打细算：

- 最大上下文长度
- 最大并发
- cache 分配策略

## 11. KV Cache 为什么特别适合流式输出

流式输出的特点是：

- 用户想尽快看到第一个 token
- 后续 token 要持续低延迟地产生

这天然就是 decode 场景，而 decode 最依赖 KV Cache。

如果没有 cache：

- 每输出一个 token 都要重新把历史上下文完整过一遍
- 流式体验会很差

有了 cache：

- 后续每个 token 的生成只需要增量计算
- token-by-token 的延迟更可控

所以只要是聊天、代码补全、实时生成，KV Cache 基本都是默认配置。

## 12. KV Cache 和训练的关系

### 12.1 训练时一般不用它来做标准全序列前向

训练和推理不同。

训练中常见的是 teacher forcing：

- 整个序列一次性并行计算
- 所有位置一起算 loss

这时你并不是像推理那样一 token 一 token 地 decode，因此 KV Cache 不是训练主角。

### 12.2 推理时它几乎是核心优化

真正离不开 KV Cache 的，是推理阶段的自回归生成。

所以一个简单判断是：

- 训练：重点看并行前向、反向传播、激活显存
- 推理：重点看 KV Cache、batching、调度、吞吐和延迟

## 13. 为什么说 KV Cache 只缓存 K/V，不缓存整层输出

这是因为注意力的关键复用点就在 `K/V`。

对于一个新 token：

- 它要用自己的 `Q`
- 去查询历史 token 的信息

历史 token 作为被查询对象，最直接需要的就是它们的 `K/V`。

如果你缓存整层所有中间状态，虽然也不是完全没用，但：

- 存储成本更高
- 复用逻辑更复杂
- 对注意力最关键的仍然是 `K/V`

所以工程里通常说 KV Cache，就是非常明确地指 attention 的 `K/V` 缓存。

## 14. 多轮对话里，KV Cache 是怎么工作的

对话场景里，你通常有一整串上下文：

- system prompt
- 历史轮次
- 当前用户输入
- 模型生成结果

当一轮回答生成中：

- 历史上下文的 `K/V` 会被缓存
- 模型边生成边追加自己的新 token 的 `K/V`

但到了下一轮用户再发消息时，是否还能复用之前的 cache，要看你的服务系统怎么组织会话。

很多系统会：

- 保留会话级上下文
- 尽量复用前缀
- 或利用 prefix caching / paged attention 进行更高级的共享

这时 KV Cache 的概念就会延伸到“会话缓存”和“前缀共享”。

## 15. Prefix Cache 和 KV Cache 的关系

这两个词很像，但不完全一样。

### 15.1 KV Cache

指一次生成过程中，历史 token 的 `K/V` 缓存。

### 15.2 Prefix Caching

指如果不同请求共享相同前缀，比如：

- 相同系统提示词
- 相同文档前缀
- 相同模板 prompt

那么这个共享前缀的 KV 也可以复用，而不是每个请求都从头 prefill 一遍。

所以：

- KV Cache 更像“单请求生成过程中的缓存”
- Prefix Cache 更像“跨请求共享的 KV 复用”

它们底层都和 `K/V` 缓存有关，但应用层级不同。

## 16. MHA、MQA、GQA 和 KV Cache 的关系

这一段很重要，因为它直接关系到显存。

### 16.1 MHA：普通多头注意力

在标准多头注意力（MHA）里：

- 每个 attention head 都有自己的 `K/V`

这意味着：

- `num_kv_heads = num_attention_heads`
- KV Cache 比较大

### 16.2 MQA：Multi-Query Attention

在 `MQA` 中：

- 多个 query heads 共享同一组 `K/V`
- 常见形式是所有 query heads 共享一个 KV 头组

效果：

- KV Cache 显著变小
- 推理更友好

### 16.3 GQA：Grouped-Query Attention

`GQA` 是 MHA 和 MQA 之间的折中。

它不是所有 query heads 都共享同一组 `K/V`，而是：

- 把多个 query heads 分成若干组
- 每组共享一套 `K/V`

效果：

- 比 MHA 省显存
- 比 MQA 保留更多表达能力

这也是今天很多大模型喜欢用 GQA 的原因之一：  
它对 KV Cache 更友好。

## 17. PagedAttention 是在解决什么问题

当你理解了 KV Cache 的价值和显存成本，就很容易明白 `PagedAttention` 为什么重要。

`PagedAttention` 的核心不是“发明了 KV Cache”，而是 **更高效地管理 KV Cache**。

### 17.1 传统问题

如果你为每个请求预留一大块连续 KV Cache：

- 会有内存碎片
- 会有浪费
- 请求长度不一致时很难高效利用显存

### 17.2 PagedAttention 的思路

像操作系统分页一样，把 KV Cache 切成块（blocks / pages）来管理。

这样做的好处：

- 分配更灵活
- 碎片更少
- 多请求混合时更容易调度
- 长短请求更容易共存

这就是为什么 vLLM 会强调：

- `PagedAttention`
- continuous batching
- block-based KV cache

它本质上是在把 KV Cache 这件事做得更工程化、更高效。

## 18. 连续批处理和 KV Cache 的关系

在传统 static batching 里，你往往希望同一批请求长度接近。  
但在线服务中，请求到达时间、prompt 长度、生成长度都不一致，这会导致批处理效率很差。

连续批处理（continuous batching）会让系统：

- 在不同时间把请求动态混进同一个执行流
- 已完成的请求退出
- 新请求及时补进来

而这一切成立的前提之一，就是底层要能灵活管理每个请求的 KV Cache。

所以你可以把关系记成：

- KV Cache：让单请求解码高效
- PagedAttention：让 KV Cache 管理高效
- Continuous batching：让多请求调度高效

## 19. 为什么 KV Cache 会成为高并发服务的瓶颈

很多人以为推理服务的瓶颈只在模型参数本身，其实在长上下文和高并发下，KV Cache 经常才是第一瓶颈。

原因很简单：

- 模型权重通常固定
- KV Cache 随请求数和上下文长度动态增长

当你有很多活跃请求时，每个请求都需要：

- 自己那份历史 `K/V`

于是显存压力来自：

- 请求数
- 每个请求的 prompt 长度
- 每个请求当前已经生成了多少 token

这也是推理服务经常要设置：

- max context length
- max batch tokens
- max active sequences

本质都是在控制 KV Cache 的总占用。

## 20. KV Cache 不是万能加速器

这点也很关键。

### 20.1 它主要优化 decode，不是 prefill

如果你的请求特点是：

- prompt 很长
- 生成很短

那主要开销可能在 `prefill`，而不是 `decode`。  
这时 KV Cache 依然有用，但体感提升未必像长生成场景那么夸张。

### 20.2 它不能消除长上下文 attention 本身的代价

虽然历史 `K/V` 不用重算，但新 token 仍然要对整段历史做 attention。

所以：

- 上下文越长
- 新 token 的 attention 范围越大

KV Cache 只是避免重复计算，不是让长上下文注意力变成零成本。

### 20.3 它不直接提升模型质量

KV Cache 是推理优化，不是训练优化，也不是能力增强方法。  
它让模型更快、更省重复算力，但不会让模型更聪明。

## 21. 一个极简 PyTorch 直觉示例

下面不是完整 Transformer 实现，只是帮助你建立“缓存追加”的感觉。

```python
import torch


batch = 1
num_heads = 4
head_dim = 8

# 假设历史已经有 10 个 token 的 K/V
cached_k = torch.randn(batch, num_heads, 10, head_dim)
cached_v = torch.randn(batch, num_heads, 10, head_dim)

# 当前新 token 的 Q/K/V
q_new = torch.randn(batch, num_heads, 1, head_dim)
k_new = torch.randn(batch, num_heads, 1, head_dim)
v_new = torch.randn(batch, num_heads, 1, head_dim)

# 把新 token 追加进缓存
all_k = torch.cat([cached_k, k_new], dim=2)
all_v = torch.cat([cached_v, v_new], dim=2)

# 当前 token 只需要拿自己的 q 去看整个历史
scores = torch.matmul(q_new, all_k.transpose(-2, -1)) / (head_dim ** 0.5)
weights = torch.softmax(scores, dim=-1)
output = torch.matmul(weights, all_v)

print(output.shape)  # [1, 4, 1, 8]
```

这段代码表达了三个关键点：

1. 历史 `K/V` 已经存在于缓存里  
2. 新 token 只把自己的 `K/V` 追加进去  
3. 当前 token 的 `Q` 去查询“历史 + 当前”的 `K/V`

这就是 KV Cache 的最基本直觉。

## 22. 在 Hugging Face Transformers 里，KV Cache 经常以什么形式出现

在 `transformers` 生态里，你经常会看到：

- `past_key_values`
- `use_cache=True`

比如：

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

inputs = tokenizer("Hello, how are", return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs, use_cache=True)

past_key_values = outputs.past_key_values
next_token_logits = outputs.logits[:, -1, :]
```

后续生成时，可以把 `past_key_values` 传回模型：

```python
next_token_id = next_token_logits.argmax(dim=-1, keepdim=True)

with torch.no_grad():
    outputs2 = model(
        input_ids=next_token_id,
        past_key_values=past_key_values,
        use_cache=True,
    )
```

这个 API 设计非常直接地体现了 KV Cache 的思想：

- 第一次前向，建立 cache
- 后续只喂新 token + past_key_values

## 23. 一个最小可运行示例：手工感受是否复用缓存

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
model.eval()

prompt = "The capital of France is"
inputs = tokenizer(prompt, return_tensors="pt")

with torch.no_grad():
    out = model(**inputs, use_cache=True)

past = out.past_key_values
next_id = out.logits[:, -1, :].argmax(dim=-1, keepdim=True)

generated_ids = [next_id]

for _ in range(10):
    with torch.no_grad():
        out = model(input_ids=next_id, past_key_values=past, use_cache=True)
    past = out.past_key_values
    next_id = out.logits[:, -1, :].argmax(dim=-1, keepdim=True)
    generated_ids.append(next_id)

all_ids = torch.cat([inputs["input_ids"]] + generated_ids, dim=1)
print(tokenizer.decode(all_ids[0], skip_special_tokens=True))
```

这段代码里的关键不是效果多好，而是你能看到：

- 第一轮输入整个 prompt
- 后面每轮只输入一个 token
- 但模型仍然知道整个历史

为什么它知道？因为历史在 `past_key_values` 里。

## 24. 常见误区

### 24.1 “KV Cache 会缓存全部计算结果”

不对。它缓存的是注意力相关的 `K/V`，不是整个网络每一步的所有中间张量。

### 24.2 “开了 KV Cache，长上下文就不贵了”

不对。长上下文仍然贵，只是没有那么重复地贵。

### 24.3 “KV Cache 主要优化训练”

不对。它主要优化推理，尤其是自回归解码。

### 24.4 “KV Cache 只和单卡推理有关”

不对。分布式推理、服务编排、批处理调度、长上下文系统设计，都深受 KV Cache 影响。

### 24.5 “KV Cache 越大越好”

不对。缓存大意味着上下文能力强，但也意味着显存成本更高、并发能力可能下降。

## 25. 做系统设计时，怎么看 KV Cache

如果你是从工程角度考虑推理服务，可以把 KV Cache 当作一个资源池问题。

你需要同时考虑：

- 单请求上下文长度
- 平均生成长度
- 请求并发数
- batch 调度策略
- 数据类型精度
- MHA / GQA / MQA 结构
- 是否启用 prefix caching
- 是否使用 paged attention

很多系统设计的本质，是在做下面几件事的平衡：

- 让 decode 足够快
- 让显存撑得住
- 让并发尽量高
- 让不同长度请求共存时浪费尽量少

## 26. 什么时候你应该特别关注 KV Cache

下面这些场景，KV Cache 基本都应该进入你的第一优先级分析：

- 聊天机器人响应慢
- 长上下文推理显存爆掉
- 服务并发上不去
- TTFT 和 TPOT 指标异常
- vLLM/TGI/自研推理服务需要调优
- 你在比较 MHA、GQA、MQA 的推理成本

其中：

- `TTFT`：time to first token，往往和 prefill 关系更大
- `TPOT`：time per output token，往往和 decode + KV Cache 更相关

## 27. 学习路径建议

如果你想把 KV Cache 放进更大的知识地图里，建议顺序是：

1. Transformer 自注意力  
2. 自回归解码  
3. Prefill / Decode 两阶段  
4. KV Cache  
5. MQA / GQA  
6. PagedAttention  
7. Continuous batching  
8. 长上下文推理优化

这条线走通之后，你对现代 LLM 推理系统的理解会清晰很多。

## 28. 最后的总结

你可以用下面这组句子快速回忆 `KV Cache`：

- 它缓存的是历史 token 的注意力 `K/V`
- 它主要用于推理，不是训练主优化
- 它的核心价值是避免重复重算历史上下文
- 它让 decode 阶段显著提速
- 它的代价是显存随上下文长度和并发增长
- `MQA/GQA` 可以降低 KV Cache 成本
- `PagedAttention` 是更高效的 KV Cache 管理方式

如果只保留一句话，就保留这句：

> `KV Cache` 的本质，是用显存换解码速度，用缓存复用历史注意力状态，避免自回归生成时对旧 token 做重复计算。

如果你愿意，下一步我可以继续把这份笔记扩展成两种版本之一：

1. 加一版“配图思维导图式”的极简讲义  
2. 再补一篇“从 KV Cache 到 PagedAttention 与 vLLM”的进阶笔记
