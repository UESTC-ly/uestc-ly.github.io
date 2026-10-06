# C++基础刷题记录

> 目标：做一道题，会一类题。  
> 记录原则：每题给出结论、原因、易混点、通法、记忆口诀。

---

## 题目1：构造函数返回类型判断

### 题目
构造方法用于创建类的实例对象，构造方法名应与类名相同，返回类型为 `void`。

### 答案
**错误**

### 原因
1. 构造函数名确实通常与类名相同。
2. 但构造函数**没有返回类型**，不是 `void`。
3. 如果写成 `void ClassName()`，那它就不是构造函数，而是普通成员函数。

### 易混点
1. **构造函数**：没有返回类型，连 `void` 都不能写。
2. **析构函数**：也没有返回类型，连 `void` 都不能写。
3. **普通成员函数**：才可以写 `void`、`int`、`double` 等返回类型。

### 一类题怎么做
判断构造/析构函数时，优先看两点：
1. 名字是否符合规则；
2. 是否**完全没有返回类型**。

### 记忆口诀
**构造析构都无返回，写了 `void` 反而错。**

---

## 题目2：`double` 大小判断

### 题目
C++语言中，64位环境下 `double` 类型数据占 8 个字节。说法是否正确？

### 答案
**正确**（按常见考试语境选 A）

### 原因
1. 在主流 C/C++ 编译环境中，`double` 通常就是 8 字节。
2. 题目里的“64位环境”容易让人误以为是因为系统 64 位才决定了 `double = 8` 字节。
3. 实际上，`double` 是否为 8 字节，主要由编译器和平台实现决定；只是主流环境下通常确实是 8 字节。

### 易混点
1. **64位系统 ≠ 所有类型都变成 8 字节**。
2. 常见情况：
   - `char`：1 字节
   - `short`：2 字节
   - `int`：通常 4 字节
   - `double`：通常 8 字节
   - 指针：32 位下常见 4 字节，64 位下常见 8 字节
3. 真正和 32/64 位强相关的，最典型是**指针大小**。

### 一类题怎么做
1. 如果题目问“主流环境中的常见大小”，按常识作答。
2. 如果题目问“标准是否保证”，就要更严谨：很多类型大小不是标准硬性写死的。

### 记忆口诀
**`double` 通常 8 字节；指针大小更看位数。**

---

## 题目3：`static` + 构造/析构 + 输出结果

### 题目
给定含 `static` 成员变量、构造函数和析构函数的程序，问最终输出结果。

### 答案
输出：

```cpp
n=0
```

### 原因
1. `static int n` 是**类静态成员**，属于整个类，所有对象共享这一份。
2. 执行 `cla *p = new cla;` 时，调用构造函数，`n++`，所以 `n` 从 `0` 变成 `1`。
3. 执行 `delete p;` 时，调用析构函数，`n--`，所以 `n` 从 `1` 变回 `0`。
4. 最后 `cla::get_n()` 返回 `0`，所以输出 `n=0`。

### 执行过程
1. 初始：`n = 0`
2. `new cla`：构造 → `n = 1`
3. `delete p`：析构 → `n = 0`
4. 输出：`n=0`

### 易混点
1. `static` 成员变量属于**类**，不属于某个具体对象。
2. `new` 会调用构造函数，`delete` 会调用析构函数。
3. 如果只 `new` 不 `delete`，那这里输出就会是 `n=1`。
4. `cla::get_n()` 这种写法说明是**类名直接访问静态成员函数**。

### 一类题怎么做
遇到“构造 + 析构 + `static` 计数器”题，按时间顺序模拟：
1. 先看静态变量初值；
2. 看每次构造如何变化；
3. 看每次析构如何变化；
4. 最后看输出发生在 `delete` 前还是 `delete` 后。

### 记忆口诀
**`static` 看全类。**

---

## string 常用操作（字符串题速查）

`std::string` 可理解为长度可变的字符数组。使用 `<string>`；下列示例默认 `using namespace std;`。

