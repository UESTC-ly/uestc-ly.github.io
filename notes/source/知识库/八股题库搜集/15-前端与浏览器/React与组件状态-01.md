# React与组件状态

<a id="k93a12d0c9256"></a>

## Agent常见模式（ReAct/Plan and Execute等）

**回答：**
Agent 系统要拆成任务规划、工具调用、环境观察、记忆管理、反思修正和停止条件。核心难点是多步轨迹的可靠性：工具是否该调用、参数是否正确、观察是否被正确利用、失败后能否恢复。反思机制本质是对中间轨迹或最终答案做自检/外部评估，但不能无限循环，必须有预算、置信度和失败兜底。

<a id="batch4-p1-q16"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L259)，来源许可：GPL-3.0。

<a id="k96b2e7e20efe"></a>

## Are custom DOM attributes supported in React v16?

**Note:** This question references React v16, which is outdated. The information below applies to React 16+, including current versions (React 18/19).

Yes. Starting with React 16, React no longer ignores unknown DOM attributes. If you write JSX with an attribute that React doesn't recognize, React will pass it through to the DOM.

For example, let's take a look at the below attribute:

```jsx harmony
<div mycustomattribute={"something"} />
```

In React 15 and earlier, this would render an empty div:

```html
<div />
```

In React 16 and later (including React 18/19), any unknown attributes will end up in the DOM:

```html
<div mycustomattribute="something" />
```

This is useful for supplying browser-specific non-standard attributes, trying new DOM APIs, and integrating with opinionated third-party libraries.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2194)，来源许可：MIT。

<a id="k5ed3e9917071"></a>

## Are there any similarities between Redux and RxJS?

     These libraries are very different for very different purposes, but there are some vague similarities.

     Redux is a tool for managing state throughout the application. It is usually used as an architecture for UIs. Think of it as an alternative to (half of) Angular. RxJS is a reactive programming library. It is usually used as a tool to accomplish asynchronous tasks in JavaScript. Think of it as an alternative to Promises. Redux uses the Reactive paradigm because the Store is reactive. The Store observes actions from a distance, and changes itself. RxJS also uses the Reactive paradigm, but instead of being an architecture, it gives you basic building blocks, Observables, to accomplish this pattern.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3403)，来源许可：MIT。

<a id="kc163779fdf25"></a>

## Can Hooks be used in class components?

     No, Hooks cannot be used inside class components. They are specially designed for function components. This is because hooks depend on the sequence in which they are called during a component’s render, something that's only guaranteed in functional components. However, both class and function components can coexist in the same application.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6847)，来源许可：MIT。

<a id="k0b9967202026"></a>

## Can I import an SVG file as react component?

     You can import SVG directly as component instead of loading it as a file. This feature is available with `react-scripts@2.0.0` and higher.

```jsx harmony
     import { ReactComponent as Logo } from "./logo.svg";

     const App = () => (
       <div>
         {/* Logo is an actual react component */}
         <Logo />
       </div>
     );
```

     **Note**: Don't forget about the curly braces in the import.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4157)，来源许可：MIT。

<a id="k1497c875385f"></a>

## Can I use javascript urls in react16.9?

     **⚠️ DEPRECATED:** As of React 19, `javascript:` URLs are no longer supported and may throw errors.

     In React 16.9, `javascript:` URLs would log a warning in the console because URLs starting with `javascript:` are dangerous security vulnerabilities (XSS attacks).

```javascript
     const companyProfile = {
       website: "javascript: alert('Your website is hacked')",
     };
     // This logged a warning in React 16.9
     // Now blocked or throws error in modern React
     <a href={companyProfile.website}>More details</a>;
```

     **Modern Best Practice:**
     - Never use `javascript:` URLs
     - Use proper event handlers instead:

```javascript
     const handleClick = (e) => {
       e.preventDefault();
       // Your logic here
     };

     <a href="#" onClick={handleClick}>More details</a>
     // Or better:
     <button onClick={handleClick}>More details</button>
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12766)，来源许可：MIT。

<a id="kc2e8e5d583c3"></a>

## Can I use web components in react application?

     Yes, you can use web components in a react application. Even though many developers won't use this combination, it may require especially if you are using third-party UI components that are written using Web Components.

     For example, let us use `Vaadin` date picker web component as below,

```javascript
     import "./App.css";
     import "@vaadin/vaadin-date-picker";
     export default function App() {
       return (
         <div className="App">
           <vaadin-date-picker label="When were you born?"></vaadin-date-picker>
         </div>
       );
     }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4994)，来源许可：MIT。

<a id="kf5e751ca9e54"></a>

## Can Redux only be used with React?

     Redux can be used as a data store for any UI layer. The most common usage is with React and React Native, but there are bindings available for Angular, Angular 2, Vue, Mithril, and more. Redux simply provides a subscription mechanism which can be used by any other code.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4116)，来源许可：MIT。

<a id="kacfe220dc0cd"></a>

## Can useState take a function as an initial value?

     Yes, `useState` can take a function as an initial value, and this is a useful feature in React called **lazy initialization**. This function is also known as **initializer function**.

     When you call useState(initialValue), you normally pass in a value directly:

```js
     const [count, setCount] = useState(0);  // initial value is 0
```

     But if calculating that initial value is expensive or involves logic, you can pass a function that returns the value:
```js
        const [count, setCount] = useState(() => {
        // This function only runs once — when the component first renders
        return expensiveComputation();
        });
```

     This function avoids doing heavy computation on every render. If you don't use this function form and invokes it directly, the function will run everytime the component renders and impact the performance.
     For example, the below usage is not recommended. 
```js
     const [count, setCount] = useState(expensiveComputation());
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6884)，来源许可：MIT。

<a id="k2dca6befddcf"></a>

## Can you combine useReducer with useContext?

      Yes, it's common to combine **useReducer** with **useContext** to build a lightweight state management system similar to Redux:

```js
      const AppContext = React.createContext();

      function AppProvider({ children }) {
        const [state, dispatch] = useReducer(reducer, initialState);
        return (
          <AppContext.Provider value={{ state, dispatch }}>
            {children}
          </AppContext.Provider>
        );
      }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7138)，来源许可：MIT。

