# React与组件状态

<a id="k097b3911101f"></a>

## What rules need to be followed for hooks?

     You need to follow two rules in order to use hooks,

     1. **Call Hooks only at the top level of your react functions:** You should always use hooks at the top level of react function before any early returns. i.e, You shouldn’t call Hooks inside loops, conditions, or nested functions. This will ensure that Hooks are called in the same order each time a component renders and it preserves the state of Hooks between multiple re-renders due to `useState` and `useEffect` calls.

     Let's see the difference using an example,
     **Correct usage:**:
```jsx
     function UserProfile() {
      // Correct: Hooks called at the top level
      const [name, setName] = useState('John');
      const [country, setCountry] = useState('US');

      return (
        <div>
          <h1>Name: {name}</h1>
          <p>Country: {country}</p>
        </div>
      );
     }
```
     **Incorrect usage:**:
```jsx
     function UserProfile() {
      const [name, setName] = useState('John');

      if (name === 'John') {
        // Incorrect: useState is called inside a conditional
        const [country, setCountry] = useState('US'); 
      }

      return (
        <div>
          <h1>Name: {name}</h1>
          <p>Country: {country}</p> {/* This will throw an error if the name condition isn't met */}
        </div>
      );
     }
```
     The `useState` hook for the country field is being called conditionally within an `if` block. This can lead to inconsistent state behavior and may cause hooks to be called in a different order on each re-render.

     2. **Call Hooks from React Functions only:** You shouldn’t call Hooks from regular JavaScript functions or class components. Instead, you should call them from either function components or custom hooks.

     Let's find the difference of correct and incorrect usage with below examples,

     **Correct usage:**:
```jsx
     //Example1:
     function Counter() {
      // Correct: useState is used inside a functional component
      const [count, setCount] = useState(0);

      return <div>Counter: {count}</div>;
     }
     //Example2:
     function useFetchData(url) {
      const [data, setData] = useState(null);

      useEffect(() => {
        fetch(url)
          .then((response) => response.json())
          .then((data) => setData(data));
      }, [url]);

      return data;
     }

     function UserProfile() {
      // Correct: Using a custom hook here
      const user = useFetchData('https://some-api.com/user');

      return (
        <div>
          <h1>{user ? user.name : 'Loading profile...'}</h1>
        </div>
      );
     }
```
     **Incorrect usage:**:
```jsx
      //Example1
      function normalFunction() {
        // Incorrect: Can't call hooks in normal functions
        const [count, setCount] = useState(0); 
      }

      //Example2
      function fetchData(url) {
        // Incorrect: Hooks can't be used in non-React functions
        const [data, setData] = useState(null);

        useEffect(() => {
          fetch(url)
            .then((response) => response.json())
            .then((data) => setData(data));
        }, [url]);

        return data;
      }
```
     In the above incorrect usage example, both `useState` and `useEffect` are used in non-React functions(`normalFunction` and `fetchData`), which is not allowed.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4379)，来源许可：MIT。

<a id="k20e5ca0a81d7"></a>

## What should be stored in Redux vs derived with selectors?

     A common mistake is storing **computed/derived values** in Redux state itself, which then has to be kept in sync manually every time the source data changes. The rule of thumb: **store the minimal raw data, and compute everything else with selectors.**

     | Store in Redux (source of truth) | Derive with selectors (computed) |
     | --- | --- |
     | Raw entities fetched from the server (`items`, `users`) | Filtered/sorted/paginated views of that list |
     | Simple flags representing real state (`isLoggedIn`, `selectedId`) | Aggregates like totals, counts, averages |
     | IDs of selected/active items | The full object looked up by that ID |
     | Form field values | Validation results / "is form valid" flags |

```javascript
     // BAD: `total` is derived data stored redundantly in state
     // Now every reducer that touches `items` must also recompute `total`
     { items: [...], total: 42 }

     // GOOD: store only `items`; compute `total` with a memoized selector
     const selectItems = (state) => state.cart.items;
     const selectTotal = createSelector([selectItems], (items) =>
       items.reduce((sum, i) => sum + i.price * i.qty, 0)
     );
```

     Storing only raw data and deriving the rest avoids state getting out of sync, removes the need for extra reducer logic to keep computed fields updated, and keeps re-renders scoped to components that actually depend on the derived value (thanks to selector memoization).

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L9983)，来源许可：MIT。

<a id="k29c442e07c06"></a>

## What types of values can useState hold?

     The `useState` hook accepts different types of values.

     *   Primitives: `number`, `string`, `boolean`
     *   Arrays
     *   Objects
     *   Functions
     *   `null` or `undefined`

     But you needs to be cautious with **reference types (objects/arrays)** because React compares old and new values **by reference**, so direct mutations won't trigger a re-render.
     For example, the correct and wrong ways of state updates as shown below, 
```js
     user.name = "Sudheer"; //wrong way
     setUser(prev => ({ ...prev, name: 'Sudheer' })); //correct way
```
**[⬆ Back to Top](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#table-of-contents)**

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6909)，来源许可：MIT。

<a id="ke680cd6e6fe3"></a>

## What will happen by defining nested function components?

Technically it is possible to write nested function components but it is not suggested to write nested function definitions. Because it leads to unexpected bugs and performance issues.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6537)，来源许可：MIT。

<a id="kc932c737a004"></a>

## What will happen if you use props in initial state?

If the props on the component are changed without the component being refreshed, the new prop value will never be displayed because the constructor function will never update the current state of the component. The initialization of state from props only runs when the component is first created.

The below component won't display the updated input value:

