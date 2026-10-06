# C++ 智能指针与所有权管理

> 智能指针是 RAII 在动态内存管理中的典型应用。它解决的核心问题不是“如何像指针一样访问对象”，而是：**谁拥有资源、谁负责释放资源，以及资源应在何时释放。**

相关笔记：

- [RAII、异常安全与资源生命周期](RAII、异常安全与资源生命周期.md)
- [C++ 左值、右值、移动语义与完美转发](C++左值、右值、移动语义与完美转发.md)
- [C++ 深浅拷贝与拷贝控制](C++深浅拷贝与拷贝控制.md)

## 1. 为什么需要智能指针

直接使用裸指针管理动态内存时，程序员必须手动释放资源：

```cpp
#include <iostream>

int main() {
    int* number = new int(10);
    std::cout << *number << '\n';

    // 必须手动释放动态对象
    delete number;
    number = nullptr;
}
```

这种写法容易引发：

- 忘记 `delete`，造成内存泄漏；
- 异常或提前 `return` 使释放代码无法执行；
- 重复释放，导致未定义行为；
- 释放后继续访问，形成悬空指针；
- 所有权不明确，不知道谁应负责释放资源。

智能指针将资源包装进 RAII 对象：创建时获得资源，析构时自动释放资源。

```cpp
#include <memory>

void process() {
    // 创建动态整数，并将独占所有权交给智能指针
    auto number = std::make_unique<int>(10);

    // 离开作用域时自动释放，不需要手动 delete
}
```

三种智能指针都定义在：

```cpp
#include <memory>
```

## 2. 三种智能指针的所有权语义

| 类型 | 所有权含义 | 能否复制 | 主要用途 |
|---|---|---:|---|
| `std::unique_ptr<T>` | 独占所有权 | 否，只能移动 | 一个所有者独占资源 |
| `std::shared_ptr<T>` | 共享所有权 | 是 | 多个所有者共同决定资源生命周期 |
| `std::weak_ptr<T>` | 非拥有观察 | 是 | 观察共享对象、打破循环引用 |

记忆方式：

```text
unique_ptr：独占
shared_ptr：共享
weak_ptr：观察
```

选择原则：

1. 能直接使用普通对象，就不要进行动态分配；
2. 需要动态分配时，默认优先使用 `unique_ptr`；
3. 确实需要共享生命周期时，使用 `shared_ptr`；
4. 只需观察共享对象时，使用 `weak_ptr`。

---

## 3. `unique_ptr`：独占所有权

### 3.1 创建与访问

`std::unique_ptr` 表示同一时刻只有一个所有者。C++14 起应优先使用 `std::make_unique` 创建：

```cpp
#include <iostream>
#include <memory>

class Student {
public:
    void introduce() const {
        std::cout << "Hello\n";
    }
};

int main() {
    // 创建动态整数
    auto number = std::make_unique<int>(10);
    std::cout << *number << '\n';

    // 创建动态类对象
    auto student = std::make_unique<Student>();
    student->introduce();
}
```

不推荐直接写：

```cpp
// 虽然可以工作，但通常应避免显式 new
std::unique_ptr<int> number(new int(10));
```

推荐：

```cpp
// 创建对象和建立所有权在同一表达式内完成
const auto number = std::make_unique<int>(10);
```

### 3.2 不能复制，只能移动

独占所有权不能复制：

```cpp
auto first = std::make_unique<int>(10);

// 编译错误：不能复制独占所有权
// auto second = first;
```

可以通过移动转移所有权：

```cpp
#include <iostream>
#include <memory>
#include <utility>

int main() {
    auto first = std::make_unique<int>(10);

    // 将所有权从 first 转移给 second
    auto second = std::move(first);

    if (!first) {
        std::cout << "first 已不再拥有对象\n";
    }

    std::cout << *second << '\n';
}
```

移动前后关系：

```text
移动前：first  ───> int(10)
移动后：first  ───> nullptr
        second ───> int(10)
```

`std::move` 本身不搬运资源，它只是把表达式转换成允许触发移动操作的形式；真正的所有权转移由 `unique_ptr` 的移动构造或移动赋值完成。

### 3.3 空指针检查

智能指针可能为空，解引用前应在需要时检查：

```cpp
auto number = std::make_unique<int>(10);

if (number) {
    // number 有效时才能安全解引用
    std::cout << *number << '\n';
}
```

