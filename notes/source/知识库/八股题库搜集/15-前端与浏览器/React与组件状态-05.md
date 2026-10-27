# React与组件状态

<a id="k3738a9b16d10"></a>

## What is Redux middleware?

     **Middleware** provides a way to extend Redux with custom logic that runs **between dispatching an action and the moment it reaches the reducer**. It's the standard extension point for side effects (logging, crash reporting, async calls, analytics) since reducers themselves must stay pure and synchronous.

```javascript
     import { configureStore } from "@reduxjs/toolkit";

     const logger = (store) => (next) => (action) => {
       console.log("dispatching", action);
       const result = next(action);
       console.log("next state", store.getState());
       return result;
     };

     const store = configureStore({
       reducer: rootReducer,
       middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(logger),
     });
```

     Common middleware includes `redux-thunk` (dispatch functions for async logic), `redux-saga` (generator-based side effects), `redux-logger` (action/state logging), and RTK's built-in serializable/immutable-state check middleware.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L9758)，来源许可：MIT。

<a id="k77ee3575a29b"></a>

## What is Redux Thunk?

     _Redux Thunk_ middleware allows you to write action creators that return a function instead of an action. The thunk can be used to delay the dispatch of an action, or to dispatch only if a certain condition is met. The inner function receives the store methods `dispatch()` and `getState()` as parameters.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3720)，来源许可：MIT。

<a id="kad1294e93ddc"></a>

## What is redux-saga?

     `redux-saga` is a library that aims to make side effects (asynchronous things like data fetching and impure things like accessing the browser cache) in React/Redux applications easier and better.

     It is available in NPM:

```console
     $ npm install --save redux-saga
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3680)，来源许可：MIT。

<a id="k9c9a2a35c406"></a>

## What is Redux?

       Redux is a predictable state container for JavaScript applications, most commonly used with React. It helps you manage and centralize your application’s state in a single source of truth, enabling easier debugging, testing, and maintenance—especially in large or complex applications. Redux core is tiny library(about 2.5kB gzipped) and has no dependencies.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3290)，来源许可：MIT。

<a id="k84b8fab34ebf"></a>

## What is render hijacking in react?

     The concept of render hijacking is the ability to control what a component will output from another component. It means that you decorate your component by wrapping it into a Higher-Order component. By wrapping, you can inject additional props or make other changes, which can cause changing logic of rendering. It does not actually enable hijacking, but by using HOC you make your component behave differently.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4176)，来源许可：MIT。

<a id="ka8da5610333d"></a>

## What is Shallow Renderer in React testing?

    _Shallow rendering_ is useful for writing unit test cases in React. It lets you render a component _one level deep_ and assert facts about what its render method returns, without worrying about the behavior of child components, which are not instantiated or rendered.

    For example, if you have the following component:

```javascript
    function MyComponent() {
      return (
        <div>
          <span className={"heading"}>{"Title"}</span>
          <span className={"description"}>{"Description"}</span>
        </div>
      );
    }
```

    Then you can assert as follows:

```jsx harmony
    import ShallowRenderer from "react-test-renderer/shallow";

    // in your test
    const renderer = new ShallowRenderer();
    renderer.render(<MyComponent />);

    const result = renderer.getRenderOutput();

    expect(result.type).toBe("div");
    expect(result.props.children).toEqual([
      <span className={"heading"}>{"Title"}</span>,
      <span className={"description"}>{"Description"}</span>,
    ]);
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3134)，来源许可：MIT。

<a id="k94a756d8a891"></a>

## What is state in React?

_State_ of a component is an object that holds some information that may change over the lifetime of the component. The important point is whenever the state object changes, the component re-renders. It is always recommended to make our state as simple as possible and minimize the number of stateful components.

![state](https://raw.githubusercontent.com/sudheerj/reactjs-interview-questions/55b7d491cd74c7b37f9352f3b2420d66e7187951/images/state.jpg)

Let's take an example of **User** component with `message` state. Here, **useState** hook has been used to add state to the User component and it returns an array with current state and function to update it.

```jsx harmony
import { useState } from "react";

function User() {
  const [message, setMessage] = useState("Welcome to React world");

  return (
    <div>
      <h1>{message}</h1>
    </div>
  );
}
```

Whenever React calls your component or access `useState` hook, it gives you a snapshot of the state for that particular render.

See Class
<p>

```jsx harmony
import React from "react";
class User extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      message: "Welcome to React world",
    };
  }

  render() {
    return (
      <div>
        <h1>{this.state.message}</h1>
      </div>
    );
  }
}
```

</p>

State is similar to props, but it is private and fully controlled by the component ,i.e., it is not accessible to any other component till the owner component decides to pass it.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L843)，来源许可：MIT。

<a id="kd9d47e57a0a4"></a>

## What is Streaming SSR and how does React 18+ improve it?

     **Streaming SSR** sends HTML to the browser in chunks as it's generated, rather than waiting for the entire page. React 18+ dramatically improves this with Suspense integration.

     #### Traditional SSR (Pre-React 18)
```
     Server: Wait for ALL data → Generate ALL HTML → Send to client
     Client: Receive HTML → Download ALL JS → Hydrate ALL components
     Problem: Slow components block entire page!
```

     #### Streaming SSR (React 18+)
```
     Server: Send HTML as it's ready, wrap slow parts in <Suspense>
     Client: Render immediately, hydrate progressively
     Benefit: User sees content faster!
```

     #### Basic Example
```jsx
     import { Suspense } from 'react';

     export default function Page() {
       return (
         <html>
           <body>
             {/* Sent immediately */}
             <header>
               <h1>My App</h1>
             </header>

             {/* Sent immediately with fallback */}
             <Suspense fallback={<div>Loading comments...</div>}>
               <Comments /> {/* Streamed when ready */}
             </Suspense>

             {/* Also streamed separately */}
             <Suspense fallback={<div>Loading recommendations...</div>}>
               <Recommendations /> {/* Streamed when ready */}
             </Suspense>

             <footer>© 2026</footer>
           </body>
         </html>
       );
     }
```

     #### Server Component with Data Fetching
