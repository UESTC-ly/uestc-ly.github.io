# RAG与检索增强

<a id="k0edfd86b4c28"></a>

## 3D patch 时序分块与动态 FPS 采样如何保留时序信息？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

视频比图像多了时间维，逐帧编码会让 token 数随帧数线性增长。Qwen2.5-VL 把动态分辨率从空间维扩展到时间维[3]，用两项设计控制 token 数，同时保留时序信息，如图 4-6 所示：

1. **3D patch 把时间维纳入 patch 划分。** 相邻两帧绑成一个时序 patch（temporal patch size 为 2），patch 形状是时间×高×宽，即 $`2\times14\times14`$。视频以时空小块为单位编码，时间维的 token 数减半，短时的时序信息保留在同一个 patch 里。这一做法沿用自 Qwen2-VL，实现上是深度为 2 的 3D 卷积，单张图像则复制成两帧处理[2,3]。

2. **动态 FPS（Frames Per Second，每秒帧数）采样让模型适应不同帧率。** 训练时用变化的帧率采样视频，并把 M-RoPE 的时间 ID 和绝对时间对齐，模型通过时间 ID 之间的间隔感知节奏快慢，在不同采样率的视频之间保持一致的时间语义[3]。真实视频的帧率各不相同，固定帧率很难同时照顾长短视频和快慢动作；Qwen2-VL 只按帧序号编码时间，反映不了内容变化的速度和事件的绝对时刻。时间 ID 和绝对时间对齐后，模型能理解事件发生在第几秒。

两者配合，3D patch 降低时间维的冗余，动态 FPS 加绝对时间对齐保证时间语义，模型可以在可控的 token 预算内处理更长的视频，也能做时刻定位。

![3D patch 与动态 FPS 采样示意图](https://raw.githubusercontent.com/WeThinkIn/AIGC-Interview-Book/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/images/4-6-3Dpatch与动态FPS采样示意图.png)
<p align="center">图 4-6 3D patch 与动态 FPS 采样示意图</p>

> **面试速答**：3D patch 把相邻两帧绑成一个 2×14×14 的时空 patch，时间维 token 减半，短时时序留在 patch 内。动态 FPS 在训练时用变化的帧率采样，并把 M-RoPE 的时间 ID 和绝对时间对齐，模型靠 ID 间隔感知快慢，能定位事件发生在第几秒。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/4_AI%E5%A4%9A%E6%A8%A1%E6%80%81%E4%B8%BB%E6%B5%81%E6%A8%A1%E5%9E%8B%E6%A0%B8%E5%BF%83%E6%8A%80%E6%9C%AF%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L376)，来源许可：GPL-3.0。

<a id="ke753e4dbbf01"></a>

## agentic rag 和传统 rag 的区别？

**回答：**

<a id="tencent-llm-collection-20260903-q132"></a>

**相关解释：** [agent 调用工具这个过程是怎么优化的？](Agent%E3%80%81%E5%B7%A5%E5%85%B7%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81-01.md#k98cb3547adb1)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1628)，来源许可：GPL-3.0。

<a id="k166ffee255aa"></a>

## ArcFace embedding 如何作为生成模型的身份损失？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

冻结一个预训练人脸识别网络 $f$，分别提取参考人脸和生成结果的人脸 embedding，常见身份损失为：

```math
L_{id}=1-\cos\big(f(x_{ref}),f(x_{gen})\big)
```

它可以与重建、感知、关键点、分割、对抗或扩散噪声损失联合使用，约束生成结果保留身份，同时允许文本、姿态、服装和风格发生变化。视频生成还要对多帧身份相似度和时序波动进行约束。

身份损失依赖可靠的人脸检测和对齐；过强会牺牲表情自然度、姿态多样性和画面质量。对未授权人物进行身份复刻可能造成隐私、冒名和肖像权风险，因此训练、推理和评估都需要授权检查与内容安全策略。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BB%8F%E5%85%B8%E6%A8%A1%E5%9E%8B/%E4%BA%BA%E8%84%B8%E6%A8%A1%E5%9E%8B%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L228)，来源许可：GPL-3.0。

<a id="k16e1d6bad8c7"></a>

## BLIP 在图文检索任务上相比 CLIP 有何优势？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐ (3/5)**

BLIP 在图文检索上的优势来自 ITC 召回加 ITM 重排的两阶段做法，弥补了 CLIP 纯双塔召回快但不够准的短板，同时受益于数据和训练方式，具体有三点：

1. **更干净的训练数据。** CapFilt 清洗后的图文对噪声更低，ITC 学到的全局对齐好于直接在原始网络文本上训练的结果。

2. **ITM 提供细粒度精排。** CLIP 只能算全局向量相似度，分辨不出"看着像、细节不符"的候选。BLIP 先用 ITC 双塔召回 Top-K 候选，保留双塔的效率，再用带 cross-attention 的 ITM 编码器给这 K 个候选逐一打匹配分并重排。ITM 让文本逐层关注图像，能识别 ITC 漏掉的细粒度错配，把匹配的结果排到前面。

3. **难负样本训练让排序更可靠。** 训练 ITM 时按 ITC 相似度挖掘难负样本，逼模型分辨细微差别，区分高度相似的干扰项时明显强于只看全局相似度的模型。

效率上，ITM 只作用于召回后的小候选集，BLIP 论文在 COCO 上取 $`k=256`$，在 Flickr30K 上取 $`k=128`$。全库召回仍由 ITC 双塔加 ANN 完成，ITM 只做最后的精排，整体延迟可控。论文报告，用同样的 1400 万张预训练图片，BLIP 在 COCO 上的平均 R@1（正确结果排在第一位的查询比例）比此前最好的 ALBEF 高 2.7 个百分点[4]。

> **面试速答**：BLIP 先用 ITC 双塔召回 Top-K，再用带 cross-attention 的 ITM 编码器逐一打分重排，COCO 上 k 取 256。ITM 靠难负样本训练，能识别全局相似度分辨不出的细节错配，CapFilt 清洗的数据也让召回更准。重排只作用于小候选集，整体延迟可控。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/3_AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%9F%B3%E6%A8%A1%E5%9E%8B%E6%A0%B8%E5%BF%83%E6%8A%80%E6%9C%AF%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L399)，来源许可：GPL-3.0。

<a id="k6ae759ae7cc7"></a>

## Chunk 太大或太小分别有什么问题？重叠部分主要解决什么问题？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

块太大时，多个主题混在一个向量中，相关部分可能被无关内容稀释，重排与上下文成本也更高；块太小时，标题、限定条件和结论容易分离，单块无法支持完整回答。最优粒度取决于问题和文档结构。

重叠主要缓解答案跨切分边界的问题，例如定义在前一块末尾、例外条件在下一块开头。但重叠不会自动修复表格结构、指代关系或错误解析，也不是越多越好。

可以采用小块召回、父段或邻块补全，在召回精度和生成上下文之间做分工。评测同时记录证据覆盖、重复占比、平均上下文 Token 和端到端质量，避免仅靠扩大块与重叠掩盖检索问题。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L167)，来源许可：GPL-3.0。

<a id="ka4976289a240"></a>

## Claude Code是给模型用grep检索，没有用RAG检索，这俩有什么区别？为什么没用rag？

**回答：**

grep 检索和 RAG 检索的核心区别在于：grep 是对当前文件系统做精确字符串或正则匹配，RAG 通常是把文档切块、向量化、建索引，再通过语义相似度召回相关 chunk。

grep 的优点是确定、实时、可解释。代码仓库里很多问题依赖精确符号，例如函数名、类名、配置项、错误日志、接口路径、变量名。grep 可以直接告诉你某个符号在哪个文件哪一行出现，而且检索的是当前工作区最新内容，不需要提前建索引，也不会因为 embedding 过期导致召回旧内容。

RAG 的优点是语义召回。用户不知道准确关键词时，RAG 可以通过语义相似度找到相关内容，适合文档问答、知识库问答、概念相近但措辞不同的场景。但在代码任务中，RAG 有几个问题：切块可能破坏函数或类的完整上下文；embedding 对精确符号、短变量名、路径名不一定敏感；索引可能落后于文件最新状态；top-k 召回可能漏掉关键定义；还会增加索引维护和延迟成本。

所以 Claude Code 这类 coding agent 更偏向使用 grep、文件读取、目录遍历等实时、确定、可定位的检索方式，是因为代码修改需要精确 grounding。它不是说 RAG 没用，而是代码仓库场景里第一优先级通常是找准当前代码里的真实引用和定义。

如果仓库非常大，或者要做跨项目语义理解，可以把 grep 和语义检索结合：先用语义检索找可能相关模块，再用 grep 精确定位符号；或者先 grep 找入口，再读文件构建上下文。比较好的 coding agent 不会迷信某一种检索，而是根据任务选择确定性检索、语义检索和人工结构信息。

<a id="ant-agent-20260520-q8"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%9A%82%E8%9A%81%E9%9B%86%E5%9B%A2%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L179)，来源许可：GPL-3.0。

<a id="k4a3114cef1ea"></a>

## CLIP 检索在实际落地中存在哪些瓶颈？如何缓解？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐ (3/5)**

CLIP 检索效率高，到了工业场景也会暴露几个瓶颈，面试中常以"你用 CLIP 做检索遇到过什么问题"的形式追问：

1. **细粒度和组合语义检索弱。** query 越精确，CLIP 越吃力。"穿红色裙子、戴墨镜、站在埃菲尔铁塔前的女性"这种多属性组合加空间关系的查询，全局向量很难编码准确，容易召回只满足部分条件的图。缓解办法是用 BLIP、BLIP-2 这种带融合编码器的模型做召回后重排[4,14]，双塔先召回 Top-K，再用带 cross-attention 的 ITM 模型精排。

2. **领域偏移导致精度下降。** CLIP 主要在自然图像上训练，迁移到医学影像、工业缺陷、遥感、电商白底图等专业领域时，预训练分布覆盖不到，检索精度明显下降。缓解办法是在领域图文对上做 LoRA 微调或继续对比预训练，BiomedCLIP、FashionCLIP 都是这样得到的领域版本[15,16]。

3. **文本端长度和表达受限。** 文本编码器的上下文只有 77 个 token，长查询、长文档放不下，复杂的逻辑查询也理解不好。缓解办法是长文本先截断或摘要再编码，或者换用文本端更强的模型，如微软的 LLM2CLIP 把微调过的 LLM 接成 CLIP 的文本编码器，长文本检索提升明显[17]。

4. **模态鸿沟（modality gap）。** Liang 等人 2022 年的研究发现，CLIP 的图像向量和文本向量在联合空间里各自聚在一块区域，彼此隔着一段距离，没有完全重合[18]。跨模态相似度的绝对值因此偏低，阈值不好定。缓解办法是检索时只看相对排序，不用绝对阈值，或者对向量做中心化校正。

5. **向量索引要在精度和延迟之间权衡。** 亿级库必须用 IVF-PQ、HNSW 等近似索引，PQ 量化压缩会损失精度，召回率、延迟和内存要反复调参。缓解办法是分层索引，召回阶段放宽，重排阶段补回精度。

这些瓶颈决定了 CLIP 在检索系统里适合做高召回的粗排。典型架构是 CLIP 双塔召回几百个候选，再由融合模型或业务规则精排，返回 Top-N。

> **面试速答**：主要瓶颈有五个。组合语义查询容易召回只满足部分条件的图，可以用 ITM 模型重排；专业领域精度下降，要用领域数据微调；文本只有 77 个 token；图文向量之间有模态鸿沟，阈值难定；ANN 索引要权衡精度和延迟。实际常把 CLIP 当召回器，后面接精排。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/3_AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%9F%B3%E6%A8%A1%E5%9E%8B%E6%A0%B8%E5%BF%83%E6%8A%80%E6%9C%AF%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L244)，来源许可：GPL-3.0。

