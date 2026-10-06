# 第 05 课：Accuracy、Precision、Recall、F1 与 AUC

> 所属模块：六、Python AI 应用开发 → 1. 机器学习与深度学习基础  
> 学习顺序：监督学习、无监督学习 → 数据集划分 → 过拟合、欠拟合、正则化 → 分类、回归、聚类 → **分类模型评估指标**  
> 资料说明：本笔记依据本次会话提供的第 05 课内容整理；项目中未检索到本课的独立原始资料。相关基础概念可参阅 [[01-监督学习与无监督学习]]、[[02-训练集、验证集与测试集]]、[[03-过拟合、欠拟合与正则化]] 和 [[04-分类、回归与聚类]]。

## 一、学习目标

完成本课后，应能够：

1. 读懂二分类混淆矩阵中的 TP、FP、TN、FN；
2. 计算并解释 Accuracy、Precision、Recall 和 F1；
3. 理解分类阈值对 Precision、Recall 和告警量的影响；
4. 解释 ROC 曲线、ROC-AUC 以及它们的局限；
5. 在类别不平衡场景下选择更合适的评估指标；
6. 使用 scikit-learn 计算分类指标，并避免测试集泄漏。

---

## 二、为什么不能只看 Accuracy

Accuracy 表示所有样本中预测正确的比例：

$$
Accuracy = \frac{TP + TN}{TP + TN + FP + FN}
$$

当类别严重不平衡时，Accuracy 可能掩盖模型对少数类的无能。

例如，1000 笔交易中有 990 笔正常交易、10 笔欺诈交易。若模型把所有交易都预测为正常，Accuracy 仍然是 99%，但一笔欺诈也没有识别出来。

因此，评估分类模型时不能只看整体正确率，还要结合：

- 模型预测为正类时是否可信；
- 真实正类是否被充分发现；
- 误报和漏报哪一种代价更高；
- 实际业务阈值下的告警数量和处理成本。

---

## 三、混淆矩阵

二分类中通常将目标类别定义为正类（Positive），其他类别定义为负类（Negative）。预测结果可分为四种：

| 真实情况 | 预测为正类 | 预测为负类 |
|---|---:|---:|
| 真实为正类 | TP：真正例 | FN：假负例 |
| 真实为负类 | FP：假正例 | TN：真负例 |

### 3.1 TP：真正例（True Positive）

真实是正类，模型也预测为正类。例如实际为欺诈交易，模型成功识别为欺诈。

### 3.2 FP：假正例（False Positive）

真实是负类，但模型预测为正类，也称误报或第一类错误。例如正常交易被错误拦截。

### 3.3 FN：假负例（False Negative）

真实是正类，但模型预测为负类，也称漏报或漏检。例如欺诈交易被判断为正常。

### 3.4 TN：真负例（True Negative）

真实是负类，模型也预测为负类。例如正常交易被正确放行。

记忆方式：

- 第一个字母表示预测是否正确：`T` 为正确，`F` 为错误；
- 第二个字母表示预测类别：`P` 为正类，`N` 为负类。

在 scikit-learn 中，二分类 `confusion_matrix` 通常按以下顺序返回：

```text
[[TN, FP],
 [FN, TP]]
```

---

## 四、核心指标

以下示例使用同一组混淆矩阵：

```text
TP = 30
FP = 10
FN = 20
TN = 940
```

总样本数为 1000。

### 4.1 Accuracy：准确率

表示全部样本中预测正确的比例：

$$
Accuracy = \frac{TP + TN}{TP + TN + FP + FN}
$$

本例：

$$
Accuracy = \frac{30 + 940}{1000} = 97\%
$$

适用场景：类别比较均衡，且 FP 与 FN 的业务代价相近。

局限：类别不平衡时，模型只预测多数类也可能得到很高的 Accuracy。

### 4.2 Precision：精确率

表示模型预测为正类的样本中，实际为正类的比例：

$$
Precision = \frac{TP}{TP + FP}
$$

本例：

$$
Precision = \frac{30}{30 + 10} = 75\%
$$

它回答的是：

> 模型找出来的正类，有多少是真的？

Precision 主要受 `FP` 影响。误报代价高时，应重点关注 Precision，例如：

- 将正常账户错误冻结；
- 将正常内容直接拦截或删除；
- 将正常邮件放入垃圾箱；
- 自动执行不可逆的高风险操作。

### 4.3 Recall：召回率

表示所有真实正类中，被模型识别出来的比例：

$$
Recall = \frac{TP}{TP + FN}
$$

本例：

$$
Recall = \frac{30}{30 + 20} = 60\%
$$

