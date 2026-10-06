# macOS / Ubuntu 大模型微调实战教程：LLaMA-Factory + LoRA + DeepSeek-R1-Distill-Qwen-1.5B

本文整理了一次完整跑通的本地微调实战流程，目标是在 `macOS` 或 `Ubuntu` 环境下，用 `LLaMA-Factory` 对 `DeepSeek-R1-Distill-Qwen-1.5B` 做一次 `LoRA SFT` 微调，并在 WebUI 中验证微调效果。

这份教程默认你已经有如下背景：

- 你会用命令行
- 使用 `uv` 管理 Python 环境
- 想先跑通一遍完整流程，再做更大规模训练
- 当前这次实战的实际项目路径是 `/Volumes/DevExpand/LLM/FineTuning`

本文同时覆盖两类环境：

- `macOS + Apple Silicon`：本次实战的真实运行环境，设备后端是 `MPS`
- `Ubuntu + NVIDIA GPU`：最常见的 Linux 微调环境，设备后端是 `CUDA`

如果你在 Ubuntu 上使用的是纯 CPU，也不是完全不能跑，但速度通常会很慢，更适合用来验证流程，不适合作为正式训练环境。

## 1. 这次实战最后完成了什么

这次实战最终跑通了下面这条完整链路：

1. 下载基座模型
2. 安装 LLaMA-Factory
3. 准备自定义数据集
4. 在 WebUI 中启动 LoRA 训练
5. 拿到 LoRA 适配器输出
6. 在 Chat 页面加载底模 + LoRA 适配器
7. 通过对话验证微调是否生效

本次项目目录如下：

```text
/Volumes/DevExpand/LLM/FineTuning
├── LlamaFactory
├── configs
├── magic_conch.json
├── models
├── output
└── 笔记文档.md
```

其中最关键的几个路径是：

- 基座模型目录：`/Volumes/DevExpand/LLM/FineTuning/models/DeepSeek-R1-Distill-Qwen-1.5B`
- LLaMA-Factory 仓库：`/Volumes/DevExpand/LLM/FineTuning/LlamaFactory`
- 训练数据目录：`/Volumes/DevExpand/LLM/FineTuning/LlamaFactory/data`
- LoRA 输出目录：`/Volumes/DevExpand/LLM/FineTuning/LlamaFactory/saves/DeepSeek-R1-1.5B-Distill/lora`

## 2. 为什么这套方案适合本机和 Ubuntu

对 `16GB` 内存的 Mac 来说，直接做全参数微调并不现实。对普通单卡 Ubuntu 机器来说，如果显存也比较有限，LoRA 仍然是更稳妥的路线。最合适的起步方案是：

- 用较小的基座模型
- 使用 LoRA 做参数高效微调
- 先跑通一版小数据集训练
- 再逐步提升数据量和训练参数

本次选择：

- 框架：`LLaMA-Factory`
- 微调方式：`LoRA`
- 基座模型：`DeepSeek-R1-Distill-Qwen-1.5B`

这套组合的优点是：

- 文档和 WebUI 都比较成熟
- 对新手友好
- 1.5B 模型对本机内存和普通单卡显存都更友好
- LoRA 只训练少量参数，显著降低资源压力

## 3. 先区分两类系统环境

在继续之前，先确认你属于哪一类：

### 3.1 macOS 路线

适用于：

- Apple Silicon Mac
- 使用 `MPS` 跑训练
- 本次教程里的真实实践路径

特点：

- 环境搭建简单
- 本地可直接跑通
- 训练速度通常慢于 Ubuntu + NVIDIA GPU

### 3.2 Ubuntu 路线

适用于：

- Ubuntu 22.04 或 24.04
- 建议搭配 NVIDIA GPU
- 使用 `CUDA` 跑训练

特点：

- 更适合正式训练
- 训练速度通常更快
- 后续做更大模型或更大数据集也更方便

## 4. 前置准备

### 4.1 目录准备

先确保根目录存在：

```bash
cd /Volumes/DevExpand/LLM/FineTuning
mkdir -p models output configs
```

如果你在 Ubuntu 上，不必使用这个绝对路径。你只需要保证有一个统一的项目根目录即可，例如：

