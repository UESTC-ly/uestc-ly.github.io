# RAII、异常安全与资源生命周期管理

> 本笔记整理自本次会话中对 C++ 资源管理主题的讲解。
>
> 相关技术栈索引：[秋招求职技术栈](../秋招求职技术栈.md)

## 1. 核心概念

这三个概念的关系可以概括为：

```text
RAII：用对象自动管理资源
资源生命周期管理：明确资源何时获取、使用、转移和释放
异常安全：即使发生异常，也不能泄漏资源，并尽量保持对象状态有效
```

### 1.1 什么是资源

资源不仅包括动态内存，还包括：

- 动态分配的内存；
- 文件句柄和文件流；
- 网络连接、数据库连接；
- 互斥锁；
- 操作系统文件描述符；
- 线程句柄；
- 图形界面或其他系统资源。

资源通常具有以下特点：

1. 获取资源需要执行某种操作；
2. 使用完毕后必须释放；
3. 通常只能由明确的所有者释放一次；
4. 在异常、提前 `return` 等情况下也不能忘记释放。

### 1.2 RAII 的含义

RAII 是 **Resource Acquisition Is Initialization** 的缩写，通常逐字母读作“R-A-I-I”，意思是“资源获取即初始化”。

它的核心做法是：

```text
对象构造时获取资源
对象存活期间使用资源
对象析构时释放资源
```

资源的生命周期绑定到管理对象的生命周期。C++ 局部对象离开作用域时会自动析构，因此正常返回、提前 `return` 和异常退出都能触发资源释放。

## 2. 为什么不推荐裸 `new` / `delete`

传统写法需要手动管理资源：

```cpp
void process() {
    int* value = new int(42);

    // 使用动态内存
    doSomething();

    delete value;
    value = nullptr;
}
```

这种写法容易出现以下问题：

### 2.1 忘记释放

```cpp
void process() {
    int* value = new int(42);

    // 忘记 delete，造成内存泄漏
}
```

### 2.2 异常导致释放代码无法执行

```cpp
void process() {
    int* value = new int(42);

    doSomething(); // 如果这里抛出异常

    delete value;  // 可能执行不到
}
```

### 2.3 重复释放

```cpp
int* value = new int(42);

delete value;
delete value; // 错误：重复释放
```

### 2.4 使用释放后的指针

```cpp
int* value = new int(42);
delete value;

// 错误：value 已经成为悬空指针
std::cout << *value;
```

### 2.5 所有权不明确

```cpp
int* p1 = new int(42);
int* p2 = p1;
```

此时 `p1` 和 `p2` 指向同一资源，但无法从类型上看出谁负责释放。两个指针都释放会重复释放，谁都不释放则会泄漏。

因此，资源管理的关键问题是：

> 谁拥有资源，谁负责释放资源；所有权应当尽量通过类型表达。

## 3. 用 RAII 管理资源

### 3.1 自定义 RAII 类

```cpp
#include <iostream>

class Resource {
public:
    Resource() {
        // 构造时获取资源
        std::cout << "获取资源\n";
    }

    ~Resource() noexcept {
        // 析构时释放资源
        std::cout << "释放资源\n";
    }
};

void process() {
    Resource resource;

    std::cout << "使用资源\n";

    // 即使这里提前 return，resource 也会自动析构
}
```

调用 `process()` 时，生命周期大致为：

```text
进入函数
→ 构造 resource，获取资源
→ 使用资源
→ 离开作用域
→ 析构 resource，释放资源
```

如果函数抛出异常，栈展开同样会销毁已经构造完成的局部对象。

### 3.2 生命周期管理的基本步骤

```text
获取资源
    ↓
确定资源的所有者
    ↓
使用资源
    ↓
必要时转移所有权
    ↓
自动或显式释放资源
```

现代 C++ 的目标是：资源获取后尽快交给 RAII 类型管理，而不是让裸指针长期承担所有权。

## 4. `std::unique_ptr`：独占所有权

一个资源同一时间只有一个 `unique_ptr` 拥有：

```cpp
#include <iostream>
#include <memory>

void process() {
    auto value = std::make_unique<int>(42);

    std::cout << *value << '\n';

    // 离开作用域时自动释放 int
}
```

### 4.1 不能复制，可以移动

```cpp
auto p1 = std::make_unique<int>(42);

// auto p2 = p1; // 错误：unique_ptr 不能复制

auto p2 = std::move(p1); // 正确：转移所有权
```

移动后：

```text
p1：不再拥有资源，通常为空
p2：拥有原来的资源
```

### 4.2 返回 `unique_ptr`

```cpp
#include <memory>

std::unique_ptr<int> createValue() {
    auto value = std::make_unique<int>(42);

    // 返回时转移所有权，调用者接管资源
    return value;
}

void useValue() {
    auto result = createValue();

    // result 离开作用域时自动释放资源
}
```

### 4.3 使用建议

当资源存在明确的唯一拥有者时，优先使用 `unique_ptr`。它通常是动态对象所有权管理的默认选择。

## 5. `std::shared_ptr`：共享所有权

多个 `shared_ptr` 可以共同管理一个对象：

