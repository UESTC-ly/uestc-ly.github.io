# C++ 专题

---

## 1. C++ 继承

### 1.1 一句话抓本质
**继承的本质，就是“复用 + 扩展 + 多态”的基础机制。**

父类负责抽象出公共部分，子类在此基础上补充自己的特性。这样既能减少重复代码，也能让多个对象通过统一接口被处理。

---

### 1.2 为什么要用继承
继承解决的是“**多个类有共同特征，但又各自不同**”的问题。

例如：
- `Animal`：都有名字、年龄、吃饭行为
- `Dog` / `Cat`：都有动物的共性，但叫声、行为不同

如果不用继承，你可能会把公共代码复制很多份；如果用了继承，就可以把共性放进父类，把差异留给子类。

---

### 1.3 基本语法
```cpp
class Parent {
public:
    void hello() {
        cout << "hello" << endl;
    }
};

class Child : public Parent {
public:
    void world() {
        cout << "world" << endl;
    }
};
```

调用：
```cpp
Child c;
c.hello();
c.world();
```

---

### 1.4 继承的三种访问方式
C++ 里继承不仅是“继承”，还要指定**继承方式**：

```cpp
class A : public B   // 公有继承
class A : protected B // 保护继承
class A : private B   // 私有继承
```

#### （1）public 继承
- 父类 `public` 成员在子类中仍是 `public`
- 父类 `protected` 成员在子类中仍是 `protected`
- 最常用，表示“**is-a**”关系

#### （2）protected 继承
- 父类 `public` / `protected` 成员在子类中都变成 `protected`
- 外部不能直接通过子类对象访问
- 比较少用

#### （3）private 继承
- 父类的 `public` / `protected` 成员在子类中都变成 `private`
- 表示“用父类实现子类”，不是“子类是父类”
- 也比较少用

---

### 1.5 public / protected / private 访问规则

#### 公有继承下
| 父类成员 | 子类中可见性 |
|---|---|
| public | public |
| protected | protected |
| private | 不能直接访问 |

#### 重点理解
- `private` 不是“子类继承不到”，而是“子类不能直接访问”
- 父类的 `private` 成员仍然属于父类对象的一部分，只是对子类隐藏

---

### 1.6 一个完整示例
```cpp
#include <iostream>
using namespace std;

class Animal {
public:
    string name;

    Animal(string n) : name(n) {}

    void eat() {
        cout << name << " is eating" << endl;
    }
};

class Dog : public Animal {
public:
    Dog(string n) : Animal(n) {}

    void bark() {
        cout << name << " is barking" << endl;
    }
};

int main() {
    Dog d("Tom");
    d.eat();
    d.bark();
}
```

这个例子里：
- `Dog` 继承了 `Animal` 的属性和方法
- 子类构造函数通过初始化列表调用父类构造函数
- 继承让公共逻辑只写一次

---

### 1.7 构造函数和析构函数的调用顺序
继承体系里，构造和析构的顺序非常重要。

#### 构造顺序
**先父类，再子类**

#### 析构顺序
**先子类，再父类**

#### 原因
- 子类构造前，必须先把父类部分建好
- 子类析构时，先释放自己的资源，再释放父类资源

```cpp
class A {
public:
    A() { cout << "A ctor" << endl; }
    ~A() { cout << "A dtor" << endl; }
};

class B : public A {
public:
    B() { cout << "B ctor" << endl; }
    ~B() { cout << "B dtor" << endl; }
};
```

---

### 1.8 父类构造函数要先初始化
如果父类没有默认构造函数，子类必须在初始化列表里显式调用父类构造函数。

```cpp
class Base {
public:
    Base(int x) {}
};

class Derived : public Base {
public:
    Derived() : Base(10) {}
};
```

---

### 1.9 子类能做什么
子类通常有三种行为：
1. **继承**父类能力
2. **扩展**新能力
3. **重写**父类行为

例如：
```cpp
class Base {
public:
    void show() { cout << "Base" << endl; }
};

class Derived : public Base {
public:
    void extra() { cout << "Derived" << endl; }
};
```

---

### 1.10 函数重写（override）
如果子类重新定义了父类的同名成员函数，这叫**重写**（也常被叫做覆盖）。

```cpp
class Base {
public:
    virtual void speak() {
        cout << "Base speak" << endl;
    }
};

class Derived : public Base {
public:
    void speak() override {
        cout << "Derived speak" << endl;
    }
};
```

#### `override` 的好处
- 告诉编译器：我就是要重写父类函数
- 防止函数名写错、参数不一致导致“以为重写了，其实没有”

---

### 1.11 虚函数和多态
继承真正强大的地方，是和**虚函数**一起使用，形成**运行时多态**。

```cpp
class Animal {
public:
    virtual void sound() {
        cout << "animal sound" << endl;
    }
};

class Dog : public Animal {
public:
    void sound() override {
        cout << "woof" << endl;
    }
};
```

使用父类指针指向子类对象：
```cpp
Animal* p = new Dog();
p->sound();  // woof
```

#### 这说明了什么
- 编译时看的是父类类型
- 运行时执行的是实际对象类型
- 这就是动态绑定 / 运行时多态

---

### 1.12 纯虚函数和抽象类
如果父类只想规定“接口”，不想自己实现，可以写成纯虚函数。

```cpp
class Shape {
public:
    virtual double area() = 0;
};
```

这种类叫**抽象类**，特点是：
- 不能直接实例化
- 子类必须实现纯虚函数，才能成为可创建对象的类

#### 抽象类的作用
- 统一接口
- 强制子类实现核心行为
- 用于设计框架和规范

---

### 1.13 继承中的对象切片
对象切片（object slicing）是一个经典坑。

```cpp
class Base {
public:
    int x = 1;
};

class Derived : public Base {
public:
    int y = 2;
};

Derived d;
Base b = d;   // 切片
```

这里 `b` 只保留了 `Base` 部分，`Derived` 独有的部分被“切掉”了。

#### 为什么危险
- 会丢失子类信息
- 可能让你误以为对象还保留完整层次

#### 避免方式
- 尽量用引用或指针传递多态对象
- 不要轻易按值拷贝派生类到基类对象

---

### 1.14 基类指针和基类引用
多态场景里，推荐使用：
- `Base*`
- `Base&`

而不是按值传递。

```cpp
void play(Base& b) {
    b.sound();
}
```

这样可以保留对象的动态类型，避免切片。

---

### 1.15 虚析构函数很重要
如果父类会被当成基类指针使用，析构函数通常要写成 `virtual`。

```cpp
class Base {
public:
    virtual ~Base() {}
};
```

#### 为什么
通过父类指针删除子类对象时，如果析构函数不是虚函数，可能只调用父类析构，子类资源没释放干净。

#### 结论
**只要类可能作为多态基类，就优先给它一个虚析构函数。**

---

### 1.16 单继承 vs 多继承
#### 单继承
一个子类只继承一个父类。
- 结构简单
- 关系清楚
- 最常见

#### 多继承
一个子类继承多个父类。

```cpp
class C : public A, public B {};
```

##### 优点
- 可以组合多个父类能力

##### 缺点
- 容易出现名字冲突
- 容易出现菱形继承问题
- 复杂度显著增加

#### 建议
如果不是特别需要，优先考虑**组合**而不是多继承。

---

### 1.17 菱形继承问题
典型结构：

```text
    A
   / \
  B   C
   \ /
    D
```

如果 `B` 和 `C` 都继承 `A`，再由 `D` 同时继承 `B` 和 `C`，就可能出现 `A` 被继承两份的问题。

#### 问题
- 成员重复
- 访问歧义
- 对象布局复杂

#### 解决方式：虚继承
```cpp
class B : virtual public A {};
class C : virtual public A {};
class D : public B, public C {};
```

虚继承能保证最底层只保留一份公共基类子对象。

---

### 1.18 组合 vs 继承
继承不是唯一手段，很多时候**组合比继承更合适**。

#### 继承适合
- 明确的 `is-a` 关系
- 子类确实就是父类的一种
- 需要多态

#### 组合适合
- `has-a` 关系
- 复用功能，但不是“是某种东西”
- 想降低耦合

#### 例子
- `Dog is Animal`：适合继承
- `Car has Engine`：更适合组合

---

### 1.19 继承设计原则
1. 先判断是不是“是一个”关系
2. 父类要抽象公共行为，不要把细节全塞进去
3. 父类接口要稳定
4. 多态类优先写虚析构
5. 尽量避免无意义的多继承
6. 能组合就先考虑组合

---

### 1.20 常见坑
- 父类析构函数没写 `virtual`
- 想重写函数却没加 `virtual` / `override`
- 把继承当成代码复制工具，结果设计越来越乱
- 在对象切片后误以为还保留多态
- 多继承太多，层次混乱
- 忽略访问控制，误用 `private` 和 `protected`

---

### 1.21 记忆口诀
> **继承先看是不是“是一个”，多态优先虚函数；父类析构要虚，组合不行再继承。**

---

### 1.22 小练习
1. 定义一个 `Animal` 基类，再写 `Dog`、`Cat` 子类。
2. 给基类加虚函数，观察多态效果。
3. 给基类加虚析构函数，理解资源释放顺序。
4. 写一个抽象类 `Shape`，让 `Circle`、`Rect` 实现 `area()`。
5. 尝试构造一次菱形继承，并用虚继承修复它。

---

### 1.23 一页总结
- **继承**：复用公共代码，扩展子类能力
- **public/protected/private 继承**：控制父类成员在子类中的可见性
- **虚函数**：支持运行时多态
- **纯虚函数**：定义抽象接口
- **虚析构函数**：保证通过基类指针删除时资源完整释放
- **对象切片**：按值赋给基类对象时丢失子类部分
- **多继承**：能用，但要谨慎
- **虚继承**：解决菱形继承问题
- **组合优先**：不是所有复用都要靠继承


---

## 2. C++ 智能指针

### 2.1 一句话抓本质
**智能指针的本质，就是“用对象管理指针，让资源释放自动化”。**

你可以把它理解成：程序员不再手动盯着 `delete`，而是把“谁负责释放”这件事交给标准库对象去管理。

---

### 2.2 为什么需要智能指针
裸指针最大的麻烦不是“能不能用”，而是**生命周期太容易失控**。

常见问题：
- 忘记 `delete`，内存泄漏
- 多个指针都觉得自己该释放，重复释放
- 提前释放后继续使用，悬空指针
- 异常中途跳出，资源没来得及释放

智能指针的价值就是：**把资源释放和对象生命周期绑定起来**。

---

### 2.3 先记住一个大原则
> **能不用裸 `new/delete`，就尽量不用。**

现代 C++ 里，优先考虑：
- 容器
- 值语义
- 智能指针
- RAII

只有在确实需要动态生命周期时，才考虑智能指针。

---

### 2.4 三大智能指针
C++ 标准库里最常见的是：
- `unique_ptr`：独占所有权
- `shared_ptr`：共享所有权
- `weak_ptr`：弱引用，不拥有对象

它们分别解决不同的问题。

---