```jsx harmony
class MyComponent extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      records: [],
      inputValue: this.props.inputValue,
    };
  }

  render() {
    return <div>{this.state.inputValue}</div>;
  }
}
```

Using props inside render method will update the value:

```jsx harmony
class MyComponent extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      record: [],
    };
  }

  render() {
    return <div>{this.props.inputValue}</div>;
  }
}
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10930)，来源许可：MIT。

<a id="ke7c40c21db9e"></a>

## What would be the common mistake of function being called every time the component renders?

You need to make sure that function is not being called while passing the function as a parameter.

```jsx harmony
render() {
  // Wrong: handleClick is called instead of passed as a reference!
  return <button onClick={this.handleClick()}>{'Click Me'}</button>
}
```

Instead, pass the function itself without parenthesis:

```jsx harmony
render() {
  // Correct: handleClick is passed as a reference!
  return <button onClick={this.handleClick}>{'Click Me'}</button>
}
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10801)，来源许可：MIT。

<a id="kee4e68bbb697"></a>

## What would the context value be for no matching provider?

     When a component calls `useContext(SomeContext)` but **no matching** `<SomeContext.Provider>` **is present higher up in the component tree**, the **default value** passed to `React.createContext(defaultValue)` is returned.

```js
     const ThemeContext = React.createContext('light'); // 'light' is the default value

     function ThemedComponent() {
       const theme = useContext(ThemeContext);
       return <div>Current theme: {theme}</div>;
     }

     // No ThemeContext.Provider anywhere in the tree
```
     In this case, `theme` will be 'light'. It's the default value you provided when you created the context.

     **Note:** If you don’t specify a default value, the context value will be undefined when used without a provider:

```jsx
     const AuthContext = React.createContext(); // No default

     function Profile() {
       const auth = useContext(AuthContext);
       // auth will be undefined if there's no AuthContext.Provider
     }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7470)，来源许可：MIT。

<a id="kf35d041ba42e"></a>

## What's a common pitfall when using useContext with objects?

   A **common pitfall** when using `useContext` with objects is **triggering unnecessary re-renders** across all consuming components — even when only part of the context value changes.

   When you provide an object as the context value, React compares the entire object reference. If the object changes (even slightly), React assumes the whole context has changed, and **all components using** `useContext(MyContext)` **will re-render**, regardless of whether they use the part that changed.

   **Example:**
```js
      const MyContext = React.createContext();

      function MyProvider({ children }) {
        const [user, setUser] = useState(null);
        const [theme, setTheme] = useState('light');

        // This causes all consumers to re-render on any state change
        const contextValue = { user, setUser, theme, setTheme };

        return (
          <MyContext.Provider value={contextValue}>
            {children}
          </MyContext.Provider>
        );
      }
```
   In this case, a change in `theme` will also trigger a re-render in components that only care about `user`.

   This issue can be fixed in two ways,

   **1. Split Contexts**  
   Create separate contexts for unrelated pieces of state:

```jsx
   const UserContext = React.createContext(); 
   const ThemeContext = React.createContext();
```

   **2. Memoize Context Value**  
   Use `useMemo` to prevent unnecessary re-renders:

```jsx
     const contextValue = useMemo(() => ({ user, setUser, theme, setTheme }), [user, theme]);
```

   However, this only helps if the object structure and dependencies are well controlled.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7424)，来源许可：MIT。

<a id="k59e8eb20619e"></a>

## Whats the purpose of at symbol in the Redux connect decorator?

    The **@** symbol is in fact a JavaScript expression used to signify decorators. _Decorators_ make it possible to annotate and modify classes and properties at design time.

    Let's take an example setting up Redux without and with a decorator.

    - **Without decorator:**

```javascript
      import React from "react";
      import * as actionCreators from "./actionCreators";
      import { bindActionCreators } from "redux";
      import { connect } from "react-redux";

      function mapStateToProps(state) {
        return { todos: state.todos };
      }

      function mapDispatchToProps(dispatch) {
        return { actions: bindActionCreators(actionCreators, dispatch) };
      }

      class MyApp extends React.Component {
        // ...define your main app here
      }

      export default connect(mapStateToProps, mapDispatchToProps)(MyApp);
```

    - **With decorator:**

```javascript
      import React from "react";
      import * as actionCreators from "./actionCreators";
      import { bindActionCreators } from "redux";
      import { connect } from "react-redux";

      function mapStateToProps(state) {
        return { todos: state.todos };
      }

      function mapDispatchToProps(dispatch) {
        return { actions: bindActionCreators(actionCreators, dispatch) };
      }

      @connect(mapStateToProps, mapDispatchToProps)
      export default class MyApp extends React.Component {
        // ...define your main app here
      }
```

    The above examples are almost similar except the usage of decorator. The decorator syntax isn't built into any JavaScript runtimes yet, and is still experimental and subject to change. You can use babel for the decorators support.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11730)，来源许可：MIT。

<a id="k5ba6f4bee173"></a>

## When and how often does React invoke the setup and cleanup functions inside a useEffect hook?

     1. **Setup Function Execution (`useEffect`)**

         The setup function (or the main function) you pass to `useEffect` runs at specific points:

           1.  **After the component is mounted** (if the dependency array is empty `[]`)
           2.  **After every render** (if no dependency array is provided)
           3.  **After a dependency value changes** (if the dependency array contains variables)

     2. **Cleanup Function Execution (Returned function from `useEffect`)**

        The cleanup function is called **before the effect is re-executed** and when the component **unmounts**.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7544)，来源许可：MIT。

<a id="k4716283256c2"></a>

## When component props defaults to true?

     If you pass no value for a prop, it defaults to true. This behavior is available so that it matches the behavior of HTML.

     For example, below expressions are equivalent,

```javascript
     <MyInput autocomplete />

     <MyInput autocomplete={true} />