```cpp
#include <iostream>
#include <memory>

void example() {
    auto p1 = std::make_shared<int>(42);
    auto p2 = p1;

    // p1 和 p2 共同拥有同一个 int 对象
    std::cout << p1.use_count() << '\n'; // 通常为 2
}
```

它通过控制块中的引用计数管理生命周期：

- 复制一个 `shared_ptr`，强引用计数增加；
- 销毁一个 `shared_ptr`，强引用计数减少；
- 强引用计数归零时，对象被销毁。

```cpp
{
    auto p1 = std::make_shared<int>(42);

    {
        auto p2 = p1;
        // 此时有两个 shared_ptr 持有对象
    } // p2 销毁，但对象仍由 p1 持有

} // p1 销毁，最后一个所有者消失，对象被释放
```

### 5.1 使用场景与代价

只有在多个对象确实需要共享生命周期时才使用 `shared_ptr`。它会带来引用计数、控制块和间接访问等开销，也会让所有权关系更复杂。

一般原则：

```text
默认使用 unique_ptr
确实需要共享所有权时使用 shared_ptr
只观察、不拥有时使用 weak_ptr、引用或非拥有指针
```

## 6. `std::weak_ptr`：观察但不拥有

`weak_ptr` 通常从 `shared_ptr` 创建，但不会增加强引用计数：

```cpp
#include <iostream>
#include <memory>

void observe(const std::weak_ptr<int>& observer) {
    if (auto value = observer.lock()) {
        // lock 成功，临时 shared_ptr 保证对象在本次使用期间存在
        std::cout << *value << '\n';
    } else {
        // 对象已经销毁
        std::cout << "对象已经销毁\n";
    }
}
```

使用 `weak_ptr` 前必须通过 `lock()` 获取一个临时的 `shared_ptr`，不能直接解引用。

适用场景：

- 观察对象但不延长其生命周期；
- 缓存；
- 父子关系中的非拥有引用；
- 打破 `shared_ptr` 循环引用。

## 7. 循环引用

两个对象互相使用 `shared_ptr` 持有，可能导致引用计数永远无法归零：

```cpp
#include <memory>

struct Node {
    std::shared_ptr<Node> next;
    std::shared_ptr<Node> previous;
};
```

如果 A 持有 B，B 又持有 A：

```text
A --shared_ptr--> B
A <--shared_ptr-- B
```

即使外部指针销毁，A 和 B 仍然互相持有，最终造成内存泄漏。

将不拥有的一侧改为 `weak_ptr`：

```cpp
#include <memory>

struct Parent;

struct Child {
    std::weak_ptr<Parent> parent; // 只观察父对象，不拥有父对象
};

struct Parent {
    std::shared_ptr<Child> child; // 父对象拥有子对象
};
```

## 8. RAII 管理文件

C++ 文件流对象会在析构时自动关闭文件：

```cpp
#include <fstream>

void writeFile() {
    std::ofstream file("data.txt"); // 构造时打开文件

    file << "hello\n";               // 使用文件

} // 析构时自动关闭文件
```

与手动管理 `FILE*` 相比，`std::ofstream` 能避免异常或提前返回时忘记 `fclose()`。

## 9. RAII 管理互斥锁

手动加锁和解锁存在异常安全问题：

```cpp
std::mutex mutex;

void update() {
    mutex.lock();

    doSomething(); // 如果抛出异常，unlock 可能执行不到

    mutex.unlock();
}
```

使用 `std::lock_guard`：

```cpp
#include <mutex>

std::mutex mutex;

void update() {
    std::lock_guard<std::mutex> lock(mutex); // 构造时加锁

    // 操作共享数据

} // lock 析构时自动解锁
```

它把互斥锁的生命周期绑定到 `lock` 对象，因此异常退出也能自动解锁。

## 10. 异常安全

异常安全要求：

1. 发生异常时不泄漏资源；
2. 对象仍处于有效状态；
3. 重要操作失败时，尽量让对象状态保持不变。

### 10.1 RAII 与异常安全

```cpp
void process() {
    auto memory = std::make_unique<int>(10);
    std::ofstream file("data.txt");
    std::lock_guard<std::mutex> lock(mutex);

    doSomething(); // 即使抛出异常，也会按逆序自动清理
}
```

退出时的销毁顺序：

```text
先销毁 lock：自动解锁
再销毁 file：自动关闭文件
最后销毁 memory：自动释放动态内存
```

局部对象通常按照构造顺序的反方向析构，即“后构造、先析构”。

### 10.2 不抛出保证

函数保证不会抛出异常，通常使用 `noexcept`：

```cpp
void releaseResource() noexcept {
    // 释放资源的操作不应抛出异常
}
```

析构函数通常也应尽量不抛异常：

```cpp
class Resource {
public:
    ~Resource() noexcept {
        // 释放资源
    }
};
```

析构期间再次抛出异常可能导致程序终止。

### 10.3 基本保证

操作失败并抛出异常时：

- 不发生资源泄漏；
- 对象仍然有效；
- 对象可以继续使用；
- 但对象的值可能已经发生改变。

### 10.4 强保证

