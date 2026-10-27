# React与组件状态

<a id="k8a23dacc4e12"></a>

## What are the differences between Functional and Class Components?

     There are two different ways to create components in ReactJS. The main differences are listed down as below,

     ## 1. Syntax:

     The class components uses ES6 classes to create the components. It uses `render` function to display the HTML content in the webpage.

     The syntax for class component looks like as below.

```js
     class App extends React.Component {
       render() {
         return <h1>This is a class component</h1>;
       }
     }
```

     **Note:** The **Pascal Case** is the recommended approach to provide naming to a component.

     Functional component has been improved over the years with some added features like Hooks. Here is a syntax for functional component.

```js
     function App() {
       return (
         <div className="App">
           <h1>Hello, I'm a function component</h1>
         </div>
       );
     }
```

     ## 2. State:

     State contains information or data about a component which may change over time.

     In class component, you can update the state when a user interacts with it or server updates the data using the `setState()` method. The initial state is going to be assigned in the `Constructor()` method using the `this.state` object and it is possible to assign different data types such as string, boolean, numbers, etc.

     **A simple example showing how we use the setState() and constructor():**

```js
     class App extends Component {
       constructor() {
         super();
         this.state = {
           message: "This is a class component",
         };
       }
       updateMessage() {
         this.setState({
           message: "Updating the class component",
         });
       }
       render() {
         return (
           <>
             <h1>{this.state.message}</h1>
             <button
               onClick={() => {
                 this.updateMessage();
               }}>
               Click!!
             </button>
           </>
         );
       }
     }

```

     You didn't use state in functional components because it was only supported in class components. But over the years hooks have been implemented in functional components which enables to use state too.

     The `useState()` hook can used to implement state in functional components. It returns an array with two items: the first item is current state and the next one is a function (setState) that updates the value of the current state.

     Let's see an example to demonstrate the state in functional components,

```js
     function App() {
       const [message, setMessage] = useState("This is a functional component");
       const updateMessage = () => {
         setMessage("Updating the functional component");
       };
       return (
         <div className="App">
           <h1>{message} </h1>
           <button onClick={updateMessage}>Click me!!</button>
         </div>
       );
     }
```

     ## 3. Props:

     Props are referred to as "properties". The props are passed into React component just like arguments passed to a function. In other words, they are similar to HTML attributes.

     The props are accessible in child class component using `this.props` as shown in below example,

```js
     class Child extends React.Component {
       render() {
         return (
           <h1>
             {" "}
             This is a functional component and component name is {
               this.props.name
             }{" "}
           </h1>
         );
       }
     }

     class Parent extends React.Component {
       render() {
         return (
           <div className="Parent">
             <Child name="First child component" />
             <Child name="Second child component" />
           </div>
         );
       }
     }
```

     Props in functional components are similar to that of the class components but the difference is the absence of 'this' keyword.

```js
     function Child(props) {
       return (
         <h1>
           This is a child component and the component name is{props.name}
         </h1>
       );
     }

     function Parent() {
       return (
         <div className="Parent">
           <Child name="First child component" />
           <Child name="Second child component" />
         </div>
       );
     }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5944)，来源许可：MIT。

<a id="k5cf434b549cc"></a>

## What are the differences between Redux and MobX?

     Below are the main differences between Redux and MobX,

     | Topic         | Redux                                                         | MobX                                                                   |
     | ------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------- |
     | Definition    | It is a javascript library for managing the application state | It is a library for reactively managing the state of your applications |
     | Programming   | It is mainly written in ES6                                   | It is written in JavaScript(ES5)                                       |
     | Data Store    | There is only one large store exist for data storage          | There is more than one store for storage                               |
     | Usage         | Mainly used for large and complex applications                | Used for simple applications                                           |
     | Performance   | Need to be improved                                           | Provides better performance                                            |
     | How it stores | Uses JS Object to store                                       | Uses observable to store the data                                      |

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5564)，来源许可：MIT。

<a id="k2f06921dae02"></a>

## What are the differences between redux-saga and redux-thunk?

     Both _Redux Thunk_ and _Redux Saga_ take care of dealing with side effects. In most of the scenarios, Thunk uses _Promises_ to deal with them, whereas Saga uses _Generators_. Thunk is simple to use and Promises are familiar to many developers, Sagas/Generators are more powerful but you will need to learn them. But both middleware can coexist, so you can start with Thunks and introduce Sagas when/if you need them.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3726)，来源许可：MIT。

<a id="k4d095306a1a1"></a>

## What are the differences between useEffect and useEvent (experimental)?

     `useEvent` is an **experimental hook** (not yet stable in React) designed to solve the problem of creating **stable event handlers** that always access the latest props and state without causing re-renders or needing to be in dependency arrays.

     #### The Problem useEvent Solves
```jsx
     // Problem: onTick changes on every render, causing interval to reset
     function Timer({ onTick }) {
       useEffect(() => {
         const id = setInterval(() => {
           onTick(); // Uses stale closure if onTick is not in deps
         }, 1000);
         return () => clearInterval(id);
       }, [onTick]); // Adding onTick causes interval to reset frequently
     }
```

     #### Solution with useEvent (Experimental)
```jsx
     import { useEvent } from 'react'; // Experimental

     function Timer({ onTick }) {
       const stableOnTick = useEvent(onTick);

       useEffect(() => {
         const id = setInterval(() => {
           stableOnTick(); // Always calls latest onTick
         }, 1000);
         return () => clearInterval(id);
       }, []); // No dependency needed!
     }