```

     **Note:** It is not recommended to use this approach because it can be confused with the ES6 object shorthand (example, `{name}` which is short for `{name: name}`)

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4808)，来源许可：MIT。

<a id="kf767bcfd399b"></a>

## When to use a Class Component over a Function Component?

After the addition of Hooks(i.e. React 16.8 onwards) it is always recommended to use Function components over Class components in React. Because you could use state, lifecycle methods and other features that were only available in class component present in function component too.

But even there are two reasons to use Class components over Function components.

1. If you need a React functionality whose Function component equivalent is not present yet, like Error Boundaries.
2. In older versions, If the component needs _state or lifecycle methods_ then you need to use class component.

So the summary to this question is as follows:

**Use Function Components:**

- If you don't need state or lifecycle methods, and your component is purely presentational.
- For simplicity, readability, and modern code practices, especially with the use of React Hooks for state and side effects.

**Use Class Components:**

- If you need to manage state or use lifecycle methods.
- In scenarios where backward compatibility or integration with older code is necessary.

**Note:** You can also use reusable [react error boundary](https://github.com/bvaughn/react-error-boundary) third-party component without writing any class. i.e, No need to use class components for Error boundaries.

The usage of Error boundaries from the above library is quite straight forward.

> **_Note when using react-error-boundary:_** ErrorBoundary is a client component. You can only pass props to it that are serializable or use it in files that have a `"use client";` directive.

```jsx
"use client";

import { ErrorBoundary } from "react-error-boundary";

<ErrorBoundary fallback={<div>Something went wrong</div>}>
  <ExampleApplication />
</ErrorBoundary>;
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L751)，来源许可：MIT。

<a id="ke2e58110e2e6"></a>

## When to use client and server components?

      You can efficiently build nextjs application if you are aware about which part of the application needs to use client components and which other parts needs to use server components. The common cases of both client and server components are listed below:

        **Client components:**
        1. Whenever your need to add interactivity and event listeners such as onClick(), onChange(), etc to the pages
        2. If you need to use State and Lifecycle Effects like useState(), useReducer(), useEffect() etc.
        3. If there is a requirement to use browser-only APIs.
        4. If you need to implement custom hooks that depend on state, effects, or browser-only APIs.
        5. There are React Class components in the pages.

        **Server components:**
        1. If the component logic is about data fetching.
        2. If you need to access backend resources directly.
        3. When you need to keep sensitive information((access tokens, API keys, etc)	) on the server.
        4. If you want reduce client-side JavaScript and placing large dependencies on the server.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6705)，来源许可：MIT。

<a id="k7f0f1b3087b4"></a>

## Why are Redux state functions called reducers?

     Reducers always return the accumulation of the state (based on all previous and current actions). Therefore, they act as a reducer of state. Each time a Redux reducer is called, the state and action are passed as parameters. This state is then reduced (or accumulated) based on the action, and then the next state is returned. You could _reduce_ a collection of actions and an initial state (of the store) on which to perform these actions to get the resulting final state.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3480)，来源许可：MIT。

<a id="k5aa70a46fdf2"></a>

## Why can't you update props in React?

    The React philosophy is that props should be _immutable_(read only) and _top-down_. This means that a parent can send any prop values to a child, but the child can't modify received props.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2475)，来源许可：MIT。

<a id="ka3ee535cfb65"></a>

## Why do we use array destructuring (square brackets notation) in useState?

When we declare a state variable with `useState`, it returns a pair — an array with two items. The first item is the current value, and the second is a function that updates the value. Using [0] and [1] to access them is a bit confusing because they have a specific meaning. This is why we use array destructuring instead.

For example, the array index access would look as follows:

```javascript
var userStateVariable = useState("userProfile"); // Returns an array pair
var user = userStateVariable[0]; // Access first item
var setUser = userStateVariable[1]; // Access second item
```

Whereas with array destructuring the variables can be accessed as follows:

```javascript
const [user, setUser] = useState("userProfile");
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5493)，来源许可：MIT。

<a id="k74257fdab464"></a>

## Why do you need additional care for component libraries while using forward refs?

    When you start using forwardRef in a component library, you should treat it as a breaking change and release a new major version of your library. This is because your library likely has a different behavior such as what refs get assigned to, and what types are exported. These changes can break apps and other libraries that depend on the old behavior.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12570)，来源许可：MIT。

<a id="k9ac34c205ae6"></a>

## Why does strict mode render twice in React?

     StrictMode renders components twice in development mode(not production) in order to detect any problems with your code and warn you about those problems. This is used to detect accidental side effects in the render phase. If you used `create-react-app` development tool then it automatically enables StrictMode by default.

```js
     const root = createRoot(document.getElementById("root"));
     root.render(
       <StrictMode>
         <App />
       </StrictMode>
     );
```

     If you want to disable this behavior then you can simply remove `strict` mode.

```js
     const root = createRoot(document.getElementById("root"));
     root.render(<App />);
