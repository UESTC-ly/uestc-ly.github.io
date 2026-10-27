# React与组件状态

<a id="k24bf7910ce21"></a>

## Is it mandatory to define constructor for React component?

    No, it is not mandatory. i.e, If you don’t initialize state and you don’t bind methods, you don’t need to implement a constructor for your React component.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12090)，来源许可：MIT。

<a id="k45cf921bb5ec"></a>

## Is it possible to use async/await in plain React?

    Yes, you can use `async/await` in plain React, as long as your JavaScript environment supports ES2017+. Nowadays most modern browsers and build tools support ES2017+ version. If you're using **Create React App**, **Next.js**, **Remix**, or any modern React setup, `async/await` is supported out of the box through **Babel**.

    ### Example Usage

```jsx
    import { useEffect, useState } from 'react';

    function UserProfile() {
      const [user, setUser] = useState(null);

      useEffect(() => {
        const fetchUser = async () => {
          const response = await fetch('/api/user');
          const data = await response.json();
          setUser(data);
        };

        fetchUser();
      }, []);

      return user ? <div>Hello, {user.name}</div> : <div>Loading...</div>;
    }
```
    But If you're not using a bundler like **Webpack or Babel**, you will need _Babel_ and [transform-async-to-generator](https://babeljs.io/docs/en/babel-plugin-transform-async-to-generator) plugin. However, React Native ships with Babel and a set of transforms.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2629)，来源许可：MIT。

<a id="k92c93ed0505d"></a>

## Is it possible to use react without JSX?

    Yes, JSX is not mandatory for using React. Actually it is convenient when you don’t want to set up compilation in your build environment. Each JSX element is just syntactic sugar for calling `React.createElement(component, props, ...children)`.

    For example, let us take a greeting example with JSX,

```javascript
    class Greeting extends React.Component {
      render() {
        return <div>Hello {this.props.message}</div>;
      }
    }

    ReactDOM.render(
      <Greeting message="World" />,
      document.getElementById("root")
    );
```

    You can write the same code without JSX as below,

```javascript
    class Greeting extends React.Component {
      render() {
        return React.createElement("div", null, `Hello ${this.props.message}`);
      }
    }

    ReactDOM.render(
      React.createElement(Greeting, { message: "World" }, null),
      document.getElementById("root")
    );
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12602)，来源许可：MIT。

<a id="kd16529ee966e"></a>

## Is it possible to use React without rendering HTML?

    It is possible. Below are the possible options:

```jsx harmony
    render() {
      return false
    }
```

```jsx harmony
    render() {
      return true
    }
```

```jsx harmony
    render() {
      return null
    }
```

    React version >=16.0.0:

```jsx harmony
    render() {
      return []
    }
```

```jsx harmony
    render() {
      return ""
    }
```

    React version >=16.2.0:

```jsx harmony
    render() {
      return <React.Fragment></React.Fragment>
    }
```

```jsx harmony
    render() {
      return <></>
    }
```

    React version >=18.0.0:

```jsx harmony
    render() {
      return undefined
    }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11374)，来源许可：MIT。

<a id="k619697d1849a"></a>

## Is it recommended to use CSS In JS technique in React?

     React does not have any opinion about how styles are defined but if you are a beginner then good starting point is to define your styles in a separate \*.css file as usual and refer to them using className. This functionality is not part of React but came from third-party libraries. But If you want to try a different approach(CSS-In-JS) then styled-components library is a good option.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5415)，来源许可：MIT。

<a id="keb3659caf136"></a>

## Is ref argument available for all functions or class components?

    Regular function or class components don’t receive the ref argument, and ref is not available in props either. The second ref argument only exists when you define a component with React.forwardRef call.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12565)，来源许可：MIT。

<a id="k22724ebe5ae0"></a>

## Is useState Synchronous or Asynchronous?

     The `useState` hook is synchronous, but state updates are asynchronous. When you call `useState()`, it runs synchronously and returns the state variable and setter function as tuple.
```js
     const [count, setCount] = useState(0);
```
     This happens immediately during rendering.
     However, the state update function (**setState**) is asynchronous in the sense that it doesn't update the state immediately.
     React **batches** updates and applies them before the next render. You won’t see the updated value immediately after calling `setState`.

     **Example:**
```js
     const [count, setCount] = useState(0);

     function handleClick() {
       setCount(count + 1);
       console.log(count); // ❗️Still logs the old value
     }
```
     The > `console.log(count)` prints the **old value**, because the update hasn’t happened yet.

     To see the updated state value, you can use `useEffect()` hook. It runs **after the component has re-rendered.**  By the time `useEffect` runs:

        *   The component has been updated.
        *   The **state contains the new value**.

```js
        import React, { useState, useEffect } from 'react';

        function Counter() {
        const [count, setCount] = useState(0);

        const handleClick = () => {
        setCount(count + 1);
        console.log('Clicked count (old):', count); // Old value
        };

        useEffect(() => {
        console.log('Updated count:', count); // New value
        }, [count]); // Only runs when `count` changes

        return <button onClick={handleClick}>Count: {count}</button>;
        }
```
**[⬆ Back to Top](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#table-of-contents)**

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6939)，来源许可：MIT。

<a id="k41a5e976dafb"></a>

## Must prop be named as render for render props?

     Even though the pattern named render props, you don’t have to use a prop named render to use this pattern. i.e, Any prop that is a function that a component uses to know what to render is technically a “render prop”. Lets take an example with the children prop for render props,

```javascript
     <Mouse
       children={(mouse) => (
         <p>
           The mouse position is {mouse.x}, {mouse.y}
         </p>
       )}
     />
```

     Actually children prop doesn’t need to be named in the list of “attributes” in JSX element. Instead, you can keep it directly inside element,

```javascript
     <Mouse>
       {(mouse) => (
         <p>
           The mouse position is {mouse.x}, {mouse.y}
         </p>
       )}
     </Mouse>
```

     While using this above technique(without any name), explicitly state that children should be a function in your propTypes.

```javascript
     Mouse.propTypes = {
       children: PropTypes.func.isRequired,
     };
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5247)，来源许可：MIT。

<a id="kc6d052b2235c"></a>

## React setState 的时机？

使用 setState 时不会直接更新数据，而是会直接将其挂到更新队列中�?
更新的时机是：当前宏任务结束后，微任务开始前�?

```javascript
this.state = {
  a: 1,
}

