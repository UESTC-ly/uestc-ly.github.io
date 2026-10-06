
# C++资源库

这份笔记按“先认识 STL 和标准库，再逐个吃透常见头文件”的方式整理。目标不是背函数名，而是建立一张清晰的资源地图：**什么场景用什么头文件，怎么组合，容易错在哪。**

## 学习地图
1. C++ STL 教程
2. C++ 导入标准库
3. C++ 标准库
4. C++ 有用的资源
5. C++ 实例
6. C++ 测验（头文件速记）

---

## 1. C++ STL 教程

### 1.1 一句话抓本质
**STL 的本质，就是把“常用的数据结构、算法、遍历方式”封装成可以直接复用的工具箱。**

STL 不是一堆零散接口，而是一套协作体系：容器负责“存数据”，算法负责“处理数据”，迭代器负责“连接数据和算法”。

### 1.2 为什么 STL 很重要
- 少写重复代码
- 提高可读性和稳定性
- 让你更快完成业务逻辑
- 面试和工程里都高频出现

### 1.3 STL 的三大核心
- **容器**：`vector`、`list`、`map` 等
- **算法**：`sort`、`find`、`count`、`transform` 等
- **迭代器**：把容器和算法串起来

### 1.4 一个最典型的 STL 组合
```cpp
#include <vector>
#include <algorithm>
#include <iostream>

int main() {
    std::vector<int> v = {3, 1, 4, 1, 5};
    std::sort(v.begin(), v.end());
    for (int x : v) std::cout << x << ' ';
}
```

### 1.5 学 STL 的方法
1. 先记住容器的特点
2. 再记住算法的输入输出形式
3. 最后理解迭代器的意义

### 1.6 常见坑
- 以为 STL 是“万能的”，忽略复杂度
- 只会用容器，不会用算法
- 迭代器失效后还继续访问
- 把 `begin/end` 和下标混为一谈

### 1.7 记忆口诀
> **容器管存，算法管做，迭代器管连；先选对容器，再选对算法。**

---

## 2. C++ 导入标准库

### 2.1 一句话抓本质
**导入标准库的本质，就是告诉编译器：我需要哪些能力，以及这些能力从哪里来。**

### 2.2 两种常见方式
```cpp
#include <iostream>
using namespace std;
```
或更稳妥地写成：
```cpp
#include <iostream>

std::cout << "Hello" << std::endl;
```

### 2.3 你需要理解的两件事
- `#include` 是把头文件内容引入当前编译单元
- `std::` 是告诉编译器去标准命名空间里找名字

### 2.4 为什么不总是写 `using namespace std;`
因为大项目里名字很多，直接全放开容易冲突。教学代码里可以偷一点懒，工程代码里建议更克制。

### 2.5 常见坑
- 头文件没引入就用名字
- 混用 `stdio.h` 和 `iostream` 但没搞清风格
- 习惯性全局 `using namespace std;`

### 2.6 记忆口诀
> **先 include，再找名字；能写前缀，就别偷懒。**

---

## 3. C++ 标准库

### 3.1 一句话抓本质
**标准库就是 C++ 官方给你的“稳定基础设施”。**

### 3.2 标准库覆盖什么
- 输入输出
- 容器
- 算法
- 字符串
- 时间与并发
- 智能指针与资源管理
- 类型判断与异常
- 数学与随机数

### 3.3 为什么要认识标准库全景
你不需要把所有接口背下来，但必须知道“某类问题应该去哪个头文件里找答案”。这比死记函数更重要。

### 3.4 常见模块
- I/O：`<iostream>`、`<fstream>`、`<sstream>`
- 容器：`<vector>`、`<map>`、`<set>` 等
- 算法：`<algorithm>`、`<numeric>`、`<iterator>`
- 并发：`<thread>`、`<mutex>`、`<future>`
- 内存：`<memory>`、`<new>`
- 工具：`<utility>`、`<type_traits>`、`<chrono>`

### 3.5 学习策略
先从“用得最多”的头文件开始，再按分类扩展，不要一开始就把所有头文件当成死目录背。

### 3.6 记忆口诀
> **标准库不是目录表，而是问题地图。**

---

## 4. C++ 有用的资源

### 4.1 一句话抓本质
**好的资源能帮你少走弯路，尤其在查头文件、行为细节和复杂示例时。**

