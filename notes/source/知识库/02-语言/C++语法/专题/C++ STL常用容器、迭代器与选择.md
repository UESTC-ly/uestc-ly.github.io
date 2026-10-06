# C++ STL 常用容器、迭代器与选择

> 本笔记整理本次新增会话中对 STL 常用容器的讲解，涵盖 `vector`、`list`、`deque`、`map`、`unordered_map`、`set`、`priority_queue`，以及迭代器和失效规则。
>
> 相关技术栈索引：[秋招求职技术栈](../秋招求职技术栈.md)

## 1. STL 的组成

STL 是 **Standard Template Library（标准模板库）**，主要组成包括：

```text
容器：保存数据
迭代器：以统一方式访问容器元素
算法：排序、查找、统计等
函数对象：定制算法行为
分配器：管理容器所需内存
```

典型协作方式：

```cpp
#include <algorithm>
#include <iostream>
#include <vector>

int main() {
    std::vector<int> numbers{3, 1, 2}; // 容器

    // begin()、end() 提供迭代器，sort 是通用算法
    std::sort(numbers.begin(), numbers.end());

    for (int number : numbers) {
        std::cout << number << ' ';
    }
}
```

常用容器可以分为：

- 顺序容器：`vector`、`list`、`deque`；
- 关联容器：`map`、`set`；
- 无序关联容器：`unordered_map`；
- 容器适配器：`priority_queue`。

## 2. 容器总览

| 容器               | 核心特点           | 典型复杂度                             | 主要用途        |
| ---------------- | -------------- | --------------------------------- | ----------- |
| `vector`         | 连续内存、支持下标      | 下标 `O(1)`；尾插均摊 `O(1)`；中间增删 `O(n)` | 默认动态数组      |
| `list`           | 双向链表、不支持下标     | 查找 `O(n)`；已知位置增删 `O(1)`           | 在已知位置频繁增删   |
| `deque`          | 分段存储、支持下标和两端操作 | 下标 `O(1)`；两端增删 `O(1)`             | 频繁操作头尾      |
| `map`            | 键唯一且有序         | 查找、插入、删除 `O(log n)`               | 有序键值对、范围查询  |
| `unordered_map`  | 哈希表、遍历无序       | 平均 `O(1)`，最坏 `O(n)`               | 快速按键查找      |
| `set`            | 元素唯一且有序        | 查找、插入、删除 `O(log n)`               | 有序去重、存在性判断  |
| `priority_queue` | 堆结构，只访问最高优先级元素 | `top()` 为 `O(1)`；增删 `O(log n)`    | 持续取得最大值或最小值 |

快速选择：

```text
普通顺序数据              → vector
频繁操作头尾              → deque
已知位置频繁插入、删除    → list
键值对且需要有序          → map
键值对且追求平均快速查找  → unordered_map
去重并保持有序            → set
持续取得最大值或最小值    → priority_queue
```

## 3. `std::vector`：连续动态数组

`vector` 是可自动扩容的连续动态数组，通常应作为顺序容器的默认选择。

```cpp
#include <iostream>
#include <vector>

int main() {
    std::vector<int> numbers{10, 20, 30};

    numbers.push_back(40); // 尾部添加元素
    numbers[1] = 200;      // 支持随机访问和修改

    for (int number : numbers) {
        std::cout << number << ' ';
    }
}
```

### 3.1 连续内存的意义

元素在逻辑和物理上连续存放：

```text
[10][20][30][40]
```

因此：

- 可以通过下标在 `O(1)` 时间内访问元素；
- 缓存局部性通常较好；
- 可以在需要连续数据的接口中使用其数据区；
- 中间插入和删除需要移动后续元素，通常是 `O(n)`。

即使程序存在一定数量的中间增删，`vector` 也可能因为连续内存和缓存局部性而比链表更快。

### 3.2 常用接口

```cpp
std::vector<int> numbers;

numbers.push_back(10);        // 尾部添加
numbers.push_back(20);
numbers.pop_back();           // 删除末尾元素，但不返回该元素

bool isEmpty = numbers.empty();
std::size_t count = numbers.size();

if (!numbers.empty()) {
    int first = numbers.front(); // 第一个元素
    int last = numbers.back();   // 最后一个元素
}

numbers.clear();              // 删除所有元素
```

### 3.3 `operator[]` 与 `at()`

```cpp
std::vector<int> numbers{10, 20, 30};

int first = numbers[0];    // 不检查越界
int second = numbers.at(1); // 检查越界
```

