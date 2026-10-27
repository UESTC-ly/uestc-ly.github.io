# React与组件状态

<a id="k0d5efb2b977e"></a>

## How does React batch multiple state updates?

      React prevents component from re-rendering for each and every state update by grouping multiple state updates within an event handler. This strategy improves the application performance and this process known as **batching**. The older version of React only supported batching for browser events whereas React18 supported for asynchronous actions, timeouts and intervals along with native events. This improved version of batching is called **automatic batching**.

      Let's demonstrate this automatic batching feature with a below example.

```jsx
      import { useState } from "react";

      export default function BatchingState() {
        const [count, setCount] = useState(0);
        const [message, setMessage] = useState("batching");

        console.log("Application Rendered");

        const handleAsyncFetch = () => {
          fetch("https://jsonplaceholder.typicode.com/users/1").then(() => {
            // Automatic Batching re-render only once
            setCount(count + 1);
            setMessage("users fetched");
          });
        };

        return (
          <>
            <h1>{count}</h1>
            <button onClick={handleAsyncFetch}>Click Me!</button>
          </>
        );
      }
```

      The preceding code updated two state variables with in an event handler. However, React will perform automatic batching feature and the component will be re-rendered only once for better performance.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6240)，来源许可：MIT。

<a id="ke9b0dcdaf154"></a>

## How does React Fiber works? Explain in detail.

      React Fiber is the **core engine** that enables advanced features like **concurrent rendering**, **prioritization**, and **interruptibility** in React. Here's how it works:

      ### 1. **Fiber Tree Structure**

      Each component in your app is represented by a **Fiber node** in a tree structure. A Fiber node contains:
      *   Component type
      *   Props & state
      *   Pointers to parent, child, and sibling nodes
      *   Effect tags to track changes (e.g., update, placement)
      *   This forms the **Fiber Tree**, a data structure React uses instead of the traditional call stack.

      ### 2. **Two Phases of Rendering**

        #### **A. Render Phase (work-in-progress)**

      *   React builds a **work-in-progress Fiber tree**.
      *   It walks through each component (begin phase), calculates what needs to change, and collects side effects (complete phase).
      *   This phase is **interruptible**—React can pause it and resume later.
        #### **B. Commit Phase**

      *   React applies changes to the **Real DOM**.
      *   Runs lifecycle methods (e.g., `componentDidMount`, `useEffect`).
      *   This phase is **non-interruptible** but fast.

        ### 3. **Work Units and Scheduling**

      *   React breaks rendering into **units of work** (small tasks).
      *   These units are scheduled based on **priority** using the **React Scheduler**.
      *   If time runs out (e.g., user starts typing), React can **pause and yield** control back to the browser.

        ### 4. **Double Buffering with Two Trees**

      *   React maintains two trees:
      *   **Current Tree** – what's visible on the screen.
      *   **Work-In-Progress Tree** – the next version being built in memory.
      *   Only after the new tree is fully ready, React **commits** it, making it the new current tree.

        ### 5. **Concurrency and Prioritization**

      *   React can prepare multiple versions of UI at once (e.g., during slow data loading).
      *   Updates can be **assigned priorities**, so urgent updates (like clicks) are handled faster than background work.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7982)，来源许可：MIT。

<a id="k414850b9c29f"></a>

## How does React updates screen in an application?

     React updates UI in three steps,

     1. **Triggering or initiating a render:** The component is going to triggered for render in two ways.

        1. **Initial render:** When the app starts, you can trigger the initial render by calling `creatRoot` with the target DOM node followed by invoking component's `render` method. For example, the following code snippet renders `App` component on root DOM node.

```jsx
        import { createRoot } from "react-dom/client";

        const root = createRoot(document.getElementById("root"));
        root.render(<App />);
```

        2. **Re-render when the state updated:** When you update the component state using the state setter function, the componen't state automatically queues for a render.

     2. **Rendering components:** After triggering a render, React will call your components to display them on the screen. React will call the root component for initial render and call the function component whose state update triggered the render. This is a recursive process for all nested components of the target component.

     3. **Commit changes to DOM:** After calling components, React will modify the DOM for initial render using `appendChild()` DOM API and apply minimal necessary DOM updates for re-renders based on differences between rerenders.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6217)，来源许可：MIT。

<a id="k2b6cfbe43cbd"></a>

## How does ReactJS work behind the scenes?

     ReactJS is a powerful JavaScript library for building user interfaces. While it appears simple on the surface, React performs a lot of complex operations behind the scenes to efficiently update the UI. Here's an overview of how it works internally:

     #### **1. Virtual DOM & Component Rendering**

     React doesn't manipulate the real DOM directly. Instead, it uses a **Virtual DOM** — a lightweight JavaScript representation of the UI.

     When a component renders (e.g., `<App />`):

        *   React **executes the component function** (e.g., `App()`).
        *   Hooks like `useState` are registered and tracked in order.
        *   React builds a **Virtual DOM tree** from the returned JSX.
        *   This virtual DOM is a **plain JS object** that describes the desired UI.

     This process ensures fast and efficient rendering before React decides how to update the real DOM.

     #### 2. **React Fiber Architecture**

     React’s core engine is called **Fiber**, introduced in React 16. Fiber is a reimplementation of the React reconciliation algorithm with the following capabilities:

        *   Breaks rendering work into **units of work** (fiber nodes).
        *   Enables **interruptible rendering** (important for responsiveness).
        *   Supports **priority scheduling** and **concurrent rendering**.

     Each Fiber node represents a component and stores:

        *   The component type (function/class).
        *   Props, state, and effects.
        *   Links to parent, child, and sibling fibers.

     #### 3. **Reconciliation (Diffing Algorithm)**

     When state or props change:

        *   React re-executes the component to produce a new virtual DOM.
        *   It **compares the new virtual DOM to the previous one** using an efficient diffing algorithm.
        *   React determines the **minimal set of DOM changes** required.

     This process is known as **reconciliation**.

     #### 4. **Commit Phase (Real DOM Updates)**

     Once reconciliation is done:

        *   React enters the **commit phase**.
        *   It applies calculated changes to the **real DOM**.
        *   It also runs side effects like `useEffect` or `useLayoutEffect`.

     This is the only time React interacts directly with the browser DOM.

     #### 5. **Hooks and State Management**

     With Hooks (like `useState`, `useEffect`):

        *   React keeps an **internal list of hooks per component**.
        *   Hooks are identified by their order in the function.
        *   When state updates occur, React re-renders the component and re-runs the hooks in the same order.

     #### 6. **React Scheduler**

     React uses an internal **Scheduler** to control how updates are prioritized:

        *   Urgent tasks like clicks and inputs are processed immediately.
        *   Non-urgent tasks (like data fetching) can be delayed or paused.
        *   This improves responsiveness and allows for **time slicing** in Concurrent Mode.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6559)，来源许可：MIT。

