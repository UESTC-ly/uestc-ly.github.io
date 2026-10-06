# C++ 语言基础与面向对象总结

> 面向秋招复习整理：C++11/14/17 为重点，了解 C++20 常用特性；覆盖指针、引用、数组、字符串、函数、类，以及面向对象核心机制。每一节尽量做到“能讲清语法 + 能说明用途 + 能应对面试追问”。

---

## 一、C++11/14/17 与 C++20 常用特性

### 1. C++11

C++11 是现代 C++ 的分水岭，引入了大量提升安全性、表达力和性能的特性。

- `auto`：根据初始化表达式推导变量类型，减少冗长的类型书写。
- `decltype`：获取表达式的类型，常用于模板和返回类型推导。
- 范围 `for`：简洁地遍历数组和容器。
- `nullptr`：类型安全的空指针字面量，优于 `NULL`（`NULL` 常被定义为 `0`，可能引起重载歧义）。
- `using`：定义类型别名，也可用于模板别名，比 `typedef` 更直观。
- Lambda 表达式：就地定义可调用对象，常配合标准库算法使用。
- 右值引用 `T&&` 和移动语义：把资源从临时对象“搬走”，减少不必要的深拷贝。
- 完美转发：配合转发引用和 `std::forward` 保留参数的值类别（左值 / 右值）。
- `std::move`：把对象转换为右值引用，允许调用移动构造或移动赋值；它本身不执行移动，只是做类型转换。
- `constexpr`：声明可在编译期求值的变量或函数。
- `enum class`：类型安全的强类型枚举，不会隐式转换为整数。
- `static_assert`：编译期断言，条件不满足时直接编译报错。
- 智能指针：`std::unique_ptr`、`std::shared_ptr`、`std::weak_ptr`。
- 并发库：`std::thread`、互斥量、条件变量、原子类型等。
- 容器和工具：`std::array`、`std::unordered_map`、`std::tuple`、`std::function`、`std::bind` 等。

示例：

```cpp
#include <memory>
#include <vector>

std::vector<int> values{1, 2, 3};
auto p = std::make_unique<int>(42);

for (const auto value : values) {
    // value 是只读副本
}
```

`auto` 使用要点：

```cpp
auto i = 10;        // int
auto d = 3.14;      // double
auto& r = i;        // int&，引用要显式写 &
const auto& cr = i; // const int&，避免拷贝
```

注意 `auto` 默认会丢弃引用和顶层 `const`，需要保留时要显式写出 `auto&` 或 `const auto&`。

### 2. C++14

C++14 主要是对 C++11 的补充和完善。

- 泛型 Lambda：Lambda 参数可以使用 `auto`。
- 函数返回值类型推导：使用 `auto` 作为返回类型，由 `return` 语句推导。
- 放宽 `constexpr` 函数限制：允许局部变量、循环、分支等。
- 二进制字面量（`0b1010`）和数字分隔符（`1'000'000`）。
- `std::make_unique`：C++11 遗漏，C++14 补上。

```cpp
auto add = [](auto a, auto b) {
    return a + b;
};

add(1, 2);       // int
add(1.5, 2.5);   // double
```

### 3. C++17

- 结构化绑定：一次解包数组、`pair`、`tuple` 或类对象中的成员。
- `if constexpr`：编译期条件分支，未选中的分支在实例化时被丢弃。
- `if`/`switch` 初始化语句：把变量作用域限制在条件语句内。
- 类模板参数推导（CTAD）：`std::pair p{1, 2.0};` 无需显式写模板参数。
- 折叠表达式：简化可变参数模板的展开。
- `inline` 变量：解决头文件中定义全局变量的重复定义问题。
- `std::optional`：表示“可能没有值”。
- `std::variant`：类型安全的联合体。
- `std::any`：保存任意类型的值。
- `std::string_view`：不拥有字符串内存的只读视图。
- `std::filesystem`：文件系统操作。
- `[[nodiscard]]`、`[[maybe_unused]]`、`[[fallthrough]]` 等属性。

```cpp
#include <map>
#include <optional>
#include <string>

std::optional<std::string> findName(int id);

if (auto name = findName(1); name.has_value()) {
    // name 只在 if 和后续 else-if/else 的作用域内有效
}

std::map<int, std::string> users{{1, "Alice"}};
for (const auto& [id, name] : users) {
    // id 和 name 是结构化绑定
}
```

`std::optional` 使用示例：

