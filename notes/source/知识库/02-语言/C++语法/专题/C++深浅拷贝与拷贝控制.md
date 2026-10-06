# C++ 深浅拷贝与拷贝控制

> 本文整理浅拷贝、深拷贝、析构、拷贝构造、拷贝赋值、移动构造、移动赋值，以及三法则、五法则和零法则。核心问题是：对象复制、移动和销毁时，资源所有权应该如何处理。

## 1. 首先判断资源所有权

看到类中的指针时，先问：

1. 指针是否拥有资源？
2. 谁负责释放资源？
3. 复制对象后，资源应该独立、共享，还是禁止复制？
4. 能否使用 `std::vector`、`std::string` 或智能指针代替裸资源？

```text
拥有型指针：对象负责释放其指向的资源
非拥有指针：对象只观察或借用资源，不负责释放
```

深拷贝和浅拷贝是否合理，不能脱离所有权语义判断。

---

## 2. 浅拷贝

浅拷贝只逐成员复制值。对于裸指针，它通常只复制地址，不复制指针指向的资源。

```cpp
class Buffer {
public:
    int* data_{nullptr}; // 假设它拥有一块动态内存
};
```

默认复制后可概念化为：

```text
first.data_  ─┐
              ├──> 同一块动态内存
second.data_ ─┘
```

如果类的析构函数释放这块内存：

```cpp
class Buffer {
public:
    int* data_{nullptr};

    ~Buffer() {
        delete data_; // 两个浅拷贝对象可能重复释放同一地址
    }
};
```

就可能出现：

- 两个对象互相影响；
- 悬空指针；
- 重复释放；
- 未定义行为。

但浅拷贝并非总是错误。若指针明确是非拥有观察者，复制地址可能正是期望语义：

```cpp
class IntView {
private:
    const int* value_{nullptr}; // 只观察，不负责 delete

public:
    explicit IntView(const int* value)
        : value_(value) {
    }
};
```

---

## 3. 深拷贝

深拷贝会为新对象申请独立资源，并复制原资源的内容。

```text
first.data_  ───> 资源 A
second.data_ ───> 资源 B

资源 A 与资源 B 内容相同，但生命周期彼此独立
```

简化示例：

```cpp
class Integer {
private:
    int* value_{nullptr};

public:
    explicit Integer(int value)
        : value_(new int(value)) {
    }

    ~Integer() {
        delete value_; // 当前对象只释放自己的资源
    }

    Integer(const Integer& other)
        : value_(new int(*other.value_)) {
        // 为新对象重新申请内存并复制数值
    }
};
```

浅拷贝与深拷贝对比：

| 对比项 | 浅拷贝 | 深拷贝 |
|---|---|---|
| 裸指针成员 | 复制地址 | 新建资源并复制内容 |
| 资源是否独立 | 通常不独立 | 独立 |
| 复制成本 | 较低 | 较高 |
| 拥有型裸指针是否安全 | 通常不安全 | 可安全设计 |
| 典型语义 | 观察或共享 | 值语义、独立副本 |

---

## 4. 拷贝控制的五个特殊成员函数

```cpp
class ResourceOwner {
public:
    ~ResourceOwner(); // 1. 析构函数

    ResourceOwner(const ResourceOwner& other); // 2. 拷贝构造
    ResourceOwner& operator=(const ResourceOwner& other); // 3. 拷贝赋值

    ResourceOwner(ResourceOwner&& other) noexcept; // 4. 移动构造
    ResourceOwner& operator=(ResourceOwner&& other) noexcept; // 5. 移动赋值
};
```

| 函数 | 作用 |
|---|---|
| 析构函数 | 释放当前对象拥有的资源 |
| 拷贝构造 | 用左值源对象创建新对象，复制资源 |
| 拷贝赋值 | 已有对象接收左值源对象的资源副本 |
| 移动构造 | 用右值源对象创建新对象，接管资源 |
| 移动赋值 | 已有对象释放旧资源，再接管右值源对象资源 |

调用判断：

| 代码 | 调用操作 |
|---|---|
| `Buffer b = a;` | 拷贝构造 |
| `b = a;` | 拷贝赋值 |
| `Buffer b = std::move(a);` | 移动构造 |
| `b = std::move(a);` | 移动赋值 |

先看左侧对象是否正在创建，再看右侧是左值还是可移动的右值。

---