<a id="k1f9b0c325976"></a>

## How does useContext works? Explain with an example

     The `useContext` hook can be used for authentication state management across multiple components and pages in a React application.

     Let's build a simple authentication flow with:

        *   **Login and Logout buttons**
        *   Global `AuthContext` to share state
        *   Components that can **access and update** auth status

      **1. Create the Auth Context:**

       You can define `AuthProvider` which holds and provides `user`, `login()`, and `logout()` via context.
```js
        // AuthContext.js
        import React, { createContext, useContext, useState } from 'react';

        const AuthContext = createContext();

        export function AuthProvider({ children }) {
          const [user, setUser] = useState(null);

          const login = (username) => setUser({ name: username });
          const logout = () => setUser(null);

          return (
            <AuthContext.Provider value={{ user, login, logout }}>
              {children}
            </AuthContext.Provider>
          );
        }

        // Custom hook for cleaner usage
        export const useAuth = () => useContext(AuthContext);
```
     **2. Wrap Your App with the Provider:**

        Wrap the above created provider in main `App.js` file      
```js
        // App.js
        import React from 'react';
        import { AuthProvider } from './AuthContext';
        import HomePage from './HomePage';
        import Dashboard from './Dashboard';

        function App() {
          return (
            <AuthProvider>
              <HomePage />
              <Dashboard />
            </AuthProvider>
          );
        }

        export default App;
```
     **3. Home page with login:**
      Read or access user and login details through custom useAuth hook and use it inside home page.

```js
         // HomePage.js
         import React from 'react';
         import { useAuth } from './AuthContext';

         function HomePage() {
           const { user, login } = useAuth();

           return (
             <div>
               <h1>Home</h1>
               {user ? (
                 <p>Welcome back, {user.name}!</p>
               ) : (
                 <button onClick={() => login('Alice')}>Login</button>
               )}
             </div>
           );
         }

         export default HomePage;
```

     **4. Dashboard with logout:**
      Read or access user and logout details from `useAuth` custom hook and use it inside dashboard page.

```js
        // Dashboard.js
        import React from 'react';
        import { useAuth } from './AuthContext';

        function Dashboard() {
          const { user, logout } = useAuth();

          if (!user) {
            return <p>Please login to view the dashboard.</p>;
          }

          return (
            <div>
              <h2>Dashboard</h2>
              <p>Logged in as: {user.name}</p>
              <button onClick={logout}>Logout</button>
            </div>
          );
        }

        export default Dashboard;
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7268)，来源许可：MIT。

<a id="keca2c82c1d83"></a>

## How events are different in React?

Handling events in React elements has some syntactic differences:

1. React event handlers are named using camelCase, rather than lowercase.
2. With JSX you pass a function as the event handler, rather than a string.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1976)，来源许可：MIT。

<a id="k3601c7653102"></a>

## How is the new JSX transform different from old transform??

     The new JSX transform doesn’t require React to be in scope. i.e, You don't need to import React package for simple scenarios.

     Let's take an example to look at the main differences between the old and the new transform,

     **Old Transform:**

```js
     import React from "react";

     function App() {
       return <h1>Good morning!!</h1>;
     }
```

     Now JSX transform convert the above code into regular JavaScript as below,

```js
     import React from "react";

     function App() {
       return React.createElement("h1", null, "Good morning!!");
     }
```

     **New Transform:**

     The new JSX transform doesn't require any React imports

```js
     function App() {
       return <h1>Good morning!!</h1>;
     }
```

     Under the hood JSX transform compiles to below code

```js
     import { jsx as _jsx } from "react/jsx-runtime";

     function App() {
       return _jsx("h1", { children: "Good morning!!" });
     }
```

     **Note:** You still need to import React to use Hooks.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5805)，来源许可：MIT。

<a id="kf4d874ef4a27"></a>

## How is useReducer Different from useState?

     There are notable differences between `useState` and `useReducer` hooks.

        | Feature               | `useState`                           | `useReducer`                          |
        |-----------------------|--------------------------------------|---------------------------------------|
        | State complexity      | Simple (one variable or flat object) | Complex, multi-part or deeply nested  |
        | Update style          | Direct (e.g. `setState(x)`)          | Through actions (e.g. `dispatch({})`) |
        | Update logic          | In component                         | In reducer function                   |
        | Reusability & testing | Less reusable                        | Highly reusable & testable            |

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6628)，来源许可：MIT。

<a id="k82326b000c60"></a>

## How React PropTypes allow different types for one prop?

     You can use `oneOfType()` method of `PropTypes`.

     For example, the height property can be defined with either `string` or `number` type as below:

```javascript
     Component.propTypes = {
       size: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
     };
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4143)，来源许可：MIT。

<a id="kb7990dccaa06"></a>

## How React Router is different from history library?

    React Router is a wrapper around the `history` library which handles interaction with the browser's `window.history` with its browser and hash histories. It also provides memory history which is useful for environments that don't have global history, such as mobile app development (React Native) and unit testing with Node.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2759)，来源许可：MIT。

<a id="k0b315d66dcbe"></a>

## How Redux Form initialValues get updated from state?

     You need to add `enableReinitialize : true` setting.

