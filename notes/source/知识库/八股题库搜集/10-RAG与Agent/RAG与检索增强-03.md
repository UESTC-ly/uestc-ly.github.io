# RAG与检索增强

<a id="k8b298746062f"></a>

## 短期记忆和长期记忆分别怎么设计？历史对话在什么情况下会被摘要或召回？

**回答：**

短期记忆服务当前任务，包括最近消息、工具 Observation、未完成计划、结构化槽位和 checkpoint。它通常按 `tenant_id/user_id/conversation_id/task_id` 隔离，存放在会话存储或持久化状态机中。长期记忆保存跨会话仍有价值的信息，例如用户明确偏好、稳定事实、已确认决定和可复用经验，并附带来源、时间、置信度、版本和过期策略。

历史对话接近 token 预算、出现长工具结果或阶段目标完成时，可以生成摘要。但摘要不能只保留一段流畅文本，应保存目标、硬约束、已确认事实、决定、未决事项、关键引用和工具副作用。原始对话仍放在可检索存储中，摘要只是工作状态，不是唯一真相。

长期记忆写入前要经过重要性判断、用户授权、敏感信息过滤、去重和冲突检测。召回由当前 Query、任务类型、时间衰减、权限和相似度共同决定，并经过 Rerank；不是每轮都把所有记忆注入。新旧事实冲突时要保留版本或请用户确认，不能让最后一次模型推测覆盖已确认事实。

评估记忆系统要看任务成功率、重复询问率、正确记忆召回率、错误记忆引用率、token 成本和隐私风险。其本质是维护当前决策所需的最小充分状态，而不是无限增长的聊天记录。

<a id="pinduoduo-ai-agent-20260816-q12"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E6%8B%BC%E5%A4%9A%E5%A4%9A%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L316)，来源许可：GPL-3.0。

<a id="k7e3916c0dd36"></a>

## 第 4 课：先修解析与切分，再讨论向量库

核心阅读：[第 20 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-001)、[第 24 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-005)、[第 26 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-007)、[第 27 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-008)、[第 28 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-009)、[第 29 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-010)、[第 30 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-011)、[第 31 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-012)、[第 32 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-013)、[第 33 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-014)、[第 34 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-015)。

准备三类小语料：带标题与表格的课程 Markdown、包含分页或扫描内容的 PDF、带注释和函数定义的代码文件。为每份文档标明版本、权限、更新时间、页码或行号，不把网页解析失败的残片直接作为高质量数据。

设计至少两组切分策略：固定预算切分作为基线；按标题/结构切分，过长部分再递归拆分。记录每块标题路径、顺序、父段和原文位置。为跨块限定条件构造问题，比较原始块、邻块扩展和父段回取的证据覆盖。

Embedding 选择先看中文、专业名词、长度限制和实际质量，再看部署成本。对归一化向量验证 L2 与余弦排序关系，对零向量显式拒绝或特殊处理；不要把相同维度误当作同一表示空间。

**实验。** 建立一份带标准证据位置的问题集，将索引开发集与最终测试集分开。切换模型时创建新版本索引，不覆盖旧版本后只跑一次查询就宣告成功。

**验收。** 抽样逐块回查原文，说明每个块为什么这样切；如果 PDF 读取顺序已经错误，应先修解析。RAG 与微调的选择能对应具体故障，而不是哪个概念更热门。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%83%AD%E9%97%A8AI%E5%AD%A6%E4%B9%A0%E6%A0%B8%E5%BF%83%E8%AF%BE%E7%A8%8B%E4%B8%8E%E6%95%99%E7%A8%8B/16_AI_Agent%E5%B7%A5%E7%A8%8B%E5%AE%9E%E6%88%98%EF%BC%9A%E5%9F%BA%E7%A1%8080%E9%97%AE%E5%AD%A6%E4%B9%A0AI%20Agent.md#L99)，来源许可：GPL-3.0。

<a id="k244f87889468"></a>

## 第 5 课：让 Hybrid RAG 有可解释的排名链路

