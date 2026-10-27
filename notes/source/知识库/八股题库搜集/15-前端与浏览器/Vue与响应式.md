# Vue与响应式

<a id="kff70209a1c6f"></a>

## Can useRef be used to store previous values?

        Yes, `useRef` is a common pattern when you want to compare current and previous props or state without causing re-renders.

        **Example: Storing previous state value**
```js
        import { useEffect, useRef, useState } from 'react';

        function PreviousValueExample() {
          const [count, setCount] = useState(0);
          const prevCountRef = useRef();

          useEffect(() => {
            prevCountRef.current = count;
          }, [count]);

          const prevCount = prevCountRef.current;

          return (
            <div>
              <p>Current: {count}</p>
              <p>Previous: {prevCount}</p>
              <button onClick={() => setCount(c => c + 1)}>Increment</button>
            </div>
          );
        }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7737)，来源许可：MIT。

<a id="kcac1f2221d22"></a>

## Can you use useRef to persist values across renders??

        Yes, you can use `useRef` to persist values across renders in React. Unlike `useState`, changing `.current` does not cause re-renders, but the value is preserved across renders.

        **Example:**
```js
        function Timer() {
          const renderCount = useRef(0);
          useEffect(() => {
            renderCount.current++;
            console.log("Render count:", renderCount.current);
          });

          return <div>Check console for render count.</div>;
        }
```
**[⬆ Back to Top](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#table-of-contents)**

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7720)，来源许可：MIT。

<a id="ke79bcd100bb5"></a>

## How to create refs?

There are two approaches

1. This is a recently added approach. _Refs_ are created using `React.createRef()` method and attached to React elements via the `ref` attribute. In order to use _refs_ throughout the component, just assign the _ref_ to the instance property within constructor.

```jsx harmony
   class MyComponent extends React.Component {
     constructor(props) {
       super(props);
       this.myRef = React.createRef();
     }
     render() {
       return <div ref={this.myRef} />;
     }
   }
```

2. You can also use ref callbacks approach regardless of React version. For example, the search bar component's input element is accessed as follows,
```jsx harmony
   class SearchBar extends Component {
     constructor(props) {
       super(props);
       this.txtSearch = null;
       this.state = { term: "" };
       this.setInputSearchRef = (e) => {
         this.txtSearch = e;
       };
     }
     onInputChange(event) {
       this.setState({ term: this.txtSearch.value });
     }
     render() {
       return (
         <input
           value={this.state.term}
           onChange={this.onInputChange.bind(this)}
           ref={this.setInputSearchRef}
         />
       );
     }
   }
```

You can also use _refs_ in function components using **closures**.
**Note**: You can also use inline ref callbacks even though it is not a recommended approach.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10529)，来源许可：MIT。

<a id="kcd4c780f1ed4"></a>

## How to debug forwardRefs in DevTools?

    **React.forwardRef** accepts a render function as parameter and DevTools uses this function to determine what to display for the ref forwarding component.

    For example, If you don't name the render function or not using displayName property then it will appear as ”ForwardRef” in the DevTools,

```javascript
    const WrappedComponent = React.forwardRef((props, ref) => {
      return <LogProps {...props} forwardedRef={ref} />;
    });
```

    But If you name the render function then it will appear as **”ForwardRef(myFunction)”**

```javascript
    const WrappedComponent = React.forwardRef(function myFunction(props, ref) {
      return <LogProps {...props} forwardedRef={ref} />;
    });
```

    As an alternative, You can also set displayName property for forwardRef function,

```javascript
    function logProps(Component) {
      class LogProps extends React.Component {
        // ...
      }

      function forwardRef(props, ref) {
        return <LogProps {...props} forwardedRef={ref} />;
      }

      // Give this component a more helpful display name in DevTools.
      // e.g. "ForwardRef(logProps(MyComponent))"
      const name = Component.displayName || Component.name;
      forwardRef.displayName = `logProps(${name})`;

      return React.forwardRef(forwardRef);
    }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12222)，来源许可：MIT。

<a id="kf827778c94c6"></a>

## Is it possible to access a ref in the render method?

        Yes, you can access a ref in the render method, but what you get from it depends on how you're using the ref and when in the component lifecycle you're rendering.

        For example, when using ref to access a DOM node (e.g., divRef.current), it's not immediately available on the first render.
