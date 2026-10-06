# 图表规范

## 教学要求

每张图必须包含标题、要解决的教学问题、阅读顺序说明和验证状态。正文在图后解释
读法与限制。装饰性图片不计入图表要求。

## 选择顺序

1. 流程、架构、时序、状态、数据流和依赖优先使用 Mermaid。
2. Mermaid 不适合连续空间或数值关系时，使用可复现绘图脚本。
3. 小型结构可用 ASCII、Markdown 表格、公式或伪代码。

## Mermaid 安全子集

- 优先 `flowchart`、`sequenceDiagram`、`stateDiagram-v2` 和简单 `erDiagram`。
- 节点 ID 使用 ASCII；中文只放标签。
- 避免实验语法、复杂 HTML、过深子图和超大单图。
- 复杂系统拆成概览、数据面、控制面或失败路径多张图。
- 源文件放在 `assets/diagrams/`，章节通过相对链接或内嵌受控代码块引用。

## 状态

- `planned`：只完成图的需求登记。
- `static-checked`：通过仓库静态规则和人工阅读检查，未证明 Mermaid 解析成功。
- `rendered`：真实解析或渲染成功，并在 `reports/diagram-validation.md` 记录命令和环境。
- `visual-reviewed`：在 rendered 基础上检查可读性、标签、布局和教学价值。

当前环境没有 `mmdc`，因此在真实渲染器可用前，任何 Mermaid 最多标为
`static-checked`。

## 关键图登记

D01 至 D20 的标题、主文件和最低验证要求见 `PROJECT_PLAN.md`；状态和证据见
`ACCEPTANCE_MATRIX.md` 与 `reports/diagram-validation.md`。
