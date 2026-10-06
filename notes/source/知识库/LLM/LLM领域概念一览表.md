---
title: LLM领域概念一览表
tags:
  - LLM
  - AI
  - 速查表
  - 机器学习
  - RAG
  - Agent
  - 微调
created: 2026-05-14
updated: 2026-05-14
---

# LLM领域概念一览表

> 用途：把 LLM 领域主流概念按领域拆成多张表，方便面试、读论文、做项目和复盘时快速回忆。  
> 覆盖范围：基础概念、数学基础、数据、Tokenizer、Transformer、训练、微调/PEFT、对齐、推理、Prompt、RAG、Agent/MCP、评测、幻觉、部署/LLMOps、优化、安全、多模态、应用、生态、常见模型、研究热点、易混概念。  
> 说明：LLM 领域持续快速演化，严格意义上的“全部概念”不可能穷尽；本表尽量覆盖高频、主流、工程实用和近年热点概念。当前共整理 **891** 条概念。

## 总览心智图

```text
LLM 生命周期 = 数据 -> Tokenizer -> 预训练 -> 后训练/对齐 -> 推理 -> 应用/RAG/Agent -> 评测 -> 部署运维 -> 安全治理
核心技术线 = Transformer + Attention + Scaling Law + Instruction Tuning + RLHF/DPO/GRPO/RLVR + PEFT/LoRA + KV Cache + RAG + Tool/MCP + Agent
核心权衡 = 效果 vs 成本、上下文长度 vs 延迟、泛化 vs 过拟合、对齐 vs 能力、召回率 vs 精确率、安全 vs 可用性、自由度 vs 可控性
```

## 使用方法

- 想快速复习：只看每张表的「一句话速记」。
- 想面试准备：重点看「微调与PEFT」「对齐」「RAG」「评测」「推理」「易混概念」。
- 想做项目：重点看「提示工程」「RAG」「Agent」「部署」「安全」「LLMOps」。
- 想读论文：重点看「Transformer」「训练」「对齐」「优化」「研究热点」。

## 领域导航