### 4.2 推荐资源
- **cppreference**：查标准库最常用
- **ISO C++ 网站**：了解语言方向和标准动态
- **GCC / Clang / MSVC 文档**：看编译器行为差异
- **Compiler Explorer**：看代码如何被编译器解释
- **标准库示例仓库/教程**：帮助你看实际用法

### 4.3 怎么用资源
- 先看接口签名
- 再看复杂度和说明
- 再看示例
- 最后自己写小测试验证

### 4.4 记忆口诀
> **查接口看 cppreference，验行为看编译器，最后自己跑一遍。**

---

## 5. C++ 实例

### 5.1 最好的学习方式
**看完头文件，不如直接看“头文件怎么组合起来解决问题”。**

### 5.2 示例 1：读文件并统计单词
```cpp
#include <fstream>
#include <sstream>
#include <string>
#include <iostream>

int main() {
    std::ifstream fin("input.txt");
    std::string line, word;
    int count = 0;
    while (std::getline(fin, line)) {
        std::stringstream ss(line);
        while (ss >> word) ++count;
    }
    std::cout << count << std::endl;
}
```

### 5.3 示例 2：排序并去重
```cpp
#include <vector>
#include <algorithm>
#include <iostream>

int main() {
    std::vector<int> v = {3, 1, 3, 2, 1};
    std::sort(v.begin(), v.end());
    v.erase(std::unique(v.begin(), v.end()), v.end());
}
```

### 5.4 示例 3：线程任务
```cpp
#include <thread>
#include <iostream>

void work() { std::cout << "work\n"; }

int main() {
    std::thread t(work);
    t.join();
}
```

### 5.5 记忆口诀
> **资源不是背出来的，是组合练出来的。**

---

## 6. C++ 测验（头文件速记）

### <iostream>

#### 一句话抓本质
标准输入输出流，负责把程序和终端连接起来。

#### 适用场景
控制台打印、读取命令行输入、调试输出。

#### 常见用法
`std::cout` 输出，`std::cin` 输入，`std::cerr` 报错。

#### 示例
```cpp
#include <iostream>
std::cout << "Hi" << std::endl;
```

#### 易错点
和 `printf` 混用时要注意缓冲；忘记加 `std::` 也很常见。

#### 记忆口诀
> 输入输出先想 iostream，终端交互最常见。

### <fstream>

#### 一句话抓本质
文件流，把数据和磁盘文件连接起来。

#### 适用场景
日志、配置、读写文本/二进制文件。

#### 常见用法
`ifstream` 读，`ofstream` 写，`fstream` 读写。

#### 示例
```cpp
#include <fstream>
std::ifstream fin("a.txt");
```

#### 易错点
路径、权限、打开模式最容易出问题。

#### 记忆口诀
> 读写文件先开流，打开失败先别急。

### <sstream>

#### 一句话抓本质
字符串流，让字符串像文件一样被解析和拼装。

#### 适用场景
拆分文本、格式转换、临时缓冲。

#### 常见用法
`istringstream` 读字符串，`ostringstream` 拼字符串，`stringstream` 双向。

#### 示例
```cpp
#include <sstream>
std::stringstream ss; ss << 123;
```

#### 易错点
把它当普通字符串容器会误解它的解析能力。

#### 记忆口诀
> 字符串想分解，先找 sstream。

### <iomanip>

#### 一句话抓本质
格式控制头，专门管输出长相。

#### 适用场景
对齐、补零、定宽、定小数位。

#### 常见用法
`setw`、`setfill`、`setprecision`、`fixed`。

#### 示例
```cpp
#include <iomanip>
std::cout << std::setw(6) << std::setfill('0') << 42;
```

#### 易错点
格式控制符会影响后续输出，常常要记得恢复。

#### 记忆口诀
> 想让输出更漂亮，iomanip 来帮忙。

### <array>

#### 一句话抓本质
固定大小数组容器，语义更清晰。

#### 适用场景
编译期大小已知的场景。

#### 常见用法
支持迭代器、`size()`、`front()`、`back()`。

#### 示例
```cpp
#include <array>
std::array<int, 3> a{1,2,3};
```

#### 易错点
别把它当裸数组，`size()` 是强项。

#### 记忆口诀
> 固定长度要安全，array 比裸数组更稳。

