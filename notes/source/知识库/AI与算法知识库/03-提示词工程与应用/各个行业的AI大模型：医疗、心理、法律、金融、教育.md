# 各个行业的AI大模型：医疗、心理、法律、金融、教育....



## **一、医疗领域大模型**

### 1、**DoctorGLM**

基于ChatGLM-6B的卓越中文问诊模型，它融合了海量的中文医疗对话数据集进行精准微调，采用lora、p-tuningv2等前沿技术实现高效部署。

**项目地址：**https://github.com/xionghonglin/DoctorGLM

**论文地址：**https://arxiv.org/abs/2304.01097



### 2、**BenTsao (本草）**

该项目集大成者，开源了多款经过中文医学指令微调的大语言模型，涵盖LLaMA、Alpaca-Chinese、Bloom等，皆以医学知识图谱和医学文献为基础，结合ChatGPT API精心打造，实现了中文医学指令微调数据集的精准训练，极大提升了医疗领域问答的准确性与实用性。

**项目地址：**https://github.com/SCIR-HI/Huatuo-Llama-Med-Chinese

**论文地址：**https://arxiv.org/abs/2304.06975



### 3、**Med-ChatGLM**

该项目同样基于中文医学指令微调，对ChatGLM-6B模型进行了深度优化，微调数据与BenTsao项目一脉相承，确保了模型在医疗领域的卓越表现。

**项目地址：**https://github.com/SCIR-HI/Med-ChatGLM



### 4、**BianQue (扁鹊）**

该项目开创性地推出了生活空间健康大模型，深度整合了当前开源的中文医疗问答数据集，结合自建的生活空间健康对话大数据，构建了千万级别的扁鹊健康大数据BianQueCorpus，基于此精心打造了ChatGLM-6B为初始化的BianQue模型，全面提升了模型在医疗与健康领域的应用价值。

**项目地址：**https://github.com/scutcyr/BianQue



### 5、**HuatuoGPT (华佗）**

该项目鼎力推出医疗大模型HuatuoGPT，其中包括了基于Baichuan-7B训练的HuatuoGPT-7B与基于Ziya-LLaMA-13B-Pretrain-v1的HuatuoGPT-13B，旨在提供全方位、高标准的医疗智能服务。

**项目地址：**https://github.com/FreedomIntelligence/HuatuoGPT

**论文地址：**https://arxiv.org/abs/2305.15075



### 6、**QiZhenGPT**

该项目通过启真医学知识库的精妙运用，构建了独具匠心的中文医学指令数据集，进一步在Chinese-LLaMA-Plus-7B、CaMA-13B、ChatGLM-6B等尖端模型上精心调整指令，显著提升了模型在中文医疗环境中的实用效果。

**项目地址：**https://github.com/CMKRG/QiZhenGPT



### 7、ChatMed

该项目创新性地发布了中文医疗大模型ChatMed-Consult，以ChatMed\_Consult\_Dataset中超过50万的中文医疗在线问诊数据及ChatGPT的精准回复作为训练基石，基于LlaMA-7b并通过LoRA技术进行了细致微调。

**项目地址：**https://github.com/michael-wzhu/ChatMed



### 8、ShenNong-TCM-LLM（神农）

该项目推出了中文中医药领域的杰出模型ShenNong-TCM-LLM，以中医药知识图谱为基础，运用实体为核心的自指令方法，通过ChatGPT生成了丰富的2.6万+中医药指令数据集ChatMed\_TCM\_Dataset，再基于LlaMA底座，借助LoRA技术进行了精准微调。

**项目地址：**https://github.com/michael-wzhu/ShenNong-TCM-LLM



### 9、XrayGLM

该项目开创了中文多模态医学数据集与模型的先河，尤其在医学影像诊断与多轮交互对话中展现出卓越的潜能。

**项目地址：**https://github.com/WangRongsheng/XrayGLM



### 10、MedicalGPT

该项目隆重推出了医疗大模型MedicalGPT，集成了增量预训练、有监督微调、RLHF（奖励建模、强化学习训练）和DPO（直接偏好优化）等前沿技术。

**项目地址：**https://github.com/shibing624/MedicalGPT



### 11、Sunsimiao（孙思邈）

该项目推出了中文医疗大模型Sunsimiao，该模型以baichuan-7B和ChatGLM-6B为坚实底座，在数十万条高质量的中文医疗数据中进行了精心微调。