### 3.4 `get()`、`reset()` 与 `release()`

#### `get()`：借用裸指针

```cpp
#include <iostream>
#include <memory>

void printNumber(const int* number) {
    // 只借用对象，不接管所有权
    if (number != nullptr) {
        std::cout << *number << '\n';
    }
}

int main() {
    auto number = std::make_unique<int>(10);
    printNumber(number.get());
}
```

`get()` 不转移所有权，返回的裸指针不能手动 `delete`：

```cpp
auto number = std::make_unique<int>(10);
int* raw = number.get();

// 错误：对象仍由 number 管理，手动释放会造成重复释放
// delete raw;
```

#### `reset()`：释放或替换当前资源

```cpp
#include <memory>

int main() {
    auto number = std::make_unique<int>(10);

    // 释放当前对象并将 number 置空
    number.reset();

    // 推荐通过新的 unique_ptr 替换资源
    number = std::make_unique<int>(20);
}
```

#### `release()`：放弃所有权但不释放资源

```cpp
#include <memory>

int main() {
    auto number = std::make_unique<int>(10);

    // number 变空；raw 接收裸指针及其释放责任
    int* raw = number.release();

    // 现在必须由接管方负责释放
    delete raw;
    raw = nullptr;
}
```

`release()` 很容易重新引入手动资源管理问题，普通业务代码中应谨慎使用。

| 操作 | 是否释放当前资源 | 原智能指针是否变空 | 含义 |
|---|---:|---:|---|
| `get()` | 否 | 否 | 临时借用裸指针 |
| `reset()` | 是 | 是 | 放弃并释放当前资源 |
| `release()` | 否 | 是 | 交出资源及释放责任 |

### 3.5 动态数组

`unique_ptr` 可以管理动态数组：

```cpp
#include <iostream>
#include <memory>

int main() {
    // 创建包含 5 个整数的动态数组
    auto numbers = std::make_unique<int[]>(5);

    numbers[0] = 10;
    numbers[1] = 20;
    std::cout << numbers[0] << '\n';
}
```

不过，一般优先使用 `std::vector<T>`，因为它还提供长度信息、迭代器、扩容能力和更丰富的容器接口。

---

## 4. `shared_ptr`：共享所有权

### 4.1 创建、复制与引用计数

`std::shared_ptr` 允许多个指针共同拥有同一个对象。通常优先使用 `std::make_shared`：

```cpp
#include <iostream>
#include <memory>

int main() {
    auto first = std::make_shared<int>(10);

    // 复制 shared_ptr，共享同一个动态对象
    auto second = first;

    *second = 20;
    std::cout << *first << '\n';  // 输出 20
}
```

复制 `shared_ptr` 不会深拷贝目标对象：

```text
first  ───┐
          ├──> int(20)
second ───┘
```

`shared_ptr` 通常通过控制块中的强引用计数记录所有者数量。当最后一个共享所有者消失时，目标对象才会被释放。

```cpp
#include <iostream>
#include <memory>

int main() {
    auto first = std::make_shared<int>(10);
    std::cout << first.use_count() << '\n';  // 1

    {
        auto second = first;
        std::cout << first.use_count() << '\n';  // 2
    }

    std::cout << first.use_count() << '\n';  // 1
}
```

`use_count()` 适合学习和调试，不宜作为核心业务逻辑的判断依据。

### 4.2 `reset()` 只放弃当前这一份共享所有权

```cpp
#include <memory>

int main() {
    auto first = std::make_shared<int>(10);
    auto second = first;

    // first 变空，但 second 仍拥有对象，因此对象不会立即销毁
    first.reset();
}
```

只有最后一个共享所有者也被销毁或重置，对象才会释放。

### 4.3 适用场景与成本

适合 `shared_ptr` 的情况：

- 多个模块确实需要共同拥有同一资源；
- 资源生命周期由最后一个使用者决定；
- 对象需要跨模块或异步任务共享，且没有天然唯一所有者。

它的代价包括：

- 需要维护引用计数和控制块；
- 所有权关系不如 `unique_ptr` 清晰；
- 释放时机可能更难判断；
- 不当设计可能产生循环引用。

因此，`shared_ptr` 不是“更高级的 `unique_ptr`”，也不应仅为了传参方便而到处使用。