### 长度、访问与遍历

| 操作 | 含义 |
|---|---|
| `s.size()` / `s.length()` | 字符串长度 |
| `s.empty()` | 是否为空 |
| `s[i]` | 访问或修改字符，正常字符下标为 `[0, s.size())` |
| `s.front()` / `s.back()` | 首字符 / 尾字符，要求非空 |

`size()` 返回无符号整数。倒序下标先转为 `int` 再减一，避免空字符串时无符号下溢（适用于长度可由 int 表示的刷题输入）：

```cpp
for (int i = static_cast<int>(s.size()) - 1; i >= 0; i--) {
    // 使用 s[i]
}
```

### 添加、删除与清空

| 操作 | 含义 |
|---|---|
| `s.push_back(c)` | 末尾添加一个字符 |
| `s += c` / `s += str` | 末尾添加字符 / 字符串 |
| `s.append(str)` | 拼接字符串 |
| `a + b` | 生成拼接后的新字符串（至少一方为 string 的常用情形） |
| `s.pop_back()` | 删除末尾字符，要求非空，不返回被删字符 |
| `s.erase(pos, count)` | 从 pos 开始删除 count 个字符 |
| `s.erase(pos)` | 删除 pos 到末尾的内容 |
| `s.clear()` | 清空内容 |

**单字符用 `push_back`，拼字符串用 `+=`。** `string` 没有 `pop()`。

```cpp
string s = "hello";
s.push_back(' ');
s += "world";  // "hello world"

if (!s.empty()) {
    char c = s.back();
    s.pop_back();
}
```

### 字符串数组与追加字符

```cpp
vector<string> rows(3);  // 三个空字符串，需要 <vector>
int row = 1;
char c = 'A';
rows[row] += c;          // rows[1] 变成 "A"
rows[1] += 'P';          // "AP"
rows[1] += 'L';          // "APL"
```

- `rows`：存放字符串的数组，初始内容为 `["", "", ""]`。
- `rows[row]`：第 row 行的整个字符串。
- `rows[row][j]`：第 row 行中下标为 j 的字符，访问时要保证两层下标有效。
- `rows[row] += c`：把字符 c 追加到当前行末尾，等价于 `rows[row].push_back(c)`；这里是字符串拼接，不是数字加法。

记忆：**先用 row 选一张纸条，再在纸条末尾写一个字符。**

应用：[[模拟/Z 字形变换（6）]]。

### 子串、插入与替换

```cpp
string s = "abcdef";
string a = s.substr(2, 3);  // "cde"，原字符串不变
string b = s.substr(2);     // "cdef"，取到末尾
```

**`substr(起点, 长度)`，第二个参数不是终点。**

| 区间 | 提取写法 |
|---|---|
| `[left, right]` | `s.substr(left, right - left + 1)` |
| `[left, right)` | `s.substr(left, right - left)` |

迭代器也遵循左闭右开，`string(s.begin() + left, s.begin() + right)` 提取 `[left, right)`。

```cpp
string s = "hello";
s.insert(5, " world");      // "hello world"
s.replace(6, 5, "C++");     // "hello C++"
// replace(起点, 原内容长度, 新字符串)
```

### 查找

```cpp
string s = "abcabc";
size_t p1 = s.find("bc");     // 1，第一次出现
size_t p2 = s.find("bc", 2);  // 4，从下标 2 开始找
size_t p3 = s.rfind("bc");    // 4，最后一次出现

if (s.find("xyz") == string::npos) {
    // 找不到
}
```

不能直接写 `if (s.find(...))` 判断是否找到：位置 0 也可能是有效结果。**查找返回位置，未找到用 `string::npos` 判断。**

### 反转、排序与比较

`reverse`、`sort` 是 `<algorithm>` 中的独立函数，不是 string 成员方法。

```cpp
reverse(s.begin(), s.end());
sort(s.begin(), s.end());
// 反转闭区间 [left, right]
reverse(s.begin() + left, s.begin() + right + 1);
```