// 这种情况只会+1，因为它相当于Object.assign(oldState, {count: XXX}, {count: XXX})
this.setState({ count: this.state.count + 1 })
this.setState({ count: this.state.count + 1 })

console.log(this.state.count) // 这时候会取到原来的state，也就是1

// 进行改造，这样就一定会+2�?
this.setState((state, props) => {
  return { count: state.count + 1 }
})
this.setState((state, props) => {
  return { count: state.count + 1 }
})
```

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/06-development-tech/frontend/frontend-frameworks.md#L31)，来源许可：GPL-3.0。

<a id="k1997a6f3c211"></a>

## ReAct 与 CoT-SC 混合策略为什么有效？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

CoT-SC 指 Chain-of-Thought Self-Consistency，即让模型生成多个推理路径，再通过投票或一致性选择答案。它利用模型内部知识，适合低工具成本的推理任务。

ReAct 与 CoT-SC 可以互补：

1. **ReAct 失败后回退 CoT-SC**

   当搜索失败、工具不可用或环境噪声大时，可以让模型基于内部知识生成多个候选推理，再选择最一致的答案。

2. **CoT-SC 置信度低时切换 ReAct**

   当多个候选答案分歧很大，说明内部知识不稳定，应主动调用外部工具验证。

3. **先 ReAct 收集事实，再 CoT-SC 推理**

   对需要事实依据又需要复杂推理的问题，可以先用工具拿证据，再对证据进行多路径推理。

4. **先 CoT 拆解问题，再 ReAct 查关键缺口**

   对复杂研究任务，可以先拆成子问题，只对缺失信息调用工具。

面试中可以总结：ReAct 提供外部 grounding，CoT-SC 提供内部多样性和一致性，两者组合能在事实性、效率和鲁棒性之间做动态平衡。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L215)，来源许可：GPL-3.0。

<a id="k2fd52f2e988e"></a>

## ReAct 提示通常包含哪些元素？

一个 ReAct 风格提示通常包含：

- 当前任务和可用工具说明；
- 每个工具的输入参数、输出含义和调用限制；
- 决策规则：什么时候调用工具，什么时候直接回答；
- 工具结果如何进入下一步推理；
- 失败处理策略：工具报错、无结果、结果冲突时怎么办；
- 最终答案格式。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/05_%E6%8F%90%E7%A4%BA%E5%B7%A5%E7%A8%8B%EF%BC%9A%E5%BA%94%E7%94%A8%E5%A4%A7%E6%A8%A1%E5%9E%8B%E7%9A%84%E9%AB%98%E7%BA%A7%E6%96%B9%E6%B3%95.md#L359)，来源许可：GPL-3.0。

<a id="k8f4e9c2baa58"></a>

## ReAct 相比 CoT 的优势和局限是什么？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

| 维度 | CoT | ReAct |
| --- | --- | --- |
| 信息来源 | 模型内部知识 | 内部推理 + 外部工具观察 |
| 事实性 | 容易受训练数据影响 | 可通过检索和工具降低幻觉 |
| 成本 | 低 | 工具调用和多轮交互成本更高 |
| 可解释性 | 有推理链但可能不接地 | 能看到行动和观察轨迹 |
| 稳定性 | 对简单推理稳定 | 可能陷入工具循环 |
| 适用任务 | 数学、逻辑、常识推理 | 检索、交互、排障、动态任务 |

ReAct 的局限：

- 工具结果质量会强烈影响最终答案。
- 搜索关键词错误会导致偏航。
- 贪心决策可能反复调用无效工具。
- 每轮工具调用都增加延迟和成本。
- 工具返回内容可能带有 prompt injection。
- 长任务中 observation 太多会挤爆上下文。

所以 ReAct 不是万能模式。对于步骤明确、无需外部信息的问题，CoT 或 Plan-and-Solve 可能更便宜、更稳定。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L187)，来源许可：GPL-3.0。

<a id="k39d0e13d98c7"></a>

## ReAct、Plan-and-Execute、Reflection、Tree-of-Thought 如何对比？

**难度评分：⭐⭐⭐ (3/5)  |  考察频率：⭐⭐⭐⭐ (4/5)**

本节只做面试总览，帮助快速识别不同模式的适用边界；ReAct、Plan-and-Solve、ReWOO、Reflection、ToT、GoT、LATS 和多 Agent 编排的完整推导，见 [03_Agent设计模式与工作流编排高频考点.md](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent设计模式与工作流编排高频考点.md)。

| 模式 | 核心思想 | 优点 | 局限 |
| --- | --- | --- | --- |
| ReAct | Reasoning 和 Acting 交替 | 简单、适合工具使用 | 容易局部贪心 |
| Plan-and-Execute | 先制定计划，再分步执行 | 结构清晰，适合长任务 | 初始计划可能过时 |
| Reflection | 执行后自评和修正 | 能从错误中恢复 | 增加成本和延迟 |
| Tree-of-Thought | 多路径搜索和比较 | 适合复杂推理 | 成本高，工程复杂 |
| Multi-Agent | 多角色协作 | 适合专业分工 | 协调成本和一致性问题 |

实际系统常常混合使用：

- 简单任务：ReAct。
- 长任务：Plan-and-Execute + 动态重规划。
- 高风险任务：Reflection + 人类确认。
- 复杂研究或编码：主 Agent + 子 Agent + 工具执行。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/01_AIGC%E6%97%B6%E4%BB%A3AI%20Agent%E5%9F%BA%E7%A1%80%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L176)，来源许可：GPL-3.0。

<a id="kea5566324eb7"></a>

## ReAct模式和Plan模式有什么区别？

**面试官：** ReAct模式和Plan模式有什么区别？分别适合什么场景？

**回答：**

ReAct 与 Plan 模式的本质区别，是“决策与执行交错进行”还是“先形成显式计划，再由执行器推进”。二者不是互斥框架，也不能简单等同于“ReAct 灵活但慢、Plan 一定高效”。

**ReAct** 通常按 Observation -> Reason/Decision -> Action -> New Observation 循环。每一步都根据最新环境反馈决定下一步，适合信息不完整、需要搜索、工具结果不确定或错误恢复频繁的任务。优势是反馈闭环短；缺点是模型可能局部贪心、重复调用、路径漂移，而且每一步都要重新推理，成本和延迟较高。

**Plan-and-Execute** 先把目标拆成子任务、依赖和验收条件，再由执行器逐步完成。计划可以是线性列表，也可以是 DAG，但“Plan 模式必然一次性生成完整 DAG”并不准确。优势是全局目标更清晰、任务可并行、便于预算和审计；缺点是环境变化后原计划会过时，错误计划如果不允许重规划，执行越认真可能偏得越远。

场景上可以这样选择：

- 开放式检索、故障排查、网页操作、代码探索：更适合 ReAct，因为下一步依赖刚获得的观察。
- 固定审批流、批处理、可预测的数据流水线：更适合显式 Plan 或 Workflow。
- 长周期复杂任务：通常采用分层混合模式，Planner 生成里程碑和依赖，每个子任务内部使用 ReAct，遇到关键假设失效时触发 Replan。

工程实现中，计划不应只是一段自然语言。至少要有 `step_id`、依赖、输入、工具权限、预算、完成条件和状态；执行器则要维护最大步数、重试策略、幂等键、Checkpoint 和取消信号。每一步完成后由确定性 Verifier 或环境状态判断是否达标，不能只让同一个模型口头宣布成功。

一个成熟系统还要支持“不要用 Agent”的判断。如果流程稳定、风险高且规则明确，状态机或工作流引擎通常比自主 ReAct 更可靠。**ReAct 解决动态探索，Plan 解决全局分解，生产系统真正重要的是反馈、验证和重规划，而不是给循环贴哪一个模式标签。**

<a id="alibaba-cloud-agent-algo-20260901-q7"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1394)，来源许可：GPL-3.0。

<a id="k971558de80d2"></a>

## Should I learn ES6 before learning ReactJS?

     No, you don’t have to learn es2015/es6 to learn react. But you may find many resources or React ecosystem uses ES6 extensively. Let's see some of the frequently used ES6 features,

     1. **Destructuring:** To get props and use them in a component

```javascript
        // in es 5
        var someData = this.props.someData;
        var dispatch = this.props.dispatch;

        // in es6
        const { someData, dispatch } = this.props;