```cpp
std::optional<int> parse(const std::string& text);

if (auto value = parse("123")) {
    std::cout << *value;      // 解引用取值
} else {
    std::cout << "解析失败";
}

int v = parse("x").value_or(0); // 没有值时返回默认值
```

### 4. C++20 常用特性（了解）

- Concepts：约束模板参数，改善泛型代码的可读性和报错信息。
- Ranges：以范围为中心组织算法和视图，支持管道式写法。
- `std::span`：不拥有内存的连续区间视图。
- 协程：支持异步或生成器风格的代码。
- 模块：替代部分头文件包含场景，改善编译速度和封装。
- 三路比较运算符 `<=>`（太空船运算符），可一次生成全部比较运算符。
- 指定初始化：对聚合类型按成员名初始化。
- `consteval`、`constinit`：更严格地控制编译期求值和初始化。

```cpp
#include <concepts>

template <typename T>
concept Addable = requires(T a, T b) {
    a + b;
};

template <Addable T>
T add(T a, T b) {
    return a + b;
}
```

> 复习重点：理解特性解决的问题、基本语法、使用场景和生命周期影响，不必一开始追求记住所有库细节。

---

## 二、指针

### 1. 基本概念

指针是保存对象地址的变量。`&` 用于取地址，`*` 在声明中表示指针、在表达式中表示解引用。

```cpp
int value = 10;
int* p = &value;

*p = 20; // 通过指针修改 value
```

- 指针本身有自己的存储空间（在 64 位系统上通常是 8 字节）。
- 指针可以为空，用 `nullptr` 表示。
- 解引用空指针、悬空指针或野指针都是未定义行为。
- 指针的类型决定了如何解释目标地址以及指针运算的步长。

指针运算的步长由类型决定：

```cpp
int arr[3];
int* p = arr;
p + 1; // 地址前进 sizeof(int) 个字节，不是 1 个字节
```

### 2. 常见写法与含义

`const` 与指针的组合是高频考点，判断技巧是“从右往左读”，或看 `const` 紧挨着谁。

```cpp
int value = 10;

const int* p1 = &value; // 不能通过 p1 修改目标对象，p1 可以改指向
int* const p2 = &value; // p2 不能改指向，可以通过 p2 修改目标对象
const int* const p3 = &value; // 指向和目标对象都不能通过 p3 修改
```

记忆方法：

- `const` 在 `*` 左边：修饰的是“指向的对象”，对象不可改。
- `const` 在 `*` 右边：修饰的是“指针本身”，指向不可改。

### 3. 指针与数组

数组名在许多表达式中会退化为指向首元素的指针，但在 `sizeof`、取数组地址等场景不会退化。

```cpp
int a[3] = {10, 20, 30};
int* p = a;

p[1] == *(p + 1); // true
```

数组长度应在数组仍是数组类型时计算：

```cpp
int a[] = {1, 2, 3, 4};
std::size_t n = sizeof(a) / sizeof(a[0]); // 4
```

将数组传给普通函数时通常会退化为指针，因此函数无法仅凭参数得到原数组长度：

```cpp
void process(int a[]) {
    // 这里 a 实际是 int*，sizeof(a) 得到的是指针大小
}
```

可以使用模板保留数组类型：

```cpp
template <typename T, std::size_t N>
void process(T (&array)[N]) {
    // N 是数组元素个数
}
```

### 4. 动态内存与智能指针

不推荐裸 `new`/`delete` 管理资源，容易忘记释放、异常时泄漏或重复释放。现代 C++ 优先使用 RAII 和智能指针。

**RAII（Resource Acquisition Is Initialization，资源获取即初始化）**：把资源交给对象管理，构造时获取资源，析构时自动释放。资源的生命周期绑定到对象的生命周期上。

- `std::unique_ptr`：独占所有权，不能拷贝但可以移动。默认首选。
- `std::shared_ptr`：共享所有权，使用引用计数管理对象。
- `std::weak_ptr`：不增加引用计数，用于观察对象和打破循环引用。

```cpp
auto p = std::make_unique<int>(42);
// 离开作用域时自动释放资源，无需手动 delete
```

三者对比：

| 智能指针 | 所有权 | 能否拷贝 | 主要用途 |
|---|---|---:|---|
| `unique_ptr` | 独占 | 不能，可移动 | 默认选择，唯一拥有者 |
| `shared_ptr` | 共享 | 可以 | 多个对象共享生命周期 |
| `weak_ptr` | 不拥有 | 可以 | 观察对象、打破循环引用 |

