# C++ 面向对象、虚函数与对象模型

> 本文系统整理 C++ 面向对象中的封装、继承、多态、虚函数和对象模型。重点是理解各概念解决的问题、常见写法及面试高频点。

## 1. 总体关系

```text
封装：把数据与操作组织在类中，隐藏实现并保护对象状态
继承：表达稳定的 is-a 关系，复用或扩展基类接口
多态：通过统一接口，让不同对象表现出不同的行为
虚函数：C++ 实现运行时多态的主要语言机制
对象模型：解释对象、成员、继承和虚函数在底层如何组织
```

---

## 2. 封装

封装是把数据和操作数据的方法放进类中，并使用访问权限控制外部能够接触的内容。

```cpp
class Account {
private:
    double balance_{0.0}; // 私有数据，只允许类内部直接访问

public:
    bool deposit(double amount) {
        // 通过公开接口维护“存款必须为正数”的约束
        if (amount <= 0.0) {
            return false;
        }

        balance_ += amount;
        return true;
    }

    double balance() const {
        // 查询函数只读取状态，因此声明为 const
        return balance_;
    }
};
```

访问权限：

| 权限 | 类外 | 派生类 | 当前类及友元 |
|---|---:|---:|---:|
| `public` | 可以 | 可以 | 可以 |
| `protected` | 不可以 | 可以 | 可以 |
| `private` | 不可以 | 不可以直接访问 | 可以 |

封装的主要价值：

1. 保护类的不变量，例如余额不能被任意设为非法值；
2. 隐藏实现细节，外部只依赖稳定接口；
3. 降低模块耦合，方便以后修改内部实现；
4. 集中进行参数校验、日志记录和状态维护。

> 封装不只是“把成员变量写成 `private`”，更重要的是通过公开接口维护对象始终处于合法状态。

---

## 3. 继承与组合

### 3.1 继承表达 is-a 关系

```cpp
class Animal {
public:
    void eat() const {
        // 基类提供所有动物共有的行为
    }
};

class Dog : public Animal {
public:
    void bark() const {
        // 派生类增加自己的行为
    }
};
```

`Dog` 对象中包含一个 `Animal` 基类子对象，因此可以使用基类的公开接口。

```cpp
Dog dog;
dog.eat();  // 调用从 Animal 继承的接口
dog.bark(); // 调用 Dog 自己的接口
```

### 3.2 公有继承下的访问权限

| 基类成员权限 | 在派生类中的权限 |
|---|---|
| `public` | `public` |
| `protected` | `protected` |
| `private` | 派生类不能直接访问 |

基类的 `private` 成员仍然存在于基类子对象中，只是派生类不能直接访问，通常要通过基类的 `public` 或 `protected` 接口操作。

### 3.3 优先考虑组合

继承适合稳定的 is-a 关系；组合适合 has-a 关系。

```cpp
class Engine {
public:
    void start() {
        // 启动发动机
    }
};

class Car {
private:
    Engine engine_; // Car 拥有 Engine，属于 has-a 关系

public:
    void start() {
        engine_.start(); // 通过组合复用功能
    }
};
```

组合通常比继承耦合更低。不要仅仅为了复用几行代码就建立继承关系。

---

## 4. 多态

多态表示同一个接口可以根据对象类型表现出不同的行为。

### 4.1 编译期多态

编译期就能确定具体调用，例如：

- 函数重载；
- 运算符重载；
- 函数模板和类模板。

```cpp
void print(int value) {
    // 处理整数
}

void print(double value) {
    // 处理浮点数
}
```

### 4.2 运行时多态

运行时多态通常需要同时满足：

1. 存在继承关系；
2. 基类声明虚函数；
3. 派生类重写虚函数；
4. 通过基类指针或引用调用虚函数。