### 4.4 禁止从同一个裸指针建立多个独立的 `shared_ptr`

错误写法：

```cpp
#include <memory>

int main() {
    int* raw = new int(10);

    // 错误：两个 shared_ptr 建立了彼此独立的控制关系
    std::shared_ptr<int> first(raw);
    std::shared_ptr<int> second(raw);
}
```

两个控制块都认为自己应释放同一个对象，最终可能导致重复释放。

正确写法：

```cpp
// 先建立一份共享所有权，再通过复制进行共享
const auto first = std::make_shared<int>(10);
const auto second = first;
```

同样不能手动释放 `shared_ptr::get()` 返回的裸指针：

```cpp
auto number = std::make_shared<int>(10);
int* raw = number.get();

// 错误：资源仍由 shared_ptr 管理
// delete raw;
```

---

## 5. `weak_ptr`：非拥有观察

### 5.1 基本语义

`std::weak_ptr` 配合 `std::shared_ptr` 使用。它可以观察共享对象，但不增加强引用计数，也不延长对象生命周期。

```cpp
#include <iostream>
#include <memory>

int main() {
    auto shared = std::make_shared<int>(10);
    std::weak_ptr<int> weak = shared;

    // weak 不增加强引用计数，通常仍输出 1
    std::cout << shared.use_count() << '\n';
}
```

关系为：

```text
shared ──拥有──> int(10)
weak   ──观察──> int(10)
```

### 5.2 通过 `lock()` 安全访问

`weak_ptr` 不能直接解引用，因为它观察的对象可能已经销毁。访问前必须调用 `lock()`，尝试取得临时 `shared_ptr`：

```cpp
#include <iostream>
#include <memory>

int main() {
    auto shared = std::make_shared<int>(10);
    std::weak_ptr<int> weak = shared;

    if (auto locked = weak.lock()) {
        // locked 存活期间，对象不会被销毁
        std::cout << *locked << '\n';
    } else {
        std::cout << "对象已经不存在\n";
    }
}
```

`lock()` 的结果：

- 对象存在：返回有效的 `shared_ptr`；
- 对象已销毁：返回空的 `shared_ptr`。

### 5.3 `expired()`

`expired()` 可以判断被观察对象是否已经销毁：

```cpp
#include <memory>

int main() {
    auto shared = std::make_shared<int>(10);
    std::weak_ptr<int> weak = shared;

    shared.reset();

    if (weak.expired()) {
        // 最后一个 shared_ptr 已消失
    }
}
```

真正访问对象时仍应优先使用 `lock()`，因为它既完成检查，也能在返回的临时 `shared_ptr` 存活期间稳定对象生命周期。

---

## 6. 使用 `weak_ptr` 打破循环引用

如果两个对象内部互相持有 `shared_ptr`：

```text
A ──shared_ptr──> B
B ──shared_ptr──> A
```

即使外部所有者都消失，A 和 B 仍互相保持强引用，引用计数无法降为零，造成资源泄漏。

应让不表示所有权的一方使用 `weak_ptr`：

```cpp
#include <iostream>
#include <memory>
#include <string>

class Person {
public:
    std::string name;

    // 只观察伙伴，不决定伙伴的生命周期
    std::weak_ptr<Person> partner;
};

int main() {
    auto first = std::make_shared<Person>();
    auto second = std::make_shared<Person>();

    first->name = "小明";
    second->name = "小红";

    // 双方互相观察，不形成强引用环
    first->partner = second;
    second->partner = first;

    if (auto partner = first->partner.lock()) {
        std::cout << first->name << " 的伙伴是 "
                  << partner->name << '\n';
    }
}
```

关键不是机械地规定“某一侧必须弱引用”，而是先分析真实关系：

- 拥有关系使用 `unique_ptr` 或 `shared_ptr`；
- 非拥有、观察、反向关联使用引用、裸指针或 `weak_ptr`；
- 只有由 `shared_ptr` 管理且生命周期可能失效的对象，才使用 `weak_ptr` 观察。

---

## 7. 用函数参数表达所有权

函数接口应明确说明是否接管或共享所有权。

### 7.1 只使用对象，不接管所有权

优先传对象的引用或指针：

```cpp
#include <iostream>

void printNumber(const int& number) {
    // 只读取对象，不管理其生命周期
    std::cout << number << '\n';
}
```