```

     #### Key Differences

     | Feature | useEffect | useEvent (experimental) |
     |---------|-----------|------------------------|
     | Purpose | Run side effects | Create stable callbacks |
     | Runs | After render | During render (creates function) |
     | Returns | Cleanup function | Stable event handler |
     | Closure | Captures values at render time | Always accesses latest values |
     | Dependencies | Must list all used values | Not needed in other hooks' deps |

     **Note:** Until `useEvent` is stable, you can use `useCallback` with `useRef` as a workaround for stable callbacks.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L8445)，来源许可：MIT。

<a id="k3410e6c3ed8d"></a>

## What are the differences between useEffect and useLayoutEffect hooks?

     useEffect and useLayoutEffect are both React hooks that can be used to synchronize a component with an external system, such as a browser API or a third-party library. However, there are some key differences between the two:

     - Timing: useEffect runs after the browser has finished painting, while useLayoutEffect runs synchronously before the browser paints. This means that useLayoutEffect can be used to measure and update layout in a way that feels more synchronous to the user.

     - Browser Paint: useEffect allows browser to paint the changes before running the effect, hence it may cause some visual flicker. useLayoutEffect synchronously runs the effect before browser paints and hence it will avoid visual flicker.

     - Execution Order: The order in which multiple useEffect hooks are executed is determined by React and may not be predictable. However, the order in which multiple useLayoutEffect hooks are executed is determined by the order in which they were called.

     - Error handling: useEffect has a built-in mechanism for handling errors that occur during the execution of the effect, so that it does not crash the entire application. useLayoutEffect does not have this mechanism, and errors that occur during the execution of the effect will crash the entire application.

     In general, it's recommended to use useEffect as much as possible, because it is more performant and less prone to errors. useLayoutEffect should only be used when you need to measure or update layout, and you can't achieve the same result using useEffect.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5928)，来源许可：MIT。

<a id="k6e726cc992d3"></a>

## What are the different phases of component lifecycle?

The component lifecycle has three distinct lifecycle phases:

1. **Mounting:** The component is ready to mount in the browser DOM. This phase covers initialization from `constructor()`, `getDerivedStateFromProps()`, `render()`, and `componentDidMount()` lifecycle methods.

2. **Updating:** In this phase, the component gets updated in two ways, sending the new props and updating the state either from `setState()` or `forceUpdate()`. This phase covers `getDerivedStateFromProps()`, `shouldComponentUpdate()`, `render()`, `getSnapshotBeforeUpdate()` and `componentDidUpdate()` lifecycle methods.

3. **Unmounting:** In this last phase, the component is not needed and gets unmounted from the browser DOM. This phase includes `componentWillUnmount()` lifecycle method.

It's worth mentioning that React internally has a concept of phases when applying changes to the DOM. They are separated as follows

4. **Render** The component will render without any side effects. This applies to Pure components and in this phase, React can pause, abort, or restart the render.

5. **Pre-commit** Before the component actually applies the changes to the DOM, there is a moment that allows React to read from the DOM through the `getSnapshotBeforeUpdate()`.

6. **Commit** React works with the DOM and executes the final lifecycles respectively `componentDidMount()` for mounting, `componentDidUpdate()` for updating, and `componentWillUnmount()` for unmounting.

React 16.3+ Phases (or an [interactive version](http://projects.wojtekmaj.pl/react-lifecycle-methods-diagram/))

![phases 16.4+](https://raw.githubusercontent.com/sudheerj/reactjs-interview-questions/55b7d491cd74c7b37f9352f3b2420d66e7187951/images/phases16.4.png)

Before React 16.3

![phases 16.2](https://raw.githubusercontent.com/sudheerj/reactjs-interview-questions/55b7d491cd74c7b37f9352f3b2420d66e7187951/images/phases.png)

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10663)，来源许可：MIT。

<a id="kfe40f02d5d27"></a>

## What are the different ways to write mapDispatchToProps()?

     There are a few ways of binding _action creators_ to `dispatch()` in `mapDispatchToProps()`.

     Below are the possible options:

```javascript
     const mapDispatchToProps = (dispatch) => ({
       action: () => dispatch(action()),
     });
```

```javascript
     const mapDispatchToProps = (dispatch) => ({
       action: bindActionCreators(action, dispatch),
     });
```

```javascript
     const mapDispatchToProps = { action };
```

     The third option is just a shorthand for the first one.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3618)，来源许可：MIT。

<a id="kc13e8c4e463b"></a>

## What are the downsides of Redux compared to Flux?

     While Redux offers a powerful and predictable state management solution, it comes with a few trade-offs when compared to Flux. These include:

     1.  **Immutability is essential**  
        Redux enforces a strict immutability model for state updates, which differs from Flux’s more relaxed approach. This means you must avoid mutating state directly. Many Redux-related libraries assume immutability, so your team must be disciplined in writing pure update logic. You can use tools like `redux-immutable-state-invariant`, `Immer`, or `Immutable.js` to help enforce this practice, especially during development.
     2.  **Careful selection of complementary packages**  
        Redux is more minimal by design and provides extension points such as middleware and store enhancers. This has led to a large ecosystem, but it also means you must thoughtfully choose and configure additional packages for features like undo/redo, persistence, or form handling—something Flux explicitly leaves out but may be simpler to manage in smaller setups.
     3.  **Limited static type integration**  
        While Flux has mature support for static type checking with tools like Flow, Redux’s type integration is less seamless. Although TypeScript is commonly used with Redux now, early Flow support was limited, and more boilerplate was required for static type safety. This may affect teams that rely heavily on type systems for large codebases.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3326)，来源许可：MIT。

<a id="kd4e0348c28dc"></a>

## What are the exceptions on React component naming?

The component names should start with an uppercase letter but there are few exceptions to this convention. The lowercase tag names with a dot (property accessors) are still considered as valid component names.
For example, the below tag can be compiled to a valid component,

```jsx harmony
     render() {
          return (
            <obj.component/> // `React.createElement(obj.component)`
          )
    }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2614)，来源许可：MIT。

<a id="ke2d5c2a318d0"></a>

## What are the features of create react app?

    Below are the list of some of the features provided by create react app.

    1.  React, JSX, ES6, Typescript and Flow syntax support.
    2.  Autoprefixed CSS
    3.  CSS Reset/Normalize
    4.  A live development server
    5.  A fast interactive unit test runner with built-in support for coverage reporting
    6.  A build script to bundle JS, CSS, and images for production, with hashes and sourcemaps
    7.  An offline-first service worker and a web app manifest, meeting all the Progressive Web App criteria.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12665)，来源许可：MIT。