```

     To detect side effects the following functions are invoked twice:

     1. Function component bodies, excluding the code inside event handlers.
     2. Functions passed to `useState`, `useMemo`, or `useReducer` (any other Hook)
     3. Class component's `constructor`, `render`, and `shouldComponentUpdate` methods
     4. Class component static `getDerivedStateFromProps` method
     5. State updater functions

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6133)，来源许可：MIT。

<a id="k58ac4ffb90ce"></a>

## Why is a component constructor called only once?

    React's _reconciliation_ algorithm assumes that without any information to the contrary, if a custom component appears in the same place on subsequent renders, it's the same component as before, so reuses the previous instance rather than creating a new one.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11533)，来源许可：MIT。

<a id="k67470288815b"></a>

## Why is Redux Toolkit recommended over Redux?

     **Redux Toolkit (RTK)** is the official, opinionated way to write Redux logic today. It's built on top of plain Redux and re-exports its APIs, but wraps them with utilities that remove most of the boilerplate and footguns of hand-written Redux.

     | Problem with plain Redux | How Redux Toolkit fixes it |
     | --- | --- |
     | Verbose store setup (`combineReducers`, manual middleware wiring) | `configureStore()` sets up the store, `redux-thunk`, and Redux DevTools automatically |
     | Hand-written action types/creators and switch-based reducers | `createSlice()` generates action types, action creators, and a reducer from a single object |
     | Reducers must return new state immutably (easy to mutate by mistake) | Uses **Immer** internally, so you can write "mutating" logic that's safely converted to immutable updates |
     | Async logic needs extra middleware setup (thunk/saga boilerplate) | `createAsyncThunk()` standardizes async action creators with pending/fulfilled/rejected states |
     | Repeated normalization code for lists/entities | `createEntityAdapter()` provides prebuilt reducers/selectors for normalized state |
     | No built-in data-fetching/caching layer | **RTK Query** (built on top of RTK) handles caching, refetching, and loading/error states for API calls |

     #### Example: plain Redux vs. Redux Toolkit

     **Plain Redux:**

```javascript
     const INCREMENT = "counter/increment";
     const increment = () => ({ type: INCREMENT });

     function counterReducer(state = { value: 0 }, action) {
       switch (action.type) {
         case INCREMENT:
           return { ...state, value: state.value + 1 }; // must copy manually
         default:
           return state;
       }
     }
```

     **Redux Toolkit:**

```javascript
     import { createSlice, configureStore } from "@reduxjs/toolkit";

     const counterSlice = createSlice({
       name: "counter",
       initialState: { value: 0 },
       reducers: {
         increment: (state) => {
           state.value += 1; // "mutation" is safe — Immer produces new state
         },
       },
     });

     export const { increment } = counterSlice.actions;

     const store = configureStore({ reducer: { counter: counterSlice.reducer } });
```

     In short, Redux Toolkit is recommended because it enforces best practices by default (immutability, DevTools, sensible middleware), drastically cuts boilerplate via `createSlice`/`createAsyncThunk`, and is what the official Redux docs now recommend for any new Redux code.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L9541)，来源许可：MIT。

<a id="k2097ab5277fb"></a>

## Why React tab is not showing up in DevTools?

     When the page loads, _React DevTools_ sets a global named `__REACT_DEVTOOLS_GLOBAL_HOOK__`, then React communicates with that hook during initialization. If the website is not using React or if React fails to communicate with DevTools then it won't show up the tab.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4013)，来源许可：MIT。

<a id="k2dc8512a222f"></a>

## Why React uses className over class attribute?

React uses **className** instead of **class** because of a JavaScript naming conflict with the class keyword.

1. `class` is a reserved keyword in JavaScript
    In JavaScript, class is used to define ES6 classes:

```js
    class Person {
      constructor(name) {
        this.name = name;
      }
    }
```
    If you try to use class as a variable or property name, it will throw a syntax error. Since JSX is just JavaScript with XML-like syntax, using class directly in JSX would break the parser.

2. JSX Is JavaScript

    When you write JSX like this:
```jsx
    <div class="btn">Click</div>
```
    It will be compiled to:
```jsx
    React.createElement('div', { class: 'btn' }, 'Click');
```
    But `class` is invalid in this object literal context (since it clashes with the JS keyword), hence React instead uses className.
```jsx
    <div className="btn">Click</div>
```
    which compiles to:
```jsx
    React.createElement('div', { className: 'btn' }, 'Click');
```
    React then translates `className` to` class` in the final HTML DOM.

3. Aligns with DOM APIs
    In vanilla JavaScript, you interact with element classes using:
```js
    element.className = 'my-class';
```
    React follows this convention, staying consistent with the DOM API's property name rather than HTML’s attribute.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1567)，来源许可：MIT。

<a id="kf1013ca12779"></a>

## Why ReactDOM is separated from React?

The React team worked on extracting all DOM-related features into a separate library called _ReactDOM_. React v0.14 is the first release in which the libraries are split. By looking at some of the packages, `react-native`, `react-art`, `react-canvas`, and `react-three`, it has become clear that the beauty and essence of React has nothing to do with browsers or the DOM.

To build more environments that React can render to, React team planned to split the main React package into two: `react` and `react-dom`. This paves the way to writing components that can be shared between the web version of React and React Native.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2317)，来源许可：MIT。

<a id="kd2d798dda750"></a>

## Why should component names start with capital letter?

If you are rendering your component using JSX, the name of that component has to begin with a capital letter otherwise React will throw an error as an unrecognized tag. This convention is because only HTML elements and SVG tags can begin with a lowercase letter.

```jsx harmony
function SomeComponent {
  // Code goes here
}
```

You can define function component whose name starts with lowercase letter, but when it's imported it should have a capital letter. Here lowercase is fine:

```jsx harmony
function myComponent {
  render() {
    return <div />;
  }
}

export default myComponent;
```

While when imported in another file it should start with capital letter:

```jsx harmony
import MyComponent from "./myComponent";
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2164)，来源许可：MIT。

<a id="k9a55fa36cb46"></a>

