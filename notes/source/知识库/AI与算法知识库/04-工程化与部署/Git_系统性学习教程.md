---
tags:
  - Git
  - 版本控制
  - 工程化
aliases:
  - Git 教程
  - Git 入门到进阶
---

# Git_系统性学习教程

这篇笔记的目标，不是让你“背几个 Git 命令”，而是让你真正理解 **Git 为什么这样设计、平时该怎么用、出问题时怎么救**。

学完这篇后，至少应该能做到：

- 理解工作区、暂存区、提交历史、远程仓库之间的关系
- 独立完成日常开发流：拉代码、改代码、提交、同步、推送
- 理解分支、合并、变基的区别
- 知道什么时候用 `reset`，什么时候用 `revert`
- 遇到冲突、误删提交、切错分支时知道怎么恢复

---

## 1. Git 到底是什么

Git 本质上是一个 **分布式版本控制系统**。

它解决的不是“保存文件”这么简单，而是 4 个核心问题：

1. **记录变化**：代码从 A 变成 B，中间每一步都可追踪
2. **多人协作**：多人可以同时改同一个项目
3. **安全回退**：改坏了能回到之前稳定版本
4. **形成历史**：知道“谁在什么时间，为什么改了什么”

一句话理解：

> Git = 给代码建立一条可以分叉、合并、回退、审计的时间线。

---

## 2. 先建立正确心智模型

很多人学 Git 卡住，不是命令背不住，而是没理解 Git 的“4 层结构”。

### 2.1 Git 的 4 个核心区域

```text
工作区（Working Tree）
    ↓ git add
暂存区（Index / Staging Area）
    ↓ git commit
本地仓库（Local Repository）
    ↓ git push / git fetch / git pull
远程仓库（Remote Repository）
```

分别理解：

- **工作区**：你当前电脑上正在直接编辑的文件
- **暂存区**：本次准备提交的内容清单
- **本地仓库**：已经提交成功的历史
- **远程仓库**：GitHub / GitLab / Gitee 上的共享版本

### 2.2 最关键的理解：Commit 是“快照”，不是“补丁”

Git 中一次提交（commit），本质上更像：

- “当前项目在这一刻的完整快照”

而不是：

- “从旧版本改了哪几行”

这也是为什么 Git 可以高效做分支、合并、回退。

### 2.3 分支到底是什么

很多人以为分支是“复制了一份代码”。

其实更准确的理解是：

> 分支只是一个指向某个提交的可移动指针。

比如：

```text
A --- B --- C  (main)
            \
             D --- E  (feature/login)
```

- `main` 指向 `C`
- `feature/login` 指向 `E`

当你在 `feature/login` 上继续提交，本质上只是这个指针继续往前移动。

### 2.4 HEAD 是什么

`HEAD` 可以理解为：

> “我当前正站在哪个提交 / 哪个分支上”

通常：

- `HEAD -> main`
- 或 `HEAD -> feature/xxx`

如果出现 **detached HEAD**，说明你现在正直接站在某个历史提交上，而不是某个正常分支上。

---

## 3. 第一次使用 Git 应该先做什么

### 3.1 配置身份

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

因为 Git 的每次提交都要记录作者信息。

### 3.2 建议的基础配置

```bash
git config --global init.defaultBranch main
git config --global core.editor "vim"
git config --global pull.rebase true
```

说明：

- `init.defaultBranch main`：新仓库默认主分支叫 `main`
- `core.editor`：提交信息默认编辑器
- `pull.rebase true`：拉取远程更新时优先使用 rebase，减少无意义 merge commit

如果要查看所有配置：

```bash
git config --list
```

---

## 4. 如何创建和获取仓库

### 4.1 新建仓库

```bash
mkdir demo
cd demo
git init
```

这会在当前目录下生成一个 `.git` 目录，它就是 Git 仓库的核心元数据。

### 4.2 克隆已有仓库

```bash
git clone <repo-url>
```

例如：

```bash
git clone https://github.com/user/project.git
```

### 4.3 `.gitignore` 是什么

`.gitignore` 用来指定：

> 哪些文件不要被 Git 跟踪

常见示例：

```gitignore
node_modules/
dist/
.env
.DS_Store
```

原则：

- 构建产物不要提交
- 本地环境文件谨慎提交
- 密钥文件绝不能随便提交

---

## 5. 日常开发最重要的 80% 工作流

如果只看最常用流程，其实就是下面这套：

```bash
git status
git add .
git commit -m "feat: add login form"
git pull --rebase
git push
```

但真正理解时，要拆开来看。

### 5.1 查看当前状态：`git status`

```bash
git status
```