### 2.5 `unique_ptr`：独占所有权
#### 本质
一个对象只能有一个明确的主人。

#### 用途
- 默认首选
- 表示“这个资源只有我负责”
- 场景最安全、最清晰

#### 示例
```cpp
#include <memory>
#include <iostream>
using namespace std;

int main() {
    unique_ptr<int> p = make_unique<int>(10);
    cout << *p << endl;
}
```

#### 特点
- 不能拷贝
- 可以移动
- 离开作用域自动释放

#### 你要记住
- `unique_ptr` 表达“唯一拥有者”
- 资源转移用 `std::move`

```cpp
unique_ptr<int> a = make_unique<int>(1);
auto b = std::move(a);  // 所有权转移
```

#### 常见坑
- 试图复制 `unique_ptr`
- 忘记 `#include <memory>`
- 以为 `move` 之后原指针还拥有对象

#### 记忆口诀
> **独占所有权，unique 最简单；只能转移，不能复制。**

---

### 2.6 `shared_ptr`：共享所有权
#### 本质
多个指针共同拥有同一个对象，最后一个离开的人负责释放。

#### 用途
- 多个模块都需要持有同一资源
- 对象生命周期不容易固定由一个人管理

#### 示例
```cpp
#include <memory>
#include <iostream>
using namespace std;

int main() {
    shared_ptr<int> p1 = make_shared<int>(42);
    shared_ptr<int> p2 = p1;
    cout << p1.use_count() << endl;
}
```

#### 特点
- 可以拷贝
- 内部有引用计数
- 引用计数归零时自动释放

#### `make_shared` 的优点
- 更简洁
- 通常效率更好
- 少一次额外分配的可能性

#### 常见坑
- 过度使用 `shared_ptr`，让所有权变模糊
- 循环引用
- 以为共享所有权就等于“随便共享”

#### 记忆口诀
> **shared 是共享，不是乱共享；引用计数归零，自动释放。**

---

### 2.7 `weak_ptr`：弱引用
#### 本质
`weak_ptr` 只“观察”对象，不拥有对象。

#### 为什么需要它
`shared_ptr` 很容易形成循环引用：
- A 持有 B 的 `shared_ptr`
- B 也持有 A 的 `shared_ptr`
- 结果两边引用计数都不为 0，内存永远不释放

`weak_ptr` 就是为了解决这个问题。

#### 示例思路
```cpp
#include <memory>

struct B;

struct A {
    std::shared_ptr<B> b;
};

struct B {
    std::weak_ptr<A> a; // 避免循环引用
};
```

#### 常见用途
- 父子关系中的“非拥有者”一方
- 缓存观察者
- 避免 shared_ptr 循环引用

#### 使用方法
`weak_ptr` 不能直接解引用，要先 `lock()`：
```cpp
auto sp = wp.lock();
if (sp) {
    // 对象还活着
}
```

#### 常见坑
- 把 `weak_ptr` 当成普通指针直接用
- 忘记 `lock()` 判断空
- 不知道循环引用为何内存不释放

#### 记忆口诀
> **weak 不拥有，只观察；要用先 lock，安全再访问。**

---

### 2.8 智能指针和 RAII
智能指针是 RAII 最典型的应用之一。

#### 逻辑
- 构造时获得资源
- 析构时释放资源
- 出作用域自动清理

这意味着：即使中间 `throw` 异常，也能确保资源被释放。

```cpp
void f() {
    auto p = std::make_unique<int>(10);
    throw runtime_error("error");
} // 这里依然会自动释放
```

#### 这点特别重要
因为很多内存泄漏并不是“忘了 delete”，而是“中途异常返回，根本没机会 delete”。

---

### 2.9 智能指针的选择顺序
通常可以这样想：
1. **优先 `unique_ptr`**
2. 真的需要共享所有权，再考虑 `shared_ptr`
3. 如果只是观察共享对象，用 `weak_ptr`

不要一上来全用 `shared_ptr`。

---

### 2.10 自定义删除器
有些资源不是靠普通 `delete` 释放的，比如文件句柄、C 接口资源等，这时可以给智能指针配删除器。

```cpp
#include <memory>
#include <cstdio>

int main() {
    std::unique_ptr<FILE, decltype(&fclose)> fp(fopen("a.txt", "r"), fclose);
}
```

#### 这说明什么
智能指针不仅能管内存，还能管“其他需要自动释放的资源”。

---

### 2.11 容器里放智能指针
智能指针和容器常常一起用。

```cpp
#include <vector>
#include <memory>

std::vector<std::unique_ptr<int>> v;
v.push_back(std::make_unique<int>(1));
```

#### 作用
- 管对象集合
- 避免手动批量释放
- 对象生命周期更清晰

---

### 2.12 常见误区
- 以为“用了智能指针就万无一失”
- 过度使用 `shared_ptr`
- 循环引用不处理
- `weak_ptr` 不 `lock()` 就使用
- 忘记 `unique_ptr` 不能复制
- 在不需要共享时也用 `shared_ptr`

---

### 2.13 和裸指针的关系
智能指针并不是完全取代裸指针，而是**在“拥有资源”这件事上替代裸指针**。

#### 什么时候还会见到裸指针
- 观察对象，不拥有对象
- C API 交互
- 需要兼容旧代码
- 性能/底层场景

#### 但原则仍然是
**拥有者尽量用智能指针，观察者可以用裸指针/引用/weak_ptr。**

---

### 2.14 记忆口诀
> **unique 独占，shared 共享，weak 观察；资源管理靠 RAII，别再手动 delete 到处跑。**

---

### 2.15 小练习
1. 用 `unique_ptr` 管理一个整型对象。
2. 用 `shared_ptr` 做一次共享所有权实验。
3. 构造一个循环引用，再用 `weak_ptr` 修复它。
4. 给 `FILE*` 写一个自定义删除器。
5. 把智能指针放入 `vector` 里管理一组对象。

---

### 2.16 一页总结
- **unique_ptr**：唯一拥有者，默认首选
- **shared_ptr**：共享所有权，引用计数管理
- **weak_ptr**：不拥有对象，防循环引用
- **make_unique / make_shared**：推荐的构造方式
- **RAII**：让释放自动化，减少泄漏和异常问题
- **自定义删除器**：让智能指针管理非内存资源

---

## 3. C++ 深拷贝与浅拷贝 / 拷贝构造 / 拷贝赋值 / 析构函数 / 三五法则

### 3.1 一句话抓本质

**这一组知识的本质，是在回答一个问题：对象在“复制、赋值、销毁”时，内部资源到底该怎么处理。**

如果一个类只有普通成员，比如 `int`、`double`、`std::string`、`std::vector`，通常默认拷贝就够用。

但如果类里自己管理了资源，比如：

- `new` 出来的堆内存
- 文件句柄
- socket 连接
- 互斥锁
- C 风格资源指针

那就必须认真考虑：

> **拷贝时是共享同一份资源，还是复制出一份新资源？销毁时谁负责释放？**

---

### 3.2 先记住一条主线

这一章可以按下面这条线理解：

```text
对象里有资源
   ↓
默认浅拷贝可能只复制地址
   ↓
多个对象指向同一块资源
   ↓
析构时可能重复释放 / 悬空指针 / 数据互相影响
   ↓
所以要自己写拷贝构造、拷贝赋值、析构函数
   ↓
这就是三法则
   ↓
如果还想支持高效“搬资源”，再加移动构造、移动赋值
   ↓
这就是五法则
```

记忆：

> **只要类自己管资源，就要考虑“三五法则”。**

---

### 3.3 浅拷贝 vs 深拷贝

#### 3.3.1 浅拷贝是什么

**浅拷贝 = 只复制成员变量本身。**

如果成员变量是指针，那么浅拷贝只会复制指针里的地址，不会复制指针指向的内容。

```cpp
class A {
public:
    int* p;
};

A a;
a.p = new int(10);

A b = a;  // 默认拷贝：b.p 和 a.p 指向同一块内存
```

此时内存关系是：

```text
a.p ─┐
     ├──> int(10)
b.p ─┘
```

问题是：`a` 和 `b` 都以为自己拥有这块内存。

如果两个对象析构时都执行：

```cpp
delete p;
```

就会发生**重复释放**。

---

#### 3.3.2 深拷贝是什么

**深拷贝 = 不只复制指针地址，还要复制指针指向的内容。**

也就是说：

```text
a.p ───> int(10)

b.p ───> int(10)  // 另一块新内存，内容相同，但地址不同
```

深拷贝的目标是：

> **两个对象内容一样，但资源互不干扰。**

---

#### 3.3.3 对比表

| 对比点 | 浅拷贝 | 深拷贝 |
|---|---|---|
| 复制内容 | 复制成员值 | 复制成员值 + 复制资源内容 |
| 指针成员 | 只复制地址 | 重新分配内存并复制数据 |
| 多个对象关系 | 可能共享同一资源 | 各自拥有独立资源 |
| 风险 | 重复释放、悬空指针、互相影响 | 成本更高，但更安全 |
| 适用场景 | 不拥有资源，或明确共享 | 对象应独立拥有资源 |

一句话：

> **浅拷贝拷地址，深拷贝拷内容。**

---

### 3.4 默认拷贝为什么危险

看一个典型错误例子：

```cpp
#include <iostream>
#include <cstring>
using namespace std;

class BadString {
public:
    char* data;

    BadString(const char* s) {
        data = new char[strlen(s) + 1];
        strcpy(data, s);
    }

    ~BadString() {
        delete[] data;
    }
};

int main() {
    BadString a("hello");
    BadString b = a;  // 默认拷贝：只复制 data 地址
}
```

这里的问题是：

- `a.data` 指向一块堆内存
- `b.data` 也指向同一块堆内存
- `b` 析构时 `delete[] data`
- `a` 析构时又 `delete[] data`

结果就是：

> **同一块内存被释放两次。**

这就是经典的 **double free**。

---

### 3.5 拷贝构造函数

#### 3.5.1 拷贝构造函数是什么

拷贝构造函数用于：

> **用一个已有对象，初始化一个新对象。**

形式：

```cpp
ClassName(const ClassName& other);
```

例如：

```cpp
String s1("hello");
String s2 = s1;      // 调用拷贝构造
String s3(s1);       // 也调用拷贝构造
```

重点：

> **拷贝构造发生在“新对象创建时”。**

---

#### 3.5.2 为什么参数一定通常写成 `const ClassName&`

```cpp
ClassName(const ClassName& other);
```

原因有三个：

1. **用引用避免再次拷贝**
2. **用 `const` 表示不会修改被拷贝对象**
3. **可以接收 const 对象和临时对象**

如果写成这样：

```cpp
ClassName(ClassName other);  // 错误思路
```

传参时又要拷贝一次，而拷贝又要调用拷贝构造，可能导致无限递归。

记忆：

> **拷贝构造参数必须用引用，通常还要加 const。**

---

### 3.6 拷贝赋值运算符

#### 3.6.1 拷贝赋值是什么

拷贝赋值用于：

> **两个对象都已经存在，把右边对象的内容赋给左边对象。**