## Why should not call setState in componentWillUnmount?

    You should not call `setState()` in `componentWillUnmount()` because once a component instance is unmounted, it will never be mounted again.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12095)，来源许可：MIT。

<a id="kaaaa7db8ad40"></a>

## Why we need to be careful when spreading props on DOM elements?

When we _spread props_ we run into the risk of adding unknown HTML attributes, which is a bad practice. Instead we can use prop destructuring with `...rest` operator, so it will add only required props.

For example,

```jsx harmony
const ComponentA = () => (
  <ComponentB isDisplay={true} className={"componentStyle"} />
);

const ComponentB = ({ isDisplay, ...domProps }) => (
  <div {...domProps}>{"ComponentB"}</div>
);
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2035)，来源许可：MIT。

<a id="kfa1004a4d77f"></a>

## Would you put all API data into Redux?

     **No** — not by default. Server data (see [client state vs server state](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#what-is-the-difference-between-client-state-and-server-state)) has different needs than plain client state: caching, background refetching, deduplication of in-flight requests, invalidation, pagination, and loading/error tracking. Hand-rolling all of that inside Redux slices reinvents a data-fetching layer.

     Guidance:

     - **Use RTK Query (or React Query/SWR) for server data** — these libraries already integrate with the Redux store (RTK Query lives inside your Redux store) and handle caching/invalidation/refetching for you.
     - **Use plain Redux slices for genuine client state**: UI state, auth/session flags, user preferences, multi-step form state, feature toggles — anything that isn't just a mirror of server data.
     - **Avoid duplicating server data into a separate hand-written slice** "just in case" — it creates two sources of truth that can drift out of sync (e.g., a `users` slice updated manually alongside an RTK Query cache for the same endpoint).
     - It's fine to **combine both**: e.g., store the *currently selected* item's ID in a normal slice, while the actual item data comes from an RTK Query/React Query cache keyed by that ID.

     In short, Redux (or any store) is best reserved for state your UI truly owns; let a dedicated data-fetching layer own anything that mirrors the server.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10010)，来源许可：MIT。

<a id="k0f59690e2016"></a>

## 什么是 ReAct？

**ReAct** 是 Reasoning and Acting 的组合思想，即让**模型在任务中交替进行“推理”和“行动”**。推理用于决定下一步要做什么，行动通常是调用工具、检索资料、执行代码、查询数据库或访问 API。

![](https://raw.githubusercontent.com/WeThinkIn/AIGC-Interview-Book/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/imgs/05-3.png)

与单纯生成答案相比，ReAct 更适合需要外部信息或多步操作的任务。例：模型先判断需要查询订单状态，再调用订单 API；拿到结果后再判断是否需要查询物流；最后组织用户可读答案。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80/05_%E6%8F%90%E7%A4%BA%E5%B7%A5%E7%A8%8B%EF%BC%9A%E5%BA%94%E7%94%A8%E5%A4%A7%E6%A8%A1%E5%9E%8B%E7%9A%84%E9%AB%98%E7%BA%A7%E6%96%B9%E6%B3%95.md#L351)，来源许可：GPL-3.0。

<a id="kc764a1605303"></a>

## 你刚才提到Plan‑and‑Execute适合大型工程拆解执行，部署时会结合ReAct。那如果遇到需要动态调整全局目标，初始计划很快失效的开放场景，你会选择哪种模式组合来处理？

**回答：**

可以采用分层、滚动规划：上层维护用户授权的目标、约束和里程碑，下层使用 ReAct 处理局部不确定性，只详细规划近期步骤，根据新观察更新后续计划。计划是可修订的工作假设，不是一次生成后必须机械执行的脚本。

要区分“手段需要变化”和“用户目标本身变化”。工具失败、资源变化可以触发换路径；新的证据可能说明目标不可达，需要向用户报告或请求澄清。Agent 不能因为网页、工具输出或自我反思中的一句话，擅自改掉用户目标、权限或风险边界。

状态中至少保存目标版本、约束、计划版本、已完成且验证的里程碑、未完成依赖、预算与失败证据。局部失败先尝试受控替代方案，只有影响关键依赖或全局可行性时才升级重规划。保留有效的已完成成果，对失效部分明确作废；取消旧计划任务时还需防止其延迟结果覆盖新状态。

```text
目标与约束 -> 短期计划 -> 局部执行 -> 可验证观察
                    ^                 |
                    |-- 触发条件成立 --|
                    |
             必要时确认目标变化