这是 Git 里最值得高频使用的命令。

它能告诉你：

- 当前在哪个分支
- 哪些文件被修改了
- 哪些文件已经加入暂存区
- 有没有未跟踪文件

### 5.2 查看差异：`git diff`

```bash
git diff
git diff --staged
```

- `git diff`：看工作区和暂存区差异
- `git diff --staged`：看暂存区和上一次提交差异

### 5.3 把改动加入暂存区：`git add`

```bash
git add file.txt
git add src/
git add .
```

重点理解：

> `git add` 不是“提交”，而是“把这次准备提交的内容放进购物车”。

### 5.4 提交：`git commit`

```bash
git commit -m "fix: handle empty input"
```

提交信息建议遵循：

- 一次提交只做一类事情
- 提交信息说明“为什么改”，不要只写“update”

坏例子：

```text
update
fix
修改代码
```

好例子：

```text
feat: add password strength validation
fix: avoid null pointer in order service
docs: add setup instructions for local env
```

### 5.5 查看历史：`git log`

```bash
git log --oneline --graph --decorate --all
```

这是一个非常实用的历史查看命令，建议记住。

---

## 6. 远程仓库与同步

### 6.1 远程仓库是什么

远程仓库是团队共享代码历史的地方，比如 GitHub 上的仓库。

常见默认远程名：

- `origin`

查看远程仓库：

```bash
git remote -v
```

### 6.2 推送：`git push`

```bash
git push origin main
```

第一次推送新分支常用：

```bash
git push -u origin feature/login
```

`-u` 的作用是建立上游跟踪关系，之后就可以直接 `git push` / `git pull`。

### 6.3 拉取：`git fetch` vs `git pull`

这是 Git 初学者最容易混淆的点之一。

#### `git fetch`

```bash
git fetch
```

只做一件事：

- 把远程最新历史下载到本地

但 **不会自动合并** 到你当前分支。

#### `git pull`

```bash
git pull
```

相当于：

```bash
git fetch + git merge
```

如果使用：

```bash
git pull --rebase
```

则更接近：

```bash
git fetch + git rebase
```

### 6.4 为什么很多团队更推荐 `git pull --rebase`

因为普通 `git pull` 很容易产生很多无意义的 merge commit，让历史线变乱。

而 `pull --rebase` 的效果通常是：

- 先拿到远程最新提交
- 再把你本地尚未推送的提交“重新接”到最新历史后面

这样提交历史更线性。

---

## 7. 分支：Git 协作的核心

### 7.1 创建并切换分支

```bash
git switch -c feature/login
```

等价旧写法：

```bash
git checkout -b feature/login
```

建议优先使用：

- `git switch`
- `git restore`

因为语义更清晰。

### 7.2 切换分支

```bash
git switch main
git switch feature/login
```

### 7.3 删除分支

```bash
git branch -d feature/login
```

如果是强制删除：

```bash
git branch -D feature/login
```

### 7.4 推荐的分支命名

```text
feature/login-page
fix/payment-timeout
refactor/user-service
docs/setup-guide
```

### 7.5 推荐协作流

一个很稳的团队协作流通常是：

1. 基于 `main` 拉最新代码
2. 新建功能分支
3. 在功能分支开发
4. 自测通过后推送远程
5. 提交 PR / MR
6. 代码评审通过后合并回 `main`

---

## 8. merge 和 rebase 到底怎么选

这是 Git 学习中的核心分水岭。

### 8.1 merge：保留分叉历史

```bash
git merge feature/login
```

效果：

- 把另一个分支的改动合并进来
- 保留“曾经分叉过”的历史结构

适合：

- 团队协作
- 公共分支合并
- 想保留完整历史结构

### 8.2 rebase：改写提交接入位置

```bash
git rebase main
```

效果：

- 把当前分支的提交“摘下来”
- 重新接到 `main` 最新提交之后

适合：

- 整理你自己的本地分支历史
- 让历史更线性

### 8.3 一句话区别

- **merge**：把两条线接起来
- **rebase**：把你这条线搬家后再接上去

### 8.4 非常重要的原则

> 不要随便 rebase 已经推送给团队共用的公共历史。

因为 rebase 会改写提交 ID，别人已经基于旧历史开发时，会造成协作混乱。

一个稳妥原则：

- **自己的本地分支**：可以 rebase
- **团队共享分支**：谨慎 rebase

---

## 9. 冲突为什么会发生，怎么处理

### 9.1 冲突本质

冲突不是 Git “坏了”，而是 Git 无法自动判断：

> 同一段代码的两个修改，应该保留哪一个。

常见触发场景：