核心阅读：[第 21 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-002)、[第 22 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-003)、[第 23 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-004)、[第 35 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-016)、[第 36 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-017)、[第 37 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-018)、[第 38 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-019)、[第 39 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-020)、[第 40 题](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent基础/10_Agent_RAG与混合检索工程高频考点.md#q-021)。

使用 PostgreSQL FTS 做词法路，pgvector 做语义路，先分别记录 TopN 及其排名。中文入库与查询使用相同分词方案。精确课程编号与错误码单独设测试组，语义改写设另一组，避免总分掩盖一条路径的缺陷。

将两路按 chunk_id 去重后执行 RRF，再送有限候选给重排器。候选数、RRF 常数、重排截断和最终证据数分别控制，不能把 TopK 当作一个贯穿全链路的万能参数。最终生成前再按需要扩展父段或邻块，并控制 Token 预算。

**可运行练习。** 附带示例的 RRF 输入是人工给定的排名，用于验证融合、去重与并列排序，不代表已经运行真实向量检索。完成它后，将人工排名替换为实际数据库结果，保留同一融合接口。

**对照实验。** 固定问题集，比较词法单路、向量单路、RRF、RRF 加重排。记录证据 Recall@K、nDCG 或 MRR、候选规模与耗时。FTS 的 rank 与向量距离不能直接相加；GIN 匹配成功也不等于排序已经正确。

**验收。** 给出一条被每个阶段保留或淘汰的证据，解释原因。若重排前没有授权过滤，先修安全边界，再比较检索分数。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%83%AD%E9%97%A8AI%E5%AD%A6%E4%B9%A0%E6%A0%B8%E5%BF%83%E8%AF%BE%E7%A8%8B%E4%B8%8E%E6%95%99%E7%A8%8B/16_AI_Agent%E5%B7%A5%E7%A8%8B%E5%AE%9E%E6%88%98%EF%BC%9A%E5%9F%BA%E7%A1%8080%E9%97%AE%E5%AD%A6%E4%B9%A0AI%20Agent.md#L113)，来源许可：GPL-3.0。

<a id="k4e619ea02be7"></a>

## 综合排查题

- 原始文档已经入库，但相关问题始终召回不到正确 Chunk，你会从哪些环节开始检查？
- 正确文档进入了候选池，却总是排在 TopK 之外，应该调整召回还是引入 Rerank？
- 检索结果正确，模型仍然引用了错误片段，如何检查上下文顺序、截断和指令约束？
- 同一份文档的新旧版本被同时召回，数据和索引更新链路可能出了什么问题？
- 只有最终答案好坏的评分时，如何判断问题出在检索还是生成？
- 某类问题需要跨多篇文档查关系，如何判断应该优化向量 RAG，还是引入 GraphRAG？

### 参考资料

- [JavaGuide](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/rag-interview-questions.md#L125)，来源许可：Apache-2.0。

<a id="kda8dd501b80f"></a>

## 聊了一下 RAG

**回答：**

### 补充说明

<a id="tencent-llm-collection-20260903"></a>

**相关解释：** [Embedding模型与Reranker差异，二者训练Loss区别](RAG%E4%B8%8E%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA-01.md#k1abf61aa73cc)；[正常来说，一个query进了RAG之后，整体的工作流程是怎样的？](Agent%E3%80%81%E5%B7%A5%E5%85%B7%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81-05.md#kf95403e9fa89)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1613)，来源许可：GPL-3.0。
- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%85%BE%E8%AE%AF%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L255)，来源许可：GPL-3.0。

<a id="k1bc1c7048a1f"></a>

## 讲讲RAG的混合召回

**回答：**

RAG 的混合召回是指同时使用多种召回方式，把它们的结果融合后再交给 reranker 或生成模型。目标是提升召回率和鲁棒性，避免单一向量检索或单一关键词检索的短板。

最常见的是稀疏召回加稠密召回。稀疏召回通常是 BM25、倒排索引或关键词匹配，擅长精确词、专有名词、编号、错误码、函数名、政策条款。稠密召回通常是 Embedding 向量检索，擅长语义相近但表述不同的问题，例如“怎么防止模型乱编”和“如何降低幻觉”。

标准流程是：用户 query 先做清洗和改写，例如补全领域词、生成多个子 query、抽取关键词；然后并行走 BM25 和向量检索，各自取 top-k；再做结果融合，常见方法有加权分数融合、归一化后求和、RRF；融合后去重，并按 metadata 过滤，例如权限、时间、文档类型、业务线；最后用 cross-encoder reranker 或 LLM reranker 重排，选出最适合放进 prompt 的证据。

混合召回还可以扩展到结构化数据库召回、知识图谱召回、FAQ 精确匹配、标题/摘要字段召回、历史对话召回、工具检索。企业场景中经常需要权限过滤和时效过滤，否则召回对了但用户无权访问，也不能放进上下文。

评价混合召回时，不只看最终回答好不好，还要看检索侧指标，例如 recall@k、MRR、nDCG、命中证据覆盖率、rerank 后正确证据排名、无答案问题的拒答率。常见坑包括 chunk 切得太碎、BM25 和向量分数直接相加、top-k 太大引入噪声、没有 rerank、没有权限过滤、没有评估集。

<a id="ant-agent-20260520-q9"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E8%9A%82%E8%9A%81%E9%9B%86%E5%9B%A2%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L194)，来源许可：GPL-3.0。

<a id="ka0c2c90f5995"></a>

## 语义检索是如何实现的？

**回答：**

语义检索通常分为离线建库和在线检索两部分。

离线侧对文档解析、清洗、按标题/段落/语义边界分块，保留文档 ID、版本、权限、时间和来源等 metadata；用 Embedding 模型将块编码为向量，写入向量数据库或 ANN 索引，同时维护倒排索引。

在线侧先规范化 Query，必要时做意图识别、改写和过滤条件提取；用同一表示空间的 Embedding 编码 Query，进行向量召回，并与 BM25/关键词、规则和结构化过滤融合；对候选用 Cross-Encoder Rerank，按阈值或 token 预算截断，去重后注入上下文并携带引用。

向量相似度可以写成：

$$
s(q,d)=\frac{e_q^{\mathsf T}e_d}{\lVert e_q\rVert_2\lVert e_d\rVert_2}
$$

工程上不能只看相似度。要验证 Recall@K、MRR/nDCG、证据支持率、无结果率、延迟、索引更新时效和权限过滤正确率；专业术语、编号、代码和新词通常需要保留关键词召回。

<a id="alibaba-agent-20260802-q7"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L877)，来源许可：GPL-3.0。