```js
        const divRef = useRef(null);

        console.log(divRef.current); // ❌ null on initial render
        return <div ref={divRef}>Hello</div>;
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7766)，来源许可：MIT。

<a id="k980c76a5fcc7"></a>

## Is that possible to use useImperativeHandle without forwardRef?

        **No.** `useImperativeHandle` only works when the component is wrapped in `forwardRef`. It's the combination that allows parent components to use a `ref` on a function component.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7862)，来源许可：MIT。

<a id="k25f8cf1d12ea"></a>

## vue2和vue3的响应式有什么区别（defineProperty是属性级响应式，proxy是对象级

**回答：**

Vue 2 通过 `Object.defineProperty` 为被观察对象的现有属性安装 getter/setter，并递归处理嵌套值；数组则重写部分变更方法。它难以自动侦测新增或删除属性，以及直接设置数组下标或 length 等操作，常需 `Vue.set`、`splice` 等方式。

Vue 3 主要用 Proxy 代理对象，通过 get、set、deleteProperty、迭代相关拦截收集和触发依赖，也对 Map/Set 提供适配。它仍按具体 target/key 等信息追踪依赖，因此‘Proxy 是对象级’只说明拦截入口，不代表修改任意属性就无差别更新整棵组件树。

原始值无法直接被 Proxy 代理，ref 用对象的 value 属性封装响应式值。两代框架都需要更新调度；依赖触发不意味着 DOM 已经同步更新，读取更新后的 DOM 通常使用 nextTick。

<a id="jd-damodel-20251211-20260205-p5-q4"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E4%BA%AC%E4%B8%9C%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L655)，来源许可：GPL-3.0。

<a id="k1e8646d15ef6"></a>

## What are forward refs?

_Ref forwarding_ is a feature that lets some components take a _ref_ they receive, and pass it further down to a child.

```jsx harmony
const ButtonElement = React.forwardRef((props, ref) => (
  <button ref={ref} className="CustomButton">
    {props.children}
  </button>
));

// Create ref to the DOM button:
const ref = React.createRef();
<ButtonElement ref={ref}>{"Forward Ref"}</ButtonElement>;
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10578)，来源许可：MIT。

<a id="ke6129e0662d9"></a>

## What are the common usecases of useRef hook?

      Some of the common cases are:
      *   Automatically focus an input when a component mounts.
      *   Scroll to a specific element.
      *   Measure element dimensions (`offsetWidth`, `clientHeight`).
      *   Control video/audio playback.
      *   Integrate with non-React libraries (like D3 or jQuery).

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7779)，来源许可：MIT。

<a id="k393a3cf7cc57"></a>

## What are the preferred and non-preferred array operations for updating the state?

      The below table represent preferred and non-preferred array operations for updating the component state.

      | Action    | Preferred            | Non-preferred              |
      | --------- | -------------------- | -------------------------- |
      | Adding    | concat, [...arr]     | push, unshift              |
      | Removing  | filter, slice        | pop, shift, splice         |
      | Replacing | map                  | splice, arr[i] = someValue |
      | sorting   | copying to new array | reverse, sort              |

      If you use Immer library then you can able to use all array methods without any problem.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6522)，来源许可：MIT。

<a id="k697c66b22917"></a>

## What is the purpose of forward ref in HOCs?

    Refs will not get passed through because ref is not a prop. It is handled differently by React just like **key**. If you add a ref to a HOC, the ref will refer to the outermost container component, not the wrapped component. In this case, you can use Forward Ref API. For example, we can explicitly forward refs to the inner FancyButton component using the React.forwardRef API.

    The below HOC logs all props,

```javascript
    function logProps(Component) {
      class LogProps extends React.Component {
        componentDidUpdate(prevProps) {
          console.log("old props:", prevProps);
          console.log("new props:", this.props);
        }

        render() {
          const { forwardedRef, ...rest } = this.props;

          // Assign the custom prop "forwardedRef" as a ref
          return <Component ref={forwardedRef} {...rest} />;
        }
      }

      return React.forwardRef((props, ref) => {
        return <LogProps {...props} forwardedRef={ref} />;
      });
    }
```

    Let's use this HOC to log all props that get passed to our “fancy button” component,

```javascript
    class FancyButton extends React.Component {
      focus() {
        // ...
      }

      // ...
    }
    export default logProps(FancyButton);
```

    Now let's create a ref and pass it to FancyButton component. In this case, you can set focus to button element.

