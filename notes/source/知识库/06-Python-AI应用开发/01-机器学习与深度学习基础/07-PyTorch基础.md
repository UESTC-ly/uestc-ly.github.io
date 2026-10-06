# 第 07 课：PyTorch 基础与第一个二分类神经网络

## 1. 学习目标

本课把神经网络的数学训练流程落实为 PyTorch 代码，重点掌握：

- Tensor 的概念、形状与基本创建方式；
- 使用 `nn.Module` 和 `nn.Sequential` 定义神经网络；
- 二分类中的 logit、Sigmoid 与概率；
- `BCEWithLogitsLoss` 的正确用法；
- 自动微分、反向传播与优化器的职责；
- 完整训练循环、mini-batch 训练和模型评估；
- 参数与超参数的区别；
- 常见的形状、类型、梯度和评估模式错误。

前置内容参见：[第 06 课：神经网络、损失函数、梯度下降与反向传播](./06-神经网络、损失函数、梯度下降与反向传播.md)。

## 2. 从数学训练流程到 PyTorch API

神经网络可以写成：

$$
\hat{y}=f(X;\theta)
$$

其中：

- $X$：输入数据；
- $\theta$：模型中的权重和偏置；
- $\hat{y}$：预测结果；
- $f$：神经网络表示的参数化函数。

训练过程可以概括为：

$$
X
\rightarrow
\hat{y}
\rightarrow
L(y,\hat{y})
\rightarrow
\nabla_\theta L
\rightarrow
\theta-\eta\nabla_\theta L
$$

它在 PyTorch 中通常对应：

```python
logits = model(X)              # 前向传播
loss = criterion(logits, y)    # 计算损失
optimizer.zero_grad()          # 清空旧梯度
loss.backward()                # 反向传播，计算梯度
optimizer.step()               # 根据梯度更新参数
```

各部分的职责必须区分：

| 组件 | 职责 |
|---|---|
| 模型 | 根据输入完成前向传播并产生预测 |
| 损失函数 | 衡量预测结果与真实标签之间的差异 |
| `backward()` | 沿计算图反向应用链式法则，计算参数梯度 |
| 优化器 | 使用已经计算出的梯度更新模型参数 |

## 3. Tensor：PyTorch 的基本数据结构

Tensor（张量）可以理解为多维数组：

| 维度 | 含义 | 示例 |
|---|---|---|
| 0 维 | 标量 | `3.14` |
| 1 维 | 向量 | `[1, 2, 3]` |
| 2 维 | 矩阵 | 多行多列的数据 |
| 3 维及以上 | 高维张量 | 图片、视频或批量数据 |

创建张量：

```python
import torch

scalar = torch.tensor(3.14)
vector = torch.tensor([1.0, 2.0, 3.0])
matrix = torch.tensor([
    [1.0, 2.0],
    [3.0, 4.0]
])

print(scalar.shape)  # torch.Size([])
print(vector.shape)  # torch.Size([3])
print(matrix.shape)  # torch.Size([2, 2])
```

### 3.1 样本数与特征数

假设有 1000 个样本，每个样本包含 2 个特征：

```python
X = torch.randn(1000, 2)
```

其形状 `[1000, 2]` 表示：

```text
1000 个样本 × 每个样本 2 个特征
```

若二分类任务中每个样本对应一个标签，可以创建：

```python
y = torch.randint(0, 2, (1000, 1)).float()
```

标签形状为 `[1000, 1]`。理解并检查张量形状非常重要，许多 PyTorch 错误本质上都是维度不匹配。

## 4. 构造一个二分类数据集

下面构造一个带少量噪声的二分类数据集。每个样本包含特征 $x_1$ 和 $x_2$，分类规则近似为：

$$
2x_1-x_2+0.5>0
$$

满足条件时标签为 1，否则为 0。

```python
import torch

torch.manual_seed(42)

# 1000 个样本，每个样本有两个特征
X = torch.randn(1000, 2)

# 加入少量噪声
noise = 0.3 * torch.randn(1000)
scores = 2 * X[:, 0] - X[:, 1] + 0.5 + noise

# 布尔结果转为浮点标签，并由 [1000] 调整为 [1000, 1]
y = (scores > 0).float().unsqueeze(1)

print(X.shape)  # torch.Size([1000, 2])
print(y.shape)  # torch.Size([1000, 1])
```