```bash
mkdir -p ~/FineTuning
cd ~/FineTuning
mkdir -p models output configs
```

后文所有出现的 `/Volumes/DevExpand/LLM/FineTuning`，在 Ubuntu 上都可以替换成你自己的项目根目录，例如 `~/FineTuning`。

### 4.2 准备 LLaMA-Factory 仓库

如果你还没克隆：

```bash
cd /Volumes/DevExpand/LLM/FineTuning
git clone --depth 1 https://github.com/hiyouga/LLaMA-Factory.git LlamaFactory
```

如果仓库已经在本地，直接进入即可：

```bash
cd /Volumes/DevExpand/LLM/FineTuning/LlamaFactory
```

### 4.3 Ubuntu 额外依赖

如果你在 Ubuntu 上，建议先准备一些基础系统依赖：

```bash
sudo apt update
sudo apt install -y git curl build-essential ffmpeg
```

如果你是 NVIDIA GPU 环境，还应确保：

- `nvidia-smi` 能正常执行
- 对应 CUDA 驱动已安装

你可以先用：

```bash
nvidia-smi
```

确认 GPU 和驱动可见。

## 5. 使用 uv 创建 Python 3.11 环境

本机默认系统 Python 不一定是 `3.11`，而 LLaMA-Factory 当前更适合单独建立一个 `3.11` 环境。

在仓库目录下执行：

```bash
cd /Volumes/DevExpand/LLM/FineTuning/LlamaFactory

uv python install 3.11
uv venv --python 3.11
source .venv/bin/activate
```

验证 Python 版本：

```bash
python -V
```

期望看到类似：

```text
Python 3.11.12
```

## 6. 安装 LLaMA-Factory 依赖

在虚拟环境中安装：

```bash
cd /Volumes/DevExpand/LLM/FineTuning/LlamaFactory
source .venv/bin/activate

uv pip install -e .
```

说明：

- 本次实战里也用过 `uv pip install -e ".[torch,metrics]"`，可以装上，但会有 extras 警告
- 对当前仓库版本来说，`uv pip install -e .` 更直接

安装完成后验证：

```bash
llamafactory-cli version
python -c "import torch; print(torch.__version__); print('mps:', torch.backends.mps.is_available())"
```

如果你是 macOS，上面这条命令能看到版本号，且 `mps: True`，环境就基本可用了。

如果你是 Ubuntu，更建议这样验证：

```bash
llamafactory-cli version
python -c "import torch; print(torch.__version__); print('cuda:', torch.cuda.is_available()); print('cuda_device_count:', torch.cuda.device_count())"
```

如果能看到版本号，且 `cuda: True`，环境就基本可用了。

## 7. 设置常用环境变量

每次开始训练或打开 WebUI 前，都建议先激活环境并设置这几个变量：

### 7.1 macOS

```bash
cd /Volumes/DevExpand/LLM/FineTuning/LlamaFactory
source .venv/bin/activate

export PYTORCH_ENABLE_MPS_FALLBACK=1
export TOKENIZERS_PARALLELISM=false
export HF_HOME=/Volumes/DevExpand/LLM/FineTuning/models/hf-cache
```

说明：

- `PYTORCH_ENABLE_MPS_FALLBACK=1` 可以让一些 MPS 不支持的算子回退，减少报错
- `TOKENIZERS_PARALLELISM=false` 可以减少 tokenizer 相关警告
- `HF_HOME` 用于统一管理 Hugging Face 下载缓存

### 7.2 Ubuntu

在 Ubuntu 上，一般不用设置 `PYTORCH_ENABLE_MPS_FALLBACK`，因为训练后端不是 `MPS`，而是 `CUDA`。

```bash
cd ~/FineTuning/LlamaFactory
source .venv/bin/activate

export TOKENIZERS_PARALLELISM=false
export HF_HOME=~/FineTuning/models/hf-cache
```

如果你要指定某张 GPU，还可以加：

```bash
export CUDA_VISIBLE_DEVICES=0
```

## 8. 下载基座模型

### 8.1 安装 Hugging Face 命令行工具

```bash
cd /Volumes/DevExpand/LLM/FineTuning/LlamaFactory
source .venv/bin/activate

uv pip install -U huggingface_hub
hf --help
```