### <vector>

#### 一句话抓本质
最常用动态数组，连续内存，随机访问快。

#### 适用场景
几乎所有“列表型数据”都能先想到它。

#### 常见用法
`push_back`、`size`、`reserve`、`resize`。

#### 示例
```cpp
#include <vector>
std::vector<int> v = {1,2,3};
```

#### 易错点
频繁插入中间会慢；扩容可能让迭代器失效。

#### 记忆口诀
> 动态数组先想 vector，快读快写都好用。

### <list>

#### 一句话抓本质
双向链表，适合频繁插入删除。

#### 适用场景
需要在中间高频插入/删除且不关心随机访问。

#### 常见用法
`push_front`、`push_back`、`insert`、`erase`。

#### 示例
```cpp
#include <list>
std::list<int> l; l.push_back(1);
```

#### 易错点
不能像 vector 一样用下标随机访问。

#### 记忆口诀
> 中间常改用 list，链上操作更灵活。

### <forward_list>

#### 一句话抓本质
单向链表，更省空间，前向遍历。

#### 适用场景
内存更敏感、只需要向前遍历。

#### 常见用法
`push_front`、`insert_after`、`erase_after`。

#### 示例
```cpp
#include <forward_list>
std::forward_list<int> fl = {1,2,3};
```

#### 易错点
接口和 list 不一样，很多操作是 after 风格。

#### 记忆口诀
> 单向链表 forward_list，省空间但要顺着走。

### <deque>

#### 一句话抓本质
双端队列，两头都能高效进出。

#### 适用场景
两端频繁插入删除、又想保留随机访问。

#### 常见用法
`push_front`、`push_back`、`pop_front`、`pop_back`。

#### 示例
```cpp
#include <deque>
std::deque<int> d; d.push_front(1);
```

#### 易错点
它不是完全连续的一整块内存。

#### 记忆口诀
> 两头都要常操作，deque 很合适。

### <stack>

#### 一句话抓本质
栈适配器，后进先出。

#### 适用场景
回退、递归模拟、表达式求值。

#### 常见用法
`push`、`pop`、`top`。

#### 示例
```cpp
#include <stack>
std::stack<int> st; st.push(1);
```

#### 易错点
不能遍历内部元素，只能操作栈顶。

#### 记忆口诀
> 后进先出就是栈，顶上动手最自然。

### <queue>

#### 一句话抓本质
队列适配器，先进先出。

#### 适用场景
任务调度、消息排队、缓存队列。

#### 常见用法
`push`、`pop`、`front`、`back`。

#### 示例
```cpp
#include <queue>
std::queue<int> q; q.push(1);
```

#### 易错点
只能从队头/队尾做有限操作。

#### 记忆口诀
> 先进先出叫 queue，排队逻辑最直观。

### <priority_queue>

#### 一句话抓本质
优先队列，始终让“最重要的元素”在顶上。

#### 适用场景
Top-K、调度、最短路的辅助结构。

#### 常见用法
`push`、`pop`、`top`。

#### 示例
```cpp
#include <queue>
std::priority_queue<int> pq;
```

#### 易错点
不要把它当普通排序容器，它只保证顶元素最优。

#### 记忆口诀
> 谁最重要谁先出，priority_queue。

### <set>

#### 一句话抓本质
有序去重集合。

#### 适用场景
需要自动去重且保持排序。

#### 常见用法
`insert`、`find`、`erase`。

#### 示例
```cpp
#include <set>
std::set<int> s = {3,1,2};
```

#### 易错点
插入结果是有序的，不是原顺序。

#### 记忆口诀
> 要去重还要排序，set 很省心。

### <unordered_set>

#### 一句话抓本质
无序去重集合，哈希实现。

#### 适用场景
只关心查找快，不关心顺序。

#### 常见用法
`insert`、`find`、`count`。

#### 示例
```cpp
#include <unordered_set>
std::unordered_set<int> us;
```

#### 易错点
平均快不等于绝对快，哈希冲突要知道。

#### 记忆口诀
> 无序去重查得快，unordered_set。

### <map>

#### 一句话抓本质
有序键值表，按键排序的字典。

#### 适用场景
键值映射、按键遍历、范围查询。

#### 常见用法
`operator[]`、`insert`、`find`。