<a id="k347fc4c90697"></a>

## What are the features of Redux DevTools?

     Some of the main features of Redux DevTools are below,

     1. Lets you inspect every state and action payload.
     2. Lets you go back in time by _cancelling_ actions.
     3. If you change the reducer code, each _staged_ action will be re-evaluated.
     4. If the reducers throw, you will see during which action this happened, and what the error was.
     5. With `persistState()` store enhancer, you can persist debug sessions across page reloads.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3738)，来源许可：MIT。

<a id="k3afc35317240"></a>

## What are the key features introduced in React 18?

     React 18, released in March 2022, introduced several groundbreaking features focused on performance and user experience:

     #### 1. **Automatic Batching**
     Batch multiple state updates together (even in async code) to reduce re-renders.
```jsx
     // Before React 18: Only batched in event handlers
     // After React 18: Batched everywhere
     setTimeout(() => {
       setCount(c => c + 1);
       setFlag(f => !f);
       // Only 1 re-render in React 18!
     }, 1000);
```

     #### 2. **Concurrent Features**
     - **useTransition**: Mark updates as non-urgent
     - **useDeferredValue**: Defer expensive re-renders
     - **Suspense on Server**: SSR with Suspense support

     #### 3. **New createRoot API**
```jsx
     // Old way (React 17)
     ReactDOM.render(<App />, document.getElementById('root'));

     // New way (React 18)
     import { createRoot } from 'react-dom/client';
     const root = createRoot(document.getElementById('root'));
     root.render(<App />);
```

     #### 4. **Streaming SSR with Suspense**
     Stream HTML from server and hydrate components as they arrive.

     #### 5. **New Hooks**
     - `useId`: Generate unique IDs for accessibility
     - `useSyncExternalStore`: Subscribe to external stores
     - `useInsertionEffect`: For CSS-in-JS libraries

     #### 6. **Strict Mode Improvements**
     Double-invokes effects in development to catch bugs.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L8575)，来源许可：MIT。

<a id="ka184bdbd5587"></a>

## What are the key features introduced in React 19?

     React 19 (released 2024) brings major improvements for full-stack React applications:

     #### 1. **React Compiler (formerly React Forget)**
     Automatic memoization - no more manual `useMemo`, `useCallback`, or `React.memo` needed!
```jsx
     // Before: Manual optimization
     const memoizedValue = useMemo(() => expensiveCalc(a, b), [a, b]);

     // React 19: Compiler does it automatically
     const value = expensiveCalc(a, b); // Automatically optimized!
```

     #### 2. **Server Actions**
     Call server functions directly from components:
```jsx
     async function createPost(formData) {
       'use server'
       const post = await db.posts.create({
         title: formData.get('title')
       });
       revalidatePath('/posts');
       return post;
     }

     function NewPost() {
       return (
         <form action={createPost}>
           <input name="title" />
           <button type="submit">Create</button>
         </form>
       );
     }
```

     #### 3. **Actions & Form Actions**
     Automatic handling of pending states, errors, and optimistic updates:
```jsx
     function Form() {
       const [state, formAction] = useFormState(serverAction, initialState);
       const { pending } = useFormStatus();

       return (
         <form action={formAction}>
           <input disabled={pending} />
           <button disabled={pending}>
             {pending ? 'Submitting...' : 'Submit'}
           </button>
         </form>
       );
     }
```

     #### 4. **use() Hook**
     Read resources (Promises, Context) inside render:
```jsx
     function User({ userPromise }) {
       const user = use(userPromise); // Suspends until resolved
       return <div>{user.name}</div>;
     }
```

     #### 5. **useOptimistic Hook**
     Implement optimistic UI updates:
```jsx
     function TodoList({ todos }) {
       const [optimisticTodos, addOptimisticTodo] = useOptimistic(
         todos,
         (state, newTodo) => [...state, { ...newTodo, pending: true }]
       );

       async function createTodo(title) {
         addOptimisticTodo({ id: Date.now(), title });
         await saveTodo(title);
       }

       return optimisticTodos.map(todo => (
         <Todo key={todo.id} {...todo} />
       ));
     }
```

     #### 6. **Document Metadata**
     Built-in support for `<title>`, `<meta>`, etc.:
```jsx
     function BlogPost({ post }) {
       return (
         <>
           <title>{post.title}</title>
           <meta name="description" content={post.excerpt} />
           <article>{post.content}</article>
         </>
       );
     }
```

     #### 7. **Asset Loading APIs**
     Preload resources for better performance:
```jsx
     import { preload, preinit } from 'react-dom';

     preload('/font.woff2', { as: 'font' });
     preinit('/script.js', { as: 'script' });
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L8620)，来源许可：MIT。

<a id="kf6b9cf49d282"></a>

## What are the lifecycle methods going to be deprecated in React v16?

**⚠️ FULLY DEPRECATED:** These lifecycle methods have been deprecated and removed from React 17+.

The following lifecycle methods were deprecated due to unsafe coding practices and problems with async rendering:

1. `componentWillMount()` - **REMOVED in React 17**
2. `componentWillReceiveProps()` - **REMOVED in React 17**
3. `componentWillUpdate()` - **REMOVED in React 17**

**Timeline:**
- React 16.3: Methods aliased with `UNSAFE_` prefix
- React 17+: Unprefixed versions completely removed
- Current (React 18/19): Only `UNSAFE_` versions exist (not recommended)

**Modern Alternatives:**

| Deprecated Method | Modern Replacement |
|---|---|
| `componentWillMount()` | `constructor()` or `componentDidMount()` |
| `componentWillReceiveProps()` | `static getDerivedStateFromProps()` or `componentDidUpdate()` |
| `componentWillUpdate()` | `getSnapshotBeforeUpdate()` + `componentDidUpdate()` |

**Best Practice:** Use functional components with hooks instead:
- `useEffect()` for side effects
- `useState()` for state management
- `useMemo()`/`useCallback()` for optimization

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11085)，来源许可：MIT。

<a id="ke00ca1f59fb1"></a>

## What are the lifecycle methods of React?

Before React 16.3

- **componentWillMount:** Executed before rendering and is used for App level configuration in your root component.
- **componentDidMount:** Executed after first rendering and here all AJAX requests, DOM or state updates, and set up event listeners should occur.
- **componentWillReceiveProps:** Executed when particular prop updates to trigger state transitions.
- **shouldComponentUpdate:** Determines if the component will be updated or not. By default it returns `true`. If you are sure that the component doesn't need to render after state or props are updated, you can return false value. It is a great place to improve performance as it allows you to prevent a re-render if component receives new prop.
- **componentWillUpdate:** Executed before re-rendering the component when there are props & state changes confirmed by `shouldComponentUpdate()` which returns true.
- **componentDidUpdate:** Mostly it is used to update the DOM in response to prop or state changes.
- **componentWillUnmount:** It will be used to cancel any outgoing network requests, or remove all event listeners associated with the component.

React 16.3+

- **getDerivedStateFromProps:** Invoked right before calling `render()` and is invoked on _every_ render. This exists for rare use cases where you need a derived state. Worth reading [if you need derived state](https://reactjs.org/blog/2018/06/07/you-probably-dont-need-derived-state.html).
- **componentDidMount:** Executed after first rendering and where all AJAX requests, DOM or state updates, and set up event listeners should occur.
- **shouldComponentUpdate:** Determines if the component will be updated or not. By default, it returns `true`. If you are sure that the component doesn't need to render after the state or props are updated, you can return a false value. It is a great place to improve performance as it allows you to prevent a re-render if component receives a new prop.
- **getSnapshotBeforeUpdate:** Executed right before rendered output is committed to the DOM. Any value returned by this will be passed into `componentDidUpdate()`. This is useful to capture information from the DOM i.e. scroll position.
- **componentDidUpdate:** Mostly it is used to update the DOM in response to prop or state changes. This will not fire if `shouldComponentUpdate()` returns `false`.
- **componentWillUnmount** It will be used to cancel any outgoing network requests, or remove all event listeners associated with the component.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10691)，来源许可：MIT。

<a id="k1d7decf72007"></a>

## What are the limitations of React?

Apart from the advantages, there are few limitations of React too,

1. React is just a view library, not a full framework.
2. There is a learning curve for beginners who are new to web development.
3. Integrating React into a traditional MVC framework requires some additional configuration.
4. The code complexity increases with inline templating and JSX.
5. Too many smaller components leading to over engineering or boilerplate.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1854)，来源许可：MIT。

<a id="kb6958642b26f"></a>

## What are the main features of React Intl?

    Below are the main features of React Intl,

    1.  Display numbers with separators.
    2.  Display dates and times correctly.
    3.  Display dates relative to "now".
    4.  Pluralize labels in strings.
    5.  Support for 150+ languages.
    6.  Runs in the browser and Node.
    7.  Built on standards.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3022)，来源许可：MIT。

<a id="kf0c4f9477dae"></a>

## What are the main features of Redux Form?

     Some of the main features of Redux Form are:

     1. Field values persistence via Redux store.
     2. Validation (sync/async) and submission.
     3. Formatting, parsing and normalization of field values.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3773)，来源许可：MIT。

<a id="k4e14292e62d0"></a>

## What are the major features of React?

React offers a powerful set of features that have made it one of the most popular JavaScript libraries for building user interfaces:

**Core Features:**

- **Component-Based Architecture**: React applications are built using components - independent, reusable pieces of code that return HTML via a render function. This modular approach enables better code organization, reusability, and maintenance.

- **Virtual DOM**: React creates an in-memory data structure cache, computes the resulting differences, and efficiently updates only the changed parts in the browser DOM. This approach significantly improves performance compared to direct DOM manipulation.

- **JSX (JavaScript XML)**: A syntax extension that allows writing HTML-like code in JavaScript. JSX makes the code more readable and expressive while providing the full power of JavaScript.

- **Unidirectional Data Flow**: React follows a one-way data binding model where data flows from parent to child components. This makes the code more predictable and easier to debug.

- **Declarative UI**: React allows you to describe what your UI should look like for a given state, and it handles the DOM updates when the underlying data changes.

**Advanced Features:**

- **React Hooks**: Introduced in React 16.8, hooks allow using state and other React features in functional components without writing classes.

- **Context API**: Provides a way to share values between components without explicitly passing props through every level of the component tree.

- **Error Boundaries**: Components that catch JavaScript errors anywhere in their child component tree and display fallback UI instead of crashing.

- **Server-Side Rendering (SSR)**: Enables rendering React components on the server before sending HTML to the client, improving performance and SEO.

- **Concurrent Mode**: A set of new features (in development) that help React apps stay responsive and gracefully adjust to the user's device capabilities and network speed.

- **React Server Components**: A new feature that allows components to be rendered entirely on the server, reducing bundle size and improving performance.

- **Suspense**: A feature that lets your components "wait" for something before rendering, supporting code-splitting and data fetching with cleaner code.

These features collectively make React powerful for building everything from small widgets to complex, large-scale web applications.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L580)，来源许可：MIT。

<a id="kd7ac613e2df4"></a>

## What are the Pointer Events supported in React?

_Pointer Events_ provide a unified way of handling all input events. In the old days we had a mouse and respective event listeners to handle them but nowadays we have many devices which don't correlate to having a mouse, like phones with touch surface or pens. We need to remember that these events will only work in browsers that support the _Pointer Events_ specification.

The following event types are now available in _React DOM_:

1. `onPointerDown`
2. `onPointerMove`
3. `onPointerUp`
4. `onPointerCancel`
5. `onGotPointerCapture`
6. `onLostPointerCapture`
7. `onPointerEnter`
8. `onPointerLeave`
9. `onPointerOver`
10. `onPointerOut`

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2145)，来源许可：MIT。

<a id="k0c06f257c359"></a>

## What are the popular React-specific linters?

    ESLint is a popular JavaScript linter. There are plugins available that analyse specific code styles. One of the most common for React is an npm package called `eslint-plugin-react`. By default, it will check a number of best practices, with rules checking things from keys in iterators to a complete set of prop types.

    Another popular plugin is `eslint-plugin-jsx-a11y`, which will help fix common issues with accessibility. As JSX offers slightly different syntax to regular HTML, issues with `alt` text and `tabindex`, for example, will not be picked up by regular plugins.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2741)，来源许可：MIT。

<a id="k240c31686a79"></a>

## What are the problems of using render props with pure components?

     If you create a function inside a render method, it negates the purpose of pure component. Because the shallow prop comparison will always return false for new props, and each render in this case will generate a new value for the render prop. You can solve this issue by defining the render function as instance method.

```javascript
     class Mouse extends React.PureComponent {
       render() {
         // BAD: a new arrow function reference is created on every render,
         // so PureComponent's shallow comparison always sees "new" props
         return <MouseTracker render={(mouse) => <Cat mouse={mouse} />} />;
       }
     }