<a id="k7f847cc3e728"></a>

## Can you describe about componentDidCatch lifecycle method signature?

     The **componentDidCatch** lifecycle method is invoked after an error has been thrown by a descendant component. The method receives two parameters,

     1. error: - The error object which was thrown
     2. info: - An object with a componentStack key contains the information about which component threw the error.

     The method structure would be as follows

```javascript
     componentDidCatch(error, info);
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4584)，来源许可：MIT。

<a id="k3160a1b222ff"></a>

## Can you explain how useState works internally?

      React’s hooks, including `useState`, rely on some internal machinery that keeps track of state **per component** and **per hook call** during rendering. Here's a simplified explanation of the internal mechanics:

      #### 1. **Hook List / Linked List**

      *   React maintains a linked list or array of "hook states" for each component.
      *   When a component renders, React keeps track of which hook it is currently processing via a cursor/index.
      *   Each call to `useState()` corresponds to one "slot" in this list.

      #### 2. **State Storage**

      *   Each slot stores:
        *   The current state value.
        *   A queue of pending state updates.

      #### 3. **Initial Render**

      *   When the component first renders, React:
         *   Creates a new slot for `useState` with the initial state (e.g., `0`).
         *   Returns `[state, updaterFunction]`.

      #### 4. **Updater Function**

      *   The updater function (`setCount`) is a closure that, when called:
        *   Enqueues a state update to React's internal queue.
        *   Schedules a re-render of the component.

      #### 5. **Re-render and State Update**

      *   On the next render:
        *   React processes all queued updates for each hook slot.
        *   Updates the stored state value accordingly.
        *   Returns the new state to the component.

      #### 6. **Important: Hook Order**

      *   Hooks must be called in the same order on every render so React can match hook calls to their internal slots.
      *   That’s why you can’t call hooks conditionally.

      The pseudocode for internal implementation of `useState` looks like below,
```js
        let hookIndex = 0;
        const hooks = [];

        function useState(initialValue) {
            const currentIndex = hookIndex;

            if (!hooks[currentIndex]) {
                // First render: initialize state
                hooks[currentIndex] = {
                    state: initialValue,
                    queue: [],
                };
            }

            const hook = hooks[currentIndex];

            // Process queued updates
            hook.queue.forEach(update => {
                hook.state = update(hook.state);
            });
            hook.queue = [];

            // Define updater function
            function setState(action) {
                // action can be new state or function(state) => new state
                hook.queue.push(typeof action === 'function' ? action : () => action);
                scheduleRender(); // triggers React re-render
            }

            hookIndex++;
            return [hook.state, setState];
        }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6984)，来源许可：MIT。

<a id="k04bba71fb74f"></a>

## Can you force a component to re-render without calling setState?

By default, when your component's state or props change, your component will re-render. If your `render()` method depends on some other data, you can tell React that the component needs re-rendering by calling `forceUpdate()`.

```javascript
component.forceUpdate(callback);
```

It is recommended to avoid all uses of `forceUpdate()` and only read from `this.props` and `this.state` in `render()`.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11298)，来源许可：MIT。

<a id="kf2127e97b53d"></a>

## Can you have multiple useEffect hooks in a single component?

      Yes, multiple useEffect hooks are allowed and recommended when you want to separate concerns.

```jsx
      useEffect(() => {
        // Handles API fetch
      }, []);

      useEffect(() => {
        // Handles event listeners
      }, []);
```
      Each effect runs independently and helps make code modular and easier to debug.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7583)，来源许可：MIT。

<a id="k889f329290ec"></a>

## Can you list down top websites or applications using react as front end framework?

     Below are the `top 10 websites` using React as their front-end framework,

     1. Facebook
     2. Uber
     3. Instagram
     4. WhatsApp
     5. Khan Academy
     6. Airbnb
     7. Dropbox
     8. Flipboard
     9. Netflix
     10. PayPal

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5398)，来源许可：MIT。

<a id="k6476bd6791f9"></a>

## Can You Use Multiple Contexts in One Component?

     Yes, it is possible. You can use multiple contexts inside the same component by calling useContext multiple times, once for each context.

     It can be achieved with below steps,

        *   Create multiple contexts using `createContext()`.
        *   Wrap your component tree with multiple `<Provider>`s.
        *   Call `useContext()` separately for each context in the same component.

     **Example: Using `ThemeContext` and `UserContext` Together**