| 访问方式                | 越界行为                         |
| ------------------- | ---------------------------- |
| `numbers[index]`    | 不检查；越界访问产生未定义行为              |
| `numbers.at(index)` | 检查；越界时抛出 `std::out_of_range` |

### 3.4 `size()` 与 `capacity()`

```text
size：当前已经存在的元素数量
capacity：当前已分配内存最多可容纳的元素数量
```

当添加元素导致 `size()` 超过当前容量时，`vector` 通常需要：

1. 申请更大的连续内存；
2. 将旧元素移动或复制到新内存；
3. 释放旧内存。

因为扩容不是每次尾插都发生，所以 `push_back()` 的复杂度是**均摊 `O(1)`**。

### 3.5 `reserve()` 与 `resize()`

```cpp
#include <vector>

int main() {
    std::vector<int> numbers;

    // 只预留容量，不创建元素，size 仍为 0
    numbers.reserve(100);

    // 改变实际元素数量，增大时创建新元素
    numbers.resize(100);
}
```

区别：

| 操作 | 是否改变 `size()` | 是否改变可用容量 | 是否创建或销毁元素 |
|---|---:|---:|---:|
| `reserve(n)` | 否 | 可能 | 否 |
| `resize(n)` | 是 | 可能 | 是 |

若能预估元素数量，可以提前 `reserve()`，以减少扩容次数。

### 3.6 中间插入和删除

```cpp
#include <vector>

int main() {
    std::vector<int> numbers{10, 20, 30};

    numbers.insert(numbers.begin() + 1, 15); // 在 20 前插入 15
    numbers.erase(numbers.begin() + 2);      // 删除当前位置的元素
}
```

这类操作需要移动后续元素，通常为 `O(n)`。

### 3.7 删除所有指定值

C++11/14/17 常用 erase-remove 写法：

```cpp
#include <algorithm>
#include <vector>

int main() {
    std::vector<int> numbers{1, 2, 3, 2, 4};

    // remove 将保留的元素移动到前部，erase 再真正缩短容器
    numbers.erase(
        std::remove(numbers.begin(), numbers.end(), 2),
        numbers.end()
    );
}
```

C++20 可直接使用：

```cpp
std::erase(numbers, 2); // 删除所有值为 2 的元素
```

### 3.8 扩容与迭代器失效

扩容后旧内存被释放，原来指向元素的指针、引用和迭代器都可能失效：

```cpp
#include <vector>

int main() {
    std::vector<int> numbers{10, 20};
    int* first = &numbers[0];

    numbers.push_back(30); // 可能触发扩容

    // 若发生扩容，first 已经失效，不能再解引用
}
```

不要在修改 `vector` 结构的同时长期保存其中元素的地址、引用或迭代器。

## 4. `std::list`：双向链表

`list` 通常使用双向链表实现，节点在内存中通常不连续：

```text
[10] ⇄ [20] ⇄ [30]
```

```cpp
#include <iostream>
#include <list>

int main() {
    std::list<int> numbers{10, 20, 30};

    numbers.push_front(5); // 头部添加
    numbers.push_back(40); // 尾部添加
    numbers.pop_front();   // 删除头部
    numbers.pop_back();    // 删除尾部

    for (int number : numbers) {
        std::cout << number << ' ';
    }
}
```

### 4.1 不支持随机访问

`list` 不支持 `operator[]`。访问第 `n` 个元素需要从某个位置逐个移动，通常是 `O(n)`：

```cpp
std::list<int> numbers{10, 20, 30};

auto iterator = numbers.begin();
++iterator; // 移动到第二个元素

int value = *iterator;
```

### 4.2 已知位置时增删为 `O(1)`

```cpp
std::list<int> numbers{10, 20, 30};

auto iterator = numbers.begin();
++iterator; // 指向 20

numbers.insert(iterator, 15); // 在 20 前插入
iterator = numbers.erase(iterator); // 删除 20，接收下一个有效迭代器
```

关键限定是：

> 只有已经持有目标位置的有效迭代器时，插入和删除才通常是 `O(1)`；查找该位置本身可能需要 `O(n)`。

### 4.3 成员算法

```cpp
#include <list>

int main() {
    std::list<int> numbers{3, 1, 2, 2};

    numbers.remove(2); // 删除所有值为 2 的元素
    numbers.sort();    // list 使用自身的排序成员函数
    numbers.unique();  // 删除相邻重复元素
}
```

`std::sort` 要求随机访问迭代器，不能直接用于 `list`；应调用 `list::sort()`。

### 4.4 优缺点与选择

优点：

- 已知位置时插入、删除快；
- 插入其他节点通常不会使已有节点的迭代器失效；
- 适合节点移动和链表拼接类操作。