#### 示例
```cpp
#include <map>
std::map<std::string,int> m;
```

#### 易错点
`operator[]` 可能会插入默认值。

#### 记忆口诀
> 要有序字典就找 map。

### <unordered_map>

#### 一句话抓本质
无序键值表，哈希字典。

#### 适用场景
查找频繁、只关心平均性能。

#### 常见用法
`operator[]`、`emplace`、`find`。

#### 示例
```cpp
#include <unordered_map>
std::unordered_map<std::string,int> um;
```

#### 易错点
键必须可哈希，且注意冲突。

#### 记忆口诀
> 字典要快就 unordered_map。

### <bitset>

#### 一句话抓本质
定长二进制位集合。

#### 适用场景
位运算、状态压缩、位掩码展示。

#### 常见用法
`set`、`reset`、`flip`、`test`。

#### 示例
```cpp
#include <bitset>
std::bitset<8> b(\"1010\");
```

#### 易错点
位数是编译期固定的。

#### 记忆口诀
> 二进制状态想直观，bitset 来显示。

### <algorithm>

#### 一句话抓本质
算法大本营，提供大量通用算法。

#### 适用场景
排序、查找、变换、区间操作。

#### 常见用法
`sort`、`find`、`copy`、`count`、`remove`。

#### 示例
```cpp
#include <algorithm>
std::sort(v.begin(), v.end());
```

#### 易错点
`remove` 不是删除容器元素，而是移动并返回新尾。

#### 记忆口诀
> 算法一大堆，先认 algorithm。

### <iterator>

#### 一句话抓本质
迭代器工具头，帮助你操控遍历位置。

#### 适用场景
移动迭代器、插入迭代器、流迭代器。

#### 常见用法
`advance`、`distance`、`back_inserter`。

#### 示例
```cpp
#include <iterator>
std::advance(it, 2);
```

#### 易错点
不同迭代器类别支持的操作不同。

#### 记忆口诀
> 想把迭代器玩明白，iterator 很关键。

### <functional>

#### 一句话抓本质
函数对象和调用器工具头。

#### 适用场景
自定义比较、回调、绑定、适配。

#### 常见用法
`greater`、`less`、`bind`、`function`。

#### 示例
```cpp
#include <functional>
std::sort(v.begin(), v.end(), std::greater<int>());
```

#### 易错点
`bind` 时代码可读性可能下降。

#### 记忆口诀
> 比较器回调要灵活，functional。

### <numeric>

#### 一句话抓本质
数值算法头，做累计、内积、前缀处理。

#### 适用场景
求和、乘积、内积、部分扫描。

#### 常见用法
`accumulate`、`inner_product`、`partial_sum`。

#### 示例
```cpp
#include <numeric>
auto s = std::accumulate(v.begin(), v.end(), 0);
```

#### 易错点
初值类型会影响结果类型。

#### 记忆口诀
> 求和统计别手写，numeric 很顺手。

### <complex>

#### 一句话抓本质
复数类型支持。

#### 适用场景
信号处理、数学计算、工程仿真。

#### 常见用法
`std::complex<double>`、实部虚部运算。

#### 示例
```cpp
#include <complex>
std::complex<double> z{1, 2};
```

#### 易错点
别忘了复数不是字符串，它是数学对象。

#### 记忆口诀
> 实部虚部一起算，complex 最自然。

### <valarray>

#### 一句话抓本质
面向数值批量计算的数组类型。

#### 适用场景
科学计算、向量化表达。

#### 常见用法
支持整体运算、切片、统计。

#### 示例
```cpp
#include <valarray>
std::valarray<double> a = {1,2,3};
```

#### 易错点
适用面比 vector 小，别强行替代容器。

#### 记忆口诀
> 数值批处理想简洁，valarray 可考虑。

### <cmath>

#### 一句话抓本质
C 风格数学函数的 C++ 版本入口。

#### 适用场景
三角、指数、对数、开方、取整。

#### 常见用法
`sqrt`、`pow`、`sin`、`cos`、`fabs`。

#### 示例
```cpp
#include <cmath>
double r = std::sqrt(9.0);
```

#### 易错点
注意重载和类型，整数传入可能被提升。

#### 记忆口诀
> 数学函数找 cmath，开方三角都在这。

### <string>

#### 一句话抓本质
现代字符串类。