```

     2. **Spread operator:** Helps in passing props down into a component

```javascript
        // in es 5
        <SomeComponent someData={this.props.someData} dispatch={this.props.dispatch} />

        // in es6
        <SomeComponent {...this.props} />
```

     3. **Arrow functions:** Makes compact syntax
```javascript
        // es 5
        var users = usersList.map(function (user) {
          return <li>{user.name}</li>;
        });
        // es 6
        const users = usersList.map((user) => <li>{user.name}</li>);
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5579)，来源许可：MIT。

<a id="k5253e1b014ed"></a>

## vue中reactive和ref的区别

**回答：**

`reactive` 接受对象并返回响应式代理，适合对象内部的字段变更；`ref` 返回带 value 属性的容器，可保存原始值或对象，适合整体替换。常规 ref 保存对象时也会做深层响应式转换，`shallowRef` 则保留较浅的跟踪语义。

`const state=reactive({count:0})` 后修改 `state.count` 会触发跟踪它的依赖；`const {count}=state` 得到的是当时的数字值，失去关联，需要 `toRef/toRefs`。ref 通过 `count.value++` 修改，在合适的模板上下文中自动解包，但数组和原生集合内的 ref 不应假定都会自动解包。

reactive 代理被新的普通对象替换时，原先依赖关系不会自动迁移。要经常整体替换数据可以用 ref，并清楚区分代理对象身份和原对象身份。

<a id="jd-damodel-20251211-20260205-p5-q13"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E4%BA%AC%E4%B8%9C%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L740)，来源许可：GPL-3.0。

<a id="k3917077651d6"></a>

## What are Custom React Hooks, and How Can You Develop One?

      **Custom Hooks** in React are JavaScript functions that allow you to **extract and reuse component logic** using React’s built-in Hooks like `useState`, `useEffect`, etc.

      They start with the word **"use"** and let you encapsulate logic that multiple components might share—such as fetching data, handling forms, or managing timers—without repeating code.

      Let's explain the custom hook usage with `useFetchData` example. The `useFetchData` custom Hook is a reusable function in React that simplifies the process of fetching data from an API. It encapsulates common logic such as initiating the fetch request, managing loading and error states, and storing the fetched data. By using built-in Hooks like `useState` and `useEffect`, `useFetchData` provides a clean interface that returns the `data`, `loading`, and `error` values, which can be directly used in components.

```jsx
      import { useState, useEffect } from 'react';

      function useFetchData(url) {
        const [data, setData] = useState(null);     // Holds the response
        const [loading, setLoading] = useState(true); // Loading state
        const [error, setError] = useState(null);     // Error state

        useEffect(() => {
          let isMounted = true; // Prevent setting state on unmounted component
          setLoading(true);

          fetch(url)
            .then((response) => {
              if (!response.ok) throw new Error('Network response was not ok');
              return response.json();
            })
            .then((json) => {
              if (isMounted) {
                setData(json);
                setLoading(false);
              }
            })
            .catch((err) => {
              if (isMounted) {
                setError(err.message);
                setLoading(false);
              }
            });

          return () => {
            isMounted = false; // Clean-up function to avoid memory leaks
          };
        }, [url]);

        return { data, loading, error };
      }
```

      The above custom hook can be used to retrieve users data for `AuthorList`, `ReviewerList` components.

      **Example: AuthorList component**
```jsx
      function AuthorList() {
        const { data, loading, error } = useFetchData('https://api.example.com/authors');

        if (loading) return <p>Loading authors...</p>;
        if (error) return <p>Error: {error}</p>;

        return (
          <ul>
            {data.map((author) => (
              <li key={author.id}>{author.name}</li>
            ))}
          </ul>
        );
      }
```

      Some of the benefits of custom hooks are:
       *   Promotes **code reuse**
       *   Keeps components **clean and focused**
       *   Makes complex logic **easier to test and maintain**

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7908)，来源许可：MIT。

<a id="kc9c14b44d427"></a>

## What are default props?

     The _defaultProps_ can be defined as a property on the component to set the default values for the props. These default props are used when props not supplied(i.e., undefined props), but not for `null` or `0` as props. That means, If you provide null value then it remains null value. It's the same behavior with 0 as well.

     For example, let us create color default prop for the button component,

```javascript
     function MyButton {
       // ...
     }

     MyButton.defaultProps = {
       color: "red",
     };
```

     If `props.color` is not provided then it will set the default value to 'red'. i.e, Whenever you try to access the color prop it uses the default value

