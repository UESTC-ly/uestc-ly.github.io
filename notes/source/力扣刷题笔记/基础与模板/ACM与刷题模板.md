# ACM与刷题模板

> 目标：把 BISHI1-BISHI8 整理成一份 **便于复习、便于迁移套路、便于手写 ACM 模式** 的笔记。

---

# ACM 模式先记住

## 1. 什么是 ACM 模式
ACM 模式就是：

- 自己写 `main`
- 自己读输入
- 自己处理逻辑
- 自己输出答案

最常见骨架：

```cpp
#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;

    // 处理输入
    // 调用逻辑
    // 输出答案

    return 0;
}
```

## 2. 刷题时优先注意

1. 输入是一行一个操作，还是一行两个数
2. 操作是字符串，还是数字编号
3. 输出是每次查询都输出，还是最后统一输出
4. 下标从 0 开始还是 1 开始
5. 容器是否允许重复

## 3. 常用输出习惯
优先写：

```cpp
cout << ans << '\n';
```

少用：

```cpp
cout << ans << endl;
```

因为 `endl` 会额外刷新缓冲区，比赛里通常没必要。

---

# BISHI1：顺序表 8 种操作

## 题型判断

- 模拟题
- 顺序表 / `vector` 基础操作
- 数据结构题

## 一眼识别信号
题目让你维护一个序列，支持：

- 尾插
- 尾删
- 按下标访问
- 中间插入
- 排序
- 输出长度
- 输出整个序列

这种题直接想：

> `vector<int>` 暴力模拟。

## 为什么用 `vector`
因为题目数据范围不大，且操作刚好都能映射成 STL：

- `push_back`
- `pop_back`
- `a[i]`
- `insert`
- `sort`
- `size`

## 关键代码模板

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <functional>
using namespace std;

int main() {
    int q;
    cin >> q;

    vector<int> a;

    while (q--) {
        int op;
        cin >> op;

        if (op == 1) {
            int x;
            cin >> x;
            a.push_back(x);
        }
        else if (op == 2) {
            a.pop_back();
        }
        else if (op == 3) {
            int i;
            cin >> i;
            cout << a[i] << '\n';
        }
        else if (op == 4) {
            int i, x;
            cin >> i >> x;
            a.insert(a.begin() + i + 1, x);
        }
        else if (op == 5) {
            sort(a.begin(), a.end());
        }
        else if (op == 6) {
            sort(a.begin(), a.end(), greater<int>());
        }
        else if (op == 7) {
            cout << a.size() << '\n';
        }
        else if (op == 8) {
            for (int i = 0; i < (int)a.size(); i++) {
                if (i > 0) cout << ' ';
                cout << a[i];
            }
            cout << '\n';
        }
    }

    return 0;
}
```

## 最容易错的点

### 1. 插入位置为什么是 `i + 1`

```cpp
a.insert(a.begin() + i + 1, x);
```

因为 `insert(pos, x)` 的意思是：

> 把 `x` 插到 `pos` 前面。

题目说“插到 `i` 和 `i+1` 中间”，等价于：

> 插到原来 `i+1` 这个位置前面。

所以是 `i+1`。

### 2. 输出整个数组时的空格
稳妥写法：

```cpp
if (i > 0) cout << ' ';
cout << a[i];
```

## 记忆口诀

> 多操作维护一个序列，先想 `vector`。  
> 插入是 `insert`，排序是 `sort`，整行输出注意空格。

---

# BISHI2：栈的基础操作

## 题型判断

- 栈
- 模拟题
- 基础数据结构

## 一眼识别信号
支持：

- `push x`
- `pop`
- `query`
- `size`

这就是标准栈。

## 为什么用 `stack`
栈特征：

> 后进先出（LIFO）

所以直接：

```cpp
stack<long long> st;
```

## 代码模板

```cpp
#include <iostream>
#include <stack>
#include <string>
using namespace std;

