# C++ 函数声明与类成员语法

> 本文整理函数声明、类成员初始化、默认构造函数、`const` 成员函数和 `static` 成员等常用语法，重点说明代码应该怎么写以及容易混淆的位置。

## 1. 什么时候需要函数声明

判断原则：

> 代码调用一个函数时，编译器在此之前必须已经见过该函数的声明或定义。

### 1.1 函数定义写在调用之后

```cpp
#include <iostream>

int add(int left, int right); // 提前声明函数接口

int main() {
    std::cout << add(1, 2) << '\n'; // 编译器已经知道 add 的签名
}

int add(int left, int right) {
    // 在后面提供函数定义
    return left + right;
}
```

声明告诉编译器函数名、返回类型和参数类型；定义还包含函数体。

```cpp
int add(int, int); // 只有声明，参数名可以省略

int add(int left, int right) {
    // 这是定义，同时也属于声明
    return left + right;
}
```

### 1.2 函数定义在其他源文件

常见项目结构：

```cpp
// math_utils.h
#pragma once

int add(int left, int right); // 头文件只暴露接口
```

```cpp
// math_utils.cpp
#include "math_utils.h"

int add(int left, int right) {
    // 源文件提供实现
    return left + right;
}
```

```cpp
// main.cpp
#include "math_utils.h"
#include <iostream>

int main() {
    std::cout << add(1, 2) << '\n'; // 通过头文件获得声明
}
```

每个 `.cpp` 文件通常独立编译，链接器再把调用与另一个目标文件中的定义连接起来。

### 1.3 函数互相调用

```cpp
bool isOdd(int value); // isEven 调用它之前先声明

bool isEven(int value) {
    // 递归终止条件
    return value == 0 ? true : isOdd(value - 1);
}

bool isOdd(int value) {
    // 调用前面已经定义的 isEven
    return value == 0 ? false : isEven(value - 1);
}
```

### 1.4 类内声明、类外定义

```cpp
#include <iostream>

class Student {
public:
    void introduce() const; // 类中声明成员函数
};

void Student::introduce() const {
    // 使用作用域解析符说明这是 Student 的成员函数
    std::cout << "Hello\n";
}
```

如果函数已经在使用位置之前完整定义，就不需要额外再声明一次。

---

## 2. 类定义的基本语法

```cpp
#include <string>
#include <utility>

class Student {
private:
    std::string name_; // 下划线只是成员变量命名习惯
    int age_{};        // 默认成员初始化：int 被初始化为 0

public:
    Student(std::string name, int age)
        : name_(std::move(name)), age_(age) {
        // 成员已在初始化列表中完成初始化，函数体可以为空
    }

    const std::string& name() const {
        // 返回只读引用，避免复制字符串
        return name_;
    }

    int age() const {
        // int 直接按值返回即可
        return age_;
    }
}; // 类定义结束后必须有分号
```

---

## 3. 三处容易混淆的括号

观察下面两行：

```cpp
int age_{}; // 第一处：默认成员初始化

Student(int age)
    : age_(age) {} // 第二处是圆括号初始化，第三处是空函数体
```

### 3.1 `int age_{};`

```cpp
int age_{};
```

表示使用空花括号进行值初始化。对于 `int`，结果是 `0`。

```cpp
int age_{18}; // 指定默认值为 18
```

这是类内默认成员初始化器：只有构造函数没有另外指定 `age_` 的初始值时，它才会生效。

### 3.2 `age_(age)`

```cpp
Student(int age)
    : age_(age) {
}
```

外层是圆括号，不是花括号。左边的 `age_` 是成员变量，圆括号中的 `age` 是构造函数参数：

```text
成员变量 age_ ← 使用参数 age 初始化
```

也可以写成花括号形式：

```cpp
Student(int age)
    : age_{age} {
    // age_{age} 是成员初始化，最后的花括号是函数体
}
```

### 3.3 最后的 `{}`

```cpp
Student(int age)
    : age_(age) {}
```

最后的 `{}` 是构造函数体。因为没有额外逻辑，所以函数体为空。

### 3.4 哪个初始值优先