#### 适用场景
文本拼接、查找、替换、切片。

#### 常见用法
`size`、`substr`、`find`、`append`。

#### 示例
```cpp
#include <string>
std::string s = \"hello\";
```

#### 易错点
别把它和 C 字符串混得太乱。

#### 记忆口诀
> 文本处理先用 string，安全又顺手。

### <regex>

#### 一句话抓本质
正则表达式支持。

#### 适用场景
文本校验、提取、匹配。

#### 常见用法
`regex`、`regex_match`、`regex_search`。

#### 示例
```cpp
#include <regex>
std::regex re(\"\\\\d+\");
```

#### 易错点
正则能强大也能难读，别写成迷宫。

#### 记忆口诀
> 文本匹配有规则，regex 来帮忙。

### <ctime>

#### 一句话抓本质
C 风格时间接口。

#### 适用场景
旧代码、简单时间戳、兼容场景。

#### 常见用法
`time`、`localtime`、`strftime`。

#### 示例
```cpp
#include <ctime>
std::time_t now = std::time(nullptr);
```

#### 易错点
`localtime` 返回静态缓冲，不可随意长期保存。

#### 记忆口诀
> 老时间接口要兼容，ctime 还能见。

### <chrono>

#### 一句话抓本质
现代时间库，类型安全、可表达单位。

#### 适用场景
计时、时间点、持续时间、性能测试。

#### 常见用法
`duration`、`time_point`、`system_clock`、`steady_clock`。

#### 示例
```cpp
#include <chrono>
auto now = std::chrono::system_clock::now();
```

#### 易错点
做性能计时优先用 `steady_clock`。

#### 记忆口诀
> 现代时间想精确，chrono 最顺手。

### <thread>

#### 一句话抓本质
线程支持，启动并发任务。

#### 适用场景
并行计算、后台任务、响应优化。

#### 常见用法
`std::thread`、`join`、`detach`。

#### 示例
```cpp
#include <thread>
std::thread t(work); t.join();
```

#### 易错点
忘记 join/detach 会出大问题。

#### 记忆口诀
> 多线程第一步，thread 先启动。

### <mutex>

#### 一句话抓本质
互斥锁，保护共享资源。

#### 适用场景
多个线程同时写同一份数据时。

#### 常见用法
`lock_guard`、`unique_lock`、`mutex`。

#### 示例
```cpp
#include <mutex>
std::lock_guard<std::mutex> lock(m);
```

#### 易错点
不要忘记加锁范围，死锁和性能问题都可能来。

#### 记忆口诀
> 共享数据要上锁，mutex 来守门。

### <condition_variable>

#### 一句话抓本质
条件变量，让线程按条件等待和唤醒。

#### 适用场景
生产者消费者、事件通知。

#### 常见用法
`wait`、`notify_one`、`notify_all`。

#### 示例
```cpp
#include <condition_variable>
cv.wait(lock, []{ return ready; });
```

#### 易错点
必须和互斥锁配合使用。

#### 记忆口诀
> 等条件再继续，condition_variable。

### <future>

#### 一句话抓本质
异步结果和任务封装。

#### 适用场景
异步计算、任务回传、并发结果收集。

#### 常见用法
`std::async`、`future`、`promise`。

#### 示例
```cpp
#include <future>
auto f = std::async([]{ return 42; });
```

#### 易错点
别忘了获取结果，否则可能忽略异常。

#### 记忆口诀
> 异步有回执，future 最合适。

### <atomic>

#### 一句话抓本质
原子操作，保证并发下的基本安全。

#### 适用场景
计数器、状态标志、无锁并发基础。

#### 常见用法
`atomic<int>`、`load`、`store`、`fetch_add`。

#### 示例
```cpp
#include <atomic>
std::atomic<int> cnt{0};
```

#### 易错点
原子不等于万能同步，复杂场景还要配合其他机制。

#### 记忆口诀
> 并发计数要稳，atomic 先上场。

### <type_traits>

#### 一句话抓本质
编译期类型判断和类型变换工具。

#### 适用场景
模板约束、条件编译、泛型编程。

#### 常见用法
`is_integral`、`remove_reference`、`enable_if`。

#### 示例
```cpp
#include <type_traits>
static_assert(std::is_integral_v<int>);
```

#### 易错点
类型推导很强，但看不懂就会很痛苦。