```

```javascript
     class MouseWithCat extends React.PureComponent {
       // GOOD: defined once as an instance method/class property, so the
       // reference stays stable across renders
       renderTheCat = (mouse) => <Cat mouse={mouse} />;

       render() {
         return <MouseTracker render={this.renderTheCat} />;
       }
     }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5283)，来源许可：MIT。

<a id="k87d57f9a96ab"></a>

## What are the rules of JSX?

     The below 3 rules needs to be followed while using JSX in a react application.

     1. **Return a single root element**:
        If you are returning multiple elements from a component, wrap them in a single parent element. Otherwise you will receive the below error in your browser console.

        `html Adjacent JSX elements must be wrapped in an enclosing tag.`

     2. **All the tags needs to be closed:**
        Unlike HTML, all tags needs to closed explicitly with in JSX. This rule applies for self-closing tags(like hr, br and img tags) as well.
     3. **Use camelCase naming:**
        It is suggested to use camelCase naming for attributes in JSX. For example, the common attributes of HTML elements such as `class`, `tabindex` will be used as `className` and `tabIndex`.  
        **Note:** There is an exception for `aria-*` and `data-*` attributes which should be lower cased all the time.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6163)，来源许可：MIT。

<a id="k9fe290e11649"></a>

## What are the sources used for introducing hooks?

     Hooks got the ideas from several different sources. Below are some of them,

     1. Previous experiments with functional APIs in the react-future repository
     2. Community experiments with render prop APIs such as Reactions Component
     3. State variables and state cells in DisplayScript.
     4. Subscriptions in Rx.
     5. Reducer components in ReasonReact.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5513)，来源许可：MIT。

<a id="ke6d464ca6dac"></a>

## What are the two ways of formatting in React Intl?

    The library provides two ways to format strings, numbers, and dates:

    1.  **Using react components:**

```jsx harmony
        <FormattedMessage
          id={"account"}
          defaultMessage={"The amount is less than minimum balance."}
        />
```

    2.  **Using an API:**

```javascript
        const messages = defineMessages({
          accountMessage: {
            id: "account",
            defaultMessage: "The amount is less than minimum balance.",
          },
        });

        formatMessage(messages.accountMessage);
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3036)，来源许可：MIT。

<a id="k92ecbe319ef9"></a>

## What are the use cases of useContext hook?

     The `useContext` hook in React is used to share data across components without having to pass props manually through each level. Here are some common and effective use cases:

        1.  **Theme Customization**  
            `useContext` can be used to manage application-wide themes, such as light and dark modes, ensuring consistent styling and enabling user-driven customization.
        2.  **Localization and Internationalization**  
            It supports localization by providing translated strings or locale-specific content to components, adapting the application for users in different regions.
        3.  **User Authentication and Session Management**  
            `useContext` allows global access to authentication status and user data. This enables conditional rendering of components and helps manage protected routes or user-specific UI elements.
        4.  **Shared Modal or Sidebar Visibility**  
            It's ideal for managing the visibility of shared UI components like modals, drawers, or sidebars, especially when their state needs to be controlled from various parts of the app.
        5.  **Combining with** `**useReducer**` **for Global State Management**  
            When combined with `useReducer`, `useContext` becomes a powerful tool for managing more complex global state logic. This pattern helps maintain cleaner, scalable state logic without introducing external libraries like Redux.
             Some of the common use cases of useContext are listed below,

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6688)，来源许可：MIT。

<a id="kf88ed4e7a2b0"></a>

## What are typical middleware choices for handling asynchronous calls in Redux?

     Some of the popular middleware choices for handling asynchronous calls in Redux eco system are `Redux Thunk, Redux Promise, Redux Saga`.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5540)，来源许可：MIT。

<a id="kbad528d4e514"></a>

## What are uncontrolled components?

    The **Uncontrolled components** are form elements (like `<input>`, `<textarea>`, or `<select>`) that **manage their own state internally** via the **DOM**, rather than through React state.
    You can query the DOM using a `ref` to find its current value when you need it. This is a bit more like traditional HTML.

    The uncontrolled components will be implemented using the below steps,

    1. Create a ref using `useRef` react hook in function component or `React.createRef()` in class based component.
    2. Attach this `ref` to the form element.
    3. The form element value can be accessed directly through `ref` in event handlers or `componentDidMount` for class components

    In the below UserProfile component, the `username` input is accessed using ref.

```jsx harmony
    import React, { useRef } from "react";

    function UserProfile() {
      const usernameRef = useRef(null);

      const handleSubmit = (event) => {
        event.preventDefault();
        console.log("The submitted username is: " + usernameRef.current.value);
      };

      return (
        <form onSubmit={handleSubmit}>
          <label>
            Username:
            <input type="text" ref={usernameRef} />
          </label>
          <button type="submit">Submit</button>
        </form>
      );
    }