**项目地址：**https://github.com/thomas-yanxin/Sunsimiao



### 12、CareLlama（关怀羊驼）

该项目推出了医疗大模型CareLlama，并汇集了数十个公开可用的医疗微调数据集和开放可用的医疗大语言模型，旨在为医疗LLM的快速发展注入强劲动力。

**项目地址：**https://github.com/itsharex/CareLlama



### 13、DISC-MedLLM

该项目由复旦大学发布，针对医疗健康对话式场景精心设计了医疗领域大模型与数据集。模型通过DISC-Med-SFT数据集在Baichuan-13B-Base基础上进行指令微调，有效匹配了医疗场景下的人类偏好，缩小了通用语言模型输出与真实世界医疗对话之间的差距。

**项目地址**：https://github.com/FudanDISC/DISC-MedLLM

**论文地址**：https://arxiv.org/abs/2308.14346



### **14、PMC-LLaMA**

本项目公开了前沿的医疗大模型PMC-LLaMA，其中包含MedLLaMA\_13B预训练版本与PMC\_LLaMA\_13B指令微调版本，为医疗领域带来了革新的技术突破。

**项目地址**：https://github.com/chaoyi-wu/PMC-LLaMA

**论文地址**：https://arxiv.org/abs/2304.14454



### **15、ChatDoctor**

ChatDoctor，一款基于LLaMA训练的医疗大模型，其开源特性让更多人能够领略医疗科技的魅力。

**项目地址**：https://github.com/Kent0n-Li/ChatDoctor

**论文地址**：https://arxiv.org/abs/2303.14070



### **16、MING (明医）**

MING，一个基于bloomz-7b指令微调而成的医疗大模型，其卓越的性能在医疗问答、智能问诊等方面得到了充分体现。

**项目地址：**https://github.com/189569400/MedicalGPT-zh



### **17、IvyGPT**

IvyGPT，一款医疗大模型，经过高质量的医学问答数据监督微调和人类反馈强化学习训练，展现了出色的智能医疗处理能力。

**项目地址**：https://github.com/WangRongsheng/IvyGPT



### **18、PULSE**

本项目开源了中文医疗大模型PULSE，该模型采用约4,000,000个中文医学与通用领域指令微调数据进行优化，支持广泛的医疗领域自然语言处理任务，包括健康教育、医师考试问题解答、报告解读、医疗记录结构化以及模拟诊断和治疗等。

**项目地址**：https://github.com/openmedlab/PULSE



### **19、HuangDI (皇帝）**

HuangDI，一款中医大模型，其独特之处在于融合了中医教材、网站数据与Ziya-LLaMA-13B-V1基座模型，打造出具有深厚中医知识理解力的预训练模型，并通过海量中医古籍指令对话数据与通用指令数据进行微调，实现中医古籍知识问答的精准能力。

**项目地址**：https://github.com/Zlasejd/HuangDI



### **20、ZhongJing (仲景）**

ZhongJing，一个旨在传承中医精髓与现代技术相结合的中医大模型。该项目不仅弘扬了中医的博大精深，还通过现代技术创新，为医学领域提供了可信赖和专业的工具，是中医与AI融合的杰出代表。

**项目地址**：https://github.com/pariskang/CMLM-ZhongJing



### **21、TCMLLM**

该项目旨在通过大型模型技术，实现中医临床辅助诊疗（包括病证诊断、处方推荐等）以及中医药知识问答等多项任务，引领中医知识问答与临床辅助诊疗等领域的飞跃性进步。当前，我们已针对中医临床智能诊疗中的处方推荐问题，发布了TCMLLM-PR这一中医处方推荐大模型。该模型通过整合真实世界的临床病历、医学典籍与中医教科书等海量数据，精心构建了包含68k数据条目的处方推荐指令微调数据集，并在ChatGLM大模型上进行深度优化与微调。

**项目地址**：https://github.com/2020MEAI/TCMLLM



### **22、OpenBioMed**

该项目致力于开源多模态生物医学大模型，涵盖了BioMedGPT这一多模态生物医药大模型、DrugFM和MolFM等多模态小分子基础模型，以及CellLM等细胞表示学习模型。

**项目地址**：https://github.com/PharMolix/OpenBioMed

**论文地址**：https://arxiv.org/abs/2308.09442



### 23、**PromptCBLUE医疗评测基准**

