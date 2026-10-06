# 208. 实现 Trie（前缀树）

> 整理自源笔记《力扣刷题笔记-回溯等.md》；已排除目标库中已有的同题旧稿。

## 208. 实现 Trie（前缀树）

### 简短题意

实现 Trie（前缀树），支持 `insert(word)` 插入单词、`search(word)` 判断完整单词是否存在、`startsWith(prefix)` 判断是否存在以该前缀开头的单词。单词和前缀只包含小写英文字母；仅有前缀存在不代表完整单词存在。

### 题型
- 字符串数据结构设计
- Trie / 前缀树

### 核心思路
Trie 本质是：
> 把字符串按字符路径存进树里

公共前缀共用同一段路径，所以特别适合做：
- 单词查找
- 前缀查找
- 自动补全

### 节点要存什么
1. `children[26]`
   - 表示 26 个小写字母对应的孩子节点
   - `children[0]` 对应 `'a'`，`children[25]` 对应 `'z'`
2. `isEnd`
   - 标记当前节点是不是某个完整单词的结尾

### 三个操作
#### 1）insert(word)
逐字符往下走：
- 没路就新建
- 有路就继续走
- 最后把结尾节点标记为 `isEnd = true`

#### 2）search(word)
逐字符往下走：
- 只要某一步没路，返回 `false`
- 路走完后，还要看当前节点 `isEnd` 是否为 `true`

#### 3）startsWith(prefix)
逐字符往下走：
- 只要路径存在，就返回 `true`
- 不需要检查 `isEnd`

### 关键区别
- `search(word)`：查完整单词，**要看 `isEnd`**
- `startsWith(prefix)`：查前缀，**不用看 `isEnd`**

### 记忆口诀
- Trie = 把字符串存成路径
- 公共前缀共用节点
- `search` 看 `isEnd`，`startsWith` 不看 `isEnd`

### C++
```cpp
class Trie {
private:
    Trie* children[26]; // 26 个孩子，对应 a~z
    bool isEnd;         // 当前节点是否是单词结尾

public:
    Trie() {
        // 初始化孩子节点为空
        for (int i = 0; i < 26; i++) {
            children[i] = nullptr;
        }
        isEnd = false;
    }
    
    void insert(string word) {
        Trie* node = this; // 从根节点开始
        
        for (char c : word) {
            int idx = c - 'a'; // 字符映射到 0~25
            
            // 路不存在就新建
            if (node->children[idx] == nullptr) {
                node->children[idx] = new Trie();
            }
            
            node = node->children[idx]; // 走到下一层
        }
        
        node->isEnd = true; // 标记单词结束
    }
    
    bool search(string word) {
        Trie* node = this; // 从根节点开始
        
        for (char c : word) {
            int idx = c - 'a';
            
            if (node->children[idx] == nullptr) {
                return false; // 路径不存在
            }
            
            node = node->children[idx];
        }
        
        return node->isEnd; // 必须是完整单词结尾
    }
    
    bool startsWith(string prefix) {
        Trie* node = this; // 从根节点开始
        
        for (char c : prefix) {
            int idx = c - 'a';
            
            if (node->children[idx] == nullptr) {
                return false; // 前缀路径不存在
            }
            
            node = node->children[idx];
        }
        
        return true; // 只要前缀路径存在即可
    }
};
```

### 复杂度
- `insert`：`O(L)`
- `search`：`O(L)`
- `startsWith`：`O(L)`

其中 `L` 是字符串长度。

### 一类题总结
看到这些关键词优先想 Trie：
- 前缀匹配
- 自动补全
- 字符串检索
- 字典树

通用模型：
> 字符逐层建树，路径表示前缀，节点标记是否为完整单词结尾