记忆口诀：

```text
unique_ptr：这是我的
shared_ptr：这是我们共同的
weak_ptr：我只是看看，不负责它的生命周期
```

`shared_ptr` 可能因为循环引用无法释放：

```cpp
struct Node {
    std::shared_ptr<Node> next;
    std::weak_ptr<Node> parent; // 观察关系通常用 weak_ptr 打破循环
};
```

`weak_ptr` 使用前需要通过 `lock()` 提升为 `shared_ptr`：

```cpp
if (auto p = weak.lock()) {
    // 对象仍存活，p 是有效的 shared_ptr
} else {
    // 对象已销毁
}
```

### 5. 指针面试注意点

- `nullptr` 比 `NULL` 类型更安全。
- `delete` 必须与 `new` 配对，`delete[]` 必须与 `new[]` 配对；实际项目优先避免手动管理。
- 释放对象后原指针不会自动变为空，继续使用会形成悬空指针。
- 多态基类通常需要虚析构函数，才能通过基类指针正确删除派生类对象。

---

## 三、引用

引用是对象的别名，必须在定义时初始化，通常不能改为绑定另一个对象。

```cpp
int value = 10;
int& ref = value;
ref = 20; // value 也变为 20
```

### 1. 左值引用

```cpp
void increment(int& value) {
    ++value;
}
```

使用 `const T&` 可以避免拷贝，同时允许绑定到常量和临时对象：

```cpp
void print(const std::string& text);

print("hello");            // 可以绑定临时对象
std::string s = "world";
print(s);                  // 也可以绑定左值
```

这是传递大对象时最常用的方式：不复制，又保证不被修改。

### 2. 右值引用

```cpp
std::string makeText();
std::string text = makeText(); // 触发移动构造，接管临时对象资源
```

右值引用 `T&&` 主要用于移动语义和完美转发。移动构造通常接管源对象的资源，移动后源对象必须仍然处于有效但未指定的状态（例如可以析构、可以重新赋值）。

```cpp
class Buffer {
public:
    Buffer(Buffer&& other) noexcept;
    Buffer& operator=(Buffer&& other) noexcept;
};
```

移动构造建议加 `noexcept`，否则标准库容器（如 `vector` 扩容）在某些情况下会退回到拷贝。

### 3. 转发引用与引用折叠（进阶）

在模板中，`T&&` 且 `T` 是被推导出来的时，叫做**转发引用**（万能引用），既能接收左值也能接收右值：

```cpp
template <typename T>
void wrapper(T&& value) {
    target(std::forward<T>(value)); // 完美转发，保留原始值类别
}
```

引用折叠规则：

```text
T&  + &  → T&
T&  + && → T&
T&& + &  → T&
T&& + && → T&&
```

概括：只要出现左值引用 `&`，结果就是左值引用；两个都是 `&&` 才是右值引用。

### 4. 指针与引用的区别

| 对比项 | 指针 | 引用 |
|---|---|---|
| 是否可以为空 | 可以，用 `nullptr` | 设计上应始终绑定有效对象 |
| 是否可以重新指向 | 可以 | 通常不能重新绑定 |
| 使用方式 | 需要解引用 | 直接使用 |
| 是否有指针运算 | 有 | 没有 |
| 是否必须初始化 | 不强制 | 必须初始化 |
| 常见用途 | 可选对象、数组遍历、所有权表达 | 参数传递、对象别名、多态接口 |

> 引用底层通常通过指针实现，但这是常见实现方式，不应把引用简单等同于指针；语言层面的语义不同。

---

## 四、数组

### 1. C 风格数组

```cpp
int numbers[4] = {1, 2, 3, 4};
int matrix[2][3] = {{1, 2, 3}, {4, 5, 6}};
```

特点：

- 长度通常在编译期确定。
- 元素连续存储。
- 不记录自己的长度。
- 不能直接整体赋值或比较。
- 访问下标不做边界检查，越界是未定义行为。

### 2. `std::array`

`std::array` 是固定长度容器，保留数组的连续存储特性，同时提供 `size()`、迭代器和 `at()` 等接口。

```cpp
#include <array>

std::array<int, 3> numbers{1, 2, 3};
numbers.at(0) = 10;    // 越界时抛出 std::out_of_range
numbers[0] = 10;       // 不做边界检查，更快
std::size_t n = numbers.size();
```

相比 C 数组，`std::array` 知道自己的长度，可以整体拷贝、能安全传参，推荐优先使用。