PromptCBLUE是一个针对中文医疗场景的评测基准，通过二次开发CBLUE基准，将16种不同的医疗场景NLP任务全面转化为基于提示的语言生成任务，为中文医疗领域的研究提供了有力的支持。

**项目地址**：https://github.com/michael-wzhu/PromptCBLUE

**论文地址**：https://arxiv.org/abs/2308.04823



### 24、**中文医疗模型评估基准CMB**

A Comprehensive Medical Benchmark in Chinese（CMB）是一项综合性的中文医疗模型评估基准，它涵盖了不同临床职业、不同职业阶段考试中的多项选择题（CMB-Exam）以及基于真实病例的复杂临床诊断问题（CMB-Clin），为中文医疗模型的评估提供了全面的参考。

**论文地址**：https://arxiv.org/abs/2308.08833

**项目地址**：https://github.com/FreedomIntelligence/CMB



**二、4大心理健康领域大模型**
-----------------



### **1、MeChat**

该项目致力于开源中文心理健康支持对话大模型与数据集。该模型基于ChatGLM-6B LoRA 16-bit指令进行了细致的微调。同时，我们通过ChatGPT技术将真实的心理互助QA改写为多轮的心理健康支持多轮对话，构建了含有56k个多轮对话的丰富数据集。该数据集的主题、词汇和篇章语义丰富多样，特别适用于长程多轮对话的应用场景。

**项目地址**：https://github.com/qiuhuachuan/smile



### 2、SoulChat (灵心）

该项目开源了心理健康大模型SoulChat（灵心）。该模型源于ChatGLM-6B的深厚底蕴，经过百万规模心理咨询领域的中文长文本指令与多轮共情对话数据的精心微调，得以诞生。它不仅仅是一个模型，更是人们心灵的守护者，静静倾听，深情理解。

**项目地址：**https://github.com/scutcyr/SoulChat



### 3、MindChat（漫谈）

这一项目致力于开源心理大模型MindChat。经过人工精心清洗的约20万条高质量多轮心理对话数据，涵盖了工作、家庭、学习、生活、社交、安全等多个层面，为模型的训练提供了丰富的素材。MindChat期望从心理咨询、心理评估、心理诊断、心理治疗四个维度，为人们带来心灵的慰藉与解脱，提升整体的心理健康水平。

**项目地址：**https://github.com/X-D-Lab/MindChat



### 4、QiaoBan（巧板）

在儿童情感陪伴领域，QiaoBan这一儿童情感对话大模型应运而生。它基于开源通用大模型，融合了通用域人机对话、单轮指令数据以及专为儿童设计的情感陪伴对话数据，经过精心微调，最终形成了这款专为儿童量身打造的情感陪伴大模型。

**项目地址：**https://github.com/HIT-SCIR-SC/QiaoBan



**三、10大法律领域微调模型及2大评测基准**
------------------------

### 1、LawGPT\_zh（獬豸）

这一中文法律通用模型源自ChatGLM-6B与LoRA 16-bit指令的精心融合。数据集方面，项目团队不仅利用了现有的法律问答数据集，更通过self-Instruct技术，基于法条和真实案例构建了高质量的法律文本问答数据，大幅提升了模型在法律领域的表现，确保了回答的专业性和可靠性。

**项目地址：**https://github.com/LiuHC0428/LAW-GPT



### 2、LaWGPT

LaWGPT系列模型在通用中文基座模型的基础上，增添了法律领域的专有词表和大规模中文法律语料，极大地增强了模型在法律领域的基础语义理解能力。结合法律领域对话问答数据集、中国司法考试数据集的指令精调，LaWGPT对法律内容的理解和执行能力得到了显著提升。

**项目地址：**https://github.com/pengxiao-song/LaWGPT



### 3、LexiLaw

LexiLaw，这一中文法律大模型，以ChatGLM-6B为架构基础，经过法律领域数据的精心微调，使得其在法律咨询与支持方面展现出卓越的性能和专业性。无论是法律从业者、学生还是普通用户，LexiLaw都能为他们提供准确、可靠的法律咨询服务，助力他们在法律问题的海洋中乘风破浪。

**项目地址：**https://github.com/CSHaitao/LexiLaw



### 4、Lawyer LLaMA

这一项目开源了法律领域的指令微调数据和基于LLaMA训练的中文法律大模型Lawyer LLaMA。Lawyer LLaMA以其卓越的性能和深度，为法律领域带来了前所未有的创新与突破。LLaMA经过大规模法律语料库的预训练，深入系统地学习了中国的法律知识体系。在此基石之上，我们借助ChatGPT的智慧，搜集了一系列针对中国国家统一法律职业资格考试客观题的分析和法律咨询的回答，并通过对这些宝贵数据的指令微调，使模型具备了将法律知识灵活应用于各种具体场景的能力。