不存在 `s.reverse()`。字符串可直接用 `==`、`!=`、`<` 等比较，大小比较采用字典序，因此 `string("10") < string("2")` 为 true，并非数值比较。

### 数字转换

| 独立函数 | 含义 |
|---|---|
| `to_string(num)` | 数字转字符串 |
| `stoi(s)` | 字符串转 int |
| `stoll(s)` | 字符串转 long long |

无法转换或数值超出范围时，`stoi`、`stoll` 会抛出异常。单个数字字符可直接转换：

```cpp
int x = '7' - '0';  // 7
char c = 7 + '0';   // '7'，仅用于 0～9
```

### 分词与分隔符拼接模板

使用 `<sstream>`，自动跳过空白，每次读取一个单词：

```cpp
stringstream ss(s);
string word;
while (ss >> word) {
    // 处理 word
}
```

只在元素之间添加空格，避免首尾空格：

```cpp
if (!ans.empty()) {
    ans += ' ';
}
ans += word;
```

应用：[[双指针/反转字符串中的单词（151）]]。

### 复杂度与方法总结

- 获取长度、判空、访问字符为 O(1)。
- 提取长度为 k 的子串需要 O(k) 时间和存储空间。
- 尾部添加单字符通常按均摊 O(1) 分析；追加 k 个字符需计入字符复制和可能的扩容。
- 头部或中间插入、删除通常需要移动后续字符。循环反复在头部拼接可能变成 O(n²)。

**先分清操作单位：字符用字符接口，字符串用拼接或子串接口；涉及区间，先明确左闭右开，再计算长度。**

## unordered_map 的查询与默认值

`unordered_map<char, int>` 保存“字符 → 整数”的映射，没有 `vector(n, value)` 那样把所有位置统一填充的构造方式。

```cpp
unordered_map<char, int> pos;
pos.count('a');      // 0，不插入元素
auto it = pos.find('a'); // pos.end()，不插入元素
int x = pos['a'];    // 插入 {'a', 0}，x 为 0
```

不存在的键通过 `operator[]` 访问时，`int` 值初始化为 `0`，不能把这个默认值改成 `-1`。可显式初始化指定键，但这不会改变其他键的默认插入行为：

```cpp
unordered_map<char, int> pos{{'a', -1}, {'b', -1}};
// pos['c'] 仍会插入 0
```

记录字符最后出现位置时，推荐先判断存在，再读取旧位置：

```cpp
if (pos.count(c) && pos[c] >= left) {
    left = pos[c] + 1;
}
pos[c] = right;
```

`&&` 短路求值：键不存在时，不执行右侧的 `pos[c]`。也可使用 `find`：

```cpp
auto it = pos.find(c);
if (it != pos.end() && it->second >= left) {
    left = it->second + 1;
}
```

如果已知输入字符编码都在 `0～127`，可以用 `vector<int> pos(128, -1)`，一次填充所有位置。不要把这个大小用于任意字节输入；常见 8 位字节环境中，可用长度 `256` 并将字符转为 `unsigned char` 后索引。UTF-8 的一个字符可能占多个字节，不能直接当作单个 `char` 处理。

应用：[无重复字符的最长子串](../滑动窗口/滑动窗口与字符统计（3、438）.md)。

## const、引用与指针

`const` 限制通过当前变量或访问方式修改值。

```cpp
const int n = 10; // 等价于 int const n = 10
// n = 20;       // 错误，普通局部常量需要初始化，之后不能赋值

int x = 10;
const int& ref = x;
// ref = 20;     // 错误，不能通过只读引用修改 x
x = 20;          // 正确，x 本身不是常量，ref 读到的也是 20
```

### 函数参数怎么选

| 写法 | 传入普通 vector 变量时是否复制 | 能否通过参数修改原对象 |
|---|---|---|
| `vector<int> v` | 复制 | 不能，只修改副本 |
| `vector<int>& v` | 不复制 | 可以 |
| `const vector<int>& v` | 不复制 | 不可以 |