```javascript
     const InitializeFromStateForm = reduxForm({
       form: "initializeFromState",
       enableReinitialize: true,
     })(UserEdit);
```

     If your `initialValues` prop gets updated, your form will update too.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4128)，来源许可：MIT。

<a id="k42a15256148a"></a>

## How Relay is different from Redux?

Relay is similar to Redux in that they both use a single store. The main difference is that relay only manages state originated from the server, and all access to the state is used via _GraphQL_ queries (for reading data) and mutations (for changing data). Relay caches the data for you and optimizes data fetching for you, by fetching only changed data and nothing more.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3818)，来源许可：MIT。

<a id="ke38f7f32e63b"></a>

## How to access current locale with React Intl?

    You can get the current locale in any component of your application using `injectIntl()`:

```jsx harmony
    import { injectIntl, intlShape } from "react-intl";

    const MyComponent = ({ intl }) => (
      <div>{`The current locale is ${intl.locale}`}</div>
    );

    MyComponent.propTypes = {
      intl: intlShape.isRequired,
    };

    export default injectIntl(MyComponent);
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3086)，来源许可：MIT。

<a id="k410a012365b9"></a>

## How to access Redux store outside a component?

     You just need to export the store from the module where it created with `createStore()`. Also, it shouldn't pollute the global window object.

```javascript
     store = createStore(myReducer);

     export default store;
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3382)，来源许可：MIT。

<a id="k9898238031a9"></a>

## How to add Bootstrap to a react application?

     Bootstrap can be added to your React app in a three possible ways,

     1. Using the Bootstrap CDN:
        This is the easiest way to add bootstrap. Add both bootstrap CSS and JS resources in a head tag.
     2. Bootstrap as Dependency:
        If you are using a build tool or a module bundler such as Webpack, then this is the preferred option for adding Bootstrap to your React application
```javascript
        npm install bootstrap
```
     3. React Bootstrap Package:
        In this case, you can add Bootstrap to our React app is by using a package that has rebuilt Bootstrap components to work particularly as React components. Below packages are popular in this category,
        1. react-bootstrap
        2. reactstrap

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5380)，来源许可：MIT。

<a id="k90c3d791d7b4"></a>

## How to add Google Analytics for React Router?

    Add a listener on the `history` object to record each page view:

```javascript
    history.listen(function (location) {
      window.ga("set", "page", location.pathname + location.search);
      window.ga("send", "pageview", location.pathname + location.search);
    });
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2552)，来源许可：MIT。

<a id="k36a5c8bf3462"></a>

## How to add multiple middlewares to Redux?

     You can use `applyMiddleware()`.

     For example, you can add `redux-thunk` and `logger` passing them as arguments to `applyMiddleware()`:

```javascript
     import { createStore, applyMiddleware } from "redux";
     const createStoreWithMiddleware = applyMiddleware(
       ReduxThunk,
       logger
     )(createStore);
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3783)，来源许可：MIT。

<a id="k7e4120cd5cf5"></a>

## How to apply validation on props in React?

When the application is running in _development mode_, React will automatically check all props that we set on components to make sure they have _correct type_. If the type is incorrect, React will generate warning messages in the console. It's disabled in _production mode_ due to performance impact. The mandatory props are defined with `isRequired`.

The set of predefined prop types:

1. `PropTypes.number`
2. `PropTypes.string`
3. `PropTypes.array`
4. `PropTypes.object`
5. `PropTypes.func`
6. `PropTypes.node`
7. `PropTypes.element`
8. `PropTypes.bool`
9. `PropTypes.symbol`
10. `PropTypes.any`

We can define `propTypes` for `User` component as below:

```jsx harmony
import React from "react";
import PropTypes from "prop-types";

class User extends React.Component {
  static propTypes = {
    name: PropTypes.string.isRequired,
    age: PropTypes.number.isRequired,
  };

  render() {
    return (
      <>
        <h1>{`Welcome, ${this.props.name}`}</h1>
        <h2>{`Age, ${this.props.age}`}</h2>
      </>
    );
  }
}
```

**Note:** In React v15.5 _PropTypes_ were moved from `React.PropTypes` to `prop-types` library.

**Modern Recommendation:** While PropTypes are still supported, **TypeScript** is now the industry standard for type checking in React applications. Consider using TypeScript for better type safety, IDE support, and compile-time error detection.

_The Equivalent Functional Component_

```jsx harmony
import React from "react";
import PropTypes from "prop-types";

function User({ name, age }) {
  return (
    <>
      <h1>{`Welcome, ${name}`}</h1>
      <h2>{`Age, ${age}`}</h2>
    </>
  );
}

User.propTypes = {
  name: PropTypes.string.isRequired,
  age: PropTypes.number.isRequired,
};
```

_Modern TypeScript Version_

```tsx
import React from "react";

interface UserProps {
  name: string;
  age: number;
}

function User({ name, age }: UserProps) {
  return (
    <>
      <h1>{`Welcome, ${name}`}</h1>
      <h2>{`Age, ${age}`}</h2>
    </>
  );
}
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1755)，来源许可：MIT。

<a id="k3196ead08fde"></a>

## How to avoid using relative path imports in create-react-app?

    Create a file called `.env` in the project root and write the import path:

```
    NODE_PATH=src/app
```

    After that restart the development server. Now you should be able to import anything inside `src/app` without relative paths.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11505)，来源许可：MIT。

<a id="k9a12075731d2"></a>

## How to bind methods or event handlers in JSX callbacks?

There are 3 possible ways to achieve this in class components:

1. **Binding in Constructor:** In JavaScript classes, the methods are not bound by default. The same rule applies for React event handlers defined as class methods. Normally we bind them in constructor.

```javascript
   class User extends Component {
     constructor(props) {
       super(props);
       this.handleClick = this.handleClick.bind(this);
     }
     handleClick() {
       console.log("SingOut triggered");
     }
     render() {
       return <button onClick={this.handleClick}>SingOut</button>;
     }
   }