### 8.2 下载 DeepSeek-R1-Distill-Qwen-1.5B

推荐直接用官方源。如果你使用代理，确保代理节点对 Hugging Face 大文件下载比较友好。

```bash
unset HF_ENDPOINT
export HF_HUB_ENABLE_HF_TRANSFER=1
export HF_HOME=/Volumes/DevExpand/LLM/FineTuning/models/hf-cache

hf download deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B \
  --local-dir /Volumes/DevExpand/LLM/FineTuning/models/DeepSeek-R1-Distill-Qwen-1.5B
```

### 8.3 如何判断模型是否下载完整

执行：

```bash
ls -lh /Volumes/DevExpand/LLM/FineTuning/models/DeepSeek-R1-Distill-Qwen-1.5B
du -sh /Volumes/DevExpand/LLM/FineTuning/models/DeepSeek-R1-Distill-Qwen-1.5B
```

目录里通常至少要有：

- `config.json`
- `generation_config.json`
- `tokenizer_config.json`
- `tokenizer.json`
- `model.safetensors` 或若干 `model-*.safetensors`

## 9. 代理与下载速度的一个实战结论

这次实战中，模型下载一开始非常慢，最后确认不是命令错，也不是终端没走代理，而是：

- 代理节点本身到 Hugging Face 大文件下载链路太差
- 换了一个节点之后，下载速度明显改善

一个很实用的判断方法是先测速小文件：

```bash
curl -L -o /dev/null -w '\nDNS:%{time_namelookup}\nConnect:%{time_connect}\nTLS:%{time_appconnect}\nTTFB:%{time_starttransfer}\nTotal:%{time_total}\nSpeed:%{speed_download}\n' \
  https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B/resolve/main/config.json
```

如果小文件测速都非常低，那么大文件下载大概率也会很慢。对本地微调来说，换一个更适合下载模型的代理节点，比改命令更有效。

这一点对 macOS 和 Ubuntu 都成立。

## 10. 准备训练数据集

### 10.1 数据文件位置

训练数据需要放到：

```text
/Volumes/DevExpand/LLM/FineTuning/LlamaFactory/data/magic_conch.json
```

注意不要只放在根目录。  
这次实战中实际遇到过一个报错：

```text
ValueError: File data/magic_conch.json not found.
```

原因就是文件不在 `LlamaFactory/data` 下。

### 10.2 数据格式

LLaMA-Factory 最简单可用的是 `instruction/input/output` 这种格式。示例：

```json
[
  {
    "instruction": "请问你是谁",
    "input": "",
    "output": "您好，我是蟹堡王的神奇海螺，很高兴为您服务。"
  },
  {
    "instruction": "怎么修复这个报错",
    "input": "报错信息：汉堡食谱为空",
    "output": "请先检查食谱文件是否存在、路径是否正确，并尝试重新加载。"
  }
]
```

### 10.3 注册数据集

编辑：

```text
/Volumes/DevExpand/LLM/FineTuning/LlamaFactory/data/dataset_info.json
```

加入：

```json
"magic_conch": {
  "file_name": "magic_conch.json"
}
```

### 10.4 数据量建议

如果只是为了先跑通流程：

- `20-50` 条就够了

如果你希望看到更明显的风格变化：

- 尽量准备 `100+` 条高质量样本

本次实战中，第一次只有十几条样本，更多是为了验证流程，而不是追求最终效果。

## 11. 启动 LLaMA-Factory WebUI

### 11.1 macOS

执行：

```bash
cd /Volumes/DevExpand/LLM/FineTuning/LlamaFactory
source .venv/bin/activate

export PYTORCH_ENABLE_MPS_FALLBACK=1
export TOKENIZERS_PARALLELISM=false
export HF_HOME=/Volumes/DevExpand/LLM/FineTuning/models/hf-cache

llamafactory-cli webui
```

启动后一般访问：

```text
http://127.0.0.1:7860
```

如果端口被占用，可以指定：

```bash
GRADIO_SERVER_PORT=7861 llamafactory-cli webui
```

### 11.2 Ubuntu