切片含义：

- `X[:, 0]`：所有样本的第一个特征；
- `X[:, 1]`：所有样本的第二个特征；
- `unsqueeze(1)`：在第 1 维增加一个维度，将 `[1000]` 变为 `[1000, 1]`。

### 4.1 划分训练集和测试集

```python
train_size = 800

X_train = X[:train_size]
y_train = y[:train_size]

X_test = X[train_size:]
y_test = y[train_size:]

print(X_train.shape)  # [800, 2]
print(X_test.shape)   # [200, 2]
```

本例使用 800 个训练样本和 200 个测试样本。正式项目通常还需要单独划分验证集，用于调参、早停和选择模型；测试集应尽量只用于最终评估。

## 5. 使用 `nn.Module` 定义网络

PyTorch 中的神经网络通常继承 `torch.nn.Module`：

```python
import torch.nn as nn


class BinaryClassifier(nn.Module):
    def __init__(self):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(2, 8),
            nn.ReLU(),
            nn.Linear(8, 1)
        )

    def forward(self, x):
        return self.network(x)


model = BinaryClassifier()
print(model)
```

网络结构为：

```text
2 个输入特征
    ↓
8 个隐藏神经元
    ↓
ReLU 激活函数
    ↓
1 个输出值
```

### 5.1 各层的含义

`nn.Linear(2, 8)` 是一个全连接层：输入维度为 2，输出维度为 8。其核心计算为：

$$
z=XW+b
$$

`nn.ReLU()` 对每个元素应用：

$$
\operatorname{ReLU}(z)=\max(0,z)
$$

`nn.Linear(8, 1)` 将 8 个隐藏特征组合为一个输出。该输出不是概率，而是一个任意实数，称为 **logit**。

## 6. Logit、Sigmoid 与概率

二分类模型可能输出如下 logits：

```text
-2.5
 0.8
 3.1
```

Sigmoid 可以把 logit 映射到 $(0,1)$，得到正类概率：

$$
p=\sigma(z)=\frac{1}{1+e^{-z}}
$$

```python
probabilities = torch.sigmoid(logits)
predictions = (probabilities >= 0.5).float()
```

| Logit | 概率（约） | 阈值为 0.5 时的类别 |
|---:|---:|---:|
| $-2.0$ | $0.12$ | 0 |
| $0$ | $0.50$ | 1（使用 `>= 0.5` 时） |
| $2.0$ | $0.88$ | 1 |

阈值不一定永远使用 0.5。实际项目可结合 Precision、Recall、F1 或业务成本，在验证集上选择阈值。

## 7. 二分类损失：`BCEWithLogitsLoss`

二分类任务可使用：

```python
criterion = nn.BCEWithLogitsLoss()
```

它在一个数值稳定的实现中组合了：

```text
Sigmoid + 二元交叉熵
```

二元交叉熵为：

$$
L=-\left[y\log(p)+(1-y)\log(1-p)\right]
$$

### 7.1 不要重复添加 Sigmoid

使用 `BCEWithLogitsLoss` 时，模型最后一层应直接输出 logits，不要再添加 `nn.Sigmoid()`。

正确写法：

```python
self.network = nn.Sequential(
    nn.Linear(2, 8),
    nn.ReLU(),
    nn.Linear(8, 1)
)

criterion = nn.BCEWithLogitsLoss()
```

不推荐的写法：

```python
self.network = nn.Sequential(
    nn.Linear(2, 8),
    nn.ReLU(),
    nn.Linear(8, 1),
    nn.Sigmoid()
)

criterion = nn.BCEWithLogitsLoss()
```

训练时应直接将 logits 交给损失函数：

```python
logits = model(X)
loss = criterion(logits, y)
```

只有在评估、分类或展示概率时，才显式调用：

```python
probabilities = torch.sigmoid(logits)
```

## 8. 优化器：SGD 与 Adam

先使用 Adam：

```python
optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.01
)
```

其中：