```

2. **Public class fields syntax:** If you don't like to use bind approach then _public class fields syntax_ can be used to correctly bind callbacks. The Create React App enables this syntax by default.

```jsx harmony
   handleClick = () => {
     console.log("SingOut triggered", this);
   };
```

```jsx harmony
   <button onClick={this.handleClick}>SingOut</button>
```

3. **Arrow functions in callbacks:** It is possible to use _arrow functions_ directly in the callbacks.

```jsx harmony
   handleClick() {
       console.log('SingOut triggered');
   }
   render() {
       return <button onClick={() => this.handleClick()}>SignOut</button>;
   }
```

**Note:** If the callback is passed as prop to child components, those components might do an extra re-rendering. In those cases, it is preferred to go with `.bind()` or _public class fields syntax_ approach considering performance.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10450)，来源许可：MIT。

<a id="ka29448539334"></a>

## How to create components in React?

Components are the building blocks of creating User Interfaces(UI) in React. There are two possible ways to create a component.

1. **Function Components:** This is the simplest way to create a component. Those are pure JavaScript functions that accept props object as the one and only one parameter and return React elements to render the output:

```jsx harmony
   function Greeting({ message }) {
     return <h1>{`Hello, ${message}`}</h1>;
   }
```

2. **Class Components:** You can also use ES6 class to define a component. The above function component can be written as a class component:

```jsx harmony
   class Greeting extends React.Component {
     render() {
       return <h1>{`Hello, ${this.props.message}`}</h1>;
     }
   }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L727)，来源许可：MIT。

<a id="k79eebac9bf9f"></a>

## How to create props proxy for HOC component?

You can add/edit props passed to the component using _props proxy_ pattern like this:

```jsx harmony
function HOC(WrappedComponent) {
  return class Test extends Component {
    render() {
      const newProps = {
        title: "New Header",
        footer: false,
        showFeatureX: false,
        showFeatureY: true,
      };

      return <WrappedComponent {...this.props} {...newProps} />;
    }
  };
}
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10714)，来源许可：MIT。

<a id="k89deeba62bed"></a>

## How to create react class components without ES6?

    If you don’t use ES6 then you may need to use the create-react-class module instead. For default props, you need to define getDefaultProps() as a function on the passed object. Whereas for initial state, you have to provide a separate getInitialState method that returns the initial state.

```javascript
    var Greeting = createReactClass({
      getDefaultProps: function () {
        return {
          name: "Jhohn",
        };
      },
      getInitialState: function () {
        return { message: this.props.message };
      },
      handleClick: function () {
        console.log(this.state.message);
      },
      render: function () {
        return <h1>Hello, {this.props.name}</h1>;
      },
    });
```

    **Note:** If you use createReactClass then auto binding is available for all methods. i.e, You don't need to use `.bind(this)` with in constructor for event handlers.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12575)，来源许可：MIT。

<a id="k6b23ad0263f1"></a>

## How to debug your React Native?

Follow the below steps to debug React Native app:

1. Run your application in the iOS simulator.
2. Press `Command + D` and a webpage should open up at `http://localhost:8081/debugger-ui`.
3. Enable _Pause On Caught Exceptions_ for a better debugging experience.
4. Press `Command + Option + I` to open the Chrome Developer tools, or open it via `View` -> `Developer` -> `Developer Tools`.
5. You should now be able to debug as you normally would.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3866)，来源许可：MIT。

<a id="k03afb40b4978"></a>

## How to define constants in React?

    You can use ES7 `static` field to define constant.

```javascript
    class MyComponent extends React.Component {
      static DEFAULT_PAGINATION = 10;
    }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11539)，来源许可：MIT。

<a id="k94c30d71c810"></a>

## How to do logging in React Native?

     You can use `console.log`, `console.warn`, etc. As of React Native v0.29 you can simply run the following to see logs in the console:

```
     $ react-native log-ios
     $ react-native log-android
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3855)，来源许可：MIT。

<a id="k2dd443e27ec4"></a>

## How to enable production mode in React?

You should use Webpack's `DefinePlugin` method to set `NODE_ENV` to `production`, by which it strip out things like propType validation and extra warnings. Apart from this, if you minify the code, for example, Uglify's dead-code elimination to strip out development only code and comments, it will drastically reduce the size of your bundle.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2100)，来源许可：MIT。

<a id="kdff53e19d7e7"></a>

## How to ensure hooks followed the rules in your project?

        React team released an ESLint plugin called **eslint-plugin-react-hooks** that enforces Hook's two rules. It is part of Hooks API. You can add this plugin to your project using the below command,

```javascript
        npm install eslint-plugin-react-hooks --save-dev
```

        And apply the below config in your ESLint config file,

```javascript
        // Your ESLint configuration
        {
          "plugins": [
            // ...
            "react-hooks"
          ],
          "rules": {
            // ...
            "react-hooks/rules-of-hooks": "error"
          }
        }
```

        This plugin also provide another important rule through `react-hooks/exhaustive-deps`. It ensures that the dependencies of useEffect, useCallback, and useMemo hooks are correctly listed to avoid potential bugs.

```jsx
        useEffect(() => {
          // Forgetting `message` will result in incorrect behavior
          console.log(message);
        }, []); // Here `message` should be a dependency
```
        The recommended `eslint-config-react-app` preset already includes the hooks rules of this plugin.
        For example, the linter enforce proper naming convention for hooks. If you rename your custom hooks which as prefix "use" to something else then linter won't allow you to call built-in hooks such as useState, useEffect etc inside of your custom hook anymore.

        **Note:** This plugin is intended to use in Create React App by default.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4484)，来源许可：MIT。

<a id="k54088bea8717"></a>

## How to format date using React Intl?

 The `injectIntl()` higher-order component will give you access to the `formatDate()` method via the props in your component. The method is used internally by instances of `FormattedDate` and it returns the string representation of the formatted date.