```javascript
     function MyButton() {
       return <MyButton />; // props.color will contain red value
     }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4642)，来源许可：MIT。

<a id="k6458494f0b10"></a>

## What are error boundaries in React v16?

**Note:** Error boundaries were introduced in React 16 and remain valid in current React versions (18/19).

_Error boundaries_ are components that catch JavaScript errors anywhere in their child component tree, log those errors, and display a fallback UI instead of the component tree that crashed.

A class component becomes an error boundary if it defines these lifecycle methods:
- `static getDerivedStateFromError(error)` - for rendering fallback UI
- `componentDidCatch(error, info)` - for logging error information

```jsx harmony
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    // Log error to an error reporting service
    console.error('Error caught by boundary:', error, info);
    logErrorToMyService(error, info);
  }

  render() {
    if (this.state.hasError) {
      // Render custom fallback UI
      return <h1>Something went wrong.</h1>;
    }
    return this.props.children;
  }
}
```

Usage:

```jsx harmony
<ErrorBoundary>
  <MyWidget />
</ErrorBoundary>
```

**Note:** Error boundaries currently only work with class components. There is no hook equivalent yet, though `use()` hook in React 19 provides some error handling capabilities.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10823)，来源许可：MIT。

<a id="kd6baef2c6238"></a>

## What are Higher-Order Components?

A _higher-order component_ (_HOC_) is a function that takes a component and returns a new enhanced component with additional props, behavior, or data. It’s a design pattern based on React’s compositional nature, allowing you to reuse logic across multiple components without modifying their internals.

We consider HOCs **pure components** because they don’t mutate or copy behavior from the original component—they simply **wrap it**, enhance it, and pass through the necessary props. The wrapped component remains decoupled and reusable.

```javascript
const EnhancedComponent = higherOrderComponent(WrappedComponent);
```
Let's take an example of a `withAuth` higher-order component (HOC) in React. This HOC will check if a user is authenticated and either render the wrapped component if authenticated or redirect (or show a message) if not.

**withAuth HOC Example:**
```jsx
import React from 'react';
import { Navigate } from 'react-router-dom'; // For redirection (assuming React Router v6)

const isAuthenticated = () => {
  // e.g., check for a valid token in localStorage or context
  return !!localStorage.getItem('authToken');
};

function withAuth(WrappedComponent) {
  return function AuthenticatedComponent(props) {
    if (!isAuthenticated()) {
      // User is NOT authenticated, redirect to login page
      return <Navigate to="/login" replace />;
    }

    // User is authenticated, render the wrapped component
    return <WrappedComponent {...props} />;
  };
}

export default withAuth;
```
**Usage**
```jsx
import React from 'react';
import withAuth from './withAuth';

function Dashboard() {
  return <h1>Welcome to the Dashboard!</h1>;
}

// Wrap Dashboard with withAuth HOC
export default withAuth(Dashboard);
```

HOC can be used for many use cases:

1. Code reuse, logic and bootstrap abstraction (e.g., fetching data, permissions, theming).
2. Render hijacking (e.g., conditional rendering or layout changes).
3. State abstraction and manipulation(e.g., handling form logic).
4. Props manipulation(e.g., injecting additional props or filtering them).

Some of the real-world examples of HOCs in react eco-system:
1. connect() from react-redux
2. withRouter() from React Router v5
3. withTranslation() from react-i18next
4. withApollo() from Apollo client
5. withFormik from Formik library
6. withTheme from styled components

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1387)，来源许可：MIT。

<a id="k62947f667c07"></a>

## What are hooks?

     Hooks is a special JavaScript function that allows you use state and other React features without writing a class. This pattern has been introduced as a new feature in React 16.8 and helped to isolate the stateful logic from the components.

     Let's see an example of useState hook:

```jsx
     import { useState } from "react";

     function Example() {
       // Declare a new state variable, which we'll call "count"
       const [count, setCount] = useState(0);

       return (
         <>
           <p>You clicked {count} times</p>
           <button onClick={() => setCount(count + 1)}>Click me</button>
         </>
       );
     }
```

     **Note:** Hooks can be used inside an existing function component without rewriting the component.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4353)，来源许可：MIT。

<a id="kde287a63a465"></a>

## What are loadable components?

     With the release of React 18, React.lazy and Suspense are now available for server-side rendering. However, prior to React 18, it was recommended to use Loadable Components for code-splitting in a server-side rendered app because React.lazy and Suspense were not available for server-side rendering. Loadable Components lets you render a dynamic import as a regular component. For example, you can use Loadable Components to load the OtherComponent in a separate bundle like this:

```javascript
     import loadable from "@loadable/component";

     const OtherComponent = loadable(() => import("./OtherComponent"));

     function MyComponent() {
       return (
         <div>
           <OtherComponent />
         </div>
       );
     }
```

     Now OtherComponent will be loaded in a separated bundle
     Loadable Components provides additional benefits beyond just code-splitting, such as automatic code reloading, error handling, and preloading. By using Loadable Components, you can ensure that your application loads quickly and efficiently, providing a better user experience for your users.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5037)，来源许可：MIT。

<a id="k7b1200ff3c05"></a>

## What are loaders, actions, and data APIs in modern React Router?

     Starting with React Router v6.4, the library ships **data APIs** (`createBrowserRouter`, `loader`, `action`, `useLoaderData`, `useActionData`, `useFetcher`) that move data fetching and mutations out of components and into the route definitions themselves — conceptually similar to Next.js server components/actions, but framework-agnostic.

     - **Loader**: a function attached to a route that fetches the data that route needs *before* (or in parallel with) rendering, eliminating loading-state waterfalls ("render-then-fetch").
     - **Action**: a function attached to a route that handles data **mutations** (form submissions — create/update/delete), typically triggered via `<Form>` or `useFetcher()`.
     - **`useLoaderData()` / `useActionData()`**: hooks that read the data returned by the matching route's `loader`/`action` inside the rendered component.

```jsx
     import { createBrowserRouter, RouterProvider, useLoaderData, Form, redirect } from "react-router-dom";

     // Loader: runs before the route renders, its return value is available via useLoaderData()
     async function userLoader({ params }) {
       const res = await fetch(`/api/users/${params.userId}`);
       if (!res.ok) throw new Response("Not Found", { status: 404 });
       return res.json();
     }

     // Action: runs when a <Form> on this route is submitted
     async function updateUserAction({ request, params }) {
       const formData = await request.formData();
       await fetch(`/api/users/${params.userId}`, { method: "PUT", body: formData });
       return redirect(`/users/${params.userId}`); // navigate after a successful mutation
     }

     function UserProfile() {
       const user = useLoaderData(); // already-fetched data, no useEffect needed
       return (
         <Form method="put">
           <input name="name" defaultValue={user.name} />
           <button type="submit">Save</button>
         </Form>
       );
     }

     const router = createBrowserRouter([
       {
         path: "/users/:userId",
         element: <UserProfile />,
         loader: userLoader,
         action: updateUserAction,
         errorElement: <ErrorPage />,
       },
     ]);

     function App() {
       return <RouterProvider router={router} />;
     }