```jsx
     // This is a Server Component (async!)
     async function Comments() {
       const comments = await db.comments.findMany();

       return (
         <ul>
           {comments.map(comment => (
             <li key={comment.id}>{comment.text}</li>
           ))}
         </ul>
       );
     }
```

     #### How It Works
     1. Server starts sending HTML immediately
     2. When it hits `<Suspense>`, it sends the fallback
     3. Continues streaming rest of the page
     4. When data is ready, sends the actual component
     5. Client replaces fallback with real content
     6. Hydration happens independently per component

     #### Selective Hydration
```jsx
     function App() {
       return (
         <div>
           <header>Header</header> {/* Hydrates first */}

           <Suspense fallback={<Spinner />}>
             <HeavyComponent /> {/* Hydrates when user interacts */}
           </Suspense>

           <Suspense fallback={<Spinner />}>
             <Comments /> {/* Hydrates independently */}
           </Suspense>
         </div>
       );
     }
```

     #### Benefits
     - **Faster TTFB** (Time to First Byte): User sees content sooner
     - **Better UX**: Progressive loading instead of blank screen
     - **Prioritized hydration**: Interactive elements hydrate first
     - **Resilient**: Slow components don't block fast ones

     #### Next.js App Router Example
```jsx
     // app/page.tsx
     import { Suspense } from 'react';
     import ProductList from './ProductList';
     import Reviews from './Reviews';

     export default function ProductPage() {
       return (
         <div>
           <h1>Product Page</h1>

           {/* Streams product list first */}
           <Suspense fallback={<ProductSkeleton />}>
             <ProductList />
           </Suspense>

           {/* Reviews stream separately */}
           <Suspense fallback={<ReviewSkeleton />}>
             <Reviews />
           </Suspense>
         </div>
       );
     }

     // These are async Server Components
     async function ProductList() {
       const products = await fetchProducts(); // Doesn't block Reviews
       return <div>{/* render products */}</div>;
     }

     async function Reviews() {
       const reviews = await fetchReviews(); // Doesn't block ProductList
       return <div>{/* render reviews */}</div>;
     }
```

     #### Key Requirements
     - Use React 18+ with `createRoot` and `hydrateRoot`
     - Wrap slow components in `<Suspense>`
     - Use frameworks supporting streaming (Next.js, Remix, etc.)
     - Server must support streaming responses

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L9195)，来源许可：MIT。

<a id="ka3105dcb6380"></a>

## What is strict mode in React?

`React.StrictMode` is a useful component for highlighting potential problems in an application. Just like `<Fragment>`, `<StrictMode>` does not render any extra DOM elements. It activates additional checks and warnings for its descendants. These checks apply for _development mode_ only.

```jsx harmony
import { StrictMode } from "react";

function App() {
  return (
    <div>
      <Header />
      <StrictMode>
        <div>
          <ComponentOne />
          <ComponentTwo />
        </div>
      </StrictMode>
      <Header />
    </div>
  );
}
```

In the example above, the _strict mode_ checks apply to `<ComponentOne>` and `<ComponentTwo>` components only. i.e., Part of the application only.

**Note:** Frameworks such as NextJS has this flag enabled by default.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6090)，来源许可：MIT。

<a id="k0dce04f109bc"></a>

## What is suspense component?

     React Suspense is a built-in feature that lets you delay rendering part of the UI until asynchronous work (such as loading a component or fetching data) is ready. While waiting, React shows a fallback UI (loading text, skeleton, spinner, etc.) defined by the nearest `<Suspense>` boundary.

     Common use cases:

     1. **Code splitting with `React.lazy()`**

```javascript
        import { Suspense, lazy } from "react";

        const OtherComponent = lazy(() => import("./OtherComponent"));

        function MyComponent() {
          return (
            <Suspense fallback={<div>Loading component...</div>}>
              <OtherComponent />
            </Suspense>
          );
        }
```

        The fallback is shown until `OtherComponent` is downloaded and rendered.

     2. **Data fetching that can suspend**

```jsx
        import { Suspense, use } from "react";

        function UserProfile() {
          const user = use(fetchUser()); // suspends until promise resolves
          return <div>{user.name}</div>;
        }

        function App() {
          return (
            <Suspense fallback={<div>Loading user...</div>}>
              <UserProfile />
            </Suspense>
          );
        }
```

     3. **Nested Suspense for progressive loading**

        Nested boundaries let important content render first while slower sections keep loading.

```jsx
        import { Suspense, lazy } from "react";

        const ProductDetails = lazy(() => import("./ProductDetails"));
        const ProductReviews = lazy(() => import("./ProductReviews"));

        function ProductPage() {
          return (
            <Suspense fallback={<PageSkeleton />}>
              <ProductDetails />

              <Suspense fallback={<ReviewsSkeleton />}>
                <ProductReviews />
              </Suspense>
            </Suspense>
          );
        }
```

        Here, `ProductDetails` can appear first, and `ProductReviews` can continue loading with its own fallback.

     **Tip:** Keep Suspense boundaries close to slow UI regions so users see meaningful content sooner.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5060)，来源许可：MIT。

<a id="k29f874c022b9"></a>

## What is TestRenderer package in React?

    This package provides a renderer that can be used to render components to pure JavaScript objects, without depending on the DOM or a native mobile environment. This package makes it easy to grab a snapshot of the platform view hierarchy (similar to a DOM tree) rendered by a ReactDOM or React Native without using a browser or `jsdom`.

