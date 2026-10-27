# RAG与Agent

<a id="mad8535930e6e"></a>

## RAG 的完整链路与问题定位

RAG 在生成前从外部知识中检索相关证据，再把证据交给模型使用。离线链路通常包括文档解析、清洗、分块、元数据、向量化和索引；在线链路包括查询理解、召回、融合、重排、上下文组装、生成与引用。

它解决知识更新、可追溯证据和私有知识访问的一部分问题，但召回到错误材料或模型不遵守证据时仍会失败。排查顺序应拆开：原文是否正确入库、正确片段是否可检索、是否进入最终上下文、模型是否正确使用。只更换大模型或增加 top-k，可能掩盖真正的解析、权限或排序问题。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L42)；[原始 RAG 论文](https://arxiv.org/abs/2005.11401)。

<a id="m114c4711dc3f"></a>

## 文档分块、重叠与父子检索

分块决定检索的最小证据单位，应尽量保留语义边界、标题层级、表格关系和可定位来源。块太小容易丢失条件，太大则可能混入无关信息、降低匹配精度并占用生成预算；不存在适合所有文档的统一字符数。

重叠可以减少边界切断，但会增加重复召回和索引体积。父子检索可用较小子块匹配查询，再返回更完整父级上下文；这要求稳定的父子关系和预算控制。评价分块不能只看检索相似度，还应看答案需要的全部条件能否被同一次召回保留。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L197)；[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/05_%E6%8F%90%E7%A4%BA%E5%B7%A5%E7%A8%8B%EF%BC%9A%E5%BA%94%E7%94%A8%E5%A4%A7%E6%A8%A1%E5%9E%8B%E7%9A%84%E9%AB%98%E7%BA%A7%E6%96%B9%E6%B3%95.md#L743)。

<a id="mf162431ec7a9"></a>

## Embedding、相似度与模型升级

Embedding 将文本映射为向量，使相关内容在指定空间中更容易被比较。余弦相似度关注方向，内积还受向量长度影响；若向量已按单位范数归一化，二者排序具有明确关系。索引和查询必须采用一致的模型、预处理及度量设置。

语义相近不等于能回答同一个问题：版本、否定条件、实体和数值可能决定答案。升级 Embedding 后，旧向量与新查询通常不再处于同一表示空间，应明确重建索引、双写、灰度或回滚方案。不能把查询端换模型当成无状态升级。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L102)；[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L110)。

<a id="m4886b4934b1d"></a>

## BM25、向量检索与混合融合

BM25 以词项匹配为基础，擅长精确名称、编号和术语；向量检索可覆盖不同措辞表达的语义联系。混合检索并行获得不同召回结果，再去重、融合和重排，兼顾精确词项与语义扩展。

两路原始分数往往不在同一尺度，不能未经校准就机械相加。可以采用分数归一化或基于名次的融合，再在验证集上按查询类型调整。融合前还要统一文档身份、版本和权限，避免同一段落占满候选列表；所谓“最佳比例”应由评测决定。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L52)；[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/05_%E6%8F%90%E7%A4%BA%E5%B7%A5%E7%A8%8B%EF%BC%9A%E5%BA%94%E7%94%A8%E5%A4%A7%E6%A8%A1%E5%9E%8B%E7%9A%84%E9%AB%98%E7%BA%A7%E6%96%B9%E6%B3%95.md#L838)。

<a id="m0154e5b723f7"></a>

## 近似最近邻与 HNSW 的取舍

精确检索计算所有候选的距离，数据量增大时成本高；近似最近邻索引以可控的召回损失换取检索速度和资源效率。HNSW 通过分层图进行导航，在较粗层快速接近相关区域，再在较细层搜索候选。

图连接度、构建搜索范围和查询搜索范围分别影响内存、构建成本、延迟与召回。索引快不代表业务检索好：权限过滤、版本过滤和向量质量都可能影响最终结果。调参时应在目标数据规模和过滤条件下，联合报告 Recall@K、延迟、吞吐与内存，而不是只测无过滤的单条查询。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L78)；[HNSW 原论文](https://arxiv.org/abs/1603.09320)。

<a id="ma20de85a53f9"></a>

## Rerank 与上下文选择

召回追求在有限成本下尽量找全，重排对较小候选集做更精细的相关性判断。常见双塔检索允许文档向量预计算；交互式重排模型同时观察查询与文档，能够利用更细粒度的匹配关系，但每个候选的计算成本更高。

重排只能在已有候选中排序，不能找回根本未召回的证据。最终上下文还需去重、控制覆盖与长度，并保留来源定位。把 top-k 全部拼接通常不是最优方案：相似段落重复、缺少互补证据以及关键条件被截断，都可能使生成质量下降。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L327)。