```jsx harmony
 import { injectIntl, intlShape } from "react-intl";

 const stringDate = this.props.intl.formatDate(date, {
   year: "numeric",
   month: "numeric",
   day: "numeric",
 });

 const MyComponent = ({ intl }) => (
   <div>{`The formatted date is ${stringDate}`}</div>
 );

 MyComponent.propTypes = {
   intl: intlShape.isRequired,
 };

 export default injectIntl(MyComponent);
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3106)，来源许可：MIT。

<a id="k49f258a7eb9b"></a>

## How to get history on React Router v4?

    Below are the list of steps to get history object on React Router v4,

    1.  Create a module that exports a `history` object and import this module across the project.

        For example, create `history.js` file:

```javascript
        import { createBrowserHistory } from "history";

        export default createBrowserHistory({
          /* pass a configuration object here if needed */
        });
```

    2.  You should use the `<Router>` component instead of built-in routers. Import the above `history.js` inside `index.js` file:

```jsx harmony
        import { Router } from "react-router-dom";
        import history from "./history";
        import App from "./App";

        ReactDOM.render(
          <Router history={history}>
            <App />
          </Router>,
          holder
        );
```

    3.  You can also use push method of `history` object similar to built-in history object:

```javascript
        // some-other-file.js
        import history from "./history";

        history.push("/go-here");
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2933)，来源许可：MIT。

<a id="kd43ba58bcbb8"></a>

## How to get query parameters in React Router v4?

    The ability to parse query strings was taken out of React Router v4 because there have been user requests over the years to support different implementation. So the decision has been given to users to choose the implementation they like. The recommended approach is to use query strings library.

```javascript
    const queryString = require("query-string");
    const parsed = queryString.parse(props.location.search);
```

    You can also use `URLSearchParams` if you want something native:

```javascript
    const params = new URLSearchParams(props.location.search);
    const foo = params.get("name");
```

    You should use a _polyfill_ for IE11.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2860)，来源许可：MIT。

<a id="k269348dc37b6"></a>

## How to import and export components using React and ES6?

    You should use default for exporting the components

```jsx harmony
    import User from "user";

    export default function MyProfile {
        return <User type="customer">//...</User>;
    }
```

    <details><summary><b>See Class</b></summary>
    <p>
```jsx harmony
     import React from "react";
     import User from "user";

    export default class MyProfile extends React.Component {
    render() {
    return <User type="customer">//...</User>;
    }
    }

```
    </p>
    </details>

    With the export specifier, the MyProfile is going to be the member and exported to this module and the same can be imported without mentioning the name in other components.
```

**[⬆ Back to Top](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#table-of-contents)**
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2581)，来源许可：MIT。

<a id="kfdca87ed7e48"></a>

## How to loop inside JSX?

You can simply use `Array.prototype.map` with ES6 _arrow function_ syntax.

For example, the `items` array of objects is mapped into an array of components:

```jsx harmony
<tbody>
  {items.map((item) => (
    <SomeComponent key={item.id} name={item.name} />
  ))}
</tbody>
```

But you can't iterate using `for` loop:

```jsx harmony
<tbody>
  for (let i = 0; i < items.length; i++) {
    <SomeComponent key={items[i].id} name={items[i].name} />
  }
</tbody>
```

This is because JSX tags are transpiled into _function calls_, and you can't use statements inside expressions. This may change thanks to `do` expressions which are _stage 1 proposal_.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2222)，来源许可：MIT。

<a id="kb451e9db2d5c"></a>

## How to make AJAX call and in which component lifecycle methods should I make an AJAX call?

    You can use AJAX libraries such as Axios, jQuery AJAX, and the browser built-in `fetch`. You should fetch data in the `componentDidMount()` lifecycle method. This is so you can use `setState()` to update your component when the data is retrieved.

    For example, the employees list fetched from API and set local state:

```jsx harmony
    class MyComponent extends React.Component {
      constructor(props) {
        super(props);
        this.state = {
          employees: [],
          error: null,
        };
      }

      componentDidMount() {
        fetch("https://api.example.com/items")
          .then((res) => res.json())
          .then(
            (result) => {
              this.setState({
                employees: result.employees,
              });
            },
            (error) => {
              this.setState({ error });
            }
          );
      }

      render() {
        const { error, employees } = this.state;
        if (error) {
          return <div>Error: {error.message}</div>;
        } else {
          return (
            <ul>
              {employees.map((employee) => (
                <li key={employee.name}>
                  {employee.name}-{employee.experience}
                </li>
              ))}
            </ul>
          );
        }
      }
    }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11571)，来源许可：MIT。

<a id="k3ecfdb24c8ce"></a>

## How to make AJAX request in Redux?

     You can use `redux-thunk` middleware which allows you to define async actions.

     Let's take an example of fetching specific account as an AJAX call using _fetch API_:

```javascript
     export function fetchAccount(id) {
       return (dispatch) => {
         dispatch(setLoadingAccountState()); // Show a loading spinner
         fetch(`/account/${id}`, (response) => {
           dispatch(doneFetchingAccount()); // Hide loading spinner
           if (response.status === 200) {
             dispatch(setAccount(response.json)); // Use a normal function to set the received state
           } else {
             dispatch(someError);
           }
         });
       };
     }

     function setAccount(data) {
       return { type: "SET_Account", data: data };
     }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3486)，来源许可：MIT。

<a id="k2d15b25e8b7d"></a>

## How to pass numbers to React component?

     We can pass `numbers` as `props` to React component using curly braces `{}` where as `strings` in double quotes `""` or single quotes `''`

```jsx
     import React from "react";

     const ChildComponent = ({ name, age }) => {
       return (
         <>
           My Name is {name} and Age is {age}
         </>
       );
     };

     const ParentComponent = () => {
       return (
         <>
           <ChildComponent name="Chetan" age={30} />
         </>
       );
     };

     export default ParentComponent;
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4182)，来源许可：MIT。

<a id="k9b284774d3ae"></a>

## How to pass params to history.push method in React Router v4?

    While navigating you can pass props to the `history` object:

```javascript
    this.props.history.push({
      pathname: "/template",
      search: "?name=sudheer",
      state: { detail: response.data },
    });
```

    The `search` property is used to pass query params in `push()` method.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2903)，来源许可：MIT。

<a id="kbc1d331cd52c"></a>

## How to pretty print JSON with React?

    We can use `<pre>` tag so that the formatting of the `JSON.stringify()` is retained:

```jsx harmony
    const data = { name: "John", age: 42 };

    function User {
        return <pre>{JSON.stringify(data, null, 2)}</pre>;
    }

    const container = createRoot(document.getElementById("container"));

    container.render(<User />);
```

      <details><summary><b>See Class</b></summary>
      <p>

```jsx harmony
    const data = { name: "John", age: 42 };

    class User extends React.Component {
      render() {
        return <pre>{JSON.stringify(data, null, 2)}</pre>;
      }
    }

    React.render(<User />, document.getElementById("container"));
```

      </p>
      </details>

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2439)，来源许可：MIT。

<a id="k4c9212da010a"></a>

## How to prevent component from rendering?

    You can prevent component from rendering by returning null based on specific condition. This way it can conditionally render component.

```javascript
    function Greeting(props) {
      if (!props.loggedIn) {
        return null;
      }

      return <div className="greeting">welcome, {props.name}</div>;
    }
```

```javascript
    class User extends React.Component {
      constructor(props) {
        super(props);
        this.state = {loggedIn: false, name: 'John'};
      }

      render() {
       return (
           <div>
             //Prevent component render if it is not loggedIn
             <Greeting loggedIn={this.state.loggedIn} />
             <UserDetails name={this.state.name}>
           </div>
       );
      }
```

    In the above example, the `greeting` component skips its rendering section by applying condition and returning null value.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12337)，来源许可：MIT。

<a id="kc6394cf30f06"></a>

## How to prevent infinite loops with useEffect?

        Infinite loops happen when the effect updates state that’s listed in its own dependency array, which causes the effect to re-run, updating state again and so on.

        **Infinite loop scenario:**
```js
        useEffect(() => {
          setCount(count + 1);
        }, [count]); // Triggers again every time count updates
```
        You need to ensure that setState calls do not depend on values that cause the effect to rerun, or isolate them with a guard.
```js
        useEffect(() => {
          if (count < 5) {
            setCount(count + 1);
          }
        }, [count]);
```
**[⬆ Back to Top](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#table-of-contents)**

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7599)，来源许可：MIT。

<a id="k9b7e7a4af04c"></a>

## How to programmatically trigger click event in React?

    You could use the ref prop to acquire a reference to the underlying `HTMLInputElement` object through a callback, store the reference as a class property, then use that reference to later trigger a click from your event handlers using the `HTMLElement.click` method.

    This can be done in two steps:

    1.  Create ref in render method:

```jsx harmony
        <input ref={(input) => (this.inputElement = input)} />
```

    2.  Apply click event in your event handler:

```javascript
        this.inputElement.click();
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11551)，来源许可：MIT。

<a id="k4e7e22dd3b20"></a>

## How to reset state in Redux?

     You need to write a _root reducer_ in your application which delegate handling the action to the reducer generated by `combineReducers()`.

     For example, let us take `rootReducer()` to return the initial state after `USER_LOGOUT` action. As we know, reducers are supposed to return the initial state when they are called with `undefined` as the first argument, no matter the action.

```javascript
     const appReducer = combineReducers({
       /* your app's top-level reducers */
     });

     const rootReducer = (state, action) => {
       if (action.type === "USER_LOGOUT") {
         state = undefined;
       }

       return appReducer(state, action);
     };
```

     In case of using `redux-persist`, you may also need to clean your storage. `redux-persist` keeps a copy of your state in a storage engine. First, you need to import the appropriate storage engine and then, to parse the state before setting it to undefined and clean each storage state key.

```javascript
     const appReducer = combineReducers({
       /* your app's top-level reducers */
     });

     const rootReducer = (state, action) => {
       if (action.type === "USER_LOGOUT") {
         Object.keys(state).forEach((key) => {
           storage.removeItem(`persist:${key}`);
         });

         state = undefined;
       }

       return appReducer(state, action);
     };
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3411)，来源许可：MIT。

<a id="kb1b62a25f598"></a>

## How to set initial state in Redux?

     You need to pass initial state as second argument to createStore:

```javascript
     const rootReducer = combineReducers({
       todos: todos,
       visibilityFilter: visibilityFilter,
     });

     const initialState = {
       todos: [{ id: 123, name: "example", completed: false }],
     };

     const store = createStore(rootReducer, initialState);
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3799)，来源许可：MIT。

<a id="k3305cfbda1c4"></a>

## How to structure Redux top level directories?

     Most of the applications has several top-level directories as below:

     1. **Components**: Used for _dumb_ components unaware of Redux.
     2. **Containers**: Used for _smart_ components connected to Redux.
     3. **Actions**: Used for all action creators, where file names correspond to part of the app.
     4. **Reducers**: Used for all reducers, where files name correspond to state key.
     5. **Store**: Used for store initialization.

     This structure works well for small and medium size apps.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3666)，来源许可：MIT。

<a id="k2c831848f6e3"></a>

## How to test React Native apps?

     React Native can be tested only in mobile simulators like iOS and Android. You can run the app in your mobile using expo app (https://expo.io) Where it syncs using QR code, your mobile and computer should be in same wireless network.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3849)，来源许可：MIT。

<a id="k16dfb8231a31"></a>

## How to update a component every second?

    You need to use `setInterval()` to trigger the change, but you also need to clear the timer when the component unmounts to prevent errors and memory leaks.

```javascript
    componentDidMount() {
      this.interval = setInterval(() => this.setState({ time: Date.now() }), 1000)
    }

    componentWillUnmount() {
      clearInterval(this.interval)
    }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11517)，来源许可：MIT。

<a id="kd49767789c70"></a>