## 5. 析构函数

```cpp
class Buffer {
private:
    int* data_{nullptr};

public:
    ~Buffer() {
        delete[] data_; // new[] 必须与 delete[] 配对
    }
};
```

析构函数：

- 名称为 `~类名`；
- 没有返回类型；
- 不接收参数；
- 一个类只有一个析构函数；
- 对象离开生命周期时自动调用；
- 资源释放逻辑通常应保证不抛异常。

---

## 6. 拷贝构造函数

拷贝构造用于根据已有对象创建新对象：

```cpp
class Buffer {
public:
    Buffer(const Buffer& other) {
        // 根据 other 初始化一个全新的对象
    }
};
```

两种常见调用形式：

```cpp
Buffer second = first; // 拷贝初始化，调用拷贝构造
Buffer third(first);   // 直接初始化，调用拷贝构造
```

参数使用 `const Buffer&` 可以避免再次复制源对象，同时允许复制 `const` 对象。

---

## 7. 拷贝赋值运算符

拷贝赋值用于把源对象内容复制给一个已经存在的目标对象：

```cpp
class Buffer {
public:
    Buffer& operator=(const Buffer& other) {
        // 将 other 的内容复制给当前对象
        return *this; // 支持 a = b = c
    }
};
```

### 7.1 自赋值

```cpp
object = object;
```

如果实现会先释放目标资源，就要避免在自赋值时把源资源一起释放：

```cpp
if (this == &other) {
    return *this; // 当前对象和源对象相同，无需操作
}
```

### 7.2 异常安全顺序

不安全顺序：

```text
先释放旧资源
再申请新资源
```

如果申请失败，原对象已经失去旧数据。更安全的顺序是：

```text
先申请并复制新资源
新资源准备成功后再释放旧资源
最后更新成员
```

---

## 8. 移动构造与移动赋值

移动的目标不是复制资源内容，而是转移所有权。

### 8.1 移动构造

```cpp
Buffer(Buffer&& other) noexcept
    : size_(other.size_), data_(other.data_) {
    // 源对象放弃资源，避免两个对象重复释放
    other.size_ = 0;
    other.data_ = nullptr;
}
```

### 8.2 移动赋值

目标对象已经存在，所以必须先处理自己的旧资源：

```cpp
Buffer& operator=(Buffer&& other) noexcept {
    if (this == &other) {
        return *this; // 防止自移动破坏对象
    }

    delete[] data_; // 先释放目标对象原来的资源

    size_ = other.size_;
    data_ = other.data_; // 接管源对象资源

    other.size_ = 0;
    other.data_ = nullptr; // 源对象保持可析构状态

    return *this;
}
```

移动后源对象应该保持有效、可析构、可重新赋值，但通常不要依赖它仍有原来的值。

移动操作常加 `noexcept`，这样标准容器在需要重新分配时更愿意使用移动操作，并能维持所需的异常安全策略。

---

## 9. 完整的教学版 `Buffer`

下面故意使用裸指针展示五个特殊成员函数。实际业务代码应优先使用 `std::vector` 或智能指针。

```cpp
#include <algorithm>
#include <cstddef>
#include <utility>

class Buffer {
private:
    std::size_t size_{0};
    int* data_{nullptr};

public:
    explicit Buffer(std::size_t size)
        : size_(size),
          data_(size > 0 ? new int[size]{} : nullptr) {
        // 创建指定大小的动态数组，并把元素初始化为 0
    }

    ~Buffer() {
        // 释放当前对象拥有的动态数组
        delete[] data_;
    }

    Buffer(const Buffer& other)
        : size_(other.size_),
          data_(other.size_ > 0 ? new int[other.size_]{} : nullptr) {
        // 为新对象申请独立数组并复制内容
        if (size_ > 0) {
            std::copy(other.data_, other.data_ + size_, data_);
        }
    }

    Buffer& operator=(const Buffer& other) {
        if (this == &other) {
            return *this; // 处理自赋值
        }

        // 先创建新资源；如果 new 抛异常，当前对象仍保持原状
        int* newData = nullptr;
        if (other.size_ > 0) {
            newData = new int[other.size_]{};
            std::copy(
                other.data_,
                other.data_ + other.size_,
                newData
            );
        }

        // 新资源准备成功后再替换旧资源
        delete[] data_;
        data_ = newData;
        size_ = other.size_;

        return *this;
    }

    Buffer(Buffer&& other) noexcept
        : size_(other.size_), data_(other.data_) {
        // 接管资源后清空源对象
        other.size_ = 0;
        other.data_ = nullptr;
    }

    Buffer& operator=(Buffer&& other) noexcept {
        if (this == &other) {
            return *this; // 处理自移动
        }

        // 目标对象先释放自己的旧资源
        delete[] data_;

        // 再接管源对象的资源
        size_ = other.size_;
        data_ = other.data_;

        // 源对象放弃所有权
        other.size_ = 0;
        other.data_ = nullptr;

        return *this;
    }

    std::size_t size() const {
        return size_; // 返回元素数量
    }

    int& operator[](std::size_t index) {
        return data_[index]; // 普通对象获得可修改引用
    }

    const int& operator[](std::size_t index) const {
        return data_[index]; // const 对象获得只读引用
    }
};
```