形式：

```cpp
ClassName& operator=(const ClassName& other);
```

例如：

```cpp
String s1("hello");
String s2("world");

s2 = s1;  // 调用拷贝赋值，不是拷贝构造
```

重点：

> **拷贝赋值发生在“已有对象重新赋值时”。**

---

#### 3.6.2 拷贝构造 vs 拷贝赋值

| 场景 | 调用什么 |
|---|---|
| `A b = a;` | 拷贝构造 |
| `A b(a);` | 拷贝构造 |
| `A b; b = a;` | 拷贝赋值 |
| 函数按值传参 | 可能调用拷贝构造 |
| 函数按值返回 | 可能调用拷贝/移动构造，也可能被优化掉 |

口诀：

> **新对象叫构造，老对象叫赋值。**

---

### 3.7 析构函数

析构函数用于：

> **对象生命周期结束时，自动释放它拥有的资源。**

形式：

```cpp
~ClassName();
```

例如：

```cpp
~String() {
    delete[] data;
}
```

析构函数的特点：

- 没有返回值
- 不能重载
- 一个类只能有一个析构函数
- 对象离开作用域时自动调用
- `delete` 对象时自动调用

如果类中有 `new`，析构函数里通常就要有对应的 `delete`。

记忆：

> **构造拿资源，析构还资源。**

---

### 3.8 一个完整深拷贝示例

下面用一个简单的字符串类模拟资源管理。

```cpp
#include <iostream>
#include <cstring>
using namespace std;

class MyString {
private:
    char* data;

public:
    // 普通构造函数：申请资源
    MyString(const char* s = "") {
        data = new char[strlen(s) + 1];
        strcpy(data, s);
    }

    // 拷贝构造函数：深拷贝
    MyString(const MyString& other) {
        data = new char[strlen(other.data) + 1];
        strcpy(data, other.data);
    }

    // 拷贝赋值运算符：深拷贝
    MyString& operator=(const MyString& other) {
        // 1. 处理自赋值
        if (this == &other) {
            return *this;
        }

        // 2. 释放旧资源
        delete[] data;

        // 3. 申请新资源并复制内容
        data = new char[strlen(other.data) + 1];
        strcpy(data, other.data);

        // 4. 返回自身，支持连续赋值 a = b = c
        return *this;
    }

    // 析构函数：释放资源
    ~MyString() {
        delete[] data;
    }

    void print() const {
        cout << data << endl;
    }
};

int main() {
    MyString s1("hello");
    MyString s2 = s1;   // 调用拷贝构造

    MyString s3("world");
    s3 = s1;            // 调用拷贝赋值

    s1.print();
    s2.print();
    s3.print();
}
```

这个类里三件事必须配套：

1. 析构函数负责释放 `data`
2. 拷贝构造负责新对象的深拷贝
3. 拷贝赋值负责已有对象的资源替换

---

### 3.9 拷贝赋值为什么要判断自赋值

自赋值就是：

```cpp
s1 = s1;
```

如果不判断自赋值，可能发生：

```cpp
delete[] data;
data = new char[strlen(other.data) + 1];
```

但 `other` 就是自己。你先把自己的 `data` 删除了，再去读 `other.data`，就可能访问已经释放的内存。

所以常见写法是：

```cpp
if (this == &other) {
    return *this;
}
```

记忆：

> **赋值先问一句：是不是自己给自己赋值？**

---

### 3.10 拷贝赋值的更安全写法：先申请，再释放

上面的写法已经可以理解，但还有异常安全问题。

如果你先释放旧资源：

```cpp
delete[] data;
data = new char[strlen(other.data) + 1];
```

万一 `new` 失败，对象的旧数据已经没了。

更稳妥的思路是：

> **先申请新资源，成功后再释放旧资源。**

```cpp
MyString& operator=(const MyString& other) {
    if (this == &other) {
        return *this;
    }

    char* newData = new char[strlen(other.data) + 1];
    strcpy(newData, other.data);

    delete[] data;
    data = newData;

    return *this;
}
```

这个版本更安全，因为只有新资源申请成功后，才会释放旧资源。

---

### 3.11 copy-and-swap 写法

更现代、更简洁的一种写法叫 **copy-and-swap**。

核心思想：

> **先复制出一个临时对象，再和自己交换资源。临时对象析构时带走旧资源。**

```cpp
#include <algorithm>

class MyString {
private:
    char* data;

public:
    MyString(const char* s = "") {
        data = new char[strlen(s) + 1];
        strcpy(data, s);
    }

    MyString(const MyString& other) {
        data = new char[strlen(other.data) + 1];
        strcpy(data, other.data);
    }

    void swap(MyString& other) noexcept {
        std::swap(data, other.data);
    }

    MyString& operator=(MyString other) {
        // other 是一份副本
        // 和副本交换后，this 拿到新资源
        // other 拿到旧资源，函数结束时自动析构释放旧资源
        swap(other);
        return *this;
    }

    ~MyString() {
        delete[] data;
    }
};
```

这种写法的优点：

- 天然处理自赋值
- 异常安全性更好
- 代码更简洁

但初学阶段，你至少要先理解普通版本，再理解 copy-and-swap。

---

### 3.12 三法则：Rule of Three

三法则说的是：

> **如果一个类需要自己写析构函数、拷贝构造函数、拷贝赋值运算符中的任意一个，通常三个都要考虑。**

三件套：

| 函数 | 作用 |
|---|---|
| 析构函数 | 释放资源 |
| 拷贝构造函数 | 用已有对象创建新对象 |
| 拷贝赋值运算符 | 已有对象之间赋值 |

为什么？

因为只要你需要手动析构，说明这个类大概率拥有资源。

既然拥有资源，就必须想清楚：

- 新对象拷贝资源时怎么办？
- 已有对象重新赋值时怎么办？
- 对象销毁时怎么办？

口诀：

> **有析构，必问拷贝；有资源，三件配齐。**

---

### 3.13 五法则：Rule of Five

C++11 引入移动语义后，三法则扩展成了五法则。

五件套：

| 函数 | 作用 |
|---|---|
| 析构函数 | 释放资源 |
| 拷贝构造函数 | 深拷贝新对象 |
| 拷贝赋值运算符 | 深拷贝赋值 |
| 移动构造函数 | 从临时对象“偷资源”创建新对象 |
| 移动赋值运算符 | 从临时对象“偷资源”赋给已有对象 |

移动语义的核心：

> **能搬走资源，就不要再复制资源。**

---

### 3.14 移动构造和移动赋值

#### 3.14.1 移动构造

移动构造用于：

> **用一个即将不用的对象，快速创建新对象。**

```cpp
MyString(MyString&& other) noexcept {
    data = other.data;       // 直接拿走资源
    other.data = nullptr;    // 让原对象不再拥有资源
}
```

这里不是深拷贝，而是“偷资源”。

原来：

```text
other.data ───> heap memory
```

移动后：

```text
this.data  ───> heap memory
other.data ───> nullptr
```

重点：

> **移动后，原对象必须进入一个可析构的安全状态。**

所以要把 `other.data` 置为 `nullptr`。

---

#### 3.14.2 移动赋值

```cpp
MyString& operator=(MyString&& other) noexcept {
    if (this == &other) {
        return *this;
    }

    delete[] data;           // 释放自己原来的资源
    data = other.data;       // 接管对方资源
    other.data = nullptr;    // 对方不再拥有资源

    return *this;
}
```

移动赋值的逻辑是：

1. 先释放自己旧资源
2. 接管对方资源
3. 把对方资源指针置空
4. 返回自己

---

### 3.15 带五法则的完整版本

```cpp
#include <iostream>
#include <cstring>
using namespace std;

class MyString {
private:
    char* data;

public:
    // 构造函数
    MyString(const char* s = "") {
        data = new char[strlen(s) + 1];
        strcpy(data, s);
    }

    // 析构函数
    ~MyString() {
        delete[] data;
    }

    // 拷贝构造：深拷贝
    MyString(const MyString& other) {
        data = new char[strlen(other.data) + 1];
        strcpy(data, other.data);
    }

    // 拷贝赋值：深拷贝
    MyString& operator=(const MyString& other) {
        if (this == &other) {
            return *this;
        }

        char* newData = new char[strlen(other.data) + 1];
        strcpy(newData, other.data);

        delete[] data;
        data = newData;

        return *this;
    }

    // 移动构造：偷资源
    MyString(MyString&& other) noexcept {
        data = other.data;
        other.data = nullptr;
    }

    // 移动赋值：释放旧资源，再偷新资源
    MyString& operator=(MyString&& other) noexcept {
        if (this == &other) {
            return *this;
        }

        delete[] data;
        data = other.data;
        other.data = nullptr;

        return *this;
    }

    void print() const {
        if (data) {
            cout << data << endl;
        } else {
            cout << "null" << endl;
        }
    }
};
```

这就是一个典型的资源管理类。

---

### 3.16 零法则：Rule of Zero

现代 C++ 更推荐：

> **能不自己管理资源，就不要自己管理资源。**

也就是说：

- 用 `std::string` 管字符串
- 用 `std::vector` 管动态数组
- 用 `std::unique_ptr` 管独占资源
- 用 `std::shared_ptr` 管共享资源

这样类就不需要自己写析构、拷贝构造、拷贝赋值、移动构造、移动赋值。

例如：

```cpp
#include <string>

class Person {
private:
    std::string name;

public:
    Person(std::string n) : name(std::move(n)) {}
};
```

这个类不需要自己写三五法则，因为 `std::string` 已经帮你管理好了资源。

记忆：

> **能用标准库，就别手写资源管理。三五法则很重要，零法则更推荐。**

---

### 3.17 哪些类需要自己写三五法则

通常这些类需要考虑：

- 类里有裸指针，并且拥有它指向的资源
- 构造函数里有 `new` / `malloc`
- 析构函数里有 `delete` / `free`
- 类管理文件、锁、socket、数据库连接等资源
- 类负责某种“独占所有权”

通常这些类不需要自己写：

- 只包含 `int`、`double` 等普通值类型
- 只包含 `std::string`、`std::vector` 等标准库容器
- 只包含智能指针，并且默认语义符合需求

---

### 3.18 常见坑总结

#### 坑 1：只写析构，不写拷贝构造和拷贝赋值

```cpp
class A {
    int* p;
public:
    ~A() { delete p; }
};
```

危险：默认拷贝会导致多个对象指向同一块内存，析构时重复释放。

---

#### 坑 2：拷贝构造写成值传递

```cpp
A(A other);  // 错误
```

应该写成：

```cpp
A(const A& other);
```

---

#### 坑 3：拷贝赋值忘记返回 `*this`

```cpp
A& operator=(const A& other) {
    // ...
    return *this;
}
```

返回引用是为了支持：

```cpp
a = b = c;
```

---

#### 坑 4：移动后没有置空原对象

```cpp
data = other.data;
// 忘记 other.data = nullptr;
```

危险：两个对象仍然指向同一资源，最后重复释放。

---

#### 坑 5：析构函数里释放方式不匹配