```

开放场景也需要全局 deadline、最大工具步数、重规划次数与成本上限。达到预算后应输出已完成内容和未解决问题，而不是让系统无限“继续思考”。

<a id="hengsheng-ai-dev-20260923-q17"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E6%81%92%E7%94%9F%E7%94%B5%E5%AD%90%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L333)，来源许可：GPL-3.0。

<a id="kfdf92f427e6b"></a>

## 你的 Agent 是用的 ReAct 还是 Plan-and-Execute？——为什么选这个？如果任务更复杂（比如 50 步的长链路），你的方案还 work 吗？怎么改进？

**回答：**

ReAct 是“思考/决策 -> 行动 -> 观察 -> 下一步决策”的交错循环。它每一步都利用最新观察，适合搜索、问答和工具结果会改变后续路径的任务；缺点是模型调用次数多，容易局部贪心、重复调用或在相似状态中循环。

Plan-and-Execute 先生成一个较完整的计划，再由执行器逐步完成，并在必要时重新规划。它减少了每一步规划开销，适合子任务边界清晰、计划相对稳定的任务；缺点是初始计划可能基于错误假设，若执行器不反馈给规划器，错误会被连续放大。

真实系统通常采用混合方案：先生成粗粒度计划，由确定性执行器控制预算和依赖；每个高不确定性节点内部使用 ReAct；当观察与计划偏差超过阈值时触发局部重规划，而不是每一步从头规划。选择标准可以写成：

$$
\text{Policy}=
\begin{cases}
\text{ReAct}, & \text{环境反馈强、动作短且路径不确定};\\
\text{Plan-and-Execute}, & \text{子任务边界清晰、依赖稳定};\\
\text{Hybrid}, & \text{长链路且局部不确定性高}.
\end{cases}
$$

50 步长链路不能简单把最大步数改成 50。需要增加：任务分段与层级规划、每段的完成条件、阶段性 checkpoint、依赖图、错误预算、幂等执行、局部重试、全局超时和人工接管。上下文也不能保留全部原始 Observation，而应将每一步压缩成结构化状态，只保留未完成目标、已确认事实、工具结果引用、失败原因和下一步约束。

长链路的评测不能只看最终成功率，还要看每步错误率如何累积、失败恢复率、平均有效步数、重复副作用率和成本。若单步成功概率为 $p$，50 步完全正确的概率近似为 $p^{50}$，这说明系统必须通过验证、重试和分段恢复降低误差传播，而不能只依赖更大的上下文窗口。

<a id="deepseek-agent-20260908-q5"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/DeepSeek%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L482)，来源许可：GPL-3.0。

<a id="k914c5c73e1f4"></a>

## 在解释代码的时候有串联到前面提到的reactive和ref的区别与各自的特点

**回答：**

可以用实际变量连接前面的原理：若查询结果需要整体替换，`const items=ref([])` 后赋值 `items.value=newItems`；若是同一表单对象中的字段变化，`const form=reactive({keyword:''})` 后修改 `form.keyword`。

需要解构表单字段时使用 toRefs 保留连接，而不是取出一个普通字符串。若图表库实例或大型不可变结果无需深层代理，可评估 shallowRef，并显式管理更新。

代码解释应说明为什么选择这种状态边界、谁拥有它、何时清理，以及模板或计算属性如何读取。不要把 ref 说成只能保存基本类型，也不要把 reactive 说成不能嵌套对象。

<a id="jd-damodel-20251211-20260205-p5-q18"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E4%BA%AC%E4%B8%9C%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L795)，来源许可：GPL-3.0。

<a id="kbeaeb3bbdf76"></a>

## 对比一下react和vue

**回答：**

Vue 提供较完整的响应式与模板/单文件组件约定，React 更偏 UI 库，以函数组件、props 和显式状态更新为核心，生态中常通过 hooks、路由和状态库组合。比较应落到项目：团队生态、渲染方式、状态边界、TypeScript、性能诊断和迁移成本，而非简单判断谁更快。

<a id="jd-damodel-20251211-20260205-p5-q12"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E4%BA%AC%E4%B8%9C%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L733)，来源许可：GPL-3.0。

<a id="k8d461926bf69"></a>

## 对比思维链（CoT），ReAct范式在模型与外部环境交互过程中，核心解决了哪些痛点问题？

<a id="batch4-p2-q9"></a>

**相关解释：** [系统是否用到ReAct模式？](React%E4%B8%8E%E7%BB%84%E4%BB%B6%E7%8A%B6%E6%80%81-06.md#k772377a2cedb)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L366)，来源许可：GPL-3.0。

<a id="kdd874f506f93"></a>

## 手写一个简单的 Agent Loop 框架（Python 伪代码），支持：工具注册、ReAct 循环、最大步数限制、错误处理。

**回答：**

下面的伪代码将模型决策、工具注册、参数校验、循环预算和异常处理分开。真实生产代码还应增加权限、超时、取消、幂等、持久化、流式输出和审计。

```python
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Tool:
    name: str
    description: str
    function: Callable[..., Any]


class AgentLoop:
    def __init__(self, model, max_steps: int = 8):
        self.model = model
        self.max_steps = max_steps
        self.tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if not tool.name or tool.name in self.tools:
            raise ValueError("invalid or duplicated tool name")
        self.tools[tool.name] = tool

    def run(self, user_input: str) -> str:
        messages = [{"role": "user", "content": user_input}]
        errors = 0

        for step in range(self.max_steps):
            try:
                decision = self.model.decide(
                    messages=messages,
                    tools=[
                        {"name": t.name, "description": t.description}
                        for t in self.tools.values()
                    ],
                )
                # decide must return {type: final|tool_call, ...}.
                if decision["type"] == "final":
                    return decision["content"]
                if decision["type"] != "tool_call":
                    raise ValueError("unknown decision type")

                name = decision["name"]
                arguments = decision.get("arguments", {})
                if name not in self.tools:
                    raise ValueError(f"unknown tool: {name}")
                tool = self.tools[name]
                validate_arguments(tool, arguments)
                result = tool.function(**arguments)
                observation = bound_observation(result)
                messages.append({"role": "assistant", "content": decision})
                messages.append({"role": "tool", "name": name, "content": observation})
                errors = 0
            except RetryableToolError as exc:
                errors += 1
                messages.append({"role": "tool", "content": f"retryable error: {exc}"})
                if errors >= 2:
                    return "工具连续失败，任务暂停，请检查后重试。"
            except (ValueError, ToolError) as exc:
                messages.append({"role": "system", "content": f"action rejected: {exc}"})
                errors += 1
                if errors >= 2:
                    return "工具调用未通过校验，任务终止。"
            except Exception:
                # 真实代码应记录 trace，不把堆栈直接暴露给模型或用户。
                return "执行过程中发生内部错误，任务终止。"

        return "已达到最大执行步数，任务未完成。"