```js
     import React, { createContext, useContext } from 'react';

      // Step 1: Create two contexts
      const ThemeContext = createContext();
      const UserContext = createContext();

      function Dashboard() {
        // Step 2: Use both contexts
        const theme = useContext(ThemeContext);
        const user = useContext(UserContext);

        return (
          <div style={{ background: theme === 'dark' ? '#333' : '#fff' }}>
            <h1>Welcome, {user.name}</h1>
            <p>Current theme: {theme}</p>
          </div>
        );
      }

      // Step 3: Provide both contexts
      function App() {
        return (
          <ThemeContext.Provider value="dark">
            <UserContext.Provider value={{ name: 'Sudheer' }}>
              <Dashboard />
            </UserContext.Provider>
          </ThemeContext.Provider>
        );
      }

      export default App;
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7378)，来源许可：MIT。

<a id="k78a9e912176b"></a>

## CoT、ReAct、Plan-and-Execute 在工程实现上有什么区别？如何选择？

**回答：**

三者处于不同层次：CoT 是与分步推理相关的方法，ReAct 是推理与环境交互交替的模式，Plan-and-Execute 是将计划与执行职责分开的架构。它们可以组合，不是严格互斥的三个框架。

| 方法 | 运行方式 | 适用任务 | 主要边界 |
| --- | --- | --- | --- |
| CoT | 模型内部或单次生成中进行中间推理 | 有足够输入的一次性分析 | 不等于执行协议，文本解释不保证忠实反映真实计算 |
| ReAct | 观察结果后选择下一动作，逐步与环境交互 | 信息未知、需动态探索与查询 | 调用轮次、错误累积、成本和循环风险 |
| Plan-and-Execute | 生成结构化计划，执行器完成步骤，必要时重规划 | 长流程、有依赖、可并行与可恢复任务 | 计划可能过时，需要反馈、检查点和重规划 |

生产系统应依赖显式计划、工具参数、观察结果和验证状态，不要求输出模型隐藏推理过程，也不把自由文本思考当作授权依据。ReAct 可以通过结构化 tool call 实现，不需要在用户界面暴露内部思维链。

固定业务流程优先用工作流或状态机；开放式信息收集采用受预算约束的 ReAct；步骤较多的分析任务采用依赖图计划与执行，局部节点可以再使用 ReAct。高风险操作统一进入执行门禁，与使用哪种推理方式无关。

选择时固定模型、工具和预算，比较任务成功率、无效调用率、恢复能力、p95 延迟和单次成功成本。**架构越复杂，不代表智能越强；需要证明额外的规划与交互确实减少了业务失败。**

<a id="baidu-agent-20260922-r2-q7"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%99%BE%E5%BA%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1047)，来源许可：GPL-3.0。

<a id="k2d1124cd4fe6"></a>

## Critic什么意思？为什么不用ReAct？

**回答：**

Critic 是评估器或审查角色，用来判断当前计划、步骤产物或最终结果是否满足 rubric、事实、测试和业务约束，并给出修订、重规划或停止信号。它可以是规则、单元测试、奖励模型、LLM Judge 或人工，并不天然等于一个独立大模型 Agent。

“Critic”和“ReAct”不在同一维度，因此并不互斥：ReAct 描述的是执行过程中 Thought/Action/Observation 的局部循环；Critic 描述的是质量反馈机制。常见组合是 Planner 生成全局计划，Executor 在每个步骤内部用 ReAct 调工具，Critic 在阶段边界验收结果。

不采用**纯 ReAct**的理由通常有：长任务需要全局依赖和里程碑，ReAct 容易局部贪心；工具调用串行导致高延迟；Observation 持续累积；模型可能重复尝试；完成条件和质量标准不容易仅靠下一步推理保证。对于步骤明确的业务，Workflow + Validator 更稳定；对于开放探索，ReAct 更合适。

同样，Critic 也不是越多越好。若结果可由测试或业务状态确定，就优先确定性验证；LLM Critic 会有偏好、位置和自洽偏差，自己评自己尤其容易放过错误。正确回答不是“Critic 替代 ReAct”，而是根据任务把规划、执行和验证放在合适边界，并说明为什么。

<a id="xiaohongshu-agent-dev-20260812-q13"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%B0%8F%E7%BA%A2%E4%B9%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1090)，来源许可：GPL-3.0。

<a id="k208dea8e2e64"></a>

## Describe about data flow in react?

     React implements one-way reactive data flow using props which reduce boilerplate and is easier to understand than traditional two-way data binding.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5550)，来源许可：MIT。

<a id="k638551df6c5e"></a>

## Do browsers understand JSX code?

     No, browsers can't understand JSX code. You need a transpiler to convert your JSX to regular Javascript that browsers can understand. The most widely used transpiler right now is Babel.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5545)，来源许可：MIT。

<a id="k70ae91db4692"></a>

## Do Hooks replace render props and higher order components?

Both render props and higher-order components render only a single child but in most of the cases Hooks are a simpler way to serve this by reducing nesting in your tree.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2106)，来源许可：MIT。

<a id="ka1a6dad08f45"></a>

## Do I need to keep all my state into Redux? Should I ever use react internal state?

     It is up to the developer's decision, i.e., it is developer's job to determine what kinds of state make up your application, and where each piece of state should live. Some users prefer to keep every single piece of data in Redux, to maintain a fully serializable and controlled version of their application at all times. Others prefer to keep non-critical or UI state, such as “is this dropdown currently open”, inside a component's internal state.

     Below are the rules of thumb to determine what kind of data should be put into Redux

     1. Do other parts of the application care about this data?
     2. Do you need to be able to create further derived data based on this original data?
     3. Is the same data being used to drive multiple components?
     4. Is there value to you in being able to restore this state to a given point in time (ie, time travel debugging)?
     5. Do you want to cache the data (i.e, use what's in state if it's already there instead of re-requesting it)?

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4210)，来源许可：MIT。

<a id="ke8336723cb37"></a>

## Do I need to rewrite all my class components with hooks?

     No. But you can try Hooks in a few components(or new components) without rewriting any existing code. Because there are no plans to remove classes in ReactJS.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5420)，来源许可：MIT。

<a id="k34c175f412de"></a>

## Do you need to have a particular build tool to use Redux?

     Redux is originally written in ES6 and transpiled for production into ES5 with Webpack and Babel. You should be able to use it regardless of your JavaScript build process. Redux also offers a UMD build that can be used directly without any build process at all.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4122)，来源许可：MIT。

<a id="k38203a5723d0"></a>

## Does React support all HTML attributes?

     As of React 16, both standard or custom DOM attributes are fully supported. Since React components often take both custom and DOM-related props, React uses the camelCase convention just like the DOM APIs.

     Let us take few props with respect to standard HTML attributes,

```javascript
     <div tabIndex="-1" />      // Just like node.tabIndex DOM API
     <div className="Button" /> // Just like node.className DOM API
     <input readOnly={true} />  // Just like node.readOnly DOM API
```

     These props work similarly to the corresponding HTML attributes, with the exception of the special cases. It also support all SVG attributes.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4792)，来源许可：MIT。

<a id="ke139e5f049f4"></a>

## Does React.memo prevent Context consumers from re-rendering?

     **No.** `React.memo` only performs a shallow comparison of a component's **props** — it has no visibility into context. If a component reads a value via `useContext`/`Context.Consumer`, that component re-renders whenever the **context value** changes, regardless of whether it's wrapped in `React.memo` and regardless of whether its own props changed.

```jsx
     const CountContext = React.createContext();

     // Wrapping with React.memo does NOT help here
     const Display = React.memo(function Display() {
       const count = useContext(CountContext);
       return <div>{count}</div>;
     });

     function App() {
       const [count, setCount] = useState(0);
       return (
         <CountContext.Provider value={count}>
           <button onClick={() => setCount((c) => c + 1)}>Increment</button>
           <Display />
         </CountContext.Provider>
       );
     }