```jsx harmony
    import TestRenderer from "react-test-renderer";

    const Link = ({ page, children }) => <a href={page}>{children}</a>;

    const testRenderer = TestRenderer.create(
      <Link page={"https://www.facebook.com/"}>{"Facebook"}</Link>
    );

    console.log(testRenderer.toJSON());
    // {
    //   type: 'a',
    //   props: { href: 'https://www.facebook.com/' },
    //   children: [ 'Facebook' ]
    // }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3171)，来源许可：MIT。

<a id="kc540319f5b39"></a>

## What is the behavior of uncaught errors in react 16?

     **Note:** This behavior was introduced in React 16 and continues in React 18/19.

     In React 16+, errors that are not caught by any error boundary will result in unmounting of the whole React component tree. The reason behind this decision is that it is worse to leave corrupted UI in place than to completely remove it. For example, it is worse for a payments app to display a wrong amount than to render nothing.

     **Best Practice:** Always wrap your application or critical sections in error boundaries to prevent complete unmounting and provide a better user experience.

```jsx
     <ErrorBoundary fallback={<ErrorPage />}>
       <App />
     </ErrorBoundary>
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4610)，来源许可：MIT。

<a id="k20cd8bca06bd"></a>

## What is the benefit of component stack trace from error boundary?

     Apart from error messages and javascript stack, React16 will display the component stack trace with file names and line numbers using error boundary concept.

     For example, BuggyCounter component displays the component stack trace as below,

     ![stacktrace](https://raw.githubusercontent.com/sudheerj/reactjs-interview-questions/55b7d491cd74c7b37f9352f3b2420d66e7187951/images/error_boundary.png)

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4632)，来源许可：MIT。

<a id="k0e94b36dd059"></a>

## What is the browser support for react applications?

     React supports all popular browsers, including Internet Explorer 9 and above, although some polyfills are required for older browsers such as IE 9 and IE 10. If you use **es5-shim and es5-sham** polyfill then it even support old browsers that doesn't support ES5 methods.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4693)，来源许可：MIT。

<a id="k4e6cfc34a8b5"></a>

## What is the difference between an Element and a Component?

  **Element:**
  - A React **Element** is a plain JavaScript object that describes what you want to see on the UI. It represents a DOM node or a component at a specific point in time. 
  - Elements are immutable: once created, you cannot change their properties. Instead, you create new elements to reflect updates.
  - Elements can be nested within other elements through their `props`.
  - Creating an element is a fast, lightweight operation—it does **not** create any actual DOM nodes or render anything to the screen directly.

    **Example (without JSX):**
```js
    const element = React.createElement("button", { id: "login-btn" }, "Login");
```

    **Equivalent JSX syntax:**
```jsx
    <button id="login-btn">Login</button>
```

    **The object returned by `React.createElement`:**
```js
    {
      type: 'button',
      props: {
        id: 'login-btn',
        children: 'Login'
      }
    }
```
    Elements are then passed to the React DOM renderer (e.g., `ReactDOM.render()`), which translates them to actual DOM nodes.

    ---

  **Component:**
  - A **Component** is a function or class that returns an element (or a tree of elements) to describe part of the UI. Components can accept inputs (called **props**) and manage their own state (in case of class or function components with hooks).
  - Components allow you to split the UI into independent, reusable pieces, each isolated and composable.
  - You can define a component using a function or a class:

    **Example (Function Component with JSX):**
```jsx
    const Button = ({ handleLogin }) => (
      <button id="login-btn" onClick={handleLogin}>
        Login
      </button>
    );
```

    When JSX is compiled, it's transformed into a tree of `React.createElement` calls:

```js
    const Button = ({ handleLogin }) =>
      React.createElement(
        "button",
        { id: "login-btn", onClick: handleLogin },
        "Login"
      );
```

  **In summary:**
  - **Elements** are the smallest building blocks in React—objects that describe what you want to see.
  - **Components** are functions or classes that return elements and encapsulate logic, structure, and behavior for parts of your UI.

   > Think of **elements** as the instructions for creating UI, and **components** as reusable blueprints that combine logic and structure to generate those instructions.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L660)，来源许可：MIT。

<a id="kee5edf2f5fd7"></a>

## What is the difference between component and container in React Redux?

     **Component** is a class or function component that describes the presentational part of your application.

     **Container** is an informal term for a component that is connected to a Redux store. Containers _subscribe_ to Redux state updates and _dispatch_ actions, and they usually don't render DOM elements; they delegate rendering to presentational child components.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3556)，来源许可：MIT。

<a id="kb3febd087a59"></a>

## What is the difference between HOCs and Hooks?

     Both **Higher-Order Components (HOCs)** and **Hooks** let you reuse logic across components, but they solve that problem in very different ways.

     | Aspect | Higher-Order Components (HOCs) | Hooks |
     | --- | --- | --- |
     | Pattern | A function that takes a component and returns a new, enhanced component | A function called directly inside a function component |
     | Component tree | Adds an extra wrapper component, which can lead to "wrapper hell" with multiple HOCs | Adds no extra components to the tree |
     | Sharing logic | Injects props/behavior into the wrapped component | Shares stateful logic directly via custom hooks (`useX`) |
     | Prop handling | Can cause prop name collisions when composing multiple HOCs | No prop collisions since state lives inside the component itself |
     | Debugging | Harder to trace which HOC injected which prop (often needs `displayName`) | Easier to trace; shows up as plain hook calls in React DevTools |
     | Usage | Works with both class and function components | Can only be used in function components (or other hooks) |

     #### Example: sharing "toggle" logic

     **Using a HOC:**

```jsx
     function withToggle(WrappedComponent) {
       return function Enhanced(props) {
         const [on, setOn] = useState(false);
         const toggle = () => setOn((prev) => !prev);
         return <WrappedComponent {...props} on={on} toggle={toggle} />;
       };
     }

     const Modal = withToggle(BaseModal);
```

     **Using a custom Hook:**

```jsx
     function useToggle(initial = false) {
       const [on, setOn] = useState(initial);
       const toggle = () => setOn((prev) => !prev);
       return [on, toggle];
     }

     function Modal() {
       const [on, toggle] = useToggle();
       // ...
     }
```

     In short, Hooks were introduced to solve the same logic-reuse problem as HOCs (and render props), but without adding extra components to the render tree—avoiding wrapper hell and making the code easier to read, type, and debug. See also [Do Hooks replace render props and higher-order components?](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#do-hooks-replace-render-props-and-higher-order-components).

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L9398)，来源许可：MIT。