```cpp
#include <iostream>

class Animal {
public:
    virtual void speak() const {
        std::cout << "Animal speaks\n";
    }

    virtual ~Animal() = default; // 多态基类使用虚析构函数
};

class Dog final : public Animal {
public:
    void speak() const override {
        std::cout << "Dog barks\n";
    }
};

void makeSound(const Animal& animal) {
    // 运行时根据实际对象类型选择虚函数实现
    animal.speak();
}

int main() {
    Dog dog;
    makeSound(dog); // 输出 Dog barks
}
```

这里 `makeSound()` 的形参类型是 `const Animal&`，但它实际引用的是 `Dog` 对象，因此调用 `Dog::speak()`。

### 4.3 静态类型与动态类型

```cpp
Dog dog;
Animal* pointer = &dog;
```

- `pointer` 的静态类型是 `Animal*`，编译时已知；
- `pointer` 指向对象的动态类型是 `Dog`，运行时确定；
- 调用虚函数时根据动态类型选择实现；
- 调用非虚函数时通常根据静态类型绑定。

---

## 5. 虚函数

### 5.1 `virtual`、`override` 和 `final`

```cpp
class Base {
public:
    virtual void run() const {
        // 基类默认实现
    }

    virtual ~Base() = default;
};

class Derived : public Base {
public:
    void run() const override {
        // override 让编译器检查是否真的完成了重写
    }
};
```

- `virtual`：声明函数支持动态绑定；
- `override`：明确表示重写基类虚函数，并请求编译器检查签名；
- `final`：禁止类继续被继承，或禁止虚函数继续被重写。

`const` 是成员函数签名的一部分。基类是 `void run() const`，派生类漏掉 `const` 就不是同一个函数；使用 `override` 可以及时发现错误。

### 5.2 纯虚函数与抽象类

```cpp
class Shape {
public:
    virtual double area() const = 0; // 纯虚函数，只规定接口
    virtual ~Shape() = default;
};

class Circle : public Shape {
private:
    double radius_{};

public:
    explicit Circle(double radius)
        : radius_(radius) {
    }

    double area() const override {
        return 3.1415926 * radius_ * radius_;
    }
};
```

包含纯虚函数的类是抽象类，不能直接创建对象。派生类如果没有实现所有纯虚函数，它也仍然是抽象类。

### 5.3 虚析构函数

如果可能通过基类指针删除派生类对象，基类析构函数必须是虚函数：

```cpp
#include <memory>

class Base {
public:
    virtual ~Base() = default; // 确保按派生类到基类的顺序析构
};

class Derived : public Base {
private:
    std::unique_ptr<int> data_{std::make_unique<int>(42)};
};

int main() {
    std::unique_ptr<Base> object = std::make_unique<Derived>();
    // 离开作用域时会正确销毁 Derived 和 Base 部分
}
```

如果基类被设计为多态基类，通常应直接声明：

```cpp
virtual ~Base() = default;
```

### 5.4 构造和析构期间的虚函数调用

在基类构造函数中调用虚函数时，派生类部分尚未构造完成，因此不会分派到尚未完成的派生类实现。析构阶段同理，派生类部分已经先被销毁。

因此应避免依赖构造函数或析构函数中的虚函数调用来执行派生类行为。

---

## 6. 虚函数表与虚函数指针

主流编译器通常使用以下结构实现运行时多态：

- `vtable`：虚函数表，记录对应类的虚函数入口；
- `vptr`：对象中的隐藏指针，指向该对象动态类型对应的虚函数表。

```text
对象：
+----------------+
| vptr           | -----> 某个类的虚函数表
+----------------+        +------------------+
| 普通成员变量   |        | virtual function |
+----------------+        | virtual function |
                          +------------------+
```

派生类重写虚函数后，它的虚函数表对应槽位通常指向派生类实现。通过基类指针调用虚函数时，程序大致会：

1. 找到实际对象中的 `vptr`；
2. 通过 `vptr` 找到虚函数表；
3. 从对应槽位取得函数地址；
4. 调用实际类型对应的实现。