```javascript
    import FancyButton from "./FancyButton";

    const ref = React.createRef();
    ref.current.focus();
    <FancyButton label="Click Me" handleClick={handleClick} ref={ref} />;
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12512)，来源许可：MIT。

<a id="kb37035a34304"></a>

## What is the use of refs?

The _ref_ is used to return a reference to the element. They _should be avoided_ in most cases, however, they can be useful when you need a direct access to the DOM element or an instance of a component.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10523)，来源许可：MIT。

<a id="kd3b3c81379cc"></a>

## When do you need to use refs?

     There are few use cases to go for refs,

     1. Managing focus, text selection, or media playback.
     2. Triggering imperative animations.
     3. Integrating with third-party DOM libraries.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5237)，来源许可：MIT。

<a id="kd46d83dec677"></a>

## Which is preferred option with in callback refs and findDOMNode()?

It is preferred to use _callback refs_ over `findDOMNode()` API. Because `findDOMNode()` prevents certain improvements in React in the future.

The **legacy** approach of using `findDOMNode`:

```javascript
class MyComponent extends Component {
  componentDidMount() {
    findDOMNode(this).scrollIntoView();
  }

  render() {
    return <div />;
  }
}
```

The recommended approach is:

```javascript
class MyComponent extends Component {
  constructor(props) {
    super(props);
    this.node = createRef();
  }
  componentDidMount() {
    this.node.current.scrollIntoView();
  }

  render() {
    return <div ref={this.node} />;
  }
}
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10596)，来源许可：MIT。

<a id="k401c6d37054f"></a>

## Why are inline ref callbacks or functions not recommended?

    If the ref callback is defined as an inline function, it will get called twice during updates, first with null and then again with the DOM element. This is because a new instance of the function is created with each render, so React needs to clear the old ref and set up the new one.

```jsx
    class UserForm extends Component {
      handleSubmit = () => {
        console.log("Input Value is: ", this.input.value);
      };

      render() {
        return (
          <form onSubmit={this.handleSubmit}>
            <input type="text" ref={(input) => (this.input = input)} /> //
            Access DOM input in handle submit
            <button type="submit">Submit</button>
          </form>
        );
      }
    }
```

    But our expectation is for the ref callback to get called once, when the component mounts. One quick fix is to use the ES7 class property syntax to define the function

```jsx
    class UserForm extends Component {
      handleSubmit = () => {
        console.log("Input Value is: ", this.input.value);
      };

      setSearchInput = (input) => {
        this.input = input;
      };

      render() {
        return (
          <form onSubmit={this.handleSubmit}>
            <input type="text" ref={this.setSearchInput} /> // Access DOM input
            in handle submit
            <button type="submit">Submit</button>
          </form>
        );
      }
    }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11867)，来源许可：MIT。

<a id="ke3a4743c1277"></a>

## Why are String Refs legacy?

If you worked with React before, you might be familiar with an older API where the `ref` attribute is a string, like `ref={'textInput'}`, and the DOM node is accessed as `this.refs.textInput`. We advise against it because _string refs have below issues_, and are considered legacy. String refs were **removed in React v16**.

1. They _force React to keep track of currently executing component_. This is problematic because it makes react module stateful, and thus causes weird errors when react module is duplicated in the bundle.
2. They are _not composable_ — if a library puts a ref on the passed child, the user can't put another ref on it. Callback refs are perfectly composable.
3. They _don't work with static analysis_ like Flow. Flow can't guess the magic that framework does to make the string ref appear on `this.refs`, as well as its type (which could be different). Callback refs are friendlier to static analysis.
4. It doesn't work as most people would expect with the "render callback" pattern (e.g. <DataGrid renderRow={this.renderRow} />)

```jsx harmony
   class MyComponent extends Component {
     renderRow = (index) => {
       // This won't work. Ref will get attached to DataTable rather than MyComponent:
       return <input ref={"input-" + index} />;

       // This would work though! Callback refs are awesome.
       return <input ref={(input) => (this["input-" + index] = input)} />;
     };

     render() {
       return (
         <DataTable data={this.props.data} renderRow={this.renderRow} />
       );
     }
   }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10634)，来源许可：MIT。

<a id="k2f365da4c790"></a>

## 如何理解vue的响应式

**回答：**

响应式的核心是读取时追踪依赖，写入时通知依赖，再由调度器安排重新计算或组件更新。以 Vue 3 为例，effect 运行时读取 `state.count`，Proxy 的 get 记录当前 effect 与该 target/key 的关系；后续 set 检测到有效变化时触发相关 effect。