```
    **Note:** Here, DOM is in charge of the value. React only accesses the value when needed (via `ref`).

    **Benefits:**
     *   **Less boilerplate** — no need for `useState` and `onChange`.
     *   Useful for **quick form setups** or when integrating with **non-React code**.
     *   Slightly better **performance** in very large forms (fewer re-renders).

    In most cases, it's recommend to use controlled components to implement forms. In a controlled component, form data is handled by a React component. The alternative is uncontrolled components, where form data is handled by the DOM itself.

    <details><summary><b>See Class</b></summary>
    <p>

```jsx harmony
    class UserProfile extends React.Component {
      constructor(props) {
        super(props);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.input = React.createRef();
      }

      handleSubmit(event) {
        alert("A name was submitted: " + this.input.current.value);
        event.preventDefault();
      }

      render() {
        return (
          <form onSubmit={this.handleSubmit}>
            <label>
              {"Name:"}
              <input type="text" ref={this.input} />
            </label>
            <input type="submit" value="Submit" />
          </form>
        );
      }
    }
```

    </p>
    </details>

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1275)，来源许可：MIT。

<a id="k20a44924c5cd"></a>

## What are useFormState and useFormStatus hooks?

     These hooks simplify form handling with Server Actions in React 19.

     #### useFormState
     Manages form state and handles server responses:
```jsx
     'use client'
     import { useFormState } from 'react-dom';
     import { loginAction } from './actions';

     export default function LoginForm() {
       const [state, formAction] = useFormState(loginAction, {
         errors: {},
         message: ''
       });

       return (
         <form action={formAction}>
           <input name="email" type="email" />
           {state.errors.email && <p>{state.errors.email}</p>}

           <input name="password" type="password" />
           {state.errors.password && <p>{state.errors.password}</p>}

           <button type="submit">Login</button>
           {state.message && <p>{state.message}</p>}
         </form>
       );
     }
```

     #### useFormStatus
     Get the pending state of parent form:
```jsx
     'use client'
     import { useFormStatus } from 'react-dom';

     function SubmitButton() {
       const { pending, data, method, action } = useFormStatus();

       return (
         <button type="submit" disabled={pending}>
           {pending ? 'Submitting...' : 'Submit'}
         </button>
       );
     }

     // Must be used in a child component of <form>
     export default function MyForm() {
       return (
         <form action={serverAction}>
           <input name="email" />
           <SubmitButton />
         </form>
       );
     }
```

     #### Combining Both
```jsx
     'use client'
     import { useFormState, useFormStatus } from 'react-dom';

     function SubmitButton() {
       const { pending } = useFormStatus();
       return (
         <button disabled={pending}>
           {pending ? '⏳ Saving...' : '💾 Save'}
         </button>
       );
     }

     export default function EditProfile() {
       const [state, formAction] = useFormState(updateProfile, null);

       return (
         <form action={formAction}>
           <input name="name" defaultValue={user.name} />
           <input name="bio" defaultValue={user.bio} />
           <SubmitButton />
           {state?.success && <p>✅ Profile updated!</p>}
           {state?.error && <p>❌ {state.error}</p>}
         </form>
       );
     }
```

     #### Key Points
     - `useFormState`: For managing server responses and errors
     - `useFormStatus`: For UI feedback during submission
     - `useFormStatus` must be used in a child component of the form
     - Works seamlessly with Server Actions

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L8867)，来源许可：MIT。

<a id="ke965ea8f08f6"></a>

## What happens if you call useState conditionally?

     As per rules of React Hooks, hooks must be called unconditionally. For example, if you conditionally call it:
```js
     if (someCondition) { 
        const [state, setState] = useState(0); 
     }
```

     React will throw a runtime error because it **relies on the order of Hook calls**, and conditional logic breaks that order.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6927)，来源许可：MIT。

<a id="k2f41b12a7aaf"></a>

## What happens if you return a Promise from useEffect??

      You should NOT return a Promise from useEffect. React expects the function passed to useEffect to return either nothing (undefined) or a cleanup function (synchronous function). i.e, It does not expect or handle a returned Promise. If you still return a Promise, React will ignore it silently, and it may lead to bugs or warnings in strict mode.

      **Incorrect:**
```js
      useEffect(async () => {
        await fetchData(); // ❌ useEffect shouldn't be async
      }, []);
```
      **Correct:**
```jsx
      useEffect(() => {
        const fetchData = async () => {
          const res = await fetch('/api');
          const data = await res.json();
          setData(data);
        };

        fetchData();
      }, []);
```
**[⬆ Back to Top](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#table-of-contents)**

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7560)，来源许可：MIT。

<a id="kbd42135e0b79"></a>

## What is a switching component?

A _switching component_ is a component that renders one of many components. We need to use object to map prop values to components.

For example, a switching component to display different pages based on `page` prop:

```jsx harmony
import HomePage from "./HomePage";
import AboutPage from "./AboutPage";
import ServicesPage from "./ServicesPage";
import ContactPage from "./ContactPage";

const PAGES = {
  home: HomePage,
  about: AboutPage,
  services: ServicesPage,
  contact: ContactPage,
};

const Page = (props) => {
  const Handler = PAGES[props.page] || ContactPage;

  return <Handler {...props} />;
};

// The keys of the PAGES object can be used in the prop types to catch dev-time errors.
Page.propTypes = {
  page: PropTypes.oneOf(Object.keys(PAGES)).isRequired,
};
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2112)，来源许可：MIT。

<a id="k6526e22bb481"></a>

## What is a wrapper component?

     A wrapper in React is a component that wraps or surrounds another component or group of components. It can be used for a variety of purposes such as adding additional functionality, styling, or layout to the wrapped components.

     For example, consider a simple component that displays a message:

```javascript
     const Message = ({ text }) => {
       return <p>{text}</p>;
     };
```

     We can create a wrapper component that will add a border to the message component:

```javascript
     const MessageWrapper = (props) => {
       return (
         <div style={{ border: "1px solid black" }}>
           <Message {...props} />
         </div>
       );
     };
```

     Now we can use the MessageWrapper component instead of the Message component and the message will be displayed with a border:

```javascript
     <MessageWrapper text="Hello World" />
```

     Wrapper component can also accept its own props and pass them down to the wrapped component, for example, we can create a wrapper component that will add a title to the message component:

```javascript
     const MessageWrapperWithTitle = ({ title, ...props }) => {
       return (
         <div>
           <h3>{title}</h3>
           <Message {...props} />
         </div>
       );
     };
```

     Now we can use the MessageWrapperWithTitle component and pass title props:

```javascript
     <MessageWrapperWithTitle title="My Message" text="Hello World" />
```

     This way, the wrapper component can add additional functionality, styling, or layout to the wrapped component while keeping the wrapped component simple and reusable.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5875)，来源许可：MIT。

<a id="kf24772756358"></a>

## What is an action in Redux?

     _Actions_ are plain JavaScript objects or payloads of information that send data from your application to your store. They are the only source of information for the store. Actions must have a type property that indicates the type of action being performed.

     For example, let's take an action which represents adding a new todo item:

```
     {
       type: ADD_TODO,
       text: 'Add todo item'
     }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3822)，来源许可：MIT。

<a id="k93cefb4bd397"></a>

## What is context?

_Context_ provides a way to pass data through the component tree without having to pass props down manually at every level.

For example, authenticated users, locale preferences, UI themes need to be accessed in the application by many components.

```javascript
const { Provider, Consumer } = React.createContext(defaultValue);
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10737)，来源许可：MIT。

<a id="k115f79e8217b"></a>

## What is JSX?

_JSX_ stands for _JavaScript XML_ and it is an XML-like syntax extension to ECMAScript. Basically it just provides the syntactic sugar for the `React.createElement(type, props, ...children)` function, giving us expressiveness of JavaScript along with HTML like template syntax.

In the example below, the text inside `<h1>` tag is returned as JavaScript function to the render function.

```jsx harmony
export default function App() {
  return <h1 className="greeting">{"Hello, this is a JSX Code!"}</h1>;
}
```

If you don't use JSX syntax then the respective JavaScript code should be written as below,

```javascript
import { createElement } from "react";

export default function App() {
  return createElement(
    "h1",
    { className: "greeting" },
    "Hello, this is a JSX Code!"
  );
}
```

 See Class
 <p>

```jsx harmony
class App extends React.Component {
  render() {
    return <h1 className="greeting">{"Hello, this is a JSX Code!"}</h1>;
  }
}
```

 </p>

**Note:** JSX is stricter than HTML

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L616)，来源许可：MIT。

<a id="k1a5a47647fec"></a>

## What is Lifting State Up in React?

When several components need to share the same changing data then it is recommended to _lift the shared state up_ to their closest common ancestor. That means if two child components share the same data from its parent, then move the state to parent instead of maintaining local state in both of the child components.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1381)，来源许可：MIT。

<a id="k9f76e852c284"></a>

## What is normalized Redux state?

     **Normalized state** stores data the way a relational database would: each type of entity is kept in a lookup table keyed by ID, instead of being nested/duplicated inside arrays. Redux Toolkit's `createEntityAdapter` generates this shape for you.

```javascript
     // Un-normalized — posts are duplicated wherever they appear
     {
       posts: [
         { id: 1, title: "Post 1", author: { id: 1, name: "Sudheer" } },
         { id: 2, title: "Post 2", author: { id: 1, name: "Sudheer" } },
       ];
     }

     // Normalized — each entity stored once, referenced by id
     {
       posts: {
         ids: [1, 2],
         entities: {
           1: { id: 1, title: "Post 1", authorId: 1 },
           2: { id: 2, title: "Post 2", authorId: 1 },
         },
       },
       users: {
         ids: [1],
         entities: { 1: { id: 1, name: "Sudheer" } },
       },
     }
```

```javascript
     import { createEntityAdapter, createSlice } from "@reduxjs/toolkit";

     const postsAdapter = createEntityAdapter();

     const postsSlice = createSlice({
       name: "posts",
       initialState: postsAdapter.getInitialState(),
       reducers: {
         postAdded: postsAdapter.addOne,
         postUpdated: postsAdapter.updateOne,
       },
     });
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L9702)，来源许可：MIT。

<a id="k7b897f02b2a0"></a>

## What is React Dev Tools?

     _React Developer Tools_ let you inspect the component hierarchy, including component props and state. It exists both as a browser extension (for Chrome and Firefox), and as a standalone app (works with other environments including Safari, IE, and React Native).

     The official extensions available for different browsers or environments.

     1. **Chrome extension**
     2. **Firefox extension**
     3. **Standalone app** (Safari, React Native, etc)

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3928)，来源许可：MIT。

<a id="k70ee5b843396"></a>

## What is React Fiber?

**React Fiber** is the **new reconciliation engine** in React, introduced in React 16. It’s a complete rewrite of React’s core algorithm(old stack-based algorithm) for rendering and updating the UI. Fiber enhances React’s ability to handle **asynchronous rendering**, **prioritized updates**(assign priority to different types of updates), and **interruption**(ability to pause, abort, or reuse work) of rendering work, enabling smoother and more responsive user interfaces.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1208)，来源许可：MIT。

<a id="k5462ae0708b6"></a>

## What is React hydration?

      React hydration is used to add client-side JavaScript interactivity to pre-rendered static HTML generated by the server. It is used only for server-side rendering(SSR) to enhance the initial rendering time and make it SEO friendly application. This hydration acts as a bridge to reduce the gap between server side and client-side rendering.

      After the page loaded with generated static HTML, React will add application state and interactivity by attaching all event handlers for the respective elements. Let's demonstrate this with an example.

      Consider that React DOM API(using `renderToString`) generated HTML for `<App>` component which contains `<button>` element to increment the counter.

```jsx
      import {useState} from 'react';
      import { renderToString } from 'react-dom/server';

      export default function App() {
        const [count, setCount] = React.useState(0);

        return (
          <h1>Counter</h1>
          <button onClick={() => setCount(prevCount => prevCount + 1)}>
            {count} times
          </button>
          );
      }

      const html = renderToString(<App />);