```

     Every time `count` changes, `Display` re-renders even though it takes no props and is memoized — `React.memo` bails out based on prop equality, but context consumption bypasses that check entirely.

     #### How to actually reduce these re-renders

     - **Split contexts** by concern so a component only subscribes to the slice of state it actually needs (see [What's a common pitfall when using useContext with objects?](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#whats-a-common-pitfall-when-using-usecontext-with-objects)).
     - **Memoize the provider's value** with `useMemo` so the reference only changes when the underlying data changes — this reduces churn but doesn't stop consumers from re-rendering when the value itself legitimately changes.
     - **Push `useContext` down** into a small wrapper component and pass the extracted value as a prop to a memoized child. The child (wrapped in `React.memo`) will now correctly skip re-rendering when that specific prop hasn't changed, since the memoization check happens one level below the context read.
     - **Use a state management library or selector-based API** (Redux's `useSelector`, Zustand, Jotai) when you need fine-grained, per-field subscriptions instead of one large context object.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L9446)，来源许可：MIT。

<a id="kc8668e33b27c"></a>

## Does the statics object work with ES6 classes in React?

    No, `statics` only works with `React.createClass()`:

```javascript
    someComponent = React.createClass({
      statics: {
        someMethod: function () {
          // ..
        },
      },
    });
```

    But you can write statics inside ES6+ classes as below,

```javascript
    class Component extends React.Component {
      static propTypes = {
        // ...
      };

      static someMethod() {
        // ...
      }
    }
```

    or writing them outside class as below,

```javascript
    class Component extends React.Component {
       ....
    }

    Component.propTypes = {...}
    Component.someMethod = function(){....}
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11826)，来源许可：MIT。

<a id="kb0129214e34a"></a>

## Does useMemo prevent re-rendering of child components?

        The `useMemo` hook **does not directly prevent re-rendering of child components**. Its main purpose is to memoize the result of an expensive computation so that it doesn’t get recalculated unless its dependencies change. While this can improve performance, it doesn’t inherently control whether a child component re-renders.

        However, `useMemo` **can help prevent re-renders** when the memoized value is passed as a prop to a child component that is wrapped in `React.memo`. In that case, if the memoized value doesn’t change between renders (i.e., it has the same reference), React.memo can skip re-rendering the child. So, while `useMemo` doesn’t stop renders on its own, it **works in combination** with tools like `React.memo` to optimize rendering behavior.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7884)，来源许可：MIT。

<a id="kf2ce959f06bd"></a>

## Give an example of Styled Components?

     Lets create `<Title>` and `<Wrapper>` components with specific styles for each.

```javascript
     import React from "react";
     import styled from "styled-components";

     // Create a <Title> component that renders an <h1> which is centered, red and sized at 1.5em
     const Title = styled.h1`
       font-size: 1.5em;
       text-align: center;
       color: palevioletred;
     `;

     // Create a <Wrapper> component that renders a <section> with some padding and a papayawhip background
     const Wrapper = styled.section`
       padding: 4em;
       background: papayawhip;
     `;
```

     These two variables, `Title` and `Wrapper`, are now components that you can render just like any other react component.

```jsx harmony
     <Wrapper>
       <Title>{"Lets start first styled component!"}</Title>
     </Wrapper>
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4025)，来源许可：MIT。

<a id="kbd65e20f5779"></a>

## Give an example on How to use context?

    **Context** is designed to share data that can be considered **global** for a tree of React components.

    For example, in the code below lets manually thread through a “theme” prop in order to style the Button component.

```javascript
    //Lets create a context with a default theme value "luna"
    const ThemeContext = React.createContext("luna");
    // Create App component where it uses provider to pass theme value in the tree
    class App extends React.Component {
      render() {
        return (
          <ThemeContext.Provider value="nova">
            <Toolbar />
          </ThemeContext.Provider>
        );
      }
    }
    // A middle component where you don't need to pass theme prop anymore
    function Toolbar(props) {
      return (
        <div>
          <ThemedButton />
        </div>
      );
    }
    // Lets read theme value in the button component to use
    class ThemedButton extends React.Component {
      static contextType = ThemeContext;
      render() {
        return <Button theme={this.context} />;
      }
    }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12373)，来源许可：MIT。

<a id="k1f6c8a9863cb"></a>

## How are error boundaries handled in React v15?

**⚠️ LEGACY:** This question is only relevant for historical context. React v15 is extremely outdated (released in 2016).

React v15 provided very basic support for _error boundaries_ using the `unstable_handleError` method. This was an experimental feature that was later redesigned and renamed to `componentDidCatch` in React v16.

**Modern Error Boundaries (React 16+):**
- Use `static getDerivedStateFromError(error)` for UI fallback
- Use `componentDidCatch(error, info)` for logging
- Work consistently across server and client rendering

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10873)，来源许可：MIT。

<a id="k5220e964ff77"></a>

## How can we find the version of React at runtime in the browser?

    You can use `React.version` to get the version.

```jsx harmony
    const REACT_VERSION = React.version;

    ReactDOM.render(
      <div>{`React version: ${REACT_VERSION}`}</div>,
      document.getElementById("app")
    );
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2537)，来源许可：MIT。

<a id="k29434f18127c"></a>

## How do reactive dependencies in the useEffect dependency array affect its execution behavior?

     The `useEffect` hook accepts an optional dependencies argument that accepts an array of reactive values. The **dependency array** determines **when** the effect runs. i.e, It makes `useEffect` _reactive_ to changes in specified values.

     #### **How Dependency Array Affects Behavior**

     1. **Empty Dependency Array:** `**[]**`

```css
     useEffect(() => {
       // runs once after the initial render
     }, []);
```

      *   Effect runs **only once** (like `componentDidMount`).
      *   Ignores all state/prop changes.

     2. **With Specific Dependencies:** `**[count, user]**`

```css
     useEffect(() => {
       // runs after initial render
       // AND whenever `count` or `user` changes
     }, [count, user]);