### 3. `std::vector`

需要动态长度时通常使用 `std::vector`：

```cpp
#include <vector>

std::vector<int> values;
values.push_back(1);
values.emplace_back(2); // 就地构造，避免临时对象
```

`vector` 的元素连续存储。扩容可能重新分配内存，使原有指针、引用和迭代器失效；`reserve()` 可提前预留容量，`size()` 是元素数量，`capacity()` 是当前容量。

```cpp
std::vector<int> v;
v.reserve(100); // 预留 100 个元素空间，减少扩容次数

int* p = &v[0];
v.push_back(1); // 可能触发扩容，之前的 p 可能失效
```

常见操作：

```cpp
v.size();      // 元素个数
v.empty();     // 是否为空
v.front();     // 第一个元素
v.back();      // 最后一个元素
v.clear();     // 清空
v.erase(it);   // 删除某个位置
```

---

## 五、字符串

### 1. C 风格字符串

C 风格字符串是以 `\0` 结尾的字符数组：

```cpp
char text[] = "hello"; // 实际占 6 个字节，包含结尾的 '\0'
```

使用 `strlen`、`strcpy` 等函数时必须确保目标空间足够，否则可能发生缓冲区溢出。

字符串字面量类型通常是 `const char[N]`，不能修改：

```cpp
const char* text = "hello";
// text[0] = 'H'; // 未定义行为
```

### 2. `std::string`

现代 C++ 优先使用 `std::string`，它自动管理内存：

```cpp
#include <string>

std::string text = "hello";
text += " world";
text.size();
text.find("world");
text.substr(0, 5);
text.empty();
```

注意：

- `size()` 返回字符数量，不一定等于用户感知的字符数；UTF-8 中文等字符可能占多个字节。
- `c_str()` 返回以 `\0` 结尾的只读 C 风格字符串指针。
- 修改字符串或使其析构后，之前保存的 `c_str()` 指针可能失效。
- `operator[]` 通常不做越界检查，`at()` 会检查越界并可能抛出异常。

### 3. `std::string_view`（C++17）

`string_view` 只是字符串的非拥有视图，不负责管理底层内存，也不复制字符：

```cpp
#include <string_view>

void print(std::string_view text) {
    // 不发生字符串拷贝，读取效率高
}

print("hello");           // 可接收字面量
std::string s = "world";
print(s);                 // 也可接收 std::string
```

使用时必须保证被观察的字符串在 `string_view` 使用期间仍然存活，不能从临时字符串或已销毁字符串中返回长期有效的 `string_view`：

```cpp
std::string_view bad() {
    std::string local = "temp";
    return local; // 危险：返回后 local 已销毁，view 悬空
}
```

---

## 六、函数

### 1. 函数声明与定义

```cpp
int add(int a, int b); // 声明

int add(int a, int b) { // 定义
    return a + b;
}
```

函数声明让编译器知道函数的名称、参数和返回类型；定义提供具体实现。每个函数定义都是声明，但声明不一定是定义。

**什么时候需要单独声明？** 编译器处理到某次调用时，必须已经见过该函数的声明或定义。因此需要声明的典型场景：

1. 函数定义写在调用位置之后。
2. 函数定义在另一个 `.cpp` 文件中（用头文件提供声明）。
3. 两个函数需要互相调用（至少提前声明其中一个）。

```cpp
void second();       // 提前声明

void first() {
    second();        // 因为已有声明，可以调用
}

void second() {
    // ...
}
```

声明中的参数名可以省略，定义中通常需要参数名：

```cpp
int add(int, int);          // 声明，参数名可省
int add(int a, int b) {     // 定义，需要参数名
    return a + b;
}
```

### 2. 参数传递

- **值传递**：复制实参，函数内修改不影响原对象。
- **指针传递**：传递地址，可以通过指针修改对象，也可以表示空值。
- **引用传递**：传递对象别名，不产生对象拷贝，通常不能为空。
- **常量引用传递**：适合传递较大对象且不修改对象，最常用。
- **右值引用传递**：用于移动和完美转发。

```cpp
void byValue(std::string text);          // 复制
void byPointer(std::string* text);       // 传地址，可为空
void byReference(std::string& text);     // 别名，可修改
void readOnly(const std::string& text);  // 只读，不复制
```

选择建议：小对象（如 `int`）用值传递；大对象只读用 `const T&`；需要修改原对象用 `T&`；可能为空用指针。

### 3. 函数重载