- `model.parameters()`：将模型中所有可训练参数交给优化器；
- `lr`：学习率，决定每次更新的大致步幅。

优化器不负责计算损失或梯度，它负责根据反向传播得到的梯度真正更新参数。

### 8.1 SGD

```python
optimizer = torch.optim.SGD(
    model.parameters(),
    lr=0.01
)
```

最基本的 SGD 更新为：

$$
\theta\leftarrow\theta-\eta\nabla_\theta L
$$

特点：

- 原理简单、容易理解；
- 某些任务中具有较好的泛化表现；
- 可能收敛较慢，对学习率相对敏感。

### 8.2 Adam

```python
optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.001
)
```

Adam 利用历史梯度信息，自适应调整不同参数的更新幅度，通常收敛较快，适合作为许多任务的起点。但 Adam 并不保证始终优于 SGD，优化器也应根据验证结果选择。

## 9. 基本训练循环

```python
epochs = 100

for epoch in range(epochs):
    model.train()

    # 1. 前向传播
    logits = model(X_train)

    # 2. 计算损失
    loss = criterion(logits, y_train)

    # 3. 清空上一轮梯度
    optimizer.zero_grad()

    # 4. 反向传播
    loss.backward()

    # 5. 更新参数
    optimizer.step()

    if (epoch + 1) % 10 == 0:
        print(
            f"Epoch {epoch + 1:3d}, "
            f"Loss: {loss.item():.4f}"
        )
```

核心顺序是：

```text
前向传播
→ 计算损失
→ 清空旧梯度
→ 反向传播
→ 更新参数
```

### 9.1 为什么必须清空梯度

PyTorch 默认会累加梯度。假设连续两次反向传播得到的梯度分别为 2 和 3，如果不清空，参数的 `.grad` 中可能累计为 5。

普通训练通常希望每个 batch 独立计算梯度，因此标准顺序为：

```python
optimizer.zero_grad()
loss.backward()
optimizer.step()
```

有意进行梯度累积时才会跳过部分 `zero_grad()`，但这属于明确设计的训练策略。

## 10. 模型评估

```python
model.eval()

with torch.no_grad():
    test_logits = model(X_test)
    test_probabilities = torch.sigmoid(test_logits)
    test_predictions = (test_probabilities >= 0.5).float()

    accuracy = (
        test_predictions == y_test
    ).float().mean()

print(f"Test Accuracy: {accuracy.item():.4f}")
```

### 10.1 `model.eval()`

将模型切换到评估模式。如果网络包含 Dropout 或 Batch Normalization，训练模式和评估模式下的行为不同。当前简单网络没有这些层，但保留这一调用是良好习惯。

重新开始训练前应调用：

```python
model.train()
```

### 10.2 `torch.no_grad()`

评估时不需要反向传播。关闭梯度记录可以：

- 避免构建不必要的计算图；
- 减少内存占用；
- 提高评估效率。

## 11. 使用 mini-batch 训练

前面的示例一次使用全部 800 个训练样本计算梯度，属于全批量训练。真实数据通常更大，一般使用 mini-batch。

```python
from torch.utils.data import TensorDataset, DataLoader

train_dataset = TensorDataset(X_train, y_train)

train_loader = DataLoader(
    train_dataset,
    batch_size=32,
    shuffle=True
)
```

训练循环改为：

```python
epochs = 100

for epoch in range(epochs):
    model.train()
    total_loss = 0.0

    for batch_X, batch_y in train_loader:
        logits = model(batch_X)
        loss = criterion(logits, batch_y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # loss.item() 是当前 batch 的平均损失，乘样本数后再汇总
        total_loss += loss.item() * batch_X.size(0)

    average_loss = total_loss / len(train_dataset)

    if (epoch + 1) % 10 == 0:
        print(
            f"Epoch {epoch + 1:3d} | "
            f"Loss: {average_loss:.4f}"
        )
```

关键参数：

- `batch_size=32`：每次使用 32 个样本计算梯度并更新一次参数；
- `shuffle=True`：每个 epoch 重新打乱训练样本，减少固定顺序带来的影响。

## 12. 自动微分与计算图

假设网络执行：