使用：

```cpp
#include <iostream>
#include <utility>

int main() {
    Buffer first(3);
    first[0] = 10;

    Buffer second = first; // 深拷贝构造
    second[0] = 100;

    std::cout << first[0] << '\n';  // 10，资源彼此独立
    std::cout << second[0] << '\n'; // 100

    Buffer third(1);
    third = first; // 深拷贝赋值

    Buffer fourth = std::move(first); // 移动构造

    Buffer fifth(2);
    fifth = std::move(second); // 移动赋值
}
```

---

## 10. 三法则、五法则与零法则

### 10.1 三法则

如果类需要自定义下面三者之一，通常也要检查另外两个：

```text
析构函数
拷贝构造函数
拷贝赋值运算符
```

原因是手写析构函数通常意味着类直接拥有资源，而默认拷贝可能只做不安全的浅拷贝。

### 10.2 五法则

C++11 加入移动语义后，还要考虑：

```text
移动构造函数
移动赋值运算符
```

五法则不是要求永远手写五个函数，而是要求明确决定每一种操作是否允许、是默认行为还是自定义行为。

### 10.3 零法则

现代 C++ 最推荐零法则：使用成熟的 RAII 类型保存资源，让业务类不需要手写五个特殊成员函数。

```cpp
#include <cstddef>
#include <vector>

class Buffer {
private:
    std::vector<int> data_; // vector 自动处理释放、深拷贝和移动

public:
    explicit Buffer(std::size_t size)
        : data_(size) {
    }

    std::size_t size() const {
        return data_.size();
    }

    int& operator[](std::size_t index) {
        return data_[index];
    }

    const int& operator[](std::size_t index) const {
        return data_[index];
    }
};
```

实际优先级：

```text
优先零法则
确实需要直接管理特殊资源时，再完整考虑五法则
```

---

## 11. `= default` 与 `= delete`

### 11.1 请求默认实现

```cpp
class Student {
public:
    Student() = default;
    Student(const Student&) = default;
    Student& operator=(const Student&) = default;
    Student(Student&&) noexcept = default;
    Student& operator=(Student&&) noexcept = default;
    ~Student() = default;
};
```

`= default` 表示明确请求编译器生成默认实现。只有当所有成员对应操作都可用时，默认操作才可用。

### 11.2 禁止拷贝

某些资源不能合理复制，可以禁止拷贝、只允许移动：

```cpp
class FileHandle {
public:
    FileHandle() = default;

    FileHandle(const FileHandle&) = delete; // 禁止复制独占句柄
    FileHandle& operator=(const FileHandle&) = delete;

    FileHandle(FileHandle&&) noexcept = default; // 允许转移所有权
    FileHandle& operator=(FileHandle&&) noexcept = default;
};
```

适合独占文件句柄、网络连接和其他不可复制资源。

---

## 12. 智能指针与复制语义

### 12.1 `unique_ptr`

`std::unique_ptr` 表示独占所有权，因此不能复制，只能移动。类包含 `unique_ptr` 时，默认情况下也不能拷贝，但通常可以移动。

如果类仍需要值语义，可以手写拷贝操作，创建新的资源副本；移动操作则可以使用默认实现。