同一作用域中函数名相同，但参数列表不同，可以构成重载：

```cpp
void print(int value);
void print(double value);
void print(const std::string& value);
```

仅返回值不同**不能**构成重载。`const` 成员函数与非 `const` 成员函数可以构成重载。

### 4. 默认参数与可变参数模板

默认参数必须从右向左连续提供：

```cpp
void connect(const std::string& host, int port = 80, bool secure = false);

connect("example.com");            // 使用默认 port 和 secure
connect("example.com", 8080);      // 指定 port
```

C++11 可使用可变参数模板，接收任意数量、任意类型的参数：

```cpp
template <typename... Args>
void log(Args&&... args) {
    // args 是函数参数包
}
```

拆解说明：

- `typename... Args`：**模板参数包**，代表零个或多个类型。
- `Args&&... args`：**函数参数包**，为每个类型声明对应参数；这里 `Args&&` 是转发引用。
- `sizeof...(Args)`：获取参数个数。
- `表达式...`：参数包展开。

C++17 可以用折叠表达式处理参数包：

```cpp
template <typename... Args>
auto sum(Args... args) {
    return (args + ...); // 折叠展开为 arg1 + arg2 + ... + argN
}

template <typename... Args>
void print(Args&&... args) {
    ((std::cout << std::forward<Args>(args) << ' '), ...);
    std::cout << '\n';
}
```

C++11/14 没有折叠表达式，通常用递归展开：

```cpp
void print() { std::cout << '\n'; } // 终止函数

template <typename T, typename... Rest>
void print(T&& first, Rest&&... rest) {
    std::cout << std::forward<T>(first) << ' ';
    print(std::forward<Rest>(rest)...); // 逐个处理剩余参数
}
```

### 5. Lambda 表达式

```cpp
int factor = 2;
auto multiply = [factor](int value) {
    return factor * value;
};

multiply(10); // 20
```

捕获方式：

- `[x]`：按值捕获 `x`。
- `[&x]`：按引用捕获 `x`。
- `[=]`：按值捕获使用到的外部变量。
- `[&]`：按引用捕获使用到的外部变量。
- `[this]`：捕获当前对象指针。
- `[x = expr]`：C++14 起支持初始化捕获。

注意 Lambda 按引用捕获时，必须保证被捕获对象的生命周期足够长，否则调用时会访问已销毁的对象。

```cpp
std::vector<int> v{3, 1, 2};
std::sort(v.begin(), v.end(), [](int a, int b) {
    return a > b; // 降序
});
```

### 6. `const` 成员函数

只读取对象数据、不修改对象状态的成员函数，应在参数列表后加 `const`：

```cpp
class User {
private:
    int id_;
    std::string name_;

public:
    int id() const {                    // 查询，加 const
        return id_;
    }

    const std::string& name() const {   // 查询，加 const
        return name_;
    }

    void setName(const std::string& name) { // 修改，不加 const
        name_ = name;
    }
};
```

关键规则：

- `const` 成员函数中不能修改普通成员变量，也不能调用非 `const` 成员函数。
- `const` 对象、`const` 引用、指向 `const` 的指针，只能调用 `const` 成员函数。

| 对象 | 调用 `const` 成员函数 | 调用非 `const` 成员函数 |
|---|---:|---:|
| 普通对象 | 可以 | 可以 |
| `const` 对象 / `const` 引用 | 可以 | 不可以 |

函数参数常用 `const T&`，所以查询类函数一定要加 `const`，否则无法被调用：

```cpp
void show(const User& user) {
    std::cout << user.name(); // name() 必须是 const 成员函数
}
```

简单记忆：

```cpp
int age() const;       // 查询数据，末尾加 const
void setAge(int age);  // 修改数据，不加 const
```

---

## 七、类与对象

### 1. 类的基本组成

类可以包含：数据成员、成员函数、构造函数和析构函数、访问控制符、静态成员、类型别名、嵌套类型和友元等。

```cpp
class Student {
private:
    std::string name_;
    int age_{};   // 默认初始化为 0

public:
    Student(std::string name, int age)
        : name_(std::move(name)), age_(age) {}

    const std::string& name() const {
        return name_;
    }

    int age() const {
        return age_;
    }
};
```

逐处语法说明：