```

       *   Effect runs on **first render**, and
       *   Again **every time** any dependency value changes.

     3. **No Dependency Array (Omitted)**

```css
          useEffect(() => {
            // runs after **every** render
          });
```

           *   Effect runs after **every render**, regardless of what changed.
           *   Can lead to **performance issues** if not used carefully.

       React uses shallow comparison of the dependencies. If any value has changed (!==), the effect will re-run.

       **Note:** This hook works well when dependencies are primitives or memoized objects/functions.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7499)，来源许可：MIT。

<a id="k516c783696b4"></a>

## How do you access imperative API of web components?

     Web Components often expose an imperative API to implement its functions. You will need to use a **ref** to interact with the DOM node directly if you want to access imperative API of a web component. But if you are using third-party Web Components, the best solution is to write a React component that behaves as a **wrapper** for your Web Component.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5525)，来源许可：MIT。

<a id="k9e9b405e6c1b"></a>

## How do you access props in attribute quotes?

React (or JSX) doesn't support variable interpolation inside an attribute value. The below representation won't work:

```jsx harmony
<img className="image" src="images/{this.props.image}" />
```

But you can put any JS expression inside curly braces as the entire attribute value. So the below expression works:

```jsx harmony
<img className="image" src={"images/" + this.props.image} />
```

Using _template strings_ will also work:

```jsx harmony
<img className="image" src={`images/${this.props.image}`} />
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2250)，来源许可：MIT。

<a id="kbcbee8beb4e6"></a>

## How do you apply vendor prefixes to inline styles in React?

    React _does not_ apply _vendor prefixes_ automatically. You need to add vendor prefixes manually.

```jsx harmony
    <div
      style={{
        transform: "rotate(90deg)",
        WebkitTransform: "rotate(90deg)", // note the capital 'W' here
        msTransform: "rotate(90deg)", // 'ms' is the only lowercase vendor prefix
      }}
    />
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2565)，来源许可：MIT。

<a id="k681f7fe87ed9"></a>

## How do you conditionally render components?

In some cases you want to render different components depending on some state. JSX does not render `false` or `undefined`, so you can use conditional _short-circuiting_ to render a given part of your component only if a certain condition is true.

```jsx harmony
const MyComponent = ({ name, address }) => (
  <div>
    <h2>{name}</h2>
    {address && <p>{address}</p>}
  </div>
);
```

If you need an `if-else` condition then use _ternary operator_.

```jsx harmony
const MyComponent = ({ name, address }) => (
  <div>
    <h2>{name}</h2>
    {address ? <p>{address}</p> : <p>{"Address is not available"}</p>}
  </div>
);
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2009)，来源许可：MIT。

<a id="k8c60bd02a74e"></a>

## How do you create HOC using render props?

    You can implement most higher-order components (HOC) using a regular component with a render prop. For example, if you would prefer to have a withMouse HOC instead of a <Mouse> component, you could easily create one using a regular <Mouse> with a render prop.

```javascript
    function withMouse(Component) {
      return class extends React.Component {
        render() {
          return (
            <Mouse
              render={(mouse) => <Component {...this.props} mouse={mouse} />}
            />
          );
        }
      };
    }
```

    This way render props gives the flexibility of using either pattern.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12638)，来源许可：MIT。

<a id="k613cbf56e5e2"></a>

## How do you debug a Redux performance problem?

     A practical, step-by-step approach:

     1.  **Confirm it's actually Redux**: use the React DevTools **Profiler** to see which components re-render and how often, before assuming Redux is the culprit.
     2.  **Inspect actions/state with Redux DevTools**: check how frequently actions are dispatched and how large/deeply nested the state diffs are on each action.
     3.  **Look for unstable selector results**: a selector that returns a new object/array/function on every call (e.g., `state => state.items.filter(...)`) breaks `useSelector`'s reference equality check and forces re-renders even when nothing meaningful changed. Wrap it in `createSelector` (Q335).
     4.  **Check for over-broad `useSelector` calls**: selecting an entire slice (`state.user`) instead of the specific field needed (`state.user.name`) causes re-renders on unrelated field changes (Q334).
     5.  **Verify normalization**: deeply nested/duplicated state (Q336) often causes broad reference changes on every update; normalizing narrows down what actually changes.
     6.  **Check for missing memoization on connected children**: wrap presentational components in `React.memo` so a parent re-render doesn't cascade if their own props are unchanged.
     7.  **Use the `why-did-you-render` library** (or React DevTools' "highlight updates") to visually confirm exactly which components re-render and why.
     8.  **Measure, don't guess**: use the Profiler's flame chart/ranked view to confirm the fix actually reduced render counts/time before moving on.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L9968)，来源许可：MIT。

<a id="k0818d3835266"></a>

## How do you get redux scaffolding using create-react-app?

    Redux team has provided official redux+js or redux+typescript templates for create-react-app project. The generated project setup includes,
    1.  Redux Toolkit and React-Redux dependencies
    2.  Create and configure Redux store
    3.  React-Redux `<Provider>` passing the store to React components
    4.  Small "counter" example to demo how to add redux logic and React-Redux hooks API to interact with the store from components
        The below commands need to be executed along with template option as below,
    5.  **Javascript template:**
```js
    npx create-react-app my-app --template redux
```
    2.  **Typescript template:**
```js
    npx create-react-app my-app --template redux-typescript
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12685)，来源许可：MIT。

<a id="kd832dcab24ce"></a>

## How do you handle cleanup in useEffect?

     The cleanup function in `useEffect` is used to **clean up side effects** before the component unmounts or before the effect runs again. This prevents memory leaks, stale data, and unexpected behavior.

     #### Syntax
```js
     useEffect(() => {
       // Setup code

       return () => {
         // Cleanup code
       };
     }, [dependencies]);
```

     #### Common Cleanup Scenarios

     **1. Event Listeners**
```jsx
     useEffect(() => {
       const handleResize = () => setWidth(window.innerWidth);
       window.addEventListener('resize', handleResize);

       return () => window.removeEventListener('resize', handleResize);
     }, []);