```

     Key points:

     - Loaders run **before** the route component renders, so data is ready immediately — no `useEffect` + `isLoading` flicker for the initial fetch.
     - Errors thrown inside a `loader`/`action` (including thrown `Response`s for status codes) are caught by the nearest route's `errorElement`, unifying error handling for fetch failures and render errors.
     - `useFetcher()` lets you call loaders/actions **without** navigating (e.g., optimistic "like" buttons, inline edits in a list).
     - This pattern requires the data-router setup (`createBrowserRouter` + `<RouterProvider>`) instead of the plain `<BrowserRouter>`/`<Routes>` components — it's opt-in, existing `<Routes>`-based apps keep working unchanged.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10285)，来源许可：MIT。

<a id="k6c7bc15110db"></a>

## What are portals in React?

A Portal is a React feature that enables rendering children into a DOM node that exists outside the parent component's DOM hierarchy, while still preserving the React component hierarchy. Portals help avoid CSS stacking issues—for example, elements with position: fixed may not behave as expected inside a parent with transform. Portals solve this by rendering content (like modals or tooltips) outside such constrained DOM contexts.

```javascript
ReactDOM.createPortal(child, container);
```
*   `child`: Any valid React node (e.g., JSX, string, fragment).
*   `container`: A real DOM node (e.g., `document.getElementById('modal-root')`).

Even though the content renders elsewhere in the DOM, it still behaves like a normal child in React. It has access to context, state, and event handling.

**Example:- Modal:**
```jsx
function Modal({ children }) {
  return ReactDOM.createPortal(
    <div className="modal">{children}</div>,
    document.body)
  );
}
```
The above code will render the modal content into the body element in the HTML, not inside the component's usual location.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1671)，来源许可：MIT。

<a id="k88568f08f7bd"></a>

## What are props in React?

    _Props_ are inputs to components. They are single values or objects containing a set of values that are passed to components on creation similar to HTML-tag attributes. Here, the data is passed down from a parent component to a child component.

    The primary purpose of props in React is to provide following component functionality:

    1. Pass custom data to your component.
    2. Trigger state changes.
    3. Use via `this.props.reactProp` inside component's `render()` method.

    For example, let us create an element with `reactProp` property:

```jsx harmony
    <Element reactProp={"1"} />
```

    This `reactProp` (or whatever you came up with) attribute name then becomes a property attached to React's native props object which originally already exists on all components created using React library.

```jsx harmony
    props.reactProp;
```

    For example, the usage of props in function component looks like below:

```jsx
    import React from "react";
    import ReactDOM from "react-dom";

    const ChildComponent = (props) => {
      return (
        <div>
          <p>{props.name}</p>
          <p>{props.age}</p>
          <p>{props.gender}</p>
        </div>
      );
    };

    const ParentComponent = () => {
      return (
        <div>
          <ChildComponent name="John" age="30" gender="male" />
          <ChildComponent name="Mary" age="25" geneder="female" />
        </div>
      );
    };
```

The properties from props object can be accessed directly using destructing feature from ES6 (ECMAScript 2015). It is also possible to fallback to default value when the prop value is not specified. The above child component can be simplified like below.

```jsx harmony
const ChildComponent = ({ name, age, gender = "male" }) => {
  return (
    <div>
      <p>{name}</p>
      <p>{age}</p>
      <p>{gender}</p>
    </div>
  );
};
```

**Note:** The default value won't be used if you pass `null` or `0` value. i.e, default value is only used if the prop value is missed or `undefined` value has been passed.

  See Class
     The Props accessed in Class Based Component as below

```jsx
import React from "react";
import ReactDOM from "react-dom";

class ChildComponent extends React.Component {
  render() {
    return (
      <div>
        <p>{this.props.name}</p>
        <p>{this.props.age}</p>
        <p>{this.props.gender}</p>
      </div>
    );
  }
}

class ParentComponent extends React.Component {
  render() {
    return (
      <div>
        <ChildComponent name="John" age="30" gender="male" />
        <ChildComponent name="Mary" age="25" gender="female" />
      </div>
    );
  }
}
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L898)，来源许可：MIT。

<a id="ka13cced32e6e"></a>

## What are React Mixins?

**⚠️ DEPRECATED:** Mixins are considered legacy and should not be used in modern React applications.

_Mixins_ were a way to share common functionality between components using `React.createClass()`. However, they caused several problems:
- Implicit dependencies
- Name clashes
- Snowballing complexity

One of the most commonly used mixins was `PureRenderMixin`:

```javascript
const PureRenderMixin = require("react-addons-pure-render-mixin");

const Button = React.createClass({
  mixins: [PureRenderMixin],
  // ...
});
```

**Modern Alternatives:**
- **React.memo()** for functional components (replaces PureRenderMixin)
- **Custom Hooks** for sharing stateful logic
- **Higher-Order Components (HOCs)** for cross-cutting concerns
- **Render Props** pattern

```javascript
// Modern equivalent using React.memo
const Button = React.memo(({ onClick, label }) => (
  <button onClick={onClick}>{label}</button>
));
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12731)，来源许可：MIT。

<a id="k7e8c78a0bbe6"></a>

## What are React Server components?

     React Server Component is a way to write React component that gets rendered in the server-side with the purpose of improving React app performance. These components allow us to load components from the backend.

     **Note:** React Server Components is still under development and not recommended for production yet.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5855)，来源许可：MIT。

<a id="k2aebdac9d1b6"></a>

## What are Redux selectors and why use them?

     _Selectors_ are functions that take Redux state as an argument and return some data to pass to the component.

     For example, to get user details from the state:

```javascript
     const getUserData = (state) => state.user.data;