<a id="k3999ed21c38e"></a>

## CLIP 的双塔结构为什么天然适合大规模跨模态检索？

**难度评分：⭐⭐ (2/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

跨模态检索（以文搜图、以图搜文）是 CLIP 落地最广的场景，双塔结构和向量检索系统配合得很好，具体体现在三个方面：

1. **特征可以离线预计算。** 图像和文本各自编码，互不依赖。亿级图库可以提前全部编码成向量，存进 FAISS、Milvus 等向量检索库[12]，检索时只编码一次 query，剩下的交给向量库。单塔要求 query 和每个候选联合编码，做不到预存。

2. **检索变成近似最近邻搜索（ANN）。** 图文都映射到同一个归一化向量空间，跨模态匹配等价于按余弦相似度（也即内积）排序，这种排序可以直接交给 HNSW、IVF-PQ 等 ANN 索引[12,13]。借助这些索引，亿级库的检索可以做到毫秒级，库变大时耗时的增长也远慢于线性。

3. **一套向量双向复用。** 同一套图文向量既支持以文搜图，也支持以图搜文，还能以图搜图、以文搜文，不用为每个方向单独建模。电商的拍照搜同款、相册的用文字找照片都用到了这一点。

和单塔对比，差距更直观。假设图库有 1 亿张图，用户发起一次文本查询，双塔只需 1 次文本编码加 1 次 ANN 检索；单塔要把 query 和 1 亿张图逐一联合编码，相当于 1 亿次前向。所以工业检索系统普遍用 CLIP 式双塔做召回，单塔的精排能力只用在召回后的小候选集上，形成双塔召回、单塔精排的两阶段方案，如图 3-2 所示。

![双塔召回与单塔精排两阶段检索流程图](https://raw.githubusercontent.com/WeThinkIn/AIGC-Interview-Book/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/images/3-2-双塔召回与单塔精排两阶段检索流程图.png)
<p align="center">图 3-2 双塔召回与单塔精排两阶段检索流程图</p>

> **面试速答**：双塔让图像和文本各自编码，图库向量可以离线算好存进向量库，查询时只编码一次 query。图文在同一个归一化空间里，匹配变成内积排序，可以直接用 HNSW、IVF-PQ 等 ANN 索引，亿级库也能毫秒级返回。单塔要和每个候选联合编码，只适合召回后的精排。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/3_AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%9F%B3%E6%A8%A1%E5%9E%8B%E6%A0%B8%E5%BF%83%E6%8A%80%E6%9C%AF%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L223)，来源许可：GPL-3.0。

<a id="k8592d3327e8e"></a>

## CLIP衍生进阶模型；检索场景模型适配改造思路

答：CLIP 之后的衍生模型大致可以分为几类。

第一类是扩大数据与训练范式的 CLIP 系列，例如 OpenCLIP、MetaCLIP、Chinese-CLIP、EVA-CLIP、SigLIP。OpenCLIP 复现并扩展了 CLIP 的开源训练体系；Chinese-CLIP 强化中文图文对齐；EVA-CLIP 使用更强视觉 backbone 和更大规模数据提升视觉表征；SigLIP 把原始 softmax 对比学习改成 sigmoid loss，降低对全局 batch softmax 的依赖，在大规模训练中更灵活。

第二类是从纯对比学习走向图文理解的模型，例如 ALBEF、BLIP、BLIP-2、LLaVA、InternVL、Qwen-VL。它们不只学习全局图文向量，还会引入图文匹配、图文生成、视觉问答、指令微调等目标，增强细粒度理解和多轮推理能力。

第三类是检索增强方向，例如 CLIP + Reranker、BLIP/MLLM Reranker、多模态 Embedding + Cross Encoder。工业检索通常不会只靠一个双塔模型解决所有问题，而是采用“召回 + 粗排 + 精排”的多阶段体系。

在检索场景里，模型适配改造可以从几个层面展开：

1. 数据层：构建业务域图文对、视频封面-标题对、视频帧-字幕对、query-click item 对、query-play item 对、query-favorite item 对。爱奇艺这类视频业务里，query 可能是“悬疑短剧”“某演员片段”“亲子动画”，正样本可以来自点击、播放时长、完播、收藏等行为，负样本要区分随机负样本和 hard negative。

2. 模型层：如果追求大规模召回，优先用双塔结构，分别编码 query 和 item，离线建 ANN 向量索引；如果追求精排效果，可加入 cross-encoder/reranker，对 query-item 进行交互式打分。图像或视频场景可把视频抽帧、OCR、ASR、标题、标签、剧情简介分别编码，再做多向量融合。

3. 训练目标层：召回模型常用 InfoNCE、Multiple Negatives Ranking Loss、Triplet Loss、Circle Loss；排序模型常用 pairwise ranking loss、listwise softmax loss、binary cross entropy。对业务场景要加入曝光偏差、点击噪声、时长偏置等校正。

4. 工程层：需要控制向量维度、索引规模、延迟和更新频率。常见做法是离线生成 item embedding，在线只编码 query；对高频 query 做缓存；对多模态 item 做向量融合或多路召回；对热门内容和冷启动内容分别设计召回策略。

5. 评估层：离线看 Recall@K、MRR、NDCG、mAP，线上看 CTR、播放时长、完播率、搜索成功率、长尾内容曝光、用户满意度。检索模型不是相似度越高越好，而是要服务于真实业务指标。

### 补充说明

<a id="batch1-p1-q3"></a>

<a id="batch4-p1-q3"></a>

**相关解释：** [Embedding模型与Reranker差异，二者训练Loss区别](RAG%E4%B8%8E%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA-01.md#k1abf61aa73cc)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%88%B1%E5%A5%87%E8%89%BA%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L49)，来源许可：GPL-3.0。
- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%88%B1%E5%A5%87%E8%89%BA%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L597)，来源许可：GPL-3.0。
- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%88%B1%E5%A5%87%E8%89%BA%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L708)，来源许可：GPL-3.0。

<a id="k22d5fd133f55"></a>

## Embedding 相似度、余弦相似度、向量检索和 RAG 的数学基础是什么？

Embedding 把离散对象映射到连续向量空间：

$$
e = f_{\theta}(x) \in \mathbb{R}^{d}
$$

余弦相似度：

$$
\cos(a,b)=\frac{a^Tb}{\|a\|_2\|b\|_2}
$$

若向量已归一化，内积等于余弦相似度。

RAG 检索通常包括：

1. 将 query 和文档 chunk 编码为向量。
2. 使用内积、余弦或 L2 距离找近邻。
3. 把检索结果拼接进上下文，条件生成答案。

**常见指标：**

- Recall@k：相关文档是否进入前 k。
- MRR：第一个相关结果排名的倒数均值。
- nDCG：考虑相关性等级和排序位置。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E6%95%B0%E5%AD%A6%26%E7%89%A9%E7%90%86%E6%9C%AC%E8%B4%A8%E5%8E%9F%E7%90%86%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3%E6%95%B0%E5%AD%A6%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L1445)，来源许可：GPL-3.0。

<a id="k1abf61aa73cc"></a>

## Embedding模型与Reranker差异，二者训练Loss区别

答：Embedding 模型和 Reranker 的核心区别是结构和使用阶段不同。

Embedding 模型通常是 bi-encoder。query 和 document/item 分别独立编码成向量：

$$
q=f_\theta(query),\quad d=g_\theta(doc)
$$

相关性通过点积或余弦相似度计算：

$$
s(q,d)=q^Td
$$

因为 document embedding 可以离线预计算并建立向量索引，所以 Embedding 模型适合大规模召回。它的优点是快、可扩展、适合百万到十亿级候选库；缺点是 query 和 document 在编码阶段没有 token 级交互，细粒度判断能力有限。

Reranker 通常是 cross-encoder 或 decoder scorer。它把 query 和候选 document/item 拼在一起输入模型：

$$
s = h_\theta([query; doc])
$$

模型可以通过 attention 直接建模 query 和 document 的细粒度交互，所以排序更准。但每个 query-doc pair 都要单独前向，成本高，通常只能对召回后的 TopK 候选做重排。

二者训练 loss 也不同。

Embedding 模型常用对比学习 loss。一个 batch 内有 $N$ 个 query-doc 正样本对，相似度矩阵为：

$$
s_{ij}=q_i^Td_j
$$

Multiple Negatives Ranking Loss / InfoNCE 可写为：

$$
\mathcal{L}=-\frac{1}{N}\sum_i \log \frac{\exp(s_{ii}/\tau)}{\sum_j \exp(s_{ij}/\tau)}
$$

如果做双向检索，还会加 document-to-query 方向。也可以使用 Triplet Loss：

$$
\mathcal{L}=\max(0, m+s(q,d^-)-s(q,d^+))
$$

Embedding loss 的重点是学习一个全局向量空间，让正样本近、负样本远。

Reranker 的 loss 更偏排序监督。常见有三类：

1. Pointwise BCE：对每个 query-doc pair 判断相关/不相关：

$$
\mathcal{L}=-y\log\sigma(s)-(1-y)\log(1-\sigma(s))
$$

2. Pairwise Ranking Loss：希望正样本分数高于负样本：

$$
\mathcal{L}=-\log\sigma(s^+ - s^-)
$$

或 hinge 形式：

$$
\mathcal{L}=\max(0,m-s^+ + s^-)
$$

3. Listwise Softmax Loss：对同一个 query 下的一组候选做 softmax，让正样本或高相关样本排在前面：

$$
\mathcal{L}=-\log\frac{\exp(s^+)}{\exp(s^+)+\sum_k\exp(s_k^-)}
$$

实际系统中，Embedding 和 Reranker 是互补关系。Embedding 负责从海量库中高召回地找出候选，Reranker 负责在较小候选集里做精细排序。面试时可以给出典型链路：query 先经过 embedding 模型召回 Top1000，再经过轻量 ranker 到 Top100，最后用 cross-encoder 或 MLLM reranker 精排 Top20。

### 补充说明

**回答：**
RAG 的关键链路是切片、向量化、召回、rerank、上下文组装和带引用生成。稀疏检索适合关键词、实体和精确匹配，稠密检索适合语义泛化，实际常用 hybrid retrieval。Rerank 用更强的交叉编码匹配弥补向量召回排序不准。HyDE 先生成假想答案再检索，适合模糊问题，但要用 rerank 和引用校验防止生成内容带偏检索。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%88%B1%E5%A5%87%E8%89%BA%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L491)，来源许可：GPL-3.0。
- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%88%B1%E5%A5%87%E8%89%BA%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L673)，来源许可：GPL-3.0。
- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%88%B1%E5%A5%87%E8%89%BA%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L784)，来源许可：GPL-3.0。

<a id="kd242cc8fff0e"></a>

## Embedding模型如何选择？不同Embedding模型会对检索效果产生哪些影响？

**回答：**

Embedding 模型把文本映射到向量空间，使语义相关文本距离更近。选择时要看目标语言、领域、输入长度、查询/文档任务是否匹配、部署形态、维度、推理吞吐、许可和成本，而不是只看通用榜单分数。

具体要检查：中文和中英混合能力，技术术语、产品名、编号和长文档表现，是否有 query/document 不同指令，最大上下文和截断策略，向量维度与存储成本，归一化方式与距离度量，以及模型是否支持批量、量化和本地部署。若数据敏感，本地部署和数据不出域可能比少量离线分数更重要。

模型会影响三个层面：

- **语义召回：** 近义表达、跨语言和上下位概念是否聚近；过度语义化可能把关键词相近但事实不同的文档召回。
- **细节区分：** 版本号、错误码、类名和数字等精确信息通常需要 BM25/倒排补充。
- **系统资源：** 维度、索引大小、编码速度和延迟直接影响成本与吞吐；模型升级还可能改变向量分布，不能直接混用旧索引。