- [[#基础定义]]（41 条）
- [[#数学基础]]（15 条）
- [[#数据]]（42 条）
- [[#Tokenization]]（16 条）
- [[#Transformer]]（52 条）
- [[#训练目标]]（11 条）
- [[#训练]]（55 条）
- [[#微调与PEFT]]（33 条）
- [[#对齐]]（37 条）
- [[#推理]]（57 条）
- [[#提示工程]]（38 条）
- [[#RAG]]（69 条）
- [[#Agent]]（52 条）
- [[#评测]]（60 条）
- [[#幻觉与事实性]]（15 条）
- [[#部署]]（51 条）
- [[#优化]]（34 条）
- [[#安全]]（36 条）
- [[#多模态]]（30 条）
- [[#应用]]（31 条）
- [[#框架生态]]（36 条）
- [[#常见模型]]（23 条）
- [[#研究热点]]（30 条）
- [[#易混概念]]（27 条）

## 基础定义

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| 大语言模型 | LLM, Large Language Model | 用海量文本训练、能生成和理解自然语言的深度学习模型。 | GPT、Llama、Claude、Qwen、Gemini |
| 生成式 AI | Generative AI | 能生成文本、图像、音频、视频、代码等内容的 AI。 | LLM 是生成式 AI 的重要分支 |
| 基座模型 | Foundation Model / Base Model | 大规模预训练得到的通用模型，尚未针对对话或指令充分对齐。 | 与 Chat Model、Instruct Model 区分 |
| 指令模型 | Instruct Model | 经过指令微调后更会听人话、按任务格式输出的模型。 | SFT、Instruction Tuning |
| 对话模型 | Chat Model | 面向多轮对话优化的模型，通常有 system/user/assistant 角色格式。 | Chat Template、System Prompt |
| 多模态大模型 | MLLM / VLM | 同时处理文本、图像、音频、视频等模态的模型。 | CLIP、Vision Encoder、Image Token |
| 参数 | Parameters | 模型中可学习的权重数量，常用 B 表示十亿参数。 | 7B、70B、MoE 活跃参数 |
| 计算量 | FLOPs | 模型训练或推理所需浮点运算量。 | 训练成本、推理成本、Scaling Law |
| 语料 | Corpus | 用于训练或评测的文本/多模态数据集合。 | 数据清洗、去重、版权 |
| 分布 | Distribution | 数据或任务出现的概率规律。 | OOD、泛化、数据偏移 |
| 泛化 | Generalization | 模型在未见样本或新任务上表现良好的能力。 | 过拟合、验证集、OOD |
| 涌现能力 | Emergent Ability | 模型规模变大后突然表现出的复杂能力。 | 推理、ICL、工具调用；是否“突然”存在争议 |
| 世界知识 | World Knowledge | 模型参数中隐式记住的事实和常识。 | 知识截止、幻觉、RAG |
| 知识截止 | Knowledge Cutoff | 模型训练数据覆盖到的最后时间范围。 | 过期信息需搜索/RAG |
| 上下文窗口 | Context Window | 一次推理中模型能看到的最大 token 数。 | 长上下文、KV Cache、位置编码 |
| Token | Token | 模型处理文本的基本单位，可能是字、词、子词或字节片段。 | Tokenizer、计费、上下文长度 |
| Tokenizer | Tokenizer | 把文本切分成 token 并映射为 ID 的工具。 | BPE、SentencePiece、词表 |
| 词表 | Vocabulary | Tokenizer 支持的全部 token 集合。 | OOV、特殊 token、扩词表 |
| 子词 | Subword | 介于字符和单词之间的切分单位。 | BPE、WordPiece、SentencePiece |
| 大模型 | Large Model | 参数、数据和计算规模显著扩大的模型统称。 | LLM、VLM、Diffusion、Foundation Model |
| 语言模型 | Language Model | 为文本序列分配概率或预测后续 token 的模型。 | n-gram、RNN、Transformer、LLM |
| 神经语言模型 | Neural LM | 用神经网络学习语言概率分布的语言模型。 | Word2Vec、RNNLM、Transformer |
| 上下文 | Context | 模型当前可见的输入、历史、检索结果和工具返回。 | Context Window、Memory、RAG |
| 上下文工程 | Context Engineering | 系统化组织指令、记忆、检索、工具结果和状态，使模型获得恰当上下文。 | Prompt Engineering 的工程化扩展 |
| 模型能力边界 | Capability Boundary | 模型在知识、推理、工具、长度、安全等方面的可用范围。 | 评测、红队、SLA |
| 开放权重 | Open Weights | 公开模型权重但许可未必等同开源。 | Llama、Qwen、Mistral；注意 license |
| 闭源模型 | Closed Model | 权重不公开，通常通过 API 或产品访问。 | OpenAI、Anthropic、Google 等 |
| 本地模型 | Local Model | 在个人电脑、服务器或边缘设备本地运行的模型。 | Ollama、llama.cpp、GGUF |
| 云端模型 | Hosted Model | 由云厂商或模型厂商托管的模型服务。 | API、SLA、配额、数据合规 |
| 模型卡 | Model Card | 描述模型能力、限制、训练数据、评测和风险的文档。 | 透明度、合规 |
| 数据卡 | Data Card | 描述数据来源、处理、偏差、许可和使用限制的文档。 | Dataset Documentation |
| 许可证 | License | 规定模型/数据/代码可用范围的法律条款。 | Apache-2.0、MIT、Llama License、商业限制 |
| 参数量 | Parameter Count | 模型权重数量，通常用 M/B/T 表示。 | 不等于能力；还看数据和训练 |
| 激活参数 | Active Parameters | MoE 推理时每个 token 实际参与计算的参数量。 | 总参数 vs 活跃参数 |
| 训练 Token 数 | Training Tokens | 预训练中模型看过的 token 总量。 | Chinchilla、数据规模 |
| 上下文预算 | Context Budget | 在有限上下文窗口中分配给指令、历史、证据、工具结果的 token 配额。 | 上下文工程、RAG |
| 能力涌现争议 | Emergence Debate | 部分能力是否真正突然出现，还是指标尺度造成的现象。 | Scaling Law、评测设计 |
| 分布内 | In-distribution / ID | 输入与训练/评测分布相近。 | 泛化较可靠 |
| 分布外 | Out-of-distribution / OOD | 输入明显偏离训练/评测分布。 | 鲁棒性、失败模式 |
| 归纳偏置 | Inductive Bias | 模型结构或训练方式自带的偏好。 | Transformer、位置编码 |
| 容量 | Capacity | 模型可表示复杂函数或知识的能力。 | 参数、架构、训练数据 |

## 数学基础

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| 张量 | Tensor | 多维数组，是深度学习中数据和参数的基本表示。 | 标量、向量、矩阵 |
| 矩阵乘法 | MatMul / GEMM | Transformer 中最主要计算形式。 | GPU/TPU 加速、FLOPs |
| Softmax | Softmax | 把 logits 转成概率分布。 | 注意力权重、token 采样 |
| 反向传播 | Backpropagation | 根据损失计算梯度并更新参数。 | 自动微分、优化器 |
| 梯度 | Gradient | 损失对参数的导数，指示更新方向。 | 梯度爆炸/消失、裁剪 |
| 梯度爆炸 | Gradient Explosion | 梯度过大导致训练不稳定。 | 梯度裁剪、归一化 |
| 梯度消失 | Gradient Vanishing | 梯度过小导致深层参数难更新。 | 残差连接、归一化 |
| 正则化 | Regularization | 限制模型复杂度以改善泛化。 | Dropout、Weight Decay、数据增强 |
| 最大似然估计 | MLE | 最大化训练数据在模型下出现概率。 | 交叉熵、NLL |
| 负对数似然 | NLL | 真实 token 概率的负对数。 | 交叉熵、PPL |
| KL 散度 | KL Divergence | 衡量两个概率分布差异。 | RLHF、蒸馏、对齐约束 |
| 熵 | Entropy | 概率分布的不确定性。 | 采样、多样性、校准 |
| 余弦退火 | Cosine Annealing | 学习率按余弦曲线逐步衰减。 | Scheduler |
| 范数 | Norm | 向量或矩阵大小的度量。 | L1/L2、梯度裁剪 |
| 低秩分解 | Low-rank Factorization | 用较小矩阵近似大矩阵变化。 | LoRA 的数学基础 |

## 数据

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| 训练集 | Training Set | 用来更新模型参数的数据。 | 验证集、测试集、数据泄露 |
| 验证集 | Validation Set | 训练过程中用于调参和早停的数据。 | 不应参与训练 |
| 测试集 | Test Set | 最终评估模型泛化能力的数据。 | 数据污染会虚高分数 |
| 数据清洗 | Data Cleaning | 去除低质、重复、脏内容、乱码、模板垃圾等。 | 质量通常比数量更关键 |
| 数据去重 | Deduplication | 删除重复或近重复样本，降低记忆和数据泄露。 | MinHash、SimHash、n-gram |
| 数据过滤 | Data Filtering | 按质量、安全、领域、语言等规则筛选数据。 | 规则过滤、模型过滤 |
| 数据配比 | Data Mixture | 不同来源、语言、领域数据的混合比例。 | 影响能力结构和偏差 |
| 数据污染 | Data Contamination | 训练数据包含测试题或评测答案导致评估失真。 | Benchmark 泄露 |
| 合成数据 | Synthetic Data | 由模型或程序生成的数据。 | Self-Instruct、蒸馏、数据增强 |
| 数据增强 | Data Augmentation | 对样本做变换以增加多样性和鲁棒性。 | 改写、翻译、扰动 |
| 数据标注 | Data Annotation | 人工或模型给数据添加标签、答案、偏好等监督信号。 | SFT、RLHF、偏好数据 |
| 偏好数据 | Preference Data | 人类或模型对多个回答进行优劣排序的数据。 | RLHF、DPO、Reward Model |
| 指令数据 | Instruction Data | 形如“任务说明 + 输入 + 期望输出”的训练样本。 | Alpaca、ShareGPT、SFT |
| 对话数据 | Dialogue Data | 多轮角色对话样本。 | Chat Template、上下文压缩 |
| 领域数据 | Domain Data | 医疗、法律、金融、代码等特定领域语料。 | 领域继续预训练、领域微调 |
| 高质量数据 | High-quality Data | 准确、干净、多样、推理链清晰、符合目标任务的数据。 | 小而精常优于大而脏 |
| 数据飞轮 | Data Flywheel | 用户反馈和线上日志持续反哺数据与模型迭代。 | 反馈闭环、主动学习 |
| 主动学习 | Active Learning | 优先挑选最有价值样本进行标注。 | 不确定性采样、困难样本 |
| 预训练数据 | Pretraining Data | 用于基础模型大规模学习的通用语料。 | 网页、书籍、代码、论文、多语言 |
| 后训练数据 | Post-training Data | 用于 SFT、偏好、安全、推理强化的数据。 | 指令、偏好、拒答、工具调用 |
| 评测集泄露 | Benchmark Leakage | 评测样本进入训练或调参流程导致分数虚高。 | 数据污染 |
| 近重复 | Near Duplicate | 语义或文本高度相似但不完全一样的样本。 | MinHash、SimHash |
| MinHash | MinHash | 快速估计集合相似度的去重方法。 | 网页去重、n-gram shingles |
| SimHash | SimHash | 把文本映射成哈希以检测近似重复。 | 海量网页去重 |
| 质量打分 | Quality Scoring | 给样本质量打分后筛选或加权。 | 分类器、LLM Judge、规则 |
| 毒性过滤 | Toxicity Filtering | 过滤仇恨、暴力、色情等有害内容。 | 安全与偏差权衡 |
| PII 过滤 | PII Filtering | 识别并移除个人敏感信息。 | 隐私合规 |
| 语言识别 | Language Identification | 判断文本语言以做配比和过滤。 | 多语言训练 |
| 代码数据 | Code Data | GitHub、StackOverflow、文档等代码相关语料。 | 代码模型、许可风险 |
| 数学数据 | Math Data | 数学题、证明、推导、竞赛题数据。 | 推理模型、RLVR |
| 轨迹数据 | Trajectory Data | Agent 执行过程中的状态、动作、观察序列。 | Tool Use、Agent 训练 |
| 拒答数据 | Refusal Data | 教模型在危险请求上拒绝的样本。 | 安全微调、过度拒答 |
| 边界样本 | Boundary Cases | 位于规则或能力边缘的困难样本。 | 红队、安全、鲁棒性 |
| 困难负样本 | Hard Negative | 与查询相似但实际不相关的负例。 | 检索训练、Reranker |
| 弱监督 | Weak Supervision | 使用规则、启发式或模型生成的低成本标签。 | 伪标签、Snorkel |
| 伪标签 | Pseudo Label | 模型为无标注数据生成的标签。 | 自训练、半监督 |
| 数据版本 | Data Versioning | 记录数据集版本、来源和处理流程。 | 可复现、审计 |
| 数据血缘 | Data Lineage | 追踪数据从来源到训练/评测的流转。 | 合规、排错 |
| 数据许可证过滤 | License Filtering | 按版权和许可证筛选可训练数据。 | 商业模型合规 |
| 数据治理 | Data Governance | 对数据质量、权限、隐私、合规进行管理。 | 企业 RAG/训练 |
| 数据策展 | Data Curation | 有目标地选择、清洗、组织高价值数据。 | Data-centric AI |
| 课程学习 | Curriculum Learning | 按难度或阶段组织训练数据。 | 推理训练、多阶段后训练 |

## Tokenization

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| BPE | Byte Pair Encoding | 反复合并高频字符片段形成子词词表。 | GPT 系常见分词方法 |
| SentencePiece | SentencePiece | 不依赖空格的子词分词工具，适合多语言。 | Unigram、BPE |
| 特殊 Token | Special Token | 表示 BOS/EOS/PAD/角色分隔等控制语义的 token。 | Chat Template、停止条件 |
| BOS | Beginning of Sequence | 序列开始标记。 | 解码起点 |
| EOS | End of Sequence | 序列结束标记。 | 生成停止、截断 |
| PAD | Padding Token | 批处理时补齐长度的 token。 | Attention Mask |
| Attention Mask | Attention Mask | 控制模型哪些位置可见、哪些位置被忽略。 | Padding、Causal Mask |
| Byte-level BPE | Byte-level BPE | 以字节为基础的 BPE，能覆盖任意字符。 | GPT tokenizer 常见 |
| Unigram LM Tokenizer | Unigram | 从候选子词中学习概率分词模型。 | SentencePiece |
| WordPiece | WordPiece | BERT 常用的子词分词算法。 | ## 前缀、MLM |
| OOV | Out-of-Vocabulary | 词表外字符或词无法直接表示。 | 子词/字节分词可缓解 |
| Chat Template | Chat Template | 把多轮角色消息序列化成模型训练时约定的文本格式。 | system/user/assistant、特殊 token |
| Token Healing | Token Healing | 修复提示末尾分词不完整导致的生成异常。 | 补全、解码细节 |
| 截断 | Truncation | 输入超过上限时裁剪部分 token。 | 长上下文、重要信息丢失 |
| 填充 | Padding | 把不同长度样本补齐以组成 batch。 | PAD、Attention Mask |
| 词表扩展 | Vocabulary Expansion | 向 tokenizer 添加新 token。 | 领域术语、多模态特殊 token |

## Transformer

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| Transformer | Transformer | 基于注意力机制的主流 LLM 架构。 | Encoder、Decoder、Attention |
| Encoder | Encoder | 把输入编码成上下文表示，擅长理解任务。 | BERT 类模型 |
| Decoder | Decoder | 自回归生成下一个 token，主流 LLM 多为 Decoder-only。 | GPT、Llama、Qwen |
| Encoder-Decoder | Seq2Seq | 编码输入再解码输出，常用于翻译、摘要。 | T5、BART |
| Decoder-only | Decoder-only | 只用解码器堆叠，通过预测下一个 token 训练。 | 当前主流生成式 LLM |
| 注意力机制 | Attention | 根据相关性动态聚合其他 token 信息。 | Self-Attention、Cross-Attention |
| 自注意力 | Self-Attention | 同一序列内部 token 互相关注。 | Q/K/V、复杂度 O(n²) |
| 交叉注意力 | Cross-Attention | 一个序列关注另一个序列的信息。 | 多模态、Encoder-Decoder |
| 多头注意力 | Multi-Head Attention / MHA | 多组注意力头并行捕捉不同关系。 | Head、GQA、MQA |
| Q/K/V | Query/Key/Value | 注意力计算中的查询、键、值向量。 | Attention Score = QKᵀ |
| 注意力头 | Attention Head | 一组独立的 Q/K/V 投影。 | 剪枝、可解释性 |
| 前馈网络 | FFN / MLP | Transformer 层中的非线性变换模块。 | SwiGLU、GeLU |
| 残差连接 | Residual Connection | 将输入直接加到输出，缓解深层训练困难。 | LayerNorm、梯度流 |
| 层归一化 | LayerNorm | 对隐藏向量归一化，稳定训练。 | Pre-LN、Post-LN、RMSNorm |
| RMSNorm | RMSNorm | 只用均方根归一化的 LayerNorm 变体。 | Llama 常用 |
| 激活函数 | Activation | 引入非线性的函数。 | GeLU、ReLU、SwiGLU |
| SwiGLU | SwiGLU | 带门控的激活结构，常提升大模型性能。 | PaLM、Llama |
| Dropout | Dropout | 训练时随机丢弃部分激活以正则化。 | 大规模预训练中有时较少用 |
| 位置编码 | Positional Encoding | 给 token 注入位置信息。 | RoPE、ALiBi、绝对位置 |
| RoPE | Rotary Position Embedding | 用旋转方式编码相对位置信息。 | 长上下文扩展常见 |
| ALiBi | Attention with Linear Biases | 在注意力分数中加入距离偏置。 | 长度外推 |
| Causal Mask | Causal Mask | 生成时只能看当前位置之前的 token。 | 自回归、下三角 Mask |
| KV Cache | Key-Value Cache | 推理时缓存历史 token 的 K/V，避免重复计算。 | 加速生成、显存占用 |
| GQA | Grouped-Query Attention | 多个 Query 头共享较少 K/V 头，兼顾效果和速度。 | MHA 与 MQA 折中 |
| MQA | Multi-Query Attention | 多个 Query 头共享一组 K/V，显著省 KV Cache。 | 推理加速 |
| FlashAttention | FlashAttention | 更省显存、更快的精确注意力实现。 | IO-aware、长上下文 |
| Sliding Window Attention | SWA | 只关注局部窗口内 token，降低长序列成本。 | Mistral、局部注意力 |
| 稀疏注意力 | Sparse Attention | 只计算部分注意力连接以降低复杂度。 | Longformer、BigBird |
| Pre-LN | Pre LayerNorm | 在子层前做归一化，深层训练更稳定。 | 现代 LLM 常用 |
| Post-LN | Post LayerNorm | 在子层后做归一化，早期 Transformer 常见。 | 深层训练可能不稳 |
| GeLU | Gaussian Error Linear Unit | BERT/GPT 系常用激活函数。 | FFN |
| ReLU | Rectified Linear Unit | 经典非线性激活函数。 | FFN、稀疏激活 |
| 门控线性单元 | GLU | 用门控控制信息流的前馈结构。 | SwiGLU、GEGLU |
| GEGLU | GEGLU | GeLU 版本的门控 FFN。 | T5 变体 |
| Embedding 层 | Embedding Layer | 把 token ID 映射成连续向量。 | 输入嵌入、词表 |
| 输出头 | LM Head | 把隐藏状态映射回词表 logits。 | 权重共享、解码 |
| 权重共享 | Weight Tying | 输入 embedding 与输出头共享权重。 | 省参数、语言模型 |
| 隐藏维度 | Hidden Size | 每个 token 表示向量的维度。 | 模型宽度 |
| 层数 | Number of Layers | Transformer Block 堆叠数量。 | 模型深度 |
| 头维度 | Head Dimension | 每个注意力头的向量维度。 | hidden_size / num_heads |
| 绝对位置编码 | Absolute PE | 直接给每个位置一个固定或学习的位置向量。 | BERT、早期 Transformer |
| 相对位置编码 | Relative PE | 编码 token 之间相对距离。 | T5 Bias、Transformer-XL |
| RoPE Scaling | RoPE Scaling | 调整 RoPE 频率或尺度以扩展上下文。 | NTK、YaRN、LongRoPE |
| NTK Scaling | NTK-aware Scaling | 一种 RoPE 长上下文外推缩放方法。 | 长上下文微调 |
| YaRN | Yet another RoPE extensioN | RoPE 长上下文扩展方法。 | Long Context |
| 状态空间模型 | SSM, State Space Model | 用状态空间结构处理长序列的替代/补充架构。 | Mamba、长序列 |
| Mamba | Mamba | 选择性状态空间模型，线性复杂度处理序列。 | 非 Transformer 语言模型方向 |
| RetNet | Retention Network | 用 retention 机制替代注意力的一类架构。 | 长序列、并行训练 |
| RWKV | RWKV | 结合 RNN 推理和 Transformer 训练特性的架构。 | 长上下文、本地模型 |
| Linear Attention | Linear Attention | 将注意力复杂度从 O(n²) 降到近似线性。 | 长序列、近似注意力 |
| 局部-全局注意力 | Local-Global Attention | 结合局部窗口和少量全局 token 的注意力。 | Longformer、BigBird |
| 专家混合层 | MoE Layer | 用多个 FFN 专家替代单个 FFN 的层。 | Mixtral、DeepSeek-V2/V3 类 |

## 训练目标

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| 语言建模 | Language Modeling | 学习文本序列概率分布。 | CLM、MLM |
| 因果语言模型 | CLM, Causal LM | 根据前文预测下一个 token。 | GPT 式预训练 |
| 掩码语言模型 | MLM, Masked LM | 遮住部分 token 让模型预测。 | BERT 式预训练 |
| 下一个 Token 预测 | Next Token Prediction | LLM 最核心训练目标之一。 | 自回归生成 |
| 交叉熵损失 | Cross-Entropy Loss | 衡量预测分布与真实 token 的差异。 | NLL、困惑度 |
| 困惑度 | Perplexity / PPL | 衡量语言模型预测不确定性，越低通常越好。 | 不等于任务能力全貌 |
| 去噪自编码 | Denoising Autoencoding | 破坏输入后训练模型恢复原文。 | BART、T5 |
| Span Corruption | Span Corruption | 遮住连续片段并让模型恢复。 | T5 预训练 |
| 对比学习 | Contrastive Learning | 拉近正样本表示、推远负样本表示。 | CLIP、Embedding 模型 |
| 排序损失 | Ranking Loss | 训练模型把好答案排在坏答案前。 | Reward Model、Reranker |
| 对比损失 | Contrastive Loss | 用于学习相似/不相似样本距离。 | Embedding、双塔模型 |

## 训练

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| 预训练 | Pretraining | 在大规模通用语料上学习基础语言和知识能力。 | Base Model、Scaling Law |
| 继续预训练 | Continued Pretraining / CPT | 在已有模型上继续用通用或领域语料训练。 | 领域适配、灾难性遗忘 |
| 领域自适应预训练 | DAPT | 用特定领域语料继续预训练。 | 医疗/法律/金融模型 |
| 任务自适应预训练 | TAPT | 用目标任务相关无标注数据继续预训练。 | 小任务提升 |
| 后训练 | Post-training | 预训练后进行 SFT、偏好对齐、安全对齐等。 | Instruct/Chat 模型形成阶段 |
| 冻结参数 | Freeze Parameters | 保持部分参数不更新。 | PEFT、多模态投影层训练 |
| 学习率 | Learning Rate | 每次参数更新步长。 | Warmup、Cosine Decay |
| Warmup | Warmup | 训练初期逐渐升高学习率，稳定训练。 | Scheduler |
| 学习率调度 | LR Scheduler | 训练中动态调整学习率。 | Cosine、Linear、Step |
| 批大小 | Batch Size | 每次参数更新使用的样本数量。 | 显存、稳定性、吞吐 |
| 梯度累积 | Gradient Accumulation | 多个小 batch 累积梯度模拟大 batch。 | 显存不足时常用 |
| 梯度裁剪 | Gradient Clipping | 限制梯度范数，防止梯度爆炸。 | 稳定训练 |
| 权重衰减 | Weight Decay | 对权重加惩罚，减少过拟合。 | AdamW |
| 优化器 | Optimizer | 根据梯度更新参数的算法。 | Adam、AdamW、Adafactor |
| AdamW | AdamW | 常用优化器，解耦权重衰减。 | LLM 微调常见 |
| 混合精度训练 | Mixed Precision | 使用 FP16/BF16 等降低显存、加速训练。 | AMP、Loss Scaling |
| BF16 | Brain Float16 | 指数位更多的 16 位浮点，训练更稳定。 | A100/H100 常用 |
| FP16 | Float16 | 半精度浮点，省显存但可能数值不稳定。 | Loss Scaling |
| 梯度检查点 | Gradient Checkpointing | 反向传播时重算部分激活以节省显存。 | 以时间换显存 |
| 过拟合 | Overfitting | 模型记住训练集而泛化变差。 | 验证损失上升、正则化 |
| 欠拟合 | Underfitting | 模型能力或训练不足，训练集也学不好。 | 增大模型/训练步数 |
| 早停 | Early Stopping | 验证指标不再提升时停止训练。 | 防过拟合 |
| Checkpoint | Checkpoint | 保存的模型参数和训练状态。 | 断点续训、模型选择 |
| Epoch | Epoch | 全部训练数据被模型看过一遍。 | Step、Iteration |
| Step | Step | 一次参数更新。 | 梯度累积会影响等效 step |
| 分布式训练 | Distributed Training | 多 GPU/多节点共同训练。 | DP、TP、PP、ZeRO |
| 数据并行 | Data Parallelism / DP | 每张卡放完整模型、处理不同数据。 | DDP、梯度同步 |
| 张量并行 | Tensor Parallelism / TP | 把单层矩阵计算切到多张卡。 | Megatron-LM |
| 流水线并行 | Pipeline Parallelism / PP | 把不同层放到不同设备分段执行。 | Bubble、Micro-batch |
| ZeRO | Zero Redundancy Optimizer | 切分优化器状态、梯度、参数以省显存。 | DeepSpeed ZeRO-1/2/3 |
| FSDP | Fully Sharded Data Parallel | PyTorch 的全切分数据并行。 | 参数/梯度/优化器切分 |
| Scaling Law | Scaling Law | 模型规模、数据量、计算量与性能之间的经验规律。 | Chinchilla、算力最优 |
| Chinchilla Law | Chinchilla Scaling | 给定算力下模型参数和训练 token 应平衡。 | 过大模型不如多训练数据 |
| 断点续训 | Resume Training | 从 checkpoint 恢复训练状态继续训练。 | 优化器状态、随机种子 |
| 随机种子 | Random Seed | 控制随机初始化和采样以提高可复现性。 | 仍可能受硬件非确定性影响 |
| 可复现性 | Reproducibility | 别人能在相同条件下复现实验结果。 | 种子、数据版本、环境 |
| 训练稳定性 | Training Stability | 训练过程中 loss、梯度和指标不异常发散。 | LR、归一化、初始化 |
| 损失尖峰 | Loss Spike | 训练 loss 突然升高。 | 数据异常、学习率、数值问题 |
| NaN | NaN | 数值计算出现非数字，训练通常崩溃。 | 混合精度、梯度爆炸 |
| 激活检查点 | Activation Checkpointing | 不保存全部激活，反向时重算。 | 同梯度检查点 |
| 序列并行 | Sequence Parallelism | 把序列维度切分到多设备。 | Megatron、长上下文 |
| 上下文并行 | Context Parallelism | 将长上下文计算跨设备切分。 | 长序列训练 |
| 专家并行 | Expert Parallelism | MoE 专家分布到不同设备。 | MoE 训练 |
| 混合并行 | Hybrid Parallelism | 组合 DP/TP/PP/EP 等并行方式。 | 超大模型训练 |
| All-Reduce | All-Reduce | 分布式训练中聚合梯度的通信操作。 | DDP、通信瓶颈 |
| 通信开销 | Communication Overhead | 多卡/多机同步带来的时间成本。 | 带宽、拓扑、并行策略 |
| 显存优化 | Memory Optimization | 减少训练/推理显存占用的方法集合。 | ZeRO、Checkpoint、量化 |
| 吞吐优化 | Throughput Optimization | 提高每秒训练或推理 token 数。 | Batch、并行、kernel 优化 |
| 数据加载器 | DataLoader | 读取、打乱、批处理训练数据的组件。 | I/O 瓶颈、Streaming |
| 流式数据集 | Streaming Dataset | 不完整下载数据，边读边训练。 | 海量数据、HF datasets |
| Packing | Sequence Packing | 把多个短样本拼到同一序列减少 padding。 | SFT 提效，但注意样本边界 |
| 样本权重 | Sample Weighting | 不同样本对 loss 贡献不同。 | 数据配比、难例加权 |
| 标签平滑 | Label Smoothing | 降低 one-hot 标签尖锐度以正则化。 | 分类/生成训练 |
| 训练-推理不一致 | Train-Inference Mismatch | 训练条件与真实推理条件不同导致性能差。 | Exposure Bias、工具轨迹 |
| 暴露偏差 | Exposure Bias | 训练看真实前缀，推理看自己生成前缀导致误差积累。 | 自回归生成 |

## 微调与PEFT

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| 监督微调 | SFT, Supervised Fine-Tuning | 用高质量“输入-答案”样本让模型学会按指令回答。 | 指令微调、全参/PEFT |
| 指令微调 | Instruction Tuning | 用多任务指令数据提升模型遵循指令能力。 | 常作为 SFT 的一种 |
| 微调 | Fine-tuning | 在已有模型上用新数据更新参数以适配任务或风格。 | 全参微调、LoRA、过拟合 |
| 全参微调 | Full Fine-tuning | 更新模型全部参数，效果强但成本高、风险大。 | 灾难性遗忘、显存需求 |
| 参数高效微调 | PEFT | 只训练少量新增或局部参数来适配任务。 | LoRA、Adapter、Prefix Tuning |
| LoRA | Low-Rank Adaptation | 用低秩矩阵增量近似权重更新，只训练小矩阵。 | r、alpha、merge、QLoRA |
| QLoRA | Quantized LoRA | 基座模型量化后训练 LoRA，显著省显存。 | 4-bit、NF4、bitsandbytes |
| AdaLoRA | Adaptive LoRA | 动态分配不同层/模块的 LoRA 秩。 | 参数预算优化 |
| Adapter | Adapter Tuning | 在模型层间插入小模块，只训练 Adapter。 | PEFT 早期主流方法 |
| Prefix Tuning | Prefix Tuning | 训练可学习前缀向量影响生成。 | Prompt Tuning、P-Tuning |
| Prompt Tuning | Prompt Tuning | 训练软提示向量而不改主模型参数。 | Soft Prompt |
| P-Tuning v2 | P-Tuning v2 | 深层连续提示调优方法。 | 中文模型早期常见 |
| BitFit | BitFit | 只微调 bias 参数。 | 参数极少，能力有限 |
| 灾难性遗忘 | Catastrophic Forgetting | 微调新任务时丢失原有通用能力或旧任务能力。 | CPT/SFT、混合回放、低学习率 |
| LoRA 秩 | LoRA Rank / r | LoRA 低秩矩阵的秩，越大容量越强但参数越多。 | r=8/16/64 常见 |
| LoRA Alpha | LoRA Alpha | 控制 LoRA 增量缩放强度的超参数。 | alpha/r scaling |
| LoRA Dropout | LoRA Dropout | 训练 LoRA 时对增量路径做 dropout。 | 正则化 |
| Target Modules | Target Modules | 指定 LoRA 注入哪些层或矩阵。 | q_proj、v_proj、o_proj、mlp |
| LoRA Merge | Merge LoRA | 把 LoRA 增量合并进基座权重用于部署。 | 不可随意多次 merge |
| 多 LoRA 切换 | Multi-LoRA Serving | 同一基座模型动态加载多个 LoRA 适配器。 | 个性化、租户隔离 |
| Adapter Fusion | Adapter Fusion | 融合多个 adapter 的知识。 | 多任务迁移 |
| IA3 | IA³ | 通过缩放激活向量进行参数高效微调。 | PEFT 方法 |
| 软提示 | Soft Prompt | 可学习的连续向量提示，不是自然语言。 | Prompt Tuning |
| 硬提示 | Hard Prompt | 人工编写的自然语言提示。 | Prompt Engineering |
| 微调数据模板 | Fine-tuning Template | 把样本组织成模型期望的训练文本格式。 | Chat Template、特殊 token |
| 监督信号 | Supervision Signal | 训练中告诉模型什么输出更好的信号。 | 标签、偏好、奖励 |
| 验证损失 | Validation Loss | 验证集上的 loss，用于判断过拟合和选 checkpoint。 | 早停 |
| 混合回放 | Replay / Rehearsal | 微调时混入旧任务或通用数据防遗忘。 | 灾难性遗忘 |
| EWC | Elastic Weight Consolidation | 通过限制重要参数变化缓解灾难性遗忘。 | 连续学习 |
| 领域漂移 | Domain Shift | 训练/微调数据与真实使用数据分布不同。 | 泛化、线上监控 |
| 指令泛化 | Instruction Generalization | 模型遵循未见过指令形式的能力。 | Instruction Tuning |
| 格式学习 | Format Learning | 模型学会固定 JSON、表格、代码等输出格式。 | SFT、结构化输出 |
| 风格迁移 | Style Adaptation | 让模型输出符合特定语气、品牌或文体。 | SFT、Prompt、LoRA |

## 对齐

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| 对齐 | Alignment | 让模型行为符合人类意图、偏好和安全要求。 | RLHF、DPO、安全微调 |
| RLHF | Reinforcement Learning from Human Feedback | 用人类偏好训练奖励模型，再用强化学习优化 LLM。 | Reward Model、PPO |
| 奖励模型 | Reward Model / RM | 判断回答好坏并给分的模型。 | 偏好数据、RLHF |
| PPO | Proximal Policy Optimization | RLHF 中常用的策略优化算法。 | KL 惩罚、训练复杂 |
| KL 惩罚 | KL Penalty | 限制新模型偏离参考模型过多。 | 防止奖励黑客 |
| DPO | Direct Preference Optimization | 不训练显式奖励模型，直接用偏好对优化策略。 | RLHF 替代方案之一 |
| IPO | Identity Preference Optimization | DPO 类偏好优化方法。 | 偏好学习 |
| KTO | Kahneman-Tversky Optimization | 用好/坏样本信号进行偏好对齐的方法。 | 不一定需要成对偏好 |
| ORPO | Odds Ratio Preference Optimization | 把 SFT 与偏好优化结合的后训练方法。 | 简化对齐流程 |
| RLAIF | RL from AI Feedback | 用 AI 反馈替代或辅助人类反馈。 | Constitutional AI、成本更低 |
| 宪法 AI | Constitutional AI | 用一组原则指导模型自我批判和修正。 | Anthropic、RLAIF |
| 拒答 | Refusal | 对危险、非法或不合规请求拒绝回答。 | 过度拒答、安全对齐 |
| 过度对齐 | Over-alignment | 模型过度安全或迎合导致能力下降/拒答过多。 | Helpfulness vs Safety |
| 奖励黑客 | Reward Hacking | 模型钻奖励函数漏洞而非真正变好。 | RLHF 风险 |
| 迎合 | Sycophancy | 模型倾向附和用户错误观点。 | 对齐副作用、评测重点 |
| 后训练流水线 | Post-training Pipeline | 从 SFT 到偏好优化、安全对齐、评测筛选的多阶段流程。 | SFT -> DPO/RLHF/RLVR -> Safety |
| 偏好优化 | Preference Optimization | 利用好坏回答偏好改进模型行为。 | DPO、IPO、KTO、ORPO |
| Bradley-Terry 模型 | Bradley-Terry Model | 用成对比较建模偏好概率。 | Reward Model、DPO |
| 参考模型 | Reference Model | 对齐训练中用于约束偏离程度的原始模型。 | DPO、KL |
| 策略模型 | Policy Model | RLHF/RL 中被优化的生成模型。 | PPO、GRPO |
| 价值模型 | Value Model | 估计当前状态未来奖励的模型。 | PPO、Actor-Critic |
| Actor-Critic | Actor-Critic | 同时学习策略和价值函数的强化学习框架。 | PPO |
| GRPO | Group Relative Policy Optimization | 用同题多样本组内相对奖励做 RL 优化，常用于推理模型训练。 | RLVR、DeepSeek-R1 类讨论 |
| DAPO | Decoupled Clip and Dynamic Sampling Policy Optimization | 面向 LLM 强化学习的策略优化变体。 | RL 后训练研究 |
| RLVR | RL with Verifiable Rewards | 用可验证答案自动给奖励的强化学习。 | 数学、代码、逻辑任务 |
| 过程监督 | Process Supervision | 对推理中间步骤给监督或奖励。 | PRM、数学推理 |
| 结果监督 | Outcome Supervision | 只根据最终答案对错给监督或奖励。 | ORM、RLVR |
| 过程奖励模型 | PRM, Process Reward Model | 给推理步骤质量打分的奖励模型。 | Step-level verification |
| 结果奖励模型 | ORM, Outcome Reward Model | 给最终答案质量打分的奖励模型。 | Answer verification |
| 拒答校准 | Refusal Calibration | 让模型该拒绝时拒绝、不该拒绝时回答。 | 安全与可用性平衡 |
| 安全后训练 | Safety Post-training | 专门降低有害输出、隐私泄露和越权行为的训练。 | 红队数据、拒答数据 |
| 有用性 | Helpfulness | 回答是否解决用户问题。 | HHH、RLHF |
| 诚实性 | Honesty | 模型不编造、不假装知道。 | 不确定性、校准 |
| 无害性 | Harmlessness | 模型避免造成伤害。 | 安全策略、拒答 |
| HHH | Helpful, Honest, Harmless | 对齐目标的经典三元组。 | RLHF、安全评测 |
| 可控性 | Controllability | 用户或系统能稳定控制模型风格、格式和边界。 | Prompt、SFT、Guardrail |
| 价值对齐 | Value Alignment | 模型行为与人类价值和社会规范一致。 | 伦理、安全 |

## 推理

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| 推理 | Inference | 使用训练好的模型生成输出。 | 延迟、吞吐、显存 |
| 自回归生成 | Autoregressive Generation | 每次生成一个 token，再把它作为上下文继续生成。 | Decoder-only LLM |
| 解码 | Decoding | 从概率分布中选择下一个 token 的策略。 | Greedy、Beam、Sampling |
| 贪心解码 | Greedy Decoding | 每步选择概率最高的 token。 | 稳定但可能死板 |
| Beam Search | Beam Search | 保留多个候选序列搜索高概率输出。 | 翻译常见，开放生成未必好 |
| 采样 | Sampling | 按概率随机选择 token，增加多样性。 | Temperature、Top-k、Top-p |
| 温度 | Temperature | 控制输出随机性；越高越发散，越低越保守。 | 0 接近确定性 |
| Top-k | Top-k Sampling | 只在概率最高的 k 个 token 中采样。 | 多样性控制 |
| Top-p | Nucleus Sampling | 只在累计概率达到 p 的候选中采样。 | 常比 Top-k 自适应 |
| 重复惩罚 | Repetition Penalty | 降低已出现 token 再出现概率。 | 防复读 |
| 停止词 | Stop Sequence | 生成遇到指定字符串或 token 时停止。 | API 输出控制 |
| 最大生成长度 | Max Tokens | 限制输出 token 数。 | 成本、截断 |
| Logits | Logits | softmax 前的未归一化分数。 | Logit Bias、采样 |
| Logprobs | Log Probabilities | token 的对数概率。 | 置信度分析、重排序 |
| Logit Bias | Logit Bias | 人为提高或降低某些 token 概率。 | 结构化输出控制 |
| 批处理推理 | Batch Inference | 多个请求合并推理以提升吞吐。 | 动态批处理 |
| 动态批处理 | Dynamic Batching | 在线把短时间内请求合成 batch。 | 吞吐 vs 延迟 |
| 连续批处理 | Continuous Batching | 生成过程中动态加入/移除请求。 | vLLM、PagedAttention |
| PagedAttention | PagedAttention | 像分页内存一样管理 KV Cache。 | vLLM 核心优化 |
| Speculative Decoding | Speculative Decoding | 小模型草拟，大模型验证，加速生成。 | Draft Model、接受率 |
| Early Exit | Early Exit | 中间层提前输出以节省计算。 | 速度/质量权衡 |
| 流式输出 | Streaming | 边生成边返回 token。 | 聊天体验、SSE |
| 延迟 | Latency | 用户等待单次请求返回的时间。 | TTFT、TPOT |
| 首 Token 时间 | TTFT | 从请求到第一个 token 出现的时间。 | 交互体验关键 |
| 每 Token 时间 | TPOT | 生成后续 token 的平均耗时。 | 解码速度 |
| 吞吐 | Throughput | 单位时间处理的请求或 token 数。 | QPS、tokens/s |
| 上下文压缩 | Context Compression | 压缩历史或检索内容以塞进上下文。 | 摘要、裁剪、记忆 |
| 长上下文 | Long Context | 支持几十万甚至更多 token 的上下文窗口。 | RoPE 扩展、注意力成本 |
| Lost in the Middle | Lost in the Middle | 长上下文中模型容易忽略中间信息。 | 检索排序、上下文布局 |
| 预填充阶段 | Prefill | 一次性处理输入上下文并生成首 token 前的计算阶段。 | TTFT、长上下文成本 |
| 解码阶段 | Decode | 逐 token 生成后续内容的阶段。 | KV Cache、TPOT |
| 吞吐-延迟权衡 | Throughput-Latency Tradeoff | 大 batch 提吞吐但可能增加单请求等待。 | Serving 调参 |
| 尾延迟 | Tail Latency | P95/P99 等高分位延迟。 | 生产体验、SLO |
| P50/P95/P99 | Latency Percentiles | 延迟分布的中位数和高分位指标。 | 线上监控 |
| 最大并发 | Max Concurrency | 服务同时处理请求的能力。 | 显存、批处理、队列 |
| 队列时间 | Queue Time | 请求等待进入推理批次的时间。 | 动态批处理、限流 |
| 吞吐瓶颈 | Bottleneck | 限制整体速度的最短板。 | 计算、显存带宽、通信、I/O |
| 显存带宽瓶颈 | Memory Bandwidth Bound | 解码时常受权重/KV 读取速度限制。 | 量化、KV Cache |
| 计算瓶颈 | Compute Bound | 主要受矩阵计算能力限制。 | Prefill、大 batch |
| KV Cache 量化 | KV Cache Quantization | 降低缓存精度以节省显存。 | 长上下文 serving |
| KV Cache 逐出 | KV Cache Eviction | 在上下文或显存不足时丢弃部分缓存。 | StreamingLLM、注意力汇聚 |
| Prefix Cache | Prefix Cache | 复用相同前缀的 KV Cache。 | 系统提示/RAG 前缀降本 |
| 语义缓存 | Semantic Cache | 相似问题复用已有答案或中间结果。 | Embedding、成本优化 |
| 确定性 | Determinism | 相同输入和参数是否总生成相同输出。 | temperature=0 也可能受并行影响 |
| 种子采样 | Seeded Sampling | 用固定随机种子控制采样结果。 | 可复现生成 |
| 约束解码 | Constrained Decoding | 限制输出必须满足格式或语法。 | JSON Schema、Grammar |
| 语法解码 | Grammar Decoding | 按文法约束生成合法结构。 | GBNF、JSON、SQL |
| Beam Width | Beam Width | Beam Search 保留候选数量。 | 越大越慢 |
| Length Penalty | Length Penalty | 调节生成长度偏好。 | 翻译/摘要 |
| Best-of-N | Best-of-N | 生成多个候选后选择最好一个。 | Verifier、Reward Model |
| 重采样 | Resampling | 答案不合格时重新生成。 | 结构化输出、Guardrail |
| 模型路由 | Model Routing | 根据任务选择不同模型。 | 小模型优先、成本控制 |
| 模型级联 | Model Cascade | 先用便宜模型，失败或低置信再升级强模型。 | 成本/质量权衡 |
| 回退策略 | Fallback | 主模型或工具失败时切换备用方案。 | 可靠性、SLA |
| 并行采样 | Parallel Sampling | 同时生成多个候选加速搜索。 | Self-consistency、Best-of-N |
| 推理预算 | Inference Budget | 为一次回答分配的 token、时间、工具调用、候选数。 | 成本控制 |
| 推理强度 | Reasoning Effort | 控制模型在推理任务上使用的计算/思考预算。 | 推理模型 API 常见参数 |

## 提示工程

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| Prompt | Prompt | 给模型的输入指令、上下文和约束。 | System/User/Assistant |
| System Prompt | System Prompt | 最高优先级的行为设定与规则提示。 | 安全、角色、格式约束 |
| User Prompt | User Prompt | 用户当前请求。 | 与 system prompt 可能冲突 |
| Prompt Engineering | Prompt Engineering | 设计输入以稳定获得目标输出。 | Few-shot、CoT、模板 |
| Zero-shot | Zero-shot | 不给示例，直接让模型完成任务。 | 泛化能力 |
| One-shot | One-shot | 给一个示例引导模型。 | Few-shot 特例 |
| Few-shot | Few-shot | 给少量示例让模型模仿模式。 | ICL、示例选择 |
| 上下文学习 | In-Context Learning / ICL | 不更新参数，仅通过上下文示例临时学任务。 | Few-shot、Prompt |
| 思维链 | Chain-of-Thought / CoT | 引导模型分步推理。 | 数学、逻辑题；不一定应暴露给用户 |
| 自洽性 | Self-Consistency | 多次采样推理路径并投票选答案。 | 提升推理稳定性 |
| ReAct | Reason + Act | 让模型交替推理和调用工具。 | Agent、Tool Use |
| Tree of Thoughts | ToT | 同时探索多条推理分支。 | 复杂规划、搜索 |
| Plan-and-Solve | Plan-and-Solve | 先制定计划再执行。 | 减少遗漏 |
| Prompt Injection | Prompt Injection | 恶意输入试图覆盖系统指令或泄露信息。 | RAG/Agent 安全重点 |
| Jailbreak | Jailbreak | 绕过安全策略让模型输出违规内容。 | 对抗提示、安全评测 |
| 结构化输出 | Structured Output | 让模型按 JSON/XML/Schema 等格式输出。 | Function Calling、JSON Schema |
| JSON 模式 | JSON Mode | 限制模型输出合法 JSON。 | 不等于语义正确 |
| 工具调用 | Tool Calling / Function Calling | 模型按 schema 选择并调用外部函数。 | Agent、API、结构化参数 |
| 角色提示 | Role Prompt | 指定模型扮演的角色或专家身份。 | 可能提升风格但不等于真实能力 |
| 任务说明 | Task Instruction | 明确告诉模型要完成什么。 | 输入、输出、约束 |
| 输出约束 | Output Constraint | 指定格式、长度、字段、语气等要求。 | 结构化输出 |
| 负面约束 | Negative Constraint | 告诉模型不要做什么。 | 但过多可能冲突 |
| 示例选择 | Example Selection | 挑选 few-shot 示例以提高任务表现。 | 相似示例、覆盖边界 |
| 提示模板 | Prompt Template | 可复用的 prompt 结构。 | 变量、版本管理 |
| 提示版本管理 | Prompt Versioning | 记录 prompt 变更和效果。 | LLMOps、A/B |
| 提示评测 | Prompt Evaluation | 系统比较不同 prompt 的输出质量。 | Eval set、LLM judge |
| 元提示 | Meta Prompt | 用于生成、改写或优化提示的提示。 | Prompt optimizer |
| 自我批判 | Self-Critique | 让模型检查自身答案问题。 | Reflection、Verifier |
| 自我改进 | Self-Refine | 生成-反馈-修改的迭代提示策略。 | 复杂写作、代码 |
| 上下文排序 | Context Ordering | 安排证据、历史和指令的顺序。 | Lost in the Middle |
| 上下文裁剪 | Context Pruning | 删除低价值上下文保留关键信息。 | 长对话、Agent |
| 上下文摘要 | Context Summarization | 把历史压缩成摘要继续对话。 | 记忆压缩 |
| 指令层级 | Instruction Hierarchy | system/developer/user/tool 等指令优先级。 | 安全、冲突处理 |
| 指令冲突 | Instruction Conflict | 不同层级或来源的指令互相矛盾。 | 遵循高优先级指令 |
| 分隔符 | Delimiter | 用标记清晰隔离指令、数据和示例。 | 防注入、可读性 |
| 引用上下文 | Quoted Context | 把不可信文本明确标为引用资料。 | Prompt Injection 防护 |
| 思维链隐藏 | Hidden Reasoning | 系统内部推理不直接暴露给终端用户。 | 安全、简洁答案 |
| 答案草稿 | Draft Answer | 中间生成的候选答案。 | Refine、Verifier |

## RAG

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| RAG | Retrieval-Augmented Generation | 先检索外部知识，再把结果给模型生成答案。 | 降低幻觉、更新知识 |
| 检索 | Retrieval | 从文档库中找到与问题相关的内容。 | 稀疏/稠密/混合检索 |
| 生成 | Generation | 根据问题和检索上下文生成最终回答。 | 忠实性、引用 |
| 文档切分 | Chunking | 把长文档切成适合检索的小块。 | Chunk Size、Overlap |
| 块大小 | Chunk Size | 每个文档块包含的字符或 token 数。 | 太小丢上下文，太大噪声多 |
| 重叠窗口 | Chunk Overlap | 相邻文档块保留部分重叠内容。 | 防止边界信息丢失 |
| 向量 | Embedding Vector | 文本语义的数值表示。 | 向量数据库、相似度 |
| 嵌入模型 | Embedding Model | 把文本/图片等转成向量的模型。 | bge、text-embedding、e5 |
| 向量数据库 | Vector Database | 存储向量并支持相似度搜索的数据库。 | FAISS、Milvus、Pinecone、Qdrant |
| 相似度 | Similarity | 衡量查询和文档向量接近程度。 | Cosine、Dot Product、L2 |
| 余弦相似度 | Cosine Similarity | 用夹角衡量两个向量方向相似。 | Embedding 检索常见 |
| 近似最近邻 | ANN | 快速查找近似最相似向量。 | HNSW、IVF、PQ |
| HNSW | Hierarchical Navigable Small World | 图索引 ANN 方法，召回和速度较好。 | 向量库常用索引 |
| 稀疏检索 | Sparse Retrieval | 基于关键词/倒排索引的检索。 | BM25、TF-IDF |
| BM25 | BM25 | 经典关键词相关性排序算法。 | 精确词匹配强 |
| 稠密检索 | Dense Retrieval | 基于 embedding 语义相似度检索。 | 语义召回强 |
| 混合检索 | Hybrid Search | 同时使用关键词检索和向量检索。 | BM25 + Embedding |
| 重排序 | Reranking | 对初步召回结果重新精排。 | Cross-Encoder、Reranker |
| Cross-Encoder | Cross-Encoder | 将 query 和文档拼接输入模型进行相关性打分。 | 精度高但慢 |
| 召回率 | Recall | 真实相关文档中被检索出来的比例。 | 高召回避免漏答案；与 Precision 权衡 |
| 精确率 | Precision | 检索结果中真正相关的比例。 | 高精确减少噪声 |
| MRR | Mean Reciprocal Rank | 正确结果排名倒数的平均值。 | 排名质量指标 |
| nDCG | Normalized Discounted Cumulative Gain | 考虑相关性等级和排名位置的指标。 | 搜索排序评估 |
| Hit Rate | Hit Rate | Top-k 结果中是否命中相关文档。 | RAG 检索评测常用 |
| 上下文召回 | Context Recall | 答案所需证据是否被放入上下文。 | RAGAS 指标 |
| 忠实性 | Faithfulness / Groundedness | 回答是否被检索证据支持。 | 幻觉检测 |
| 引文 | Citation | 回答中标注信息来源。 | 可追溯、可信度 |
| 查询改写 | Query Rewriting | 把用户问题改写成更适合检索的查询。 | 多轮问答、HyDE |
| HyDE | Hypothetical Document Embeddings | 先生成假想答案/文档再用其向量检索。 | 改善语义召回 |
| Multi-query Retrieval | Multi-query Retrieval | 生成多个查询并合并检索结果。 | 提高召回 |
| Parent-Child Retrieval | Parent-Child Retrieval | 小块用于检索，大块用于给模型阅读。 | 兼顾精确和上下文 |
| Knowledge Graph RAG | GraphRAG | 使用知识图谱组织和检索知识。 | 实体关系、全局摘要 |
| RAGAS | RAGAS | RAG 系统评测框架和指标集合。 | Faithfulness、Answer Relevance |
| 索引 | Index | 为文档建立可快速检索的数据结构。 | 倒排索引、向量索引 |
| 倒排索引 | Inverted Index | 从词到包含该词文档的映射。 | BM25、搜索引擎 |
| 元数据 | Metadata | 文档的来源、时间、作者、权限、标签等结构化信息。 | 过滤、排序、权限 |
| 元数据过滤 | Metadata Filtering | 检索时按标签、时间、权限等过滤。 | 企业知识库 |
| 权限感知检索 | Permission-aware Retrieval | 只检索用户有权访问的文档。 | ACL、数据安全 |
| ACL | Access Control List | 访问控制列表。 | 权限过滤 |
| 文档解析 | Document Parsing | 从 PDF/网页/Office 中提取结构化文本。 | OCR、表格、标题层级 |
| 版面分析 | Layout Analysis | 识别文档标题、段落、表格、页眉页脚等结构。 | PDF RAG |
| 表格解析 | Table Extraction | 从文档中提取表格结构和内容。 | 财报/论文 RAG |
| 多模态 RAG | Multimodal RAG | 检索和生成同时利用文本、图片、音频、视频等。 | VLM、图像 embedding |
| 检索增强微调 | RAFT | 用检索上下文训练模型更好利用证据。 | RAG + SFT |
| Self-RAG | Self-RAG | 模型自我决定是否检索并评估检索内容。 | 自反思、检索控制 |
| Corrective RAG | CRAG | 检测检索质量，不足时改写或补充检索。 | RAG 鲁棒性 |
| Adaptive RAG | Adaptive RAG | 根据问题难度动态选择检索策略。 | 路由、成本控制 |
| Agentic RAG | Agentic RAG | 由 Agent 多步规划检索、阅读、验证。 | 复杂问题、多跳检索 |
| 多跳检索 | Multi-hop Retrieval | 需要跨多个文档/事实链回答的检索。 | HotpotQA、GraphRAG |
| 查询扩展 | Query Expansion | 添加同义词、实体、相关词提高召回。 | 搜索引擎、RAG |
| 查询分解 | Query Decomposition | 把复杂问题拆成多个子查询。 | 多跳问答 |
| 实体抽取 | Entity Extraction | 识别查询或文档中的实体。 | GraphRAG、过滤 |
| 实体链接 | Entity Linking | 把实体提及映射到知识库中的具体实体。 | 消歧、知识图谱 |
| 知识图谱 | Knowledge Graph / KG | 以实体和关系组织知识的图结构。 | GraphRAG、推理 |
| 向量漂移 | Embedding Drift | 嵌入模型或数据变化导致向量空间不一致。 | 重建索引、版本管理 |
| 索引刷新 | Index Refresh | 文档更新后重新解析、嵌入和写入索引。 | 增量更新 |
| 增量索引 | Incremental Indexing | 只处理新增或变化文档。 | 效率、同步 |
| 检索深度 | Top-k | 检索返回的候选数量。 | 召回率、噪声、成本 |
| 上下文精确率 | Context Precision | 放入上下文的片段中有多少是相关且排序靠前的。 | RAGAS 指标 |
| 答案相关性 | Answer Relevance | 回答是否直接回应问题。 | RAGAS、LLM Judge |
| 引用精确率 | Citation Precision | 引用是否真正支持对应陈述。 | 可信 RAG |
| 引用召回率 | Citation Recall | 需要引用的陈述中有多少给出了来源。 | 合规/研究场景 |
| 证据覆盖率 | Evidence Coverage | 答案所需证据被检索和引用的完整程度。 | 复杂问答 |
| 答案可归因性 | Attribution | 回答中的声明能否归因到具体来源。 | Grounded QA |
| 检索器 | Retriever | 负责从知识库取回候选文档的组件。 | BM25、Dense、Hybrid |
| 读取器 | Reader | 在检索结果中抽取或生成答案的组件。 | 传统 QA、RAG |
| 生成器 | Generator | 根据上下文生成最终答案的 LLM。 | Faithfulness |
| 索引管道 | Indexing Pipeline | 文档加载、清洗、切分、嵌入、入库流程。 | ETL、数据质量 |
| 查询管道 | Query Pipeline | 查询改写、检索、重排、生成、校验流程。 | RAG runtime |

## Agent

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| Agent | Agent | 能感知目标、规划、调用工具并迭代完成任务的 LLM 系统。 | Tool Use、Memory、Planning |
| 工具 | Tool | 模型可调用的外部函数、API、数据库或浏览器。 | Function Calling、权限 |
| 工具选择 | Tool Selection | 判断当前任务该调用哪个工具。 | Router、Planner |
| 规划 | Planning | 将目标分解为步骤或子任务。 | Plan-and-Execute、ToT |
| 执行 | Execution | 按计划调用工具、读取结果并推进任务。 | 观察-行动循环 |
| 观察 | Observation | 工具返回或环境反馈。 | ReAct 中的 Obs |
| 记忆 | Memory | Agent 保存和检索历史信息的机制。 | 短期/长期/情景/语义记忆 |
| 短期记忆 | Short-term Memory | 当前上下文窗口内的临时信息。 | Conversation History |
| 长期记忆 | Long-term Memory | 跨会话持久化的信息。 | 向量库、知识图谱 |
| 任务分解 | Task Decomposition | 把复杂任务拆成可执行小任务。 | Planner、子代理 |
| 多代理 | Multi-Agent | 多个 Agent 分工协作或辩论。 | Crew、Swarm、Debate |
| 反思 | Reflection | Agent 回看中间结果并修正策略。 | Self-Refine、Verifier |
| 自我修正 | Self-Correction | 模型发现并修复自身错误。 | Critic、Reflexion |
| Human-in-the-loop | HITL | 人类参与审批、标注、纠偏或关键决策。 | 安全、质量控制 |
| Guardrail | Guardrail | 对输入、工具调用或输出施加规则与安全边界。 | 内容安全、Schema 校验 |
| 沙箱 | Sandbox | 隔离执行代码或工具，限制副作用。 | 安全执行、权限控制 |
| 工具幻觉 | Tool Hallucination | 模型编造不存在的工具或参数。 | Schema、严格验证 |
| 权限控制 | Permission Control | 限制 Agent 可执行的操作范围。 | 最小权限、审批 |
| 行动空间 | Action Space | Agent 可采取的全部动作集合。 | 工具、浏览器、代码执行 |
| 状态 | State | Agent 当前任务、记忆、变量和环境信息。 | LangGraph、状态机 |
| 状态机 | State Machine | 用状态和转移约束 Agent 流程。 | 可靠性、可控性 |
| 工作流 Agent | Workflow Agent | 按预定义流程调用模型和工具。 | 稳定、可审计 |
| 自主 Agent | Autonomous Agent | 可自行规划和选择行动的 Agent。 | 风险更高，需权限控制 |
| Plan-and-Execute | Plan-and-Execute | 先生成计划，再逐步执行。 | 复杂任务 |
| Router | Router | 根据输入把任务路由给模型、工具或子流程。 | 模型路由、意图识别 |
| Supervisor | Supervisor | 协调多个子 Agent 的上级控制器。 | 多代理编排 |
| Critic | Critic | 评审计划或输出并指出问题的角色/模型。 | Reflection、Verifier |
| Verifier | Verifier | 验证答案、代码、工具结果是否满足要求。 | 测试、评测、Best-of-N |
| 工具 Schema | Tool Schema | 描述工具名称、参数类型和约束。 | JSON Schema、Function Calling |
| 工具结果校验 | Tool Result Validation | 检查工具返回是否可信、完整、符合预期。 | 防注入、防错用 |
| 幂等性 | Idempotency | 重复执行同一操作不会产生额外副作用。 | 外部 API、重试安全 |
| 副作用 | Side Effect | 工具调用对外部世界产生的改变。 | 写文件、发邮件、下单 |
| 审批门 | Approval Gate | 高风险操作前要求人工确认。 | HITL、权限 |
| 审计日志 | Audit Log | 记录 Agent 做过什么、为何做、结果如何。 | 合规、追责 |
| 可恢复性 | Recoverability | 失败后能继续、回滚或重试的能力。 | Checkpoint、事务 |
| 任务检查点 | Task Checkpoint | 保存任务进度和关键状态。 | 长任务、上下文压缩 |
| MCP | Model Context Protocol | 标准化模型应用连接工具、资源和提示的协议。 | Host、Client、Server |
| MCP Host | MCP Host | 发起和管理 MCP 连接的应用。 | Claude Desktop、IDE、Agent App |
| MCP Client | MCP Client | Host 内部与某个 MCP Server 通信的客户端。 | 一对一连接 |
| MCP Server | MCP Server | 暴露工具、资源、提示等能力的服务。 | 本地/远程、stdio/http |
| MCP Tool | MCP Tool | 可由模型调用的动作能力。 | 文件、数据库、浏览器、API |
| MCP Resource | MCP Resource | 可供模型读取的上下文数据。 | 文件、文档、记录 |
| MCP Prompt | MCP Prompt | 服务器提供的可复用提示模板。 | 工作流入口 |
| MCP Roots | MCP Roots | Host 告诉 Server 可访问的工作区根目录。 | 权限边界 |
| MCP Sampling | MCP Sampling | Server 请求 Host 代为调用模型生成内容。 | 人机审批、能力复用 |
| MCP Elicitation | MCP Elicitation | 工具执行中向用户请求补充信息的机制。 | 表单、确认、交互 |
| 沙箱环境 | Sandbox Environment | 限制代码、文件、网络和系统权限的执行环境。 | 安全 Agent |
| 浏览器 Agent | Browser Agent | 能操作网页的 Agent。 | Playwright、WebAgent、视觉 |
| 代码 Agent | Coding Agent | 能读写代码、运行测试、提交补丁的 Agent。 | Codex、Claude Code |
| 任务成功轨迹 | Successful Trajectory | 完整完成任务的行动序列，可用于训练或评测。 | Agent 数据 |
| 长期任务 | Long-horizon Task | 需要多步、多工具、长时间才能完成的任务。 | 规划、记忆、恢复 |
| 环境反馈 | Environment Feedback | 外部系统对动作的返回。 | Observation、Reward |

## 评测

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| 评测 | Evaluation / Eval | 用数据集、指标或人工判断模型/系统质量。 | 离线评测、在线评测 |
| Benchmark | Benchmark | 标准化评测数据集或榜单。 | MMLU、HumanEval、GSM8K |
| MMLU | Massive Multitask Language Understanding | 多学科知识问答评测。 | 通用知识能力 |
| GSM8K | GSM8K | 小学数学应用题评测。 | 数学推理 |
| HumanEval | HumanEval | 代码生成能力评测。 | pass@k |
| HELM | HELM | 综合模型评测框架。 | 多维度评估 |
| MT-Bench | MT-Bench | 多轮对话能力评测。 | LLM-as-judge |
| Arena | Chatbot Arena | 通过人类偏好对战排名模型。 | Elo、主观偏好 |
| BLEU | BLEU | 基于 n-gram 重合的生成文本指标。 | 翻译；不适合所有开放任务 |
| ROUGE | ROUGE | 摘要中常用的 n-gram/最长公共子序列指标。 | 摘要评测 |
| METEOR | METEOR | 考虑词形和同义的文本生成指标。 | 机器翻译 |
| BERTScore | BERTScore | 用上下文 embedding 衡量语义相似。 | 比 n-gram 更语义化 |
| Exact Match | EM | 预测答案与标准答案完全一致。 | QA 评测 |
| F1 | F1 Score | Precision 和 Recall 的调和平均。 | 分类/抽取/检索 |
| 准确率 | Accuracy | 预测正确样本占比。 | 类别均衡时直观 |
| 精确率 | Precision | 预测为正的样本中真正为正的比例。 | 少误报 |
| 召回率 | Recall | 真正为正的样本中被找出的比例。 | 少漏报 |
| AUC | Area Under Curve | 分类排序质量指标。 | ROC-AUC、PR-AUC |
| pass@k | pass@k | 代码题生成 k 个答案中至少一个通过的概率。 | HumanEval |
| LLM-as-a-Judge | LLM as Judge | 用强模型评判回答质量。 | 省人工但有偏差 |
| 人工评测 | Human Evaluation | 人类从正确性、帮助性、安全性等维度打分。 | 成本高但可靠 |
| A/B 测试 | A/B Test | 线上对比两个模型或策略的用户效果。 | 统计显著性 |
| 红队测试 | Red Teaming | 主动攻击模型找安全漏洞。 | Jailbreak、Prompt Injection |
| 鲁棒性 | Robustness | 面对扰动、噪声、分布变化仍稳定。 | 对抗样本、OOD |
| 校准 | Calibration | 模型置信度与真实正确率一致的程度。 | 可靠性、风险控制 |
| 幻觉率 | Hallucination Rate | 回答中无根据或错误内容的比例。 | RAG 忠实性 |
| 任务成功率 | Task Success Rate | Agent 或应用完成目标任务的比例。 | 端到端评测 |
| 离线评测 | Offline Evaluation | 在固定数据集上批量测试模型或系统。 | 回归测试、模型选择 |
| 在线评测 | Online Evaluation | 在真实流量中观察效果。 | A/B、灰度、用户反馈 |
| 回归评测 | Regression Eval | 确保新版本没有破坏旧能力。 | CI、Golden Set |
| 黄金集 | Golden Set | 高质量、人工确认的核心评测样本。 | 业务私有 eval |
| 冒烟测试 | Smoke Test | 快速检查系统基本可用。 | 部署前 |
| 单元评测 | Unit Eval | 测试单个 prompt、retriever、tool 或 parser。 | 定位问题 |
| 端到端评测 | End-to-End Eval | 从用户输入到最终输出整体评估。 | Agent/RAG 应用 |
| 成对比较 | Pairwise Comparison | 让评审在两个回答中选更好。 | 偏好数据、Arena |
| Likert 评分 | Likert Rating | 按 1-5/1-7 等等级评分。 | 人工评测 |
| Elo 分 | Elo Rating | 根据对战胜负估计相对强弱。 | Chatbot Arena |
| 置信区间 | Confidence Interval | 指标估计的不确定范围。 | 统计显著性 |
| 统计显著性 | Statistical Significance | 观察到的差异不太可能由随机波动造成。 | A/B 测试 |
| 混淆矩阵 | Confusion Matrix | 展示 TP/FP/FN/TN 的分类结果矩阵。 | Precision/Recall/F1 |
| TP | True Positive | 正样本被正确预测为正。 | 分类指标 |
| FP | False Positive | 负样本被错误预测为正。 | 误报 |
| FN | False Negative | 正样本被错误预测为负。 | 漏报 |
| TN | True Negative | 负样本被正确预测为负。 | 分类指标 |
| Macro-F1 | Macro F1 | 先对每类算 F1 再平均，重视小类。 | 类别不均衡 |
| Micro-F1 | Micro F1 | 汇总全局 TP/FP/FN 后算 F1。 | 大类影响更大 |
| Cohen Kappa | Cohen’s Kappa | 衡量标注者一致性并扣除随机一致。 | 人工标注质量 |
| IAA | Inter-Annotator Agreement | 标注者之间一致程度。 | 数据质量 |
| Judge Bias | Judge Bias | LLM 裁判偏向某种风格、长度或模型。 | LLM-as-judge 风险 |
| 位置偏差 | Position Bias | 裁判偏好第一个或第二个答案。 | 成对比较需打乱顺序 |
| 长度偏差 | Length Bias | 裁判偏好更长答案。 | Judge 校准 |
| 泄题评测 | Leaky Eval | 评测题被模型见过或可从上下文直接泄露。 | 数据污染 |
| 对抗评测 | Adversarial Eval | 用刻意构造的困难/攻击样本测试系统。 | 红队、鲁棒性 |
| 切片评测 | Slice Evaluation | 按场景、人群、语言、难度分组分析指标。 | 发现局部失败 |
| 校准误差 | ECE, Expected Calibration Error | 衡量置信度与准确率偏差。 | 可靠性 |
| Brier Score | Brier Score | 概率预测与真实标签的均方误差。 | 校准评估 |
| 毒性指标 | Toxicity Metric | 衡量有害、冒犯或仇恨输出。 | Safety Eval |
| 越狱成功率 | Jailbreak Success Rate | 攻击提示让模型违规的比例。 | 安全红队 |
| 工具调用成功率 | Tool Call Success Rate | 工具选择、参数、执行是否正确。 | Agent Eval |
| 计划质量 | Plan Quality | Agent 计划是否完整、可执行、顺序正确。 | 长期任务评测 |

## 幻觉与事实性

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| 幻觉 | Hallucination | 模型生成看似合理但错误或无依据的信息。 | RAG、引用、校验 |
| 事实性 | Factuality | 回答与事实一致的程度。 | 知识问答、引用 |
| 忠实性 | Faithfulness | 输出是否忠于给定上下文或证据。 | 摘要、RAG |
| 可验证性 | Verifiability | 输出是否能被来源或工具验证。 | 引文、检索、数据库 |
| 不确定性表达 | Uncertainty | 模型承认不知道或给出置信范围。 | 防幻觉、校准 |
| Grounding | Grounding | 将生成内容绑定到外部证据或真实环境。 | RAG、工具调用 |
| 内在幻觉 | Intrinsic Hallucination | 输出与给定上下文矛盾。 | 摘要、RAG |
| 外在幻觉 | Extrinsic Hallucination | 输出包含上下文没有支持的信息。 | 开放生成 |
| 编造引用 | Fabricated Citation | 生成不存在或不支持陈述的来源。 | 学术/法律高风险 |
| 事实核查 | Fact Checking | 用来源、工具或数据库验证声明。 | Grounding |
| 可追溯性 | Traceability | 能追踪答案来自哪些数据和步骤。 | RAG、审计日志 |
| 置信度 | Confidence | 模型或系统对答案正确性的估计。 | 校准、拒答 |
| 不回答阈值 | Abstention Threshold | 低置信或证据不足时选择不回答。 | 安全问答、医疗法律 |
| 证据冲突 | Evidence Conflict | 检索到的来源互相矛盾。 | 需要冲突处理和来源优先级 |
| 来源可信度 | Source Credibility | 不同信息源的可靠程度。 | RAG 排序、引用 |

## 部署

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| 模型服务 | Model Serving | 将模型部署成可被应用调用的服务。 | vLLM、TGI、TensorRT-LLM |
| vLLM | vLLM | 高吞吐 LLM 推理服务框架。 | PagedAttention、连续批处理 |
| TGI | Text Generation Inference | Hugging Face 的文本生成推理服务。 | Serving、批处理 |
| TensorRT-LLM | TensorRT-LLM | NVIDIA 的 LLM 推理优化框架。 | GPU 加速、量化 |
| ONNX | ONNX | 跨框架模型交换格式。 | 推理优化 |
| GGUF | GGUF | llama.cpp 常用模型文件格式。 | 本地量化推理 |
| llama.cpp | llama.cpp | C/C++ 本地 LLM 推理项目。 | CPU/GPU、本地部署 |
| Ollama | Ollama | 本地运行和管理 LLM 的工具。 | Modelfile、GGUF |
| OpenAI API 兼容 | OpenAI-compatible API | 复用 OpenAI 风格接口接入不同模型服务。 | /v1/chat/completions |
| QPS | Queries Per Second | 每秒处理请求数。 | 吞吐指标 |
| 限流 | Rate Limiting | 限制请求频率以保护服务。 | TPM、RPM、配额 |
| TPM | Tokens Per Minute | 每分钟 token 限额。 | API 配额 |
| RPM | Requests Per Minute | 每分钟请求数限额。 | API 配额 |
| 缓存 | Caching | 复用请求、检索或模型输出结果降低成本。 | Prompt Cache、Embedding Cache |
| Prompt Cache | Prompt Cache | 缓存重复前缀上下文的计算结果。 | 长上下文降本 |
| 灰度发布 | Canary Release | 小流量先上线新模型观察效果。 | 回滚、A/B |
| 回滚 | Rollback | 出现问题时恢复到旧模型或旧策略。 | 发布安全 |
| 监控 | Monitoring | 跟踪延迟、错误、成本、质量、安全事件。 | LLMOps |
| 日志 | Logging | 记录请求、响应、工具调用和指标。 | 隐私脱敏、可观测性 |
| 追踪 | Tracing | 记录一次请求经过的链路和中间步骤。 | LangSmith、OpenTelemetry |
| 成本 | Cost | 训练、推理、存储、标注、运维等花费。 | tokens、GPU、缓存 |
| LLMOps | LLMOps | LLM 应用的开发、评测、部署、监控与迭代体系。 | MLOps + Prompt/RAG/Agent |
| SLA | Service Level Agreement | 服务可用性、延迟等对外承诺。 | 生产运维 |
| SLO | Service Level Objective | 内部设定的服务目标。 | P95 延迟、错误率 |
| 错误预算 | Error Budget | 允许服务不达标的预算。 | SRE、发布节奏 |
| 可用性 | Availability | 服务可访问和正常工作的比例。 | 99.9%、多活 |
| 可靠性 | Reliability | 服务持续正确工作的能力。 | 重试、熔断、降级 |
| 熔断 | Circuit Breaker | 故障过多时暂时停止调用下游。 | 保护系统 |
| 降级 | Degradation | 强模型/复杂流程失败时使用简化方案。 | Fallback、缓存 |
| 重试 | Retry | 失败后再次执行请求。 | 注意幂等性 |
| 超时 | Timeout | 请求超过时间限制则中断。 | 工具调用、API |
| 负载均衡 | Load Balancing | 把请求分配到多个实例。 | 高可用、扩展 |
| 自动扩缩容 | Autoscaling | 根据负载动态增减实例。 | Kubernetes、GPU 池 |
| 冷启动 | Cold Start | 新实例启动或首次加载模型带来的延迟。 | Serverless、GPU 加载 |
| 热加载 | Hot Reload | 不中断服务地加载新模型或配置。 | 模型切换 |
| 模型注册表 | Model Registry | 管理模型版本、元数据和部署状态。 | MLflow、治理 |
| Prompt 注册表 | Prompt Registry | 管理 prompt 版本和实验结果。 | LLMOps |
| 特征/Embedding 存储 | Embedding Store | 保存向量和元数据的系统。 | RAG、语义缓存 |
| 影子流量 | Shadow Traffic | 新系统接收复制流量但不影响用户。 | 上线验证 |
| 金丝雀发布 | Canary Release | 小比例用户先用新版本。 | 灰度发布 |
| 蓝绿部署 | Blue-Green Deployment | 两套环境切换发布。 | 快速回滚 |
| 成本归因 | Cost Attribution | 把 token/GPU/API 成本分摊到用户、功能或团队。 | FinOps |
| Token 计量 | Token Metering | 统计输入/输出/缓存 token 用量。 | 计费、优化 |
| Prompt 注入监控 | Prompt Injection Monitoring | 检测 RAG 或用户输入中的注入攻击。 | 安全运营 |
| 质量漂移 | Quality Drift | 线上质量随数据、用户或模型变化下降。 | 监控、回归评测 |
| 数据漂移 | Data Drift | 线上输入分布随时间变化。 | 重新评测/训练 |
| 模型漂移 | Model Drift | 模型行为或效果随版本/环境变化。 | 监控、版本锁定 |
| 观测性 | Observability | 通过日志、指标、追踪理解系统状态。 | LLMOps |
| OpenTelemetry | OpenTelemetry | 通用可观测性标准。 | Tracing、Metrics、Logs |
| 评测即 CI | Evals in CI | 在持续集成中自动运行 LLM 回归评测。 | 防 prompt/RAG 退化 |
| 人工反馈闭环 | Feedback Loop | 收集用户反馈用于修复数据、prompt 或模型。 | 数据飞轮 |

## 优化

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| 量化 | Quantization | 用低比特表示权重/激活以减少显存和加速。 | INT8、INT4、GPTQ、AWQ |
| INT8 | INT8 | 8 位整数量化。 | 效果损失较小 |
| INT4 | INT4 | 4 位整数量化。 | 更省显存但更易损失效果 |
| NF4 | NormalFloat4 | QLoRA 常用的 4-bit 数据类型。 | bitsandbytes |
| GPTQ | GPTQ | 一种训练后权重量化方法。 | 本地推理常见 |
| AWQ | Activation-aware Weight Quantization | 考虑激活分布的权重量化方法。 | 部署常见 |
| SmoothQuant | SmoothQuant | 平滑激活异常值以便量化。 | INT8 推理 |
| 剪枝 | Pruning | 删除不重要权重、通道或注意力头。 | 压缩模型 |
| 蒸馏 | Knowledge Distillation | 用大模型指导小模型学习。 | Teacher-Student、合成数据 |
| 稀疏化 | Sparsification | 让权重或激活中大量元素为零以省计算。 | 结构化/非结构化稀疏 |
| MoE | Mixture of Experts | 每个 token 只激活部分专家网络，提高参数容量。 | Router、专家负载均衡 |
| 专家 | Expert | MoE 中的子网络模块。 | 稀疏激活 |
| 路由器 | Router | 决定 token 送到哪些专家。 | 负载均衡、路由崩塌 |
| 负载均衡损失 | Load Balancing Loss | 防止 MoE 只使用少数专家。 | Expert Utilization |
| 知识编辑 | Knowledge Editing | 修改模型中特定事实知识而非整体重训。 | ROME、MEMIT；风险难控 |
| 模型合并 | Model Merging | 合并多个微调模型权重或增量。 | LoRA Merge、TIES、DARE |
| 权重平均 | Weight Averaging | 对多个 checkpoint 权重求平均。 | SWA、模型汤 |
| 训练后量化 | Post-Training Quantization / PTQ | 训练完成后直接量化权重或激活。 | GPTQ、AWQ |
| 量化感知训练 | QAT | 训练中模拟量化误差以提升低比特效果。 | 部署优化 |
| 权重量化 | Weight Quantization | 降低模型权重精度。 | INT8/INT4 |
| 激活量化 | Activation Quantization | 降低中间激活精度。 | 推理加速难度更高 |
| 动态量化 | Dynamic Quantization | 推理时动态计算量化尺度。 | CPU/部署 |
| 静态量化 | Static Quantization | 提前校准量化参数。 | 需要校准集 |
| 校准集 | Calibration Set | 用于量化或校准的小样本集合。 | PTQ、AWQ |
| 结构化剪枝 | Structured Pruning | 删除整头、整通道、整层等规则结构。 | 硬件友好 |
| 非结构化剪枝 | Unstructured Pruning | 删除单个权重。 | 稀疏硬件支持要求高 |
| 层剪枝 | Layer Dropping | 删除部分 Transformer 层。 | 加速小模型 |
| 早退模型 | Early-exit Model | 根据置信度在中间层输出。 | 动态计算 |
| 知识蒸馏温度 | Distillation Temperature | 软化 teacher 输出分布的温度。 | Dark Knowledge |
| Teacher Model | Teacher Model | 蒸馏中提供监督的大模型。 | Student Model |
| Student Model | Student Model | 学习 teacher 行为的小模型。 | 压缩部署 |
| 模型汤 | Model Soup | 平均多个微调模型权重。 | 权重空间兼容时有效 |
| TIES Merging | TIES Merging | 处理符号冲突的模型合并方法。 | 多任务合并 |
| DARE | DARE | 随机丢弃部分权重增量再合并的模型合并方法。 | LoRA/模型合并 |

## 安全

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| AI 安全 | AI Safety | 降低模型造成伤害、误导或失控风险。 | 对齐、红队、Guardrail |
| 内容安全 | Content Safety | 检测和处理暴力、色情、仇恨、自残、违法等内容。 | Moderation |
| 隐私 | Privacy | 避免泄露个人信息、商业秘密和敏感数据。 | PII、脱敏、日志治理 |
| PII | Personally Identifiable Information | 可识别个人身份的信息。 | 脱敏、合规 |
| 脱敏 | Redaction / Masking | 隐藏或替换敏感信息。 | 日志、训练数据 |
| 数据泄露 | Data Leakage | 敏感或评测信息进入不应出现的位置。 | 训练、日志、Prompt |
| 模型泄露 | Model Extraction | 通过查询窃取模型能力或近似模型。 | API 安全 |
| 训练数据提取 | Training Data Extraction | 诱导模型吐出训练中记住的原始数据。 | 隐私风险 |
| 成员推断 | Membership Inference | 判断某样本是否在训练集中。 | 隐私攻击 |
| 对抗样本 | Adversarial Example | 经过设计的输入使模型出错。 | 鲁棒性 |
| 后门攻击 | Backdoor Attack | 训练中植入触发器，使模型遇到特定输入异常行为。 | 数据投毒 |
| 数据投毒 | Data Poisoning | 恶意污染训练或检索数据影响模型行为。 | RAG 知识库安全 |
| 供应链安全 | Supply Chain Security | 模型、数据、依赖、镜像来源可信。 | 开源模型风险 |
| 越权工具调用 | Unauthorized Tool Use | Agent 调用超出权限的工具或参数。 | 沙箱、审批、审计 |
| Prompt 泄露 | Prompt Leakage | 模型泄露 system prompt、密钥或内部策略。 | Prompt Injection |
| Moderation | Moderation | 对输入/输出做安全分类和拦截。 | 安全 API、策略 |
| 安全策略 | Safety Policy | 定义允许、拒绝、转向回答的规则。 | 内容安全、合规 |
| 策略分类器 | Policy Classifier | 判断输入/输出属于哪类安全策略。 | Moderation |
| 输入护栏 | Input Guardrail | 在模型前检查用户输入风险。 | 注入、敏感信息 |
| 输出护栏 | Output Guardrail | 在返回前检查模型输出风险。 | 安全、格式、事实性 |
| 工具护栏 | Tool Guardrail | 限制工具选择、参数和执行条件。 | Agent 安全 |
| 间接提示注入 | Indirect Prompt Injection | 网页/文档/邮件中的恶意文本通过 RAG 或工具进入上下文。 | Agent/RAG 高风险 |
| 直接提示注入 | Direct Prompt Injection | 用户直接要求模型忽略系统规则。 | Jailbreak |
| 数据外泄 | Data Exfiltration | 攻击者诱导模型或工具泄露敏感数据。 | Prompt Injection、权限 |
| 越狱基准 | Jailbreak Benchmark | 评估模型抵抗越狱攻击的数据集。 | 安全评测 |
| 红队样本库 | Red-team Dataset | 收集攻击提示和危险场景的测试集。 | 回归安全评测 |
| 最小权限 | Least Privilege | 只授予完成任务所需的最少权限。 | Agent 工具安全 |
| 权限提升 | Privilege Escalation | 攻击者获取超出授权范围的能力。 | 工具链安全 |
| 秘密管理 | Secret Management | 安全保存和使用 API Key、Token、证书。 | 不要放进 prompt/log |
| 审计 | Audit | 检查数据、模型、工具调用和输出是否合规。 | 企业治理 |
| 合规 | Compliance | 满足法律、行业和组织要求。 | GDPR、HIPAA、版权 |
| 版权风险 | Copyright Risk | 训练或输出涉及受版权保护内容的风险。 | 数据许可、相似输出 |
| 偏见 | Bias | 模型对人群、语言或观点存在系统性不公平。 | 公平性评测 |
| 公平性 | Fairness | 不同群体获得一致且无歧视的模型表现。 | Bias Mitigation |
| 双重用途 | Dual Use | 技术可被用于正当或有害目的。 | 生物、网络安全 |
| 滥用监控 | Abuse Monitoring | 检测垃圾生成、诈骗、自动攻击等滥用。 | 风控、限流 |

## 多模态

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| 视觉语言模型 | VLM | 同时理解图像和文本的模型。 | CLIP、LLaVA、GPT-4V 类 |
| 图像编码器 | Vision Encoder | 将图像转为向量或视觉 token。 | ViT、CLIP |
| ViT | Vision Transformer | 用 Transformer 处理图像 patch 的架构。 | 图像编码器 |
| CLIP | CLIP | 对齐图像和文本 embedding 的模型。 | 零样本图像分类、检索 |
| OCR | Optical Character Recognition | 从图像中识别文字。 | 文档理解、多模态 QA |
| 图文对齐 | Image-Text Alignment | 让图像和文本表示处于同一语义空间。 | 对比学习 |
| 视觉指令微调 | Visual Instruction Tuning | 用图文指令数据训练模型按图回答。 | LLaVA 类流程 |
| 音频语言模型 | Audio-Language Model | 处理语音、音频和文本的模型。 | ASR、TTS、语音对话 |
| ASR | Automatic Speech Recognition | 语音转文字。 | Whisper |
| TTS | Text-to-Speech | 文字转语音。 | 语音助手 |
| 文生图 | Text-to-Image | 根据文本生成图像。 | Diffusion、Prompt |
| 扩散模型 | Diffusion Model | 通过逐步去噪生成数据的模型。 | Stable Diffusion |
| 文生视频 | Text-to-Video | 根据文本生成视频。 | 时序一致性 |
| 模态 | Modality | 信息类型，如文本、图像、音频、视频、传感器。 | 多模态模型 |
| Patch | Patch | ViT 将图像切成的小块。 | 视觉 token |
| 视觉 Token | Visual Token | 图像经过编码后的 token 表示。 | VLM 上下文 |
| 投影层 | Projection Layer | 把视觉/音频表示映射到语言模型维度。 | 多模态连接器 |
| 连接器 | Connector | 连接模态编码器和 LLM 的模块。 | MLP、Q-Former、Projector |
| Q-Former | Q-Former | 用可学习 query 从视觉特征中提取信息。 | BLIP-2 |
| 图像问答 | VQA | 根据图片回答问题。 | 视觉理解 |
| 文档理解 | Document Understanding | 理解扫描件、PDF、表格、版面和文字。 | OCR、LayoutLM、VLM |
| 图像描述 | Image Captioning | 为图像生成自然语言描述。 | VLM |
| 视觉定位 | Visual Grounding | 把文本指代定位到图像区域。 | 框选、指代表达理解 |
| 目标检测 | Object Detection | 识别图像中物体类别和位置。 | YOLO、DETR |
| 图像分割 | Segmentation | 将图像按物体或区域划分。 | SAM、Mask |
| 对比图文预训练 | Contrastive Image-Text Pretraining | 用图文对比学习对齐视觉和文本。 | CLIP |
| 视频理解 | Video Understanding | 理解视频中的动作、事件和时序。 | 视频 token、长上下文 |
| 语音对话 | Speech-to-Speech | 从语音输入到语音输出的端到端交互。 | 低延迟、多模态 |
| 语音情感识别 | Speech Emotion Recognition | 从语音中判断情绪。 | 客服、交互 |
| 音频事件检测 | Audio Event Detection | 识别环境声或事件。 | 多模态感知 |

## 应用

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| 文本生成 | Text Generation | 生成文章、邮件、报告、脚本等文本。 | Prompt、风格控制 |
| 摘要 | Summarization | 压缩长文本为短摘要。 | 抽取式/生成式、忠实性 |
| 翻译 | Translation | 将文本从一种语言转换到另一种语言。 | BLEU、术语一致性 |
| 信息抽取 | Information Extraction | 从文本中抽取实体、关系、事件或字段。 | NER、JSON 输出 |
| 分类 | Classification | 将文本分到预定义类别。 | 情感分类、意图识别 |
| 问答 | Question Answering / QA | 根据知识或上下文回答问题。 | 开卷/闭卷 QA、RAG |
| 代码生成 | Code Generation | 生成函数、脚本、测试、补丁。 | HumanEval、代码审查 |
| 代码补全 | Code Completion | 根据上下文补全代码片段。 | IDE Copilot |
| 代码解释 | Code Explanation | 解释代码逻辑、复杂度和风险。 | 程序理解 |
| 数据分析 | Data Analysis | 辅助清洗、查询、统计和可视化数据。 | SQL、Python、工具调用 |
| SQL 生成 | Text-to-SQL | 把自然语言问题转成 SQL。 | Schema Linking、执行校验 |
| 智能客服 | Customer Support Bot | 自动回答用户咨询或辅助人工客服。 | RAG、工单、合规 |
| 知识库问答 | KBQA | 基于企业文档或知识库回答问题。 | RAG、权限过滤 |
| Copilot | Copilot | 人机协作式助手，帮助完成专业任务。 | IDE、办公、数据分析 |
| 工作流自动化 | Workflow Automation | 用 LLM 串联工具处理业务流程。 | Agent、审批、日志 |
| 情感分析 | Sentiment Analysis | 判断文本情绪倾向。 | 分类任务 |
| 意图识别 | Intent Detection | 判断用户想做什么。 | 客服、路由 |
| 命名实体识别 | NER | 识别人名、地点、组织、日期等实体。 | 信息抽取 |
| 关系抽取 | Relation Extraction | 抽取实体之间的关系。 | 知识图谱 |
| 事件抽取 | Event Extraction | 抽取事件类型、参与者、时间地点等。 | 情报、金融 |
| 合同审查 | Contract Review | 辅助识别合同条款、风险和差异。 | 法律 RAG、合规 |
| 医疗问答 | Medical QA | 回答医疗相关问题。 | 高风险，需证据和免责声明 |
| 金融研报 | Financial Research | 总结财报、公告、市场信息。 | RAG、时效性、合规 |
| 教育辅导 | Tutoring | 个性化讲解和练习反馈。 | 分步提示、评测 |
| 科研助手 | Research Assistant | 检索、总结、对比论文和生成综述。 | 引用、事实核查 |
| 会议纪要 | Meeting Minutes | 从会议录音/文本提炼决策和待办。 | ASR、摘要 |
| 邮件写作 | Email Drafting | 生成、改写、总结邮件。 | 风格、隐私 |
| 客服质检 | QA Audit | 检查客服对话是否合规和解决问题。 | 分类、评分 |
| 智能搜索 | AI Search | 用 LLM 改善搜索理解、排序和答案生成。 | RAG、Hybrid Search |
| 推荐解释 | Recommendation Explanation | 解释推荐系统为何推荐某项内容。 | 可解释性、生成 |
| 游戏 NPC | Game NPC | 用 LLM 驱动角色对话和行为。 | 记忆、角色一致性 |

## 框架生态

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| PyTorch | PyTorch | 主流深度学习框架。 | 训练、微调、部署 |
| Hugging Face Transformers | Transformers | 常用模型、Tokenizer、训练和推理库。 | AutoModel、Trainer |
| Datasets | Hugging Face Datasets | 数据集加载、处理和共享库。 | map、streaming |
| Accelerate | Accelerate | 简化多设备训练和推理配置。 | HF 生态 |
| DeepSpeed | DeepSpeed | 大模型训练优化库。 | ZeRO、并行 |
| Megatron-LM | Megatron-LM | NVIDIA 大模型训练框架。 | TP、PP |
| PEFT | PEFT Library | Hugging Face 参数高效微调库。 | LoRA、Adapter |
| TRL | Transformers Reinforcement Learning | HF 后训练/RLHF/DPO 等训练库。 | SFTTrainer、DPOTrainer |
| LangChain | LangChain | LLM 应用编排框架。 | Chain、Agent、Retriever |
| LlamaIndex | LlamaIndex | 面向数据/RAG 的 LLM 应用框架。 | Index、Retriever、Query Engine |
| Haystack | Haystack | 搜索、问答、RAG 管道框架。 | Retriever、Reader |
| DSPy | DSPy | 用可优化模块代替手写 prompt 的框架。 | Prompt 优化、编译 |
| LangGraph | LangGraph | 构建有状态 Agent 工作流图。 | 节点、边、状态 |
| JAX | JAX | Google 生态的高性能数值计算/深度学习框架。 | TPU、Flax |
| TensorFlow | TensorFlow | 经典深度学习框架。 | Serving、Keras |
| MLX | MLX | Apple Silicon 上的机器学习框架。 | 本地推理/训练 |
| CUDA | CUDA | NVIDIA GPU 编程平台。 | 深度学习加速 |
| cuDNN | cuDNN | NVIDIA 深度学习算子库。 | 卷积/矩阵优化 |
| Triton | Triton Language | 编写高性能 GPU kernel 的语言。 | FlashAttention、推理优化 |
| NCCL | NCCL | NVIDIA 多 GPU 通信库。 | All-Reduce、分布式训练 |
| Ray | Ray | 分布式 Python 执行和服务框架。 | 训练、Serving、Agent |
| Kubernetes | Kubernetes | 容器编排平台。 | LLM 服务部署 |
| Docker | Docker | 容器化应用和模型服务。 | 环境一致性 |
| MLflow | MLflow | 实验、模型注册和部署管理平台。 | MLOps |
| Weights & Biases | W&B | 实验追踪和模型监控工具。 | 训练日志、可视化 |
| LangSmith | LangSmith | LangChain 生态的 tracing/eval/monitor 平台。 | Agent/RAG 调试 |
| Phoenix | Arize Phoenix | LLM/RAG 可观测性与评测工具。 | Tracing、Eval |
| OpenAI Evals | OpenAI Evals | 用于构建和运行模型评测的框架。 | 回归评测 |
| lm-evaluation-harness | lm-eval-harness | 开源 LLM benchmark 评测框架。 | MMLU、GSM8K |
| EleutherAI | EleutherAI | 开源 LLM 研究社区。 | Pythia、lm-eval |
| OpenRLHF | OpenRLHF | 开源 RLHF/偏好训练框架。 | PPO、DPO、RLVR |
| Unsloth | Unsloth | 加速和节省显存的微调工具。 | LoRA/QLoRA |
| Axolotl | Axolotl | 常用开源 LLM 微调配置框架。 | SFT、LoRA、DPO |
| LLaMA-Factory | LLaMA-Factory | 中文社区常用 LLM 微调平台。 | SFT、LoRA、DPO |
| AutoGPTQ | AutoGPTQ | GPTQ 量化工具。 | 本地部署 |
| llama.cpp server | llama.cpp server | llama.cpp 的本地 OpenAI 兼容服务。 | GGUF、本地 API |

## 常见模型

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| GPT | GPT | OpenAI 的生成式预训练 Transformer 系列。 | ChatGPT、API |
| Llama | Llama | Meta 开源权重 LLM 系列。 | Llama 2/3/4、生态丰富 |
| Qwen | Qwen | 阿里通义千问系列模型。 | 中文、代码、多模态 |
| Claude | Claude | Anthropic 的对话模型系列。 | 长上下文、安全对齐 |
| Gemini | Gemini | Google 的多模态模型系列。 | Google 生态 |
| Mistral | Mistral | Mistral AI 模型系列。 | Mixtral、稀疏 MoE |
| DeepSeek | DeepSeek | DeepSeek 系列模型。 | 代码、推理、MoE |
| BERT | BERT | Encoder-only 预训练语言模型。 | 理解任务、MLM |
| T5 | Text-to-Text Transfer Transformer | 把所有任务统一成文本到文本。 | Encoder-Decoder |
| BART | BART | 去噪自编码 Seq2Seq 模型。 | 摘要、生成 |
| Mixtral | Mixtral | Mistral 的 MoE 模型系列。 | 稀疏专家 |
| Gemma | Gemma | Google 开放权重模型系列。 | 轻量、本地 |
| Phi | Phi | Microsoft 小模型系列。 | SLM、端侧 |
| Yi | Yi | 01.AI 开放权重模型系列。 | 中文/英文 |
| ChatGLM | ChatGLM / GLM | 智谱 GLM 系列模型。 | 中文、对话 |
| Baichuan | Baichuan | 百川智能模型系列。 | 中文开源生态 |
| InternLM | InternLM | 书生·浦语模型系列。 | 中文、工具、Agent |
| Command R | Command R | Cohere 面向 RAG 和工具使用的模型系列。 | 企业 RAG |
| Embedding 模型 | Embedding Models | 专门生成向量表示的模型。 | bge、e5、text-embedding |
| Reranker 模型 | Reranker Models | 专门对 query-doc 相关性重排的模型。 | bge-reranker、cross-encoder |
| 代码模型 | Code LLM | 专门强化代码理解和生成的模型。 | CodeLlama、DeepSeek-Coder、StarCoder |
| 数学模型 | Math LLM | 针对数学推理优化的模型。 | GSM8K、MATH |
| 推理模型 | Reasoning Model | 针对复杂推理和验证任务优化的模型。 | o 系列、R1 类、test-time compute |

## 研究热点

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| 推理模型 | Reasoning Model | 针对复杂数学、代码、规划推理强化的模型。 | CoT、搜索、RL |
| Test-time Compute | Test-time Compute | 推理阶段用更多计算换更好答案。 | 多采样、验证器、搜索 |
| 验证器 | Verifier | 判断候选答案或推理过程是否正确的模型。 | 数学/代码推理 |
| 自训练 | Self-Training | 模型生成伪标签再训练自己。 | 半监督、合成数据 |
| Self-Instruct | Self-Instruct | 模型自动生成指令数据用于指令微调。 | Alpaca 类数据构造 |
| Constitutional Data | Constitutional Data | 根据原则生成/筛选的对齐数据。 | CAI、安全 |
| 数据中心 AI | Data-centric AI | 更重视数据质量、覆盖和评测闭环。 | 小模型也可提升明显 |
| 小模型 | Small Language Model / SLM | 参数较少、适合本地或低成本场景的语言模型。 | 蒸馏、端侧部署 |
| 端侧模型 | On-device Model | 在手机、PC、边缘设备本地运行的模型。 | 隐私、低延迟、量化 |
| 个性化模型 | Personalized Model | 根据用户偏好或私有数据适配的模型。 | 隐私、记忆、微调 |
| 联邦学习 | Federated Learning | 数据不离本地，多方协同训练模型。 | 隐私保护 |
| 可解释性 | Interpretability | 理解模型内部表示和决策原因。 | Mechanistic Interpretability |
| 机械可解释性 | Mechanistic Interpretability | 研究神经网络内部电路和特征。 | Feature、Circuit、SAE |
| 稀疏自编码器 | Sparse Autoencoder / SAE | 用稀疏特征解释模型激活。 | 机制解释热点 |
| 神经符号结合 | Neuro-symbolic AI | 结合神经网络和符号规则/推理。 | 工具、证明、规划 |
| 程序辅助推理 | Program-aided Reasoning | 让模型写代码或调用程序完成推理。 | PAL、代码解释器 |
| 搜索增强推理 | Search-augmented Reasoning | 推理时搜索多个候选路径。 | Tree/Graph of Thoughts |
| 蒙特卡洛树搜索 | MCTS | 用树搜索探索决策空间。 | 推理、游戏、规划 |
| 自博弈 | Self-play | 模型与自己或其他模型对抗提升能力。 | 博弈、辩论、RL |
| 模型辩论 | Debate | 多个模型互相辩论以发现错误。 | 评测、对齐 |
| 合成偏好 | Synthetic Preference | 用模型或规则生成偏好标签。 | RLAIF、低成本对齐 |
| 可验证任务 | Verifiable Task | 答案能自动判定对错的任务。 | 数学、代码、RLVR |
| 长程 Agent 评测 | Long-horizon Agent Eval | 评估 Agent 长时间多步任务能力。 | WebAgent、MCP Sandbox |
| 记忆增强模型 | Memory-augmented Model | 模型可读写外部记忆或内部记忆机制。 | RAG、Agent Memory |
| 连续学习 | Continual Learning | 模型持续学习新知识而不遗忘旧知识。 | 灾难性遗忘 |
| 在线学习 | Online Learning | 模型随新数据实时或持续更新。 | 风险、数据治理 |
| 模型编辑可靠性 | Reliable Model Editing | 定向改知识且不破坏其他能力。 | ROME/MEMIT 局限 |
| 合成数据质量 | Synthetic Data Quality | 如何筛选、验证和去偏合成数据。 | Self-Instruct、蒸馏 |
| Agent 安全 | Agent Safety | 研究工具使用、自主规划和长期任务的安全边界。 | 权限、沙箱、审计 |
| AI 代理协议 | Agent Protocols | 标准化 Agent 与工具/数据/其他 Agent 的交互。 | MCP、A2A 等 |

## 易混概念

| 概念 | 英文/缩写 | 一句话速记 | 常见关联 / 易混点 |
|---|---|---|---|
| 微调 vs RAG | Fine-tuning vs RAG | 微调改变模型行为/风格；RAG 给模型外部知识。 | 新知识优先 RAG，固定风格/格式可微调 |
| SFT vs RLHF | SFT vs RLHF | SFT 学标准答案；RLHF 学人类偏好排序。 | SFT 通常先于 RLHF/DPO |
| LoRA vs 全参微调 | LoRA vs Full FT | LoRA 只训练低秩增量，省资源；全参更新全部权重。 | 成本、效果、遗忘风险 |
| 召回率 vs 精确率 | Recall vs Precision | 召回率看漏没漏；精确率看准不准。 | RAG 常先高召回再重排序提精度 |
| Embedding vs Reranker | Embedding vs Reranker | Embedding 负责快召回；Reranker 负责慢精排。 | 双阶段检索 |
| Prompt vs System Prompt | Prompt vs System Prompt | Prompt 泛指输入；System Prompt 是高优先级系统规则。 | 安全和风格控制 |
| Token vs Word | Token vs Word | Token 不等于单词，中文可按字/词片段，英文可能拆子词。 | 计费和上下文按 token |
| 上下文长度 vs 记忆 | Context vs Memory | 上下文是本次输入可见内容；记忆是跨会话保存再检索。 | 长上下文不等于永久记忆 |
| 幻觉 vs 过时知识 | Hallucination vs Stale Knowledge | 幻觉是无根据编造；过时知识是训练截止导致信息旧。 | RAG/搜索可缓解 |
| Benchmark 分数 vs 真实可用 | Benchmark vs Production | 榜单高不代表业务场景好。 | 需私有评测集和线上监控 |
| Base Model vs Chat Model | Base vs Chat | Base 擅长续写；Chat 经过指令和对话对齐。 | 使用 prompt 格式不同 |
| 量化 vs 蒸馏 | Quantization vs Distillation | 量化压低数值精度；蒸馏训练小模型模仿大模型。 | 都可降本但机制不同 |
| MoE 总参数 vs 活跃参数 | Total vs Active Params | MoE 总参数很大，但每个 token 只激活部分专家。 | 推理成本看活跃参数和路由 |
| PPL vs 人类偏好 | PPL vs Preference | PPL 衡量预测下个 token，不等于回答有用、安全、符合偏好。 | 后训练会改变偏好质量 |
| JSON 合法 vs JSON 正确 | Valid vs Correct JSON | JSON Mode 只保证格式，字段语义仍需校验。 | Schema、业务规则 |
| 工具调用 vs 代码执行 | Tool Calling vs Code Execution | 工具调用是生成结构化调用意图；代码执行是真正运行。 | 权限和沙箱 |
| RAG 忠实性 vs 答案正确性 | Faithfulness vs Correctness | 忠实性看是否依据上下文；正确性看事实是否真。 | 检索上下文本身可能错 |
| 后训练 vs 微调 | Post-training vs Fine-tuning | 后训练是多阶段对齐总称；微调是更新参数的训练动作。 | SFT/DPO/RLHF 都可属于后训练 |
| 指令微调 vs 对齐 | Instruction Tuning vs Alignment | 指令微调提升听指令；对齐还包含偏好、安全和价值约束。 | SFT、RLHF、DPO |
| Embedding 模型 vs 生成模型 | Embedding vs Generative Model | Embedding 输出向量用于检索；生成模型输出文本/代码等。 | RAG 两者常配合 |
| RAG vs 长上下文 | RAG vs Long Context | RAG 先筛选证据；长上下文直接塞更多内容但成本高且会丢中间。 | 可组合使用 |
| Agent vs Workflow | Agent vs Workflow | Agent 动态决策；Workflow 流程固定，生产中常混合。 | 可靠性 vs 灵活性 |
| Tool Calling vs MCP | Tool Calling vs MCP | Tool calling 是模型输出函数调用；MCP 是连接工具/资源的协议。 | MCP tool 可被 function calling 调用 |
| 安全拒答 vs 不知道 | Refusal vs Abstention | 拒答因安全策略；不知道因证据或置信不足。 | 用户体验不同 |
| 量化精度 vs 模型精度 | Numeric Precision vs Accuracy | 低比特是数值表示精度；任务准确率是效果指标。 | 中文都叫“精度”易混 |
| 参数高效 vs 推理高效 | PEFT vs Efficient Inference | PEFT 省训练参数；推理是否更快取决于合并、量化和服务实现。 | LoRA 未合并可能有额外开销 |
| 离线高分 vs 在线高转化 | Offline Score vs Online KPI | 离线 eval 高不一定带来用户满意或业务收益。 | A/B 与私有评测 |

## 高频公式与指标速记

| 指标/公式 | 速记 | 何时使用 |
|---|---|---|
| Precision = TP / (TP + FP) | 预测为正里有多少是真的 | 误报代价高时关注 |
| Recall = TP / (TP + FN) | 真正为正里找回了多少 | 漏报代价高时关注；RAG 召回关键 |
| F1 = 2PR / (P + R) | Precision 和 Recall 的调和平均 | 需要平衡误报/漏报 |
| Perplexity = exp(CrossEntropy) | 模型对下个 token 的困惑程度 | 语言建模基础评估 |
| Cosine Similarity = A·B/(|A||B|) | 两个向量方向相似度 | Embedding 检索 |
| MRR = mean(1/rank) | 正确答案越靠前越好 | 搜索/检索排序 |
| nDCG | 相关结果越靠前分越高 | 多等级相关性排序 |
| pass@k | k 个代码候选里至少一个通过 | 代码生成评测 |
| TTFT | 从请求到首 token 的时间 | 聊天交互体验 |
| TPOT | 后续每个 token 的平均生成时间 | 解码速度 |
| P95/P99 延迟 | 95%/99% 请求不超过的延迟 | 生产服务体验和 SLO |
| Context Precision | 检索上下文中有多少片段相关且排序靠前 | RAG 检索质量 |
| Context Recall | 答案所需证据有多少被检索进上下文 | RAG 是否漏证据 |
| Faithfulness | 回答是否被上下文支持 | RAG 幻觉检测 |
| Answer Relevance | 回答是否切题 | RAG/问答生成质量 |

## 快速选型口诀

| 场景 | 优先方案 | 原因 |
|---|---|---|
| 需要接入最新/私有知识 | RAG / 搜索 / 数据库工具 | 不必重训，知识可更新、可追溯 |
| 需要固定输出格式或领域风格 | SFT / LoRA | 改变模型行为模式更稳定 |
| 资源有限想微调 | LoRA / QLoRA | 显存和训练成本低 |
| 模型太慢太贵 | 量化 / 蒸馏 / 缓存 / 小模型路由 | 降低推理成本 |
| RAG 答案漏信息 | 提高召回：改 chunk、混合检索、多查询 | 先把证据找回来 |
| RAG 答案噪声多 | Rerank、过滤、压缩上下文 | 提高精确率和忠实性 |
| 模型乱编事实 | RAG + 引用 + 工具校验 + 不确定性表达 | Grounding 和验证 |
| Agent 误操作风险高 | 权限控制 + 沙箱 + Human-in-the-loop | 限制副作用 |
| Benchmark 高但业务差 | 建私有评测集 + 线上 A/B + 日志分析 | 评测必须贴近任务分布 |
| 微调后通用能力下降 | 降学习率、混合通用数据、PEFT、早停 | 缓解灾难性遗忘 |
| 长上下文效果不稳 | RAG + 摘要 + 证据重排 + 上下文布局 | 避免 Lost in the Middle |
| 工具调用不可靠 | 严格 schema + 参数校验 + 重试 + 审计日志 | 提高 Agent 可控性 |

## 学习路线建议

1. **入门层**：Token、Tokenizer、Transformer、Attention、预训练、推理参数。  
2. **应用层**：Prompt Engineering、RAG、Embedding、Reranker、Function Calling、Agent。  
3. **训练层**：SFT、LoRA/QLoRA、数据清洗、过拟合、灾难性遗忘、分布式训练。  
4. **对齐层**：RLHF、DPO、GRPO、RLVR、Reward Model、安全后训练。  
5. **工程层**：KV Cache、vLLM、量化、缓存、监控、评测、成本优化、LLMOps。  
6. **研究层**：MoE、长上下文、推理模型、可解释性、Agent 安全、模型编辑。

## 相关笔记

- [[微调/LLM微调详解]]
- [[微调/LLM微调面试20问]]
- [[RAG]]
- [[Transformer]]
- [[agent]]

## 参考资料与延伸阅读

- [RAGAS Metrics](https://docs.ragas.io/en/stable/concepts/metrics/)：Context Precision、Context Recall、Faithfulness、Response Relevancy、Tool Call Accuracy、Agent Goal Accuracy 等 RAG/Agent 评测指标。
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/draft/client/sampling)：MCP Sampling、Tools、Resources、Prompts、Host/Client/Server 与人机审批等协议概念。
- [Direct Preference Optimization: Your Language Model is Secretly a Reward Model](https://arxiv.org/abs/2305.18290)：DPO 与 RLHF/PPO 对齐流程的核心论文。
- Microsoft Learn 生成式 AI 评测指标：BLEU、ROUGE、F1、RAGAS 等常见指标。
- NVIDIA NeMo RAG Evaluation：RAG 检索和答案生成的评测类型。
- 近年 Post-training/RL 论文和教程：SFT、偏好优化、RLHF、DPO、GRPO、RLVR、Verifier-guided methods。