#### 记忆口诀
> 模板想变聪明，type_traits。

### <typeinfo>

#### 一句话抓本质
运行时类型信息。

#### 适用场景
多态、调试、类型识别。

#### 常见用法
`typeid`、查看对象动态类型。

#### 示例
```cpp
#include <typeinfo>
std::cout << typeid(x).name();
```

#### 易错点
名字输出是实现相关的，不可当稳定接口。

#### 记忆口诀
> 想看类型标签，typeinfo 来帮忙。

### <exception>

#### 一句话抓本质
异常体系的基础头。

#### 适用场景
统一异常捕获、标准异常基类。

#### 常见用法
`std::exception`、`what()`。

#### 示例
```cpp
#include <exception>
catch (const std::exception& e) { }
```

#### 易错点
只抓大类会丢失细节。

#### 记忆口诀
> 异常总入口，exception 先认识。

### <stdexcept>

#### 一句话抓本质
标准运行时异常头。

#### 适用场景
参数非法、越界、逻辑错误。

#### 常见用法
`runtime_error`、`invalid_argument`、`out_of_range`。

#### 示例
```cpp
#include <stdexcept>
throw std::runtime_error(\"bad\");
```

#### 易错点
异常信息要具体，别只写“error”。

#### 记忆口诀
> 运行时出问题，stdexcept 很常用。

### <cstdio>

#### 一句话抓本质
C 风格 I/O 头。

#### 适用场景
兼容旧代码、格式化输出、底层读写。

#### 常见用法
`printf`、`scanf`、`fopen`、`fclose`。

#### 示例
```cpp
#include <cstdio>
std::printf(\"%d\\n\", 10);
```

#### 易错点
格式串和参数类型不匹配是经典坑。

#### 记忆口诀
> 老式输入输出，cstdio 还常见。

### <cstdint>

#### 一句话抓本质
固定宽度整数类型。

#### 适用场景
协议、序列化、跨平台数据。

#### 常见用法
`int32_t`、`uint64_t` 等。

#### 示例
```cpp
#include <cstdint>
std::int32_t x = 0;
```

#### 易错点
别假设 `int` 在所有平台位宽都一样。

#### 记忆口诀
> 跨平台要稳，cstdint 最靠谱。

### <memory>

#### 一句话抓本质
智能指针与资源管理头。

#### 适用场景
对象生命周期管理、避免裸指针泄漏。

#### 常见用法
`unique_ptr`、`shared_ptr`、`weak_ptr`、`make_unique`。

#### 示例
```cpp
#include <memory>
auto p = std::make_unique<int>(42);
```

#### 易错点
共享所有权要谨慎，循环引用会出事。

#### 记忆口诀
> 资源管理想省心，memory 最关键。

### <new>

#### 一句话抓本质
与动态内存相关的底层支持。

#### 适用场景
placement new、自定义分配、对象重建。

#### 常见用法
`new`、`placement new`、`std::bad_alloc`。

#### 示例
```cpp
#include <new>
new (buf) T();
```

#### 易错点
placement new 只构造对象，不负责分配内存。

#### 记忆口诀
> 想碰底层内存，new 这头文件要认。

### <utility>

#### 一句话抓本质
通用工具头。

#### 适用场景
交换、移动、成对数据。

#### 常见用法
`pair`、`move`、`swap`、`forward`。

#### 示例
```cpp
#include <utility>
auto p = std::make_pair(1, 2);
```

#### 易错点
`move` 不是“搬家完成”，只是允许移动。

#### 记忆口诀
> 小工具很多样，utility 最杂但常用。

### <random>

#### 一句话抓本质
现代随机数设施。

#### 适用场景
随机测试、抽样、模拟。

#### 常见用法
`mt19937`、`uniform_int_distribution`。

#### 示例
```cpp
#include <random>
std::mt19937 gen(std::random_device{}());
```

#### 易错点
不要依赖 `rand()` 的低质量随机性。

#### 记忆口诀
> 随机别靠手气，random 更专业。

### <locale>

#### 一句话抓本质
本地化与字符分类支持。

#### 适用场景
地区格式、字符判断、流本地化。

#### 常见用法
`locale`、`use_facet`、流的区域设置。

#### 示例
```cpp
#include <locale>
std::locale::global(std::locale(\"\"));
```