如果你在 Ubuntu 上，启动命令基本相同，只是通常不需要 `PYTORCH_ENABLE_MPS_FALLBACK`：

```bash
cd ~/FineTuning/LlamaFactory
source .venv/bin/activate

export TOKENIZERS_PARALLELISM=false
export HF_HOME=~/FineTuning/models/hf-cache
export CUDA_VISIBLE_DEVICES=0

llamafactory-cli webui
```

如果你是在本机桌面 Ubuntu 上运行，浏览器直接访问：

```text
http://127.0.0.1:7860
```

如果你是在远程 Ubuntu 服务器上运行，则要么：

- 通过 SSH 隧道把 `7860` 端口转发到本地
- 要么在内网或安全环境中直接开放对应端口

## 12. 在 WebUI 训练页面如何填写

以下内容以本次实战为例。

### 12.1 基础配置

- `Model name`: `DeepSeek-R1-1.5B-Distill`
- `Model path`: `/Volumes/DevExpand/LLM/FineTuning/models/DeepSeek-R1-Distill-Qwen-1.5B`
- `Hub name`: `huggingface`
- `Finetuning method`: `lora`
- `Checkpoint path`: 训练时先留空
- `Quantization bit`: `none`
- `Chat template`: `deepseekr1`
- `RoPE scaling`: `none`
- `Booster`: `auto`

这里有一个很重要的点：  
`Model path` 填的是基座模型目录，不是 `hf-cache`，也不是 `models` 上一级目录。

### 12.2 训练参数建议

针对本机配置，建议一开始用偏保守的参数：

- `Stage`: `sft`
- `Dataset`: `magic_conch`
- `Cutoff length`: `512`
- `Learning rate`: `1e-4`
- `Epochs`: `10` 或 `20`
- `Per device train batch size`: `1` 或 `2`
- `Gradient accumulation steps`: `8`
- `Validation split`: `0.1`
- `Gradient checkpointing`: 开启
- `Compute type`: 优先 `fp16` 或自动

如果你是 Ubuntu + NVIDIA GPU，可以按显存情况适度放宽：

- `Per device train batch size`: 如果显存够，可以从 `2` 提到 `4`
- `Cutoff length`: 如果显存够，可以尝试 `1024`
- `Compute type`: 优先 `bf16` 或 `fp16`

### 12.3 关于 epoch 的真实经验

本次实战里曾经用过：

- 样本数：`21`
- `Epochs = 100`

它能跑通，但对这样的小数据集明显偏大，容易过拟合。  
如果你只是想得到一版更合理的训练结果，建议优先：

- `Epochs = 10`
- 或 `Epochs = 20`

## 13. 训练过程怎么看是否正常

训练开始后，终端里会看到类似：

```text
Num examples = 21
Num Epochs = 100
Total optimization steps = 200
```

同时会不断打印 `loss`，例如：

```text
{'loss': 4.9559, ...}
{'loss': 4.4408, ...}
{'loss': 3.6467, ...}
{'loss': 2.9987, ...}
{'loss': 2.5876, ...}
```

这说明：

- 训练已经开始
- 数据集被正确读取
- LoRA 正在生效
- 模型在收敛

下列日志可以先忽略，不代表训练失败：

```text
Could not locate the custom_generate/generate.py ...
```

```text
The tokenizer has new PAD/BOS/EOS tokens ...
```

```text
You are using reasoning template ...
```

对于 `DeepSeek-R1-Distill-Qwen-1.5B`，继续使用 `deepseekr1` 模板是合理的。

## 14. 训练结果放在哪里

LoRA 训练结果保存在：

```text
/Volumes/DevExpand/LLM/FineTuning/LlamaFactory/saves/DeepSeek-R1-1.5B-Distill/lora
```

每次训练会生成一个新的时间戳目录，例如：

```text
train_2026-03-29-18-39-33
train_2026-03-29-19-34-05
```

查看目录：

```bash
ls -lt /Volumes/DevExpand/LLM/FineTuning/LlamaFactory/saves/DeepSeek-R1-1.5B-Distill/lora
```

训练输出目录中通常会有：

- `adapter_model.safetensors`
- `adapter_config.json`
- `tokenizer_config.json`
- `chat_template.jinja`
- `checkpoint-*`