<a id="me2752a73d495"></a>

## 查询改写、HyDE 与多跳检索

查询改写将口语、省略或多轮指代整理为便于检索的表达；多查询扩展用不同表述提高覆盖；HyDE 先生成假设文档式内容，再利用其表示检索真实材料。这些方法都在改变检索输入，而不是直接提供可信答案。

改写必须保留原问题的实体、限制、时间和权限范围；模型扩展出的内容可能偏离问题，不能将假设内容当证据。复杂问题可分解并逐步检索，但每步要记录已有结论和来源。是否采用这些方法应比较召回收益、额外延迟与失败样本，而非默认所有请求都调用一遍。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/05_%E6%8F%90%E7%A4%BA%E5%B7%A5%E7%A8%8B%EF%BC%9A%E5%BA%94%E7%94%A8%E5%A4%A7%E6%A8%A1%E5%9E%8B%E7%9A%84%E9%AB%98%E7%BA%A7%E6%96%B9%E6%B3%95.md#L776)。

<a id="m9526c999450b"></a>

## 元数据、权限过滤与知识版本

文档 ID、版本、时间、来源、租户和访问范围是知识链路的一部分。权限应在服务端与检索执行中实施，并贯穿召回、重排、缓存和生成；只在提示里要求“不要透露无权限内容”不能替代访问控制。

索引更新要支持新增、修改、删除和权限变更。稳定文档身份与内容版本可避免旧块残留；删除源文档后只移除目录记录而保留向量，会继续召回过期信息。更换分块或向量模型时，应将数据版本、索引版本和部署版本关联，保证灰度和回滚能够解释用户实际看到的内容。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L341)；[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L355)。

<a id="m5b01e1a24681"></a>

## RAG 评测：检索与生成分开衡量

检索评测关注正确证据是否被找回及排序位置，例如 Recall@K、MRR、NDCG；生成评测关注是否回答问题、是否得到证据支持、引用是否指向真正支持结论的片段。高召回并不保证答案正确，高流畅度也不代表忠实于证据。

评测集应包含有答案、无答案、歧义、多版本、权限受限和多跳问题，并保留标准证据。先定位失败发生在哪个环节，再改分块、召回、重排或提示。LLM-as-judge 可辅助扩大评测，但需要评判标准、人工抽查和对偏差的检查；不能把同一模型的自评当成独立事实证明。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L384)；[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L402)。

<a id="m3b0d1e7224ab"></a>

## 幻觉、拒答与可核验引用

在有证据约束的问答中，幻觉不仅是编造事实，也包括把证据没有支持的推论说成已确认结论。提供 RAG 上下文能增加可用证据，但模型仍可能忽略条件、混淆来源或补全缺失信息。

应让答案区分已支持事实、必要推断和信息缺口；无足够证据时拒答或请求补充条件。引用要落到能支持具体主张的片段，而不是挂一个相关文档标题。上线检查还需验证引用确实存在、用户有权限访问、版本正确，以及答案是否越过了证据范围。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L416)。

<a id="mbb3b93abe76c"></a>

## RAG 与微调的职责划分

RAG 主要把可更新的外部信息在推理时提供给模型；微调主要改变模型的行为、任务形式和对特定数据分布的适应。频繁变化、需要引用和权限控制的知识通常适合在外部知识链路管理；格式遵循或特定任务表现可能适合训练优化。

二者可以结合：微调改善查询、工具使用或证据利用，RAG 提供最新材料。但微调不能替代事实更新和访问控制，RAG 也不能自动修复弱指令遵循或复杂任务能力。选型应先明确失败来自缺知识、不会使用知识，还是输出行为不符合要求。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/10_Agent_RAG%E4%B8%8E%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L133)。

<a id="mec437c41c1a0"></a>