最终应构建与线上分布一致的 Query-证据集，比较 Recall@K、MRR/nDCG、长短问题、中文术语、噪声和权限场景，并同时记录 P95、吞吐、内存、成本和版本迁移方案。Embedding 是召回组件，不是完整 RAG 质量的唯一决定因素。

<a id="bilibili-ai-agent-20260818-q10"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%93%94%E5%93%A9%E5%93%94%E5%93%A9%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L164)，来源许可：GPL-3.0。

<a id="ka5816a881c23"></a>

## GraphRAG

相关内容：[《GraphRAG：用图结构补充向量检索》](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/rag/graphrag.md)

GraphRAG 题集中在实体关系、多跳推理和全局问题，也会追问实体关系如何抽取、社区摘要如何生成、权限如何过滤，以及后续更新需要多少成本。选型时还要对照业务问题和现有检索链路。

常见面试题：

- GraphRAG 解决什么问题？和标准向量 RAG 有什么区别？
- 为什么说 Chunk 是信息孤岛？
- 向量相似度为什么不擅长多跳推理？
- GraphRAG 中实体、关系、社区发现分别是什么？
- 全局检索和局部检索有什么区别？
- GraphRAG 的社区摘要有什么价值？它的成本在哪里？
- GraphRAG 如何做权限过滤？
- 什么场景适合 GraphRAG？什么场景不适合？
- 成熟系统为什么会组合关键词检索、向量检索、多向量检索和图检索？

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/rag-interview-questions.md#L90)，来源许可：Apache-2.0。

<a id="k413a5298aeac"></a>

## Kimi「长 PDF 解析问答」应该用长上下文直读还是多模态 RAG？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

长 PDF 问答需要按文档规模和问题类型在长上下文直读与多模态 RAG 之间路由，短文档直读，长文档和文档库走检索，全局问题先分段摘要再汇总。Kimi 于 2024 年 3 月宣布 200 万字上下文版本开启内测[14]，这一数字对应当时的内测版本。两条路线及其混合方案的对照如图 6-5 所示：

1. **长上下文直读。** 整篇文档放进上下文，跨章节推理和全局汇总的效果最好，也不存在召回遗漏。代价有三项：百页 PDF 经视觉 token 化后，预填充的延迟和费用随长度上升；超长序列存在 lost in the middle 现象，中部信息的利用率低于首尾[15]；几千份合同组成的文档库无法放进任何上下文窗口。

2. **多模态 RAG。** ColPali 把每一页编码为多向量，MaxSim 公式见 [5.6.1.2](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/6_AI%E5%A4%9A%E6%A8%A1%E6%80%81%E4%B8%8B%E6%B8%B8%E5%BA%94%E7%94%A8%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#q5612)。这种逐 token 匹配比单向量双塔更容易命中页面中的一小块图表，页面向量还可以离线预计算[1]。召回 top-k 页之后交给 MLLM 精读，费用与文档库的总页数解耦，版面信息也得以保留。代价是两跳结构带来召回损失，问题表述与原文措辞差别较大时，相关页面可能进不了上下文。

3. **混合。** 短文档直读，长文档和文档库走检索，全局问题先分段摘要再汇总。路由时考察三个变量：单篇还是整库，定位型问题还是全局型问题，静态文档还是每日更新的文档。

在答案旁标注页码和出处，既是交互设计，也是幻觉治理手段。检索式架构天然带有出处，直读架构则需要额外训练模型输出引用，这是很多产品最终采用混合架构的一个原因。

![长文档直读与检索示意图](https://raw.githubusercontent.com/WeThinkIn/AIGC-Interview-Book/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/images/6-5-长文档直读与检索示意图.png)

<p align="center">图 6-5 长文档直读与检索示意图</p>

> **面试速答**：直读适合单篇文档中的跨章节和全局问题，但中部信息利用率低，文档库也放不进窗口。多模态 RAG 按页检索再精读，费用与库的规模解耦，代价是召回损失。产品通常按文档长度和问题类型混合路由，并在答案旁标注页码。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80%EF%BC%88%E7%B2%BE%E5%8D%8E%E7%89%88%EF%BC%89/6_AI%E5%A4%9A%E6%A8%A1%E6%80%81%E4%B8%8B%E6%B8%B8%E5%BA%94%E7%94%A8%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L259)，来源许可：GPL-3.0。

<a id="k2b4dc943b40f"></a>

## Markdown、PDF 和代码文件的切分方式有什么不同？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

Markdown 宜按标题层级、段落、列表、表格和代码围栏处理，保留标题路径；PDF 要先确认读取顺序、分页、双栏、页眉页脚、OCR 与表格是否正确；代码则更适合按文件、类、函数或 AST 节点切分，并关联符号、注释和依赖信息。

PDF 的视觉相邻不一定代表语义相邻，解析错误发生在切分之前，调整 chunk size 无法修复被打乱的双栏文字。跨页表格需要关联表头，扫描件要保留 OCR 置信度和页码。代码不能把函数签名与主体随意分离。

统一输出可以包含 `doc_id、version、section_path、page_or_lines、chunk_index、parent_id`，但不同类型的结构不能被强行抹平。抽样比较原文件和解析结果，再开展检索评测，才能定位是解析损失还是召回失败。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L177)，来源许可：GPL-3.0。

<a id="kc996e1a85980"></a>

## Memory 与 RAG 如何组合使用？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

一个完整 Agent 往往同时使用 Memory 和 RAG：

1. **先理解用户和任务状态**

   从 Memory 中取用户偏好、当前任务进度、历史约束。

2. **再检索外部知识**

   用 RAG 查企业文档、技术资料、产品政策、实时信息。

3. **合并上下文**

   将用户目标、相关记忆、检索证据、工具结果和当前状态按优先级拼装。

4. **生成答案或行动**

   模型基于合并上下文推理。

5. **写回记忆**

   任务结束后提取新的偏好、经验或状态更新。

典型场景：

- 个人旅行助手：Memory 记住预算和偏好，RAG 查航班酒店政策。
- 企业客服：Memory 记住客户历史问题，RAG 查产品知识库。
- 编码 Agent：Memory 记住项目规范，RAG/代码检索查当前实现。

关键是来源标注。模型要知道哪些信息来自长期记忆，哪些来自文档检索，哪些来自当前用户指令，避免把不可信内容当成高优先级规则。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/05_Agent%E8%AE%B0%E5%BF%86%E4%B8%8E%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L215)，来源许可：GPL-3.0。

<a id="ka9392eb1bf5a"></a>

## Memory 和 RAG 的区别如何快速回答？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

RAG 主要解决“从外部知识库检索事实”；Memory 主要解决“Agent 在交互和执行中积累状态与经验”。

| 维度 | RAG | Memory |
| --- | --- | --- |
| 数据来源 | 文档、知识库、网页、数据库 | 对话、行为、偏好、任务状态 |
| 更新频率 | 相对低 | 高，随交互变化 |
| 目标 | 补充知识 | 保持连续性和个性化 |
| 检索方式 | Query-driven | Context/State-driven |
| 风险 | 检索不准、文档过期 | 记忆污染、隐私泄露 |

两者可以结合：RAG 提供外部知识，Memory 提供个体和任务上下文。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L617)，来源许可：GPL-3.0。

<a id="k53774d5589d0"></a>

## Memory 和 RAG 的本质区别是什么？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

| 维度 | Memory | RAG |
| --- | --- | --- |
| 核心目的 | 保持连续性、个性化、状态和经验 | 检索外部知识，增强事实性 |
| 数据来源 | 对话、行为、任务轨迹、偏好、工具使用 | 文档、网页、知识库、数据库、手册 |
| 更新频率 | 高频、增量、交互驱动 | 低到中频，常为批量更新 |
| 检索方式 | Context / State-driven | Query-driven |
| 数据形态 | 事件、画像、摘要、向量、图、状态 | 文档块、向量索引、倒排索引、知识条目 |
| 风险 | 记忆污染、隐私泄露、跨用户串线 | 文档过期、检索不准、来源不可信 |

Memory 解决“这个 Agent 记得什么”；RAG 解决“这个问题需要查什么知识”。

例子：

- 用户说“我不吃香菜”，应进入个人 Memory。
- 企业产品手册、API 文档、报销制度，应进入 RAG 知识库。
- 某次任务失败原因“上次部署失败是因为 staging 环境缺少 env”，可进入任务 Memory。

检索实现的完整链路见 [Agent RAG 与混合检索工程](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG与混合检索工程高频考点.md)，涵盖切分、索引、排序、过滤与质量诊断。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/05_Agent%E8%AE%B0%E5%BF%86%E4%B8%8E%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L188)，来源许可：GPL-3.0。

<a id="kbd28eefcca14"></a>

## MRAG系统如何通过"Refiner"组件（如LLMLingua的困惑度过滤、Prompt-SAW的关系感知图）压缩检索结果？

Refiner设计：  
• 硬提示：LLMLingua基于困惑度（PPL）过滤冗余token，压缩率50%时任务准确率下降<3%。  

• 软提示：AutoCompressor将长上下文压缩为32维向量，通过RNN循环更新记忆，在GovReport摘要任务上ROUGE-2保持0.82。  

权衡指标：  
| 方法          | 压缩率 | 信息保留率 | 跨模型兼容性 |  
|---------------|--------|------------|--------------|  
| 硬提示        | 50-70% | 85%        | 高           |  
| 软提示        | 80-95% | 92%        | 低（需微调） |  

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80/%E5%A4%9A%E6%A8%A1%E6%80%81-%E5%89%8D%E6%B2%BF%E6%8A%80%E6%9C%AF.md#L290)，来源许可：GPL-3.0。

<a id="ka2accdd608f1"></a>

## OCR + RAG 如何构建文档问答系统？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐⭐ (5/5)**

OCR + RAG 是企业文档问答、合同审查、论文助手、票据问答中的常见架构。

典型流程：

```text
PDF/图片/扫描件
  -> OCR 识别文字
  -> 版面分析和阅读顺序恢复
  -> 表格/公式/图片说明解析
  -> 文档切分 chunk
  -> 向量化与索引
  -> 用户问题检索相关片段
  -> LLM 基于证据生成答案
  -> 返回引用位置和置信度
```

关键问题包括：

- **阅读顺序**：多栏论文、表格、页眉页脚如果顺序错，会影响 RAG；
- **chunk 策略**：不能机械按字数切，要考虑标题、段落、表格和页码；
- **表格处理**：表格应保留行列结构，可转 Markdown/HTML；
- **证据引用**：答案应返回页码、坐标、原文片段，方便审计；
- **纠错机制**：OCR 错字会传递到检索和生成，需要词典、规则、LLM 校验或人工复核。

面试中要强调：OCR + RAG 的难点不只是识别准确率，还包括文档结构恢复、检索粒度、证据可追溯和幻觉控制。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BB%8F%E5%85%B8%E6%A8%A1%E5%9E%8B/OCR%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L298)，来源许可：GPL-3.0。

<a id="k547389c9711c"></a>

## QLoRA 中的分块量化如何解决普通量化导致的信息损失问题？

QLoRA 的分块量化通过将模型权重按小块（block）独立量化，解决普通量化信息损失问题，具体体现在：

1. 局部自适应量化：每个小块单独计算缩放因子，保留更多局部细节和动态范围。
2. 减少量化误差累积：避免整块或全局量化带来的误差集中，提升表达精度。
3. 兼顾压缩率与精度：在保持高压缩的同时，有效保留关键权重信息。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/04-ai-algorithms/llm/llm-interview-questions.md#L537)，来源许可：GPL-3.0。