注意：这里保存的是 **LoRA 适配器**，不是完整合并后的模型。

## 15. 如何在 WebUI 的 Chat 页面验证微调效果

这一段是整个实战里最容易填错的地方。

### 15.1 先理解一个关键点

如果你在 Chat 页面中：

- 只填了 `Model path`
- 没填 `Checkpoint path`

那么你加载的只是 **原始底模**，不是微调后的 LoRA 模型。

这次实战中，正是因为 `Checkpoint path` 最开始留空，所以聊天时看到的其实是底模回答，而不是微调后的结果。

### 15.2 Chat 页面正确填写方式

在 Chat 页面里：

- `Model path`: `/Volumes/DevExpand/LLM/FineTuning/models/DeepSeek-R1-Distill-Qwen-1.5B`
- `Checkpoint path`: 填 LoRA 输出目录，例如：

```text
/Volumes/DevExpand/LLM/FineTuning/LlamaFactory/saves/DeepSeek-R1-1.5B-Distill/lora/train_2026-03-29-19-34-05
```

- `Finetuning method`: `lora`
- `Chat template`: `deepseekr1`
- `Inference engine`: `huggingface`
- `Quantization bit`: `none`
- `Extra arguments`: 建议清空，或者填 `{}`，不要保留与 `vllm` 相关的参数

### 15.3 正确的验证流程

1. 先点击 `Unload model`
2. 填好 `Checkpoint path`
3. 再点击 `Load model`
4. 等待页面提示模型加载成功
5. 使用训练集中出现过或非常接近的问题做测试

推荐测试问题：

- `请问你是谁`
- `怎么修复这个报错`
- 训练集中与你业务最接近的问题

### 15.4 如何判断微调是否真的生效

如果 LoRA 被正确加载，通常会看到：

- 回答风格更接近训练数据
- 对特定身份设定更稳定
- 对训练集中高频问题的回答更一致
- 与基座模型相比，更贴近你的业务场景

如果你看不出明显变化，优先检查：

1. `Checkpoint path` 是否为空
2. 加载的是否是最新训练目录
3. 样本量是不是太少
4. 训练 epoch 是否太低

## 16. 导出与合并模型

如果你只是在 WebUI 里验证 LoRA 效果，那么底模 + 适配器的组合已经可以用了。  
但如果你后面希望把模型用于更简单的部署，通常会希望合并出一个完整模型。

### 16.1 在 WebUI 的 Export 页面处理

导出页面一般这样填：

- `Model path`: `/Volumes/DevExpand/LLM/FineTuning/models/DeepSeek-R1-Distill-Qwen-1.5B`
- `Checkpoint path` / `Adapter path`: 最新训练出来的 LoRA 目录
- `Template`: `deepseekr1`
- `Finetuning method`: `lora`
- `Export dir`: `/Volumes/DevExpand/LLM/FineTuning/output/deepseek-r1-1.5b-merged`
- `Export device`: `cpu`

### 16.2 合并后的结果放在哪里

建议放到：

```text
/Volumes/DevExpand/LLM/FineTuning/output/deepseek-r1-1.5b-merged
```

合并完成后，后续推理时就不再需要单独指定 LoRA 适配器路径。

## 17. 常见问题与踩坑总结

### 17.1 `huggingface-cli: command not found`

原因：

- 没装 `huggingface_hub`

解决：

```bash
uv pip install -U huggingface_hub
hf --help
```

### 17.2 `uv pip install -e ".[torch,metrics]"` 报 extras 警告

原因：

- 当前版本并没有定义这两个 extras

解决：

```bash
uv pip install -e .
```

### 17.3 `File data/magic_conch.json not found`

原因：

- 数据文件没放在 `LlamaFactory/data` 目录下

正确位置：

```text
/Volumes/DevExpand/LLM/FineTuning/LlamaFactory/data/magic_conch.json
```

### 17.4 模型下载非常慢

原因通常不是命令错，而是：

- 代理节点到 Hugging Face 大文件链路差
- 当前节点只适合网页访问，不适合大文件下载

解决思路：

- 先测小文件下载速度
- 换一个更适合下载的代理节点
- 再重新执行 `hf download`