#### 易错点
本地化涉及平台差异，别想当然。

#### 记忆口诀
> 想处理地域格式，locale 会派上用场。

### <codecvt>

#### 一句话抓本质
字符编码转换相关头，偏旧式。

#### 适用场景
老项目字符集转换、兼容遗留代码。

#### 常见用法
`wstring_convert` 等旧接口。

#### 示例
```cpp
#include <codecvt>
// 旧项目中可能会见到字符编码转换
```

#### 易错点
现代新项目尽量少依赖它，关注平台/库替代方案。

#### 记忆口诀
> 编码转换有历史，codecvt 记旧不记新。

### <cassert>

#### 一句话抓本质
断言检查头。

#### 适用场景
调试阶段验证假设、抓早期错误。

#### 常见用法
`assert(expr)`。

#### 示例
```cpp
#include <cassert>
assert(x > 0);
```

#### 易错点
断言通常在发布版可能被关闭。

#### 记忆口诀
> 假设必须成立时，assert 来验收。

### <cwchar>

#### 一句话抓本质
宽字符操作头。

#### 适用场景
Unicode 兼容、宽字符接口。

#### 常见用法
`wchar_t`、`wcslen`、`wcscpy`。

#### 示例
```cpp
#include <cwchar>
const wchar_t* s = L\"你好\";
```

#### 易错点
宽字符不是普通窄字符串，接口不同。

#### 记忆口诀
> 宽字符要处理，cwchar 来支持。

### <climits>

#### 一句话抓本质
整型极值常量头。

#### 适用场景
边界判断、数值范围。

#### 常见用法
`INT_MAX`、`INT_MIN` 等。

#### 示例
```cpp
#include <climits>
if (x == INT_MAX) {}
```

#### 易错点
别手写魔法数字，优先用标准极值。

#### 记忆口诀
> 整型边界想清楚，climits 最直接。

### <cfloat>

#### 一句话抓本质
浮点极值常量头。

#### 适用场景
浮点范围、精度边界判断。

#### 常见用法
`FLT_MAX`、`DBL_MAX`、`FLT_EPSILON`。

#### 示例
```cpp
#include <cfloat>
if (std::fabs(a-b) < DBL_EPSILON) {}
```

#### 易错点
浮点比较不能简单用 `==`。

#### 记忆口诀
> 浮点边界要知道，cfloat 很重要。

### <cstdlib>

#### 一句话抓本质
C 标准通用工具头。

#### 适用场景
转换、内存、随机数、退出。

#### 常见用法
`strtol`、`atoi`、`rand`、`exit`、`system`。

#### 示例
```cpp
#include <cstdlib>
int n = std::atoi(\"123\");
```

#### 易错点
`rand()` 质量一般，`system` 也要慎用。

#### 记忆口诀
> 通用工具很多项，cstdlib 常见。

### <numbers>

#### 一句话抓本质
数学常量头，C++20 以后常用。

#### 适用场景
高精度数学常量、公式编写。

#### 常见用法
`std::numbers::pi`、`e` 等。

#### 示例
```cpp
#include <numbers>
double p = std::numbers::pi;
```

#### 易错点
需要 C++20 支持。

#### 记忆口诀
> 圆周率常量别手敲，numbers 更标准。


---

## 7. C++ 测验复习清单

- `iostream`：终端输入输出
- `fstream`：文件读写
- `sstream`：字符串解析
- `iomanip`：格式控制
- `array/vector/list/forward_list/deque`：基础容器
- `stack/queue/priority_queue`：容器适配器
- `set/map/unordered_*`：有序与无序关联容器
- `algorithm/iterator/functional/numeric`：算法与通用工具
- `complex/valarray/cmath/string/regex`：数值与文本处理
- `ctime/chrono`：时间
- `thread/mutex/condition_variable/future/atomic`：并发
- `type_traits/typeinfo/exception/stdexcept`：类型与异常
- `cstdio/cstdint/memory/new/utility/random/locale/codecvt`：底层与工具
- `cassert/cwchar/climits/cfloat/cstdlib/numbers`：调试、字符、边界、数学常量

## 学习建议
先记住“头文件解决什么问题”，再记具体函数名。只要你能在 10 秒内说出一个头文件的用途、典型场景和常见坑，就已经真正掌握它了。