```cpp
#include <algorithm>
#include <cstddef>
#include <memory>

class Buffer {
private:
    std::size_t size_{0};
    std::unique_ptr<int[]> data_;

public:
    explicit Buffer(std::size_t size)
        : size_(size),
          data_(size > 0 ? std::make_unique<int[]>(size) : nullptr) {
    }

    Buffer(const Buffer& other)
        : size_(other.size_),
          data_(other.size_ > 0
                    ? std::make_unique<int[]>(other.size_)
                    : nullptr) {
        // unique_ptr 管释放，当前函数只负责深拷贝内容
        if (size_ > 0) {
            std::copy(
                other.data_.get(),
                other.data_.get() + size_,
                data_.get()
            );
        }
    }

    Buffer(Buffer&&) noexcept = default;
    Buffer& operator=(Buffer&&) noexcept = default;
    ~Buffer() = default;
};
```

### 12.2 `shared_ptr`

复制 `shared_ptr` 不会复制它管理的对象，而是增加共享所有权：

```cpp
#include <memory>

int main() {
    auto first = std::make_shared<int>(10);
    auto second = first; // 两个 shared_ptr 共同拥有同一个 int
}
```

这种共享不是错误的浅拷贝，而是 `shared_ptr` 明确设计的所有权语义。只有业务确实需要共享生命周期时才应使用。

---

## 13. 复制后交换（copy-and-swap）

一种经典赋值实现是先按值复制参数，再交换资源：

```cpp
#include <utility>

class Buffer {
public:
    void swap(Buffer& other) noexcept {
        using std::swap;

        swap(size_, other.size_); // 交换大小
        swap(data_, other.data_); // 交换资源指针
    }

    Buffer& operator=(Buffer other) {
        // other 已经通过拷贝或移动构造完成
        swap(other);

        // 函数结束时，other 析构并释放当前对象原来的旧资源
        return *this;
    }

private:
    std::size_t size_{0};
    int* data_{nullptr};
};
```

优点：

- 复制临时参数失败时，目标对象保持不变；
- 交换操作可以设计为 `noexcept`；
- 能统一处理一部分拷贝赋值和移动赋值逻辑。

初学阶段应先掌握普通的拷贝赋值和移动赋值，再理解此技巧。

---

## 14. 如何选择复制策略

### 14.1 深拷贝：值语义

复制后两个对象独立，适合字符串、动态数组、图片数据等“副本”概念明确的对象。

### 14.2 共享语义

复制后共同拥有资源，适合业务上本来就需要共享生命周期的对象，可使用 `std::shared_ptr` 明确表达。

### 14.3 禁止拷贝、允许移动

适合独占文件句柄、网络连接、互斥锁或其他无法合理复制的资源。

设计类时应先回答：

> “复制这个对象”在业务上究竟意味着创建独立副本、共享同一资源，还是根本不应允许？

---

## 15. 常见错误

1. 析构函数释放裸资源，却使用编译器默认浅拷贝；
2. `new[]` 与 `delete` 混用，正确配对是 `new[]`/`delete[]`；
3. 移动构造接管资源后没有清空源对象；
4. 移动赋值覆盖目标指针前没有释放旧资源；
5. 拷贝赋值先释放旧资源，导致申请新资源失败后对象被破坏；
6. 把两个 `unique_ptr` 交给同一个裸指针，造成重复释放；
7. 对所有指针机械深拷贝，而没有先判断它是否拥有资源；
8. 为了方便滥用 `shared_ptr`，使所有权关系变得模糊。

---

## 16. 面试速记

> 浅拷贝对指针成员通常只复制地址，深拷贝会重新申请资源并复制内容。拥有型裸指针若使用默认浅拷贝，容易造成相互影响和重复释放。三法则关注析构、拷贝构造和拷贝赋值；C++11 后加入移动构造和移动赋值，扩展为五法则。现代 C++ 更推荐零法则，即使用 `vector`、`string`、`unique_ptr` 等 RAII 类型管理资源，让业务类尽量不手写资源管理函数。复制策略最终应由所有权语义决定。

## 17. 相关笔记与来源说明

- [RAII、异常安全与资源生命周期](RAII、异常安全与资源生命周期.md)
- [C++ 左值、右值、移动语义与完美转发](C++左值、右值、移动语义与完美转发.md)
- [C++ 面向对象、虚函数与对象模型](C++面向对象、虚函数与对象模型.md)

本文根据本次会话中的深拷贝、浅拷贝、拷贝控制、三/五/零法则等讲解整理。裸指针 `Buffer` 仅用于教学，实际项目应优先使用标准 RAII 类型。