<a id="kd4e307edb281"></a>

## What is the difference between HTML and React event handling?

Below are some of the main differences between HTML and React event handling,

1. In HTML, the event name usually represents in _lowercase_ as a convention:

```html
   <button onclick="activateLasers()"></button>
```

   Whereas in React it follows _camelCase_ convention:

```jsx harmony
   <button onClick={activateLasers}>
```

2. In HTML, you can return `false` to prevent default behavior:

```html
   <a
     href="#"
     onclick='console.log("The link was clicked."); return false;'
   />
```

   Whereas in React you must call `preventDefault()` explicitly:

```javascript
   function handleClick(event) {
     event.preventDefault();
     console.log("The link was clicked.");
   }
```

3. In HTML, you need to invoke the function by appending `()`
   Whereas in react you should not append `()` with the function name. (refer "activateLasers" function in the first point for example)

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1039)，来源许可：MIT。

<a id="k9685d4530329"></a>

## What is the difference between Imperative and Declarative in React?

     Imagine a simple UI component, such as a "Like" button. When you tap it, it turns blue if it was previously grey, and grey if it was previously blue.

     The imperative way of doing this would be:

```javascript
     if (user.likes()) {
       if (hasBlue()) {
         removeBlue();
         addGrey();
       } else {
         removeGrey();
         addBlue();
       }
     }
```

     Basically, you have to check what is currently on the screen and handle all the changes necessary to redraw it with the current state, including undoing the changes from the previous state. You can imagine how complex this could be in a real-world scenario.

     In contrast, the declarative approach would be:

```javascript
     if (this.state.liked) {
       return <blueLike />;
     } else {
       return <greyLike />;
     }
```

     Because the declarative approach separates concerns, this part of it only needs to handle how the UI should look in a specific state, and is therefore much simpler to understand.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5679)，来源许可：MIT。

<a id="k056ae5ed87c4"></a>

## What is the difference between mapStateToProps() and mapDispatchToProps()?

     `mapStateToProps()` is a utility which helps your component get updated state (which is updated by some other components):

```javascript
     const mapStateToProps = (state) => {
       return {
         todos: getVisibleTodos(state.todos, state.visibilityFilter),
       };
     };
```

     `mapDispatchToProps()` is a utility which will help your component to fire an action event (dispatching action which may cause change of application state):

```javascript
     const mapDispatchToProps = (dispatch) => {
       return {
         onTodoClick: (id) => {
           dispatch(toggleTodo(id));
         },
       };
     };
```

     It is recommended to always use the “object shorthand” form for the `mapDispatchToProps`.

     Redux wraps it in another function that looks like (…args) => dispatch(onTodoClick(…args)), and pass that wrapper function as a prop to your component.