## How to use &lt;FormattedMessage&gt; as placeholder using React Intl?

    The `<Formatted... />` components from `react-intl` return elements, not plain text, so they can't be used for placeholders, alt text, etc. In that case, you should use lower level API `formatMessage()`. You can inject the `intl` object into your component using `injectIntl()` higher-order component and then format the message using `formatMessage()` available on that object.

```jsx harmony
    import React from "react";
    import { injectIntl, intlShape } from "react-intl";

    const MyComponent = ({ intl }) => {
      const placeholder = intl.formatMessage({ id: "messageId" });
      return <input placeholder={placeholder} />;
    };

    MyComponent.propTypes = {
      intl: intlShape.isRequired,
    };

    export default injectIntl(MyComponent);
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3064)，来源许可：MIT。

<a id="kb47c5a826259"></a>

## How to use class field declarations syntax in React classes?

    React Class Components can be made much more concise using the class field declarations. You can initialize the local state without using the constructor and declare class methods by using arrow functions without the extra need to bind them.

    Let's take a counter example to demonstrate class field declarations for state without using constructor and methods without binding,

```jsx
    class Counter extends Component {
      state = { value: 0 };

      handleIncrement = () => {
        this.setState((prevState) => ({
          value: prevState.value + 1,
        }));
      };

      handleDecrement = () => {
        this.setState((prevState) => ({
          value: prevState.value - 1,
        }));
      };

      render() {
        return (
          <div>
            {this.state.value}

            <button onClick={this.handleIncrement}>+</button>
            <button onClick={this.handleDecrement}>-</button>
          </div>
        );
      }
    }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11954)，来源许可：MIT。

<a id="k4c083a8d36bb"></a>

## How to use connect() from React Redux?

    You need to follow two steps to use your store in your container:

    1.  **Use `mapStateToProps()`:** It maps the state variables from your store to the props that you specify.
    2.  **Connect the above props to your container:** The object returned by the `mapStateToProps` function is connected to the container. You can import `connect()` from `react-redux`.

```jsx harmony
        import React from "react";
        import { connect } from "react-redux";

        class App extends React.Component {
          render() {
            return <div>{this.props.containerData}</div>;
          }
        }

        function mapStateToProps(state) {
          return { containerData: state.data };
        }

        export default connect(mapStateToProps)(App);
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11704)，来源许可：MIT。

<a id="kbaf4a8ace8fd"></a>

## How to use Font Awesome icons in React?

     The below steps followed to include Font Awesome in React:

     1. Install `font-awesome`:

```console
        $ npm install --save font-awesome
```

     2. Import `font-awesome` in your `index.js` file:

```javascript
        import "font-awesome/css/font-awesome.min.css";
```

     3. Add Font Awesome classes in `className`:

```javascript
        function MyComponent {
          return <div><i className={'fa fa-spinner'} /></div>
        }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3902)，来源许可：MIT。

<a id="k1eb891d24237"></a>

## How to use innerHTML in React?

The `dangerouslySetInnerHTML` attribute is React's replacement for using `innerHTML` in the browser DOM. Just like `innerHTML`, it is risky to use this attribute considering cross-site scripting (XSS) attacks. You just need to pass a `__html` object as key and HTML text as value.

In this example MyComponent uses `dangerouslySetInnerHTML` attribute for setting HTML markup:

```jsx harmony
function createMarkup() {
  return { __html: "First &middot; Second" };
}

function MyComponent() {
  return <div dangerouslySetInnerHTML={createMarkup()} />;
}
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1939)，来源许可：MIT。

<a id="k900b72ffb87f"></a>

## How to use Polymer in React?

     You need to follow below steps to use Polymer in React,

     1. Create a Polymer element:

```jsx harmony
        <link
          rel="import"
          href="../../bower_components/polymer/polymer.html"
        />;
        Polymer({
          is: "calendar-element",
          ready: function () {
            this.textContent = "I am a calendar";
          },
        });
```

     2. Create the Polymer component HTML tag by importing it in a HTML document, e.g. import it in the `index.html` of your React application:

```html
        <link
          rel="import"
          href="./src/polymer-components/calendar-element.html"
        />
```

     3. Use that element in the JSX file:

```javascript
        export default function MyComponent {
          return <calendar-element />;
        }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3946)，来源许可：MIT。

<a id="k5e63cb97eeb7"></a>

## How to use React label element?

If you try to render a `<label>` element bound to a text input using the standard `for` attribute, then it produces HTML missing that attribute and prints a warning to the console.

```jsx harmony
<label for={'user'}>{'User'}</label>
<input type={'text'} id={'user'} />
```

Since `for` is a reserved keyword in JavaScript, use `htmlFor` instead.

```jsx harmony
<label htmlFor={'user'}>{'User'}</label>
<input type={'text'} id={'user'} />
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2325)，来源许可：MIT。

<a id="k1daed9af9f15"></a>

## How to use styles in React?

The `style` attribute accepts a JavaScript object with camelCased properties rather than a CSS string. This is consistent with the DOM style JavaScript property, is more efficient, and prevents XSS security holes.

```jsx harmony
const divStyle = {
  color: "blue",
  backgroundImage: "url(" + imgUrl + ")",
};

function HelloWorldComponent() {
  return <div style={divStyle}>Hello World!</div>;
}
```

Style keys are camelCased in order to be consistent with accessing the properties on DOM nodes in JavaScript (e.g. `node.style.backgroundImage`).

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1957)，来源许可：MIT。

<a id="k9e09cd580bb7"></a>

## How to use TypeScript in create-react-app application?

    Starting from react-scripts@3.3.0+ releases onwards, you can now optionally start a new app from a template by appending `--template [template-name]` to the creation command. If you don't select a template, it will create your project with base template. Remember that templates are always named in the format `cra-template-[template-name]`, here you only need to fill the `[template-name]` section.

    The typeScript can be used in your project by appending `--template typescript` to the creation command.

```bash
     npx create-react-app my-app --template typescript
```

    But if you are using React Scripting between react-scripts@2.1.0 and react-scripts@3.2.x , there is a built-in support for TypeScript. i.e, `create-react-app` now supports TypeScript natively. You can just pass `--typescript` option as below

```bash
     npx create-react-app my-app --typescript

     # or

     yarn create react-app my-app --typescript
