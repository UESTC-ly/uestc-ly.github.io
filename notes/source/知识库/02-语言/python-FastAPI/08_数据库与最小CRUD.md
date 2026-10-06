# 08 数据库与最小 CRUD

> 记忆句：**引擎管连接基础设施，会话管本次操作；add 是登记，commit 才提交。**

## 1. 为什么内存列表还不够

前几章把任务放在 Python 列表里，适合观察 HTTP 请求怎样进出。但进程一重启，列表就重新创建；多个进程也不会天然共享同一个列表。数据库让数据拥有独立于某个请求、某个进程的存储位置，还提供查询、约束和事务。

本章使用 SQLite 与 SQLModel。SQLite 把数据库保存为一个文件，不必先安装独立数据库服务器；SQLModel 让 Python 类与关系数据库表之间的对应关系更容易表达。CRUD 是创建、读取、更新、删除四类基本操作。正文只写“创建和读取”，先掌握保存数据的完整过程，再把同一套理解推广到修改和删除。

## 2. 先记住四个不同的角色

表模型描述“存什么”：例如每条任务有 ID 和标题。数据库表则是真正存放记录的地方；Python 中创建一个模型对象，只是在内存里得到一个对象，不代表数据库已经多了一行。

`Engine` 提供连接数据库的基础设施，可以在一个应用进程内复用。`Session` 跟踪一组数据库操作及其对象状态，承载一次工作单元。两者的区别类似“整个图书馆的服务系统”和“某位读者本次办理业务的窗口记录”：基础设施可以服务很多人，但某人的办理状态不能混进另一个人的记录里。

| 名称 | 负责什么 | 本章生命周期 |
| --- | --- | --- |
| 表模型 | 描述表字段和约束 | 代码定义的一部分 |
| Engine | 数据库连接基础设施 | 应用进程内复用 |
| Session | 跟踪本次读写与事务状态 | 每次请求单独创建和关闭 |
| 事务 | 一组需要一起提交或撤销的修改 | 按业务边界提交或回滚 |