缺点：

- 不支持随机访问；
- 查找位置较慢；
- 每个节点需要额外保存链接指针；
- 内存不连续，缓存局部性较差。

不能只根据“存在频繁增删”就选择 `list`，还需要判断能否直接得到操作位置，以及是否真的需要稳定迭代器。普通顺序数据仍应优先考虑 `vector`。

## 5. `std::deque`：双端队列

`deque` 是 Double-Ended Queue，支持头尾两端快速增删，也支持 `O(1)` 下标访问。其内存通常不是一整块连续区域。

```cpp
#include <deque>
#include <iostream>

int main() {
    std::deque<int> numbers;

    numbers.push_back(20);
    numbers.push_back(30);
    numbers.push_front(10);

    std::cout << numbers[1] << '\n'; // 支持下标访问

    numbers.pop_front();
    numbers.pop_back();
}
```

### 5.1 与 `vector` 的比较

| 特点 | `vector` | `deque` |
|---|---|---|
| 是否是一整块连续内存 | 是 | 通常不是 |
| 下标访问 | `O(1)` | `O(1)` |
| 尾部增删 | 快 | 快 |
| 头部增删 | `O(n)` | `O(1)` |
| 是否适合需要连续内存的接口 | 是 | 否 |

适合场景包括滑动窗口：

```cpp
std::deque<int> window;

window.push_back(10); // 新元素从尾部进入
window.push_back(20);
window.pop_front();   // 旧元素从头部离开
```

`std::queue` 默认也通常使用 `deque` 作为底层容器。

## 6. `std::map`：有序键值对

`map<Key, Value>` 保存键值对，键唯一并按比较规则保持有序。查找、插入和删除通常是 `O(log n)`。

```cpp
#include <iostream>
#include <map>
#include <string>

int main() {
    std::map<std::string, int> scores;

    scores["小明"] = 90;
    scores["小红"] = 95;

    // C++17 结构化绑定：按键顺序遍历
    for (const auto& [name, score] : scores) {
        std::cout << name << ": " << score << '\n';
    }
}
```

`map` 常由平衡搜索树实现，但标准重点保证的是有序性和对数复杂度，不应把某一种树实现当成所有实现的强制要求。

### 6.1 使用 `find()` 查询

```cpp
std::map<std::string, int> scores{
    {"小明", 90},
    {"小红", 95}
};

auto iterator = scores.find("小明");
if (iterator != scores.end()) {
    std::cout << iterator->first << '\n';  // 键
    std::cout << iterator->second << '\n'; // 值
}
```

找不到时，返回 `end()`。

### 6.2 `operator[]` 会插入缺失键

```cpp
std::map<std::string, int> scores;

// 键不存在时，会插入 {"小明", 0}
int score = scores["小明"];
```

因此，只想查询而不希望改变容器时，应使用：

```cpp
auto iterator = scores.find("小明"); // 不插入
int score = scores.at("小明");       // 不存在时抛出 std::out_of_range
```

### 6.3 插入和更新

```cpp
std::map<std::string, int> scores;

scores.insert({"小明", 90});

auto [iterator, inserted] = scores.emplace("小红", 95);
if (inserted) {
    // 只有键原先不存在时才成功插入
}

// C++17：不存在则插入，存在则覆盖值
scores.insert_or_assign("小明", 100);
```

普通 `insert()` 和 `emplace()` 在键已存在时不会覆盖原值。

### 6.4 有序范围查询

```cpp
std::map<int, std::string> users{
    {10, "A"},
    {20, "B"},
    {30, "C"}
};

// 找到第一个键不小于 15 的元素
const auto iterator = users.lower_bound(15);

if (iterator != users.end()) {
    std::cout << iterator->first << '\n'; // 20
}
```

按键遍历、`lower_bound()` 等范围操作是 `map` 相比哈希容器的重要优势。

## 7. `std::unordered_map`：哈希键值表

`unordered_map` 通常使用哈希表实现，不保证遍历顺序。其查找、插入和删除平均为 `O(1)`，最坏可能退化为 `O(n)`。

```cpp
#include <iostream>
#include <string>
#include <unordered_map>

int main() {
    std::unordered_map<std::string, int> scores;

    scores["小明"] = 90;
    scores["小红"] = 95;

    const auto iterator = scores.find("小明");
    if (iterator != scores.end()) {
        std::cout << iterator->second << '\n';
    }
}
```

### 7.1 哈希表基本思路

```text
key → 哈希函数 → 哈希值 → 桶位置
```

多个键映射到相同位置时会发生哈希冲突。冲突严重时，操作性能可能从平均 `O(1)` 退化。