它回答的是：

> 所有真正的正类，有多少被找到了？

Recall 也称为查全率、敏感度或 TPR（True Positive Rate）。它主要受 `FN` 影响。漏报代价高时，应重点关注 Recall，例如：

- 疾病初筛；
- 欺诈交易初筛；
- 火灾和故障告警；
- 高风险内容发现；
- 安全漏洞检测。

### 4.4 F1 Score

F1 是 Precision 和 Recall 的调和平均数：

$$
F1 = 2 \times \frac{Precision \times Recall}{Precision + Recall}
$$

本例：

$$
F1 = 2 \times \frac{0.75 \times 0.60}{0.75 + 0.60} \approx 66.7\%
$$

F1 的特点：

- Precision 或 Recall 任意一项很低，F1 都会明显下降；
- 适合类别不平衡且同时关心误报、漏报的场景；
- 不考虑 TN，因此不能代替完整的业务分析。

不要把 F1 当作永远最优的指标。如果业务明确更在意漏报或误报，应使用相应指标或自定义成本函数。

### 4.5 F-beta Score

当 Precision 和 Recall 的重要程度不相同时，可以使用 F-beta：

$$
F_\beta = (1+\beta^2)\frac{Precision \times Recall}{\beta^2 \times Precision + Recall}
$$

- `β = 1`：F1，二者权重相同；
- `β > 1`：更重视 Recall，例如 F2；
- `β < 1`：更重视 Precision，例如 F0.5。

---

## 五、Specificity 与 FPR

### 5.1 Specificity：特异度

表示所有真实负类中，被正确识别为负类的比例：

$$
Specificity = \frac{TN}{TN + FP}
$$

### 5.2 FPR：假正例率

表示所有真实负类中，被错误预测为正类的比例：

$$
FPR = \frac{FP}{FP + TN}
$$

二者关系为：

$$
FPR = 1 - Specificity
$$

在前面的示例中：

$$
Specificity = \frac{940}{940+10} \approx 98.95\%
$$

$$
FPR = \frac{10}{10+940} \approx 1.05\%
$$

---

## 六、分类概率与阈值

分类模型通常先输出正类概率或连续分数，再通过阈值转换为最终类别：

```text
P(欺诈 | X) = 0.82
阈值 = 0.50
最终预测 = 欺诈
```

阈值不一定必须是 `0.5`，应根据业务目标在验证集上选择。

### 6.1 降低阈值

通常会使更多样本被预测为正类：

- Recall 往往提高；
- FN 往往减少；
- FP 往往增加；
- Precision 可能下降；
- 告警数量增加。

### 6.2 提高阈值

通常只有更有把握的样本才会被预测为正类：

- Precision 往往提高；
- FP 往往减少；
- Recall 往往下降；
- FN 可能增加；
- 告警数量减少。

这只是一般趋势，具体数值需要在验证数据上实际观察。

### 6.3 阈值选择原则

阈值选择要同时考虑：

- FP 与 FN 的实际成本；
- 可接受的最低 Precision 或 Recall；
- 每天可处理的告警数量；
- 人工审核能力；
- 高风险操作是否需要人工确认。

不能只选择 F1 最高的阈值，也不能只追求某个离线指标。

---

## 七、ROC 曲线与 ROC-AUC

### 7.1 ROC 曲线

ROC（Receiver Operating Characteristic）曲线以：

- 横轴：FPR；
- 纵轴：TPR，也就是 Recall；

展示不同分类阈值下模型的表现。

理想情况下，希望 TPR 高、FPR 低，因此曲线越靠近左上角越好。随机猜测的结果通常接近从左下角到右上角的对角线。

### 7.2 AUC 的含义

AUC（Area Under the ROC Curve）是 ROC 曲线下面积，常见范围是 0 到 1。

它可以直观理解为：

> 随机选择一个正类样本和一个负类样本时，模型将正类的分数排在负类之前的概率。

例如 `AUC = 0.85`，可理解为模型在随机正负样本对上的正确排序概率约为 85%。

经验上：

- `AUC = 1.0`：排序完全正确；
- `AUC ≈ 0.5`：接近随机；
- `AUC < 0.5`：排序方向可能反了。

具体好坏仍然要结合任务、数据和业务要求判断。

### 7.3 AUC 的优点与局限

优点：

- 综合观察多个阈值；
- 衡量模型的整体区分和排序能力；
- 不依赖单一分类阈值。

局限：

- 不告诉你实际线上阈值下的 Precision 和 Recall；
- 不代表输出概率已经校准；
- 极端类别不平衡时可能显得过于乐观；
- 不能代替业务成本和告警量分析。