int main() {
    int n;
    cin >> n;

    stack<long long> st;

    while (n--) {
        string op;
        cin >> op;

        if (op == "push") {
            long long x;
            cin >> x;
            st.push(x);
        }
        else if (op == "pop") {
            if (st.empty()) cout << "Empty" << '\n';
            else st.pop();
        }
        else if (op == "query") {
            if (st.empty()) cout << "Empty" << '\n';
            else cout << st.top() << '\n';
        }
        else if (op == "size") {
            cout << st.size() << '\n';
        }
    }

    return 0;
}
```

## 易错点

1. `pop` 空栈时也要输出 `Empty`
2. `query` 前必须先 `empty()`
3. 命令是字符串，要用 `string op`

## 记忆口诀

> 栈：后进先出。  
> `push` 进，`pop` 出，`query` 看顶，`size` 看数量。

---

# BISHI3：队列的基础操作

## 题型判断

- 队列
- 模拟题
- 基础数据结构

## 一眼识别信号
支持：

- 入队
- 出队头
- 查队头
- 查长度

这就是标准队列。

## 为什么用 `queue`
队列特征：

> 先进先出（FIFO）

## 代码模板

```cpp
#include <iostream>
#include <queue>
using namespace std;

int main() {
    int n;
    cin >> n;

    queue<long long> q;

    while (n--) {
        int op;
        cin >> op;

        if (op == 1) {
            long long x;
            cin >> x;
            q.push(x);
        }
        else if (op == 2) {
            if (q.empty()) cout << "ERR_CANNOT_POP" << '\n';
            else q.pop();
        }
        else if (op == 3) {
            if (q.empty()) cout << "ERR_CANNOT_QUERY" << '\n';
            else cout << q.front() << '\n';
        }
        else if (op == 4) {
            cout << q.size() << '\n';
        }
    }

    return 0;
}
```

## 易错点

1. `op == 3` 空时输出是 `ERR_CANNOT_QUERY`，不是 `ERR_CANNOT_POP`
2. 查询队首用 `front()`，不是 `back()`
3. 已知循环次数时，不需要 `else break`

## 记忆口诀

> 队列：先进先出。  
> `push` 进队尾，`pop` 删队头，`query` 看队头。

---

# BISHI4：有序集合 `set`

## 题型判断

- 有序集合
- 前驱 / 后继
- STL `set`

## 一眼识别信号
题目同时出现：

- 插入
- 删除
- 查询是否存在
- 查询大小
- 前驱
- 后继

这种题要想到：

> `set<int>`

## 为什么用 `set`

- 自动去重
- 自动有序
- 支持 `lower_bound / upper_bound`

## 代码模板

```cpp
#include <iostream>
#include <set>
using namespace std;

int main() {
    int n;
    cin >> n;

    set<int> s;

    while (n--) {
        int op;
        cin >> op;

        if (op == 1) {
            int x;
            cin >> x;
            s.insert(x);
        }
        else if (op == 2) {
            int x;
            cin >> x;
            s.erase(x);
        }
        else if (op == 3) {
            int x;
            cin >> x;
            cout << (s.count(x) ? "YES" : "NO") << '\n';
        }
        else if (op == 4) {
            cout << s.size() << '\n';
        }
        else if (op == 5) {
            int x;
            cin >> x;
            auto it = s.lower_bound(x);
            if (it == s.begin()) cout << -1 << '\n';
            else {
                --it;
                cout << *it << '\n';
            }
        }
        else if (op == 6) {
            int x;
            cin >> x;
            auto it = s.upper_bound(x);
            if (it == s.end()) cout << -1 << '\n';
            else cout << *it << '\n';
        }
    }

    return 0;
}
```

## 核心知识点

### `lower_bound(x)`
返回：

> 第一个 `>= x` 的位置

### `upper_bound(x)`
返回：

> 第一个 `> x` 的位置

### 前驱为什么这样找
前驱定义：

> 小于 `x` 的最大值

所以：

- 先找第一个 `>= x` 的位置
- 再往前退一格

### 后继为什么这样找
后继定义：

> 大于 `x` 的最小值

所以直接：

```cpp
auto it = s.upper_bound(x);
```

## 易错点

1. 三目运算放进 `cout` 要加括号：

```cpp
cout << (s.count(x) ? "YES" : "NO") << '\n';
```

2. `it == begin()` 时不能再 `--it`
3. 后继用 `upper_bound`，不是 `lower_bound`

## 记忆口诀

> 前驱看左边，后继看右边。  
> 前驱：`lower_bound` 再退一格；后继：`upper_bound` 直接取。

---

# BISHI5：有序多重集合 `multiset`

## 题型判断

- 有序多重集合
- 允许重复
- 前驱 / 后继
- STL `multiset`

## 一眼识别信号
题目除了插删查前驱后继外，还出现：

- 查询某个值出现次数
- 删除时只删一个
- 允许重复

这时要想到：

> `multiset<int>`

## 为什么不用 `set`
因为 `set` 会去重，而这题要求：

> 相同元素可以存在多个。

## 代码模板

```cpp
#include <iostream>
#include <set>
using namespace std;