```javascript
     const mapDispatchToProps = {
       onTodoClick,
     };
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3340)，来源许可：MIT。

<a id="k3b373d652d7b"></a>

## What is the difference between React and Angular?

     Let's see the difference between React and Angular in a table format.

     | React                                                                                       | Angular                                                                                                                            |
     | ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
     | React is a library and has only the View layer                                              | Angular is a framework and has complete MVC functionality                                                                          |
     | React handles rendering on the server side                                                  | AngularJS renders only on the client side but Angular 2 and above renders on the server side                                       |
     | React uses JSX that looks like HTML in JS which can be confusing                            | Angular follows the template approach for HTML, which makes code shorter and easy to understand                                    |
     | React Native, which is a React type to build mobile applications are faster and more stable | Ionic, Angular's mobile native app is relatively less stable and slower                                                            |
     | In React, data flows only in one way and hence debugging is easy                            | In Angular, data flows both way i.e it has two-way data binding between children and parent and hence debugging is often difficult |

**Note:** The above list of differences are purely opinionated and it vary based on the professional experience. But they are helpful as base parameters.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3997)，来源许可：MIT。

<a id="k35b642933d29"></a>

## What is the difference between React and ReactDOM?

The `react` package contains `React.createElement()`, `React.Component`, `React.Children`, and other helpers related to elements and component classes. You can think of these as the isomorphic or universal helpers that you need to build components. The `react-dom` package contains `ReactDOM.render()`, and in `react-dom/server` we have _server-side rendering_ support with `ReactDOMServer.renderToString()` and `ReactDOMServer.renderToStaticMarkup()`.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L2311)，来源许可：MIT。

<a id="k0ae65c37d570"></a>

## What is the difference between React context and React Redux?

     You can use **Context** in your application directly and is going to be great for passing down data to deeply nested components which what it was designed for.

     Whereas **Redux** is much more powerful and provides a large number of features that the Context API doesn't provide. Also, React Redux uses context internally but it doesn't expose this fact in the public API.

     | Aspect | Context API | Redux |
     | --- | --- | --- |
     | Purpose | Dependency injection — passes data through the tree without prop drilling | Full state-management library with a predictable, centralized store |
     | State updates | Plain `useState`/`useReducer` next to the provider; no built-in middleware | Actions + reducers, with middleware support (`redux-thunk`, `redux-saga`, etc.) |
     | Performance | Every consumer re-renders on any value change unless you split contexts/memoize | Uses selectors (`useSelector`/`connect`) so components only re-render when the selected slice changes |
     | DevTools | None built-in | Time-travel debugging, action logs via Redux DevTools |
     | Async logic | You wire it yourself (custom hooks, effects) | Standardized patterns via middleware |
     | Boilerplate | Minimal — just `createContext`/`useContext` | More setup, though Redux Toolkit reduces this significantly |

     #### Does Context replace Redux?

     Not entirely — they solve overlapping but different problems, so the right choice depends on the app's needs:

     - **Context is a good fit** for low-frequency, mostly-static data that many components need (theme, locale, authenticated user, feature flags). Combined with `useReducer`, it can even model simple local/global state without pulling in Redux (see [Can you combine useReducer with useContext?](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#can-you-combine-usereducer-with-usecontext)).
     - **Redux is still preferable** for large apps with complex, frequently-updating state, cross-cutting concerns like caching/undo/logging, a need for middleware (async flows, side effects), or debugging tools like time-travel and action replay.
     - **Performance matters**: Context has no built-in mechanism to prevent unnecessary re-renders of all consumers when the provided value changes, whereas Redux's `useSelector` re-renders only the components that depend on the changed slice of state.

     In short, Context is a simpler tool for prop-drilling/dependency-injection use cases, while Redux remains a more robust, scalable option for complex application-wide state management. Many apps use both together — Context for simple, rarely-changing values and Redux (or another store) for the rest.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3453)，来源许可：MIT。

<a id="k25b9b804b375"></a>

## What is the difference between React Native and React?

     **React** is a JavaScript library, supporting both front end web and being run on the server, for building user interfaces and web applications.

     **React Native** is a mobile framework that compiles to native app components, allowing you to build native mobile applications (iOS, Android, and Windows) in JavaScript that allows you to use React to build your components, and implements React under the hood.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3841)，来源许可：MIT。

<a id="kec86a9287aa4"></a>

## What is the difference between super() and super(props) in React using ES6 classes?

When you want to access `this.props` in `constructor()` then you should pass props to `super()` method.

**Using `super(props)`:**

```javascript
class MyComponent extends React.Component {
  constructor(props) {
    super(props);
    console.log(this.props); // { name: 'John', ... }
  }
}
```

**Using `super()`:**

```javascript
class MyComponent extends React.Component {
  constructor(props) {
    super();
    console.log(this.props); // undefined
  }
}
```

Outside `constructor()` both will display same value for `this.props`.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11310)，来源许可：MIT。

<a id="k28b1bc8624f9"></a>

## What is the difference between useState and useRef hook?

     1. useState causes components to re-render after state updates whereas useRef doesn’t cause a component to re-render when the value or state changes.
        Essentially, useRef is like a “box” that can hold a mutable value in its (`.current`) property.
     2. useState allows us to update the state inside components. While useRef allows referencing DOM elements and tracking values.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5868)，来源许可：MIT。

<a id="k513b9f1e25bf"></a>

## What is the history behind React evolution?

The history of ReactJS started in 2010 with the creation of **XHP**. XHP is a PHP extension which improved the syntax of the language such that XML document fragments become valid PHP expressions and the primary purpose was used to create custom and reusable HTML elements.

The main principle of this extension was to make front-end code easier to understand and to help avoid cross-site scripting attacks. The project was successful to prevent the malicious content submitted by the scrubbing user.

But there was a different problem with XHP in which dynamic web applications require many roundtrips to the server, and XHP did not solve this problem. Also, the whole UI was re-rendered for small change in the application. Later, the initial prototype of React is created with the name **FaxJ** by Jordan inspired from XHP. Finally after sometime React has been introduced as a new library into JavaScript world.

    <summary><b>See deep-dive answer</b></summary>
    The evolution of React has a fascinating history that spans over a decade:

**2010-2011: The Origins**
- The journey began with **XHP**, a PHP extension created at Facebook that allowed HTML components to be used in PHP code
- XHP improved front-end code readability and helped prevent cross-site scripting (XSS) attacks
- However, XHP had limitations with dynamic web applications, requiring frequent server roundtrips and complete UI re-renders for small changes

**2011-2012: Early Development**
- Jordan Walke created the first prototype called **FaxJS** (later renamed to React), inspired by XHP's component model
- The key innovation was bringing XHP's component model to JavaScript with performance improvements
- React introduced the Virtual DOM concept to solve the performance issues of full page re-renders
- First deployed internally on Facebook's News Feed in 2011 and Instagram in 2012

**2013: Public Release**
- React was officially open-sourced at JSConf US in May 2013
- Initial public reception was mixed, with some developers skeptical about the JSX syntax and the approach of mixing markup with JavaScript

**2014-2015: Growing Adoption**
- React Native was announced in 2015, extending React's paradigm to mobile app development
- The ecosystem began to grow with tools like Redux for state management
- Companies beyond Facebook began adopting React for production applications

**2016-2018: Maturation**
- React 16 ("Fiber") was released in 2017 with a complete rewrite of the core architecture
- Introduction of new features like Error Boundaries, Portals, and improved server-side rendering
- React 16.3 introduced the Context API for easier state management

**2019-Present: Modern React**
- React Hooks were introduced in React 16.8 (February 2019), revolutionizing state management in functional components
- React 17 (October 2020) focused on making React upgrades easier
- React 18 (March 2022) introduced concurrent rendering and automatic batching
- React continues to evolve with Server Components, the new React compiler (React Forget), and other performance improvements

**Note:** JSX, React's syntax extension, was indeed inspired by XHP's approach of embedding XML-like syntax in code.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L533)，来源许可：MIT。

<a id="k729dfb6516ed"></a>

## What is the main goal of React Fiber?

The goal of _React Fiber_ is to increase its suitability for areas like animation, layout, and gestures. Its headline feature is **incremental rendering**: the ability to split rendering work into chunks and spread it out over multiple frames.

Its main goals are:

*   **Incremental Rendering** – Breaks work into chunks for smoother updates.
*   **Interruptible Rendering** – Pauses and resumes rendering to keep the UI responsive.
*   **Prioritization** – Handles high-priority updates (e.g. animations) before low-priority ones.
*   **Concurrency Support** – Enables working on multiple UI versions simultaneously.
*   **Better Error Handling** – Supports component-level error boundaries.
*   **Suspense Support** – Allows waiting for async data before rendering.
*   **Improved DevTools** – Enables better debugging and performance tracking.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1214)，来源许可：MIT。

<a id="kb028a3154ce1"></a>

## What is the mental model of redux-saga?

     _Saga_ is like a separate thread in your application, that's solely responsible for side effects. `redux-saga` is a redux _middleware_, which means this thread can be started, paused and cancelled from the main application with normal Redux actions, it has access to the full Redux application state and it can dispatch Redux actions as well.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3692)，来源许可：MIT。

<a id="k9de4d8867ac9"></a>

## What is the methods order when component re-rendered?

    An update can be caused by changes to props or state. The below methods are called in the following order when a component is being re-rendered.

    1.  static getDerivedStateFromProps()
    2.  shouldComponentUpdate()
    3.  render()
    4.  getSnapshotBeforeUpdate()
    5.  componentDidUpdate()

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12137)，来源许可：MIT。

<a id="kddd461f75de4"></a>

## What is the proper way to access Redux store?

     The best way to access your store in a component is to use the `connect()` function, that creates a new component that wraps around your existing one. This pattern is called _Higher-Order Components_, and is generally the preferred way of extending a component's functionality in React. This allows you to map state and action creators to your component, and have them passed in automatically as your store updates.

     Let's take an example of `<FilterLink>` component using connect:

```javascript
     import { connect } from "react-redux";
     import { setVisibilityFilter } from "../actions";
     import Link from "../components/Link";

     const mapStateToProps = (state, ownProps) => ({
       active: ownProps.filter === state.visibilityFilter,
     });

     const mapDispatchToProps = (dispatch, ownProps) => ({
       onClick: () => dispatch(setVisibilityFilter(ownProps.filter)),
     });

     const FilterLink = connect(mapStateToProps, mapDispatchToProps)(Link);

     export default FilterLink;