<a id="kd133e559856d"></a>

## 跨模态检索的评估指标有哪些?

跨模态检索主要评估指标包括：

1）Recall@K，衡量前K个结果中包含正确结果的比例；

2）Mean Reciprocal Rank（MRR），计算首个正确结果的倒数排名均值；

3）Normalized Discounted Cumulative Gain（NDCG），考虑结果排序相关性的加权评分；

4）Cross-modal Semantic Consistency，通过预训练模型计算图文嵌入的余弦相似度分布。新兴指标如Modality-Aware F1 Score，综合评估多模态查询中各模态贡献的平衡性。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%E5%A4%9A%E6%A8%A1%E6%80%81%E5%9F%BA%E7%A1%80/%E5%A4%9A%E6%A8%A1%E6%80%81-%E6%A0%B8%E5%BF%83%E6%A8%A1%E5%9E%8B.md#L191)，来源许可：GPL-3.0。

<a id="k6bddb6368b17"></a>

## 选一个你做得最满意的 Agent 项目，完整讲一遍。——从业务背景到技术方案到落地效果。不要报菜名（说用了 RAG、用了 Multi-Agent），我要听设计决策背后的思考。

**回答：**

一个合格的项目介绍应该沿着“业务目标 -> 任务不确定性 -> 系统决策 -> 验证结果”展开，而不是罗列技术名词。可以用下面的结构回答：

1. **背景与目标。** 说明服务对象、原流程、痛点和成功标准。例如，用户需要在企业知识、工单和业务系统之间完成一个多步骤问题，原来由人工检索、判断并填写结果，耗时长且过程不可追踪。
2. **为什么需要 Agent。** 如果路径固定、规则明确，就使用 Workflow；只有当任务需要根据中间观察动态选择工具、拆解子任务或处理异常时，才引入 Agent。Agent 的合理性来自决策路径不固定，而不是因为系统中调用了大模型。
3. **系统边界。** 接入层负责鉴权和会话；编排层负责状态机、预算和停止条件；模型层负责规划、结构化动作和自然语言生成；知识层负责检索证据；工具层负责受控访问业务 API；状态层保存检查点和事件轨迹；评测层记录每一步输入、输出和结果。
4. **关键设计决策。** 说明为什么采用混合检索、为什么把高风险工具放在人工确认后、为什么使用结构化状态而不是把全部历史对话塞给模型、为什么某些固定步骤用确定性代码而不是交给模型。
5. **效果和证据。** 报告任务成功率、工具调用正确率、引用支持率、P95 延迟、单任务 token 成本、人工接管率等指标，同时说明评测集规模、时间窗口、基线和统计口径。没有真实线上数字时，应明确说这是离线实验或 PoC 结果，不能临场编造。

Agent 项目的本质不是“模型回答得像不像人”，而是从输入到最终结果形成可验证的闭环：

$$
\text{Goal}\rightarrow\text{Plan}\rightarrow\text{Action}\rightarrow\text{Observation}
\rightarrow\text{Verification}\rightarrow\text{Result}
$$

落地效果必须能对应到业务指标，例如平均处理时长降低、人工转交率下降、关键字段准确率提高或审计覆盖率提升。若只有模型离线打分上升，却没有任务级收益，不能称为完整落地。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/DeepSeek%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L430)，来源许可：GPL-3.0。

<a id="k111fe5348e21"></a>

## 递归字符切分是怎么工作的？块大小、重叠大小和分隔符顺序怎么设置？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

递归字符切分按照由粗到细的分隔符尝试拆分。先用段落边界；仍超长的片段再用换行、句末或更细粒度分隔符；将较小片段按预算合并为块，必要时保留前一块末尾的一部分作为重叠。