int main() {
    int n;
    cin >> n;

    multiset<int> ms;

    while (n--) {
        int op, x;
        cin >> op >> x;

        if (op == 1) {
            ms.insert(x);
        }
        else if (op == 2) {
            auto it = ms.find(x);
            if (it != ms.end()) ms.erase(it);  // 只删一个
        }
        else if (op == 3) {
            cout << ms.count(x) << '\n';
        }
        else if (op == 4) {
            cout << ms.size() << '\n';
        }
        else if (op == 5) {
            auto it = ms.lower_bound(x);
            if (it == ms.begin()) cout << -1 << '\n';
            else {
                --it;
                cout << *it << '\n';
            }
        }
        else if (op == 6) {
            auto it = ms.upper_bound(x);
            if (it == ms.end()) cout << -1 << '\n';
            else cout << *it << '\n';
        }
    }

    return 0;
}
```

## 本题最关键的坑

### 删除一个元素不能写：

```cpp
ms.erase(x);
```

因为这会：

> 把所有值等于 `x` 的元素全部删掉。

### 正确写法：

```cpp
auto it = ms.find(x);
if (it != ms.end()) ms.erase(it);
```

这样才是：

> 只删一个。

## 易错点

1. `size()` 统计的是总元素数，重复也算
2. `count(x)` 在 `multiset` 里可能大于 1
3. 前驱 / 后继模板和 `set` 完全一样

## 记忆口诀

> `set` 去重，`multiset` 保重。  
> 删一个要 `find + erase(it)`，别直接 `erase(x)`。

---

# BISHI6：维护最小值 —— 小根堆 / `priority_queue`

## 题型判断

- 堆
- 优先队列
- 动态维护最小值

## 一眼识别信号
题目只关心：

- 插入元素
- 查询最小值
- 删除最小值

这种题优先想：

> 小根堆

## 为什么不用 `multiset`
`multiset` 当然也能做，
但这题只需要维护“最小值”，不需要：

- 删除任意值
- 查前驱后继
- 查某值出现次数

所以堆更贴切。

## 小根堆写法

```cpp
priority_queue<int, vector<int>, greater<int>> pq;
```

含义：

- 默认 `priority_queue<int>` 是大根堆
- 加 `greater<int>` 后变成小根堆

## 代码模板

```cpp
#include <iostream>
#include <queue>
#include <vector>
#include <functional>
using namespace std;

int main() {
    int n;
    cin >> n;

    priority_queue<int, vector<int>, greater<int>> pq;

    while (n--) {
        int op;
        cin >> op;

        if (op == 1) {
            int x;
            cin >> x;
            pq.push(x);
        }
        else if (op == 2) {
            cout << pq.top() << '\n';
        }
        else if (op == 3) {
            pq.pop();
        }
    }

    return 0;
}
```

## 易错点

1. `top()` 只是看，不删除
2. `pop()` 才是删除堆顶
3. 默认是大根堆，小根堆要写完整模板

## 记忆口诀

> 插入一个，查最小，删最小 —— 直接小根堆。

---

# BISHI7：统计不同字符串个数

## 题型判断

- 字符串
- 去重统计
- `set / unordered_set`

## 一眼识别信号
题目问的是：

> 不同字符串的个数

第一反应：

> 去重

## 为什么用集合
集合天然支持：

- 自动去重
- 最后直接 `size()`

## `set` 写法

```cpp
#include <iostream>
#include <set>
#include <string>
using namespace std;