```

     **2. Timers and Intervals**
```jsx
     useEffect(() => {
       const intervalId = setInterval(() => {
         setCount(c => c + 1);
       }, 1000);

       return () => clearInterval(intervalId);
     }, []);
```

     **3. Subscriptions**
```jsx
     useEffect(() => {
       const subscription = dataSource.subscribe(handleChange);

       return () => subscription.unsubscribe();
     }, [dataSource]);
```

     **4. Abort Fetch Requests**
```jsx
     useEffect(() => {
       const controller = new AbortController();

       fetch(url, { signal: controller.signal })
         .then(response => response.json())
         .then(data => setData(data))
         .catch(err => {
           if (err.name !== 'AbortError') {
             setError(err);
           }
         });

       return () => controller.abort();
     }, [url]);
```

     **When Cleanup Runs:**
     - Before the component unmounts
     - Before re-running the effect when dependencies change

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L8374)，来源许可：MIT。

<a id="k966593773f83"></a>

## How do you handle race conditions in Redux?

     A race condition happens when multiple async requests are in flight and they **resolve out of order** — e.g., a user types quickly in a search box, an older request for "re" resolves *after* the newer request for "react", overwriting the correct results with stale ones.

     1.  **`createAsyncThunk` + request tracking**: store the latest `requestId` and ignore results from stale requests.

```javascript
         const fetchResults = createAsyncThunk("search/fetch", async (query) => {
           const res = await fetch(`/api/search?q=${query}`);
           return res.json();
         });

         builder.addCase(fetchResults.fulfilled, (state, action) => {
           // Only apply the result if it belongs to the most recent request
           if (action.meta.requestId === state.currentRequestId) {
             state.results = action.payload;
           }
         });
```

     2.  **Abort stale requests** using `AbortController`, which `createAsyncThunk` supports via `thunkAPI.signal` — cancel the previous request when a new one starts.
     3.  **Debounce/throttle the trigger** (e.g., debounce keystrokes) so fewer overlapping requests are made in the first place.
     4.  **Use RTK Query**, which automatically de-duplicates in-flight requests, cancels/ignores stale ones, and keeps the cache consistent without manual bookkeeping.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L9898)，来源许可：MIT。

<a id="k7b4b1bdd2eae"></a>

## How do you make sure that user remains authenticated on page refresh while using Context API State Management?

     When a user logs in and reload, to persist the state generally we add the load user action in the useEffect hooks in the main App.js. While using Redux, loadUser action can be easily accessed.

     **App.js**

```js
     import { loadUser } from "../actions/auth";
     store.dispatch(loadUser());
```

     - But while using **Context API**, to access context in App.js, wrap the AuthState in index.js so that App.js can access the auth context. Now whenever the page reloads, no matter what route you are on, the user will be authenticated as **loadUser** action will be triggered on each re-render.

     **index.js**

```js
     import React from "react";
     import ReactDOM from "react-dom";
     import App from "./App";
     import AuthState from "./context/auth/AuthState";

     ReactDOM.render(
       <React.StrictMode>
         <AuthState>
           <App />
         </AuthState>
       </React.StrictMode>,
       document.getElementById("root")
     );
```

```js
     const authContext = useContext(AuthContext);

     const { loadUser } = authContext;

     useEffect(() => {
       loadUser();
     }, []);
```

     **loadUser**

```js
     const loadUser = async () => {
       const token = sessionStorage.getItem("token");

       if (!token) {
         dispatch({
           type: ERROR,
         });
       }
       setAuthToken(token);

       try {
         const res = await axios("/api/auth");

         dispatch({
           type: USER_LOADED,
           payload: res.data.data,
         });
       } catch (err) {
         console.error(err);
       }
     };
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5724)，来源许可：MIT。

<a id="ke6d5cbf38493"></a>

## How do you memoize a component?

There are memoize libraries available which can be used on function components.

For example `moize` library can memoize the component in another component.

```jsx harmony
import moize from "moize";
import Component from "./components/Component"; // this module exports a non-memoized component

const MemoizedFoo = moize.react(Component);

const Consumer = () => {
  <div>
    {"I will memoize the following entry:"}
    <MemoizedFoo />
  </div>;
};
```

**Update:** Since React v16.6.0, we have a `React.memo`. It provides a higher order component which memoizes component unless the props change. To use it, simply wrap the component using React.memo before you use it.

```js
const MemoComponent = React.memo(function MemoComponent(props) {
  /* render using props */
});
OR;
export default React.memo(MyFunctionComponent);
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2053)，来源许可：MIT。

<a id="k462d48bd977d"></a>

## How do you navigate programmatically in React Router?

     In React Router v6+, programmatic navigation (redirecting from code rather than a user clicking a link) is done with the **`useNavigate`** hook, which replaces the old `history.push()`/`this.props.history.push()` approach from v4/v5 (see [How do you programmatically navigate using React Router v4?](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#how-do-you-programmatically-navigate-using-react-router-v4)).

```jsx
     import { useNavigate } from "react-router-dom";

     function LoginForm() {
       const navigate = useNavigate();

       async function handleSubmit(e) {
         e.preventDefault();
         await login();
         navigate("/dashboard");        // push a new entry (like clicking a link)
         // navigate("/dashboard", { replace: true }); // replace current entry (no back button to login)
         // navigate(-1);                 // go back, like history.back()
         // navigate("/users/42", { state: { from: "login" } }); // pass state to the next route
       }

       return <form onSubmit={handleSubmit}>{/* ... */}</form>;
     }
```

     Key points:

     - `navigate(to)` pushes a new history entry; `navigate(to, { replace: true })` replaces the current one (useful after login/logout so the back button doesn't return to the old page).
     - `navigate(delta)` with a number (e.g., `navigate(-1)`, `navigate(1)`) moves through history like the browser back/forward buttons.
     - `useNavigate` can only be called inside components rendered under a `<Router>`; it can't be used outside React (for that, some apps keep a module-level history object created with `createBrowserRouter`/`history` package instead).
     - Prefer declarative navigation (`<Link>`/`<NavLink>`) for user-initiated clicks, and reserve `useNavigate` for navigation triggered by logic — form submissions, redirects after auth, timers, etc.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10123)，来源许可：MIT。

<a id="k3bec7ed74527"></a>

## How do you pass an event handler to a component?

     You can pass event handlers and other functions as props to child components. The functions can be passed to child component as below,

```jsx
     function Button({ onClick }) {
       return <button onClick={onClick}>Download</button>;
     }

     export default function downloadExcel() {
       function handleClick() {
         alert("Downloaded");
       }

       return <Button onClick={handleClick}></Button>;
     }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4837)，来源许可：MIT。