```

     Due to it having quite a few performance optimizations and generally being less likely to cause bugs, the Redux developers almost always recommend using `connect()` over accessing the store directly (using context API).

```javascript
     function MyComponent {
       someMethod() {
         doSomethingWith(this.context.store);
       }
     }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3520)，来源许可：MIT。

<a id="k836fa0e37009"></a>

## What is the purpose of default value in context?

     The defaultValue argument is only used when a component does not have a matching Provider above it in the tree. This can be helpful for testing components in isolation without wrapping them.

     Below code snippet provides default theme value as Luna.

```javascript
     const MyContext = React.createContext(defaultValue);
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5162)，来源许可：MIT。

<a id="k1d314fbe6579"></a>

## What is the purpose of eslint plugin for hooks?

     The ESLint plugin enforces rules of Hooks to avoid bugs. It assumes that any function starting with ”use” and a capital letter right after it is a Hook. In particular, the rule enforces that,

     1. Calls to Hooks are either inside a PascalCase function (assumed to be a component) or another useSomething function (assumed to be a custom Hook).
     2. Hooks are called in the same order on every render.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5670)，来源许可：MIT。

<a id="k13d9a9ef5bd7"></a>

## What is the purpose of getDerivedStateFromProps() lifecycle method?

The new static `getDerivedStateFromProps()` lifecycle method is invoked after a component is instantiated as well as before it is re-rendered. It can return an object to update state, or `null` to indicate that the new props do not require any state updates.

```javascript
class MyComponent extends React.Component {
  static getDerivedStateFromProps(props, state) {
    // ...
  }
}
```

This lifecycle method along with `componentDidUpdate()` covers all the use cases of `componentWillReceiveProps()`.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11115)，来源许可：MIT。

<a id="k1b33becfac27"></a>

## What is the purpose of ReactTestUtils package?

    _ReactTestUtils_ are provided in the `with-addons` package and allow you to perform actions against a simulated DOM for the purpose of unit testing.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3194)，来源许可：MIT。

<a id="k979921c2bff6"></a>

## What is the purpose of registerServiceWorker in React?

     React creates a service worker for you without any configuration by default. The service worker is a web API that helps you cache your assets and other files so that when the user is offline or on a slow network, he/she can still see results on the screen, as such, it helps you build a better user experience, that's what you should know about service worker for now. It's all about adding offline capabilities to your site.

```jsx
     import React from "react";
     import ReactDOM from "react-dom";
     import App from "./App";
     import registerServiceWorker from "./registerServiceWorker";

     ReactDOM.render(<App />, document.getElementById("root"));
     registerServiceWorker();
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L4224)，来源许可：MIT。

<a id="k973eafb98280"></a>

## What is the purpose of render method of react-dom?

This method is used to render a React element into the DOM in the supplied container and return a reference to the component. If the React element was previously rendered into container, it will perform an update on it and only mutate the DOM as necessary to reflect the latest changes.

```
ReactDOM.render(element, container, [callback])
```

If the optional callback is provided, it will be executed after the component is rendered or updated.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10886)，来源许可：MIT。

<a id="ka4d49595cbaa"></a>

## What is the purpose of the constants in Redux?

     Constants allows you to easily find all usages of that specific functionality across the project when you use an IDE. It also prevents you from introducing silly bugs caused by typos – in which case, you will get a `ReferenceError` immediately.

     Normally we will save them in a single file (`constants.js` or `actionTypes.js`).

```javascript
     export const ADD_TODO = "ADD_TODO";
     export const DELETE_TODO = "DELETE_TODO";
     export const EDIT_TODO = "EDIT_TODO";
     export const COMPLETE_TODO = "COMPLETE_TODO";
     export const COMPLETE_ALL = "COMPLETE_ALL";
     export const CLEAR_COMPLETED = "CLEAR_COMPLETED";
```

     In Redux, you use them in two places:

     1. **During action creation:**

        Let's take `actions.js`:

```javascript
        import { ADD_TODO } from "./actionTypes";

        export function addTodo(text) {
          return { type: ADD_TODO, text };
        }
```

     2. **In reducers:**

        Let's create `reducer.js`:

```javascript
        import { ADD_TODO } from "./actionTypes";

        export default (state = [], action) => {
          switch (action.type) {
            case ADD_TODO:
              return [
                ...state,
                {
                  text: action.text,
                  completed: false,
                },
              ];
            default:
              return state;
          }
        };
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3564)，来源许可：MIT。

<a id="kc734251778fc"></a>

## What is the purpose of unmountComponentAtNode method?

    This method is available from react-dom package and it removes a mounted React component from the DOM and clean up its event handlers and state. If no component was mounted in the container, calling this function does nothing. Returns true if a component was unmounted and false if there was no component to unmount.

    The method signature would be as follows,

```javascript
    ReactDOM.unmountComponentAtNode(container);
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12158)，来源许可：MIT。