“会话按请求”是一种易用的起步方式，不代表一个 Session 永远等于一个事务，也不代表同一请求必须只能提交一次。实际项目应按业务一致性需要划分事务边界。[官方数据库教程](https://fastapi.tiangolo.com/tutorial/sql-databases/)

## 3. 写入时，add、commit、refresh 为什么分开

创建对象后，`add` 把对象交给 Session 管理。它表达了保存意图，但并未完成事务提交；即使后来执行了 SQL，也不等于修改已经正式提交。

`commit` 提交当前事务。假设一次业务同时修改两条记录，事务的意义就是让这组修改按约定一起成功，或者在失败时撤销尚未提交的改动。不要为了“保险”每改一个字段就提交一次，那会拆散本来应该作为整体的业务。

`refresh` 从数据库重新读取对象数据，适合取得数据库生成的 ID、默认值等。它不是再次保存，也不是提交的替代品。因此可以把本章写入顺序记成：**创建对象 → 登记 → 提交 → 读取数据库确认后的字段。**

## 4. 最小 demo：保存一条，再读出来

先按[学习地图](00_学习地图.md)安装依赖，其中已经包含本章需要的 `sqlmodel`。将代码复制到 `main.py`，用 `python -m uvicorn main:app --reload` 启动；切换前停止上一章。

```python
from contextlib import asynccontextmanager
from fastapi import Body, Depends, FastAPI
from sqlmodel import Field, Session, SQLModel, create_engine, select

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str

engine = create_engine("sqlite:///./tasks.db", connect_args={"check_same_thread": False})

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield
    engine.dispose()

app = FastAPI(lifespan=lifespan)

def get_session():
    with Session(engine) as session:
        yield session

@app.post("/tasks", status_code=201)
def create_task(
    title: str = Body(embed=True, min_length=1),
    session: Session = Depends(get_session),
):
    task = Task(title=title)
    session.add(task)
    session.commit()
    session.refresh(task)
    return {"id": task.id, "title": task.title}

@app.get("/tasks")
def list_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()
```

打开 `http://127.0.0.1:8000/docs`，先执行 `POST /tasks`，请求体填写 `{"title":"学习数据库"}`，得到包含实际 ID 的对象；再执行 `GET /tasks`，确认列表里出现这条记录。这里的 `Body(embed=True)` 要求 JSON 对象里包含 `title`，避免把表模型直接作为客户端的完整输入。

停止并重新启动服务，再读一次列表，记录仍然存在。数据库文件是启动命令所在目录下的 `tasks.db`，不是自动固定在 `main.py` 旁边；换一个工作目录启动，可能生成另一个数据库文件。本例不对已有数据排序，也不分页，读取顺序不能当作接口保证。

## 5. 把一次请求串起来

应用启动时，`lifespan` 中 `yield` 前的代码建立缺失的表。每次请求到来，`get_session` 创建一个新 Session，随后用 `yield` 把它交给接口；接口完成相应数据库操作，依赖退出时由 `with` 关闭会话。服务关闭时，再释放引擎管理的连接资源。

这里有三个不同时间尺度：**启动时准备表；请求时借用会话；写入时提交事务。** 不要在每次请求里重新创建整套引擎，也不要用一个全局 Session 接待所有请求。

关闭会话不等于自动提交。请求途中失败时，未提交的事务不能靠函数返回或会话关闭来“补保存”。如果捕获数据库异常后还要继续使用同一会话，需要先正确回滚；最小例子让异常向外传播并关闭本次会话，没有演示复杂的错误恢复流程。

## 6. 不贴更多代码，也能理解更新与删除

更新通常先按 ID 查到对象，判断是否存在，再修改允许变更的字段，最后提交。删除也要先决定对象不存在时的接口语义，然后登记删除并提交。它们与创建的共同点都是“会话内组织操作，事务中确认修改”，区别在于操作的是已有记录还是新记录。

HTTP 层的 PUT 通常表达完整替换，PATCH 表达部分修改。对于 PATCH，“客户端没传标题”和“客户端传了空值”不能被当作一回事。Pydantic 的 `model_dump(exclude_unset=True)` 按是否提供字段筛选，`exclude_none=True` 按值是否为 None 筛选，两者含义不同。[更新请求体说明](https://fastapi.tiangolo.com/tutorial/body-updates/)

表模型也不应自动决定客户端的权限。本例只接收标题，ID 由数据库生成；正式业务中还常有内部状态、创建时间、所属用户等字段，需要独立定义输入与输出边界，而不是把所有表字段直接开放修改。

## 7. 这个 demo 的边界

`check_same_thread=False` 放宽 SQLite 连接使用上的线程检查，以配合框架处理同步请求的方式。它不意味着 Session 线程安全，更不意味着多个并发请求可以随意共享一个 Session。同步数据库操作写在普通 `def` 路由中，由框架安排执行；不能仅把路由改成 `async def` 就获得异步数据库能力。

`create_all` 能创建缺失的表，但不会负责把已有表升级成新结构。给模型增加字段后，已有数据库不一定自动出现该列；随着应用演进，需要用数据库迁移工具管理结构变化。本例启动阶段做少量同步建表工作，方便初学观察，不把它当作大型生产环境的迁移方案。

SQLite 适合这个单机练习，但实际服务还要考虑并发写入、索引、分页和备份。首先应准确掌握当前程序保存到哪里、何时提交、何时关闭，再继续学习这些工程问题。

## 8. 合上笔记再回答

1. 只创建 `Task(...)`，数据库就多一行了吗？没有，那只是内存对象。
2. 只有 `add` 没有 `commit`，能认为写入已完成吗？不能。
3. 为什么 Engine 可复用而 Session 要按请求隔离？前者是基础设施，后者携带本次操作和事务状态。
4. 重新启动后数据还在，说明什么？数据位于 SQLite 文件中，独立于上次 Python 进程的内存。
5. 给模型加字段后，`create_all` 会升级旧表吗？不会自动完成结构迁移。

## 9. 可选配套与官方资料

[demos/ch08.py](demos/ch08.py) 保留更完整的 CRUD、独立输入输出模型和错误处理。它的接口、校验规则及数据库路径与正文可能不同：配套文件使用系统临时目录数据库，正文使用当前工作目录的 `tasks.db`。两者的数据不自动共享；掌握正文读写流程后再阅读配套即可。

[SQL Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/) · [Body Updates](https://fastapi.tiangolo.com/tutorial/body-updates/)

---

[返回学习地图](00_学习地图.md)