只读大型容器常用 `const T&`；需要修改调用方容器则用 `T&`。例如生命游戏的邻居统计函数使用只读引用，而更新棋盘的主函数使用普通引用。

### 为什么引用后不能再写 const

```cpp
// 错误：const vector<vector<int>>& const board
// 正确：const vector<vector<int>>& board
```

前面的 `const` 限制通过引用修改矩阵；`&` 后的 `const` 试图修饰引用本身，C++ 不允许这种声明。引用绑定后本来就不能重新绑定到另一个对象。

```cpp
int a = 1, b = 2;
int& ref = a;
ref = b; // 给 a 赋值为 2，不是让 ref 改为引用 b
```

### 只读引用不是快照

```cpp
vector<vector<int>> snap = board;        // 复制，保存独立旧状态
const vector<vector<int>>& view = board; // 只读别名，仍指向同一对象
```

修改 `board` 会反映到 `view`，但不会影响 `snap`。生命游戏的同时更新必须保留独立旧状态，不能把副本换成只读引用。

`for (const string& s : strs)` 同样是不复制、不通过 `s` 修改原字符串；需要排序时另写 `string key = s` 创建副本。

### 指针中的 const

以下为三个独立声明示例，假设 `x` 是普通 `int` 变量：

| 写法 | 能通过指针修改 x | 能改变指针指向 |
|---|---|---|
| `const int* p = &x;` | 否 | 能 |
| `int* const p = &x;` | 能 | 否 |
| `const int* const p = &x;` | 否 | 否 |

指针变量保存地址，可以用 `const` 限制它本身的赋值；引用不能直接照搬这种写法。口诀：**只读参数 const 加引用；单层指针星前管内容，星后管指向。**

应用：[生命游戏（289）](../数组/生命游戏（289）.md)。


## 栈题中的容器选择与字符串处理

### vector 模拟栈与 stack

| 操作 | vector | stack |
|---|---|---|
| 入栈 | `push_back(x)` | `push(x)` |
| 删除栈顶 | `pop_back()` | `pop()` |
| 访问栈顶 | `back()` | `top()` |
| 判空 | `empty()` | `empty()` |
| 从底到顶遍历 | 支持范围 for | 不提供直接遍历接口 |

删除和访问栈顶前要保证非空；pop 不返回被删除的元素，需要先读取再删除。只操作栈顶时 stack 很合适；还需要按入栈顺序遍历时，vector 模拟栈更方便。

应用：[简化路径（71）](../栈/简化路径（71）.md)。

### 按指定分隔符读取

```cpp
stringstream ss(path); // 需要 <sstream>
string part;
while (getline(ss, part, '/')) {
    // part 是读取到的这一段，不包含分隔符 '/'
}
```

与 `ss >> word` 按空白分词不同，getline 在这里按 `/` 分割，开头或连续分隔符可能产生空段，可用 `part.empty()` 判断。分隔符会被消耗；无法继续读取时循环结束。

### 判断单个字符是否为数字：isdigit

正确函数名是 `isdigit`，不是 `isdigig`，声明在 `<cctype>` 中；数字字符返回非零值，否则返回 0。

```cpp
#include <cctype>
bool isDigit = std::isdigit(static_cast<unsigned char>(c)) != 0;
```

对字符串解码题中的英文字母、数字和括号，也可以直接使用 `c >= '0' && c <= '9'`。确认是数字后，通过 `num = num * 10 + (c - '0')` 累积多位数，例如依次读取 `'1'`、`'2'` 得到 12。

应用：[字符串解码（394）](../栈/栈专题（20、155、394）.md)。

### 数字字符串与数字字符不要混淆

```cpp
string token = "-11";
int value = stoi(token); // -11，支持负数和多位数
char digit = '7';
int number = digit - '0'; // 7，仅适用于数字字符
```

string 没有 `isdigit()` 成员函数，不能写 `token.isdigit()`，也不能对 string 写 `token - '0'`。逆波兰题中，比较完整 token 是否为 `+、-、*、/` 即可区分运算符和数字，不要仅根据首字符判断负数。

