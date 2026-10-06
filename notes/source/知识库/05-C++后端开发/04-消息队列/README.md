# 消息队列学习路径

## 学习目标

- 建立生产者、消费者、主题、分区、消费组、ack、重试和死信的完整模型。
- 以 Kafka 为深入主线，理解吞吐、顺序、可靠性、幂等和 exactly-once 的语义边界。
- 能为 AI 异步任务、订单事件、日志采集等场景选择合适的队列设计。

## 核心原理

消息队列把生产和消费解耦，用可持久化日志或队列缓冲峰值流量。Kafka 更像分布式提交日志，RocketMQ 更强调业务消息能力，RabbitMQ 更偏路由灵活和传统 AMQP 队列。

## 工程实践/示例

阅读顺序：

1. [通用原理篇](./01-通用原理.md)
2. [Kafka 深入篇](./02-Kafka深入.md)
3. [可靠性与幂等篇](./03-可靠性与幂等.md)
4. [顺序、积压、延迟、重试与死信](./04-顺序积压延迟重试死信.md)
5. [AI 异步任务实践篇](./05-AI异步任务实践.md)

### 学习依赖

| 前置知识 | 要掌握到什么程度 |
| --- | --- |
| TCP/磁盘顺序写/批处理 | 理解 MQ 高吞吐和延迟来源 |
| 数据库事务 | 能设计 outbox、幂等表和业务状态机 |
| 分布式系统基础 | 理解 leader、副本、ISR、rebalance 和故障窗口 |
| 监控与容量估算 | 能把 lag、吞吐、处理耗时换算成扩容需求 |
| AI 任务基础 | 理解 GPU、batch、token、对象存储和模型版本 |

### 阶段产出

| 阶段 | 阅读范围 | 产出 |
| --- | --- | --- |
| 抽象阶段 | 01 | 画出 queue/log、push/pull、topic/partition/group/offset 模型 |
| Kafka 阶段 | 02 | 输出 broker、partition、leader、replica、ISR、segment、retention 机制图 |
| 可靠性阶段 | 03 | 写出端到端失败矩阵、幂等表、outbox 和 EOS 边界 |
| 稳定性阶段 | 04 | 给出顺序、积压、重试、DLQ 和毒消息排障流程 |
| AI 实战阶段 | 05 | 设计文档解析/Embedding/批推理/评测任务状态机和 GPU 背压策略 |

### 场景索引

| 场景 | 重点章节 | 关键问题 |
| --- | --- | --- |
| 订单事件流 | 01、02、03、04 | 分区键、顺序边界、幂等消费、outbox |
| 邮件/通知任务 | 01、03、04 | 退避重试、死信、外部 API 幂等 |
| 日志采集 | 01、02 | 高吞吐、retention、consumer lag |
| 文档解析 | 05 | 阶段状态、对象存储、失败分类 |
| Embedding/批推理 | 05 | batch、GPU 背压、模型版本和向量幂等 |

### 最小可交付检查

学习完本目录后，应能为一个异步业务链路写清楚：消息体字段、分区键、消费组、可靠性失败矩阵、幂等方案、重试/DLQ 策略、容量估算和监控指标。Kafka EOS 只能写在 Kafka 内部事务范围内；外部数据库、HTTP API 和对象存储必须单独说明幂等或补偿。

## 常见误区

| 误区 | 正确认知 |
| --- | --- |
| MQ 能让所有请求变快 | MQ 改善削峰和解耦，不消灭真实工作量 |
| ack 后就代表业务成功 | ack 语义取决于提交时机和业务事务边界 |
| exactly-once 是端到端魔法 | Kafka EOS 主要约束 Kafka 内部生产、事务和位点提交组合 |
| 分区越多越好 | 分区增加并发，也增加协调、文件句柄和再均衡成本 |

## 自测题

1. Topic、Partition、Consumer Group 的关系是什么？
2. 重复消费为什么几乎不可避免？
3. Kafka、RocketMQ、RabbitMQ 的定位差异是什么？

## 实践任务

- 为“用户上传视频后转码、审核、通知”设计异步任务 Topic 和消费者组。
- 写出消费失败时的重试、死信、人工补偿流程。

## 延伸阅读

- Apache Kafka Documentation：https://kafka.apache.org/documentation/
- RabbitMQ Documentation：https://www.rabbitmq.com/docs
- Apache RocketMQ Documentation：https://rocketmq.apache.org/docs/