**项目地址：**https://github.com/AndrewZhe/lawyer-llama

**论文地址：**https://arxiv.org/abs/2305.15062



### 5、HanFei (韩非）

HanFei-1.0作为国内首个全参数训练的法律大模型，拥有高达7b的参数量，其功能涵盖法律问答、多轮对话、文章撰写、检索等多元化需求。

**项目地址：**https://github.com/siat-nlp/HanFei



### 6、ChatLaw

北京大学开源的法律大模型系列——ChatLaw，依托海量的法律新闻、论坛、法条、司法解释、法律咨询、法考题及判决文书等原始文本，构建了丰富的对话数据。ChatLaw-13B和ChatLaw-33B便是基于姜子牙-13B、Anima-33B的卓越训练成果。同时，ChatLaw-Text2Vec更是利用93万条判决案例，基于BERT训练出相似度匹配模型，精准匹配用户提问与对应法条。

**项目地址：**https://github.com/PKU-YuanGroup/ChatLaw

**论文地址：**https://arxiv.org/abs/2306.16092



### 7、Lychee (律知）

我们开源了基于GLM-10B模型的中文司法领域大模型Law-GLM-10B，经过30GB中文法律数据的指令微调，展现出卓越的司法领域应用能力。

**项目地址：**https://github.com/davidpig/lychee\_law



### 8、wisdomInterrogatory (智海-录问）

由浙江大学、阿里巴巴达摩院及华院计算携手打造的法律大模型，该模型基于Baichuan-7B进行了法律领域数据的深度预训练与指令微调，并独具匠心地设计了知识增强的推理流程。

**项目地址：**https://github.com/zhihaiLLM/wisdomInterrogatory



### 9、JurisLMs

该项目基于丰富的中文法学语料库，精心训练了一系列法律领域的语言模型，包括：

- AI Judge——一款可解释的法律判决预测模型，由GPT2在法学语料上深化预训练，并结合法条适用模型（基于BERT的分类器）微调而成，不仅能精准预测判决结果，更能阐述法院的审理观点；

- AI Lawyer——一款智能法律咨询模型，通过主动学习在有限的数据上进行精细微调，能够针对用户咨询，精确匹配并应用相应的法律法规进行回答。

**项目地址：**https://github.com/seudl/JurisLMs



### 10、夫子•明察司法大模型

该模型汇聚了法律领域的智慧，致力于司法领域的深度应用与探索。以ChatGLM为基石，我们精心构建了一个中文司法大模型，它依托海量的中文无监督司法语料与精准的有监督司法微调数据。这款模型功能丰富，涵盖法条检索、案例分析、三段论推理判决以及司法对话等，致力于为用户提供全面且精准的法律咨询与解答服务。

**项目地址：**https://github.com/irlab-sdu/fuzi.mingcha



在法律评测领域，LEXTREME作为一个多语言的法律评测基准，覆盖24种语言，拥有11个评测数据集，其权威性和全面性备受认可。

**项目地址：**https://github.com/JoelNiklaus/LEXTREME

**论文地址：**https://arxiv.org/abs/2301.13126



另一法律评测基准LexGLUE，专注于英文法律评测，以其独特的视角和深度在业界获得了广泛认可。

**项目地址：**https://github.com/coastalcph/lex-glue

**论文地址：**https://arxiv.org/abs/2110.00976



**四、10大金融领域微调模型及3大评测基准**
------------------------

### 1、BBT-FinCUGE-Applications

该项目不仅开源了中文金融领域语料库BBT-FinCorpus，还推出了知识增强型大模型BBT-FinT5及评测基准CFLEB，展现了其在金融领域的深厚积累。

**论文地址：**https://arxiv.org/abs/2302.09432

**项目地址：**https://github.com/ssymmetry/BBT-FinCUGE-Applications



### 2、Cornucopia (聚宝盆）

该项目凭借对公开和爬取的中文金融领域问答数据的深入挖掘，构建了独特的指令数据集，并对LLaMA系模型进行了精准指令微调，显著提升了模型在金融领域的问答效果。

**项目地址：**https://github.com/jerry1993-tech/Cornucopia-LLaMA-Fin-Chinese