```cpp
int* p = new int;
delete[] p;  // 错误

int* arr = new int[10];
delete arr;  // 错误
```

规则：

| 申请方式 | 释放方式 |
|---|---|
| `new` | `delete` |
| `new[]` | `delete[]` |
| `malloc` | `free` |

---

### 3.19 面试回答模板

#### 问：什么是浅拷贝和深拷贝？

可以这样答：

> 浅拷贝只复制成员值，如果成员是指针，只复制地址，多个对象可能共享同一块资源。深拷贝会重新申请资源，并复制资源内容，让不同对象拥有独立资源。资源管理类如果使用默认浅拷贝，容易导致重复释放、悬空指针等问题。

---

#### 问：什么是拷贝构造和拷贝赋值？

可以这样答：

> 拷贝构造是在用已有对象初始化一个新对象时调用，比如 `A b = a`。拷贝赋值是在两个对象都已经存在时调用，比如 `b = a`。前者是创建新对象，后者是修改已有对象。

---

#### 问：什么是三法则？

可以这样答：

> 如果一个类需要自定义析构函数、拷贝构造函数、拷贝赋值运算符中的任意一个，通常说明它管理了资源，那么另外两个也要考虑，否则默认拷贝可能导致资源管理错误。

---

#### 问：什么是五法则？

可以这样答：

> C++11 引入移动语义后，资源管理类除了析构、拷贝构造、拷贝赋值，还应该考虑移动构造和移动赋值。移动操作可以直接接管临时对象资源，避免昂贵的深拷贝。

---

#### 问：什么是零法则？

可以这样答：

> 零法则是现代 C++ 更推荐的做法：尽量把资源交给标准库类型或智能指针管理，让类不需要手写析构、拷贝、移动等特殊函数，从而减少错误。

---

### 3.20 一页总结

| 概念 | 核心 |
|---|---|
| 浅拷贝 | 只复制地址，可能共享资源 |
| 深拷贝 | 复制资源内容，资源独立 |
| 拷贝构造 | 用已有对象创建新对象 |
| 拷贝赋值 | 已有对象之间赋值 |
| 析构函数 | 对象结束时释放资源 |
| 三法则 | 析构、拷贝构造、拷贝赋值要一起考虑 |
| 五法则 | 三法则 + 移动构造 + 移动赋值 |
| 零法则 | 尽量让标准库管理资源，自己不写特殊函数 |

---

### 3.21 记忆口诀

#### 口诀 1
**浅拷贝拷地址，深拷贝拷内容。**

#### 口诀 2
**新对象用构造，老对象用赋值。**

#### 口诀 3
**构造拿资源，析构还资源。**

#### 口诀 4
**有析构，问拷贝；有资源，三件配齐。**

#### 口诀 5
**能复制就深拷贝，能搬走就移动，能不用手写就零法则。**

---

### 3.22 本章最重要的一句话

> **只要类拥有资源，就必须想清楚：复制时谁拥有资源，赋值时旧资源怎么办，销毁时谁释放资源。**

---

## 4. C++ 智能指针：unique_ptr / shared_ptr / weak_ptr / RAII

### 4.1 一句话抓本质
**智能指针的本质，就是把“谁负责释放资源”交给对象自己管理。**

### 4.2 三大智能指针
- `unique_ptr`：独占所有权
- `shared_ptr`：共享所有权
- `weak_ptr`：观察对象，不拥有对象

### 4.3 `unique_ptr`
默认首选，只能移动不能拷贝。

### 4.4 `shared_ptr`
引用计数共享所有权，最后一个离开的人释放资源。

### 4.5 `weak_ptr`
解决 `shared_ptr` 的循环引用问题，用前先 `lock()`。

### 4.6 RAII
资源获取即初始化，离开作用域自动释放。

### 4.7 常见坑
- `unique_ptr` 复制失败
- `shared_ptr` 过度使用
- 循环引用不处理
- `weak_ptr` 不 `lock()` 就使用

### 4.8 记忆口诀
> unique 独占，shared 共享，weak 观察；资源管理靠 RAII。

### 4.9 面试高频点
- `unique_ptr` 和 `shared_ptr` 的区别？
- `weak_ptr` 为什么存在？
- 什么是循环引用？

---

## 5. C++ 继承 / 多态 / 虚函数 / 纯虚函数 / 虚析构 / 对象切片

### 5.1 一句话抓本质
**继承的本质，就是“复用 + 扩展 + 多态”的基础机制。**

### 5.2 核心概念
- `public` 继承最常用，表示 `is-a`
- 虚函数支持运行时多态
- 纯虚函数定义抽象接口
- 虚析构保证通过基类指针释放资源完整
- 对象切片会丢失派生类部分

### 5.3 菱形继承
多继承时可能出现重复基类子对象，必要时用虚继承。

### 5.4 常见坑
- 忘记 `virtual`
- 忘记 `override`
- 基类析构不虚
- 对象切片
- 多继承过多

### 5.5 记忆口诀
> 继承先看是不是“是一个”，多态优先虚函数；父类析构要虚，组合不行再继承。

### 5.6 面试高频点
- 继承和组合的区别？
- 什么是多态？
- 为什么基类析构函数要写成虚函数？

---

## 6. C++ const / constexpr / static / inline

### 6.1 一句话抓本质
**这些关键字的本质，都是在控制“是否可改、何时可算、属于谁、是否展开”。**

### 6.2 `const`
表示只读。

### 6.3 `constexpr`
表示尽量在编译期求值。

### 6.4 `static`
常见含义：静态局部变量、类静态成员、文件内可见性控制。

### 6.5 `inline`
常用于头文件函数定义，也表达“允许多处定义合并”。

### 6.6 常见坑
- `const` 和 `constexpr` 混淆
- `static` 用法混乱
- `inline` 误以为一定内联

### 6.7 记忆口诀
> const 只读，constexpr 编译期，static 看归属，inline 防重复。

### 6.8 面试高频点
- `const` 和 `constexpr` 有什么区别？
- `static` 的几种含义分别是什么？
- `inline` 真的一定内联吗？

---

## 7. C++ 左值 / 右值引用 / move / forward

### 7.1 一句话抓本质
**这一组知识的本质，是在区分“对象能不能被复用”和“资源能不能被搬走”。**

### 7.2 左值和右值
- 左值：有名字、能取地址
- 右值：临时对象、将亡值

### 7.3 右值引用
```cpp
int&& x = 10;
```

### 7.4 `move`
把对象转换成右值，允许移动语义接管资源。

### 7.5 `forward`
完美转发，保留参数原本的左值/右值属性。

### 7.6 常见坑
- 把 `move` 当成“真正搬家完成”
- `forward` 用错模板参数
- 右值引用理解成“万能引用”

### 7.7 记忆口诀
> 右值能搬资源，move 只是授权；forward 保原样，完美转发靠它。

### 7.8 面试高频点
- 左值和右值的区别？
- `move` 和 `forward` 的区别？
- 为什么移动语义能提升性能？

## 8. C++ 线程 / 互斥锁 / 条件变量 / 原子操作

### 8.1 一句话抓本质
**并发编程的本质，就是“让多个执行流安全地共享数据，同时尽量不把性能锁死”。**

### 8.2 为什么重要
- 多核时代程序几乎一定会碰到并发
- 线程能提升吞吐和响应速度
- 锁、条件变量、原子操作是线程安全的核心工具
- 面试和工程里最容易出错的也是并发问题

### 8.3 核心概念拆解
#### 8.3.1 线程 `std::thread`
- 表示一个独立执行流
- 启动后和主线程并发运行
- 线程对象析构前必须 `join()` 或 `detach()`

```cpp
#include <thread>
#include <iostream>

void work() {
    std::cout << "worker thread\n";
}

int main() {
    std::thread t(work);
    t.join();
}
```

#### 8.3.2 互斥锁 `std::mutex`
- 用来保护共享资源，保证同一时刻只有一个线程进入临界区
- 常配合 `std::lock_guard` / `std::unique_lock` 使用
- 适合“读写共享状态”的场景

```cpp
#include <mutex>

std::mutex m;
int counter = 0;

void add() {
    std::lock_guard<std::mutex> lock(m);
    ++counter;
}
```

#### 8.3.3 条件变量 `std::condition_variable`
- 用来“等条件满足再继续”，不是单纯加锁
- 适合生产者-消费者、任务队列、事件通知
- 通常和 `std::unique_lock`、谓词一起用

```cpp
#include <condition_variable>
#include <mutex>
#include <queue>

std::mutex m;
std::condition_variable cv;
std::queue<int> q;
bool ready = false;

void consumer() {
    std::unique_lock<std::mutex> lock(m);
    cv.wait(lock, [] { return ready || !q.empty(); });
    int x = q.front();
    q.pop();
}
```

#### 8.3.4 原子操作 `std::atomic`
- 对单个变量提供无锁或低成本的线程安全访问
- 适合计数器、标志位、状态切换
- 比互斥锁更轻，但能力也更局部

```cpp
#include <atomic>

std::atomic<int> hit{0};

void inc() {
    hit.fetch_add(1, std::memory_order_relaxed);
}
```

### 8.4 典型示例
#### 8.4.1 线程安全计数器
```cpp
#include <thread>
#include <mutex>
#include <vector>

std::mutex m;
int cnt = 0;

void add(int n) {
    for (int i = 0; i < n; ++i) {
        std::lock_guard<std::mutex> lock(m);
        ++cnt;
    }
}

int main() {
    std::thread t1(add, 1000);
    std::thread t2(add, 1000);
    t1.join();
    t2.join();
}
```

#### 8.4.2 条件变量等待任务
```cpp
#include <condition_variable>
#include <mutex>
#include <queue>

std::mutex m;
std::condition_variable cv;
std::queue<int> q;
bool done = false;

void producer() {
    {
        std::lock_guard<std::mutex> lock(m);
        q.push(42);
    }
    cv.notify_one();
}

void consumer() {
    std::unique_lock<std::mutex> lock(m);
    cv.wait(lock, [] { return done || !q.empty(); });
    if (!q.empty()) {
        int v = q.front();
        q.pop();
    }
}
```

#### 8.4.3 原子标志控制退出
```cpp
#include <atomic>
#include <thread>

std::atomic<bool> stop{false};

void loop() {
    while (!stop.load(std::memory_order_relaxed)) {
        // do work
    }
}
```

### 8.5 常见坑
- 线程对象没 `join()` 就析构，程序直接 `std::terminate()`
- 把所有共享数据都无脑加锁，导致性能差
- 锁顺序不一致，出现死锁
- `condition_variable` 没有配合谓词，容易虚假唤醒
- 等待条件前没先检查状态
- 原子变量只能保证“单个变量”的安全，不能替代复杂临界区
- `memory_order` 乱用，逻辑看似对，实际有可见性问题

### 8.6 记忆口诀
> 线程负责并发，mutex 负责互斥；cv 负责唤醒，atomic 负责轻量原子。先保正确，再谈性能。

