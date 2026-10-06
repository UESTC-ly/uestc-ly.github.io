# C++ 左值、右值、移动语义与完美转发

> 本文整理 C++ 中的值类别、引用、移动语义与完美转发。重点是理解它们之间的关系，并掌握常见用法与易错点。

## 目录

- [1. 核心关系](#1-核心关系)
- [2. 左值与右值](#2-左值与右值)
- [3. 左值引用与右值引用](#3-左值引用与右值引用)
- [4. 移动语义](#4-移动语义)
- [5. `std::move`](#5-stdmove)
- [6. 移动构造与移动赋值](#6-移动构造与移动赋值)
- [7. 移动后的对象](#7-移动后的对象)
- [8. 完美转发](#8-完美转发)
- [9. 转发引用与引用折叠](#9-转发引用与引用折叠)
- [10. `std::move` 与 `std::forward` 的区别](#10-stdmove-与-stdforward-的区别)
- [11. 可变参数的完美转发](#11-可变参数的完美转发)
- [12. 常见错误](#12-常见错误)
- [13. 面试问答](#13-面试问答)
- [14. 速记总结](#14-速记总结)

---

## 1. 核心关系

这几个概念可以按下面的逻辑理解：

```text
左值、右值
    ↓
描述表达式是否具有稳定身份，以及是否适合转移资源
    ↓
左值引用、右值引用
    ↓
分别绑定已有对象和临时对象
    ↓
移动语义
    ↓
接管不再需要的对象所拥有的资源，避免昂贵复制
    ↓
完美转发
    ↓
模板函数继续传参时，保留实参原来的左值/右值属性
```

关键结论：

1. 左值通常表示有明确身份、之后仍可访问的对象。
2. 右值通常表示临时值，或者即将不再使用的值。
3. 右值引用为移动语义提供了语言基础。
4. `std::move` 不执行移动，只把表达式转换成可移动的右值形式。
5. 真正的资源转移由移动构造函数或移动赋值运算符完成。
6. 完美转发依靠转发引用和 `std::forward` 保留参数原来的值类别。

---

## 2. 左值与右值

### 2.1 左值

可以先把左值理解为：

> 有明确身份、能够被定位、之后还可以继续访问的对象表达式。

常见左值包括：

- 有名字的普通变量；
- 解引用表达式；
- 返回左值引用的函数调用；
- 数组下标访问得到的元素。

```cpp
#include <string>

int number = 10;
std::string name = "Tom";

number = 20;  // number 是左值，可以作为赋值目标
name = "Bob"; // name 是左值

int* pointer = &number; // 普通左值通常可以取地址
```

返回引用的函数调用也是左值：

```cpp
int globalValue = 10;

int& getValue() {
    // 返回已有对象的左值引用
    return globalValue;
}

int main() {
    getValue() = 20; // 相当于给 globalValue 赋值
}
```

### 2.2 右值

可以先把右值理解为：

> 临时产生、通常马上就会被销毁，或者其资源可以被接管的表达式。

常见右值包括：

- 数字、布尔等字面量；
- 临时对象；
- 算术表达式的临时结果；
- 按值返回的函数调用。

```cpp
#include <string>
#include <vector>

int a = 10;
int b = 20;

int result = a + b;                    // a + b 是临时结果
std::string name = std::string("Tom"); // std::string("Tom") 是临时对象
std::vector<int> values{1, 2, 3};      // 右侧创建了临时初始化数据
```

按值返回的函数调用通常是右值：

```cpp
#include <string>

std::string createName() {
    return "Tom";
}

int main() {
    std::string name = createName(); // createName() 的结果是临时值
}
```

### 2.3 左值不等于“可修改”

`const` 对象仍然可以是左值，但不能修改：

```cpp
const int number = 10;

// number 是左值，但受 const 限制，不能修改
// number = 20; // 编译错误
```

因此，不要把左值简单等同于“可以写在赋值号左边”。更准确的理解是：

> 左值强调对象具有身份；是否可修改还要看它是否受到 `const` 等限制。

### 2.4 初学阶段的辅助判断

以下方法可以辅助判断，但不是完整的语言定义：

- 有名字、之后还能继续访问：通常是左值；
- 临时创建、马上使用：通常是右值；
- 普通左值通常可以取地址；
- 按值返回的函数结果通常是右值；
- 返回引用的函数结果通常是左值。

---

## 3. 左值引用与右值引用

### 3.1 左值引用 `T&`

左值引用通常绑定已有对象：

```cpp
int number = 10;
int& reference = number;

reference = 20; // 通过引用修改原对象
// 此时 number 也是 20
```

普通左值引用不能直接绑定临时右值：

```cpp
// int& reference = 10; // 编译错误
```

### 3.2 常量左值引用 `const T&`

常量左值引用既可以绑定左值，也可以绑定右值：

```cpp
int number = 10;

const int& first = number; // 绑定左值
const int& second = 20;    // 绑定右值
```

但不能通过它修改对象：

```cpp
// first = 30;  // 编译错误
// second = 30; // 编译错误
```

函数只读取参数、不需要保存参数时，经常使用 `const T&`：

```cpp
#include <iostream>
#include <string>

void printName(const std::string& name) {
    // 只读取字符串，避免复制
    std::cout << name << '\n';
}

int main() {
    std::string name = "Tom";

    printName(name);                // 接收左值
    printName(std::string("Bob"));  // 接收右值
    printName("Jerry");             // 可转换为临时 std::string
}
```

### 3.3 右值引用 `T&&`

普通右值引用主要绑定右值或临时对象：

```cpp
#include <string>

std::string&& reference = std::string("Tom");
```

普通右值引用不能直接绑定左值：

```cpp
std::string name = "Tom";

// std::string&& reference = name; // 编译错误
```

右值引用的重要用途是：

> 表示这个对象的原值即将不再需要，因此可以接管其内部资源。

### 3.4 有名字的右值引用变量仍然是左值表达式

这是非常重要的易错点：

```cpp
#include <iostream>
#include <string>
#include <utility>

void process(const std::string&) {
    std::cout << "左值版本\n";
}

void process(std::string&&) {
    std::cout << "右值版本\n";
}

int main() {
    std::string&& reference = std::string("Tom");

    process(reference);            // reference 有名字，因此是左值表达式
    process(std::move(reference)); // 转换成右值形式，调用右值版本
}
```

必须区分：

- 变量的声明类型可能是 `T&&`；
- 但这个变量一旦有了名字，它作为表达式使用时就是左值。

---

## 4. 移动语义

### 4.1 为什么需要移动语义

复制对象时，一般需要创建一份独立资源：

```cpp
#include <string>

std::string first = "一个较长的字符串";
std::string second = first; // 复制
```

复制后，`first` 和 `second` 各自拥有一份可独立使用的数据。

对于 `std::string`、`std::vector`、大型自定义对象等，复制可能涉及：

1. 重新分配内存；
2. 复制全部元素；
3. 分别维护两份资源。

如果源对象马上就要销毁，复制整份资源就可能没有必要。移动语义允许目标对象直接接管源对象内部的资源。

### 4.2 复制与移动的区别

```text
复制：
源对象继续保留资源
目标对象获得一份新的资源副本

移动：
目标对象接管源对象的资源
源对象不再拥有原来的资源
```

可以形象地理解为：

```text
复制：重新复制一套房子
移动：把现有房子的钥匙交给另一个人
```

对于动态数组、字符串缓冲区等资源，移动往往只需要转移：

- 指针；
- 长度；
- 容量；
- 文件句柄等。

因此移动通常比深复制更高效。

---

## 5. `std::move`

### 5.1 基本用法

```cpp
#include <iostream>
#include <string>
#include <utility>

int main() {
    std::string source = "Tom";

    // 表示 source 的原值后面不再需要，允许 target 接管其资源
    std::string target = std::move(source);

    std::cout << target << '\n';
}
```

使用 `std::move` 需要包含：

```cpp
#include <utility>
```

### 5.2 `std::move` 本身不会移动资源

单独调用：

```cpp
std::move(source);
```

通常不会转移任何资源。`std::move` 的主要作用是：

> 把表达式转换成可以匹配右值引用的形式，表示调用者允许移动该对象。

真正的资源转移由以下函数完成：

- 移动构造函数；
- 移动赋值运算符。

例如：

```cpp
std::string target = std::move(source);
```

过程可以理解为：

1. `std::move(source)` 把 `source` 转换成可移动的右值形式；
2. 编译器选择 `std::string` 的移动构造函数；
3. 移动构造函数接管 `source` 的内部资源。

### 5.3 常见使用场景

#### 场景一：明确不再需要原对象的值

```cpp
#include <string>
#include <utility>
#include <vector>

int main() {
    std::vector<std::string> names;
    std::string name = "Tom";

    // 把 name 的资源移入容器，之后不再依赖 name 的原值
    names.push_back(std::move(name));
}
```

#### 场景二：把按值参数移动到成员变量

```cpp
#include <string>
#include <utility>

class Student {
private:
    std::string name_;

public:
    explicit Student(std::string name)
        : name_(std::move(name)) {
        // 参数 name 后面不再使用，可以把资源移动给成员变量
    }
};
```

#### 场景三：转移 `unique_ptr` 所有权

```cpp
#include <memory>
#include <utility>

int main() {
    auto first = std::make_unique<int>(42);

    // unique_ptr 不能复制，只能移动所有权
    auto second = std::move(first);

    // 移动后 first 不再拥有该 int 对象
}
```

### 5.4 不要滥用 `std::move`

如果之后仍需要源对象原来的值，就不要移动：

```cpp
std::string source = "Tom";
std::string target = std::move(source);

// 不应再假设 source 仍然等于 "Tom"
```

如果需要两份独立数据，应复制：

```cpp
std::string source = "Tom";
std::string target = source; // 复制，source 仍保留原值
```

### 5.5 返回局部对象时通常不要手动移动

推荐：

```cpp
#include <string>

std::string createName() {
    std::string name = "Tom";

    // 让编译器进行返回值优化或自动选择移动
    return name;
}
```

通常不要习惯性写成：

```cpp
std::string createName() {
    std::string name = "Tom";

    return std::move(name); // 通常没有必要，还可能影响返回值优化
}
```

### 5.6 `const` 对象通常不能真正移动

```cpp
#include <string>
#include <utility>

const std::string source = "Tom";
std::string target = std::move(source);
```

`std::move(source)` 仍然带有 `const`。普通移动构造函数通常需要修改源对象，因此无法接受 `const` 右值，以上代码往往会调用复制构造函数。

结论：

> 如果对象后续需要转移资源，通常不应把它声明为 `const`。

---

## 6. 移动构造与移动赋值

### 6.1 移动构造函数

移动构造函数用于创建新对象：

```cpp
类名(类名&& other);
```

示例：

```cpp
#include <cstddef>
#include <utility>

class Buffer {
private:
    int* data_{nullptr};
    std::size_t size_{0};

public:
    explicit Buffer(std::size_t size)
        : data_(new int[size]{}), size_(size) {
        // 创建指定大小的动态数组
    }

    ~Buffer() {
        // 释放当前对象拥有的动态数组
        delete[] data_;
    }

    Buffer(Buffer&& other) noexcept
        : data_(other.data_), size_(other.size_) {
        // 接管 other 的资源后，让 other 放弃所有权
        other.data_ = nullptr;
        other.size_ = 0;
    }
};

int main() {
    Buffer first(1000);

    // second 正在被创建，因此调用移动构造函数
    Buffer second(std::move(first));
}
```

移动前：

```text
first.data_  → 动态数组
```

移动后：

```text
first.data_  = nullptr
second.data_ → 原来的动态数组
```

必须让源对象放弃资源，否则两个对象析构时可能重复释放同一块内存。

### 6.2 移动赋值运算符

移动赋值用于目标对象已经存在的情况：

```cpp
类名& operator=(类名&& other);
```

示例：

```cpp
#include <cstddef>
#include <utility>

class Buffer {
private:
    int* data_{nullptr};
    std::size_t size_{0};

public:
    explicit Buffer(std::size_t size)
        : data_(new int[size]{}), size_(size) {
    }

    ~Buffer() {
        delete[] data_;
    }

    Buffer(Buffer&& other) noexcept
        : data_(other.data_), size_(other.size_) {
        // 转移所有权，清空源对象
        other.data_ = nullptr;
        other.size_ = 0;
    }

    Buffer& operator=(Buffer&& other) noexcept {
        if (this != &other) {
            // 先释放当前对象原来拥有的资源
            delete[] data_;

            // 接管源对象的资源
            data_ = other.data_;
            size_ = other.size_;

            // 源对象放弃资源，避免重复释放
            other.data_ = nullptr;
            other.size_ = 0;
        }

        return *this;
    }

    // 此示例聚焦移动语义，禁止复制，避免浅复制裸指针
    Buffer(const Buffer&) = delete;
    Buffer& operator=(const Buffer&) = delete;
};

int main() {
    Buffer first(1000);
    Buffer second(100);

    // second 已经存在，因此调用移动赋值运算符
    second = std::move(first);
}
```

移动赋值一般需要：

1. 防止自移动赋值；
2. 释放目标对象原有资源；
3. 接管源对象资源；
4. 将源对象置于安全的可析构状态；
5. 返回 `*this`。

### 6.3 二者的区别

```cpp
Buffer first(1000);

Buffer second(std::move(first)); // 移动构造：创建新对象

Buffer third(100);
third = std::move(second);       // 移动赋值：目标对象已经存在
```

简单记忆：

```text
创建新对象：移动构造
已有对象重新接收资源：移动赋值
```

### 6.4 为什么移动函数常写 `noexcept`

```cpp
Buffer(Buffer&& other) noexcept;
Buffer& operator=(Buffer&& other) noexcept;
```

标准容器在扩容或重新分配内存时，为了维持异常安全，通常更愿意使用不会抛异常的移动构造函数。

如果移动构造函数没有标记 `noexcept`，并且类型还支持复制，某些标准容器可能选择复制而不是移动。

---

## 7. 移动后的对象

对象移动后通常处于：

> 有效但未指定的状态。

“有效”表示它仍然可以：

- 正常析构；
- 被重新赋值；
- 执行不依赖原值的合法操作。

“未指定”表示不能依赖它还保留移动前的具体内容。

```cpp
#include <string>
#include <utility>

int main() {
    std::string source = "Tom";
    std::string target = std::move(source);

    // 不要假设 source 一定为空，也不要假设它仍是 "Tom"

    // 可以重新赋值后继续正常使用
    source = "Jerry";
}
```

实践原则：

> 对象被移动后，不再读取或依赖它原来的值；如果还要继续使用，先重新赋值。

---

## 8. 完美转发

### 8.1 完美转发要解决的问题

先准备两个重载：

```cpp
#include <iostream>
#include <string>

void process(const std::string&) {
    std::cout << "处理左值\n";
}

void process(std::string&&) {
    std::cout << "处理右值\n";
}
```

直接调用时，可以正确区分左值和右值：

```cpp
std::string name = "Tom";

process(name);               // 调用左值版本
process(std::string("Bob")); // 调用右值版本
```

现在增加一个包装函数：

```cpp
template <typename T>
void wrapper(T&& value) {
    process(value);
}
```

即使调用者传入右值，函数体内的 `value` 也是有名字的变量，因此 `value` 是左值表达式：

```cpp
std::string name = "Tom";

wrapper(name);               // process(value) 按左值调用
wrapper(std::string("Bob")); // process(value) 仍按左值调用
```

这就丢失了调用者传入参数时的左值/右值属性。

### 8.2 使用 `std::forward`

正确写法：

```cpp
#include <utility>

template <typename T>
void wrapper(T&& value) {
    // 保留调用者传入参数时的左值/右值属性
    process(std::forward<T>(value));
}
```

效果：

```cpp
std::string name = "Tom";

wrapper(name);               // 保持左值，调用左值版本
wrapper(std::string("Bob")); // 保持右值，调用右值版本
```

`std::forward` 的作用可以概括为：

```text
调用者传入左值 → 继续转发为左值
调用者传入右值 → 继续转发为右值
```

这就是完美转发。

---

## 9. 转发引用与引用折叠

### 9.1 什么是转发引用

在下面的特定形式中：

```cpp
template <typename T>
void wrapper(T&& value);
```

如果 `T` 由调用时自动推导，那么 `T&&` 是转发引用。

转发引用可以接收左值和右值：

```cpp
std::string name = "Tom";

wrapper(name);               // 可以接收左值
wrapper(std::string("Bob")); // 可以接收右值
```

### 9.2 普通右值引用不是转发引用

```cpp
void process(std::string&& value);
```

这里没有模板类型推导，因此是普通右值引用，只能直接接收右值：

```cpp
process(std::string("Tom")); // 正确

std::string name = "Tom";
// process(name); // 编译错误
```

所以不能看到 `&&` 就一律认为它是转发引用。

### 9.3 引用折叠规则

引用折叠规则如下：

```text
T&  + &  → T&
T&  + && → T&
T&& + &  → T&
T&& + && → T&&
```

简单记忆：

> 只要组合中出现左值引用 `&`，结果就是左值引用；只有两边都是 `&&`，结果才是右值引用。

传入左值：

```cpp
std::string name = "Tom";
wrapper(name);
```

此时 `T` 会被推导为：

```cpp
T = std::string&
```

参数类型 `T&&` 代入后是：

```cpp
std::string& &&
```

引用折叠后得到：

```cpp
std::string&
```

传入右值：

```cpp
wrapper(std::string("Bob"));
```

此时 `T` 被推导为：

```cpp
T = std::string
```

参数类型最终是：

```cpp
std::string&&
```

---

## 10. `std::move` 与 `std::forward` 的区别

### `std::move`

```cpp
target(std::move(value));
```

含义：

> 无论 `value` 原来如何，现在都允许把它当成右值处理。

适用场景：明确转移资源或所有权。

### `std::forward`

```cpp
target(std::forward<T>(value));
```

含义：

> 调用者原来传入左值，就继续作为左值；原来传入右值，就继续作为右值。

适用场景：模板包装函数中的完美转发。

| 工具 | 作用 | 常见场景 |
|---|---|---|
| `std::move(value)` | 无条件转换成可移动的右值形式 | 转移资源或所有权 |
| `std::forward<T>(value)` | 保留参数原来的值类别 | 模板包装与完美转发 |

速记：

```text
move：我不再需要它的原值，可以移动
forward：调用者怎么传给我，我就怎么继续传
```

---

## 11. 可变参数的完美转发

工厂函数通常需要接收任意数量、任意类型的构造参数，再把它们传给目标对象：

```cpp
#include <memory>
#include <utility>

template <typename T, typename... Args>
std::unique_ptr<T> createObject(Args&&... args) {
    // 将每个参数按照原来的左值/右值属性转发给 T 的构造函数
    return std::make_unique<T>(
        std::forward<Args>(args)...
    );
}
```

示例类型：

```cpp
#include <string>
#include <utility>

class Student {
private:
    std::string name_;
    int age_{};

public:
    Student(std::string name, int age)
        : name_(std::move(name)), age_(age) {
        // 按值接收 name，再移动到成员变量中
    }
};
```

使用：

```cpp
auto student = createObject<Student>("Tom", 18);
```

其中：

```cpp
Args&&... args
```

表示接收任意数量的转发引用参数。

```cpp
std::forward<Args>(args)...
```

表示把参数包中的每个参数按照原来的值类别继续转发。

实际项目中，`std::make_unique` 已经提供了这一能力，一般可以直接写：

```cpp
auto student = std::make_unique<Student>("Tom", 18);
```

---

## 12. 常见错误

### 12.1 误以为 `std::move` 会自动移动

```cpp
std::move(value); // 单独调用通常不会转移任何资源
```

正确理解：它只是提供匹配移动操作的右值形式。

### 12.2 移动后继续依赖源对象原值

```cpp
std::string source = "Tom";
std::string target = std::move(source);

// 错误思路：继续假设 source 还是 "Tom"
```

正确做法：不再依赖源对象的旧值，或者先重新赋值。

### 12.3 把有名字的右值引用变量当成右值

```cpp
std::string&& value = std::string("Tom");

process(value); // value 有名字，是左值表达式
```

需要明确按右值处理时：

```cpp
process(std::move(value));
```

模板中需要保留原值类别时：

```cpp
process(std::forward<T>(value));
```

### 12.4 返回局部变量时习惯性写 `std::move`

```cpp
return std::move(localObject); // 通常没必要
```

通常直接写：

```cpp
return localObject;
```

### 12.5 对 `const` 对象使用 `std::move`，误以为一定会移动

```cpp
const std::string source = "Tom";
std::string target = std::move(source); // 通常仍会复制
```

原因是普通移动操作需要修改源对象，而 `const` 不允许修改。

### 12.6 在非模板函数中使用 `std::forward`

`std::forward` 的主要用途是依据模板推导结果保留参数原值类别。普通业务代码明确放弃源对象时，应使用 `std::move`，而不是随意使用 `std::forward`。

---

## 13. 面试问答

### 13.1 什么是左值和右值？

左值通常是有明确身份、可被定位并能在之后继续访问的对象表达式；右值通常是临时产生或即将不再使用的值。左值强调对象身份，不代表一定可以修改，例如 `const` 对象仍然是左值。

### 13.2 `std::move` 会真正移动对象吗？

不会。`std::move` 只是把表达式转换成可匹配右值引用的形式，真正的资源转移由移动构造函数或移动赋值运算符完成。

### 13.3 移动后的对象还能使用吗？

可以正常析构和重新赋值，但它的具体值通常处于有效但未指定状态，不能继续依赖移动前的内容。

### 13.4 为什么右值引用变量本身是左值？

因为这个变量有名字，可以被重复定位和访问。变量的类型与表达式的值类别是两个不同概念。

```cpp
std::string&& value = std::string("Tom");

process(value);            // value 是左值表达式
process(std::move(value)); // 转换后按右值处理
```

### 13.5 `std::move` 和 `std::forward` 有什么区别？

- `std::move` 无条件把表达式转换成可移动的右值形式；
- `std::forward` 根据模板推导结果保留实参原来的左值或右值属性。

### 13.6 什么是完美转发？

完美转发是指模板包装函数继续传递参数时，尽可能保持参数原来的类型、`const` 属性和值类别。常见写法是：

```cpp
template <typename T>
void wrapper(T&& value) {
    target(std::forward<T>(value));
}
```

### 13.7 什么是转发引用？

当 `T` 是由调用自动推导的函数模板参数，且形参形式为 `T&&` 时，`T&&` 是转发引用。它可以接收左值和右值，并配合 `std::forward` 实现完美转发。

### 13.8 为什么移动构造函数经常标记 `noexcept`？

标准容器为了保证异常安全，在重新分配内存时通常优先使用不会抛异常的移动操作。若移动构造函数没有 `noexcept`，容器在可复制时可能改用复制。

---

## 14. 速记总结

### 引用类型

```cpp
T&       // 左值引用，通常绑定已有左值
const T& // 只读引用，可以绑定左值和右值
T&&      // 普通场景下是右值引用
```

### 移动

```cpp
std::string target = std::move(source);
```

表示允许从 `source` 转移资源，但真正的移动由移动构造或移动赋值完成。

### 完美转发

```cpp
template <typename T>
void wrapper(T&& value) {
    // 调用者传左值就继续传左值，传右值就继续传右值
    target(std::forward<T>(value));
}
```

### 最核心的四句话

> 左值通常是有明确身份、可以继续访问的对象。  
> 右值通常是临时值或即将不再使用的值。  
> 移动语义通过转移资源避免不必要的复制，`std::move` 只是提供移动条件。  
> 完美转发使用转发引用和 `std::forward`，把参数按照调用者原来的方式继续传递。

---

## 相关笔记

- [秋招求职技术栈](../秋招求职技术栈.md)