<a id="kd8c9c0acc611"></a>

## RAG 与库存一致性：假如商品知识库是实时更新的，那么要怎样保证 RAG 的召回结果和库存信息保持一致呢？

**回答：**

语义检索索引通常是最终一致的，不能单靠‘实时更新向量库’保证库存强一致。商品介绍与语义表示进入检索索引，库存、上下架、区域可售和价格由权威业务服务管理。

召回候选后批量检查当前售卖状态，重排与回答基于校验后的结果；变更事件携带版本，消费者幂等更新、处理乱序，并通过定期对账修复丢失事件。缓存失效、TTL 和读取版本共同控制陈旧窗口。

即使回答生成时有货，下单前仍可能被其他用户买走。真正的交易保证要在库存服务通过原子扣减、预占或相应事务完成，不能靠检索时的一次检查。服务不可用时明确库存未确认，避免把旧描述当成购买承诺。

<a id="jd-damodel-20251211-20260205-p9-q5"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E4%BA%AC%E4%B8%9C%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1412)，来源许可：GPL-3.0。

<a id="k3ef4ce58d14e"></a>

## RAG 为什么不能完全消除幻觉？

因为 RAG 的每个环节都可能出错：

- 文档解析错误导致知识库内容不准确；
- 分块不合理导致关键上下文被切断；
- embedding 不匹配导致没召回正确片段；
- 排序错误导致相关片段排在后面；
- 检索结果不足但模型仍强行回答；
- 多个片段冲突时模型错误整合；
- 提示约束不强导致模型加入参数知识。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/05_%E6%8F%90%E7%A4%BA%E5%B7%A5%E7%A8%8B%EF%BC%9A%E5%BA%94%E7%94%A8%E5%A4%A7%E6%A8%A1%E5%9E%8B%E7%9A%84%E9%AB%98%E7%BA%A7%E6%96%B9%E6%B3%95.md#L570)，来源许可：GPL-3.0。

<a id="k2fa767805bfd"></a>

## rag 召回率 90%，badcase 都是什么问题，具体是哪个环节导致的？有想过怎么优化吗？

**回答：**

线上 RAG 要同时报告效果和系统指标：Recall@K、MRR/nDCG、答案正确率、引用准确率、拒答准确率、P50/P95 延迟、QPS、Token、缓存命中率和单位请求成本。召回数量不应永远固定，可根据 query 难度、分数间隔、置信度、上下文预算和风险动态截断；但动态策略必须在验证集上校准。

召回 badcase 要按解析、切分、Embedding、查询改写、过滤、索引、融合、Rerank 和上下文组装逐环定位。不能把“召回率 90%”直接等同于回答正确率，剩余 badcase 可能来自答案不可回答、权限过滤、版本过期、跨块关系丢失或生成阶段误用证据。

<a id="tencent-llm-collection-20260903-q138"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1676)，来源许可：GPL-3.0。

<a id="kd974a87df78d"></a>

## RAG 和微调可以结合吗？

RAG 解决知识接入，微调解决行为适配。常见组合方式包括：

- 用微调提升模型遵循 RAG 指令和引用格式的能力；
- 用 RAG 提供实时知识；
- 用微调适配领域语言风格；
- 用 RAG 日志沉淀高质量训练数据；
- 用偏好优化提升答案选择和拒答边界。

<a id="prompting-section-34-question-06"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/05_%E6%8F%90%E7%A4%BA%E5%B7%A5%E7%A8%8B%EF%BC%9A%E5%BA%94%E7%94%A8%E5%A4%A7%E6%A8%A1%E5%9E%8B%E7%9A%84%E9%AB%98%E7%BA%A7%E6%96%B9%E6%B3%95.md#L650)，来源许可：GPL-3.0。

<a id="kec13f17a23bc"></a>

## RAG 和微调的主要区别是什么？

RAG 通过外部检索提供知识，不更新或很少更新模型参数；微调通过训练数据改变模型参数。二者解决的问题不同：

![](https://raw.githubusercontent.com/WeThinkIn/AIGC-Interview-Book/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/imgs/05-7.png)

| 维度 | RAG | 微调 |
| --- | --- | --- |
| 主要目标 | 接入外部知识和证据 | 改变模型行为、风格或能力分布 |
| 数据更新 | 更新知识库和索引即可 | 需要重新训练或继续训练 |
| 可追溯性 | 可返回引用 | 参数知识难以追溯 |
| 适用场景 | 企业文档、动态知识、私有知识问答 | 固定任务、风格对齐、格式稳定、领域表达 |
| 风险 | 检索错误、上下文不足 | 数据质量、过拟合、能力退化 |

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/05_%E6%8F%90%E7%A4%BA%E5%B7%A5%E7%A8%8B%EF%BC%9A%E5%BA%94%E7%94%A8%E5%A4%A7%E6%A8%A1%E5%9E%8B%E7%9A%84%E9%AB%98%E7%BA%A7%E6%96%B9%E6%B3%95.md#L632)，来源许可：GPL-3.0。

<a id="kc5ac567876bb"></a>

## RAG 基础

相关内容：[《RAG 基础概念：检索、生成与工程取舍》](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/rag/rag-basis.md)

基础题围绕 RAG 的工作流程和适用场景展开，也会与传统搜索、微调和长上下文做比较。幻觉、引用和拒答通常会作为后续追问。

常见面试题：

- 什么是 RAG？为什么需要 RAG？
- RAG 和传统搜索引擎有什么区别？
- RAG 和微调怎么选？什么时候用 RAG，什么时候微调，什么时候两者结合？
- RAG 系统中 Embedding 模型怎么选？为什么？
- 余弦相似度、内积和欧氏距离有什么区别？
- RAG 的幻觉问题怎么解决？RAG 一定不会产生幻觉吗？
- 什么是 Lost in the Middle 问题？怎么应对？
- 长上下文窗口是否会取代 RAG？
- RAG 系统的评估指标有哪些？
- RAG 的优势和局限性是什么？
- 什么场景适合用 RAG？什么场景不适合？

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/rag-interview-questions.md#L17)，来源许可：Apache-2.0。

<a id="kb9023081a54c"></a>

## RAG 常见失败模式有哪些？

- 解析失败：表格、公式、代码、页眉页脚或 OCR 文本处理错误；
- 切块不合理：关键证据被切散，或者 chunk 过大混入多个主题；
- 召回缺失：正确文档没有被检索出来；
- 排序错误：正确文档排在后面，被截断或未进入上下文；
- 噪声过多：无关上下文干扰生成；
- 忠实性不足：模型加入检索内容没有的信息；
- 引用错误：引用位置不支持答案；
- 过度回答：资料不足时仍然编造结论。

<a id="evaluation-section-45-question-02"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/06_%E6%A8%A1%E5%9E%8B%E8%AF%84%E4%BC%B0%EF%BC%9A%E5%A4%9A%E7%BB%B4%E8%AF%84%E4%BC%B0%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B.md#L665)，来源许可：GPL-3.0。

<a id="k4c15a318ff81"></a>

## RAG 延迟高时怎么优化？流式输出能不能真正降低处理耗时？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

先用 trace 拆分查询改写、Embedding、检索、重排、上下文组装、模型首 Token 和完整生成耗时，再优化占比最大的瓶颈。可并行双路召回、减少无效模型步骤、批处理重排、控制候选与上下文长度，并按身份及版本缓存。

流式输出通常改善首字可见时间和感知等待，不会自动缩短检索、重排或完整生成耗时；若模型必须等证据齐全才开始输出，前置阶段仍在关键路径上。不能为抢首字先编造结论，等证据回来再改口。

同时报告 TTFT、端到端 P50/P95、超时率、Token 与成功率。查询向量缓存适合相同模型和预处理版本；答案缓存还需用户权限、文档版本和失效规则。降低 TopK、换小模型或减少重排候选后，必须复测证据覆盖和答案质量。

**用关键路径解释延迟。** 假设两路召回分别耗时 40 ms 和 70 ms，并行召回阶段约取两者最大值，再加合并开销；随后重排 100 ms、上下文组装 10 ms，则到生成开始前约需 180 ms 加上未计入的排队与调度成本。这只是教学算例，不能当作任何项目实测值。

真实请求的 P95 不能简单由各阶段 P95 相加得到：排队、长文本、重试和模型负载可能相关。应在同一条 trace 上记录阶段跨度，再统计整条链路的分布。流式输出改善首个可见结果的等待时间；若证据还没准备好就提前生成，可能引入撤回或重写，不能只为了更短的首字延迟破坏答案一致性。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L430)，来源许可：GPL-3.0。

<a id="k9cf616b07cb7"></a>

## RAG 文档块表怎么设计？为什么要保存原文、元数据、向量和全文检索字段？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

文档块表同时服务召回、生成、引用、更新和授权。原文用于回答与引用，向量用于语义召回，全文字段用于词法匹配，元数据关联文档结构、版本、租户与权限。只存向量无法还原证据，也难以处理删除和审计。

```sql
CREATE TABLE chunks (
    chunk_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id text NOT NULL,
    doc_id text NOT NULL,
    doc_version integer NOT NULL,
    chunk_index integer NOT NULL,
    parent_id text,
    content text NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    visibility text NOT NULL,
    is_active boolean NOT NULL DEFAULT true,
    embedding_model text NOT NULL,
    embedding vector(3),
    fts tsvector NOT NULL,
    UNIQUE (tenant_id, doc_id, doc_version, chunk_index)
);
```

这是需要先安装 pgvector 扩展的教学表，`vector(3)` 只示意维度，实际应与 Embedding 模型一致。完整系统还需文档表、成员/ACL 关系、时间字段、内容哈希及事务更新策略；`visibility` 一个字段不足以表达企业权限。

把模型版本、分词版本和文档版本纳入重建流程，写入成功与索引可查之间的延迟要可观测。关键过滤字段宜用有类型的列和索引，不能把所有字段塞入 JSON 后再假定性能不会下降。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L355)，来源许可：GPL-3.0。

<a id="k641ad3d9905c"></a>

## RAG 文档处理流程包括哪些步骤？

**难度评分：⭐⭐⭐ (3/5) | 考察频率：⭐⭐⭐⭐⭐ (5/5)**

1. **文档采集**：从文件系统、对象存储、网页、数据库、知识库或代码仓库获取数据。
2. **格式解析**：解析 PDF、Word、HTML、Markdown、Excel、代码文件等。
3. **文本清洗**：去除页眉页脚、目录噪声、重复内容、乱码和无意义符号。
4. **结构恢复**：保留标题、章节、表格、列表、代码块等结构。
5. **分块**：切成适合检索和生成的 chunk。
6. **metadata 标注**：记录来源、标题、页码、章节、权限、时间等。
7. **向量化与入库**：生成 embedding 并存入向量库或搜索引擎。

<a id="prompting-section-35-question-02"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/05_%E6%8F%90%E7%A4%BA%E5%B7%A5%E7%A8%8B%EF%BC%9A%E5%BA%94%E7%94%A8%E5%A4%A7%E6%A8%A1%E5%9E%8B%E7%9A%84%E9%AB%98%E7%BA%A7%E6%96%B9%E6%B3%95.md#L700)，来源许可：GPL-3.0。

<a id="k7b9372e097dd"></a>

## RAG 检索优化

相关内容：[《RAG 优化：从召回、重排到上下文工程》](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/rag/rag-optimization.md)

检索优化题要先区分召回、排序、上下文和生成问题。Hybrid Search、Query Rewrite、Rerank 和上下文压缩处理的故障位置不同，不能用同一个手段解决所有失败样本。

常见面试题：