### 8.7 面试高频问法或练习点
- `std::thread`、`join()`、`detach()` 的区别？
- `mutex` 和 `atomic` 怎么选？
- 为什么 `condition_variable` 要配合谓词？
- 什么是死锁？怎么避免？
- `lock_guard` 和 `unique_lock` 的区别？
- 设计一个生产者-消费者队列
- `memory_order_relaxed` 是什么场景用的？

## 9. C++ 模板进阶：`typename` / `decltype` / `auto` / SFINAE / `type_traits`
### 9.1 一句话抓本质
模板进阶的核心，就是“让编译期替你做类型判断和函数选择”，把很多本来要靠手写分支、重复重载、运行时判断的逻辑，提前折叠到类型系统里。

### 9.2 为什么重要
- C++ 泛型编程的能力，几乎都建立在模板进阶之上
- 它决定了你能不能写出“一个模板覆盖多种类型”的通用库代码
- 现代 C++ 的很多能力都离不开它：完美转发、泛型接口、容器适配、序列化、检测某个成员是否存在
- 面试里经常不是考你会不会语法，而是考你能不能说清楚“编译器到底做了什么”

### 9.3 核心概念拆解
#### 9.3.1 `typename`
- 在模板里，`typename` 最常见的作用有两个：
  - 声明模板参数：`template<typename T>`
  - 告诉编译器“下面这个依赖于模板参数的名字是类型”
- 为什么需要它：
  - 因为依赖名在模板实例化前，编译器无法确定它到底是类型还是静态成员
- 典型写法：
```cpp
template <typename T>
void print_size() {
    typename T::size_type n = 0;
}
```
- 这里 `typename T::size_type` 的意思是：`T::size_type` 是一个类型名，不是变量或静态成员

#### 9.3.2 `decltype`
- `decltype` 用来“精确推导表达式类型”
- 和 `auto` 最大的区别：
  - `auto` 更像“按初始化值推一个可用类型”
  - `decltype` 更像“原样问编译器这个表达式到底是什么类型”
- 两个高频规则：
  - `decltype(x)` 取变量名本身的类型
  - `decltype((x))` 因为是左值表达式，通常会得到引用类型
- 典型写法：
```cpp
int x = 0;
decltype(x) a = 1;     // int
decltype((x)) b = x;   // int&
```
- 常见用途：
  - 推导返回值类型
  - 跟踪复杂表达式的真实类型
  - 配合 `std::declval` 做检测

#### 9.3.3 `auto`
- `auto` 的本质是“让编译器从初始化式推导类型”
- 它最适合：
  - 类型太长时简化代码
  - 迭代器、lambda、泛型返回值
- 需要记住的细节：
  - `auto` 会丢掉顶层 `const`
  - `auto` 默认按值推导，引用要自己加 `&`
  - 花括号初始化可能推导成 `std::initializer_list`
- 典型写法：
```cpp
const int n = 10;
auto a = n;      // int
auto& b = n;     // const int&
auto c{1};       // 有时会走初始化列表推导，要小心
```

#### 9.3.4 SFINAE
- 全称是 `Substitution Failure Is Not An Error`
- 一句话理解：
  - 模板替换过程中，如果某个候选模板不合法，编译器不是直接报错，而是把它从候选集中踢掉
- 它的重要性：
  - 可以做“条件重载”
  - 可以做“只对某些类型开放的接口”
  - 是早期泛型编程和类型检测的基础
- 常见实现方式：
  - `std::enable_if`
  - 返回值类型推导
  - 参数列表依赖类型
- 典型写法：
```cpp
#include <type_traits>

template <typename T>
std::enable_if_t<std::is_integral_v<T>, T> twice(T x) {
    return x * 2;
}

template <typename T>
std::enable_if_t<std::is_floating_point_v<T>, T> twice(T x) {
    return x + x;
}
```

#### 9.3.5 `type_traits`
- `type_traits` 是 C++ 标准库提供的“编译期类型工具箱”
- 常见能力：
  - 判断类型：`is_same`、`is_integral`、`is_pointer`
  - 修改类型：`remove_reference`、`remove_cv`、`decay`
  - 条件选择：`conditional`
  - 控制模板可用性：`enable_if`
- 它的本质是把“类型逻辑”变成编译期常量和类型别名
- 典型写法：
```cpp
#include <type_traits>

static_assert(std::is_integral_v<int>);
using Plain = std::remove_cv_t<const volatile int>;
using Chosen = std::conditional_t<true, int, double>;
```

### 9.4 典型示例
#### 9.4.1 用 `decltype` 写泛型返回值
```cpp
template <typename T, typename U>
auto add(T a, U b) -> decltype(a + b) {
    return a + b;
}
```
- 作用：返回值类型跟着表达式走，不用手写一堆重载

#### 9.4.2 用 `enable_if` 限制接口
```cpp
#include <type_traits>

template <typename T>
std::enable_if_t<std::is_integral_v<T>, bool> is_even(T x) {
    return x % 2 == 0;
}
```
- 作用：只有整型才能调用，浮点数会在编译期被排除

#### 9.4.3 检测成员是否存在
```cpp
#include <type_traits>
#include <utility>

template <typename, typename = void>
struct has_begin : std::false_type {};

template <typename T>
struct has_begin<T, std::void_t<decltype(std::declval<T>().begin())>> : std::true_type {};

template <typename T>
constexpr bool has_begin_v = has_begin<T>::value;
```
- 作用：在编译期判断某个类型是否支持 `begin()`

#### 9.4.4 用 `auto` 简化复杂迭代器类型
```cpp
#include <vector>

std::vector<int> v{1, 2, 3};
for (auto it = v.begin(); it != v.end(); ++it) {
    // it 的真实类型太长，用 auto 更清晰
}
```

### 9.5 常见坑
- `typename` 少写了，依赖类型会被编译器误判
- `decltype(x)` 和 `decltype((x))` 不是一回事
- `auto` 会丢掉顶层 `const` 和引用
- `auto` 配合 `{}` 时，可能推导出意料之外的类型
- SFINAE 报错信息很长，定位时要顺着“哪个候选被踢掉了”去看
- `type_traits` 只解决“类型层面”的判断，不等于运行时逻辑
- 过度模板化会让代码可读性急剧下降，能不用就别滥用

### 9.6 记忆口诀
> `typename` 认类型，`decltype` 看表达式，`auto` 先偷懒，SFINAE 选候选，`type_traits` 管编译期分流。

### 9.7 面试高频问法或练习点
- `typename` 在模板里什么时候必须写？
- `decltype(x)` 和 `decltype((x))` 的区别是什么？
- `auto` 和 `decltype(auto)` 有什么区别？
- 什么是 SFINAE？它解决了什么问题？
- `enable_if` 的常见用法有哪些？
- 说说你用过哪些 `type_traits`
- 练习：实现一个 `has_size<T>`，判断类型是否有 `size()` 成员函数


---

## 9. C++ 类型转换：static_cast / dynamic_cast / const_cast / reinterpret_cast

### 9.1 一句话抓本质
**类型转换的本质，就是“告诉编译器：我知道自己在做什么，请按这个方向解释这个值”。**

### 9.2 为什么重要
类型转换是 C++ 里最容易“看起来能跑，实际上埋雷”的地方。写得好，它能帮助你明确意图；写得差，它能让 bug 隐藏得很深。

### 9.3 四种转换先区分
- `static_cast`：编译期已知的安全转换
- `dynamic_cast`：多态类型之间的运行时检查转换
- `const_cast`：去掉或添加 `const`
- `reinterpret_cast`：按比特重新解释，最危险

### 9.4 `static_cast`
适合：
- 数值类型转换
- 父类/子类指针或引用的“向上/向下”相关场景（前提是你明确知道对象类型）
- 明确、可读的转换

```cpp
double x = 3.14;
int y = static_cast<int>(x);
```

### 9.5 `dynamic_cast`
适合多态场景的安全向下转换。

```cpp
Base* p = new Derived();
Derived* d = dynamic_cast<Derived*>(p);
```

如果转换失败，指针版返回 `nullptr`，引用版会抛异常。

### 9.6 `const_cast`
用于修改 `const` 限定。

```cpp
const int a = 10;
int* p = const_cast<int*>(&a);
```

#### 注意
不是所有 `const_cast` 都安全；如果原对象本来就是 const，去掉 const 后强改值可能是未定义行为。

### 9.7 `reinterpret_cast`
最“硬核”，把一段比特按另一种类型强行解释。

```cpp
int x = 0;
char* p = reinterpret_cast<char*>(&x);
```

#### 重点
- 可读性差
- 可移植性差
- 风险高
- 一般只在底层、系统、协议、硬件相关场景用

### 9.8 常见坑
- 把 C 风格强转当成万能工具
- `dynamic_cast` 用在没有虚函数的类上
- 误以为 `const_cast` 可以安全修改真正的 const 对象
- 过度使用 `reinterpret_cast`

### 9.9 记忆口诀
> static 看得懂，dynamic 要多态；const_cast 动 const，reinterpret 最危险。

### 9.10 面试高频点
- 四种转换分别用于什么场景？
- `dynamic_cast` 失败返回什么？
- 为什么 `reinterpret_cast` 风险高？

---

## 10. C++ 内存管理：new/delete、智能指针进阶、RAII、内存泄漏与悬空指针

### 10.1 一句话抓本质
**内存管理的本质，就是“谁申请、谁释放、什么时候释放”。**

### 10.2 `new/delete`
```cpp
int* p = new int(10);
delete p;
```

数组要配对：
```cpp
int* arr = new int[10];
delete[] arr;
```

### 10.3 智能指针进阶
- `unique_ptr`：独占
- `shared_ptr`：共享
- `weak_ptr`：观察，防循环引用

### 10.4 RAII
把资源放进对象生命周期里管理，是现代 C++ 最核心的工程习惯之一。

### 10.5 内存泄漏
申请了内存却忘记释放。

### 10.6 悬空指针
内存已经释放，但指针还在用。

### 10.7 常见坑
- `new[]` 配 `delete`
- 释放后继续使用
- 一个资源多次释放
- 智能指针循环引用

### 10.8 记忆口诀
> 申请要负责，释放要成对；智能指针管生命周期，别让裸指针乱飞。

### 10.9 面试高频点
- `new/delete` 和 `malloc/free` 的区别？
- 什么是内存泄漏？什么是悬空指针？
- 为什么 RAII 很重要？

---

## 11. C++ 文件流 / stringstream / iomanip / 编码与文本处理

### 11.1 一句话抓本质
**这组知识的本质，就是“让文本数据能被读取、解析、格式化、再输出”。**

### 11.2 `fstream`
用于文件读写。

### 11.3 `stringstream`
把字符串当流来解析。

### 11.4 `iomanip`
负责格式控制，比如宽度、对齐、小数位。

### 11.5 编码与文本处理
- ASCII
- UTF-8
- 宽字符
- 本地化
- 旧式 `codecvt`

### 11.6 常见坑
- `getline` 和 `>>` 混用时缓冲区问题
- 文本编码不一致
- 格式控制影响后续输出