int main() {
    int N;
    cin >> N;

    set<string> s;

    while (N--) {
        string str;
        cin >> str;
        s.insert(str);
    }

    cout << s.size() << '\n';
    return 0;
}
```

## `unordered_set` 写法（更快）

```cpp
#include <iostream>
#include <unordered_set>
#include <string>
using namespace std;

int main() {
    int N;
    cin >> N;

    unordered_set<string> s;

    while (N--) {
        string str;
        cin >> str;
        s.insert(str);
    }

    cout << s.size() << '\n';
    return 0;
}
```

## 易错点

1. 题目区分大小写，所以：
   - `Hello`
   - `hello`
   - `HELLO`
   都算不同字符串
2. 不需要自己计数，直接输出 `size()`

## 记忆口诀

> 问不同元素个数，就想 `set / unordered_set` 去重。

---

# BISHI8：哈希映射 + `mod 2^64`

## 题型判断

- 哈希表
- 映射维护
- 数学取模技巧
- 模拟题

## 题目本质
维护映射：

\[
f : [0, 2^{64}) \to [0, 2^{64})
\]

初始所有 `f(x)=0`。

每次给 `(x, y)`：

1. 先取当前 `f(x)`，记作 `ans_i`
2. 再更新 `f(x) = y`

最后求：

\[
\sum_{i=1}^{n} i \times ans_i \pmod{2^{64}}
\]

## 为什么用 `unordered_map`
因为 `x` 的值域极大：

\[
0 \le x < 2^{64}
\]

不可能开数组。

但真正出现的键最多只有 `n` 个，所以用：

```cpp
unordered_map<unsigned long long, unsigned long long>
```

## 为什么 `unsigned long long` 正好适合
题目要求的是：

\[
\bmod 2^{64}
\]

而 C++ 里 `unsigned long long` 溢出时，效果正好等价于：

> 自动对 `2^64` 取模。

所以直接累加就行，不需要手动 `%`。

## 代码模板

```cpp
#include <iostream>
#include <unordered_map>
using namespace std;

using ull = unsigned long long;