调用：

```cpp
auto number = std::make_unique<int>(10);
printNumber(*number);
```

如果参数允许为空，可以使用非拥有裸指针，并在接口约定中说明不接管所有权。

### 7.2 接管独占所有权

按值接收 `unique_ptr`：

```cpp
#include <memory>

void saveObject(std::unique_ptr<int> object) {
    // 函数接管 object 的独占所有权
}

int main() {
    auto number = std::make_unique<int>(10);
    saveObject(std::move(number));

    // number 已不再拥有对象
}
```

### 7.3 取得一份共享所有权

按值接收 `shared_ptr`：

```cpp
#include <memory>

void storeObject(std::shared_ptr<int> object) {
    // 函数获得一份共享所有权
}
```

如果函数只在调用期间临时使用目标对象，不需要延长其生命周期，就不必为了方便而按值传递 `shared_ptr`。

---

## 8. 智能指针与线程安全

`shared_ptr` 的线程安全需要分层理解：

- 不同 `shared_ptr` 实例共享同一控制块时，引用计数等控制块操作可以安全协作；
- 同一个 `shared_ptr` 变量若被多个线程同时修改，仍需要同步；
- `shared_ptr` 指向的业务对象不会自动变成线程安全对象；
- 多线程同时读写目标对象时，仍需互斥锁、原子操作或其他同步机制。

因此，“使用了 `shared_ptr`”只解决生命周期共享问题，不等于解决目标对象的数据竞争问题。

---

## 9. 常见错误清单

1. **复制 `unique_ptr`**：独占所有权不能复制，应通过 `std::move` 转移。
2. **误解 `std::move`**：它只是值类别转换，不会自行搬运资源。
3. **手动释放 `get()` 的结果**：`get()` 只用于借用，不转移所有权。
4. **滥用 `release()`**：它不释放资源，而是把释放责任交还给程序员。
5. **从同一个裸指针建立多个独立 `shared_ptr`**：会形成多个控制块并可能重复释放。
6. **所有地方都使用 `shared_ptr`**：共享所有权必须有真实设计依据。
7. **两个对象互相强引用**：可能形成无法自动释放的循环引用。
8. **直接解引用 `weak_ptr`**：必须先调用 `lock()`。
9. **认为智能指针解决所有指针错误**：它不能自动防止越界、空指针解引用、悬空的内部视图或数据竞争。

---

## 10. 面试回答要点

### `unique_ptr` 与 `shared_ptr` 的区别

- `unique_ptr` 表示独占所有权，不能复制，只能移动，开销较小，是动态资源的默认选择；
- `shared_ptr` 表示共享所有权，可以复制，通过控制块和引用计数管理生命周期；
- 最后一个 `shared_ptr` 所有者消失时，目标对象才会销毁。

### `weak_ptr` 的作用

- 观察由 `shared_ptr` 管理的对象；
- 不增加强引用计数，不延长对象生命周期；
- 通过 `lock()` 获取临时 `shared_ptr` 后再访问；
- 常用于打破循环引用以及表达缓存、观察者等非拥有关系。

### 为什么推荐 `make_unique` 和 `make_shared`

- 减少显式 `new`；
- 让对象创建与所有权建立在一个表达式中完成；
- 代码更简洁，降低资源管理错误的概率；
- `make_shared` 通常还可以减少对象与控制信息的分配次数。

### 是否应完全禁止裸指针

不是。裸指针仍可表达“允许为空的非拥有访问”，引用可表达“不能为空的非拥有访问”。应避免的是：

- 用裸指针承担不清晰的所有权；
- 用裸指针手动管理本可由 RAII 类型管理的资源。

---

## 11. 总结

```text
能使用普通对象：直接使用普通对象
需要动态分配且只有一个所有者：unique_ptr
需要转移独占所有权：移动 unique_ptr
确实需要共同决定生命周期：shared_ptr
只观察 shared_ptr 管理的对象：weak_ptr
```

一句话概括：

> `unique_ptr` 负责独占，`shared_ptr` 负责共享，`weak_ptr` 负责观察；智能指针的核心是表达所有权，而不只是替代裸指针语法。

---

## 来源

- 本次新增会话中关于 `unique_ptr`、`shared_ptr`、`weak_ptr`、循环引用、函数传参与线程安全的讲解；未使用外部网页或文档页码。