### 17.5 Ubuntu 上 `cuda: False`

原因通常是：

- NVIDIA 驱动没装好
- 机器没有可用 GPU
- PyTorch 安装的版本与 CUDA 环境不匹配

先检查：

```bash
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

如果 `nvidia-smi` 都不正常，优先修驱动和 CUDA 环境，而不是继续排查 LLaMA-Factory。

### 17.6 Chat 页面看不到微调效果

最常见原因：

- `Checkpoint path` 没填

结果：

- 页面加载的是底模，不是 LoRA 微调结果

### 17.7 小数据集把 epoch 设太大

本次实战中，`21` 条样本配 `100` 个 epoch 能跑，但过拟合风险很高。  
更合理的起步参数通常是：

- `10` epoch
- 或 `20` epoch

## 18. 推荐的最小可复现参数

如果你只是希望在这台 Mac 上稳定复现一遍流程，建议直接用下面这套：

- 模型：`DeepSeek-R1-Distill-Qwen-1.5B`
- 微调方式：`LoRA`
- 模板：`deepseekr1`
- 样本量：`20-100`
- `cutoff_len = 512`
- `train batch size = 1`
- `gradient accumulation = 8`
- `learning rate = 1e-4`
- `epoch = 10`
- `quantization bit = none`

如果你在 Ubuntu + NVIDIA GPU 上显存更充足，可以把这一套微调成：

- `train batch size = 2` 或 `4`
- `cutoff_len = 1024`
- `compute type = bf16`

## 19. 一套最简执行顺序

如果你只记流程，不记细节，可以按这个顺序做：

1. 进入仓库并激活 `.venv`
2. 设置 `PYTORCH_ENABLE_MPS_FALLBACK=1`
3. 下载基座模型到 `models/DeepSeek-R1-Distill-Qwen-1.5B`
4. 把 `magic_conch.json` 放到 `LlamaFactory/data`
5. 在 `dataset_info.json` 注册 `magic_conch`
6. 启动 `llamafactory-cli webui`
7. Train 页面选择底模、模板、LoRA 和数据集
8. 跑训练
9. 记下 `saves/.../train_时间戳` 输出目录
10. 在 Chat 页面把 `Checkpoint path` 指向这个 LoRA 输出目录
11. 重新加载模型并测试
12. 需要时再去 Export 页面做合并

## 20. macOS 和 Ubuntu 的最终建议

如果你是 `macOS + Apple Silicon`：

- 这套流程完全能跑通
- 更适合做本地验证、学习和小规模实验
- 模型和数据量都不要一开始拉得太大

如果你是 `Ubuntu + NVIDIA GPU`：

- 优先推荐在 Ubuntu 上做正式训练
- 同样的流程基本通用
- 只是设备后端从 `MPS` 换成了 `CUDA`
- 可以根据显存适度提升 batch size、cutoff length 和数据量

## 21. 这次实战的结论

这套方案已经验证可在本机跑通，关键经验如下：

- `macOS + Apple Silicon + uv + LLaMA-Factory` 是可行的
- `Ubuntu + NVIDIA GPU + uv + LLaMA-Factory` 同样适用，而且更适合正式训练
- 对 `16GB` 内存机器，LoRA 是最现实的起步方案
- 先跑通流程，再谈效果优化
- 对小数据集来说，`Checkpoint path` 和 `epoch` 设置比很多细枝末节更重要
- 训练是否成功，不只看是否跑完，更要看你能否在 Chat 页面正确加载 LoRA 适配器并观察到风格变化

## 22. 参考资料

- 你的笔记：`/Volumes/DevExpand/LLM/FineTuning/笔记文档.md`
- LLaMA-Factory 仓库：<https://github.com/hiyouga/LLaMA-Factory>
- WebUI 文档：<https://llamafactory.readthedocs.io/en/latest/getting_started/webui.html>
- 合并文档：<https://llamafactory.readthedocs.io/en/latest/getting_started/merge_lora.html>
- 推理文档：<https://llamafactory.readthedocs.io/en/latest/getting_started/inference.html>
- PyTorch MPS 文档：<https://docs.pytorch.org/docs/stable/notes/mps.html>
- 模型页：<https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B>