```

     These selectors have two main benefits,

     1. The selector can compute derived data, allowing Redux to store the minimal possible state
     2. The selector is not recomputed unless one of its arguments changes

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3750)，来源许可：MIT。

<a id="k872f036ca691"></a>

## What are Redux serializable values?

     Redux (and Redux Toolkit's default middleware) expects **state and actions to contain only plain, serializable data**: strings, numbers, booleans, `null`, plain objects, and arrays. Values like class instances, `Promise`s, functions, `Map`/`Set`, `Symbol`, or DOM elements are **not serializable** and shouldn't be put in the store or dispatched inside an action.

```javascript
     // BAD: Date and a function are not serializable
     dispatch({
       type: "user/loaded",
       payload: { createdAt: new Date(), onDone: () => {} },
     });

     // GOOD: store a serializable representation instead
     dispatch({
       type: "user/loaded",
       payload: { createdAt: new Date().toISOString() },
     });
```

     This matters because:

     - **Redux DevTools** rely on serializing actions/state for time-travel debugging and persisting/replaying action logs.
     - **`redux-persist`** needs to serialize state to `localStorage`/`AsyncStorage`.
     - Non-serializable values can hide subtle bugs (e.g., mutable class instances bypassing Redux's change-detection).

     Redux Toolkit's `configureStore` includes a `serializableCheck` middleware (dev-only) that warns in the console whenever a non-serializable value is dispatched or stored.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L9870)，来源许可：MIT。

<a id="k7922015a9373"></a>

## What are render props?

    **Render Props** is a technique for sharing code/logic between components using a prop whose value is a function that returns a React element. Instead of duplicating stateful logic in every component that needs it, a "provider" component encapsulates the logic and delegates *what to render* to its caller via this function prop.

```jsx harmony
    <DataProvider render={(data) => <h1>{`Hello ${data.target}`}</h1>} />
```

    #### Full example

```jsx harmony
    class DataProvider extends React.Component {
      state = { target: "World" };

      render() {
        // Instead of hardcoding what to render, delegate it via the render prop
        return this.props.render(this.state);
      }
    }

    function App() {
      return (
        <DataProvider render={(data) => <h1>{`Hello ${data.target}`}</h1>} />
      );
    }
```

    Here, `DataProvider` owns the state, but has no opinion on markup — any consumer can reuse the same logic while rendering completely different UI.

    #### Why use render props?

    1.  **Cross-cutting logic reuse:** Encapsulates logic (data fetching, subscriptions, mouse/scroll tracking, form state, etc.) once and reuses it across many components without inheritance.
    2.  **Explicit data flow:** Unlike HOCs, which implicitly inject props, render props make it obvious exactly what data is being passed to the render function since it's right there as an argument.
    3.  **No naming collisions:** HOCs composed together can silently clash on injected prop names; with render props, you control the destructuring/naming at the call site.
    4.  **Flexible children API:** The render function doesn't need to be named `render` — the `children` prop can also be used as a function (see [Must a prop be named "render" for render props?](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#is-it-prop-must-be-named-as-render-for-render-props)).

    #### Common use cases

    - Tracking mouse position / window size and sharing it with multiple components.
    - Toggling UI state (modals, accordions, dropdowns) — see [How do you create HOC using render props?](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#how-do-you-create-hoc-using-render-props).
    - Fetching remote data and letting the consumer decide how to render loading/success/error states.
    - Libraries such as React Router (`<Route render={...} />`) and Downshift use this pattern.

    #### Downsides

    - Can lead to deeply nested JSX ("wrapper hell") when composing many render-prop components together.
    - Defining an inline arrow function as the render prop on every render can hurt performance with `PureComponent`/`React.memo` since a new function reference is created each time (see [What are the problems with using render props with Pure Components?](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#what-are-the-problems-of-using-render-props-with-pure-components)).
    - Hooks now solve most of these use cases with less nesting and boilerplate — see [Do Hooks replace render props and higher-order components?](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#do-hooks-replace-render-props-and-higher-order-components).

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11623)，来源许可：MIT。

<a id="kba8ee92996f6"></a>

## What are Server Actions in React 19?

     **Server Actions** allow you to call server-side functions directly from client components without writing API endpoints.

     #### Basic Server Action
```jsx
     // app/actions.js
     'use server'

     export async function createPost(formData) {
       const title = formData.get('title');
       const content = formData.get('content');

       const post = await db.posts.create({
         title,
         content,
         userId: await getCurrentUser()
       });

       revalidatePath('/posts');
       redirect(`/posts/${post.id}`);
     }
```

     #### Using in Forms
```jsx
     // app/new-post.jsx
     import { createPost } from './actions';

     export default function NewPost() {
       return (
         <form action={createPost}>
           <input name="title" required />
           <textarea name="content" required />
           <button type="submit">Create Post</button>
         </form>
       );
     }
```

     #### With useFormState for Loading States
```jsx
     'use client'
     import { useFormState } from 'react-dom';
     import { createPost } from './actions';

     export default function NewPost() {
       const [state, formAction] = useFormState(createPost, { message: '' });

       return (
         <form action={formAction}>
           <input name="title" required />
           <textarea name="content" required />
           <button type="submit">Create Post</button>
           {state.message && <p>{state.message}</p>}
         </form>
       );
     }
```

     #### Progressive Enhancement
     Server Actions work even if JavaScript is disabled!
```jsx
     // This form works without JavaScript
     <form action={serverAction}>
       <input name="email" type="email" />
       <button>Subscribe</button>
     </form>
```

     #### Security
     - Automatically CSRF protected
     - Always run on server (never exposed to client)
     - Can use server-only packages safely

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L8790)，来源许可：MIT。

<a id="k7c2d13773b54"></a>

## What are stateful components?

If the behaviour of a component is dependent on the _state_ of the component then it can be termed as stateful component. These _stateful components_ are either function components with hooks or _class components_.

Let's take an example of function stateful component which update the state based on click event,

```javascript
import React, {useState} from 'react';