<a id="k99e363a281aa"></a>

## What is the purpose of using super constructor with props argument?

A child class constructor cannot make use of `this` reference until the `super()` method has been called. The same applies to ES6 sub-classes as well. The main reason for passing props parameter to `super()` call is to access `this.props` in your child constructors.

**Passing props:**

```javascript
class MyComponent extends React.Component {
  constructor(props) {
    super(props);

    console.log(this.props); // prints { name: 'John', age: 42 }
  }
}
```

**Not passing props:**

```javascript
class MyComponent extends React.Component {
  constructor(props) {
    super();

    console.log(this.props); // prints undefined

    // but props parameter is still available
    console.log(props); // prints { name: 'John', age: 42 }
  }

  render() {
    // no difference outside constructor
    console.log(this.props); // prints { name: 'John', age: 42 }
  }
}
```

The above code snippets reveals that `this.props` is different only within the constructor. It would be the same outside the constructor.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L10749)，来源许可：MIT。

<a id="ke266dadcdee1"></a>

## What is the React Compiler (React Forget)?

     The **React Compiler** (formerly known as React Forget) automatically optimizes your components by adding memoization where needed - eliminating the need for manual `useMemo`, `useCallback`, and `React.memo`.

     #### Before React Compiler
```jsx
     function TodoList({ todos, filter }) {
       // Manual optimization needed
       const filteredTodos = useMemo(() => {
         return todos.filter(todo => todo.status === filter);
       }, [todos, filter]);

       const handleToggle = useCallback((id) => {
         toggleTodo(id);
       }, [toggleTodo]);

       return (
         <div>
           {filteredTodos.map(todo => (
             <TodoItem 
               key={todo.id} 
               todo={todo} 
               onToggle={handleToggle} 
             />
           ))}
         </div>
       );
     }

     // Need to wrap in React.memo
     export default React.memo(TodoList);
```

     #### With React Compiler
```jsx
     function TodoList({ todos, filter }) {
       // Compiler automatically optimizes this!
       const filteredTodos = todos.filter(todo => todo.status === filter);

       const handleToggle = (id) => {
         toggleTodo(id);
       };

       return (
         <div>
           {filteredTodos.map(todo => (
             <TodoItem 
               key={todo.id} 
               todo={todo} 
               onToggle={handleToggle} 
             />
           ))}
         </div>
       );
     }

     // No React.memo needed!
     export default TodoList;
```

     #### How It Works
     1. **Analyzes code** during build time
     2. **Identifies expensive calculations** and renders
     3. **Automatically inserts memoization** where beneficial
     4. **Preserves React semantics** - your code still behaves correctly

     #### Benefits
     - ✅ Simpler code - no manual optimization
     - ✅ Better performance by default
     - ✅ Fewer bugs from incorrect dependencies
     - ✅ Easier to maintain and read
     - ✅ Works with existing code

     #### Enabling React Compiler
```jsx
     // next.config.js (Next.js)
     module.exports = {
       experimental: {
         reactCompiler: true
       }
     }

     // vite.config.js (Vite)
     import { defineConfig } from 'vite'
     import react from '@vitejs/plugin-react'

     export default defineConfig({
       plugins: [
         react({
           babel: {
             plugins: [['babel-plugin-react-compiler']]
           }
         })
       ]
     })
```

     #### When to Still Use Manual Optimization
```jsx
     // For external libraries without Compiler support
     import { expensiveLibFunction } from 'old-library';

     function MyComponent() {
       // May still need manual memoization here
       const result = useMemo(() => expensiveLibFunction(), []);
       return <div>{result}</div>;
     }
```

     #### Compatibility
     - Works with React 18.3+ and React 19
     - Compatible with TypeScript
     - Works with all React hooks
     - Supports Server Components and Client Components

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L9078)，来源许可：MIT。

<a id="k2de2b98afafa"></a>

## What is the reason behind multiple JSX tags to be wrapped?

      Behind the scenes, JSX is transformed into plain javascript objects. It is not possible to return two or more objects from a function without wrapping into an array. This is the reason you can't simply return two or more JSX tags from a function without
      wrapping them into a single parent tag or a Fragment.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6180)，来源许可：MIT。

<a id="k10dfe1d10170"></a>

## What is the recommended approach of removing an array element in React state?

    The better approach is to use `Array.prototype.filter()` method.

    For example, let's create a `removeItem()` method for updating the state.

```javascript
    removeItem(index) {
      this.setState({
        data: this.state.data.filter((item, i) => i !== index)
      })
    }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11358)，来源许可：MIT。

<a id="k5079521bb23a"></a>

## What is the recommended ordering of methods in component class?

_Recommended_ ordering of methods from _mounting_ to _render stage_:

1. `static` methods
2. `constructor()`
3. `getChildContext()`
4. `componentWillMount()`
5. `componentDidMount()`
6. `componentWillReceiveProps()`
7. `shouldComponentUpdate()`
8. `componentWillUpdate()`
9. `componentDidUpdate()`
10. `componentWillUnmount()`
11. click handlers or event handlers like `onClickSubmit()` or `onChangeDescription()`
12. getter methods for render like `getSelectReason()` or `getFooterContent()`
13. optional render methods like `renderNavigation()` or `renderProfilePicture()`
14. `render()`

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11179)，来源许可：MIT。

<a id="ke032ba6a2bd0"></a>

## What is the recommended way for naming components?

It is recommended to name the component by reference instead of using `displayName`.

Using `displayName` for naming component:

```javascript
export default React.createClass({
  displayName: "TodoApp",
  // ...
});
```

The **recommended** approach:

```javascript
export default class TodoApp extends React.Component {
  // ...
}
```

also

```javascript
const TodoApp = () => {
  //...
};
export default TodoApp;
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L11147)，来源许可：MIT。