- merge 时冲突
- rebase 时冲突
- stash pop 时冲突

### 9.2 冲突标记长什么样

```text
<<<<<<< HEAD
当前分支内容
=======
另一个分支内容
>>>>>>> feature/login
```

你需要手动编辑成最终想保留的样子。

### 9.3 处理冲突的标准流程

1. 打开冲突文件
2. 删除冲突标记
3. 手动整理为最终版本
4. 重新加入暂存区
5. 继续 merge / rebase

例如 rebase 场景：

```bash
git add conflicted-file
git rebase --continue
```

如果想放弃本次 rebase：

```bash
git rebase --abort
```

如果是 merge 放弃：

```bash
git merge --abort
```

---

## 10. 撤销与回退：这是最容易误用的一组命令

这一部分必须系统掌握。

### 10.1 撤销工作区修改：`git restore`

```bash
git restore file.txt
```

作用：

- 丢弃工作区中尚未暂存的改动

### 10.2 撤销暂存：`git restore --staged`

```bash
git restore --staged file.txt
```

作用：

- 把文件从暂存区拿出来
- 但不会删除工作区改动

### 10.3 修改上一次提交：`git commit --amend`

```bash
git commit --amend
```

适合：

- 漏加了一个文件
- 提交信息写错了

注意：

- 如果这个提交已经推送给别人，不要轻易 amend 后再强推

### 10.4 `git reset`：移动指针

#### soft reset

```bash
git reset --soft HEAD~1
```

效果：

- 撤销最近一次提交
- 改动保留在暂存区

#### mixed reset（默认）

```bash
git reset HEAD~1
```

效果：

- 撤销最近一次提交
- 改动回到工作区

#### hard reset

```bash
git reset --hard HEAD~1
```

效果：

- 撤销提交
- 清空暂存区
- 丢弃工作区改动

这是破坏性最强的 reset，用之前一定要确认。

### 10.5 `git revert`：最安全的回退方式

```bash
git revert <commit-id>
```

它不是“删除历史”，而是：

> 新建一个反向提交，抵消之前那次提交的影响。

所以：

- **公共分支回退优先用 revert**
- **本地未共享历史整理可以用 reset**

### 10.6 `reflog`：后悔药

```bash
git reflog
```

如果你误 reset、误切分支、误删提交，`reflog` 经常能把你救回来。

比如：

```bash
git reset --hard <某个 reflog 里的 commit>
```

---

## 11. 进阶但非常实用的命令

### 11.1 临时收纳改动：`git stash`

```bash
git stash
git stash pop
git stash list
```

适合场景：

- 改到一半突然要切分支处理紧急问题

### 11.2 挑选某个提交：`git cherry-pick`

```bash
git cherry-pick <commit-id>
```

作用：

- 把另一个分支上的某个特定提交单独拣过来

适合：

- 热修复同步
- 只需要某一个 commit，不想整分支合并

### 11.3 打标签：`git tag`

```bash
git tag v1.0.0
git push origin v1.0.0
```

适合：

- 发布版本
- 记录里程碑

### 11.4 查文件是谁改的：`git blame`

```bash
git blame file.txt
```

适合：

- 排查某行代码是谁、何时引入的

### 11.5 查某次提交改了什么：`git show`

```bash
git show <commit-id>
```

---

## 12. 真正高频的 Git 命令清单

### 12.1 状态与差异

```bash
git status
git diff
git diff --staged
git log --oneline --graph --decorate --all
```

### 12.2 提交相关

```bash
git add .
git add <file>
git commit -m "message"
git commit --amend
```

### 12.3 分支相关

```bash
git branch
git switch main
git switch -c feature/xxx
git branch -d feature/xxx
```

### 12.4 远程同步

```bash
git fetch
git pull --rebase
git push
git push -u origin feature/xxx
```

### 12.5 回退与恢复

```bash
git restore <file>
git restore --staged <file>
git reset --soft HEAD~1
git reset --hard HEAD~1
git revert <commit-id>
git reflog
```

### 12.6 其他常用

```bash
git stash
git stash pop
git cherry-pick <commit-id>
git tag
git blame <file>
```

---

## 13. 一套稳妥的日常开发模板

如果你平时在团队里开发，一个很稳的模板如下。

### 13.1 开始开发前

```bash
git switch main
git pull --rebase
git switch -c feature/my-task
```

### 13.2 开发过程中

```bash
git status
git diff
git add .
git commit -m "feat: complete task A"
```

### 13.3 推送并提 PR 前

```bash
git fetch origin
git rebase origin/main
git push -u origin feature/my-task
```

如果已经推送过，且 rebase 改写了历史，可能需要：