计算 ROC-AUC 时应使用模型输出的概率或连续分数，而不是最终的 0/1 标签。

---

## 八、ROC-AUC 与 PR-AUC

当正类极其稀少时，例如欺诈率只有 0.1%，ROC-AUC 可能仍然很高，但模型预测为正类的样本中可能只有很少一部分是真正的正类。

此时还应关注 Precision-Recall 曲线以及 PR-AUC，常见实现包括 scikit-learn 的 `average_precision_score`。

简单区分：

| 指标 | 更关注的内容 |
|---|---|
| ROC-AUC | 正负样本的整体排序，使用 TPR 与 FPR |
| PR-AUC | 正类识别效果，使用 Precision 与 Recall |

极端类别不平衡任务中，应同时报告：

- 正类比例；
- Precision；
- Recall；
- F1 或 F-beta；
- PR-AUC；
- 具体阈值下的告警量。

---

## 九、多分类指标的平均方式

多分类任务可以将每个类别轮流当作正类，其他类别作为负类，然后汇总各类别指标。

### 9.1 Macro Average

先分别计算每个类别的指标，再做简单平均：

$$
Macro\text{-}F1 = \frac{F1_1 + F1_2 + \cdots + F1_C}{C}
$$

特点：每个类别权重相同，适合关注少数类别和类别公平性的场景。

### 9.2 Micro Average

先汇总所有类别的 TP、FP、FN，再计算整体指标。

特点：每个样本权重相同，更容易受多数类影响。对于单标签多分类任务，Micro F1 通常与 Accuracy 相同。

### 9.3 Weighted Average

先分别计算每个类别的指标，再按类别样本数量加权平均。

特点：反映真实类别占比，但多数类可能掩盖少数类表现。

实践中最好同时查看：

- 每个类别的 Precision、Recall、F1；
- Macro F1；
- Weighted F1；
- 混淆矩阵。

---

## 十、指标选择与业务场景

| 业务关注点 | 优先关注指标 | 典型场景 |
|---|---|---|
| 整体正确率，类别较均衡 | Accuracy | 一般分类任务 |
| 预测为正类必须可信 | Precision、Specificity、F0.5 | 自动封禁、内容拦截 |
| 尽量找全真实正类 | Recall、F2 | 疾病初筛、故障预警 |
| 同时权衡 FP 和 FN | F1、混淆矩阵 | 一般不平衡分类 |
| 比较整体排序能力 | ROC-AUC | 模型初步比较 |
| 正类极少 | PR-AUC、Precision、Recall | 欺诈、异常、违规检测 |

最终评价应来自业务损失，而不是单纯追求某个数字最高。

例如，欺诈识别模型即使 `ROC-AUC = 0.95`，如果实际阈值下 Precision 只有 8%，也不适合直接自动冻结账户，更适合先做风险初筛、二次审核或人工确认。

---

## 十一、正确的评估流程

```text
划分训练集、验证集、测试集
→ 训练集训练模型
→ 验证集比较模型和超参数
→ 验证集选择分类阈值
→ 固定模型与阈值
→ 测试集做一次最终评估
→ 上线后监控指标和数据分布
```

关键原则：

1. 训练集指标用于判断模型是否学会训练数据；
2. 验证集用于模型选择、超参数调整和阈值选择；
3. 测试集在方案确定后才使用；
4. 不能根据测试集结果反复修改模型，否则测试集信息会泄漏到模型选择过程；
5. 线上还要监控告警量、人工处理成本、延迟、用户反馈和数据分布变化。

---

## 十二、Python 示例

### 12.1 计算基础分类指标

```python
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

y_true = [1, 1, 1, 1, 0, 0, 0, 0]
y_pred = [1, 1, 0, 0, 1, 0, 0, 0]

print("Accuracy:", accuracy_score(y_true, y_pred))
print(
    "Precision:",
    precision_score(y_true, y_pred, zero_division=0),
)
print(
    "Recall:",
    recall_score(y_true, y_pred, zero_division=0),
)
print(
    "F1:",
    f1_score(y_true, y_pred, zero_division=0),
)

print("Confusion matrix:")
print(confusion_matrix(y_true, y_pred))

print("Classification report:")
print(classification_report(y_true, y_pred, zero_division=0))
```

`zero_division=0` 用于处理某一类没有预测样本时的除零情况。实际项目中还应确认正类标签定义正确。

### 12.2 计算 ROC-AUC