const App = (props) => {
const [count, setCount] = useState(0);
handleIncrement() {
  setCount(count+1);
}

return (
  <>
    <button onClick={handleIncrement}>Increment</button>
    <span>Counter: {count}</span>
  </>
  )
}
```

See Class
<p>
The equivalent class stateful component with a state that gets initialized in the `constructor`.

```jsx harmony
class App extends Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
  }

  handleIncrement() {
    setState({ count: this.state.count + 1 });
  }

  render() {
    <>
      <button onClick={() => this.handleIncrement}>Increment</button>
      <span>Count: {count}</span>
    </>;
  }
}
```

</p>

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1702)，来源许可：MIT。

<a id="kef0f3b86a786"></a>

## What are stateless components?

If the behaviour of a component is independent of its state then it can be a stateless component. You can use either a function or a class for creating stateless components. But unless you need to use a lifecycle hook in your components, you should go for function components. There are a lot of benefits if you decide to use function components here; they are easy to write, understand, and test, a little faster, and you can avoid the `this` keyword altogether.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1696)，来源许可：MIT。

<a id="k76f7319e26f7"></a>

## What are Styled Components?

     `styled-components` is a JavaScript library for styling React applications. It removes the mapping between styles and components, and lets you write actual CSS augmented with JavaScript.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4019)，来源许可：MIT。

<a id="k6489390e6a44"></a>

## What are synthetic events in React?

`SyntheticEvent` is a cross-browser wrapper around the browser's native event. Its API is same as the browser's native event, including `stopPropagation()` and `preventDefault()`, except the events work identically across all browsers. The native events can be accessed directly from synthetic events using `nativeEvent` attribute.

Let's take an example of `BookStore` title search component with the ability to get all native event properties

```js
function BookStore() {
  function handleTitleChange(e) {
    console.log("The new title is:", e.target.value);
    console.log('Synthetic event:', e); // React SyntheticEvent
    console.log('Native event:', e.nativeEvent); // Browser native event
    e.stopPropagation();
    e.preventDefault();
  }

  return <input name="title" onChange={handleTitleChange} />;
}
```

List of common synthetic events are:

*   `onClick`
*   `onChange`
*   `onSubmit`
*   `onKeyDown`, `onKeyUp`
*   `onFocus`, `onBlur`
*   `onMouseEnter`, `onMouseLeave`
*   `onTouchStart`, `onTouchEnd`

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1078)，来源许可：MIT。

<a id="k518732d4925e"></a>

## What are the &lt;Router&gt; components of React Router v6?

    React Router v6 provides below 4 `<Router>` components:

    1.  `<BrowserRouter>`:Uses the HTML5 history API for standard web apps.
    2.  `<HashRouter>`:Uses hash-based routing for static servers.
    3.  `<MemoryRouter>`:Uses in-memory routing for testing and non-browser environments.
    4.  `<StaticRouter>`:Provides static routing for server-side rendering (SSR).

    The above components will create _browser_, _hash_, _memory_ and _static_ history instances. React Router v6 makes the properties and methods of the `history` instance associated with your router available through the context in the `router` object.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2765)，来源许可：MIT。

<a id="kac40c4183192"></a>

## What are the advantages of formik over redux form library?

     Below are the main reasons to recommend formik over redux form library,

     1. The form state is inherently short-term and local, so tracking it in Redux (or any kind of Flux library) is unnecessary.
     2. Redux-Form calls your entire top-level Redux reducer multiple times ON EVERY SINGLE KEYSTROKE. This way it increases input latency for large apps.
     3. Redux-Form is 22.5 kB minified gzipped whereas Formik is 12.7 kB

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4978)，来源许可：MIT。

<a id="k86c796a5916d"></a>

## What are the advantages of React over Vue.js?

     React has the following advantages over Vue.js:

     1. Gives more flexibility in large apps developing.
     2. Easier to test.
     3. Suitable for mobile apps creating.
     4. More information and solutions available.

**Note:** The above list of advantages are purely opinionated and it vary based on the professional experience. But they are helpful as base parameters.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3984)，来源许可：MIT。

<a id="ke9e3b208ebf3"></a>

## What are the advantages of React?

Below are the list of main advantages of React,

1. Increases the application's performance with _Virtual DOM_.
2. JSX makes code easy to read and write.
3. It renders both on client and server side (_SSR_).
4. Easy to integrate with frameworks (Angular, Backbone) since it is only a view library.
5. Easy to write unit and integration tests with tools such as Jest.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1842)，来源许可：MIT。

<a id="k42b42b7ee42b"></a>

## What are the approaches to include polyfills in your create-react-app?

    There are approaches to include polyfills in create-react-app,

    1.  **Manual import from `core-js`:**

        Create a file called (something like) `polyfills.js` and import it into root `index.js` file. Run `npm install core-js` or `yarn add core-js` and import your specific required features.

```javascript
        import "core-js/fn/array/find";
        import "core-js/fn/array/includes";
        import "core-js/fn/number/is-nan";
```

    2.  **Using Polyfill service:**

        Use the polyfill.io CDN to retrieve custom, browser-specific polyfills by adding this line to `index.html`:

```html
        <script src="https://cdn.polyfill.io/v2/polyfill.min.js?features=default,Array.prototype.includes"></script>
```

        In the above script we had to explicitly request the `Array.prototype.includes` feature as it is not included in the default feature set.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11465)，来源许可：MIT。

<a id="k360c82768d4e"></a>

## What are the benefits of new JSX transform?

     There are three major benefits of new JSX transform,

     1. It is possible to use JSX without importing React packages
     2. The compiled output might improve the bundle size in a small amount
     3. The future improvements provides the flexibility to reduce the number of concepts to learn React.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5795)，来源许可：MIT。

<a id="k82a03cd026d2"></a>

## What are the benefits of React Router V4?

     Below are the main benefits of React Router V4 module,

     1. In React Router v4(version 4), the API is completely about components. A router can be visualized as a single component(`<BrowserRouter>`) which wraps specific child router components(`<Route>`).
     2. You don't need to manually set history. The router module will take care history by wrapping routes with `<BrowserRouter>` component.
     3. The application size is reduced by adding only the specific router module(Web, core, or native)

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4574)，来源许可：MIT。

<a id="k08264fbd4408"></a>

## What are the benefits of using TypeScript with ReactJS?

Below are some of the benefits of using TypeScript with ReactJS,

1. It is possible to use latest JavaScript features
2. Use of interfaces for complex type definitions
3. IDEs such as VS Code was made for TypeScript
4. Avoid bugs with the ease of readability and Validation

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5713)，来源许可：MIT。

<a id="k9b36b2189282"></a>

## What are the best practices for using React Hooks?

     Following best practices ensures your hooks are predictable, maintainable, and bug-free.

     #### 1. **Follow the Rules of Hooks**
     - Only call hooks at the top level (not inside loops, conditions, or nested functions)
     - Only call hooks from React functions (components or custom hooks)

     #### 2. **Use the ESLint Plugin**
```bash
     npm install eslint-plugin-react-hooks --save-dev