```bash
git push --force-with-lease
```

注意是 **`--force-with-lease`**，不是裸 `--force`。

因为它更安全，会检查远程是否被别人改动过。

### 13.4 合并后清理

```bash
git switch main
git pull --rebase
git branch -d feature/my-task
```

---

## 14. 初学者最容易踩的坑

### 坑 1：把 `git add` 当成提交

不是。

- `git add` 是放进暂存区
- `git commit` 才是真正形成历史

### 坑 2：一把梭 `git add .`

可以用，但先看 `git status` / `git diff`，不要把不该提交的文件带进去。

### 坑 3：在公共分支上直接乱改

正确做法通常是：

- 从主分支拉出新分支开发

### 坑 4：不理解 `merge` 和 `rebase` 就乱用

记住：

- 想保留分叉历史，用 `merge`
- 想整理自己的线性历史，用 `rebase`

### 坑 5：在已经共享的提交上随意 `reset` / `amend` / `rebase`

这些操作会改写历史，容易把别人协作搞乱。

### 坑 6：误用 `git reset --hard`

这条命令很危险，会直接丢掉未保存改动。

除非你非常确定，否则先：

```bash
git status
git diff
git stash
```

### 坑 7：出了问题不会先看 `reflog`

很多“完蛋了”的场景，其实 `git reflog` 都能救。

---

## 15. Git 背后的对象模型（进阶理解）

如果你想真正理解 Git，可以再往下一层看：

- **blob**：文件内容对象
- **tree**：目录结构对象
- **commit**：一次快照提交
- **tag**：标签对象

Git 的历史，本质上是：

> 一组对象 + 一组引用（refs）构成的有向图。

所以：

- 分支本质是 ref
- HEAD 是特殊 ref
- commit 通过父指针连成历史图

理解到这里，你会发现很多 Git 命令本质上都是：

- 移动引用
- 创建提交
- 切换工作区内容

---

## 16. 建议的学习顺序

如果你想系统掌握 Git，建议按这个顺序：

### 第 1 阶段：先掌握日常开发闭环

只学这些就够：

- `status`
- `diff`
- `add`
- `commit`
- `push`
- `pull --rebase`
- `switch`

### 第 2 阶段：掌握分支协作

重点学：

- `branch`
- `merge`
- `rebase`
- 冲突处理

### 第 3 阶段：掌握恢复能力

重点学：

- `restore`
- `reset`
- `revert`
- `reflog`
- `stash`

### 第 4 阶段：掌握进阶工具

重点学：

- `cherry-pick`
- `tag`
- `blame`
- `show`

---

## 17. 一句话总结 Git

如果要把 Git 压缩成一句最核心的话：

> Git 不是一堆命令，而是一套“管理代码时间线”的系统。

真正重要的不是你背了多少命令，而是你是否理解：

- 当前改动在哪一层
- 这次操作会移动什么指针
- 它会不会改写历史
- 它对协作者有没有影响

一旦这四件事想清楚，Git 就不再“玄学”。

---

## 18. 推荐练习题

可以自己开一个测试仓库，重复练这些动作：

1. `init` 一个仓库并做 3 次提交
2. 新建一个分支改同一文件，再回主分支也改同一文件，制造冲突并解决
3. 用 `rebase` 把功能分支接到最新主分支后
4. 故意 `reset --hard`，再用 `reflog` 找回来
5. 用 `stash` 临时保存改动再恢复
6. 打一个 `tag`

只要这些动作你都做过一遍，Git 基本就入门了。

---

## 19. 一个最小速查模板

```bash
# 看状态
git status

# 看差异
git diff
git diff --staged

# 新建分支
git switch -c feature/xxx

# 提交
git add .
git commit -m "feat: xxx"

# 同步远程
git pull --rebase
git push -u origin feature/xxx

# 合并主分支最新改动
git fetch origin
git rebase origin/main

# 放弃工作区改动
git restore <file>

# 撤销最近提交但保留改动
git reset --soft HEAD~1

# 安全回退公共历史
git revert <commit-id>

# 后悔药
git reflog
```

---

## 20. 适用场景归类

- **入门理解**：工作区、暂存区、本地仓库、远程仓库
- **日常开发**：status / add / commit / pull --rebase / push
- **团队协作**：branch / merge / rebase / PR
- **问题恢复**：restore / reset / revert / reflog
- **进阶效率**：stash / cherry-pick / tag / blame

如果以后还要继续扩展，可以基于这篇再深入：

- GitHub Pull Request 工作流
- Git rebase 交互式整理（`git rebase -i`）
- Git hooks
- Git 子模块（submodule）
- Git 大文件管理（LFS）