- RAG 召回率低应该怎么排查？
- Chunk 策略、Metadata、Hybrid Search、Query Rewrite、Rerank 分别解决什么问题？
- Hybrid Search 是什么？BM25 和向量检索怎么融合？
- Query Rewrite、HyDE、Self-Query 分别适合什么场景？
- Rerank 解决什么问题？为什么不能只依赖向量相似度排序？
- 上下文压缩有什么价值？什么时候会伤害答案质量？
- RAG 优化为什么必须先建立失败样本集？
- 线上 RAG 出现“答非所问”，应该按什么路径定位？

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/rag-interview-questions.md#L73)，来源许可：Apache-2.0。

<a id="k93ac337d9311"></a>

## rag 流程，具体内容，rerank 机制

**回答：**

<a id="tencent-llm-collection-20260903-q56"></a>

**相关解释：** [agent 调用工具这个过程是怎么优化的？](Agent%E3%80%81%E5%B7%A5%E5%85%B7%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81-01.md#k98cb3547adb1)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L912)，来源许可：GPL-3.0。

<a id="kcf7c4c464d07"></a>

## RAG 的运行过程；检索有哪些类型

**回答：**

RAG 将外部检索与生成结合：先找到与问题有关且有权访问的证据，再让模型基于证据回答。它通常分为离线数据准备和在线请求两条链路。

离线链路是文档接入、解析与清洗、结构化切分、元数据与权限绑定、Embedding 或其他索引构建、验证与发布。每个片段保留文档 ID、版本、标题路径和位置，便于更新、撤回和引用。上传完成不等于索引已经可用，查询应使用完整就绪的数据快照。

在线链路是身份与范围校验、问题理解或按需改写、检索候选、融合与重排、证据去重及上下文补全、模型生成、引用和结果校验。问题改写与多路召回是可选策略；简单精确问题不必经过过多模型步骤。未找到证据时应扩大授权范围内的搜索策略或明确无法确认，不能把没有召回解释为事实不存在。

常见检索方式包括：关键词与 BM25 等稀疏检索，适合专有名词、编号和精确匹配；向量稠密检索，适合语义相近但措辞不同的内容；混合检索，结合两者并通过排名融合或重排整合；结构化条件检索，按日期、版本和字段筛选；图检索，沿明确关系展开多跳证据。元数据过滤通常是检索范围控制，不必把它当成独立的语义匹配算法。

缓存应区分问题向量、候选、重排和最终答案，键与失效策略包含权限范围、知识版本及必要模型配置。召回截断也要分层：候选 Top-K 服务于重排，最终证据集服务于生成；两者不能用同一个很小的 K 代替。相关片段可能分散在多个章节，完整比较任务更不能只依赖 Top-K 来保证穷尽覆盖。

<a id="alibaba-taotian-ai-app-20261020-942091198347345920-q05"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L2435)，来源许可：GPL-3.0。

<a id="k47c05f1ff2e3"></a>

## RAG 系统上线性能表现，解决哪些业务问题，如何评估效果

**回答：**

<a id="tencent-llm-collection-20260903-q45"></a>

**相关解释：** [rag 召回率 90%，badcase 都是什么问题，具体是哪个环节导致的？有想过怎么优化吗？](RAG%E4%B8%8E%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA-01.md#k2fa767805bfd)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L803)，来源许可：GPL-3.0。

<a id="kd8b67d6b8ce8"></a>

## RAG 系统有哪些核心组件？

| 组件 | 作用 |
| --- | --- |
| 文档加载器 | 从 PDF、Word、网页、数据库、代码仓库等来源读取数据 |
| 解析清洗模块 | 去除噪声、恢复结构、处理表格和乱码 |
| 文本分块器 | 将长文档切成适合检索和上下文拼接的 chunk |
| Embedding 模型 | 将文本转成向量表示 |
| 向量数据库或搜索引擎 | 存储向量、文本和 metadata，支持检索 |
| 检索器 | 根据 query 找到候选文档片段 |
| 重排序器 | 对候选片段进行更精细的相关性排序 |
| 上下文构造器 | 选择、压缩和拼接上下文 |
| 生成模型 | 基于问题和上下文生成答案 |
| 引用与日志模块 | 输出来源、记录链路、支持评估和诊断 |

**RAG 的上限由知识库质量和检索链路决定，下限由提示约束和答案生成策略决定。**

<a id="prompting-section-34-question-04"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/05_%E6%8F%90%E7%A4%BA%E5%B7%A5%E7%A8%8B%EF%BC%9A%E5%BA%94%E7%94%A8%E5%A4%A7%E6%A8%A1%E5%9E%8B%E7%9A%84%E9%AB%98%E7%BA%A7%E6%96%B9%E6%B3%95.md#L591)，来源许可：GPL-3.0。

<a id="k92ee8bf17ad8"></a>

## RAG 系统的核心数学不只是余弦相似度吗？

RAG 的数学包括向量表示、相似度检索、稀疏词项匹配、召回融合、排序学习、上下文选择、答案忠实性评估等。余弦相似度只是 dense retrieval 的一个基础组件。

RAG 可以抽象为：

$$
z = \text{Retrieve}(q,\mathcal{D})
$$

$$
y \sim p_{\theta}(y|q,z)
$$

其中 $q$ 是问题，$\mathcal{D}$ 是文档库，$z$ 是检索上下文。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E6%95%B0%E5%AD%A6%26%E7%89%A9%E7%90%86%E6%9C%AC%E8%B4%A8%E5%8E%9F%E7%90%86%E5%9F%BA%E7%A1%80/03_%E5%A4%A7%E6%A8%A1%E5%9E%8B%E4%B8%8E%E5%A4%9A%E6%A8%A1%E6%80%81%E6%9C%80%E6%96%B0%E6%95%B0%E5%AD%A6%E4%B8%93%E9%A2%98.md#L572)，来源许可：GPL-3.0。

<a id="k87e895d7e8b2"></a>

## RAG 能缓解哪些问题？

- **知识过时**：通过更新知识库和索引接入新信息；
- **私有知识缺失**：接入企业文档、内部规范、数据库和业务系统；
- **不可追溯**：通过引用来源说明答案依据；
- **幻觉风险**：让模型基于检索证据回答，而不是完全依赖参数记忆。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/05_%E6%8F%90%E7%A4%BA%E5%B7%A5%E7%A8%8B%EF%BC%9A%E5%BA%94%E7%94%A8%E5%A4%A7%E6%A8%A1%E5%9E%8B%E7%9A%84%E9%AB%98%E7%BA%A7%E6%96%B9%E6%B3%95.md#L563)，来源许可：GPL-3.0。

<a id="k1ccccb110a62"></a>

## RAG 评估中的 Recall@k、MRR、nDCG、Faithfulness 如何理解？

Recall@k：

$$
\text{Recall@k}=\frac{\text{top-k 中相关文档数}}{\text{所有相关文档数}}
$$

衡量召回是否把相关材料找出来。

MRR：

$$
\text{MRR}=\frac{1}{N}\sum_{i=1}^{N}\frac{1}{\text{rank}_i}
$$

其中 $\text{rank}_i$ 是第一个相关结果的位置。

nDCG 考虑相关性等级和排序位置：

$$
\text{DCG@k}=\sum_{i=1}^{k}\frac{rel_i}{\log_2(i+1)}
$$

$$
\text{nDCG@k}=\frac{\text{DCG@k}}{\text{IDCG@k}}
$$

Faithfulness 衡量答案是否被检索上下文支持。它不是纯检索指标，而是生成答案的忠实性指标。

**RAG 评估要分层：**

- 检索层：Recall@k、MRR、nDCG。
- 上下文层：context precision、context relevance。
- 生成层：faithfulness、answer correctness、citation accuracy。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E6%95%B0%E5%AD%A6%26%E7%89%A9%E7%90%86%E6%9C%AC%E8%B4%A8%E5%8E%9F%E7%90%86%E5%9F%BA%E7%A1%80/03_%E5%A4%A7%E6%A8%A1%E5%9E%8B%E4%B8%8E%E5%A4%9A%E6%A8%A1%E6%80%81%E6%9C%80%E6%96%B0%E6%95%B0%E5%AD%A6%E4%B8%93%E9%A2%98.md#L681)，来源许可：GPL-3.0。

<a id="keb6d249bc97b"></a>

## RAG 评估为什么要拆层？

AG 评估至少包括：

- **文档与索引评估**：文档是否被正确解析、清洗、切分，metadata 和权限信息是否保留。
- **检索评估**：相关文档是否被召回，排序是否合理，chunk 是否包含关键证据。
- **生成评估**：答案是否正确、相关、完整，并忠实于检索内容。
- **引用评估**：引用是否真实存在，是否支持对应结论。
- **拒答评估**：知识库没有答案或权限不足时，模型是否拒答、澄清或说明不确定。
- **端到端业务评估**：用户问题是否被解决，延迟、成本、满意度和人工接管率是否可接受。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/06_%E6%A8%A1%E5%9E%8B%E8%AF%84%E4%BC%B0%EF%BC%9A%E5%A4%9A%E7%BB%B4%E8%AF%84%E4%BC%B0%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B.md#L654)，来源许可：GPL-3.0。

<a id="kdb7109653c92"></a>

## RAG 长尾商品问题：在搜索场景中，RAG 的向量检索容易受到长尾商品的影响，

**回答：**

这条题干在“影响，”处结束，没有完整给出问题要求，不能补造后半句。对已明确的“RAG 向量检索与长尾商品”主题，可以给出以下分析；如果关注点另有侧重，应先补全约束再选方案。

长尾商品可能因描述少、训练曝光低、语义过于接近热门商品而漏召回，也可能因属性缺失被错误召回。先按商品频次与类目切分统计 Recall@k、候选覆盖和误召回，区分数据缺失、向量表示、索引近似误差和重排偏置。

可结合关键词与属性精确检索、语义召回、目录约束和难负例训练，提高可行候选覆盖。探索流量或长尾配额需要业务依据，不能只为平均曝光而牺牲相关性。最终还要经过库存、权限和时效校验。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E4%BA%AC%E4%B8%9C%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1423)，来源许可：GPL-3.0。

<a id="k44ef897e41fd"></a>

## RAG 项目中文本分块有哪些策略？不同策略适合什么场景？

**难度评分：⭐⭐⭐ (3/5) | 考察频率：⭐⭐⭐⭐⭐ (5/5)**

| 分块策略 | 思路 | 适合场景 |
| --- | --- | --- |
| 固定长度分块 | 按字符或 token 数切分 | 快速基线、结构弱文本 |
| 段落分块 | 按自然段切分 | 普通文档、说明文本 |
| 标题/章节分块 | 按文档层级切分 | 手册、制度、论文 |
| 递归字符分块 | 按标题、段落、句子等优先级递归切分 | 通用文本处理 |
| 语义分块 | 按语义相似度或主题边界切分 | 长文章、主题变化明显文本 |
| 滑动窗口分块 | 相邻 chunk 保留重叠 | 避免边界信息丢失 |
| 父子分块 | 小块检索，大块返回 | 兼顾召回精度和上下文完整性 |
| 代码结构分块 | 按函数、类、模块切分 | 代码库问答 |

<a id="prompting-section-35-question-03"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/05_%E6%8F%90%E7%A4%BA%E5%B7%A5%E7%A8%8B%EF%BC%9A%E5%BA%94%E7%94%A8%E5%A4%A7%E6%A8%A1%E5%9E%8B%E7%9A%84%E9%AB%98%E7%BA%A7%E6%96%B9%E6%B3%95.md#L713)，来源许可：GPL-3.0。

<a id="kbf105e3c9d08"></a>

## RAG、Memory、Context 和 State 怎么区分？

这四个概念经常在项目介绍里混在一起。

下面采用的是本文在售后项目里的工程口径，不是所有框架都统一遵守的一套类型定义。

