# C++ 模板、泛型编程与可变参数模板

> 模板是 C++ 的语言机制，泛型编程是使用模板编写类型无关代码的思想，模板元编程则利用模板在编译期进行类型处理、计算和代码选择。

## 1. 三个概念的关系

```text
模板：提供类型参数、非类型参数和实例化机制
泛型编程：面向类型的能力编程，而不是绑定某个具体类型
模板元编程：在编译期完成类型判断、类型变换、计算和分支选择
```

标准模板库 STL 是泛型编程的典型实践：容器、迭代器和算法通过模板协作。

---

## 2. 函数模板

```cpp
#include <string>

// T 是类型模板参数
// 只要 T 支持比较和复制，这个模板就可以实例化

template <typename T>
T maxValue(const T& left, const T& right) {
    return left > right ? left : right;
}

int main() {
    int intResult = maxValue(1, 2); // T 推导为 int

    std::string first = "Alice";
    std::string second = "Bob";
    std::string textResult = maxValue(first, second); // T 推导为 std::string
}
```

编译器根据调用推导 `T`，并生成所需的具体版本，这个过程称为模板实例化。

也可以显式指定模板参数：

```cpp
double result = maxValue<double>(1.5, 2.5); // 显式指定 T 为 double
```

---

## 3. 类模板

```cpp
#include <utility>

// Box 可以保存任意满足构造要求的类型

template <typename T>
class Box {
private:
    T value_;

public:
    explicit Box(T value)
        : value_(std::move(value)) {
    }

    const T& value() const {
        // 返回只读引用，避免复制大型对象
        return value_;
    }
};

int main() {
    Box<int> numberBox(42);
    Box<double> priceBox(3.14);
}
```

`std::vector<int>`、`std::map<std::string, int>` 都是类模板实例。

---

## 4. 非类型模板参数

模板参数不一定是类型，也可以是编译期常量：

```cpp
#include <cstddef>

// T 是类型参数，N 是非类型模板参数

template <typename T, std::size_t N>
class FixedArray {
private:
    T data_[N]{}; // 在对象内部保存固定长度数组

public:
    constexpr std::size_t size() const {
        return N; // N 在编译期已经确定
    }
};

FixedArray<int, 10> numbers;
```

标准库的 `std::array<T, N>` 就采用类似形式。

---

## 5. 泛型编程：依赖能力而非具体类型

```cpp
// 这个函数不要求类型继承某个公共基类
// 只要求对象能够调用 speak()

template <typename T>
void makeSound(const T& object) {
    object.speak();
}
```

这种方式常称为静态多态：具体调用在编译期确定。

| 对比项 | 模板泛型/静态多态 | 虚函数/运行时多态 |
|---|---|---|
| 主要机制 | 模板 | 继承与虚函数 |
| 绑定时间 | 编译期 | 运行期 |
| 是否需要公共基类 | 不需要 | 通常需要 |
| 调用开销 | 易于内联 | 通常有间接调用 |
| 常见代价 | 编译时间、代码膨胀、报错复杂 | `vptr`、间接调用和继承耦合 |

---

## 6. 模板特化

### 6.1 类模板全特化

```cpp
// 通用版本

template <typename T>
struct TypeName {
    static const char* get() {
        return "unknown";
    }
};

// 针对 int 的全特化版本

template <>
struct TypeName<int> {
    static const char* get() {
        return "int";
    }
};
```

### 6.2 类模板偏特化

```cpp
// 默认认为不是指针

template <typename T>
struct IsPointer {
    static constexpr bool value = false;
};

// 所有 T* 类型都匹配这个偏特化

template <typename T>
struct IsPointer<T*> {
    static constexpr bool value = true;
};

static_assert(!IsPointer<int>::value);
static_assert(IsPointer<int*>::value);
```

类模板可以偏特化；函数模板不能偏特化，通常使用函数重载或约束代替。

---

## 7. 基础模板元编程与类型萃取

### 7.1 编译期计算

```cpp
// 递归模板：计算 N 的阶乘

template <int N>
struct Factorial {
    static constexpr int value = N * Factorial<N - 1>::value;
};

// 全特化作为递归终点

template <>
struct Factorial<0> {
    static constexpr int value = 1;
};

static_assert(Factorial<5>::value == 120);
```

现代 C++ 的数值编译期计算通常优先使用更直观的 `constexpr` 函数：

```cpp
constexpr int factorial(int value) {
    // constexpr 函数可在编译期求值
    return value <= 1 ? 1 : value * factorial(value - 1);
}

static_assert(factorial(5) == 120);
```

