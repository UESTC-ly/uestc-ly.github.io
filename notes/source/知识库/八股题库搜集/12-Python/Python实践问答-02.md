# Python实践问答

<a id="kbd413e763184"></a>

## 在AI行业中，Python编程中的动态库和静态库的含义是什么？两者之间什么差异？

在 Python 生态里，底层扩展多以原生库形式存在：

- **静态库**：编译期把目标代码链接进可执行文件/扩展模块（`.a` / `.lib`）。产物自包含，体积大，更新需重编。
- **动态库**：运行时加载共享库（`.so` / `.dll` / `.dylib`）。多个程序可共享，可单独升级，但依赖管理更复杂。

### 对照

| | 静态库 | 动态库 |
|--|--------|--------|
| 链接时机 | 编译期 | 运行期 |
| 产物 | 并入二进制 | 独立 .so/.dll |
| 升级 | 整体重编 | 可替换库文件 |
| 部署 | 简单、偏大 | 需保证依赖路径正确 |
| AI 场景 | 某些完全静态链接的推理二进制 | CUDA/cuDNN/TensorRT/torch 扩展的常态 |

### Python 中的实际意义

```python
import torch
print(torch.__version__)
# torch 依赖 CUDA 动态库：libcudart、libcublas、自定义 .so 算子
```

常见问题：

1. **找不到 .so/.dll**：`PATH` / `LD_LIBRARY_PATH` / `CUDA_HOME` 没配好。
2. **ABI 不匹配**：编译器、CUDA、Python 版本不一致导致 `undefined symbol`。
3. **Windows/Linux 混用**：不能把 Linux 的 `.so` 丢到 Windows 上。

<font color=DeepSkyBlue>部署 AI 服务时，动态库版本矩阵（Python、CUDA、cuDNN、驱动、torch）是最常见的环境类故障源。</font>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L2160)，来源许可：GPL-3.0。

<a id="k62a70a5f414c"></a>

## 常用的深度学习框架有哪些，都是哪家公司开发的？

| 框架 | 主导方 | 现状备注 |
|------|--------|----------|
| PyTorch | Meta（原 Facebook） | 学术与大模型训练主流 |
| TensorFlow / Keras | Google | TF2 统一 Keras API；工业部署仍有存量 |
| JAX | Google | 函数式变换，高性能研究向 |
| PaddlePaddle | 百度 | 国内产业落地较多 |
| MindSpore | 华为 | 昇腾生态 |
| MXNet | Apache（曾 Amazon 主导） | 维护已明显减弱 |
| OneFlow | OneFlow 国产开源 | 分布式训练方向 |

推理/服务侧常见：vLLM、TensorRT / TensorRT-LLM、ONNX Runtime、OpenVINO、llama.cpp 等。

一线现状：<font color=DeepSkyBlue>训练侧 PyTorch 占绝对主导；推理侧多框架并存，按硬件与延迟要求选型</font>。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L154)，来源许可：GPL-3.0。

<a id="k186405f50aaf"></a>

## 真实踩坑：模型被重复加载

在 Flask/FastAPI 中，若每次请求都 `Infer()`，`__init__` 会反复加载权重，导致接口「推理很快、整请求很慢」。

```python
class Infer:
    _model = None

    def __init__(self, cfg: dict):
        self.cfg = cfg
        if Infer._model is None:
            Infer._model = self.load_model(cfg)
        self.model = Infer._model

    @classmethod
    def load_model(cls, cfg: dict):
        # 类属性做单例缓存
        if not hasattr(cls, "model") or cls.model is None:
            cls.model = torch.load(cfg["path"])
        return cls.model
```

更干净的一线做法是在应用生命周期里只加载一次：

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.engine = load_engine()   # 启动时加载
    yield
    app.state.engine = None            # 关闭时释放

app = FastAPI(lifespan=lifespan)
```

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E7%BC%96%E7%A8%8B%E5%9F%BA%E7%A1%80%EF%BC%9APython/Python%E8%BF%9B%E9%98%B6%E7%9F%A5%E8%AF%86%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L676)，来源许可：GPL-3.0。