C++ 整数除法向零截断，例如 `-7 / 3 == -2`。运算符的两个操作数需要保持顺序，栈先弹出的通常是右操作数。

应用：[逆波兰表达式求值（150）](../栈/逆波兰表达式求值（150）.md)。


## 链表节点、指针与基本操作

### 节点定义与创建

链表的每个节点保存一个值和下一节点的地址。头指针 `head` 指向第一个节点，末尾节点的 `next` 为 `nullptr`。

```cpp
struct ListNode {
    int val;
    ListNode* next;
    ListNode(int x) : val(x), next(nullptr) {}
};
```

构造函数把 `val` 初始化为 x，把 `next` 初始化为空。

```cpp
ListNode* a = new ListNode(2);
ListNode* b = new ListNode(4);
ListNode* c = new ListNode(3);
a->next = b;
b->next = c;
ListNode* head = a;
// head → 2 → 4 → 3 → nullptr
```

数组可以按下标 O(1) 访问，节点分散存储的链表需要沿 next 查找；访问第 i 个节点需要 O(i) 时间，不能把 `head[i]` 当作链表下标操作。

### 为什么有时用点，有时用箭头

**对象用 `.`，指针用 `->`；看左边表达式的类型，不看右边成员的类型。**

```cpp
ListNode dummy(0);      // dummy 是节点对象
ListNode* p = &dummy;   // p 是指针，&dummy 取得对象地址

dummy.val = 5;
p->val = 5;            // 访问同一个节点

dummy.next = nullptr;
p->next = nullptr;     // 访问同一个成员
```

`p->next` 等价于 `(*p).next`：先通过 `*p` 取得指向的对象，再访问成员。只有 p 指向有效节点时才能这样访问。

虽然 `dummy.next` 的值是指针，但左边的 dummy 是对象，所以仍用 `.`。`ListNode` 表示节点类型，`ListNode*` 表示节点指针类型。

### 遍历与指针移动

```cpp
ListNode* cur = head;
while (cur != nullptr) {
    // 使用 cur->val
    cur = cur->next;
}
```

`cur = head` 只复制地址，没有复制链表。移动 cur 不改变 head；通过 cur 修改节点则会影响原链表。

```cpp
cur = cur->next;    // 移动指针，链表连接不变
cur->next = other;  // 修改当前节点的连接（要求 cur 非空）
cur->val = 9;       // 修改当前节点的值（要求 cur 非空）
```

遍历 n 个节点：时间 O(n)，额外空间 O(1)。空指针不能访问 val 或 next，指针声明后要初始化。

### 插入与删除

在非空节点 p 后插入新节点，**新节点先接后面，前面再接新节点**：

```cpp
// 原来 p 指向 2，链表为 2 → 4
ListNode* node = new ListNode(3);
node->next = p->next;
p->next = node;
// 结果：2 → 3 → 4
```

删除 p 后的节点，要求 p、p->next 均非空，且被删节点通过 new 创建并由当前代码负责释放：

```cpp
ListNode* target = p->next; // 保存待删除节点
p->next = target->next;    // 绕过它，接上后继
delete target;            // 释放内存，此后不能再访问该节点
```

给定前驱节点后的插入、删除是 O(1)；寻找前驱节点的时间另算。只断开连接不等于释放内存；new 创建的节点在不再需要时应由负责其生命周期的代码释放。

### 虚拟头节点与尾插模板

```cpp
ListNode dummy(0);
ListNode* tail = &dummy;

// 每得到一个需要添加的值 x，执行：
tail->next = new ListNode(x); // 接新节点
tail = tail->next;           // 更新尾指针

// 构建完成后：
ListNode* head = dummy.next;
```

初始 tail 指向 dummy，每次添加后都指向真正的尾节点。第一个节点与后续节点的添加方式一致，不需要单独判断结果链表是否为空。

例如依次添加 7、0、8 后：