| 概念    | 在售后案例中的内容                               | 主要回答的问题               |
| ------- | ------------------------------------------------ | ---------------------------- |
| RAG     | 售后政策、产品手册、服务网点资料                 | 外部知识里有哪些相关证据？   |
| Memory  | 用户偏好、经过确认且允许长期保留的信息           | 跨轮次或跨会话需要记住什么？ |
| Context | 本轮实际发给模型的指令、证据、工具和历史         | 模型这一次能看到什么？       |
| State   | 当前订单、缺失字段、审批状态、已执行动作、工单号 | 任务现在进行到哪一步？       |

短期 Memory 在一些框架里本来就是 Agent State 的一部分，Checkpoint 也可能保存某个时刻的 State。名称会变，但边界不能混：Memory、Agent State 和工作流 Checkpoint 都不能代替权威业务数据库。把“工单是否已创建”只保存在对话历史里，是很危险的设计。

详细原理可以分别看 [上下文工程实战指南](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/agent/context-engineering.md) 和 [AI Agent 记忆系统详解](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/agent/agent-memory.md)。

项目里如果真的用了长期 Memory，还要能回答哪些信息允许写入、来源由谁确认、保存多久、用户怎样查看和删除，以及恶意内容写入后如何清理。只保存了几轮 Chat History，就按会话历史来讲，不要包装成完整的长期记忆系统。

RAG 部分也不能停在“接了向量数据库”。至少准备好文档怎么解析和切块、索引如何更新、向量与关键词怎样召回、是否使用 Reranker、Top-K 怎么定、ACL 在哪里生效，以及引用与知识版本如何回放。评测时把检索命中和最终回答分开看，不然很难判断问题出在召回还是生成。

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md#L194)，来源许可：Apache-2.0。

<a id="k694885a763bf"></a>

## RAG、传统检索+生成、微调三种方案的本质区别是什么？分别在什么场景下选用。

**回答：**

先澄清分类口径：**RAG 是检索增强生成；“传统检索 + 生成”只要把检索到的外部证据用于生成，也属于广义 RAG。** 用向量检索还是 BM25，是检索组件的选择，并不是是否属于 RAG 的分界。工程上也不要求 RAG 一定联合训练检索器与生成器。

| 方案 | 改变什么 | 优先适用的场景 |
|---|---|---|
| 稀疏检索 + 生成 | 通过词项、倒排索引等取得上下文证据 | 产品代码、专有名词、条款编号与精确词匹配 |
| 稠密/混合检索增强生成 | 利用语义向量及词项信号召回，再重排和组织证据 | 表述差异较大、知识经常更新、需要权限控制与可引用证据 |
| 微调 | 通过训练改变参数或适配器，调整行为分布 | 稳定任务模式、领域表达、工具选择、格式遵循与分类能力适配 |

RAG 的关键依赖是语料质量、索引新鲜度、权限、召回和上下文利用；微调依赖训练数据、目标和可验证泛化，知识更新也不如修改外部库直接。微调可以影响模型知识与行为，但不能作为精确可更新事实库的通用替代。

选择时先明确失败类型：缺少新事实或需要出处，优先外部检索；拿到正确材料仍不遵循规则，评估提示、解码、模型能力和微调；短小且稳定的分类或抽取，也可能只需一个任务模型。RAG 与微调可以组合，例如微调检索器、重排器或生成器，而不是互斥三选一。

金融制度类问题还应保留版本、生效时间与适用范围。检索到错误版本后生成得再流畅也不正确，训练时记住某条旧规则同样不能保证当前可用。

<a id="hengsheng-ai-dev-20260923-q13"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E6%81%92%E7%94%9F%E7%94%B5%E5%AD%90%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L255)，来源许可：GPL-3.0。

<a id="ka4367174d775"></a>

## RAG、多模态 Agent 和工具调用如何复用经典 NLP 模型思想？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

RAG 复用的 NLP 思想：

- 信息检索。
- 语义向量。
- 问答系统。
- 摘要和生成。
- 知识图谱和实体关系。

多模态 Agent 复用的模型思想：

- Attention：对不同模态和工具结果动态加权。
- Seq2Seq：从任务输入生成行动序列。
- RL：根据反馈优化策略。
- 迁移学习：把预训练模型适配到具体工具和业务。

工具调用：

- 函数名、参数、返回值可以看作结构化语言。
- LLM 生成工具调用类似生成程序或动作序列。
- 检索、OCR、检测、分割、代码执行都可以成为工具。

总结：AIGC Agent 不是脱离经典 NLP 的新物种，而是把语言建模、检索、问答、规划和强化学习组合成可行动系统。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BB%8F%E5%85%B8%E6%A8%A1%E5%9E%8B/%E8%87%AA%E7%84%B6%E8%AF%AD%E8%A8%80%E5%A4%84%E7%90%86%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L524)，来源许可：GPL-3.0。

<a id="k864ad8b85782"></a>

## RAG检索时，召回的具体是什么内容？

**回答：**

召回的通常是能够作为证据的文档单元，如段落、条款、表格片段或页面区域，而不是只把向量交给大模型。向量用于计算相似度，检索结果需要包含可读内容和可追溯元数据。

一条结果可以包含 chunk_id、doc_id、version_id、标题路径、页码或字符区间、正文、检索分数以及必要的父块标识。表格还需要表头和行列关系；扫描文档可以携带 OCR 文本与对应图像区域引用。权限相关标识用于服务端校验，不代表必须全部传入模型。

召回粒度与最终上下文粒度可以不同：先用较小块定位，再补充同一授权版本内的父段落或相邻条款。证据扩展后仍要保留位置映射，避免模型给出无法跳转或混淆版本的引用。

<a id="sftech-ai-dev-20261019-463a64c7-g3-q03"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%A1%BA%E4%B8%B0%E7%A7%91%E6%8A%80%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L224)，来源许可：GPL-3.0。

<a id="kb8c1ca0f27f9"></a>

## RAG系统从文档进入到最终生成答案的完整流程是什么？离线知识库构建和在线检索阶段分别包含哪些步骤？

**回答：**

离线阶段先处理数据质量，而不是直接切片：采集文档，解析 PDF/HTML/Office 等格式，保留标题、段落、表格、代码和页码等结构；清洗重复、导航、乱码和无效内容；按章节、语义或布局切分，并为每个 Chunk 写入文档 ID、标题路径、页码、权限、版本和时间等元数据。然后使用与查询同分布的 Embedding 生成向量，建立向量索引，同时为关键词检索建立倒排索引；必要时生成父文档关系、摘要或实体索引。

在线阶段通常是：

1. 识别问题类型、权限和过滤条件；
2. 做 Query Rewrite、查询扩展、语言归一化或拆分多跳问题；
3. 并行执行稠密向量召回、BM25/倒排召回、结构化过滤和必要的父文档召回；
4. 合并候选集并去重，使用 RRF、加权分数或学习排序融合；
5. 通过 Cross-Encoder 或 LLM Reranker 对候选 Chunk 重排，并根据上下文预算截断；
6. 把证据、来源和不确定性注入 Context，要求模型只基于证据回答，证据不足时拒答或澄清；
7. 对答案做引用、事实一致性、权限和格式校验，记录检索与生成 Trace。

评测要拆开看：检索侧看 Recall@K、MRR、nDCG、证据覆盖率和权限过滤正确率；生成侧看答案正确性、忠实度、引用准确率、拒答准确率、延迟和成本。RAG 不是“向量库 + Prompt”，而是一条从数据治理到答案验收的系统链路。

<a id="bilibili-ai-agent-20260818-q7"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%93%94%E5%93%A9%E5%93%94%E5%93%A9%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L116)，来源许可：GPL-3.0。

<a id="k0cccf3a8f12c"></a>

## Rerank 后的 TopK 截断是怎么做的？为什么是这个值？有没有其他截断方案？

**回答：**

最简单的 TopK 截断是按 rerank 分数从高到低排序，取前 K 个候选进入上下文。例如粗召回 50 个，rerank 后取 top5。这个 K 的选择要由验证集、token budget、延迟和噪声共同决定，而不是只靠经验。

为什么可能选择 top5？因为在很多知识库问答场景中，一个问题通常只需要 1 到 3 个核心证据，再加少量补充上下文。top5 能覆盖大部分必要证据，同时不会引入过多噪声。更大的 K 会增加 token 成本和上下文干扰，模型可能在多个相似但不一致的片段之间摇摆。

除了固定 topK，还有几种更稳的截断方案。第一是分数阈值截断，只保留 rerank score 高于阈值的 chunk，适合无答案拒答，但阈值要校准。第二是相对阈值截断，例如只保留分数不低于 top1 分数一定比例的候选。第三是 token budget 截断，按分数从高到低加入，直到达到上下文预算。第四是 MMR 多样性截断，在相关性和多样性之间折中，避免返回 5 个几乎重复的 chunk。第五是按 parent 聚合截断，先合并同一父文档下的 child，再限制每个 parent 的候选数量。第六是动态 K，根据 query 类型决定，简单事实题少取，复杂综合题多取。

工程上更推荐“固定 topK baseline + 阈值 + token budget + 去重”的组合。这样既有稳定上限，又能在低置信度问题上减少噪声。

<a id="bytedance-ai-agent-hard-20260602-q6"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L439)，来源许可：GPL-3.0。

<a id="k77eaca3aa808"></a>

## Rerank 后返回几个块（Chunk）？有没有针对这个返回数量做过验证？

**回答：**

Rerank 后返回几个 chunk 不能只凭经验固定，应该由三个约束共同决定：答案所需证据量、模型上下文窗口和噪声控制。实际项目里常见的最终入模数量是 3 到 8 个 chunk。如果 chunk 较长或 parent 较大，可能只返回 3 到 5 个；如果 chunk 较短、问题需要多证据综合，可能返回 6 到 10 个。

验证方式应该是离线评测加线上观察。离线可以构建一批 query-answer-evidence 标注集，分别测试 top3、top5、top8、top10 的效果，看 recall@k、faithfulness、answer accuracy、引用命中率、无答案拒答率和平均 token 成本。线上可以看用户满意度、追问率、人工质检通过率、延迟和成本。

通常会出现一个拐点：topK 从 1 增加到 3 或 5 时，答案质量明显提升；继续增加到 10 或 15 后，召回证据更多，但噪声也更多，模型更容易被无关内容干扰，延迟和成本也上升。因此返回数量要通过实验找到质量、成本和延迟的平衡点。

面试里可以给一个具体但不绝对的说法：我会先用 rerank top5 作为 baseline，然后通过评测比较 top3、top5、top8。若问题是事实型或单文档问答，top3 到 top5 往往足够；若是综合型问题，可能增加到 top8，并配合去重、parent 合并和引用约束。

<a id="bytedance-ai-agent-hard-20260602-q5"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L426)，来源许可：GPL-3.0。

<a id="k9c01f995333a"></a>

## Rerank、Cross-Encoder、Late Interaction 的数学差异是什么？

Bi-Encoder 独立编码 query 和 doc：

$$
s(q,d)=f(q)^Tg(d)
$$

优点是可提前建索引，适合大规模召回；缺点是交互较弱。

Cross-Encoder 把 query 和 doc 拼接后共同编码：

$$
s(q,d)=h_{\theta}([q;d])
$$

它能建模细粒度 token 交互，排序质量更高，但不能提前为 doc 计算固定向量，成本高。

Late Interaction 介于两者之间。以 ColBERT 风格为例，query token 向量 $q_i$ 与 doc token 向量 $d_j$ 做最大相似度聚合：

$$
s(q,d)=\sum_i \max_j q_i^Td_j
$$

**RAG 实践常见流程：**