### 11.7 记忆口诀
> 文件流管读写，stringstream 管解析，iomanip 管长相。

### 11.8 面试高频点
- `stringstream` 常见用途？
- `getline` 为什么有时读不到想要的内容？
- 文本编码为什么容易出问题？

---

## 12. C++ 命名空间 / 预处理器 / 头文件保护 / 宏的风险

### 12.1 一句话抓本质
**这组知识的本质，就是“给名字分区、给代码做预处理、给头文件防重复、给宏控风险”。**

### 12.2 命名空间
用于避免重名冲突。

### 12.3 预处理器
`#include`、`#define`、条件编译等，都在编译前处理。

### 12.4 头文件保护
```cpp
#ifndef X_H
#define X_H
#endif
```
防止头文件重复包含。

### 12.5 宏的风险
- 没有类型检查
- 容易产生副作用
- 错误难查
- 优先级坑很多

### 12.6 常见坑
- 全局 `using namespace std;`
- 宏参数没加括号
- 头文件重复包含
- 条件编译把代码切碎

### 12.7 记忆口诀
> 命名空间防冲突，头文件保护防重复，宏能省事也能埋坑。

### 12.8 面试高频点
- 为什么要有头文件保护？
- 宏和函数有什么区别？
- `using namespace` 为什么不建议乱用？

---

## 13. C++ 模板进阶：typename / decltype / auto / SFINAE / type_traits

### 13.1 一句话抓本质
**模板进阶的本质，就是让编译器在编译期做更多“类型判断和类型生成”的工作。**

### 13.2 `typename`
用于说明依赖类型。

### 13.3 `decltype`
用于“推导表达式的类型”。

### 13.4 `auto`
让编译器根据初始化表达式推导类型。

### 13.5 SFINAE
“替换失败不是错误”，常用于模板重载选择和类型约束。

### 13.6 `type_traits`
编译期类型判断工具库。

### 13.7 常见坑
- 模板错误信息太长
- `decltype` 和 `auto` 搞混
- `typename` 写漏导致编译报错
- SFINAE 看不懂就乱写

### 13.8 记忆口诀
> auto 让你少写，decltype 看表达式，type_traits 做判断，SFINAE 管筛选。

### 13.9 面试高频点
- `auto` 和 `decltype` 的区别？
- `typename` 为什么有时必须写？
- 什么是 SFINAE？
- `type_traits` 常用来做什么？

---

## 14. C++ 编译 / 链接 / ODR / 头文件模型

### 14.1 一句话抓本质
**这部分的本质，就是“代码是怎么从文本变成可执行程序的”。**

### 14.2 为什么重要
很多“明明写对了却链接失败”的问题，本质都不是语法，而是编译、链接、头文件组织出了问题。你如果不了解这一层，就很难真正理解：
- 为什么头文件要保护
- 为什么有些函数可以写在头文件里
- 为什么会有重复定义
- 为什么模板常写在头文件中

### 14.3 编译流程大概分几步
1. 预处理：展开 `#include`、宏、条件编译
2. 编译：把源代码翻译成目标文件
3. 汇编：生成机器相关的目标表示
4. 链接：把多个目标文件和库拼成可执行文件

### 14.4 头文件模型
头文件的作用不是“装代码越多越好”，而是**声明接口、减少重复、让多个源文件共享定义方式**。

通常：
- `.h` / `.hpp` 放声明
- `.cpp` 放实现

### 14.5 ODR
ODR（One Definition Rule）可以简单理解为：**同一个实体在整个程序里只能有一个合规定义**。

#### 常见 ODR 问题
- 头文件里直接定义了非 `inline` 函数
- 全局变量在多个 `.cpp` 里重复定义
- 模板/内联内容写法不规范

### 14.6 一个最小例子
```cpp
// a.h
#ifndef A_H
#define A_H

int add(int a, int b);

#endif
```

```cpp
// a.cpp
#include "a.h"
int add(int a, int b) { return a + b; }
```

### 14.7 常见坑
- 头文件没加保护导致重复包含
- 声明和定义不一致
- 把实现全写头文件却忘了 `inline`
- 链接错误和编译错误混淆

### 14.8 记忆口诀
> 预处理先展开，编译生成目标，链接拼成程序；头文件管声明，ODR 管唯一。

### 14.9 面试高频点
- 编译和链接有什么区别？
- 什么是 ODR？
- 为什么头文件需要保护？
- 为什么模板实现常放在头文件里？

---

## 15. C++ 对象模型：vtable / vptr / 虚函数机制

### 15.1 一句话抓本质
**对象模型的本质，就是“虚函数到底是怎么在运行时找到正确实现的”。**

### 15.2 为什么重要
虚函数、多态、虚析构、RTTI 等内容，底层几乎都和对象模型有关。面试里如果问到“虚函数是怎么实现的”，基本就是在考这个。

### 15.3 vtable / vptr
- **vtable**：虚函数表，保存虚函数地址
- **vptr**：虚表指针，存在对象内部，指向当前类的虚表

### 15.4 运行时多态怎么发生
通过基类指针/引用调用虚函数时，程序会沿着对象里的 vptr 找到实际类型对应的 vtable，然后调用正确版本。

### 15.5 这意味着什么
- 同一个接口，运行时可以表现出不同的行为
- 编译时并不总能完全决定调用哪个版本
- 虚函数带来灵活性，也带来一点额外开销

### 15.6 一个直观示例
```cpp
class Base {
public:
    virtual void f();
};

class Derived : public Base {
public:
    void f() override;
};
```

### 15.7 常见坑
- 以为虚函数“完全免费”
- 忽略对象内存布局
- 忘记虚析构
- 在构造/析构中调用虚函数，行为容易和预期不同

### 15.8 记忆口诀
> 虚表存函数，虚指针指表；基类看接口，运行时找实现。

### 15.9 面试高频点
- 虚函数底层怎么实现？
- vtable 和 vptr 分别是什么？
- 为什么构造函数里调用虚函数不会表现出多态？

---

## 16. C++ 三法则 / 五法则 / 零法则

### 16.1 一句话抓本质
**这几条法则的本质，就是“类如果自己管理资源，就必须把拷贝、移动、销毁的规则想清楚”。**

### 16.2 三法则
如果你自己写了下面三个中的一个，通常要考虑另外两个：
- 析构函数
- 拷贝构造
- 拷贝赋值

### 16.3 五法则
C++11 之后，如果你需要资源管理，往往还要把这两个也考虑进去：
- 移动构造
- 移动赋值

### 16.4 零法则
更现代的做法是：**尽量不要自己手写资源管理**，交给标准库类型、智能指针、容器去管理，让自己的类尽量保持“值语义”。

### 16.5 为什么零法则重要
如果你能用 `vector`、`string`、`unique_ptr` 之类的库类型来表达资源管理，就不必自己手写一堆拷贝/析构逻辑，出错概率会大幅下降。

### 16.6 一个判断方法
如果类里有：
- 裸 `new/delete`
- 文件句柄
- socket
- 锁
- 其他手动释放资源

那就要警惕是否触发三/五法则的设计问题。

### 16.7 常见坑
- 只写析构，不写拷贝控制
- 忘记移动语义
- 过度依赖默认生成函数
- 资源类仍然用浅拷贝

### 16.8 记忆口诀
> 三法则管拷贝，五法则管移动，零法则最舒服：让库帮你管资源。

### 16.9 面试高频点
- 三法则 / 五法则 / 零法则分别是什么？
- 为什么现代 C++ 更推荐零法则？
- 资源类为什么不能随便默认拷贝？

---

## 17. C++ 异常安全 / noexcept

### 17.1 一句话抓本质
**异常安全的本质，就是“即使出错，程序也不能把资源状态弄乱”。**

### 17.2 为什么重要
一个函数写完，不只是要“能跑”，还要考虑：
- 出异常时对象是否仍然有效
- 已申请资源是否能回收
- 外部可见状态是否被破坏

### 17.3 异常安全的三个层次
#### 基本保证
出错后对象仍然处于合法状态。

#### 强保证
要么成功，要么完全回到原状态。

#### 不抛异常保证
函数承诺不会抛异常。

### 17.4 `noexcept`
```cpp
void f() noexcept;
```

表示这个函数承诺不抛异常。编译器和标准库常会根据这一信息做优化或调整策略。

### 17.5 为什么 `noexcept` 有用
- 提升标准库对移动语义的使用意愿
- 明确接口行为
- 让异常相关优化更可靠

### 17.6 典型思路
写异常安全代码时，常见原则是：
- 先构造新资源，再替换旧资源
- 用 RAII 管资源
- 避免“先删旧再建新”导致中途失败

### 17.7 常见坑
- `noexcept` 写了但函数里真的可能抛
- 赋值时先释放旧资源再申请新资源
- 忽略异常导致对象状态半更新
- 把异常安全等同于“try/catch 包住”

### 17.8 记忆口诀
> 先准备新资源，再替换旧资源；异常安全不是挡住异常，而是不把状态弄坏。

### 17.9 面试高频点
- 什么是异常安全？
- 强保证和基本保证有什么区别？
- `noexcept` 有什么作用？
- 为什么移动构造常配 `noexcept`？

---

## 18. C++ STL 进阶：`emplace`、迭代器失效、`allocator`

### 18.1 一句话抓本质
**STL 进阶的本质，就是“不只是会用容器，还要知道容器内部是怎么高效管理对象的”。**

### 18.2 `emplace`
`emplace` 不是简单插入一个现成对象，而是“在容器内部直接构造对象”。

```cpp
std::vector<std::pair<int, int>> v;
v.emplace_back(1, 2);
```

### 18.3 `push` vs `emplace`
- `push_back`：先有对象，再放进去
- `emplace_back`：直接在容器内部构造对象

在某些场景下，`emplace` 可以减少临时对象和拷贝/移动。

### 18.4 迭代器失效
容器一旦发生插入、删除、扩容，部分迭代器可能失效。

这是 STL 高频坑之一，尤其是 `vector`。

### 18.5 `allocator`
`allocator` 是标准库的分配器接口，负责容器如何申请和释放底层内存。

你不一定天天手写 allocator，但要知道容器背后并不是“魔法”，而是通过分配器和构造/析构机制管理内存。

### 18.6 常见坑
- `remove` 和 `erase` 混淆
- 修改容器后还继续用旧迭代器
- 以为 `emplace` 一定比 `push` 快
- 不理解容器扩容机制

### 18.7 记忆口诀
> `emplace` 现场构造，迭代器失效要警惕，allocator 管底层，容器才跑得稳。

### 18.8 面试高频点
- `emplace` 和 `push` 的区别？
- 什么是迭代器失效？
- `vector` 扩容时发生了什么？
- allocator 是干什么的？

---

## 19. C++ 现代库专题：`string_view` / `optional` / `variant` / `any` / `span`

### 19.1 一句话抓本质
**这些现代库类型的本质，就是“让接口更轻、更安全、更表达意图”。**

### 19.2 `string_view`
表示“字符串视图”，不拥有字符串数据，只是看一段字符范围。

```cpp
std::string_view sv = "hello";
```