- `class Student { ... };`：类定义，末尾分号不能省。
- `private:` / `public:`：访问控制区域。私有成员只能在类内访问。
- `int age_{};`：成员默认初始化，`{}` 把 `age_` 初始化为 `0`。
- `Student(std::string name, int age)`：构造函数，函数名与类名相同，没有返回类型。
- `: name_(std::move(name)), age_(age)`：成员初始化列表，用参数初始化成员（这里用圆括号）。
- `std::move(name)`：把参数 `name` 的资源移动给成员 `name_`，避免拷贝。
- 结尾的 `{}`：空的构造函数体。

注意区分两种括号：

```cpp
int age_{};   // 花括号：默认初始化成员为 0
age_(age)     // 圆括号：初始化列表中用参数初始化成员
```

### 2. 构造、析构与初始化列表

- 构造函数在对象创建时初始化对象。
- 析构函数在对象生命周期结束时释放资源。
- 成员初始化顺序由成员在类中的**声明顺序**决定，而不是初始化列表中的书写顺序。
- `const` 成员、引用成员和没有默认构造函数的成员必须使用初始化列表初始化。

```cpp
class Example {
private:
    int first_;
    int second_;

public:
    Example(int first, int second)
        : first_(first), second_(second) {}
};
```

初始化列表比在函数体内赋值更高效：函数体内赋值是“先默认构造，再赋值”，初始化列表是“直接构造”。

### 3. `explicit`

单参数构造函数可能参与隐式类型转换，通常应使用 `explicit` 避免意外转换：

```cpp
class Number {
public:
    explicit Number(int value);
};

Number n1(10);   // 正确
// Number n2 = 10; // explicit 后禁止这种隐式转换
```

### 4. `static` 成员

静态数据成员属于类，而不是某一个对象；静态成员函数没有 `this` 指针，不能直接访问非静态成员，也不能加末尾的 `const`。

```cpp
class Counter {
private:
    static int count_; // 声明
public:
    static int count() { return count_; } // 静态成员函数
};

int Counter::count_ = 0; // 类外定义
```

### 5. 特殊成员函数与 Rule of 0/3/5

特殊成员函数包括：默认构造函数、析构函数、拷贝构造函数、拷贝赋值运算符、移动构造函数、移动赋值运算符。

如果类自己管理资源，通常需要关注拷贝、移动和析构的正确性：

- **Rule of 3**：自定义析构、拷贝构造或拷贝赋值之一时，通常需要同时考虑另外两个。
- **Rule of 5**：C++11 后还要考虑移动构造和移动赋值。
- **Rule of 0**：优先使用标准库资源管理类（如智能指针、`vector`、`string`），让编译器生成特殊成员函数，减少手写资源管理代码。这是最推荐的做法。

### 6. `= default` 与 `= delete`

```cpp
class NonCopyable {
public:
    NonCopyable() = default;                            // 请求默认实现
    NonCopyable(const NonCopyable&) = delete;           // 禁止拷贝
    NonCopyable& operator=(const NonCopyable&) = delete;// 禁止拷贝赋值
};
```

`= default` 表示请求编译器生成默认实现；`= delete` 表示明确禁止某个函数被调用。

---

## 八、面向对象核心

### 1. 封装

封装是把数据和操作数据的方法组织在类中，并通过访问权限隐藏实现细节、保护对象状态。

```cpp
class Account {
private:
    double balance_{};

public:
    bool deposit(double amount) {
        if (amount <= 0) {
            return false;
        }
        balance_ += amount;
        return true;
    }

    double balance() const {
        return balance_;
    }
};
```

常见访问权限：

- `public`：类外可访问，构成对外接口。
- `protected`：类内和派生类可访问。
- `private`：只有类内和友元可访问。

封装的价值：保护不变量（如余额不能被随意设为负数）、隐藏实现、降低耦合、便于后续修改。

### 2. 继承

继承表示派生类基于基类扩展功能，适合表达稳定的 `is-a` 关系：

```cpp
class Animal {
public:
    void eat() {}
};

class Dog : public Animal {
public:
    void bark() {}
};

Dog dog;
dog.eat();  // 继承自 Animal
dog.bark();
```

`public` 继承下：基类 `public` 成员在派生类中仍为 `public`，基类 `protected` 成员仍为 `protected`，基类 `private` 成员不能被派生类直接访问。

继承的注意点：

- 基类的 `private` 成员仍属于基类子对象，但派生类不能直接访问。
- 继承会建立较强耦合，不能仅为了复用少量代码而滥用。
- `has-a` 关系通常使用组合，例如 `Car` 拥有一个 `Engine`。
- 面向接口编程时，常见做法是使用抽象基类定义统一接口。