1. Bi-Encoder / BM25 / Hybrid 做高召回。
2. Cross-Encoder 或 Late Interaction 做 rerank。
3. 选择 top chunks 进入上下文。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E6%95%B0%E5%AD%A6%26%E7%89%A9%E7%90%86%E6%9C%AC%E8%B4%A8%E5%8E%9F%E7%90%86%E5%9F%BA%E7%A1%80/03_%E5%A4%A7%E6%A8%A1%E5%9E%8B%E4%B8%8E%E5%A4%9A%E6%A8%A1%E6%80%81%E6%9C%80%E6%96%B0%E6%95%B0%E5%AD%A6%E4%B8%93%E9%A2%98.md#L626)，来源许可：GPL-3.0。

<a id="k8496afd381d0"></a>

## Rerank的Top-k数量怎么确定？

<a id="batch4-p1-q3"></a>

### 补充说明

<a id="batch4-p2-q9"></a>

**相关解释：** [Embedding模型与Reranker差异，二者训练Loss区别](RAG%E4%B8%8E%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA-01.md#k1abf61aa73cc)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%BF%AB%E6%89%8B%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L157)，来源许可：GPL-3.0。
- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%BF%AB%E6%89%8B%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L282)，来源许可：GPL-3.0。

<a id="k46500b6b6373"></a>

## RRF 是什么？为什么不直接把向量分数和全文检索分数相加？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

RRF（Reciprocal Rank Fusion）按各检索列表中的名次融合候选，避免直接混合量纲不同的原始分值。对候选 d，可定义：

```math
\mathrm{RRF}(d)=\sum_{j:d\in L_j}\frac{w_j}{c+\mathrm{rank}_j(d)}.
```
名次从 1 开始，未出现在某一路的候选在该路贡献为零，c 为平滑常数，w 为可选权重。常见的 c=60 只是经验设置，并非普适最优值。c 较大时高低名次差异被压缩，权重也应通过验证集调整。

向量距离通常越小越好，全文 rank 通常越大越好，而且分布随查询变化，直接相加既可能方向错，也可能被某一路数值范围支配。经过校准的加权分数也可使用，但必须解释校准方法。融合前在每一路按文档块标识去重，保持稳定的并列排序，防止重复条目虚增投票。

**一个可直接运行的等权 RRF 实现。** 下面只处理已经按相关性排序的字符串块 ID。每一路先去重，再从 1 开始计数；同分时按 ID 排序，保证重放稳定。教学实现采用等权融合，不读取原始相似度分数。

```python
from collections import defaultdict
import math


def rrf(rankings, c=60.0):
    if isinstance(c, bool) or not isinstance(c, (int, float)):
        raise ValueError("c must be a finite nonnegative number")
    try:
        c = float(c)
    except OverflowError as exc:
        raise ValueError("c is too large") from exc
    if not math.isfinite(c) or c < 0:
        raise ValueError("c must be finite and nonnegative")
    scores = defaultdict(float)
    for ranking in rankings:
        if isinstance(ranking, (str, bytes)):
            raise ValueError("each ranking must contain document IDs")
        seen = set()
        rank = 0
        for doc_id in ranking:
            if not isinstance(doc_id, str) or not doc_id:
                raise ValueError("document IDs must be nonempty strings")
            if doc_id in seen:
                continue
            seen.add(doc_id)
            rank += 1
            scores[doc_id] += 1.0 / (c + rank)
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))
```

例如 `rrf([["A", "B", "B"], ["B", "C"]])` 中，B 得到两路有效投票，不会因为第一路重复出现而额外加分；A 在第一路排第 1，C 在第二路排第 2，所以 A 排在 C 前；若两个候选的累计浮点分值完全相同，再用 ID 打破平局。浮点运算可能让数学上极接近的分值出现微小误差，稳定排序不等于消除数值误差。

设输入列表元素总数为 N、候选并集大小为 U，累计开销约为 O(N)，完整排序为 O(U log U)，额外存储为 O(U)。只需前 K 个时可以使用堆减少排序开销，但多数检索流水线应先测重排和网络耗时，再判断融合是否值得优化。这里没有实现 ACL；调用前必须完成相应候选与数据访问控制。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L277)，来源许可：GPL-3.0。

<a id="kcf6efd005e7a"></a>

## Stay Updated with Generative AI, LLMs, Agents and RAG.

Join 🚀 [**AIxFunda** free newsletter](https://aixfunda.substack.com/) to get *latest updates* and *interesting tutorials* related to Generative AI, LLMs, Agents and RAG. 
- ✨ Weekly GenAI updates
- 📄 Weekly LLM, Agents and RAG paper updates
- 📝 1 fresh blog post on an interesting topic every week

### 参考资料

- [KalyanKS-NLP/LLM-Interview-Questions-and-Answers-Hub](https://github.com/KalyanKS-NLP/LLM-Interview-Questions-and-Answers-Hub/blob/280c8b642acd65006b11aad76633826a867f3a63/README.md#L5)，来源许可：Apache-2.0。

<a id="kbcae76e61c4e"></a>

## Token Embedding 是什么？

设词表大小为 $`V`$，隐藏维度为 $`d`$，模型维护一个可训练矩阵：

```math
E \in \mathbb{R}^{V \times d}
```

Token ID $`i`$ 的输入向量就是第 $`i`$ 行 $`E_i`$。实现上是一次查表。

Token Embedding 是**静态起点**：在同一个模型中，同一个 Token ID 查到的初始向量相同。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/02_%E6%A8%A1%E5%9E%8B%E6%9E%B6%E6%9E%84%E4%B8%8E%E5%B7%A5%E4%BD%9C%E5%8E%9F%E7%90%86.md#L169)，来源许可：GPL-3.0。

<a id="k0a25332f0f3d"></a>

## ts_rank 和 ts_rank_cd 在检索中起什么作用？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐ (3/5)**

`ts_rank` 根据匹配词项频率、权重等信息计算相关性；`ts_rank_cd` 采用 cover density 思路，进一步考虑匹配词项之间的位置接近程度。它们用于匹配候选排序，不负责向量语义理解，也不是可直接解释为答案正确率的概率。

`ts_rank_cd` 需要位置数据；被 `strip` 去掉位置的词项无法正常贡献其位置相关计算。标题权重、词项频率、查询结构和归一化选项都会影响分值，因此不能拿另一套索引的绝对分数直接套阈值。

若短语或邻近关系重要，可测试 `ts_rank_cd`；若只是代码、编号精确匹配，可能应另设精确优先规则。用真实查询比较排序指标及错误案例。PostgreSQL 内置 rank 不应未经说明就被称为标准 BM25。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L267)，来源许可：GPL-3.0。

<a id="k9611f09f473d"></a>

## 一般情况下什么操作会导致召回的东西有问题？

**回答：**

召回异常常见原因包括文档解析丢表格/跨页关系、切分破坏语义、Embedding 不适配领域、BM25 分词错误、过滤条件或权限错误、索引未刷新、版本混用、query 改写偏义、TopK/阈值不合理、Rerank 截断和上下文拼装重复。

研发负责解析、索引、检索、版本、监控和回归；产品/运营维护业务知识时，应提供结构化录入模板、必填适用范围、生效时间、审批、版本和预览检索能力。发布前做自动解析质量检查、离线评测和灰度，不能让业务人员直接修改线上索引而没有审计。

<a id="tencent-llm-collection-20260903-q71"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1049)，来源许可：GPL-3.0。

<a id="k53de65d00fab"></a>

## 为什么 KDA 能提升检索能力？

令状态对当前 key 的预测尽量接近目标 value：

$$
\mathcal{L}_t(S)=\tfrac{1}{2}\left\lVert S^\top k_t-v_t\right\rVert_2^2
$$

对 $S$ 求梯度并在 $S_{t-1}$ 处走一步（步长为 $\beta_t$）：

$$
\nabla_S\mathcal{L}_t=k_t\left(k_t^\top S_{t-1}-v_t^\top\right)
$$

$$
S_t=S_{t-1}-\beta_t\,k_t\left(k_t^\top S_{t-1}-v_t^\top\right)
=\bigl(I-\beta_t k_t k_t^\top\bigr)S_{t-1}+\beta_t k_t v_t^\top
$$

$I-\beta_t k_tk_t^\top$ **只擦除"沿 $k_t$ 方向的旧映射"**，其余方向原样保留，随后再写入新关联 $k_tv_t^\top$：

- $\lVert k_t\rVert=1,\ \beta_t\in(0,1)$ ： $1-\beta_t\in(0,1)$ ，是**收缩式擦除**；
- $\beta_t\lVert k_t\rVert^2>2$ ：特征值 $<-1$，退化为**放大/振荡**，擦除不再稳定。

<a id="sota-section-49"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/%E8%A1%A5%E5%85%85%E8%B5%84%E6%96%99%EF%BC%9ASOTA%E6%A8%A1%E5%9E%8B%E5%88%86%E6%9E%90.md#L159)，来源许可：GPL-3.0。

<a id="k248deb4b1578"></a>

## 为什么只做 Token Embedding 不够？

自注意力（Self-Attention）的核心计算只比较向量内容。如果没有位置信息，它对输入排列缺少足够区分能力，“我打他”和“他打我”包含相似 Token 集合，却有不同语义。位置机制要告诉模型：**Token 在哪里，以及两个 Token 相距多远**。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/02_%E6%A8%A1%E5%9E%8B%E6%9E%B6%E6%9E%84%E4%B8%8E%E5%B7%A5%E4%BD%9C%E5%8E%9F%E7%90%86.md#L209)，来源许可：GPL-3.0。

<a id="kdf6bb2355495"></a>

## 为什么在初筛召回之后，还要加一个Rerank模型？它能解决向量搜索的哪些局限？

<a id="batch4-p1-q9"></a>

**相关解释：** [Embedding模型与Reranker差异，二者训练Loss区别](RAG%E4%B8%8E%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA-01.md#k1abf61aa73cc)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L230)，来源许可：GPL-3.0。

<a id="k069f5d38b58c"></a>

## 为什么引入 BM25？向量检索和 BM25 的融合比例是怎样的？

**回答：**

引入 BM25 是因为向量检索和关键词检索解决的是不同问题。向量检索擅长语义相似，比如“如何降低幻觉”和“怎么防止模型乱编”能被认为相近；但它对精确实体、代码符号、错误码、产品型号、专有名词、数字、缩写、接口名不一定敏感。BM25 基于词项匹配和逆文档频率，擅长精确命中关键词，能弥补向量检索在精确匹配上的短板。

两者融合不应该拍脑袋固定比例。常见做法有两类。

第一类是分数融合。分别做 dense retrieval 和 BM25 retrieval，对两路分数做归一化，然后按权重合并，例如 `score = alpha * dense_score + (1 - alpha) * bm25_score`。alpha 可以从 0.5、0.6、0.7 等值开始网格搜索。偏语义问答时 dense 权重大一些，偏文档编号、错误码、函数名、政策条款时 BM25 权重大一些。

第二类是排名融合，最常见是 RRF。RRF 不要求不同检索器的分数可比，只根据排名融合，公式类似 `sum(1 / (k + rank_i))`。在工程上 RRF 更稳，因为向量相似度和 BM25 分数分布不同，直接线性加权容易失真。

如果面试官追问具体比例，可以回答：初始可以用 dense:BM25 = 0.6:0.4 或 0.7:0.3 做 baseline，但最终一定要通过验证集调优，指标看 recall@k、MRR、nDCG、答案正确率、引用命中率和延迟。真正上线时还可以按 query 类型动态调权：包含编号、专有名词、代码符号时提高 BM25 权重；自然语言描述较多时提高向量检索权重。

<a id="bytedance-ai-agent-hard-20260602-q3"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L390)，来源许可：GPL-3.0。