<a id="ka05ff9818d61"></a>

## How do you persist Redux state?

     **`redux-persist`** is the standard library for persisting and rehydrating a Redux store across page reloads/app restarts. It wraps your root reducer so selected slices are automatically saved to storage (e.g., `localStorage` on web, `AsyncStorage` on React Native) and restored on startup.

```javascript
     import { combineReducers } from "redux";
     import { configureStore } from "@reduxjs/toolkit";
     import { persistStore, persistReducer } from "redux-persist";
     import storage from "redux-persist/lib/storage"; // localStorage

     const rootReducer = combineReducers({ user: userReducer, cart: cartReducer });

     const persistConfig = {
       key: "root",
       storage,
       whitelist: ["cart"], // only persist the `cart` slice
     };

     const persistedReducer = persistReducer(persistConfig, rootReducer);

     export const store = configureStore({
       reducer: persistedReducer,
       middleware: (getDefaultMiddleware) =>
         getDefaultMiddleware({ serializableCheck: false }),
     });

     export const persistor = persistStore(store);
```

```jsx
     // index.js
     import { PersistGate } from "redux-persist/integration/react";

     <Provider store={store}>
       <PersistGate loading={null} persistor={persistor}>
         <App />
       </PersistGate>
     </Provider>;
```

     Key points: use `whitelist`/`blacklist` to persist only the slices that need it (e.g., auth token, cart), disable `serializableCheck` for the persistence actions RTK flags by default, and wrap the app in `<PersistGate>` so rendering waits until the persisted state has been rehydrated.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L9924)，来源许可：MIT。

<a id="kf01588fbb818"></a>

## How do you prevent unnecessary Redux re-renders?

     By default, `useSelector` re-renders a component whenever the **selected value's reference** changes between renders (it uses strict `===` comparison). Most unnecessary re-renders come from selectors that return a *new* object/array/function on every call, so React-Redux thinks the data changed even though it didn't. Ways to prevent this:

     1.  **Select the smallest piece of state you need** instead of the whole slice:

```javascript
         // BAD: re-renders whenever ANY field in `user` changes
         const user = useSelector((state) => state.user);

         // GOOD: only re-renders when `name` changes
         const name = useSelector((state) => state.user.name);
```

     2.  **Memoize derived/computed selectors** with `createSelector` (see next question) so a new array/object is only created when its actual inputs change.
     3.  **Use a custom equality function** (e.g., `shallowEqual` from `react-redux`) when you must select multiple fields as an object:

```javascript
         import { shallowEqual, useSelector } from "react-redux";

         const { name, email } = useSelector(
           (state) => ({ name: state.user.name, email: state.user.email }),
           shallowEqual
         );
```

     4.  **Split one large connected component into smaller ones**, each with its own narrow `useSelector`, so a state change only re-renders the component that actually cares about it.
     5.  **Wrap presentational children in `React.memo`** so they skip re-rendering when their own props haven't changed, even if their parent re-renders.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L9647)，来源许可：MIT。

<a id="k91dca1aa633d"></a>

## How do you print falsy values in JSX?

     The falsy values such as false, null, undefined, and true are valid children but they don't render anything. If you still want to display them then you need to convert it to string. Let's take an example on how to convert to a string,

```javascript
     <div>My JavaScript variable is {String(myVariable)}.</div>
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5315)，来源许可：MIT。

<a id="k7a983421fceb"></a>

## How do you programmatically navigate using React Router v4?

    There are three different ways to achieve programmatic routing/navigation within components.

    1.  **Using the `withRouter()` higher-order function:**

        The `withRouter()` higher-order function will inject the history object as a prop of the component. This object provides `push()` and `replace()` methods to avoid the usage of context.

```jsx harmony
        import { withRouter } from "react-router-dom"; // this also works with 'react-router-native'

        const Button = withRouter(({ history }) => (
          <button
            type="button"
            onClick={() => {
              history.push("/new-location");
            }}
          >
            {"Click Me!"}
          </button>
        ));
```

    2.  **Using `<Route>` component and render props pattern:**

        The `<Route>` component passes the same props as `withRouter()`, so you will be able to access the history methods through the history prop.

```jsx harmony
        import { Route } from "react-router-dom";

        const Button = () => (
          <Route
            render={({ history }) => (
              <button
                type="button"
                onClick={() => {
                  history.push("/new-location");
                }}
              >
                {"Click Me!"}
              </button>
            )}
          />
        );
```

    3.  **Using context:**

        This option is not recommended and treated as unstable API.

```jsx harmony
        const Button = (props, context) => (
          <button
            type="button"
            onClick={() => {
              context.history.push("/new-location");
            }}
          >
            {"Click Me!"}
          </button>
        );

        Button.contextTypes = {
          history: React.PropTypes.shape({
            push: React.PropTypes.func.isRequired,
          }),
        };
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2789)，来源许可：MIT。

<a id="ka84c54566e01"></a>

## How do you render Array, Strings and Numbers in React 16 Version?

     **Note:** This question references React 16. These features remain valid in current React versions (18/19).

     **Arrays**: Starting with React 16, you can return multiple sibling elements without a wrapping element by returning an array or using Fragments.

     **Array approach:**
```jsx
     const ReactJSDevs = () => {
       return [
         <li key="1">John</li>,
         <li key="2">Jackie</li>,
         <li key="3">Jordan</li>,
       ];
     };
```

     **Fragment approach (preferred):**
```jsx
     const ReactJSDevs = () => {
       return (
         <>
           <li>John</li>
           <li>Jackie</li>
           <li>Jordan</li>
         </>
       );
     };
```

     You can also merge this array of items in another array component.