int main() {
    int n;
    cin >> n;

    unordered_map<ull, ull> mp;
    mp.reserve(2 * n);

    ull res = 0;

    for (ull i = 1; i <= (ull)n; i++) {
        ull x, y;
        cin >> x >> y;

        ull old = mp[x];
        res += i * old;   // 自然按 mod 2^64 处理
        mp[x] = y;
    }

    cout << res << '\n';
    return 0;
}
```

## 核心知识点 1：为什么 `mp[x]` 不存在时是 0
因为 `unordered_map` 的 `operator[]`：

```cpp
mp[x]
```

如果键不存在，会：

1. 自动新建这个键
2. 对应值用默认值初始化

对于 `unsigned long long`，默认值就是 `0`。

所以这里非常方便。

## 核心知识点 2：为什么写 `mp.reserve(2 * n)`
`reserve` 不是必须，但它的作用是：

> 提前给哈希表留空间，减少扩容和 rehash。

不写也对，但写了更稳更快。

## 核心知识点 3：`using ull = unsigned long long;`
这是类型别名，方便少写一长串：

```cpp
using ull = unsigned long long;
```

不要写错成：

```cpp
using unsigned long long as ull; // 错误
```

## 易错点

1. 先取旧值，再更新新值，顺序不能反
2. 值域太大，不能开数组
3. `mod 2^64` 不需要手写取模，直接靠无符号溢出

## 记忆口诀

> 值域太大不开数组，出现过的键用哈希表存。  
> 先取旧值算贡献，再更新新值。  
> `unsigned long long` 溢出 = 自动模 `2^64`。

---

# 这 8 题的总复盘

## 1. 什么时候用 `vector`
当题目让你维护一个序列，支持：

- 尾插尾删
- 下标访问
- 中间插入
- 排序

优先想到：

```cpp
vector
```

---

## 2. 什么时候用 `stack`
当题目体现：

> 后进先出

想到：

```cpp
stack
```

---

## 3. 什么时候用 `queue`
当题目体现：

> 先进先出

想到：

```cpp
queue
```

---

## 4. 什么时候用 `set`
当题目需要：

- 去重
- 有序
- 前驱 / 后继

想到：

```cpp
set
```

---

## 5. 什么时候用 `multiset`
当题目需要：

- 有序
- 允许重复
- 前驱 / 后继
- 统计某值个数

想到：

```cpp
multiset
```

---

## 6. 什么时候用小根堆
当题目只关心：

- 插入
- 查最小值
- 删除最小值

想到：

```cpp
priority_queue<int, vector<int>, greater<int>>
```

---

## 7. 什么时候用 `set / unordered_set`
当题目问：

- 不同元素个数
- 去重后有多少

想到：

```cpp
set / unordered_set
```

---

## 8. 什么时候用 `unordered_map`
当题目需要：

- 维护键值映射
- 键范围极大
- 只关心出现过的键

想到：

```cpp
unordered_map
```

---

# 最后总口诀

> 顺序表用 `vector`，后进先出用 `stack`，先进先出用 `queue`。  
> 去重有序用 `set`，可重有序用 `multiset`，只管最值用堆。  
> 问不同个数用 `set / unordered_set`，值域太大映射关系用 `unordered_map`。

---

# BISHI9：田忌赛马（3 匹马全排列）

## 题型判断

- 暴力枚举
- 排列
- 模拟题

## 一眼识别信号

题目特征是：

- 元素个数特别少（这里只有 3 匹马）
- 一方顺序固定
- 另一方顺序可以调整
- 问“是否存在一种安排可以获胜”

这种题优先想到：

> 枚举所有排列，看有没有合法方案。

## 题目白话

齐威王和田忌各有 3 匹马。

- 齐威王的出场顺序固定：`v1, v2, v3`
- 田忌的 3 匹马速度分别是：`a1, a2, a3`
- 田忌可以自己决定出场顺序
- 每一场如果田忌的马速度 **严格大于** 对方，就赢这一场
- 三局两胜，问田忌能不能赢

## 为什么想到全排列

因为田忌只有 3 匹马。

3 匹马所有出场顺序一共只有：

\[
3! = 6
\]

种。

数量非常小，所以没必要想复杂贪心，直接把所有顺序都试一遍最稳。

## 核心思路拆解

### 1. 齐威王顺序固定，不能改
所以输入后不要排序，也不要调整顺序。

### 2. 枚举田忌的所有排列
先把田忌的马排序：

```cpp
sort(tian.begin(), tian.end());
```

然后用：

```cpp
next_permutation(tian.begin(), tian.end())
```

依次得到所有排列。

### 3. 对每种排列统计胜场数
逐场比较：

- 第 1 场：`tian[0]` 和 `qiwei[0]`
- 第 2 场：`tian[1]` 和 `qiwei[1]`
- 第 3 场：`tian[2]` 和 `qiwei[2]`

如果：

```cpp
tian[i] > qiwei[i]
```

就说明田忌赢这一场。

### 4. 只要有一种排列赢至少 2 场
就输出：

```text
Yes
```

否则输出：

```text
No
```

## ACM 模式代码模板

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    vector<int> tian(3), qiwei(3);

    for (int i = 0; i < 3; i++) cin >> qiwei[i];
    for (int i = 0; i < 3; i++) cin >> tian[i];

    sort(tian.begin(), tian.end());

    do {
        int win = 0;
        for (int i = 0; i < 3; i++) {
            if (tian[i] > qiwei[i]) win++;
        }

        if (win >= 2) {
            cout << "Yes" << '\n';
            return 0;
        }
    } while (next_permutation(tian.begin(), tian.end()));

    cout << "No" << '\n';
    return 0;
}
```

## `next_permutation` 最简理解

`next_permutation` 是 C++ 标准库 `<algorithm>` 里的函数。

作用是：

> 自动把当前顺序换成“下一种排列”。

最常见搭配：

```cpp
sort(a.begin(), a.end());

do {
    // 处理当前排列
} while (next_permutation(a.begin(), a.end()));
```

意思是：

- 先从最小排列开始
- 然后把所有排列一个一个试完

## 易错点

### 1. 不要排序齐威王
齐威王顺序是固定的，只能枚举田忌。

### 2. 必须是一一配对
不是看某匹马能赢几匹，
而是每场固定比一对。

### 3. 必须严格大于才算赢
要写：

```cpp
tian[i] > qiwei[i]
```

不能写成：

```cpp
tian[i] >= qiwei[i]
```