```

关键点有四个：第一，工具注册信息要有 schema，不只是一段描述；第二，模型返回的工具名和参数必须在服务端重新校验；第三，异常要区分可重试、不可重试和未知异常，不能无限循环；第四，达到最大步数必须有明确失败状态，并保存轨迹供诊断。若工具有写操作，还要把 `request_id` 作为幂等键传入执行层。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/DeepSeek%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L884)，来源许可：GPL-3.0。

<a id="k824a9a800e9c"></a>

## 技术栈是什么（VUE，但是秋招都在要求react，所以有自学

**回答：**

先说实际生产使用的技术栈与承担范围，再说明 React 自学进度。可以按 Vue 版本、TypeScript、状态管理、路由、请求封装、构建工具、测试和图表模块组织；只列真正使用过的工具。

迁移到 React 时，复用的是组件划分、数据流、浏览器与工程化知识，需重点理解不可变状态更新、hooks 闭包与依赖、组件重渲染和副作用清理。做一个可运行的小功能，比较两种框架的状态与生命周期，比宣称已经精通新框架更可信。

不能从题干中的招聘感受推出所有岗位都要求 React；具体以目标团队技术栈和招聘要求为准。

<a id="jd-damodel-20251211-20260205-p5-q11"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E4%BA%AC%E4%B8%9C%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L722)，来源许可：GPL-3.0。

<a id="k772377a2cedb"></a>

## 系统是否用到ReAct模式？

**回答：**
ReAct 把推理与行动交替组织：Thought 决定下一步，Action 调用工具，Observation 反馈环境结果，适合需要外部信息和多步操作的任务。Reflection 则是在执行后对结果或轨迹做自检、纠错和策略更新，适合提升复杂任务可靠性。两者的区别是 ReAct 强调边想边做，Reflection 强调做完或阶段性做完后复盘；工程上通常结合使用，并用预算、停止条件和失败兜底防止循环。

<a id="batch4-p1-q11"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L229)，来源许可：GPL-3.0。

<a id="k2403d795d7fc"></a>

## 讲一下 ReAct 的流程？

**回答：**

ReAct 是 Reasoning and Acting 的组合，核心是让模型根据当前状态选择 Action，再用真实环境返回的 Observation 修正下一步决策：

$$
s_t \xrightarrow{\text{reason/decide}} a_t
\xrightarrow{\text{tool or env}} o_{t+1}
\xrightarrow{\text{state update}} s_{t+1}
$$

工程流程通常是：

1. 解析目标、约束、可用工具、预算和停止条件；
2. 模型基于当前上下文决定直接回答还是产生结构化工具调用；
3. Harness 做权限、schema、参数、预算和副作用检查；
4. 工具执行，返回被裁剪、标注来源的 Observation；
5. 更新消息、任务状态和 action history；
6. 验证是否完成，未完成则进入下一轮，失败则重试、重规划或人工接管。

ReAct 的优势是外部 grounding：模型不必只靠参数知识猜测，可以搜索、读取文件或查询业务状态。局限是局部贪心、工具循环、长 Observation 挤压上下文，以及每一步串行等待带来的成本和延迟。

生产实现不会只写一个无限 `while`。要设置最大步数、总 Token/deadline、重复动作检测、工具错误分类、状态 checkpoint 和独立终止验证；高风险 Action 前还需要 policy gate。ReAct 是一种控制模式，不自动等于可靠 Agent。

<a id="xiaohongshu-agent-dev-20260812-q11"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E5%B0%8F%E7%BA%A2%E4%B9%A6%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1042)，来源许可：GPL-3.0。

<a id="k75b902ed88b5"></a>

## 讲一下智能体React 和Reflection范式的区别

<a id="batch3-p2-q12"></a>

**相关解释：** [Agent常见模式（ReAct/Plan and Execute等）](React%E4%B8%8E%E7%BB%84%E4%BB%B6%E7%8A%B6%E6%80%81-01.md#k93a12d0c9256)

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E7%BE%8E%E5%9B%A2%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L197)，来源许可：GPL-3.0。

<a id="kd0b632b6cce8"></a>

## 讲讲react思想

**回答：**

结合相邻的 Agent 题，这里的 react 优先理解为 **ReAct（Reasoning and Acting）**；如果面试官指前端 React，应先澄清。ReAct 将决策与行动交替：依据目标和当前观察选择工具，执行后读取结果，再决定下一动作或结束。

例如查商品是否可购买，先检索商品，再读取库存与配送条件，最后生成有依据的结论。它区别于一次性输出全部计划的方式，中间新信息可以改变后续步骤。

工程实现可用结构化 action、参数和 observation，不要求暴露模型隐藏思维链。运行时控制权限、最大步数、超时和预算，并独立验证目标是否完成；否则容易循环调用或把工具返回当成高优先级指令。

<a id="jd-damodel-20251211-20260205-p7-q14"></a>

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/%E5%A4%A7%E5%8E%82%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98%EF%BC%88%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0%EF%BC%89/%E4%BA%AC%E4%B8%9C%E9%AB%98%E9%A2%91%E9%9D%A2%E8%AF%95%E9%A2%98.md#L1157)，来源许可：GPL-3.0。

<a id="kcdbcd12adcc9"></a>

## 请简述一�?React Fiber 的概念？

在页面元素很多，且需要频繁刷新的场景下，React 15 会出现掉帧的现象。那么为什么会出现掉帧问题呢？其根本原因，是大量的同步计算任务阻塞了浏览器�?UI 渲染。默认情况下，JS 运算、页面布局和页面绘制都是运行在浏览器的主线程当中，他们之间是互斥的关系。如�?JS 运算持续占用主线程，页面就没法得到及时的更新。当我们调用 setState 更新页面的时候，React 会遍历应用的所有节点，计算出差异，然后再更�?UI。如果页面元素很多，整个过程占用的时机就可能超过 16 毫秒，就容易出现掉帧的现象。而原因就�?React 15 采用的是递归的方式遍历整颗组件树�?

react16 将底层更新单元的数据结构改成了链表结构。以前的协调算法是递归调用，通过 react dom 树级关系构成的栈递归。�?fiber 是扁平化的链表的数据存储结构，通过 child 找第一个子节点，return 找父节点，sibling 找兄弟节点。遍历从递归改为循环�?

这是 React 核心算法的一次大的更新，重写�?React �?reconciliation 算法。reconciliation 算法是用来更新并且渲�?DOM 树的算法。以�?React 15.x 的版本使用的算法称为“stack reconciliation”，现在称为“fiber reconciler”�?

fiber reconciler 主要的特点是可以把更新流程拆分成一个一个的小的单元进行更新，并且可以中断，转而去执行高优先级的任务或者浏览器的动画渲染等，等主线程空闲了再继续执行更新�?

对于流畅度问题，我们很容易想到一�?api：requestldleCallback �?这个 api 可以在浏览器空闲的时候执行回调，我们把复杂的任务分片在浏览器空闲的时间执行，就不会影响浏览器的渲染等工作。这个就可以解决复杂任务长时间霸占主线程导致渲染延迟�?

但是可能由于兼容性的考虑，react 团队放弃了这�?api，转而利�?requestAnimationFrame �?MessageChannel pollyfill 了一�?requestIdleCallback

当前帧先执行浏览器的渲染等任务，如果当前帧还有空闲时间，则执行任务，直到当前帧的时间用完。如果当前帧已经没有空闲时间，就等到下一帧的空闲时间再去执行�?

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/06-development-tech/frontend/frontend-frameworks.md#L15)，来源许可：GPL-3.0。

<a id="kbc3bfed9cccf"></a>

## 面试追问：CoT 和 ToT 分别是什么？它们和 ReAct 有什么区别？

CoT 通过中间推理步骤组织求解；ToT 将候选推理状态展开为树，结合评估、搜索和必要的回溯探索多条路径；ReAct 则强调推理和外部行动交替。三者分别突出推理表达、搜索结构与环境交互，不属于同一条互斥分类轴。

ToT 可使用宽度、深度或束搜索策略，但分支评估本身可能出错，分支数量也迅速消耗预算。CoT 的单条链容易受早期错误影响；ReAct 通过工具得到新证据，却会受到工具质量和执行成本约束。它们可以组合，也不能保证生成的解释忠实反映模型内部过程。

确定性计算交给代码，有限组合探索可以考虑搜索，未知外部信息通过工具获得。面试中举例说明任务为何需要某种机制，再给出停止条件和验证方式；生产日志记录可见的决策摘要与证据即可，不依赖读取隐藏思维链。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L399)，来源许可：GPL-3.0。

<a id="kb6eefa62d14f"></a>

## 面试追问：Plan and Execute 和 ReAct 有什么区别？什么时候适合先规划再执行？

Plan and Execute 先生成带依赖和验收标准的计划，再执行步骤；ReAct 以局部观察驱动下一步行动。前者适合目标可拆分、步骤依赖清晰、任务较长的场景，后者适合环境变化快、必须边查边决定路径的场景。

“先规划”不意味着计划永远不变。规划器应输出可检查的子目标与依赖，执行器反馈结果，评估器判断是否需要重规划。固定计划会受错误假设拖累，逐步 ReAct 又可能缺少全局方向，两者可组合为“全局计划 + 局部行动循环”。

Plan-and-Solve 常用于一次推理中先分解再解答，并不天然包含外部工具和持久化执行器；Plan-and-Execute 强调计划与实际执行的分工。比较时看状态和执行机制，不要仅凭名称判断。简单查询通常不需要额外的规划调用。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L285)，来源许可：GPL-3.0。

<a id="k40bef46025b8"></a>

## 面试追问：ReAct 的执行流程是什么？适合什么场景？

ReAct 将推理与行动交替组织：理解目标和已有观察，选择一个工具动作，读取环境反馈，再决定后续动作或给出答案。它适合需要外部证据、路径难以一次确定的搜索、排障和代码修复。

例如排查接口超时，先读取错误信息，再查看相关调用或运行测试，根据新证据决定下一步，而不是在开始时猜完所有原因。每轮工具输出都可能改变决策，因此需要保留行动与观察之间的对应关系。

论文中的 Thought/Action/Observation 是方法说明；生产系统不必获取或展示模型的私有思维链，也不能假设 API 会暴露它。可观测性应依靠可见的行动摘要、工具参数、输出和状态变化。设置步数、费用、截止时间、重复行动检测和验收条件，防止循环失控。

### 参考资料

- [AIGC Interview Book](https://github.com/WeThinkIn/AIGC-Interview-Book/blob/34e9ee6aa6d35d1e213099a7ae9f433b7b9e6fe6/AI%20Agent%E5%9F%BA%E7%A1%80/03_Agent%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E4%B8%8E%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%BC%96%E6%8E%92%E9%AB%98%E9%A2%91%E8%80%83%E7%82%B9.md#L179)，来源许可：GPL-3.0。