```

      The above code generates the below HTML with a header text and button component without any interactivity.

```html
      <h1>Counter</h1>
      <button>
        <!-- -->0<!-- -->
        times
      </button>
```

      At this stage `hydrateRoot` API can be used to perform hydration by attaching `onClick` event handler.

```jsx
      import { hydrateRoot } from "react-dom/client";
      import App from "./App.js";

      hydrateRoot(document.getElementById("root"), <App />);
```

      After this step, you are able to run React application on server-side and hydrating the javascript bundle on client-side for smooth user experience and SEO purposes.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6298)，来源许可：MIT。

<a id="kd720dd0f97d6"></a>

## What is React Intl?

    The _React Intl_ library makes internationalization in React straightforward, with off-the-shelf components and an API that can handle everything from formatting strings, dates, and numbers, to pluralization. React Intl is part of _FormatJS_ which provides bindings to React via its components and API.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3016)，来源许可：MIT。

<a id="kbd17aec1d429"></a>

## What is React lazy function?

     The `React.lazy` function lets you render a dynamic import as a regular component. It will automatically load the bundle containing the `OtherComponent` when the component gets rendered. This must return a Promise which resolves to a module with a default export containing a React component.

```jsx
     const OtherComponent = React.lazy(() => import("./OtherComponent"));

     function MyComponent() {
       return (
         <div>
           <OtherComponent />
         </div>
       );
     }
```

     **Note:**
     `React.lazy` and `Suspense` is not yet available for server-side rendering. If you want to do code-splitting in a server rendered app, we still recommend React Loadable.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4252)，来源许可：MIT。

<a id="k1bedd0a41525"></a>

## What is React memo function?

     Class components can be restricted from re-rendering when their input props are the same using **PureComponent or shouldComponentUpdate**. Now you can do the same with function components by wrapping them in **React.memo**.

```jsx
     const MyComponent = React.memo(function MyComponent(props) {
       /* only rerenders if props change */
     });
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4240)，来源许可：MIT。

<a id="k3429709f80e0"></a>

## What is React proptype array with shape?

If you want to pass an array of objects to a component with a particular shape then use `React.PropTypes.shape()` as an argument to `React.PropTypes.arrayOf()`.

```javascript
ReactComponent.propTypes = {
  arrayWithShape: React.PropTypes.arrayOf(
    React.PropTypes.shape({
      color: React.PropTypes.string.isRequired,
      fontSize: React.PropTypes.number.isRequired,
    })
  ).isRequired,
};
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2272)，来源许可：MIT。

<a id="kff1f2b56c915"></a>

## What is React Router?

    React Router is a powerful routing library built on top of React that helps you add new screens and flows to your application incredibly quickly, all while keeping the URL in sync with what's being displayed on the page.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2753)，来源许可：MIT。

<a id="k6391afdf8bcb"></a>

## What is react scripts?

    The `react-scripts` package is a set of scripts from the create-react-app starter pack which helps you kick off projects without configuring. The `react-scripts start` command sets up the development environment and starts a server, as well as hot module reloading.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12660)，来源许可：MIT。

<a id="k75580b696322"></a>

## What is React?

React (aka React.js or ReactJS) is an **open-source front-end JavaScript library** for building user interfaces based on components. It's used for handling the view layer in web and mobile applications, and allows developers to create reusable UI components and manage the state of those components efficiently.

React was created by [Jordan Walke](https://github.com/jordwalke), a software engineer at Facebook (now Meta). It was first deployed on Facebook's News Feed in 2011 and on Instagram in 2012. The library was open-sourced in May 2013 and has since become one of the most popular JavaScript libraries for building modern user interfaces.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L525)，来源许可：MIT。

<a id="kc645bcd23c4d"></a>

## What is ReactDOMServer?

The `ReactDOMServer` object enables you to render components to static markup (typically used on node server). This object is mainly used for _server-side rendering_ (SSR). The following methods can be used in both the server and browser environments:

1. `renderToString()`
2. `renderToStaticMarkup()`

For example, you generally run a Node-based web server like Express, Hapi, or Koa, and you call `renderToString` to render your root component to a string, which you then send as response.

```javascript
// using Express
import { renderToString } from "react-dom/server";
import MyPage from "./MyPage";

app.get("/", (req, res) => {
  res.write(
    "<!DOCTYPE html><html><head><title>My Page</title></head><body>"
  );
  res.write('<div id="content">');
  res.write(renderToString(<MyPage />));
  res.write("</div></body></html>");
  res.end();
});
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1912)，来源许可：MIT。

<a id="k27ad6edf8f9c"></a>

## What is reconciliation?

`Reconciliation` is the process through which React updates the Browser DOM and makes React work faster. React use a `diffing algorithm` so that component updates are predictable and faster. React would first calculate the difference between the `real DOM` and the copy of DOM `(Virtual DOM)` when there's an update of components.
React stores a copy of Browser DOM which is called `Virtual DOM`. When we make changes or add data, React creates a new Virtual DOM and compares it with the previous one. This comparison is done by `Diffing Algorithm`.
Now React compares the Virtual DOM with Real DOM. It finds out the changed nodes and updates only the changed nodes in Real DOM leaving the rest nodes as it is. This process is called _Reconciliation_.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1532)，来源许可：MIT。

<a id="k246dbd118c04"></a>

## What is Redux DevTools?

     _Redux DevTools_ is a live-editing time travel environment for Redux with hot reloading, action replay, and customizable UI. If you don't want to bother with installing Redux DevTools and integrating it into your project, consider using Redux DevTools Extension for Chrome and Firefox.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3732)，来源许可：MIT。

<a id="k725bd31ec7d0"></a>

## What is Redux Form?

     _Redux Form_ works with React and Redux to enable a form in React to use Redux to store all of its state. Redux Form can be used with raw HTML5 inputs, but it also works very well with common UI frameworks like Material UI, React Widgets and React Bootstrap.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3767)，来源许可：MIT。