### 3、XuanYuan (轩辕）

作为国内首个开源的千亿级中文对话大模型，轩辕更是针对中文金融领域进行了深度优化。它基于BLOOM-176B进行了针对性预训练与微调，既能处理通用领域问题，又能提供全面且准确的金融信息与建议。

**项目地址：**https://github.com/Duxiaoman-DI/XuanYuan

**论文地址：**https://arxiv.org/abs/2305.12002



### 4、PIXIU (貔貅）

本项目公开了金融领域的指令微调数据集FIT，以及大型模型FinMA与评估基准FLARE，为金融领域注入了智能化新动力。

**项目地址：**https://github.com/chancefocus/PIXIU

**论文地址：**https://arxiv.org/abs/2306.05443 



### 5、FinGPT

本项目贡献了多个金融领域的大模型，涵盖ChatGLM2-6B+LoRA和LLaMA2-7B+LoRA等，并汇集了金融新闻、社交媒体、财报等多维度中英文训练数据。

**项目地址：**https://github.com/AI4Finance-Foundation/FinGPT

**论文地址：**https://arxiv.org/abs/2306.06031



### 6、FLANG

本项目倾力打造了金融大模型FLANG，为金融行业的智能化发展再添新翼。

**项目地址：**https://github.com/SALT-NLP/FLANG

**论文地址：**https://arxiv.org/abs/2211.00083



### 7、FinEval

FinEval，一个专注于金融知识的评测基准，汇聚了4,661道高质量多项选择题，覆盖金融、经济、会计、证书等多个领域，涉及34个不同学术科目。

**项目地址：**https://github.com/SUFE-AIFLM-Lab/FinEval

**论文地址：**https://arxiv.org/abs/2308.09975



### 8、金融领域评测基准：FLARE

FLARE，一个专为金融领域打造的评测基准，它涵盖了金融知识理解和预测等任务，助力金融行业智能化发展。

**项目地址：**https://github.com/chancefocus/PIXIU

**论文地址：**https://arxiv.org/abs/2306.05443



### 9、金融领域评测基准：CFLEB

CFLEB，一个面向中文金融领域的评测基准，包含了语言生成与理解的多项任务，为中文金融领域智能化评测提供了有力工具。

**项目地址：**https://github.com/ssymmetry/BBT-FinCUGE-Applications

**论文地址：**https://arxiv.org/abs/2302.09432



### 10、金融领域评测基准：FLUE

FLUE，作为金融评测基准的新星，汇集了5个金融领域数据集，为金融智能化评测提供了全新视角。

**项目地址：**https://github.com/SALT-NLP/FLANG

**论文地址：**https://arxiv.org/abs/2211.00083



**五、两大教育领域引领潮流的大模型**
--------------------

### 1、桃李 (Taoli）

该项目引领了国际中文教育领域的潮流，通过开源大模型，汇集了500余册国际中文教育教材与教辅书、汉语水平考试试题以及汉语学习者词典等资源，构建了国际中文教育资源库。精心设计的88000条高质量问答数据集，让模型在国际中文教育场景中灵活应用知识。

**项目地址：**https://github.com/blcuicall/taoli



### 2、EduChat

该项目在教育垂直领域展现出了卓越的对话能力，其大模型融合了多样化的教育资源，并通过指令微调、价值观对齐等方法，为教育场景下的出题、作业批改、情感支持等提供了全面支持。它服务于教师、学生和家长，致力于实现智能化、个性化的教育。

**项目地址：**https://github.com/icalk-nlp/EduChat

**论文地址：**https://arxiv.org/abs/2308.02773



**六、自媒体领域的创新之作**
----------------

### 1、MediaGPT

该项目展示了中文自媒体领域的新锐力量，通过在大规模自媒体语料上进行预训练，系统地学习自媒体知识体系。借助ChatGPT等技术，MediaGPT在抖音运营、短视频创作等领域展现出卓越的实际应用能力。

**项目地址：**https://github.com/IMOSR/MediaGPT



**七、电商领域的佼佼者**
--------------

### 1、EcomGPT

该项目推出的电商大模型EcomGPT，凭借其出色的性能，在电商领域内脱颖而出。基于BLOOMZ在电商领域的指令微调数据集，EcomGPT在多个电商评测数据集上超越了ChatGPT，为电商领域带来了智能化的新体验。

**项目地址：**https://github.com/Alibaba-NLP/EcomGPT