```cpp
class Student {
private:
    int age_{0}; // 构造函数没有指定时使用

public:
    explicit Student(int age)
        : age_(age) { // 当前构造函数明确指定，因此使用参数值
    }
};
```

`Student student(18);` 创建后，`age_` 是 `18`，不是 `0`。

---

## 4. 什么叫“没有默认构造函数的成员”

### 4.1 默认构造函数

可以不提供参数就调用的构造函数叫默认构造函数：

```cpp
class Engine {
public:
    Engine() {
        // 不接收参数，因此可以默认构造
    }
};

Engine engine; // 正确，调用 Engine()
```

带默认实参且可以无参数调用的构造函数，也能作为默认构造函数使用。

### 4.2 没有默认构造函数的类型

```cpp
class Engine {
private:
    int power_{};

public:
    explicit Engine(int power)
        : power_(power) {
        // 只能提供功率后构造
    }
};
```

这个类只能写：

```cpp
Engine engine(150); // 正确
```

不能写：

```cpp
// Engine engine; // 错误：不存在 Engine()
```

因此，类型 `Engine` 没有默认构造函数。

### 4.3 类含有这种成员时必须明确初始化

```cpp
class Car {
private:
    Engine engine_; // Engine 不能无参数构造

public:
    Car()
        : engine_(150) {
        // 必须在成员初始化列表中调用 Engine(int)
    }
};
```

如果省略初始化列表：

```cpp
class Car {
private:
    Engine engine_;

public:
    Car() {
        // 错误：进入函数体前，编译器会尝试调用 Engine()
    }
};
```

成员是在进入构造函数体之前完成初始化的。不能先让成员“不初始化”，进入函数体后再补做一次构造。

下面看似赋值的写法也不能解决问题：

```cpp
class Car {
private:
    Engine engine_;

public:
    Car() {
        // 在执行到这里之前，engine_ 就必须已经构造完成
        // engine_ = Engine(150);
    }
};
```

必须写成：

```cpp
Car()
    : engine_(150) {
}
```

同样必须使用初始化列表的典型成员还有：

- 引用成员；
- `const` 数据成员；
- 没有默认构造函数的类类型成员；
- 需要调用特定基类构造函数的基类子对象。

```cpp
class Record {
private:
    const int id_;
    int& value_;

public:
    Record(int id, int& value)
        : id_(id), value_(value) {
        // const 成员和引用成员必须直接初始化
    }
};
```

---

## 5. 成员初始化顺序

成员按照它们在类中的声明顺序初始化，而不是初始化列表的书写顺序。

```cpp
class Example {
private:
    int first_;
    int second_;

public:
    Example()
        : first_(1), second_(2) {
        // 书写顺序与声明顺序保持一致，便于阅读和检查
    }
};
```

不要依赖颠倒的初始化列表：

```cpp
Example()
    : second_(2), first_(1) {
    // 实际仍先初始化 first_，再初始化 second_
}
```

推荐始终让初始化列表顺序与成员声明顺序一致。

---

## 6. `const` 成员函数的用法

### 6.1 基本语法

```cpp
返回类型 函数名(参数列表) const;
```

例如：

```cpp
class Student {
private:
    int age_{};

public:
    int age() const {
        // 只读取成员，不修改对象状态
        return age_;
    }

    void setAge(int age) {
        // 修改对象状态，因此不加末尾 const
        age_ = age;
    }
};
```

用法规则：

- 查询、打印等只读成员函数通常加 `const`；
- 修改对象状态的成员函数不加末尾 `const`；
- 普通对象可以调用两种成员函数；
- `const` 对象或 `const` 引用只能调用 `const` 成员函数。

```cpp
void showStudent(const Student& student) {
    // const 引用只能调用 const 成员函数
    std::cout << student.age() << '\n';
}
```

### 6.2 `const` 与非 `const` 重载

```cpp
#include <cstddef>
#include <vector>

class Buffer {
private:
    std::vector<int> data_;

public:
    int& operator[](std::size_t index) {
        // 普通对象获得可修改引用
        return data_[index];
    }

    const int& operator[](std::size_t index) const {
        // const 对象只能获得只读引用
        return data_[index];
    }
};
```