```jsx
     const JSDevs = () => {
       return (
         <ul>
           <li>Brad</li>
           <li>Brodge</li>
           <ReactJSDevs />
           <li>Brandon</li>
         </ul>
       );
     };
```

     **Strings and Numbers:** You can also return string and number type from the render method.

```jsx
     render() {
      return 'Welcome to ReactJS questions';
     }
     // Number
     render() {
      return 2018;
     }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4294)，来源许可：MIT。

<a id="k1c71fed7a407"></a>

## How do you say that props are readonly?

     When you declare a component as a function or a class, it must never modify its own props.

     Let us take a below capital function,

```javascript
     function capital(amount, interest) {
       return amount + interest;
     }
```

     The above function is called “pure” because it does not attempt to change their inputs, and always return the same result for the same inputs. Hence, React has a single rule saying "All React components must act like pure functions with respect to their props."

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4904)，来源许可：MIT。

<a id="k0eac6514f98a"></a>

## How do you set default value for uncontrolled component?

     In React, the value attribute on form elements will override the value in the DOM. With an uncontrolled component, you might want React to specify the initial value, but leave subsequent updates uncontrolled. To handle this case, you can specify a **defaultValue** attribute instead of **value**.

```javascript
     render() {
       return (
         <form onSubmit={this.handleSubmit}>
           <label>
             User Name:
             <input
               defaultValue="John"
               type="text"
               ref={this.input} />
           </label>
           <input type="submit" value="Submit" />
         </form>
       );
     }
```

     The same applies for `select` and `textArea` inputs. But you need to use **defaultChecked** for `checkbox` and `radio` inputs.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5335)，来源许可：MIT。

<a id="k9a785860cac5"></a>

## How do you share state logic between components using custom hooks?

     Custom hooks allow you to **extract and share stateful logic** between components without changing their hierarchy. The state itself is not shared—each component using the hook gets its own isolated state.

     #### Example: useLocalStorage Hook
```jsx
     import { useState, useEffect } from 'react';

     function useLocalStorage(key, initialValue) {
       // Get stored value or use initial value
       const [storedValue, setStoredValue] = useState(() => {
         try {
           const item = window.localStorage.getItem(key);
           return item ? JSON.parse(item) : initialValue;
         } catch (error) {
           console.error(error);
           return initialValue;
         }
       });

       // Update localStorage when state changes
       useEffect(() => {
         try {
           window.localStorage.setItem(key, JSON.stringify(storedValue));
         } catch (error) {
           console.error(error);
         }
       }, [key, storedValue]);

       return [storedValue, setStoredValue];
     }

     // Usage in multiple components
     function ThemeToggle() {
       const [theme, setTheme] = useLocalStorage('theme', 'light');
       return (
         <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
           Current: {theme}
         </button>
       );
     }

     function FontSizeSelector() {
       const [fontSize, setFontSize] = useLocalStorage('fontSize', 16);
       return (
         <input 
           type="range" 
           value={fontSize} 
           onChange={(e) => setFontSize(Number(e.target.value))} 
         />
       );
     }
```

     Both components use `useLocalStorage`, but each has **its own independent state** that persists to localStorage.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L8263)，来源许可：MIT。

<a id="k7870ce4911b9"></a>

## How do you solve performance corner cases while using context?

    The context uses reference identity to determine when to re-render, there are some gotchas that could trigger unintentional renders in consumers when a provider’s parent re-renders.

    For example, the code below will re-render all consumers every time the Provider re-renders because a new object is always created for value.

```javascript
    class App extends React.Component {
      render() {
        return (
          <Provider value={{ something: "something" }}>
            <Toolbar />
          </Provider>
        );
      }
    }
```

    This can be solved by lifting up the value to parent state,

```javascript
    class App extends React.Component {
      constructor(props) {
        super(props);
        this.state = {
          value: { something: "something" },
        };
      }

      render() {
        return (
          <Provider value={this.state.value}>
            <Toolbar />
          </Provider>
        );
      }
    }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12471)，来源许可：MIT。

<a id="kc0dcbac65b41"></a>

## How do you use contextType?

    ContextType is used to consume the context object. The contextType property can be used in two ways,

    1.  **contextType as property of class:**
        The contextType property on a class can be assigned a Context object created by React.createContext(). After that, you can consume the nearest current value of that Context type using this.context in any of the lifecycle methods and render function.

        Lets assign contextType property on MyClass as below,

```javascript
        class MyClass extends React.Component {
          componentDidMount() {
            let value = this.context;
            /* perform a side-effect at mount using the value of MyContext */
          }
          componentDidUpdate() {
            let value = this.context;
            /* ... */
          }
          componentWillUnmount() {
            let value = this.context;
            /* ... */
          }
          render() {
            let value = this.context;
            /* render something based on the value of MyContext */
          }
        }
        MyClass.contextType = MyContext;
```

    2.  **Static field**
        You can use a static class field to initialize your contextType using public class field syntax.

```javascript
        class MyClass extends React.Component {
          static contextType = MyContext;
          render() {
            let value = this.context;
            /* render something based on the value */
          }
        }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12411)，来源许可：MIT。

<a id="kcd219a3d5bf6"></a>

## How Do You Use useRef to Access a DOM Element in React? Give an example.

        The `useRef` hook is commonly used in React to directly reference and interact with DOM elements — like focusing an input, scrolling to a section, or controlling media elements.

        When you assign a ref to a DOM element using useRef, React gives you access to the underlying DOM node via the .current property of the ref object.

        **Example: Focus an input**

```js
        import React, { useRef } from 'react';

        function FocusInput() {
          const inputRef = useRef(null); // create the ref

          const handleFocus = () => {
            inputRef.current.focus(); // access DOM element and focus it
          };

          return (
            <div>
              <input type="text" ref={inputRef} />
              <button onClick={handleFocus}>Focus the input</button>
            </div>
          );
        }
```
       **Note:** The DOM reference is only available **after the component has mounted** — typically accessed in `useEffect` or event handlers.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7691)，来源许可：MIT。