### 7.2 与 `map` 的比较

| 特点 | `map` | `unordered_map` |
|---|---|---|
| 常见数据结构 | 平衡搜索树 | 哈希表 |
| 遍历是否有序 | 是 | 否 |
| 查找复杂度 | `O(log n)` | 平均 `O(1)`，最坏 `O(n)` |
| 范围查询 | 适合 | 不适合 |
| 自定义键的主要要求 | 可按比较规则排序 | 可计算哈希且可判断相等 |

选择原则：

- 需要按键排序或范围查询：选择 `map`；
- 不关心顺序，只需要平均快速查找：选择 `unordered_map`。

### 7.3 `rehash` 与迭代器失效

元素增多时，哈希表可能增加桶数量并重新安排元素位置，这称为 `rehash`。重新哈希会使原有迭代器失效。

```cpp
std::unordered_map<std::string, int> scores;

// 已知大致元素数量时提前预留，减少重新哈希
scores.reserve(1000);
```

## 8. `std::set`：有序唯一集合

`set` 保存唯一元素，并按比较规则自动排序。查找、插入和删除通常为 `O(log n)`。

```cpp
#include <iostream>
#include <set>

int main() {
    std::set<int> numbers;

    numbers.insert(30);
    numbers.insert(10);
    numbers.insert(20);
    numbers.insert(20); // 重复值不会再次插入

    for (int number : numbers) {
        std::cout << number << ' '; // 10 20 30
    }
}
```

可以将其理解为只有键、没有额外映射值的有序关联容器。

### 8.1 判断元素是否存在

C++11/14/17：

```cpp
std::set<int> numbers{10, 20, 30};

if (numbers.find(20) != numbers.end()) {
    // 元素存在
}

if (numbers.count(20) > 0) {
    // set 的 count 结果只能是 0 或 1
}
```

C++20：

```cpp
if (numbers.contains(20)) {
    // 元素存在
}
```

### 8.2 检查插入结果

```cpp
std::set<int> numbers;

auto [iterator, inserted] = numbers.insert(10);
if (inserted) {
    // 成功插入新元素
} else {
    // 元素原本已经存在
}
```

### 8.3 不能直接修改元素

直接修改 `set` 中的值可能破坏排序关系，因此通过迭代器获得的是不可直接改写的键。

需要“修改”时，应删除旧值并插入新值：

```cpp
numbers.erase(20);
numbers.insert(100);
```

若只要求去重和平均 `O(1)` 查找，而不要求有序，可进一步考虑 `std::unordered_set<T>`。

## 9. `std::priority_queue`：优先队列

优先队列不是按进入先后取元素，而是每次访问当前最高优先级元素。默认情况下，最大元素位于顶部，即大顶堆。

```cpp
#include <iostream>
#include <queue>

int main() {
    std::priority_queue<int> numbers;

    numbers.push(30);
    numbers.push(10);
    numbers.push(20);

    std::cout << numbers.top() << '\n'; // 30
    numbers.pop();                      // 删除顶部，不返回元素
    std::cout << numbers.top() << '\n'; // 20
}
```

常用接口：

```text
push(value)：插入元素
emplace(args...)：原地构造元素
top()：只读访问最高优先级元素
pop()：删除最高优先级元素，不返回它
size()：元素数量
empty()：是否为空
```

需要先取值再删除：

```cpp
int highest = numbers.top();
numbers.pop();
```

### 9.1 小顶堆

```cpp
#include <functional>
#include <queue>
#include <vector>

int main() {
    // greater<int> 使最小元素位于顶部
    std::priority_queue<
        int,
        std::vector<int>,
        std::greater<int>
    > numbers;

    numbers.push(30);
    numbers.push(10);
    numbers.push(20);

    int smallest = numbers.top(); // 10
}
```

三个模板参数分别是：

```text
元素类型
底层容器类型
比较规则
```

复杂度：

| 操作 | 复杂度 |
|---|---:|
| `top()` | `O(1)` |
| `push()` | `O(log n)` |
| `pop()` | `O(log n)` |

适用场景包括 Top K、任务调度、Dijkstra 最短路和合并有序序列。

## 10. 迭代器

迭代器可以理解为访问容器元素的通用指针式接口：

```cpp
#include <iostream>
#include <vector>

int main() {
    std::vector<int> numbers{10, 20, 30};

    for (auto iterator = numbers.begin();
         iterator != numbers.end();
         ++iterator) {
        std::cout << *iterator << ' ';
    }
}
```

基本含义：

```text
begin()：指向第一个元素
end()：指向最后一个元素之后的位置
*iterator：访问当前元素
++iterator：移动到下一个元素
```