```text
dummy → 7 → 0 → 8 → nullptr
                ↑
               tail
```

dummy 不属于答案，真正头节点是 `dummy.next`。dummy 是局部对象，会自动销毁，不需要 delete；返回 `dummy.next` 指向的新建节点是可行的，不能返回局部 dummy 本身的地址。这里的简单节点定义不会在 dummy 销毁时自动释放 next 后面的链表。

口诀：**对象点，指针箭头；移动指针用赋值，修改连接改 next；尾插先连接，再移动。**

应用：[[链表/链表进阶（2、25、138、148、146）#2. 两数相加]]；[[链表/链表基础（160、206、234、141、142、21）#21. 合并两个有序链表]]。


### 末尾节点与空指针

普通无环单链表用 next == nullptr 表示没有后继。这是构建时初始化或主动赋值形成的，不是节点到末尾后自动变空。

```cpp
ListNode* a = new ListNode(2); // 构造函数将 next 初始化为 nullptr
ListNode* b = new ListNode(3);
a->next = b; // a 的 next 改为 b，b 的 next 仍为空
// a → 2 → 3 → nullptr
```

- cur 指向末尾节点：读取 cur->next 合法，结果为 nullptr。
- cur 本身为 nullptr：读取 cur->next 非法，因为没有节点可访问。
- while (cur != nullptr) 保证循环内可以读取 cur->next；移动到 nullptr 后，下一轮退出。
- 局部反转中 end->next = nullptr 是主动设置区间终点；先保存原 end->next，避免丢失后半段。
- 如果尾节点连回前面的节点就形成环，沿 next 遍历不会自然遇到 nullptr。

### 用 delete 释放虚拟头节点

若使用 `ListNode* dummy = new ListNode(0)`，完成全部连接后应先保存结果，再释放 dummy：

```cpp
ListNode* result = dummy->next;
delete dummy;
return result;
```

不能先 delete dummy 再 return dummy->next，后者会访问已释放的节点。对这里仅含 val 和原始指针 next、没有递归析构逻辑的 ListNode，delete dummy 不会自动沿 next 删除整条链表，result 仍指向有效节点。

局部对象 `ListNode dummy(0)` 自动销毁，不要 delete &dummy。删除目标节点时的 delete target 与释放虚拟头节点不同：前者移除题目要求删除的真实节点，后者清理辅助节点。

应用：[[链表/反转链表 II（92）]]；[[链表/删除链表的倒数第 N 个结点（19）]]。


## priority_queue：大顶堆与小顶堆

```cpp
#include <queue>
#include <vector>
#include <functional>
using namespace std;

priority_queue<int> maxHeap;  // 默认大顶堆，top() 是最大值
priority_queue<int, vector<int>, greater<int>> minHeap; // 小顶堆

// 大顶堆操作示例
maxHeap.push(3);
maxHeap.push(1);
maxHeap.push(5);
maxHeap.push(2);

int largest = maxHeap.top(); // 5：先读取
maxHeap.pop();               // 再删除；pop() 不返回值
// 此时 maxHeap.top() == 3

while (!maxHeap.empty()) {
    int value = maxHeap.top(); // 依次得到 3、2、1
    maxHeap.pop();
    // 使用 value
}
```

| 操作 | 含义 | 复杂度 |
|---|---|---|
| `push(x)` | 加入元素 | O(log n) |
| `top()` | 读取堆顶 | O(1) |
| `pop()` | 删除堆顶，不返回值 | O(log n) |
| `size()` | 元素个数 | O(1) |
| `empty()` | 是否为空 | O(1) |

调用 `top()`、`pop()` 前必须保证非空。堆只保证堆顶是最大值或最小值，不保证内部完全有序；不断取出大顶堆堆顶才会得到降序结果。

迁移：保留最大的 k 个数，用小顶堆淘汰最小值；保留最小的 k 个数，用大顶堆淘汰最大值。

应用：[堆专题（215、347、295）](../堆/堆专题（215、347、295）.md)。