```
```json
     {
       "plugins": ["react-hooks"],
       "rules": {
         "react-hooks/rules-of-hooks": "error",
         "react-hooks/exhaustive-deps": "warn"
       }
     }
```

     #### 3. **Keep Hooks Focused and Simple**
```jsx
     // ❌ Bad: One hook doing too much
     function useEverything() {
       const [user, setUser] = useState(null);
       const [posts, setPosts] = useState([]);
       const [theme, setTheme] = useState('light');
       // ... lots of unrelated logic
     }

     // ✅ Good: Separate concerns
     function useUser() { /* user logic */ }
     function usePosts() { /* posts logic */ }
     function useTheme() { /* theme logic */ }
```

     #### 4. **Use Descriptive Names for Custom Hooks**
```jsx
     // ❌ Bad
     function useData() { }

     // ✅ Good
     function useUserAuthentication() { }
     function useFetchProducts() { }
     function useFormValidation() { }
```

     #### 5. **Properly Manage Dependencies**
```jsx
     // ❌ Bad: Missing dependency
     useEffect(() => {
       fetchUser(userId);
     }, []); // userId is missing

     // ✅ Good: All dependencies listed
     useEffect(() => {
       fetchUser(userId);
     }, [userId]);
```

     #### 6. **Avoid Inline Object/Function Dependencies**
```jsx
     // ❌ Bad: New object on every render
     useEffect(() => {
       doSomething(options);
     }, [{ page: 1, limit: 10 }]); // Always different reference

     // ✅ Good: Memoize or extract
     const options = useMemo(() => ({ page: 1, limit: 10 }), []);
     useEffect(() => {
       doSomething(options);
     }, [options]);
```

     #### 7. **Clean Up Side Effects**
     Always return a cleanup function when subscribing to events, timers, or external data sources.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L8492)，来源许可：MIT。

<a id="k1ccd719b80c4"></a>

## What are the common folder structures for React?

     There are two common practices for React project file structure.

     1.  **Grouping by features or routes:**

        One common way to structure projects is locate CSS, JS, and tests together, grouped by feature or route.

```
        common/
        ├─ Avatar.js
        ├─ Avatar.css
        ├─ APIUtils.js
        └─ APIUtils.test.js
        feed/
        ├─ index.js
        ├─ Feed.js
        ├─ Feed.css
        ├─ FeedStory.js
        ├─ FeedStory.test.js
        └─ FeedAPI.js
        profile/
        ├─ index.js
        ├─ Profile.js
        ├─ ProfileHeader.js
        ├─ ProfileHeader.css
        └─ ProfileAPI.js
```

     2.  **Grouping by file type:**

        Another popular way to structure projects is to group similar files together.

```
        api/
        ├─ APIUtils.js
        ├─ APIUtils.test.js
        ├─ ProfileAPI.js
        └─ UserAPI.js
        components/
        ├─ Avatar.js
        ├─ Avatar.css
        ├─ Feed.js
        ├─ Feed.css
        ├─ FeedStory.js
        ├─ FeedStory.test.js
        ├─ Profile.js
        ├─ ProfileHeader.js
        └─ ProfileHeader.css
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2658)，来源许可：MIT。

<a id="kbbf628af6592"></a>

## What are the core principles of Redux?

     Redux follows three fundamental principles:

     1. **Single source of truth:** The state of your whole application is stored in an object tree within a single store. The single state tree makes it easier to keep track of changes over time and debug or inspect the application.

```jsx
      const store = createStore(reducer);
```
     2. **State is read-only:** The only way to change the state is to emit an action, an object describing what happened. This ensures that neither the views nor the network callbacks will ever write directly to the state.
```js
      const action = { type: 'INCREMENT' };
      store.dispatch(action);
```
     3. **Changes are made with pure functions(Reducers):** To specify how the state tree is transformed by actions, you write reducers. Reducers are just pure functions that take the previous state and an action as parameters, and return the next state.

```jsx
      function counter(state = 0, action) {
        switch (action.type) {
          case 'INCREMENT':
            return state + 1;
          case 'DECREMENT':
            return state - 1;
          default:
            return state;
        }
      }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3295)，来源许可：MIT。

<a id="k1409c8d27f1f"></a>

## What are the differences between call() and put() in redux-saga?

     Both `call()` and `put()` are effect creator functions. `call()` function is used to create effect description, which instructs middleware to call the promise. `put()` function creates an effect, which instructs middleware to dispatch an action to the store.

     Let's take example of how these effects work for fetching particular user data.

```javascript
     function* fetchUserSaga(action) {
       // `call` function accepts rest arguments, which will be passed to `api.fetchUser` function.
       // Instructing middleware to call promise, it resolved value will be assigned to `userData` variable
       const userData = yield call(api.fetchUser, action.userId);

       // Instructing middleware to dispatch corresponding action.
       yield put({
         type: "FETCH_USER_SUCCESS",
         userData,
       });
     }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3698)，来源许可：MIT。

<a id="k934783ffe654"></a>

## What are the differences between Flux and Redux?

     The biggest conceptual difference is the data flow itself:

```
     Flux:

     View
      ↓
     Action
      ↓
     Dispatcher
      ↓
     Multiple Stores
      ↓
     View
```

     versus:

```
     Redux:

     View
      ↓
     Action
      ↓
     Middleware
      ↓
     Reducer
      ↓
     Single Store
      ↓
     View
```

     Flux routes every action through a single **Dispatcher**, which broadcasts it to **multiple stores**, each holding its own slice of state and its own change logic. Redux replaces the dispatcher with **middleware** (for side effects) and **pure reducer functions** (for state updates), all funneling into a **single store** as the one source of truth.

     Below are the major differences between Flux and Redux

     | Flux                                           | Redux                                      |
     | ---------------------------------------------- | ------------------------------------------ |
     | State is mutable                               | State is immutable                         |
     | The Store contains both state and change logic | The Store and change logic are separate    |
     | There are multiple stores exist                | There is only one store exist              |
     | All the stores are disconnected and flat       | Single store with hierarchical reducers    |
     | It has a singleton dispatcher                  | There is no concept of dispatcher          |
     | React components subscribe to the store        | Container components uses connect function |

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4523)，来源许可：MIT。