### 4. 枚举全排列前记得先排序
如果不先 `sort`，可能枚举不全。

## 记忆口诀

> 谁能调顺序，就枚举谁。  
> 元素只有 3 个，能排几种就全排。  
> 顺序固定的一边别动，逐场一一比较胜场数。

---

# BISHI10：取石子博弈（周期为 `l+r`）

## 题型判断

- 博弈论
- 必胜 / 必败态
- 找规律题

## 一眼识别信号

题目特征：

- 两个人轮流操作
- 每次必须取一段范围内的石子数
- 双方都最优
- 问先手能不能必胜

这种题先想：

> 哪些状态是必败态，哪些状态是必胜态。

## 题目白话

有 `n` 个石子。

每次必须取：

$$
l \le x \le r
$$

个石子。

规则：

- 如果当前剩余石子数 `< l`，当前人就没法操作，直接输
- 谁拿到最后一个石子，谁赢

问先手能不能必胜。

## 从小到大找规律

### 第一段：必败态
如果：

$$
0 \le n \le l-1
$$

因为连最少 `l` 个都拿不了，所以当前人直接输。

因此：

$$
[0,\; l-1]
$$

整段都是**必败态**。

---

### 第二段：必胜态
如果：

$$
l \le n \le l+r-1
$$

先手总能取一些石子，让对手剩下：

$$
[0,\; l-1]
$$

中的某个数。

而这一整段刚证明过是必败态。

所以：

$$
[l,\; l+r-1]
$$

整段都是**必胜态**。

---

### 第三段：必败态
现在看：

$$
[l+r,\; 2l+r-1]
$$

假设当前有一个数 $n$ 落在这段里。无论你取多少个，

$$
x \in [l,r]
$$

剩下的是：

$$
n-x
$$

最小会剩：

$$
n-r \ge (l+r)-r = l
$$

最大会剩：

$$
n-l \le (2l+r-1)-l = l+r-1
$$

所以无论怎么拿，剩下都一定落在：

$$
[l,\; l+r-1]
$$

而这一整段我们已经证明过，是**必胜态**。

也就是说：

> 你怎么走，都会把对手送到必胜态。

所以你当前就是**必败态**。

因此：

$$
[l+r,\; 2l+r-1]
$$

整段都是**必败态**。

---

### 第四段：必胜态
接下来再看：

$$
[2l+r,\; 2l+2r-1]
$$

这一段中的任意一个数，都可以通过某种合法取法，把对手送到上一个必败段：

$$
[l+r,\; 2l+r-1]
$$

所以：

$$
[2l+r,\; 2l+2r-1]
$$

整段都是**必胜态**。

---

## 规律总结

状态会按长度为：

$$
l+r
$$

的周期循环：

- 前 `l` 个是**必败态**
- 后 `r` 个是**必胜态**

也就是说，令：

$$
k = n \bmod (l+r)
$$

那么：

- 如果 $k < l$，先手必败，输出 `NO`
- 否则，先手必胜，输出 `YES`

## ACM 模式代码模板

```cpp
#include <iostream>
using namespace std;

int main() {
    int T;
    cin >> T;

    while (T--) {
        long long n, l, r;
        cin >> n >> l >> r;

        long long k = n % (l + r);

        if (k < l) cout << "NO" << '\n';
        else cout << "YES" << '\n';
    }

    return 0;
}
```

## 复杂度分析

每组数据只做一次取模和判断：

- 单组时间复杂度：`O(1)`
- 总时间复杂度：`O(T)`
- 空间复杂度：`O(1)`

## 易错点

### 1. 不是看 `n < l` 就结束
那只是第一段必败态。

真正结论是看：

$$
n \bmod (l+r)
$$

### 2. 不是随便找一个样例猜规律
要先分清：

- 一整段都能一步走到必败态 → 这段是必胜态
- 一整段无论怎么走都只能走到必胜态 → 这段是必败态

### 3. 输出大小写别写错
题目要求：

- 必胜输出 `YES`
- 否则输出 `NO`

## 记忆口诀

> 周期是 `l+r`。  
> 前 `l` 个必败，后 `r` 个必胜。  
> `n % (l+r) < l` 输出 `NO`，否则输出 `YES`。