组合示例（优先于继承）：

```cpp
class Engine {};

class Car {
private:
    Engine engine_; // 组合：Car has-a Engine
};
```

### 3. 多态

多态指同一个接口在不同对象上表现出不同的行为。

- 编译期多态：函数重载、运算符重载、模板。
- 运行期多态：继承、虚函数、基类指针或引用。

```cpp
#include <iostream>

class Animal {
public:
    virtual void speak() const {
        std::cout << "Animal" << '\n';
    }

    virtual ~Animal() = default;
};

class Dog : public Animal {
public:
    void speak() const override {
        std::cout << "Dog" << '\n';
    }
};

void makeSpeak(const Animal& animal) {
    animal.speak();
}

Dog dog;
makeSpeak(dog); // 调用 Dog::speak()
```

运行期多态的关键条件：

1. 存在继承关系；
2. 基类成员函数声明为 `virtual`；
3. 派生类重写该虚函数；
4. 通过基类指针或引用调用。

### 4. 虚函数、`override` 与 `final`

```cpp
class Base {
public:
    virtual void run();
};

class Derived : public Base {
public:
    void run() override;
};
```

- `virtual` 开启虚函数机制，使调用可以动态绑定。
- `override` 明确表示派生类要重写基类虚函数；如果签名不匹配（例如漏写 `const`），编译器会报错。
- `final` 可以禁止继续重写或继续继承。

```cpp
class Child final : public Base {}; // Child 不能再被继承
```

如果没有 `virtual`：

```cpp
Base* p = new Derived;
p->run(); // 按静态类型绑定，通常调用 Base::run()
```

有 `virtual` 时，调用会根据对象的动态类型选择 `Derived::run()`。

### 5. 虚函数表与对象模型

C++ 标准没有规定虚函数必须如何实现，但主流编译器通常使用：

- `vtable`：虚函数表，保存虚函数入口信息；
- `vptr`：对象中的隐藏指针，指向对应的虚函数表。

可粗略理解为：

```text
含虚函数的对象：
+----------------+
| vptr           | ----> 对应类型的 vtable
+----------------+
| 非静态成员变量 |
+----------------+
```

当基类指针指向派生类对象并调用虚函数时，大致过程是：

```text
基类指针
  -> 对象中的 vptr
  -> 派生类 vtable
  -> 派生类重写的虚函数
```

因此：

- 含虚函数的对象通常会额外占用一个虚函数指针的空间；
- 虚函数调用通常需要间接查表，可能影响内联和性能；
- 具体布局、`vptr` 位置和 `vtable` 细节依赖编译器和 ABI，不能把常见实现当成语言标准保证。

成员函数代码通常在代码区共享，不会为每个对象保存一份；成员函数调用会隐式传入当前对象的 `this` 指针。

### 6. 虚析构函数

如果类可能通过基类指针删除派生类对象，基类析构函数应声明为虚函数：

```cpp
class Base {
public:
    virtual ~Base() = default;
};

class Derived : public Base {
public:
    ~Derived() override = default;
};

Base* object = new Derived;
delete object; // 先调用 Derived 析构，再调用 Base 析构
```

否则通过 `Base*` 删除 `Derived` 对象可能只调用基类析构函数，导致派生类资源没有正确释放。

### 7. 纯虚函数与抽象类

纯虚函数使用 `= 0` 声明：

```cpp
class Shape {
public:
    virtual double area() const = 0;
    virtual ~Shape() = default;
};

class Circle : public Shape {
private:
    double r_;
public:
    explicit Circle(double r) : r_(r) {}
    double area() const override {
        return 3.1415926 * r_ * r_;
    }
};
```

包含纯虚函数的类是抽象类，不能直接实例化；派生类需要实现所有纯虚函数，才可以成为具体类。抽象类常用于定义接口。

### 8. 构造、析构期间的虚函数

构造基类部分时，派生类部分尚未构造完成；析构基类部分时，派生类部分已经销毁。因此在构造函数或析构函数中调用虚函数，不会产生通常意义上的“调用最底层派生类重写版本”，而是按当前正在构造或析构的类进行调用。

实践中不要依赖构造或析构期间的虚函数多态。

### 9. 对象切片

将派生类对象按值赋给基类对象，会只保留基类子对象部分：

```cpp
class Base {
public:
    int baseValue{};
};

class Derived : public Base {
public:
    int derivedValue{};
};

Derived derived;
Base base = derived; // 发生对象切片，derivedValue 被截断
```