```

     Whereas for lower versions of react scripts, just supply `--scripts-version` option as `react-scripts-ts` while you create a new project. `react-scripts-ts` is a set of adjustments to take the standard `create-react-app` project pipeline and bring TypeScript into the mix.

     Now the project layout should look like the following:

```
     my-app/
     ├─ .gitignore
     ├─ images.d.ts
     ├─ node_modules/
     ├─ public/
     ├─ src/
     │  └─ ...
     ├─ package.json
     ├─ tsconfig.json
     ├─ tsconfig.prod.json
     ├─ tsconfig.test.json
     └─ tslint.json
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11785)，来源许可：MIT。

<a id="k4c459f7fe68d"></a>

## How to write comments in React?

The comments in React/JSX are similar to JavaScript Multiline comments but are wrapped in curly braces.

**Single-line comments:**

```jsx harmony
<div>
  {/* Single-line comments(In vanilla JavaScript, the single-line comments are represented by double slash(//)) */}
  {`Welcome ${user}, let's play React`}
</div>
```

**Multi-line comments:**

```jsx harmony
<div>
  {/* Multi-line comments for more than
   one line */}
  {`Welcome ${user}, let's play React`}
</div>
```

You can use `//` and `/* */` in JS logic, hooks, and functions.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1505)，来源许可：MIT。

<a id="kab75e0fe8943"></a>

## How would you create a reusable Context?

     A **reusable Context** bundles the `createContext` call, its `Provider` (with local state/logic), and a custom hook to consume it into a single module. This hides the raw `Context` object from consumers, provides a clear API, and lets you validate that the hook is used within its provider.

```jsx
     // ThemeContext.js
     import { createContext, useContext, useMemo, useState } from "react";

     const ThemeContext = createContext(undefined);

     export function ThemeProvider({ children }) {
       const [theme, setTheme] = useState("light");

       const toggleTheme = () =>
         setTheme((prev) => (prev === "light" ? "dark" : "light"));

       // Memoize so the value reference is stable across renders
       const value = useMemo(() => ({ theme, toggleTheme }), [theme]);

       return (
         <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
       );
     }

     // Custom hook consumers use instead of importing ThemeContext directly
     export function useTheme() {
       const context = useContext(ThemeContext);
       if (context === undefined) {
         throw new Error("useTheme must be used within a ThemeProvider");
       }
       return context;
     }
```

```jsx
     // App.js
     function App() {
       return (
         <ThemeProvider>
           <Toolbar />
         </ThemeProvider>
       );
     }

     function Toolbar() {
       const { theme, toggleTheme } = useTheme();
       return <button onClick={toggleTheme}>Current theme: {theme}</button>;
     }
```

     #### Why wrap Context like this?

     1.  **Encapsulation:** Consumers never import or touch the raw `Context` object, so its internal shape can change without breaking callers.
     2.  **Guardrails:** The custom hook throws a clear error if used outside its provider, instead of silently returning `undefined`.
     3.  **Colocation:** State, updater functions, and derived values live next to the provider, making the context self-contained and easy to test in isolation.
     4.  **Composability:** Multiple reusable contexts (theme, auth, locale, etc.) can be combined by nesting providers, or composed with a helper that merges them.
     5.  **Performance-friendly:** Memoizing the provider's value (with `useMemo`) avoids creating a new object on every render, reducing unnecessary consumer re-renders (see [Does `React.memo` prevent Context consumers from re-rendering?](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#does-reactmemo-prevent-context-consumers-from-re-rendering)).

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L9481)，来源许可：MIT。

<a id="kc1fd372faf9c"></a>

## How would you structure Redux in a large application?

     The recommended approach (and what Redux Toolkit is designed around) is a **"feature folder" / "ducks"** structure rather than splitting by technical type (`actions/`, `reducers/`, `constants/`):

```
     src/
       app/
         store.js            # configureStore() + root reducer wiring
       features/
         posts/
           postsSlice.js     # createSlice: reducer + actions + thunks
           postsSelectors.js # createSelector-based selectors
           PostList.jsx       # components using useSelector/useDispatch
         users/
           usersSlice.js
           usersSelectors.js
```

     Guidelines:

     1.  **Colocate** a feature's slice, selectors, thunks, and components in one folder instead of scattering related code across parallel `actions/reducers/constants` folders.
     2.  **One slice per domain concept** (posts, users, cart), created with `createSlice`, combined once in `store.js`.
     3.  **Keep components decoupled from the store shape** by reading data only through selectors, never `state.posts.entities` directly in a component.
     4.  **Normalize related/nested data** (see Q336) so features can reference each other by ID instead of duplicating data.
     5.  **Use RTK Query (or a dedicated API slice) for server state**, and keep hand-written slices for genuine client/app state.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L9815)，来源许可：MIT。

<a id="k497f6a0a0646"></a>

## How you use decorators in React?

You can _decorate_ your _class_ components, which is the same as passing the component into a function. **Decorators** are flexible and readable way of modifying component functionality.

```jsx harmony
@setTitle("Profile")
class Profile extends React.Component {
  //....
}

/*
  title is a string that will be set as a document title
  WrappedComponent is what our decorator will receive when
  put directly above a component class as seen in the example above
*/
const setTitle = (title) => (WrappedComponent) => {
  return class extends React.Component {
    componentDidMount() {
      document.title = title;
    }

    render() {
      return <WrappedComponent {...this.props} />;
    }
  };
};
```

**Note:** Decorators are a feature that didn't make it into ES7, but are currently a _stage 2 proposal_.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10973)，来源许可：MIT。

<a id="kbea8d280edcb"></a>

## Is Hooks cover all use cases for classes?

     Hooks doesn't cover all use cases of classes but there is a plan to add them soon. Currently there are no Hook equivalents to the uncommon **getSnapshotBeforeUpdate** and **componentDidCatch** lifecycles yet.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5477)，来源许可：MIT。