#### 作用
- 避免不必要的拷贝
- 方便接收不同字符串来源

#### 注意
它不拥有数据，所以底层字符串生命周期必须足够长。

### 19.3 `optional`
表示“可能有值，也可能没有值”。

```cpp
std::optional<int> x;
```

比用“魔法值”更清晰。

### 19.4 `variant`
表示“在若干类型中选一个”。

```cpp
std::variant<int, std::string> v;
```

适合“一个值可能是多种类型之一”的场景。

### 19.5 `any`
表示“可以装任意类型”。

它更通用，但也更难静态检查。

### 19.6 `span`
表示“一段连续数据的视图”。

适合函数参数传递数组、vector、原始连续内存。

### 19.7 它们各自适合什么
- `string_view`：看字符串，不复制
- `optional`：有值/无值
- `variant`：多选一
- `any`：真的什么都能装
- `span`：连续区间视图

### 19.8 常见坑
- `string_view` 悬空引用
- `optional` 里有没有值没判断就用
- `variant` 取错类型
- `any` 滥用导致失去类型安全
- `span` 误以为自己拥有数据

### 19.9 记忆口诀
> `view` 不拥有，`optional` 表可有可无，`variant` 多选一，`any` 万能但危险，`span` 只看连续区间。

### 19.10 面试高频点
- `string_view` 和 `string` 的区别？
- `optional` 为什么比魔法值更好？
- `variant` 和 `any` 有什么不同？
- `span` 的典型用途是什么？


---

## 20. C++17 / C++20 / C++23 新特性

### 20.1 一句话抓本质
**现代 C++ 新特性的本质，是让代码更安全、更表达意图、更少模板样板。**

### 20.2 为什么重要
现代面试越来越少考“只会 C++98 风格”，而是更关注你是否理解：
- 结构化绑定
- `if constexpr`
- concepts
- ranges
- coroutine
- 三路比较

### 20.3 结构化绑定
```cpp
auto [x, y] = std::pair<int,int>{1, 2};
```
让拆包更直观。

### 20.4 `if constexpr`
编译期条件分支。

```cpp
if constexpr (std::is_integral_v<T>) {
    // ...
}
```

### 20.5 concepts
给模板参数加更清晰的约束。

### 20.6 ranges
让算法和区间操作表达更自然。

### 20.7 coroutine
用于异步流程、生成器、挂起恢复模型。

### 20.8 三路比较 `<=>`
统一比较接口，减少手写比较逻辑。

### 20.9 常见坑
- 把新特性当语法糖，不理解设计目的
- `if constexpr` 和普通 `if` 混淆
- concept 只会用不会解释
- coroutine 只会背概念不会落场景

### 20.10 记忆口诀
> 新特性不只是省代码，更是在省 bug、提表达、降样板。

### 20.11 面试高频点
- `if constexpr` 和 `if` 的区别？
- concepts 解决了什么问题？
- coroutine 适合什么场景？
- `<=>` 有什么价值？

---

## 21. C++ 模板元编程进阶：偏特化 / 变参模板 / 概念约束 / CRTP

### 21.1 一句话抓本质
**模板元编程的本质，是让编译器在编译期执行“类型逻辑”。**

### 21.2 偏特化
给“某类模板参数组合”提供特殊实现。

### 21.3 变参模板
```cpp
template<typename... Args>
void f(Args... args) {}
```
支持不定参数模板。

### 21.4 概念约束
比传统 `enable_if` 更清晰地表达模板要求。

### 21.5 CRTP
Curiously Recurring Template Pattern：
```cpp
template<typename Derived>
class Base {};
```
常用于静态多态。

### 21.6 常见坑
- 模板递归读不懂
- 偏特化和全特化混淆
- CRTP 看起来像继承，其实更偏编译期技巧

### 21.7 记忆口诀
> 偏特化做分支，变参模板吃参数，concept 管约束，CRTP 做静态多态。

### 21.8 面试高频点
- 什么是偏特化？
- 变参模板怎么展开？
- CRTP 的用途是什么？
- concept 和 `enable_if` 的关系？

---

## 22. C++ 对象生命周期 / 临时对象 / 返回值优化

### 22.1 一句话抓本质
**对象生命周期的本质，是“对象何时创建、何时销毁、何时能安全使用”。**

### 22.2 生命周期为什么高频
很多看似玄学的问题，本质上都是生命周期没理清：
- 返回局部引用
- 临时对象过早销毁
- 悬空引用
- move 后继续乱用对象

### 22.3 临时对象
表达式中经常会生成临时对象。

### 22.4 返回值优化 RVO / NRVO
编译器常会直接在目标位置构造对象，减少拷贝。

### 22.5 生命周期延长
`const T&` 绑定临时对象时，可延长其生命周期。

### 22.6 常见坑
- 返回局部对象引用
- 误判临时对象存活时间
- 把“编译器优化了”当作语言保证理解错误

### 22.7 记忆口诀
> 临时对象别乱留，返回值优化常帮忙；引用一旦悬空，再像样也危险。

### 22.8 面试高频点
- 什么是 RVO？
- 临时对象什么时候销毁？
- 为什么不能返回局部变量引用？

---

## 23. C++ 内存模型 / atomic / 并发安全

### 23.1 一句话抓本质
**内存模型的本质，是“多个线程看到同一份数据时，顺序和可见性如何保证”。**

### 23.2 为什么重要
并发 bug 最难查，因为它往往不是“代码错了”，而是“线程之间看见的数据顺序不同”。

### 23.3 `atomic`
适合简单共享状态的原子更新。

### 23.4 可见性与顺序
线程之间不仅有“值对不对”，还有“谁先看到谁”。

### 23.5 `memory_order`
- `memory_order_relaxed`
- `memory_order_acquire`
- `memory_order_release`
- `memory_order_seq_cst`

### 23.6 并发安全不等于线程安全万能
- 原子适合简单变量
- 锁适合复杂临界区
- 正确性优先于炫技的无锁写法

### 23.7 常见坑
- 把 `atomic` 当互斥锁替代品
- 误解内存序
- 只看单线程语义，不看多线程可见性

### 23.8 记忆口诀
> atomic 管单点，锁管大块；内存序管先后，可见性别想当然。

### 23.9 面试高频点
- 什么是内存模型？
- `atomic` 和 `mutex` 的区别？
- 为什么内存序难？

---

## 24. C++ filesystem / chrono / format

### 24.1 一句话抓本质
**这三个现代库的本质，是把“文件系统、时间、格式化输出”变成标准化、类型安全的能力。**

### 24.2 `filesystem`
用于路径、目录、文件操作。

```cpp
#include <filesystem>
std::filesystem::path p = "./a.txt";
```

### 24.3 `chrono`
现代时间库，强调时间点和持续时间的类型安全。

### 24.4 `format`
更现代的格式化输出方式，语义比传统 `printf` 更清晰。

```cpp
// C++20
// std::format("{} {}", a, b)
```

### 24.5 为什么工程里常考
因为这三类操作在真实工程里非常常见：
- 文件路径和目录扫描
- 性能计时与超时控制
- 结构化日志输出

### 24.6 常见坑
- 路径分隔符平台差异
- 混淆系统时间和稳定时钟
- 旧式格式化和新式格式化混搭

### 24.7 记忆口诀
> filesystem 管路径，chrono 管时间，format 管长相；都是现代工程高频工具。**

### 24.8 面试高频点
- `filesystem` 能解决什么问题？
- `system_clock` 和 `steady_clock` 区别？
- 为什么 `format` 比 `printf` 更现代？


---

## 25. C++ 容器选型总专题：vector / deque / list / set / map / unordered_map

### 25.1 一句话抓本质
**容器选型的本质，不是“哪个都会用”，而是“面对场景能快速选对”。**

### 25.2 为什么重要
面试和工程都很少只问“会不会 vector”，更常问：
- 为什么这里不用 list？
- map 和 unordered_map 怎么选？
- deque 和 vector 区别是什么？

### 25.3 快速选型思路
- 随机访问多：`vector`
- 两端插删多：`deque`
- 中间频繁插删：`list`
- 需要有序键值：`map`
- 需要无序快速查找：`unordered_map`
- 需要去重集合：`set` / `unordered_set`

### 25.4 核心差别
- `vector`：连续内存、缓存友好
- `deque`：分段连续，头尾扩展方便
- `list`：链表，节点分散
- `set/map`：红黑树，有序
- `unordered_map`：哈希表，无序

### 25.5 常见坑
- 以为 list 一定更快
- 在不需要有序时还用 map
- 不清楚 unordered_map 的哈希冲突问题
- 忽略迭代器失效

### 25.6 记忆口诀
> 连续访问想 vector，头尾插删想 deque，中间改动想 list；要顺序用 map/set，要哈希用 unordered。

### 25.7 面试高频点
- vector 和 list 的区别？
- map 和 unordered_map 的区别？
- deque 为什么不是完全连续内存？

---

## 26. C++ 函数对象 / 仿函数 / 可调用对象体系

### 26.1 一句话抓本质
**可调用对象体系的本质，就是“函数不只是函数名，还可以是对象、闭包、成员函数适配结果”。**

### 26.2 可调用对象有哪些
- 普通函数
- 函数指针
- Lambda
- 仿函数（重载 `operator()` 的类）
- `std::function`
- `bind` 绑定结果

### 26.3 仿函数示例
```cpp
struct Add {
    int operator()(int a, int b) const {
        return a + b;
    }
};
```

### 26.4 为什么仿函数有价值
- 可携带状态
- 可内联优化
- 类型明确
- STL 中大量使用比较器/谓词

### 26.5 常见坑
- 把所有回调都装进 std::function，忽略开销
- 搞不清 Lambda 和仿函数本质关系
- bind 写得过于复杂

### 26.6 记忆口诀
> 普通函数能调用，仿函数像函数，Lambda 是匿名仿函数，function 是统一包装器。

### 26.7 面试高频点
- 仿函数和普通函数有什么区别？
- Lambda 的底层更像什么？
- std::function 的代价是什么？

---

## 27. C++ move 语义进阶 / 完美转发 / 引用折叠

### 27.1 一句话抓本质
**这部分的本质，是把“资源所有权搬运”做得更高效、更准确。**

### 27.2 move 语义为什么重要
它让对象在“可以被搬走资源”时，不必再做昂贵的深拷贝。

### 27.3 引用折叠
模板里引用组合后会发生折叠，这是理解万能引用/转发引用的基础。

### 27.4 完美转发
```cpp
template<typename T>
void wrapper(T&& arg) {
    foo(std::forward<T>(arg));
}
```

### 27.5 为什么需要 `forward`
因为单纯 `arg` 在函数体里已经有名字，变成左值，需要 `forward` 保留原来的值类别。

### 27.6 常见坑
- 以为 `std::move` 真会移动对象
- `forward` 写成 `move`
- 不理解引用折叠就乱写模板接口

### 27.7 记忆口诀
> move 给搬家许可，forward 保原身份，引用折叠管底层规则。