为了保留多态行为，应使用基类引用或指针：

```cpp
Base& reference = derived;
Base* pointer = &derived;
```

---

## 九、对象模型与内存布局要点

### 1. 非静态成员变量

每个对象通常都有自己独立的非静态成员变量；静态成员属于类，不随每个对象重复存储。

### 2. 成员函数与 `this`

成员函数代码通常由同一类的对象共享，调用时隐式传入 `this` 指针：

```cpp
class Counter {
private:
    int value_{};

public:
    void set(int value) {
        this->value_ = value; // this 指向调用该函数的对象
    }
};
```

可以近似理解为 `counter.set(10)` 变成 `set(&counter, 10)`。

### 3. 继承对象

派生类对象通常包含一个基类子对象：

```text
Derived 对象：
+----------------+
| Base 子对象    |
+----------------+
| Derived 成员   |
+----------------+
```

因此派生类对象可以转换为基类指针或引用。多重继承、虚继承会使布局更复杂。

### 4. 对象大小

`sizeof` 受到成员变量、对齐与填充、虚函数机制、继承方式等影响。空类的大小通常不为 0，以保证不同对象具有不同地址；但具体大小应以编译器实际结果为准。含虚函数的类通常会因 `vptr` 增加一个指针大小。

---

## 十、秋招高频问答速记

### 1. 封装、继承、多态分别解决什么问题？

- 封装：隐藏实现，保护状态，降低耦合。
- 继承：表达 `is-a` 关系，复用和扩展接口。
- 多态：统一接口对应不同实现，提高可扩展性。

### 2. C++ 运行时多态如何实现？

通过继承和虚函数，使用基类指针或引用指向派生类对象，再调用虚函数进行动态绑定。主流实现通常依赖对象中的 `vptr` 和类对应的 `vtable`。

### 3. 为什么基类析构函数常常要声明为虚函数？

为了通过基类指针删除派生类对象时，能够先调用派生类析构函数，再调用基类析构函数，避免资源泄漏。

### 4. 成员函数是否占对象大小？

成员函数代码通常由同类对象共享，不会为每个对象单独保存；非静态成员变量会影响对象大小。含虚函数的类通常还会因为 `vptr` 增加对象大小。

### 5. 什么是对象切片？

派生类对象按值转换为基类对象时，派生类新增部分被截断。使用基类引用或指针可以避免切片。

### 6. `override` 有什么作用？

告诉编译器该函数必须重写基类虚函数。如果函数签名不匹配，编译器会报错，能够避免误写成新的普通函数。

### 7. 组合和继承如何选择？

稳定的 `is-a` 关系可以考虑继承；`has-a` 关系和实现复用通常优先组合。一般建议优先使用组合，避免不必要的继承耦合。

### 8. `std::move` 真的会移动数据吗？

不会。`std::move` 只是把对象转换成右值引用，真正的资源转移发生在移动构造或移动赋值中。

### 9. `unique_ptr` 和 `shared_ptr` 如何选择？

默认用 `unique_ptr` 表达独占所有权；确实需要多方共享生命周期时才用 `shared_ptr`；观察但不拥有用 `weak_ptr`，也用来打破循环引用。

### 10. `const` 成员函数的作用？

承诺不修改对象普通状态，因此可以被 `const` 对象、`const` 引用调用。只读函数应尽量加 `const`。

---

## 十一、最终记忆框架

```text
现代 C++：用 C++11/14/17 特性提升安全性、表达力和效率，了解 C++20 的 Concepts、Ranges、span、协程等。

指针：保存地址，可为空，可重新指向；注意所有权、生命周期和悬空问题。
引用：对象别名，常用于参数传递；右值引用服务于移动语义和完美转发。

数组：连续存储；C 数组不保存长度，std::array 是固定长度容器，vector 是动态长度容器。
字符串：现代代码优先 std::string；string_view 不拥有内存，必须关注生命周期。
函数：理解参数传递、重载、const、Lambda、移动和完美转发。
类：掌握构造析构、初始化列表、访问控制、特殊成员函数和 RAII。

封装：隐藏实现，保护状态。
继承：表达 is-a，复用并扩展接口。
多态：同一接口，不同行为。
虚函数：运行时动态绑定的核心。
对象模型：成员变量、this、继承子对象、vptr/vtable、对象切片和内存布局。

RAII：资源生命周期绑定对象生命周期，是现代 C++ 资源管理的根基。
```