## Agent、Workflow 与自主决策边界

工作流由程序显式规定主要步骤和分支；Agent 允许模型根据当前状态选择下一步行动或工具。两者的边界在于控制流有多大程度由模型决定，而不是是否出现某个框架名或是否调用了工具。

固定、可枚举且要求稳定的任务适合明确工作流；开放任务可以给 Agent 更大的规划空间，但需控制预算、权限和停止条件。实际系统常混合两者：关键业务步骤由程序约束，模型负责局部判断。自主性增加通常伴随测试、观测和恢复成本，不能只用“更智能”解释选型。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L74)。

<a id="me6270a7a9e05"></a>

## 工具调用的声明、执行与校验

模型的工具调用输出只是调用意图，真正的执行由宿主程序完成。完整链路包括选择工具、生成结构化参数、校验参数与权限、执行、记录结果，再将结果以明确的工具消息交回模型。模型生成的工具名或参数不能直接获得超出请求身份的能力。

工具说明应明确作用、输入、输出和错误，参数 schema 应尽量消除含糊字段。结构合法不等于语义正确，仍需校验资源存在、取值范围、调用者权限和业务前置条件。工具结果中的文本也可能不可信，应作为数据处理，而不是提升为新指令。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L201)。

<a id="m1c30e5a057bd"></a>

## ReAct、计划执行与动态修正

ReAct 将推理、行动和观察交替组织，使模型根据工具反馈调整下一步行动；计划执行先形成任务分解，再执行或修订计划。二者都试图把复杂任务拆成可管理步骤，但计划不是事实证明，工具返回也可能失败或不完整。

运行时应保留明确任务状态、已验证事实、未完成步骤与错误；遇到反馈与假设冲突时重新规划，而不是盲目完成旧清单。对外需要的是可观察行动、依据和结果，不必要求公开模型内部的全部推理文本。稳定任务可固定部分步骤，减少无必要的自主循环。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L176)；[原论文：ReAct](https://arxiv.org/abs/2210.03629)。

<a id="mfa9e797a85b4"></a>

## 短期状态、长期记忆与知识库

短期状态服务于当前任务，例如对话、计划、工具结果和执行进度；长期记忆保存经确认、跨任务有用的信息；知识库则以文档和检索结构管理外部资料。三者可能共享存储技术，但生命周期、可信度和访问方式不同。

长期记忆要有来源、时间、作用域、更新与删除机制。把全部聊天记录自动写入并在每次请求全量加载，会造成重复、过期信息和隐私范围混淆。偏好、事实、任务记录应有不同更新策略；发现冲突时依据版本、来源和确认状态处理，不能仅因某条记忆最近被模型生成就判定正确。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/07_%E4%BC%81%E4%B8%9A%E7%BA%A7Agent%E5%B9%B3%E5%8F%B0%E4%B8%8E%E4%BA%A7%E5%93%81%E8%90%BD%E5%9C%B0%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L290)。

<a id="m04ded0bbb2c8"></a>

## 上下文工程、压缩与任务交接

上下文工程管理模型完成当前步骤真正需要看到的信息，包括规则、用户目标、任务状态、检索证据、工具结果和有关记忆。提示措辞只是其中一部分，信息选择、可信层级与预算同样决定效果。

压缩应保留目标、约束、已确认结论、证据定位、未决问题与下一步，而不是只保留故事式摘要。旧工具输出可以摘要或外置，但影响操作合法性的条件不能丢失。交接后应能依据保存状态继续执行，不依赖模型记住未写出的对话；新消息对目标的修正也应进入状态。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/02_%E7%BC%96%E7%A0%81Agent%E4%B8%8EAgentOS%E5%B7%A5%E7%A8%8B%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L400)。

<a id="mded4f900de55"></a>

## MCP、Function Calling 与 Skills 的边界

Function Calling 描述模型如何表达结构化调用意图；MCP 规定宿主与外部能力服务之间的一类交互接口；Skills 通常组织完成任务所需的流程说明与辅助资源。它们位于表达调用、接入能力和任务方法等不同层面，不能视作同一个东西的不同名称。