```python
from sklearn.metrics import roc_auc_score

y_true = [0, 0, 1, 1]
y_score = [0.10, 0.40, 0.35, 0.80]

# 使用正类概率或连续分数，而不是 0/1 预测标签
auc = roc_auc_score(y_true, y_score)
print("ROC-AUC:", auc)
```

### 12.3 比较不同阈值

```python
from sklearn.metrics import f1_score, precision_score, recall_score

y_true = [1, 0, 1, 0, 1, 0]
y_score = [0.95, 0.80, 0.70, 0.45, 0.40, 0.10]

for threshold in [0.3, 0.5, 0.7, 0.9]:
    y_pred = [
        1 if score >= threshold else 0
        for score in y_score
    ]

    precision = precision_score(
        y_true, y_pred, zero_division=0
    )
    recall = recall_score(
        y_true, y_pred, zero_division=0
    )
    f1 = f1_score(
        y_true, y_pred, zero_division=0
    )

    print(
        f"threshold={threshold:.1f}, "
        f"precision={precision:.3f}, "
        f"recall={recall:.3f}, "
        f"f1={f1:.3f}"
    )
```

---

## 十三、常见误区

1. **只看训练集指标**：训练集高分不代表泛化能力好；
2. **类别不平衡时只看 Accuracy**：多数类可能掩盖少数类完全失效；
3. **混淆 Precision 与 Recall**：Precision 的分母是预测正类，Recall 的分母是真实正类；
4. **把 AUC 传入 0/1 预测标签**：AUC 应使用概率或连续分数；
5. **默认阈值永远是 0.5**：阈值应结合验证集和业务成本选择；
6. **只报告一个多分类平均值**：应检查每个类别，尤其是少数类；
7. **把高 AUC 当作可直接上线**：仍要验证实际阈值、Precision、Recall、告警量和成本；
8. **忽略正类定义**：改变正类后，指标含义也会改变；
9. **把离线指标最高当作业务最优**：还要考虑人工审核能力、延迟和错误损失。

---

## 十四、面试表达模板

> Accuracy 衡量整体预测正确率，但在类别不平衡场景下可能失真。Precision 表示预测为正类的样本中有多少是真正的正类，主要反映误报；Recall 表示真实正类中有多少被识别出来，主要反映漏报。F1 是 Precision 和 Recall 的调和平均数，适合同时关注两类错误的场景。ROC-AUC 则衡量模型在不同阈值下区分正负样本的整体排序能力。实际选择指标和阈值时，还要结合 FP、FN 的业务成本、告警量和人工处理能力。

---

## 十五、自测题

### 题目 1

某模型有：

```text
TP = 80，FP = 20，FN = 40，TN = 860
```

请计算 Accuracy、Precision、Recall、F1 和 FPR。

### 题目 2

疾病筛查中，漏掉患者的代价远高于让健康人进一步检查，应优先关注什么指标？

### 题目 3

降低二分类阈值通常会怎样影响 Precision、Recall、FP 和 FN？

### 题目 4

计算 AUC 时，为什么应使用模型输出的正类概率或连续分数，而不是最终的 0/1 标签？

### 题目 5

一个欺诈识别模型的 ROC-AUC 为 0.95，但实际阈值下 Precision 只有 8%、Recall 为 90%，是否适合直接自动冻结账户？为什么？

### 参考答案

1. `Accuracy = 94%`，`Precision = 80%`，`Recall ≈ 66.7%`，`F1 ≈ 72.7%`，`FPR ≈ 2.27%`；
2. 优先关注 Recall，但仍需控制误报数量；
3. 通常 Recall 提高、FN 减少、FP 增加，Precision 可能下降；
4. 因为 AUC 需要利用不同阈值下的排序信息，0/1 标签已经丢失了大部分分数信息；
5. 不适合直接自动冻结。Precision 过低意味着误冻结风险高，可以改为风险初筛、二次审核或加入人工确认。

---

## 十六、本课小结

- 混淆矩阵中的 `TP、FP、FN、TN` 是分类指标的基础；
- Accuracy 衡量整体正确率，但类别不平衡时可能误导；
- Precision 关注“预测出来的正类准不准”；
- Recall 关注“真实正类找得全不全”；
- F1 综合平衡 Precision 与 Recall；
- F-beta 可以根据业务需要偏向 Precision 或 Recall；
- ROC-AUC 衡量整体排序能力，PR-AUC 在正类稀少时通常更有参考价值；
- 阈值应在验证集上结合业务成本选择；
- 测试集只用于方案确定后的最终评估；
- 线上评估还要关注告警量、人工容量、错误成本、延迟和数据分布变化。

下一课：**神经网络、损失函数、梯度下降、反向传播**。