操作失败时对象状态保持不变，就像操作从未发生过。常见实现思路是先修改临时对象，成功后再替换正式数据：

```cpp
#include <string>

class Config {
private:
    std::string value_;

public:
    void setValue(const std::string& newValue) {
        std::string temporary(newValue); // 先准备临时数据

        // 临时对象构造成功后再更新正式数据
        value_.swap(temporary);
    }
};
```

如果构造 `temporary` 失败，原来的 `value_` 不会改变。

## 11. 构造函数抛异常时的清理

```cpp
#include <memory>
#include <fstream>
#include <stdexcept>

class Manager {
private:
    std::unique_ptr<int> memory_;
    std::ofstream file_;

public:
    Manager()
        : memory_(std::make_unique<int>(42)),
          file_("data.txt") {
        // 如果这里抛出异常，已构造完成的成员会自动析构
        throw std::runtime_error("初始化失败");
    }
};
```

如果构造函数抛异常：

- `Manager` 对象本身没有构造完成；
- `Manager` 的析构函数不会调用；
- 但已经成功构造的成员会自动析构；
- `memory_` 会自动释放；
- `file_` 会自动关闭。

因此，资源应尽量作为 RAII 成员保存，而不是在构造函数中使用裸句柄并手动清理。

## 12. 资源所有权表达

### 12.1 独占拥有

```cpp
std::unique_ptr<Resource> resource;
```

表示当前对象负责资源生命周期，所有权不能复制。

### 12.2 共享拥有

```cpp
std::shared_ptr<Resource> resource;
```

表示多个对象共同延长资源生命周期。

### 12.3 非拥有访问

```cpp
void useResource(const Resource& resource) {
    // 只使用资源，不负责释放
}
```

也可以用非拥有裸指针表示“可能为空”：

```cpp
void printResource(const Resource* resource) {
    if (resource != nullptr) {
        // 只使用资源，不执行 delete
    }
}
```

关键是要保证资源在使用期间仍然存在。

## 13. 虚析构函数与 RAII

如果通过基类指针删除派生类对象，基类析构函数应当是虚函数：

```cpp
#include <memory>

class Base {
public:
    virtual ~Base() = default;
};

class Derived : public Base {
private:
    std::unique_ptr<int> data_;

public:
    Derived()
        : data_(std::make_unique<int>(42)) {}
};

void useObject() {
    std::unique_ptr<Base> object = std::make_unique<Derived>();

    // 销毁时正确调用 Derived 和 Base 的析构函数
}
```

## 14. 成员初始化顺序

类成员按照声明顺序初始化，而不是按照初始化列表中的书写顺序：

```cpp
class Example {
private:
    int first_;
    int second_;

public:
    Example()
        : second_(2), first_(1) {}
};
```

实际顺序仍然是：

```text
先初始化 first_
再初始化 second_
```

建议让初始化列表与成员声明顺序保持一致：

```cpp
Example()
    : first_(1), second_(2) {}
```

局部对象则按照构造顺序的反方向销毁。

## 15. 实践原则

1. 能使用栈对象，就不要手动 `new`；
2. 动态对象默认优先使用 `std::unique_ptr`；
3. 只有确实需要共享生命周期时才使用 `std::shared_ptr`；
4. 非拥有关系使用引用、非拥有指针或 `std::weak_ptr`；
5. 资源获取后应尽快交给 RAII 对象管理；
6. 释放资源的析构函数通常应保证不抛异常；
7. 明确谁拥有资源、谁负责释放、所有权是否转移；
8. 通过基类指针管理派生类对象时，基类析构函数应为 `virtual`；
9. 避免让异常穿过资源释放逻辑；
10. 多线程共享的静态资源需要额外考虑同步。

## 16. 面试速答

### 什么是 RAII？

RAII 是 C++ 的资源管理思想，将资源获取绑定到对象初始化，将资源释放绑定到对象析构。对象离开作用域时自动释放资源，因此能处理提前 `return` 和异常退出。

### `unique_ptr`、`shared_ptr`、`weak_ptr` 的区别？

- `unique_ptr`：独占所有权，不能复制，只能移动；
- `shared_ptr`：共享所有权，通过引用计数管理生命周期；
- `weak_ptr`：不拥有对象，通常用于观察对象和打破循环引用。

### 为什么使用 RAII 可以提高异常安全？

因为资源由局部对象管理。异常导致作用域退出时，局部对象会自动析构，析构函数负责释放资源，从而避免内存泄漏、文件未关闭和锁未释放。

### 什么是强异常安全保证？

操作失败时对象状态保持不变，就像操作从未发生过。常见做法是先在临时对象中完成修改，成功后再一次性替换原状态。

## 17. 一句话总结

> RAII 让资源的释放跟随对象析构；现代 C++ 应通过智能指针、文件流和锁管理器表达资源所有权和生命周期，默认优先独占所有权，确实需要时再共享，并确保异常发生时资源仍能被自动清理。

## 来源

- 本次会话中关于 RAII、异常安全、智能指针、文件和互斥锁资源管理的讲解；
- 项目技术栈索引：[秋招求职技术栈.md](../秋招求职技术栈.md)。