> C++ 标准规定的是虚函数的行为，不强制编译器必须采用 `vptr`/`vtable`，也不保证具体对象布局。以上是主流 ABI 和编译器的常见实现。

运行时多态通常会带来：

- 每个多态对象可能多一个指针大小的 `vptr`；
- 虚函数调用通常多一次间接寻址；
- 某些虚调用不容易内联，但编译器有时可以去虚化优化。

---

## 7. C++ 对象模型要点

### 7.1 对象中通常存什么

对象通常包含：

- 非静态数据成员；
- 对齐产生的填充字节；
- 多态类中编译器可能加入的 `vptr`；
- 继承关系中的基类子对象。

成员函数代码不会在每个对象中保存一份；静态数据成员也不属于某个具体对象。

```cpp
class Example {
public:
    int value_{};            // 每个对象各自保存一份
    inline static int count_ = 0; // 整个类共享一份

    void print() const {
        // 成员函数代码由所有对象共享
    }
};
```

不要简单地用成员大小相加推断 `sizeof`，还要考虑对齐、填充、继承和虚函数实现。

### 7.2 `this` 指针

非静态成员函数调用时会获得指向当前对象的隐含 `this` 指针：

```cpp
class Counter {
private:
    int value_{};

public:
    void setValue(int value) {
        this->value_ = value; // this 指向当前调用对象
    }
};
```

静态成员函数不依赖具体对象，因此没有 `this` 指针。

### 7.3 派生类对象包含基类子对象

```cpp
class Base {
public:
    int baseValue_{};
};

class Derived : public Base {
public:
    int derivedValue_{};
};
```

可概念化为：

```text
Derived 对象
+------------------+
| Base 基类子对象  |
| baseValue_       |
+------------------+
| derivedValue_    |
+------------------+
```

具体布局、偏移和虚继承实现由编译器 ABI 决定。

### 7.4 对象切片

把派生类对象按值复制给基类对象时，只保留基类子对象部分：

```cpp
class Base {
public:
    virtual ~Base() = default;
};

class Derived : public Base {
public:
    int extra_{};
};

void consume(Base object) {
    // 按值接收会切掉派生类部分
}

int main() {
    Derived derived;
    Base base = derived; // 发生对象切片
    consume(derived);    // 也会发生对象切片
}
```

需要保留多态时，应使用基类引用或智能指针：

```cpp
void consume(const Base& object) {
    // 引用不会创建新的 Base 对象，因此不会切片
}
```

---

## 8. 常见设计原则

1. 使用 `private` 成员和公开接口维护类的不变量；
2. 继承用于真正的 is-a 关系，代码复用优先考虑组合；
3. 重写虚函数时使用 `override`；
4. 多态基类通常提供虚析构函数；
5. 纯接口可使用抽象基类，但不要让基类暴露不必要的状态；
6. 通过基类引用或智能指针使用多态，避免对象切片；
7. 不依赖未被标准保证的对象内存布局；
8. 对拥有资源的类优先使用 RAII 成员。

---

## 9. 面试速记

> 封装通过访问控制隐藏实现并保护对象状态；继承表达 is-a 关系；多态允许统一接口根据对象实际类型表现出不同的行为。C++ 运行时多态主要通过虚函数、继承以及基类指针或引用实现，主流编译器通常使用 `vptr` 和 `vtable`。对象中主要保存非静态数据成员、必要的填充和编译器为多态加入的信息，成员函数代码不在每个对象中重复保存。多态基类应特别注意虚析构函数和对象切片。

## 10. 相关笔记与来源说明

- [C++ 语言基础与面向对象总结](C++语言基础与面向对象总结.md)
- [RAII、异常安全与资源生命周期](RAII、异常安全与资源生命周期.md)
- [C++ 深浅拷贝与拷贝控制](C++深浅拷贝与拷贝控制.md)

本文根据本次会话中的讲解整理；对象布局、`vptr` 和 `vtable` 部分属于主流编译器常见实现，C++ 标准不保证具体布局。