---

## 7. 静态数据成员

普通数据成员属于具体对象，每个对象各有一份；静态数据成员属于整个类，所有对象共享一份。

### 7.1 C++17 推荐写法

```cpp
class Student {
private:
    inline static int count_{0}; // 整个 Student 类共享一份

public:
    Student() {
        ++count_; // 每创建一个对象就增加计数
    }

    ~Student() {
        --count_; // 每销毁一个对象就减少计数
    }

    static int count() {
        // 静态函数可以直接访问静态数据成员
        return count_;
    }
};
```

访问时优先使用类名：

```cpp
int current = Student::count(); // 不需要创建对象即可调用
```

C++17 之前常见写法是在类内声明、类外定义：

```cpp
class Student {
public:
    static int count_; // 类内声明
};

int Student::count_ = 0; // 类外定义，不再写 static
```

### 7.2 静态成员仍受访问控制

`static` 表示成员属于类，不等于 `public`。私有静态成员在类外仍不能直接访问，通常通过公开静态函数提供接口。

---

## 8. 静态成员函数

```cpp
class Student {
private:
    int age_{};
    inline static int count_{0};

public:
    static int count() {
        // 正确：静态函数可以直接访问静态成员
        return count_;
    }

    static int readAge(const Student& student) {
        // 通过明确传入的对象访问非静态成员
        return student.age_;
    }
};
```

静态成员函数的特点：

1. 可以通过 `类名::函数名()` 调用；
2. 没有当前对象，因此没有 `this` 指针；
3. 可以直接访问静态成员；
4. 不能直接访问某个对象的非静态成员；
5. 如果参数提供了具体对象，可以通过该对象访问普通成员；
6. 函数末尾不能添加成员函数 `const`。

错误示例：

```cpp
class Example {
private:
    int value_{};

public:
    static int value() {
        // return value_; // 错误：不知道要访问哪个对象的 value_
        return 0;
    }

    // static int count() const; // 错误：静态函数没有当前对象
};
```

静态函数的参数和返回类型仍然可以使用普通的 `const`：

```cpp
static void print(const Student& student) {
    // 这里的 const 修饰参数，不是修饰静态成员函数
}
```

---

## 9. 综合示例

```cpp
#include <iostream>
#include <string>
#include <utility>

class Student {
private:
    std::string name_;
    int age_{};
    inline static int count_{0};

public:
    Student(std::string name, int age)
        : name_(std::move(name)), age_(age) {
        ++count_; // 统计当前对象数量
    }

    ~Student() {
        --count_; // 对象销毁时减少计数
    }

    const std::string& name() const {
        // 返回成员的只读引用
        return name_;
    }

    int age() const {
        // 查询函数使用 const
        return age_;
    }

    void setAge(int age) {
        // 修改函数不使用末尾 const
        age_ = age;
    }

    static int count() {
        // 返回类共享的对象计数
        return count_;
    }
};

int main() {
    Student first("Alice", 18);
    Student second("Bob", 20);

    std::cout << first.name() << ' ' << first.age() << '\n';
    std::cout << Student::count() << '\n';
}
```

---

## 10. 速记

```text
函数声明：调用前必须让编译器知道函数签名
int age_{}：成员默认初始化为 0
age_(age)：用参数 age 初始化成员 age_
最后的 {}：构造函数体
没有默认构造函数的成员：不能无参数构造，必须在初始化列表中明确初始化
const 成员函数：只读接口，const 对象可以调用
static 数据成员：属于类，所有对象共享
static 成员函数：没有 this，不能直接访问非静态成员
```

## 11. 相关笔记与来源说明

- [C++ 语言基础与面向对象总结](C++语言基础与面向对象总结.md)
- [C++ 面向对象、虚函数与对象模型](C++面向对象、虚函数与对象模型.md)
- [RAII、异常安全与资源生命周期](RAII、异常安全与资源生命周期.md)

本文根据本次会话中的函数声明、类初始化、`const` 与 `static` 成员等讲解整理，并补充了“没有默认构造函数的成员”的完整说明。