<a id="k93784cd332ce"></a>

## What is the Redux middleware signature?

     Middleware is written as **three nested (curried) functions**:

```javascript
     const exampleMiddleware = (store) => (next) => (action) => {
       // store  => { getState, dispatch }
       // next   => calls the next middleware in the chain (or the reducer if last)
       // action => the action currently being dispatched
       return next(action);
     };
```

     - `store` gives access to `getState()` and `dispatch()`.
     - `next` passes the action along to the next middleware (or the root reducer, if this is the last middleware).
     - `action` is the action object being processed.

     Middleware **must** call `next(action)` (or `dispatch(...)` for a different action) to keep the chain moving — forgetting to call `next` silently swallows every action.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L9782)，来源许可：MIT。

<a id="kbf82caf7c3bf"></a>

## What is the required method to be defined for a class component?

    The `render()` method is the only required method in a class component. i.e, All methods other than render method are optional for a class component.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L12054)，来源许可：MIT。

<a id="kd4ae12d5a512"></a>

## What is the stable release for hooks support?

     React includes a stable implementation of React Hooks in 16.8 release for below packages

     1. React DOM
     2. React DOM Server
     3. React Test Renderer
     4. React Shallow Renderer

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5482)，来源许可：MIT。

<a id="k8ba51a6ac685"></a>

## What is the use of react-dom package?

The `react-dom` package provides _DOM-specific methods_ that can be used at the top level of your app. Most of the components are not required to use this module. Some of the methods of this package are:

1. `render()`
2. `hydrate()`
3. `unmountComponentAtNode()`
4. `findDOMNode()`
5. `createPortal()`

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L1900)，来源许可：MIT。

<a id="k711b7ea8d82f"></a>

## What is the use of the ownProps parameter in mapStateToProps() and mapDispatchToProps()?

     If the `ownProps` parameter is specified, React Redux will pass the props that were passed to the component into your _connect_ functions. So, if you use a connected component:

```jsx harmony
     import ConnectedComponent from "./containers/ConnectedComponent";

     <ConnectedComponent user={"john"} />;
```

     The `ownProps` inside your `mapStateToProps()` and `mapDispatchToProps()` functions will be an object:

```javascript
     {
       user: "john";
     }
```

     You can use this object to decide what to return from those functions.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L3644)，来源许可：MIT。

<a id="kb6ce90ce60ec"></a>

## What is the use() hook in React 19?

     The `use()` hook allows you to read the value of a resource (Promise or Context) during render, with Suspense integration.

     #### Reading Promises
```jsx
     import { use, Suspense } from 'react';

     function UserProfile({ userPromise }) {
       const user = use(userPromise); // Suspends until resolved

       return (
         <div>
           <h1>{user.name}</h1>
           <p>{user.email}</p>
         </div>
       );
     }

     function App() {
       const userPromise = fetchUser(123);

       return (
         <Suspense fallback={<div>Loading...</div>}>
           <UserProfile userPromise={userPromise} />
         </Suspense>
       );
     }
```

     #### Reading Context
```jsx
     import { use } from 'react';
     import { ThemeContext } from './context';

     function Button() {
       const theme = use(ThemeContext);
       return <button className={theme}>Click me</button>;
     }
```

     #### Key Differences from Other Hooks

     | Feature | use() | useContext() | useState() |
     |---------|-------|--------------|------------|
     | Can be called conditionally | ✅ Yes | ❌ No | ❌ No |
     | Can be called in loops | ✅ Yes | ❌ No | ❌ No |
     | Suspends for Promises | ✅ Yes | ❌ N/A | ❌ N/A |
     | Reads Context | ✅ Yes | ✅ Yes | ❌ N/A |

     #### Conditional Usage (Unique!)
```jsx
     function Component({ showUser, userPromise }) {
       // ✅ This is allowed with use()!
       const user = showUser ? use(userPromise) : null;

       return user ? <div>{user.name}</div> : <div>No user</div>;
     }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L8728)，来源许可：MIT。

<a id="k0baf36d8afff"></a>

## What is useContext? What are the steps to follow for useContext?

     The `useContext` hook is a built-in React Hook that lets you access the value of a context inside a functional component without needing to wrap it in a <Context.Consumer> component.

     It helps you **avoid prop drilling** (passing props through multiple levels) by allowing components to access shared data like themes, authentication status, or user preferences.

     The usage of useContext involves three main steps:
      #### **Step 1 : Create the Context**

        Use `React.createContext()` to create a context object.

```jsx
        import React, { createContext } from 'react'; 

        const ThemeContext = createContext(); // default value optional
```

      You typically export this so other components can import it.

      #### **Step 2: Provide the Context Value**

        Wrap your component tree (or a part of it) with the `Context.Provider` and pass a `value` prop.

```jsx
        function App() {
            return ( 
                <ThemeContext.Provider value="dark">
                   <MyComponent />
                </ThemeContext.Provider>
            ); 
        }
```

        Now any component inside `<ThemeContext.Provider>` can access the context value.

        #### **Step 3: Consume the Context with** `**useContext**`

        In any functional component **inside the Provider**, use the `useContext` hook:

```jsx
        import { useContext } from 'react'; 
        function MyComponent() {
            const theme = useContext(ThemeContext); // theme = "dark"
            return <p>Current Theme: {theme}</p>; 
        }
```

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L6640)，来源许可：MIT。

<a id="kf91f5aa44a0e"></a>

## What is your favorite React stack?

     Even though the tech stack varies from developer to developer, the most popular stack is used in react boilerplate project code. It mainly uses Redux and redux-saga for state management and asynchronous side-effects, react-router for routing purpose, styled-components for styling react components, axios for invoking REST api, and other supported stack such as webpack, reselect, ESNext, Babel.
     You can clone the project https://github.com/react-boilerplate/react-boilerplate and start working on any new react project.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5360)，来源许可：MIT。