### 7.2 `type_traits`

```cpp
#include <type_traits>

static_assert(std::is_integral_v<int>);
static_assert(!std::is_integral_v<double>);
static_assert(std::is_pointer_v<int*>);
static_assert(std::is_same_v<int, std::remove_reference_t<int&>>);
```

常用类型判断：

```text
std::is_same_v<T, U>
std::is_integral_v<T>
std::is_floating_point_v<T>
std::is_pointer_v<T>
std::is_const_v<T>
std::is_base_of_v<Base, Derived>
```

常用类型变换：

```text
std::remove_reference_t<T>
std::remove_const_t<T>
std::remove_cvref_t<T>      // C++20
std::add_pointer_t<T>
```

### 7.3 `if constexpr`

C++17 可以根据类型执行编译期分支：

```cpp
#include <iostream>
#include <type_traits>

// 指针和非指针类型采用不同实现

template <typename T>
void printValue(const T& value) {
    if constexpr (std::is_pointer_v<T>) {
        if (value != nullptr) {
            std::cout << *value << '\n';
        }
    } else {
        std::cout << value << '\n';
    }
}
```

未被选择的 `if constexpr` 分支在当前模板实例中会被丢弃，因此可以包含只对另一类类型有效的代码。

---

## 8. 可变参数模板

可变参数模板可以接收零个或多个类型与函数参数：

```cpp
// Args 是模板参数包，args 是函数参数包

template <typename... Args>
void log(Args&&... args) {
    // 参数包必须展开后才能逐项使用
}
```

### 8.1 模板参数包和函数参数包

```cpp
template <typename... Args>
```

表示 `Args` 是零个或多个类型组成的模板参数包。

```cpp
Args&&... args
```

表示根据 `Args` 中的每个类型声明一组函数参数。

例如调用：

```cpp
log(10, 3.14, "hello"); // 参数数量和类型都可以变化
```

`Args` 会推导出一组与这些实参对应的类型。字符串字面量在转发引用下可能保留数组引用类型，因此实际推导结果可能比简化描述更精确。

### 8.2 参数包不是容器

`args` 不是数组、`vector` 或 `tuple`，不能直接用范围 `for` 遍历，也不能直接写 `std::cout << args`。必须进行包展开。

### 8.3 `sizeof...`

```cpp
#include <cstddef>

// 返回实参数量

template <typename... Args>
constexpr std::size_t argumentCount(Args&&... args) {
    return sizeof...(args);
}

static_assert(argumentCount() == 0);
static_assert(argumentCount(1, 2.0, "text") == 3);
```

`sizeof...(Args)` 得到类型数量，`sizeof...(args)` 得到函数参数数量，二者在这里相同。

---

## 9. 参数包展开与折叠表达式

### 9.1 C++17 折叠表达式

```cpp
#include <iostream>
#include <utility>

// 输出任意数量、任意可输出类型的参数

template <typename... Args>
void log(Args&&... args) {
    std::cout << "[LOG] ";

    // 对每个参数执行一次输出，并保留其原始值类别
    ((std::cout << std::forward<Args>(args)), ...);

    std::cout << '\n';
}

int main() {
    int age = 18;
    log("name=Tom, age=", age);
}
```

这句：

```cpp
((std::cout << std::forward<Args>(args)), ...);
```

可概念化为：

```text
std::cout << 第一个参数;
std::cout << 第二个参数;
std::cout << 第三个参数;
...
```

如果希望连续使用 `operator<<`，也可以写：

```cpp
(std::cout << ... << std::forward<Args>(args)); // 左折叠输出所有参数
```

### 9.2 C++11/14 递归展开

C++17 之前没有折叠表达式，常用递归处理参数包：

```cpp
#include <iostream>
#include <utility>

void log() {
    // 无参数版本是递归终点
    std::cout << '\n';
}

template <typename T, typename... Rest>
void log(T&& first, Rest&&... rest) {
    // 每次处理第一个参数
    std::cout << std::forward<T>(first) << ' ';

    // 继续递归处理剩余参数
    log(std::forward<Rest>(rest)...);
}
```

---

## 10. 转发引用与完美转发

```cpp
#include <utility>

// T 由调用自动推导，T&& 是转发引用

template <typename T>
void wrapper(T&& value) {
    // 调用者传左值就继续传左值，传右值就继续传右值
    target(std::forward<T>(value));
}
```