computed 在依赖变化后失效并按需要重新计算，适合表达派生值；watch/watchEffect 用于副作用，需处理异步请求竞态与清理。修改响应式状态后 DOM 更新通常是批处理，可用 nextTick 等待刷新。

变量解构、使用原始对象绕过代理、错误替换对象身份，都会导致预期外行为。响应式解决更新传播，不自动解决循环依赖、大量深度监听或高频图表重绘的性能问题。

<a id="jd-damodel-20251211-20260205-p5-q15"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E4%BA%AC%E4%B8%9C%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L762)，来源许可：GPL-3.0。

<a id="kdf91d9d79f5c"></a>

## 请简述一�?Vue router 的原理？

Vue router 有两种模式：hash 模式�?history 模式，分别对应了两种原理�?

hash 模式�?

```
hash("#")符号的本来作用是加在 URL 指示网页中的位置，例如：
http://www.example.com/index.html#print

#本身以及它后面的字符称之�?hash 可通过 window.location.hash 属性读取�?
hash 虽然出现�?url 中，但不会被包括�?http 请求中，对服务器端完全无用，因此，改�?hash 不会重新加载页面�?

我们可以�?hash 的改变添加监听事件：
window.addEventListener("hashchange",funcRef,false)

每一次改�?hash，我们都会重新注入对应的组件，就可以来实现前端路�?更新视图但不重新请求页面"的功能了�?
```

history 模式�?

```
从HTML5开始，History interface提供�?个新的方法：pushState(),replaceState()使得我们可以对浏览器历史记录栈进行修改�?

window.history.pushState(stateObject, title, URL)
window.history.replaceState(stateObject, title, URL)

stateObject: 当浏览器跳转到新状态时，触发popState事件，该事件将携带stateObject参数的副�?
title: 所添加记录的标�?
URL: 所添加记录的URL

我们可以为window.history的改变添加监听事件：
window.addEventListener("popstate",funcRef,false)

在监听事件中，重新注入对应的组件，就可以来实现前端路�?更新视图但不重新请求页面"的功能了�?

�?HTML5 实现，单页路由的 url 就不会多出一�?，变得更加美观。但因为没有 # 号，所以当用户刷新页面之类的操作时，浏览器还是会给服务器发送请求，可能会造成404�?

```

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/06-development-tech/frontend/frontend-frameworks.md#L126)，来源许可：GPL-3.0。

<a id="kf547c4eec1cf"></a>

## 请简述一�?vue 响应式数据的原理�?

响应式数据的关键在于：data 如何更新 view，以�?view 如何更新 data�?

1、view 更新 data 可以通过事件监听，比�?input 标签监听 'input' 事件就可以实现了�?

2、�?data 更新 view 的重点是如何知道数据变了。这时候我们就通过`Object.defineProperty()`对属性设置一�?set 函数，当数据改变了就会来触发这个函数，所以我们只要将一些需要更新的方法放在这里面就可以实现 data 更新 view 了�?

Object.defineProperty 的具体用法：

```javascript
Object.defineProperty(obj, prop, descriptor)
obj：要在其上定义属性的对象�?
prop：要定义或修改的属性的名称�?
descriptor：将被定义或修改的属性描述符�?

descriptor 具有以下两种可选值：
get：给属性提�?getter 的方法，如果没有 getter 则为 undefined。当访问该属性时，该方法会被执行，方法执行时没有参数传入，但是会传入 this 对象�?
set：给属性提�?setter 的方法，如果没有 setter 则为 undefined。当属性值修改时，触发执行该方法。该方法将接受唯一参数，即该属性新的参数值�?
```

一个简单的响应式数据的例子�?

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>defineProperty</title>
  </head>
  <body>
    <div id="app">
      <input type="text" id="txt" />
      <p id="show"></p>
    </div>

    <script>
      let obj = {}

      Object.defineProperty(obj, 'txt', {
        get: function () {
          return obj
        },
        set: function (newValue) {
          document.getElementById('txt').value = newValue
          document.getElementById('show').innerHTML = newValue
        },
      })
      document.addEventListener('keyup', function (e) {
        obj.txt = e.target.value
      })
    </script>
  </body>
</html>
```

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/06-development-tech/frontend/frontend-frameworks.md#L66)，来源许可：GPL-3.0。