$$
z_1=XW_1+b_1
$$

$$
a_1=\operatorname{ReLU}(z_1)
$$

$$
z_2=a_1W_2+b_2
$$

$$
L=L(z_2,y)
$$

调用：

```python
loss.backward()
```

PyTorch 会沿计算图反向应用链式法则，计算：

$$
\frac{\partial L}{\partial W_2},\quad
\frac{\partial L}{\partial b_2},\quad
\frac{\partial L}{\partial W_1},\quad
\frac{\partial L}{\partial b_1}
$$

可以在 `loss.backward()` 之后查看某一层的梯度：

```python
print(model.network[0].weight.grad)
print(model.network[0].bias.grad)
```

`backward()` 只负责计算和累积梯度；参数要等到 `optimizer.step()` 才会被更新。

## 13. 参数与超参数

### 13.1 参数

参数由模型从训练数据中学习，例如：

- 权重；
- 偏置。

可通过以下接口访问：

```python
model.parameters()
```

### 13.2 超参数

超参数由开发者在训练前设置，例如：

- 学习率；
- batch size；
- epoch 数量；
- 隐藏层数量；
- 每层神经元数量；
- 优化器类型。

```python
learning_rate = 0.01
batch_size = 32
epochs = 100
hidden_size = 8
```

模型不会通过普通反向传播自动决定这些超参数，通常需要根据验证集表现进行选择。

## 14. 完整二分类示例

```python
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader


# =========================
# 1. 创建数据
# =========================

torch.manual_seed(42)

X = torch.randn(1000, 2)
noise = 0.3 * torch.randn(1000)
scores = 2 * X[:, 0] - X[:, 1] + 0.5 + noise
y = (scores > 0).float().unsqueeze(1)


# =========================
# 2. 划分数据
# =========================

train_size = 800

X_train = X[:train_size]
y_train = y[:train_size]
X_test = X[train_size:]
y_test = y[train_size:]

train_dataset = TensorDataset(X_train, y_train)
train_loader = DataLoader(
    train_dataset,
    batch_size=32,
    shuffle=True
)


# =========================
# 3. 定义神经网络
# =========================

class BinaryClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(2, 8),
            nn.ReLU(),
            nn.Linear(8, 1)
        )

    def forward(self, x):
        return self.network(x)


model = BinaryClassifier()


# =========================
# 4. 损失函数与优化器
# =========================

criterion = nn.BCEWithLogitsLoss()
optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.01
)


# =========================
# 5. 训练模型
# =========================

epochs = 100

for epoch in range(epochs):
    model.train()
    total_loss = 0.0

    for batch_X, batch_y in train_loader:
        logits = model(batch_X)
        loss = criterion(logits, batch_y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * batch_X.size(0)

    average_loss = total_loss / len(train_dataset)

    if (epoch + 1) % 10 == 0:
        print(
            f"Epoch {epoch + 1:3d} | "
            f"Loss: {average_loss:.4f}"
        )


# =========================
# 6. 测试模型
# =========================

model.eval()

with torch.no_grad():
    test_logits = model(X_test)
    test_probabilities = torch.sigmoid(test_logits)
    test_predictions = (test_probabilities >= 0.5).float()

    test_accuracy = (
        test_predictions == y_test
    ).float().mean()

print(f"Test Accuracy: {test_accuracy.item():.4f}")


# =========================
# 7. 查看部分预测结果
# =========================

with torch.no_grad():
    sample_logits = model(X_test[:5])
    sample_probabilities = torch.sigmoid(sample_logits)
    sample_predictions = (sample_probabilities >= 0.5).float()

print("预测概率：")
print(sample_probabilities)

print("预测类别：")
print(sample_predictions)

print("真实类别：")
print(y_test[:5])
```

该示例覆盖：数据创建、数据划分、`DataLoader`、模型定义、损失函数、优化器、mini-batch 训练、测试集评估和预测展示。本次整理未在本地环境执行代码，实际输出会受 PyTorch 版本和运行环境影响。

## 15. 常见错误与排查

### 15.1 模型输出和标签形状不同

典型错误：

```text
模型输出：[32, 1]
真实标签：[32]
```