`end()` 不指向有效元素，不能被解引用。

## 11. 迭代器失效规则

| 容器 | 插入的典型影响 | 删除的典型影响 |
|---|---|---|
| `vector` | 扩容会使所有指针、引用和迭代器失效 | 删除位置及其后的迭代器可能失效 |
| `list` | 通常不影响已有元素的迭代器 | 仅被删除元素的迭代器失效 |
| `deque` | 规则较复杂，不应跨结构修改长期保存迭代器 | 相关迭代器可能失效 |
| `map` / `set` | 通常不影响已有元素的迭代器 | 仅被删除元素的迭代器失效 |
| `unordered_map` | `rehash` 会使迭代器失效 | 被删除元素的迭代器失效 |

遍历时删除元素，通常应接收 `erase()` 返回的下一个迭代器：

```cpp
#include <vector>

int main() {
    std::vector<int> numbers{1, 2, 3, 4};

    for (auto iterator = numbers.begin();
         iterator != numbers.end();) {
        if (*iterator % 2 == 0) {
            // 删除当前元素，并取得下一个有效位置
            iterator = numbers.erase(iterator);
        } else {
            ++iterator;
        }
    }
}
```

## 12. 容器选择原则

### 12.1 默认先考虑 `vector`

`vector` 具有连续内存、随机访问和良好缓存局部性。除非有明确需求，否则普通顺序数据优先使用：

```cpp
std::vector<Student> students;
```

### 12.2 需要频繁操作两端时使用 `deque`

```cpp
std::deque<int> window;
```

### 12.3 已知操作位置并要求迭代器较稳定时考虑 `list`

使用 `list` 前应确认：

- 已经持有目标位置迭代器；
- 的确存在大量节点插入、删除或拼接；
- 不需要随机访问；
- 迭代器稳定性比缓存局部性更重要。

### 12.4 有序键值对使用 `map`

```cpp
std::map<std::string, int> scores;
```

适合有序遍历和范围查询。

### 12.5 平均快速键查找使用 `unordered_map`

```cpp
std::unordered_map<int, User> users;
```

适合不关心遍历顺序、主要按键查询的场景。

### 12.6 有序去重使用 `set`

```cpp
std::set<int> ids;
```

### 12.7 持续获取最值使用 `priority_queue`

```cpp
std::priority_queue<int> tasks;
```

## 13. 面试高频结论

### 13.1 `vector` 与 `list` 的区别

`vector` 使用连续内存，支持 `O(1)` 随机访问，缓存局部性好，尾插均摊 `O(1)`；中间增删需要移动元素。`list` 通常是双向链表，不支持随机访问；已知目标迭代器时增删为 `O(1)`，但查找位置通常是 `O(n)`，还会产生节点指针和缓存不友好的开销。一般默认优先选择 `vector`。

### 13.2 `map` 与 `unordered_map` 的区别

`map` 按键有序，查找、插入和删除是 `O(log n)`，适合有序遍历和范围查询。`unordered_map` 通常由哈希表实现，元素无序，操作平均 `O(1)`、最坏 `O(n)`，扩容时可能重新哈希。

### 13.3 `vector` 为什么会使迭代器失效？

容量不足时，`vector` 会申请新的连续内存并移动或复制元素，原地址随旧内存释放而失效，因此指向旧地址的指针、引用和迭代器也失效。

### 13.4 `reserve()` 与 `resize()` 的区别

`reserve()` 只预留容量，不改变元素数量；`resize()` 改变实际元素数量，增大时创建元素，减小时销毁多余元素。

### 13.5 `map[key]` 有什么注意事项？

键不存在时，`operator[]` 会插入该键，并默认初始化对应值。只查询而不希望插入时，应使用 `find()` 或 `at()`。

### 13.6 `priority_queue` 默认是大顶堆还是小顶堆？

默认是大顶堆，`top()` 返回最大值。使用 `std::greater<T>` 可构造小顶堆。

## 14. 一句话总结

> 普通顺序数据默认选择 `vector`；两端增删选择 `deque`；已知位置的节点增删可考虑 `list`；有序键值和范围查询选择 `map`；平均快速键查找选择 `unordered_map`；有序去重选择 `set`；持续取得最值选择 `priority_queue`。选择容器时还必须同时考虑内存布局、复杂度和迭代器失效规则。

## 来源

- 本次新增会话中关于 STL 常用容器、迭代器、复杂度、失效规则和容器选择的讲解；
- 其中具体规则采用标准 C++ 通用知识，本项目现有文件未直接提供本节全部内容。