### 27.8 面试高频点
- `std::move` 到底做了什么？
- 什么是完美转发？
- 引用折叠规则是什么？

---

## 28. C++ 多线程进阶：future / promise / async / packaged_task

### 28.1 一句话抓本质
**这组工具的本质，是把“线程执行”和“结果回传”解耦。**

### 28.2 `future`
代表一个“未来会拿到的结果”。

### 28.3 `promise`
负责把结果放进去，future 负责把结果取出来。

### 28.4 `async`
快速启动异步任务并返回 future。

```cpp
auto f = std::async([]{ return 42; });
```

### 28.5 `packaged_task`
把可调用对象包装成“可异步执行并通过 future 取结果”的任务单元。

### 28.6 常见坑
- future 结果不取
- async 的策略不清楚
- promise/future 生命周期没配合好

### 28.7 记忆口诀
> async 开任务，future 拿结果，promise 送结果，packaged_task 包任务。

### 28.8 面试高频点
- future 和 promise 的关系？
- async 和 thread 的区别？
- packaged_task 适合什么场景？

---

## 29. C++ 网络编程基础 / socket 思维

### 29.1 一句话抓本质
**网络编程的本质，就是“进程之间通过套接字交换字节流或报文”。**

### 29.2 为什么要理解 socket 思维
即使你不用 C++ 手写完整服务器，也经常会被问：
- TCP 和 UDP 区别？
- socket 是什么？
- 阻塞/非阻塞是什么？

### 29.3 socket 基本认知
socket 可以理解成“网络通信端点”。

### 29.4 TCP vs UDP
- TCP：可靠、有连接、顺序保证
- UDP：无连接、轻量、不保证可靠

### 29.5 阻塞 / 非阻塞 / IO 多路复用
这是网络程序性能模型的核心概念之一。

### 29.6 常见坑
- 把一次 send/recv 当成完整消息
- 忽略粘包拆包
- 不了解字节序

### 29.7 记忆口诀
> socket 是端点，TCP 重可靠，UDP 重轻量；网络不是调个 API 就结束，协议边界更关键。

### 29.8 面试高频点
- TCP 和 UDP 的区别？
- 什么是粘包拆包？
- 阻塞 IO 和非阻塞 IO 的区别？

---

## 30. C++ 调试与排错：core dump / gdb / sanitizers / valgrind

### 30.1 一句话抓本质
**调试的本质，不是“猜哪里错了”，而是“拿证据定位问题”。**

### 30.2 core dump
程序崩溃后留下的现场快照。

### 30.3 gdb
最经典的 C/C++ 调试器。

### 30.4 sanitizers
现代编译器提供的运行时检测工具：
- ASan：地址越界/释放后使用
- UBSan：未定义行为
- TSan：线程问题

### 30.5 valgrind
经典内存检查工具，尤其常见于 Linux 调试链。

### 30.6 常见坑
- 只看报错表面，不看调用栈
- 不开调试符号就想精确定位
- 内存 bug 不借助工具硬猜

### 30.7 记忆口诀
> 崩溃先看现场，问题先拿栈；内存 bug 用 sanitizer，别靠肉眼硬推理。

### 30.8 面试高频点
- core dump 有什么用？
- gdb 最常用哪些命令？
- ASan 和 valgrind 有什么区别？
- 线程问题通常怎么查？

---

## 31. C++ concepts / requires 专题

### 31.1 一句话抓本质
**concepts 的本质，是把“模板要求”写得更像人话。**

### 31.2 为什么出现 concepts
过去模板约束常靠 SFINAE / enable_if，表达能力强但可读性差。concepts 让约束更清晰。

### 31.3 基本形式
```cpp
template<typename T>
concept Addable = requires(T a, T b) {
    a + b;
};
```

### 31.4 `requires`
用来表达类型必须满足哪些操作、哪些返回要求。

### 31.5 常见坑
- concepts 当成普通类型别名理解
- requires 语法不熟
- 只会写，不知道它是在替代什么老方法

### 31.6 记忆口诀
> concepts 管模板门槛，requires 写清规则；比 enable_if 更像人话。

### 31.7 面试高频点
- concepts 解决了什么问题？
- requires 和 SFINAE 的关系？

---

## 32. C++ ranges 专题

### 32.1 一句话抓本质
**ranges 的本质，是把“算法 + 区间 + 惰性视图”组合得更自然。**

### 32.2 为什么重要
它代表现代 C++ 对 STL 风格的一次升级：更组合式、更声明式。

### 32.3 核心思想
- range 是“可遍历区间”
- view 是“惰性变换视图”
- 算法可以直接和 ranges 搭配

### 32.4 常见坑
- 把 view 当容器
- 忽略惰性求值
- 生命周期管理没想清楚

### 32.5 记忆口诀
> range 管区间，view 管变换；不一定立刻算，可能是惰性求值。

### 32.6 面试高频点
- ranges 和传统 STL 算法的区别？
- view 为什么不是容器？

---

## 33. C++ coroutine 专题

### 33.1 一句话抓本质
**coroutine 的本质，是“函数可以中途挂起，之后再从原地恢复”。**

### 33.2 适合什么场景
- 异步任务
- 生成器
- 协程调度框架

### 33.3 和线程的区别
线程是操作系统调度单位；coroutine 更轻量，更像语言层面的挂起/恢复机制。

### 33.4 常见坑
- 只背 co_await / co_yield 关键字，不理解调度模型
- 把 coroutine 当线程替代品

### 33.5 记忆口诀
> coroutine 不是线程，是函数能暂停；轻量在调度，关键在恢复。

### 33.6 面试高频点
- coroutine 和线程有什么区别？
- 生成器为什么适合 coroutine？

---

## 34. C++ allocator / memory_resource / pmr

### 34.1 一句话抓本质
**这组机制的本质，是“把内存分配策略从容器逻辑里拆出来”。**

### 34.2 为什么重要
高性能系统、定制内存池、低延迟场景，经常需要控制内存分配方式。

### 34.3 allocator
传统 STL 分配器接口。

### 34.4 `pmr`
polymorphic memory resource，现代 C++ 提供的更灵活内存资源模型。

### 34.5 常见坑
- 不理解 allocator 就强行自定义
- 把性能问题都归咎于分配器

### 34.6 记忆口诀
> allocator 管分配，pmr 管策略；不是每个项目都要手写，但高性能场景必须懂。

### 34.7 面试高频点
- allocator 是干什么的？
- pmr 相比传统 allocator 的价值是什么？

---

## 35. C++ span / view / 非拥有型对象设计

### 35.1 一句话抓本质
**非拥有型对象的本质，是“我只看数据，不拥有数据”。**

### 35.2 `span`
表示一段连续区间的视图。

### 35.3 `string_view`
表示字符串视图。

### 35.4 为什么这类设计重要
它让接口更轻、更快，同时表达“不会复制，不负责释放”。

### 35.5 常见坑
- 视图对象底层数据生命周期不足
- 把 view 当拥有型容器使用

### 35.6 记忆口诀
> view 只看不拥有，span 看连续区间，string_view 看字符串；轻量但最怕悬空。

### 35.7 面试高频点
- span 和 vector 有什么区别？
- string_view 为什么会悬空？

---

## 36. C++ ABI / 名字修饰 / 二进制兼容

### 36.1 一句话抓本质
**ABI 的本质，是“编译后的二进制之间怎么正确对接”。**

### 36.2 名字修饰
C++ 支持重载，所以编译后函数名通常会被改写。

### 36.3 二进制兼容
不同编译器、不同标准库版本、不同编译选项，可能导致 ABI 不兼容。

### 36.4 常见坑
- 动态库接口设计不稳
- 头文件改了，二进制兼容没考虑

### 36.5 记忆口诀
> 源码能看懂不代表二进制能对上；ABI 管接口，名字修饰管重载。

### 36.6 面试高频点
- 什么是 ABI？
- 为什么 C++ 动态库兼容性更复杂？

---

## 37. C++ 对齐 / padding / 内存布局

### 37.1 一句话抓本质
**这组知识的本质，是“对象在内存里并不总是紧密挨着的”。**

### 37.2 对齐为什么存在
为了提升访问效率，编译器会按平台要求对齐成员。

### 37.3 padding
成员之间为满足对齐插入的空白字节。

### 37.4 常见坑
- 误判结构体大小
- 网络/文件协议直接用结构体映射
- 忽略平台差异

### 37.5 记忆口诀
> 成员顺序影响大小，对齐决定空隙；结构体不是你想象中紧挨着排。**

### 37.6 面试高频点
- 为什么结构体大小比成员和还大？
- 对齐和 padding 是什么？

---

## 38. C++ Undefined Behavior（UB）专题

### 38.1 一句话抓本质
**UB 的本质，是“代码写出来了，但标准不保证结果”。**

### 38.2 为什么高频
C++ 很多危险 bug，不是“结果错了一点”，而是“标准直接不管你会发生什么”。

### 38.3 常见 UB 场景
- 越界访问
- 使用悬空指针
- 重复释放
- 未初始化变量读取
- 对真正 const 对象强改值

### 38.4 常见坑
- 误以为“我这次跑着没问题”就说明没错
- 把编译器当前行为当标准保证

### 38.5 记忆口诀
> UB 最危险的地方不是崩，而是有时不崩；这次能跑，不代表永远对。**

### 38.6 面试高频点
- 什么是未定义行为？
- 为什么 UB 比普通 bug 更危险？

---

## 39. C++ 性能优化专题

### 39.1 一句话抓本质
**性能优化的本质，是“先找瓶颈，再做有证据的改动”。**

### 39.2 常见优化方向
- 少拷贝，多 move
- 预分配 `reserve`
- 选对容器
- 减少锁竞争
- 避免不必要虚函数/动态分配

### 39.3 常见坑
- 没测就优化
- 过早优化
- 为了微优化牺牲可读性

### 39.4 记忆口诀
> 先量后改，先大后小；别拿猜想当优化，别拿复杂换微利。**

### 39.5 面试高频点
- 你怎么做性能优化？
- vector 为什么常比 list 快？
- 为什么“少拷贝、多连续内存”通常更快？

---

## 40. C++ 库设计与接口设计原则

### 40.1 一句话抓本质
**接口设计的本质，是“让使用者更难犯错，让正确用法更自然”。**

### 40.2 好接口的特点
- 语义清晰
- 所有权明确
- 生命周期明确
- 错误处理一致
- 不暴露不该暴露的细节

### 40.3 典型原则
- 尽量值语义
- 明确 const-correctness
- 非拥有型参数用引用 / view
- 资源拥有型返回值用对象/智能指针

### 40.4 常见坑
- 返回悬空引用
- 所有权不明确
- 同一接口混合多种错误策略
- 暴露过多实现细节

### 40.5 记忆口诀
> 好接口让人顺手，坏接口逼人踩坑；设计不是功能堆砌，而是约束清晰。**

### 40.6 面试高频点
- 你怎么判断一个 C++ 接口设计得好不好？
- 为什么现代 C++ 倾向值语义和 RAII？
- API 设计里所有权为什么这么重要？

