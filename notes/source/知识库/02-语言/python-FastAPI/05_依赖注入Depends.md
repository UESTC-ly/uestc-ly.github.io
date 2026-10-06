# 05 依赖注入 Depends

> 记忆句：**接口说需要什么，Depends 负责准备，再把结果交进来。**

## 1. 为什么不直接在每个接口里调用公共函数

假设任务列表和文章列表都有分页功能。最初可以在两个接口里分别接收 `offset`、`limit`，分别检查范围；但只要分页规则改变，就得同时修改多处。抽一个公共函数能减少重复计算，却仍需要每个接口自己接收参数、传参和安排调用。

依赖注入把这一步也交给框架：接口声明“我需要一个分页结果”，FastAPI 根据依赖函数的参数声明，读取请求、验证参数、调用函数，再把返回值交给接口。**依赖仍然是普通 Python 函数；特殊之处在于由谁安排调用。**

可以把接口理解成厨师，依赖理解成备料工序。厨师拿到洗好的菜才开始做饭，不必每次重新写洗菜步骤。不过这种类比只说明职责分工，并不意味着依赖在后台并行执行；必须满足的依赖会先准备好，接口才能正常执行。

## 2. 一次请求究竟经过了什么

以请求 `GET /tasks?offset=1&limit=1` 为例，FastAPI 先匹配路由，发现接口参数依赖 `pagination`，于是继续查看这个函数需要什么。它从 URL 中读取两个查询参数，将字符串转换为整数，检查范围，然后执行分页函数。函数返回的字典被赋给路由的 `page`，路由才按这个范围切片。

因此，`page` 不是客户端发送的一整个 JSON 对象，也不是 `pagination` 函数本身；它是函数执行后的结果。虽然分页参数没有直接写在路由签名里，FastAPI 仍能把它们展示到 `/docs`。这也是依赖比普通工具函数更适合处理请求准备工作的原因。[官方说明](https://fastapi.tiangolo.com/tutorial/dependencies/)

如果传入 `limit=0`，参数检查不通过，正常的列表业务不会执行，客户端收到 422。依赖也可以主动抛出 `HTTPException`，例如当前用户没有权限时提前结束请求。

## 3. 最小 demo：准备分页结果

将下面代码复制到 `main.py`，在所在目录运行 `python -m uvicorn main:app --reload`。依赖安装见[学习地图](00_学习地图.md)；每次只启动一章，切换前用 `Ctrl+C` 停止服务。

```python
from typing import Annotated
from fastapi import Depends, FastAPI, Query

app = FastAPI()

def pagination(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
):
    return {"offset": offset, "limit": limit}

@app.get("/tasks")
def tasks(page: Annotated[dict, Depends(pagination)]):
    data = ["读书", "写代码", "复习"]
    return data[page["offset"]:page["offset"] + page["limit"]]
```

打开 `http://127.0.0.1:8000/docs`，展开 `GET /tasks`，点击 **Try it out**。先用默认参数执行，会看到三个任务；再填 `offset=1`、`limit=1`，只返回“写代码”；最后填 `limit=0`，观察验证失败。先预测结果，再操作，比反复复制请求命令更容易记住。

`Annotated[dict, Depends(pagination)]` 可以读成两部分：这个参数的类型是字典；它的取值方式是执行 `pagination`。传给 `Depends` 的是函数名，不能加调用括号，否则会在定义阶段提前执行，失去按请求准备参数的含义。

## 4. 哪些逻辑适合放进依赖

**与请求有关、多个入口需要、又能独立描述的准备工作**，通常适合成为依赖，例如取得当前用户、检查权限、获取数据库会话、解析统一分页参数。单纯把两个数字相加或格式化字符串，普通函数就足够，不必所有代码都套上 `Depends`。

依赖还能依赖其他依赖。例如“管理员检查”依赖“当前用户”，“当前用户”依赖“读取令牌”。这形成一张需求关系图：先拿到令牌，再识别用户，最后检查权限。拆分的价值在于每一步职责清楚、可单独测试，不在于层数越多越好。

| 需求 | 放在哪里 | 接口能否直接拿到结果 |
| --- | --- | --- |
| 需要当前用户对象参与业务 | 路由函数参数中的 `Depends` | 能 |
| 只检查权限，通过即可 | 路由或路由组的 `dependencies` | 不会自动作为参数传入 |
| 申请资源并在使用后释放 | 带 `yield` 的依赖 | 能，得到 `yield` 交出的对象 |

## 5. 缓存与资源管理最容易混淆

同一个依赖在一次请求的多个位置被复用时，FastAPI 通常会复用该请求内已计算的结果。这可以避免同一次请求重复查询当前用户。**它不是跨请求缓存**：下一个请求仍会重新解析依赖。显式关闭依赖缓存或采用不同依赖配置时，执行次数也可能不同，不应靠猜测调用次数设计业务。[子依赖与缓存](https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/)

`return` 依赖适合“算完给结果”；`yield` 依赖适合“先借出资源，再负责收回”。数据库会话就是后者：先创建会话并交给路由，依赖退出时关闭会话。关闭和提交是两件事，不能以为用了 `yield` 就会自动保存数据。第 08 章会把这个过程展开。

另一个边界是：在普通 Python 代码里自己直接调用路由函数，并不会自动触发 FastAPI 的依赖解析。依赖注入发生在框架处理请求的过程中，不能把 `Depends` 当作任何场景都能自动取值的变量。

## 6. 合上笔记再回答

1. 客户端需要传名为 `page` 的 JSON 吗？不需要；本例由分页依赖读取查询参数并生成字典。
2. `Depends(pagination)` 传给框架什么，框架传给接口什么？前者是函数，后者是函数返回的结果。
3. 两个不同请求会共享这次分页依赖的缓存吗？不会，这是请求内的复用。
4. 普通工具函数也必须改成依赖吗？不必；先看它是否需要参与请求参数解析或资源管理。

## 7. 可选配套与官方资料

[demos/ch05.py](demos/ch05.py) 是保留的配套版本，组织形式比正文更完整；请以该文件的实际接口为准，不要求与正文代码完全相同。先理解本章，再按需阅读配套文件。

[Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) · [Sub-dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/) · [Dependencies with yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/)

---

[返回学习地图](00_学习地图.md)