接入协议不能代替业务权限：工具仍需认证、授权、参数约束、超时、审计和隔离。方法说明也不能突破运行时的能力边界。具体协议消息、传输和版本会变化，面试表达应把稳定职责与所用版本实现分开，不把某个版本的连接方式当成全部 MCP。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/04_MCP%E4%B8%8EA2A%E5%8D%8F%E8%AE%AE%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L73)；[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L337)。

<a id="mfd33f616a104"></a>

## 超时、重试、幂等与可恢复执行

Agent 会遇到模型调用超时、工具失败和任务取消。重试必须区分未执行、执行失败和执行结果未知：支付、写库等有副作用的操作，网络超时并不能证明操作没有生效。幂等键、执行记录和结果查询可帮助避免重复动作。

应为模型、工具和整个任务设置不同预算，限制轮次、成本和重复调用；取消要传递到真正执行的子任务。可恢复执行需持久化足够状态，并明确哪些步骤可以重放、哪些需要查证或用户决定。只在提示里写“不要死循环”不能替代运行时控制。

参考资料：[Snailclimb/JavaGuide 原文](https://github.com/Snailclimb/JavaGuide/blob/992dae31eade2a34ba8dbbbcf5ed9de5511325ec/docs/ai/interview-questions/agent-project-interview-guide.md#L387)。

<a id="m2daf1259c3da"></a>

## 提示注入、工具权限与不可信输入

提示注入把恶意指令混入网页、文档、检索片段或工具结果，诱导应用把外部数据当成高优先级规则。与普通错误输入相比，关键风险是它可能改变模型的目标或行动选择，尤其在模型具备外部工具时。

防护应同时建立指令与数据边界、最小权限、服务端校验和执行隔离。敏感读取或写入必须受身份与业务规则约束，不能靠模型自行判断“文本看起来可信”。分隔符和提示规则只是辅助；还需在实际工具边界阻止越权，并用攻击样本检查检索、记忆和工具结果的完整路径。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/06_Agent%E5%AE%89%E5%85%A8%E8%AF%84%E6%B5%8B%E4%B8%8EAgentOps%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L206)。

<a id="mb1297bd1c97a"></a>

## Agent 评测、轨迹观测与多 Agent 取舍

Agent 的结果取决于多步决策和工具反馈，评测除最终任务成功率，还应看工具选择与参数正确性、约束遵守、恢复能力、成本、延迟和副作用。一次演示成功不能说明可靠性，工具返回成功也不等于用户任务完成。

轨迹记录应能还原输入、调用、结果和状态变化，并对敏感信息做合适处理。多 Agent 可分工独立任务或隔离上下文，但引入消息、协调、冲突和验证成本；多个 Agent 同意一个结论并不构成独立证据。选型时先比较单 Agent 或明确工作流能否满足要求，再用任务级评测验证分工收益。

参考资料：[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/06_Agent%E5%AE%89%E5%85%A8%E8%AF%84%E6%B5%8B%E4%B8%8EAgentOps%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L98)；[WeThinkIn/AIGC-Interview-Book 原文](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/06_Agent%E5%AE%89%E5%85%A8%E8%AF%84%E6%B5%8B%E4%B8%8EAgentOps%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L272)。

## 专题阅读

- [Agent、工具与工作流（1）](Agent%E3%80%81%E5%B7%A5%E5%85%B7%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81-01.md)
- [Agent、工具与工作流（2）](Agent%E3%80%81%E5%B7%A5%E5%85%B7%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81-02.md)
- [Agent、工具与工作流（3）](Agent%E3%80%81%E5%B7%A5%E5%85%B7%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81-03.md)
- [Agent、工具与工作流（4）](Agent%E3%80%81%E5%B7%A5%E5%85%B7%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81-04.md)
- [Agent、工具与工作流（5）](Agent%E3%80%81%E5%B7%A5%E5%85%B7%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81-05.md)
- [Agent、工具与工作流（6）](Agent%E3%80%81%E5%B7%A5%E5%85%B7%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81-06.md)
- [Agent、工具与工作流（7）](Agent%E3%80%81%E5%B7%A5%E5%85%B7%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81-07.md)
- [RAG与检索增强（1）](RAG%E4%B8%8E%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA-01.md)
- [RAG与检索增强（2）](RAG%E4%B8%8E%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA-02.md)
- [RAG与检索增强（3）](RAG%E4%B8%8E%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA-03.md)