块大小必须明确计量单位：字符数与 Token 数并不等价，中文、代码和英文的比例不同。可从数百 Token 的块及较小重叠作为实验起点，但最终要按答案跨度、Embedding 限制和检索预算调参。分隔符次序应适配中文标点、Markdown 标题与代码边界。

检查单个极长段落、没有分隔符的文本、表格、代码围栏及 Unicode 字符。重叠不能导致重复候选无限占用 TopK，合并阶段还要去重。明确保留分隔符和位置偏移的规则，才能将检索结果映射回原文。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L157)，来源许可：GPL-3.0。

<a id="k17046a628071"></a>

## 针对专业术语出现语义偏移的问题，除了混合检索方案，是否尝试过Embedding模型微调、Adapter适配等优化方式？具体落地思路是怎样的？

<a id="batch4-p2-q5"></a>

**相关解释：** [Embedding模型与Reranker差异，二者训练Loss区别](RAG%E4%B8%8E%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA-01.md#k1abf61aa73cc)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L342)，来源许可：GPL-3.0。

<a id="ke67f3b93db3d"></a>

## 长期记忆可以按需检索召回，具体在什么情况下需要检索？

**回答：**

长期记忆检索的触发条件是：当前任务是否依赖跨会话的用户事实、历史决策或已沉淀经验。典型场景包括用户明确说“沿用上次方案”“继续昨天的任务”，当前输入出现历史项目/人物/文件实体，需要个性化偏好，存在未完成任务，或者当前信息与已知记忆可能冲突。

实现上可以使用多级门控。先用规则捕获显式历史指代和实体，再用轻量路由模型判断记忆依赖程度；对于高风险操作，即使用户没有明确提历史，也要查询授权状态和既有约束。路由结果还应带检索范围，例如只查当前项目、当前用户或某类记忆，避免全库搜索。

检索查询不应直接等于用户原句。可以结合当前目标、实体、时间范围和 memory type 做 query rewriting，再使用向量、关键词、结构化过滤或图关系检索。召回后按相关性、时间、置信度、来源权威性和作用域重排。

需要区分“检索”和“注入”。系统可以低成本检索候选记忆，但只有通过相关性和冲突校验的内容才进入模型上下文。若候选记忆互相矛盾，应标记冲突并询问用户，而不是静默选择一个版本。

知识图谱适合实体关系和多跳查询，但不是长期记忆的必选项。很多场景用关系数据库加向量/全文检索已足够；只有关系结构确实带来可验证收益时，才值得引入图数据库。

<a id="moonshot-agent-dev-20260721-q10"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E6%9C%88%E4%B9%8B%E6%9A%97%E9%9D%A2%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L196)，来源许可：GPL-3.0。

<a id="kad63f6e41949"></a>

## 面试追问：系统提示词、用户偏好、会话摘要、最近对话和检索结果，怎么组装成上下文？

上下文应按信任等级和用途组织：受信任的系统约束、当前任务与用户输入、适用的用户偏好、任务状态与摘要、最近交互、经授权的检索证据及工具结果。逻辑优先级由系统规则决定，不能指望改变文本先后顺序就建立权限边界。

把外部文档和历史记忆标记为数据，附上范围、时间和引用；文档中的“忽略所有规则”不成为新指令。检索结果只应帮助回答，其内容不授予工具权限。用户偏好与当前任务冲突时，根据范围和新旧关系选择，而非盲目全部拼接。

总预算要包括指令、消息、工具定义、证据、预留输出与安全余量。先删重复和低相关内容，再压缩已完成步骤，仍不足则分步处理或取回关键原文。记录组装规则与被裁剪的类别，才能复盘模型为何缺少某条证据。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/05_Agent%E8%AE%B0%E5%BF%86%E4%B8%8E%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L491)，来源许可：GPL-3.0。

<a id="k1bc90b9f7728"></a>

## 面试追问：跨对话语义记忆怎么做去重、相似归并和召回降权？

先在相同用户、权限和事实范围内做精确去重，再用语义相似度找“可能相同”的候选，由结构化字段或受约束判断决定归并。相似度高只说明表达接近，“喜欢辣”和“不喜欢辣”仍可能很相似，不能据此直接合并。

归并时保留事实主键、版本、适用场景和证据，不把临时偏好覆盖成永久偏好。召回可综合相关性、时效、可信度和频次，但重复出现次数容易被日志复制放大，需要按独立证据计数。

过期和冲突记忆可排除或降权，已删除、未授权记忆必须排除，不能只把分数调低。降权策略要避免长期稳定偏好被纯时间衰减抹掉。用冲突对、否定句、同义改写、不同用户相似事实和重复导入等样本验证。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/05_Agent%E8%AE%B0%E5%BF%86%E4%B8%8E%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L348)，来源许可：GPL-3.0。