可将标签调整为：

```python
y = y.unsqueeze(1)
```

使其形状变为 `[32, 1]`。

### 15.2 标签数据类型不正确

`BCEWithLogitsLoss` 通常要求浮点标签：

```python
y = y.float()
```

多分类的 `CrossEntropyLoss` 则通常要求类别索引为整数类型，不能把不同损失函数的数据要求混淆。

### 15.3 忘记清空梯度

错误或非预期的写法：

```python
loss.backward()
optimizer.step()
```

普通训练应写为：

```python
optimizer.zero_grad()
loss.backward()
optimizer.step()
```

### 15.4 对 `BCEWithLogitsLoss` 重复使用 Sigmoid

训练时直接传入 logits：

```python
logits = model(X)
loss = criterion(logits, y)
```

评估时再转换概率：

```python
probabilities = torch.sigmoid(logits)
```

### 15.5 评估时忘记切换模式或关闭梯度

```python
model.eval()

with torch.no_grad():
    ...
```

继续训练时再调用：

```python
model.train()
```

### 15.6 只看训练准确率

训练集准确率高不代表泛化能力好。还应观察：

- 验证集损失；
- 验证集 Accuracy；
- Precision、Recall 和 F1；
- 与业务目标匹配的指标；
- 最终测试集表现。

## 16. 核心 API 速查

| API | 作用 |
|---|---|
| `torch.tensor(...)` | 创建张量 |
| `tensor.shape` | 查看张量形状 |
| `nn.Module` | 神经网络模块基类 |
| `nn.Linear(in, out)` | 定义全连接层 |
| `nn.ReLU()` | 添加 ReLU 激活函数 |
| `nn.Sequential(...)` | 按顺序组合多个网络层 |
| `model(x)` | 调用 `forward()` 完成前向传播 |
| `nn.BCEWithLogitsLoss()` | 基于 logits 计算稳定的二分类交叉熵 |
| `optimizer.zero_grad()` | 清空已有梯度 |
| `loss.backward()` | 反向传播并计算梯度 |
| `optimizer.step()` | 更新模型参数 |
| `model.train()` | 切换到训练模式 |
| `model.eval()` | 切换到评估模式 |
| `torch.no_grad()` | 关闭梯度记录 |
| `TensorDataset` | 将多个 Tensor 组合成数据集 |
| `DataLoader` | 按 batch 加载并可打乱数据 |

## 17. 本课总结

1. Tensor 是 PyTorch 的基本数据结构，首先要能读懂样本维和特征维。
2. 神经网络通常继承 `nn.Module`，`forward()` 定义前向传播过程。
3. 二分类模型最后一层可以输出一个 logit。
4. `BCEWithLogitsLoss` 已包含稳定的 Sigmoid 与二元交叉熵计算，训练时不要重复添加 Sigmoid。
5. `loss.backward()` 负责计算梯度，`optimizer.step()` 才负责更新参数。
6. PyTorch 默认累加梯度，普通训练每轮需要调用 `optimizer.zero_grad()`。
7. `model.train()` 和 `model.eval()` 分别对应训练与评估模式。
8. 评估阶段通常配合 `torch.no_grad()`，以减少不必要的计算图和内存占用。
9. 大规模数据通常通过 `Dataset`、`DataLoader` 和 mini-batch 训练。
10. 完整训练流程是：

```text
读取 batch
→ 前向传播
→ 计算损失
→ 清空旧梯度
→ 反向传播
→ 更新参数
→ 重复训练
```

一句话记忆：

> PyTorch 使用 `model()` 完成前向传播，使用 `loss.backward()` 计算梯度，再使用 `optimizer.step()` 更新神经网络参数。

## 来源

- 本笔记仅整理本次新增会话中的“第 07 课：使用 PyTorch 训练第一个神经网络”讲解内容，并对重复段落进行了合并。
- 前置概念来自项目现有笔记：[第 06 课：神经网络、损失函数、梯度下降与反向传播](./06-神经网络、损失函数、梯度下降与反向传播.md)。
- 示例代码基于会话中的通用 PyTorch 知识，尚未在本地项目环境中实际执行。