<a id="k9a996dea3b4c"></a>

## 为什么比 CLIP 全局 embedding 更强？

CLIP embedding 更偏语义，能知道“这是一个穿红裙的人”，但不擅长保存衣服纹理、局部配饰、发型边缘等空间细节。ReferenceNet 保留多尺度空间特征，因此更适合高保真角色动画。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E6%95%B0%E5%AD%97%E4%BA%BA%E5%9F%BA%E7%A1%80/02_%E5%8F%AF%E6%8E%A7%E4%BA%BA%E4%BD%93%E7%94%9F%E6%88%90%E4%B8%8E%E8%A7%92%E8%89%B2%E5%8A%A8%E7%94%BB%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L149)，来源许可：GPL-3.0。

<a id="ke49723fc9f16"></a>

## 为什么要在向量相似度检索前，对用户输入的话进行改写？

在向量相似度检索前对用户输入进行改写，目的是提升检索效果，具体原因如下：

1. 语义增强：用户查询可能简短或模糊，改写可以补全上下文，表达更清晰的语义意图。
2. 与文档风格对齐：用户用语和文档表述方式可能不同，改写有助于统一语言风格，提升嵌入相似度。
3. 避免歧义：消除查询中的多义词或口语表达，使向量更准确地表达用户真实意图。
4. 引导模型聚焦关键点：通过重构问题，引导嵌入模型关注更相关的信息，提升召回精准度。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/04-ai-algorithms/llm/llm-interview-questions.md#L321)，来源许可：GPL-3.0。

<a id="k550f1d085843"></a>

## 为什么要把检索和生成结合？

大模型擅长语言理解、推理和表达，但参数中的知识可能过时、不完整或不可追溯。检索系统擅长从外部资料中找到相关片段，但不能自然生成面向用户的完整答案。

RAG 结合二者：检索提供事实依据，生成负责理解问题、整合证据和组织语言。对于企业知识库、智能客服、论文问答、法律条款问答、代码库问答等场景，RAG 是非常常见的方案。

<a id="prompting-section-34-question-02"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/05_%E6%8F%90%E7%A4%BA%E5%B7%A5%E7%A8%8B%EF%BC%9A%E5%BA%94%E7%94%A8%E5%A4%A7%E6%A8%A1%E5%9E%8B%E7%9A%84%E9%AB%98%E7%BA%A7%E6%96%B9%E6%B3%95.md#L552)，来源许可：GPL-3.0。

<a id="k0bd356adaa04"></a>

## 为什么需要混合检索？只用向量检索会有什么问题？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

混合检索利用词法与语义的互补性，分别召回后合并候选。纯向量检索可能漏掉精确标识符、低频术语、否定条件和细粒度数值，尤其在模型没有充分学习行业词汇时；纯关键词又可能漏掉同义表达。

常见流程是并行执行向量 TopN 和全文 TopM，按稳定 chunk_id 去重，使用排名融合得到候选，再用重排模型选择证据。N、M 和最终 K 分别控制召回覆盖、重排成本和上下文规模，通常不是同一个数。

双路并不自动更好：噪声增加、索引维护和查询成本也会上升。比较向量单路、词法单路、融合、融合加重排四个基线，按专有名词、语义改写和无答案问题分组评测。某一路超时时，应明确降级策略并记录其对召回的影响。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L62)，来源许可：GPL-3.0。

<a id="kcce7d1396ca7"></a>

## 人脸 embedding 的相似度如何计算和校准？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐⭐ (5/5)**

最常用的是对 L2 归一化 embedding 计算余弦相似度：

```math
s(x,y)=\frac{x^{\mathsf T}y}{\lVert x\rVert_2\lVert y\rVert_2}
```

归一化后，余弦相似度与欧氏距离单调对应，便于向量索引和阈值部署。欧氏距离适合未归一化或需要直接度量幅值的场景；汉明距离通常用于二值哈希，不是主流深度人脸 embedding 的默认选择。

“相似度大于 0.6 就是同一人”不是通用事实。应在与线上相近的正负对验证集上绘制 ROC，按目标 FAR 选择阈值，并报告 TAR@FAR、FRR、EER；1:N 检索还要考虑库规模、Top-k 和开集拒识。阈值还应随设备、采集流程和风险等级重新校准。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BB%8F%E5%85%B8%E6%A8%A1%E5%9E%8B/%E4%BA%BA%E8%84%B8%E6%A8%A1%E5%9E%8B%E9%AB%98%E9%A2%91%E7%9F%A5%E8%AF%86%E7%82%B9.md#L153)，来源许可：GPL-3.0。

<a id="ka91e9c7190ca"></a>

## 什么是 RAG？

**检索增强生成（Retrieval-Augmented Generation, RAG）** 是将外部知识检索与大语言模型生成结合的技术路线。**系统先根据用户问题从知识库、数据库或搜索系统中检索相关内容，再把检索结果作为上下文交给大模型生成答案。**

模型不必把所有知识都记在参数里，而是在回答时动态读取外部知识，便于接入私有、最新数据和可追溯证据。

**相关解释：** [RAG 和微调的主要区别是什么？](RAG%E4%B8%8E%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA-01.md#kec13f17a23bc)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/05_%E6%8F%90%E7%A4%BA%E5%B7%A5%E7%A8%8B%EF%BC%9A%E5%BA%94%E7%94%A8%E5%A4%A7%E6%A8%A1%E5%9E%8B%E7%9A%84%E9%AB%98%E7%BA%A7%E6%96%B9%E6%B3%95.md#L544)，来源许可：GPL-3.0。

<a id="k7970bba43202"></a>

## 什么是相邻块扩展？为什么召回命中块后，还要补充前后的内容？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

相邻块扩展是在某个块命中后，沿同一文档版本内的顺序位置读取前后若干块，补充指代、条件和连续论证。它利用局部连续性，适合答案跨块或需要前文定义的内容。

扩展必须限制文档、版本、章节和权限，不能把排序上相邻但来自不同文件的块拼起来。多个命中窗口相交时先合并去重，再按 Token 预算裁剪，保留原始命中位置和引用信息。

补充内容属于证据扩展，不应伪装为又一次高相关召回。可以先重排确定种子块再扩展，或扩展后再做相关性筛选；两种顺序各有成本，需要验证。测试扩展是否提高跨块问题的证据覆盖，同时观察噪声和延迟。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L187)，来源许可：GPL-3.0。

<a id="ke1eefff5b603"></a>

## 什么是迭代检索？

**迭代检索（Iterative Retrieval）** 是根据当前检索结果和中间推理状态，继续生成新的 query 进行下一轮检索。适合单次检索无法获得完整证据的问题。

例：用户问“某产品新版本相比旧版本有哪些合规变化？”系统可能先检索新版本说明，再检索旧版本说明，最后比较差异。

![](https://raw.githubusercontent.com/WeThinkIn/AIGC-Interview-Book/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/imgs/05-12.png)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/05_%E6%8F%90%E7%A4%BA%E5%B7%A5%E7%A8%8B%EF%BC%9A%E5%BA%94%E7%94%A8%E5%A4%A7%E6%A8%A1%E5%9E%8B%E7%9A%84%E9%AB%98%E7%BA%A7%E6%96%B9%E6%B3%95.md#L907)，来源许可：GPL-3.0。

<a id="ke6a4e1dcb80b"></a>

## 什么是递归检索？

**递归检索（Recursive Retrieval）** 通常从粗粒度文档定位到细粒度内容。递归检索可以减少一次性全量检索的噪声，让系统先确定范围，再找具体证据。

例：先检索章节摘要，确定相关章节后，再检索该章节内部段落。适合层级文档、长文档和父子分块结构。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/05_%E6%8F%90%E7%A4%BA%E5%B7%A5%E7%A8%8B%EF%BC%9A%E5%BA%94%E7%94%A8%E5%A4%A7%E6%A8%A1%E5%9E%8B%E7%9A%84%E9%AB%98%E7%BA%A7%E6%96%B9%E6%B3%95.md#L915)，来源许可：GPL-3.0。

<a id="kac6f286d6ca3"></a>

## 介绍一下你项目里的 Hybrid RAG 流程，双路召回后怎么得到最终的 TopK？

**难度评分：⭐⭐⭐⭐ (4/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

可按“查询理解—权限过滤—双路召回—去重融合—重排—扩展—预算裁剪—生成引用”的链路讲 Hybrid RAG。项目中实际用了哪一路、哪个参数和哪种模型要据实填写；没有验证的组合应表述为设计方案。

例如向量与 FTS 各取 30 个候选，按 chunk_id 合并，用 RRF 融合后保留前 20 个给重排器，再取 5 个种子块并补必要上下文。这些数字只是教学示例，应在相同延迟预算下调参。最终 K 不是越大越好，生成上下文还受 Token 和证据去重限制。

两路必须使用相同的租户、文档状态和 ACL 边界；重排前不得把未授权正文送给外部模型。记录两路排名、融合分、重排分和选中原因，便于判断某条证据在哪个阶段被丢掉。实时业务状态另外查询，不用旧知识块代替。

![图2HybridRAG的候选与证据链](https://raw.githubusercontent.com/WeThinkIn/AIGC-Interview-Book/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/imgs/agent-engineering-80-20261014/02_HybridRAG的候选与证据链.png)

图 2：双路召回共享同一身份与有效版本约束。排序分数决定优先看什么，授权和文档有效性决定能不能使用；二者不能互相替代。

**先定义证据身份，再谈 TopK。** 可以用 `(tenant_id, doc_id, doc_version, chunk_id)` 唯一定位一个块。两个版本文字高度相似，也可能具有不同政策效力；不能仅按文本相似度去重后保留任意一份。父块扩展应保留命中的子块位置，引用才能解释答案依据。

调参时固定总延迟和上下文预算，记录各阶段候选数及丢弃原因。若重排前已有足够候选而答案证据仍被挤掉，应检查相关性与去重；若权限过滤后只有两个候选，则先检查可见集合和检索计划，盲目扩大最终 K 无法制造新的证据。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L211)，来源许可：GPL-3.0。

<a id="kf86adf787818"></a>

## 介绍一下项目中的 RAG 流程，离线建库和在线检索分别做了什么？

**回答：**

离线建库从“可解析、可追踪、可更新”开始。系统接入文档后进行格式解析、OCR/版面恢复、清洗与去重，按标题、段落、表格或语义边界切块；每个 Chunk 保留 `document_id`、版本、章节路径、权限、时间和文档位置。随后用固定版本的 Embedding 模型编码，写入向量索引，同时构建 BM25/倒排索引，并记录模型版本与索引状态。

在线侧先做 Query 规范化、意图识别和权限过滤，必要时进行多轮问题改写或拆分。系统并行执行稠密向量召回和稀疏关键词召回，使用 RRF、加权分数或学习排序融合候选，再用 Cross-Encoder/LLM Reranker 精排。候选经过文档去重、相邻块扩展和 token 预算截断后进入上下文，并携带可核验引用。

生成阶段要求模型只在证据范围内回答；证据不足时澄清或拒答。输出后检查引用是否存在、结论是否被引用片段支持、数字和实体是否一致。索引更新要处理增量写入、版本切换、删除传播和旧索引回收，不能只建一次库。

评估分三层：检索层看 Recall@K、MRR/nDCG 与权限过滤；生成层看忠实度、引用正确率和答案相关性；系统层看端到端成功率、延迟、成本与更新时效。RAG 的本质是给当前决策提供可追溯证据，不是把向量库检出的文本直接堆进 Prompt。

<a id="pinduoduo-ai-agent-20260816-q9"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E6%8B%BC%E5%A4%9A%E5%A4%9A%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L267)，来源许可：GPL-3.0。