**论文地址：**https://arxiv.org/abs/2308.06966



**八、政务领域的智慧选择**
---------------

### 1、YaYi (雅意)

该项目推出的多领域大模型YaYi (雅意)，凭借其百万级高质量领域数据和上百种自然语言指令任务，为媒体宣传、舆情分析、公共安全等领域提供了智慧化的解决方案。

**项目地址：**https://github.com/wenge-research/YaYi



**九、天文地理领域的璀璨之星**
-----------------

### 1、StarGLM

该项目正式发布了天文大模型StarGLM，它依托于司天工程的丰富语料与知识库，经过精细训练而成。StarGLM的诞生，旨在破解大语言模型在天文知识及前沿变星领域所面临的挑战，从而进一步夯实了未来在天文多模态任务中的基础，并为望远镜阵列中的司天大脑（数据智能处理系统）的部署铺平了道路。

**项目地址：**https://github.com/Yu-Yang-Li/StarGLM



### 2、K2

K2，这款地球科学大模型，其灵感源于LLaMA，并巧妙地融合了地球科学文献与维基百科的精髓。进一步的指令微调，更是在GeoSignal数据集的滋养下得以实现。

**项目地址：**https://github.com/davendw49/k2

**论文地址：**https://arxiv.org/abs/2306.05064



### 3、天文地理领域的璀璨之星——GeoGLUE

GeoGLUE，这一由阿里巴巴达摩院与高德联袂推出的地理语义理解评测基准，旨在点燃地理文本处理技术的火花，推动社区共荣。多个核心场景被精心提炼，包括地图搜索、电商物流、政府登记与金融交通等，每个场景都围绕六大核心任务展开：门址地址要素解析、地理实体对齐、Query-POI库召回、Query-POI相关性排序、地址Query成分分析以及WhereWhat切分。

**项目地址：**https://modelscope.cn/datasets/damo/GeoGLUE/summary

**论文地址：**https://arxiv.org/abs/2305.06545



**十、交通领域的璀璨新星**
---------------

### 1、TransGPT (致远）

TransGPT，这一交通领域的明星大模型，以“致远”为名，寓意深远。它深植于真实交通行业，致力于实现多种实用功能，包括交通情况预测、智能咨询助手、公共交通服务、交通规划设计、交通安全教育、协助管理、交通事故报告与分析以及自动驾驶辅助系统等。TransGPT作为通用常识交通大模型，为道路工程、桥梁工程、隧道工程、公路运输、水路运输、城市公共交通运输、交通运输经济、交通运输安全等行业提供了广博的通识知识。以之为基石，可以灵活运用于各种交通应用场景。

**项目地址：**https://github.com/DUOMO/TransGPT



**十一、网络安全领域的守护者**
-----------------

### 1、AutoAudit

AutoAudit，这款网络安全大模型，犹如网络安全领域的守护者，以强大的自然语言处理能力为安全审计和网络防御提供了坚实的后盾。它具备分析恶意代码、检测网络攻击、预测安全漏洞等能力，为安全专业人员提供了不可或缺的支持。

**项目地址：**https://github.com/ddzipp/AutoAudit



**十二、科技前沿的两大模型**
----------------

### 1、TechGPT

TechGPT，这款科研领域的巨星模型，其潜力与应用价值正逐步被发掘。在未来的科研道路上，它将发挥出无可替代的作用。我们荣幸地宣布，我们已成功开源了一款卓越的科技大模型——TechGPT。该模型专注于计算机科学、材料、机械、冶金、金融及航空航天等十余种专业领域，深度集成了领域术语抽取、命名实体识别、关系三元组抽取等先进功能。不仅如此，TechGPT还拥有文本关键词生成、标题生成摘要、文本领域识别等自然语言理解和生成能力，进一步拓展了其在机器阅读理解、基础常识问答、基于上下文的知识问答等多个场景的应用。其出色的文案生成、中英互译以及简单代码生成功能，无疑将为科研人员和技术开发者提供极大的便利。

**项目地址：**https://github.com/neukg/TechGPT



### 2、开源科技论文大模型——Mozi（墨子）

这款模型专为科技文献问答和情感分析设计，旨在为用户提供精准的文献解答与深入的情感洞察。

**项目地址：**https://github.com/gmftbyGMFTBY/science-llm

**论文地址：**https://github.com/gmftbyGMFTBY/science-llm/blob/main/asset/mozi\_technical\_report.pdf