对于可变参数模板：

```cpp
#include <memory>
#include <utility>

// 将任意构造参数继续传给 T 的构造函数

template <typename T, typename... Args>
std::unique_ptr<T> createObject(Args&&... args) {
    return std::make_unique<T>(
        std::forward<Args>(args)...
    );
}
```

要点：

- `Args&&...` 在模板推导场景中是一组转发引用；
- 命名变量 `args` 在表达式中都是左值；
- 使用 `std::forward<Args>(args)...` 才能保留每个实参原来的值类别；
- `std::move` 是无条件转换为可移动形式，不能替代完美转发。

更详细内容见：[C++ 左值、右值、移动语义与完美转发](C++左值、右值、移动语义与完美转发.md)。

---

## 11. C++20 Concepts

Concepts 可以明确表达模板参数必须具备的能力：

```cpp
#include <concepts>

// 要求 T 的两个对象支持加法

template <typename T>
concept Addable = requires(T left, T right) {
    left + right;
};

// 只有满足 Addable 的类型才能实例化

template <Addable T>
T add(T left, T right) {
    return left + right;
}
```

它能让接口意图更清晰，并改善模板不满足要求时的错误信息。

---

## 12. 默认参数与可变参数模板的区别

默认参数适合参数结构固定、只允许省略末尾参数：

```cpp
#include <string>

void connect(
    const std::string& host,
    int port = 80,
    bool secure = false
) {
    // 参数类型和最大数量都是固定的
}
```

可变参数模板适合参数数量和类型都可变化：

```cpp
template <typename... Args>
void log(Args&&... args) {
    // 可以接收任意数量和类型的参数
}
```

| 特性 | 默认参数 | 可变参数模板 |
|---|---|---|
| 参数最大数量 | 固定 | 不固定 |
| 参数类型 | 预先确定 | 可以各不相同 |
| 典型用途 | 配置函数、构造函数 | 日志、工厂、包装与转发 |

---

## 13. 与 C++ 版本的关系

| 版本 | 与本主题相关的常用能力 |
|---|---|
| C++11 | 可变参数模板、右值引用、`std::forward`、类型萃取、`constexpr` 基础 |
| C++14 | 泛型 Lambda、变量模板、放宽 `constexpr` 限制 |
| C++17 | 折叠表达式、`if constexpr`、`*_v` 与 `*_t` 简写广泛使用 |
| C++20 | Concepts、`requires`、更强的非类型模板参数和 `constexpr` 能力 |

秋招阶段应重点掌握模板基本语法、实例化、特化、参数包、折叠表达式、`type_traits`、`if constexpr`、完美转发，并了解 Concepts 的作用。

---

## 14. 常见错误

### 14.1 直接使用参数包

```cpp
template <typename... Args>
void wrongLog(Args&&... args) {
    // std::cout << args; // 错误：参数包没有展开
}
```

### 14.2 转发时漏掉展开符

```cpp
// target(std::forward<Args>(args)); // 错误：Args 和 args 都是参数包

target(std::forward<Args>(args)...); // 正确：逐项展开
```

### 14.3 把所有 `T&&` 都当成转发引用

```cpp
void process(std::string&& value) {
    // 这里的类型固定为 std::string&&，是普通右值引用
}
```

只有模板参数由调用推导且形参形如 `T&&` 时，才是转发引用。

### 14.4 忘记模板的能力要求

模板并不意味着任何类型都能使用。调用了 `left + right`，传入类型就必须支持对应的 `operator+`；输出参数则要求存在合适的 `operator<<`。

---

## 15. 速记

```text
template <typename T>：一个类型模板参数
template <typename... Args>：零个或多个类型组成的参数包
Args&&... args：一组转发引用形参
sizeof...(Args)：参数包元素数量
表达式...：参数包展开
折叠表达式：C++17 以统一语法处理整个参数包
std::forward<Args>(args)...：完美转发整个参数包
if constexpr：编译期选择代码分支
Concepts：显式描述模板参数能力要求
```

## 16. 相关笔记与来源说明

- [C++ 语言基础与面向对象总结](C++语言基础与面向对象总结.md)
- [C++ 左值、右值、移动语义与完美转发](C++左值、右值、移动语义与完美转发.md)
- [C++ 函数声明与类成员语法](C++函数声明与类成员语法.md)

本文根据本次会话中的模板、泛型编程、模板元编程和可变参数模板讲解整理；具体语言规则以所使用的 C++ 标准版本和编译器支持为准。
