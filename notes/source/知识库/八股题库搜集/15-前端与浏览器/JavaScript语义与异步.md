# JavaScript语义与异步

<a id="kc3cf22eed73a"></a>

## addEventListener 用法？和 onxxx 的区别是什么？

onxxx 是 DOM0 的标准，所有浏览器支持，它会直接在 DOM 对象上注册事件名称。
例如：

```javascript
document.getElementById('click').onclick = function (event) {
  console.log(event.target)
}
```

addEventListener 是 DOM2 的标准，IE8 以上浏览器支持，它分为三个阶段：捕获阶段，目标阶段，冒泡阶段。
每个事件都会先由根传到目标元素，再传回根。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/JavaScript/javascript-fundamentals.md#L422)，来源许可：GPL-3.0。

<a id="k0995689f10cc"></a>

## Coding questions

* Make this work:
```javascript
duplicate([1,2,3,4,5]); // [1,2,3,4,5,1,2,3,4,5]
```
* Create a for loop that iterates up to `100` while outputting **"fizz"** at multiples of `3`, **"buzz"** at multiples of `5` and **"fizzbuzz"** at multiples of `3` and `5`
* What will be returned by each of these?
```javascript
console.log("hello" || "world")
console.log("foo" && "bar")
```
* Write an immediately invoked function expression (IIFE)

### 参考资料

- [h5bp/Front-end-Developer-Interview-Questions](https://github.com/h5bp/Front-end-Developer-Interview-Questions/blob/33f5498b653e7ae061ee5a65a0b44e9ab860502c/src/questions/javascript-questions.md#L61)，来源许可：MIT。

<a id="k4563064123c1"></a>

## es6 模块化、commonjs 模块化的区别？

es6 模块化：

```
在es6规范中，使用import和export可以使js文件模块化。
每个import的js文件都是单例，如果再次import，就直接在内存中进行读取。

导出方式1：
//lib.js 文件
let foo = "stringFoo";
let fn0 = function() {
    console.log("fn0");
};
export{foo, fn}

//main.js文件
import {foo, fn} from "./lib";
console.log(bar+"_"+foo);

```

commonjs 模块化：

```
Node 应用由模块组成，采用 CommonJS 模块规范。

每个文件就是一个模块，有自己的作用域。在一个文件里面定义的变量、函数、类，都是私有的，对其他文件不可见。如果要定义全局变量，需要global属性。

CommonJS规范规定，每个模块内部，module变量代表当前模块。
这个变量是一个对象，它的exports属性（即module.exports）是对外的接口。加载某个模块，其实是加载该模块的module.exports属性。
为了方便，Node为每个模块提供一个exports变量，指向module.exports。

例如：
var test = function () {
	console.log(123);
};
module.exports.test = test;

使用require('XXX')加载模块。
require命令的基本功能是，读入并执行一个JavaScript文件，然后返回该模块的exports对象。如果没有发现指定模块，会报错。
```

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/JavaScript/NodeJS.md#L133)，来源许可：GPL-3.0。

<a id="kbce781f6169a"></a>

## Everything in JavaScript is either a...

- A: primitive or object
- B: function or object
- C: trick question! only objects
- D: number or object

Answer
<p>

### 参考资料

- [lydiahallie/javascript-questions](https://github.com/lydiahallie/javascript-questions/blob/a8b427b9f7f94f1a2965144ba544b475c5f65829/README.md#L1214)，来源许可：MIT。

<a id="kefdbea300321"></a>

## Go 对比 Java、V8 中 JavaScript 的 GC 性能如何？

无论是 Java 还是 JavaScript 中的 GC 均为分代式 GC。分代式 GC 的一个核心假设就是分代假说：将对象依据存活时间分配到不同的区域，每次回收只回收其中的一个区域。

### V8 的 GC

在 V8 中主要将内存分为新生代和老生代。新生代中的对象为存活时间较短的对象，老生代中的对象为存活时间较长、常驻内存、占用内存较大的对象：

1. 新生代中的对象主要通过副垃圾回收器进行回收。该回收过程是一种采用复制的方式实现的垃圾回收算法，它将堆内存一分为二，这两个空间中只有一个处于使用中，另一个则处于闲置状态。处于使用状态的空间称为 From 空间，处于闲置的空间称为 To 空间。分配对象时，先是在 From 空间中进行分配，当开始垃圾回收时，会检查 From 空间中的存活对象，并将这些存活对象复制到 To 空间中，而非存活对象占用的空间被释放。完成复制后，From 空间和 To 空间的角色互换。也就是通过将存活对象在两个空间中进行复制。
2. 老生代则由主垃圾回收器负责。它实现的是标记清扫过程，但略有不同之处在于它还会在清扫完成后对内存碎片进行整理，进而是一种标记整理的回收器。

### Java 的 GC

Java 的 GC 称之为 G1，并将整个堆分为年轻代、老年代和永久代。包括四种不同的收集操作，从上往下的这几个阶段会选择性地执行，触发条件是用户的配置和实际代码行为的预测。

1. 年轻代收集周期：只对年轻代对象进行收集与清理
2. 老年代收集周期：只对老年代对象进行收集与清理
3. 混合式收集周期：同时对年轻代和老年代进行收集与清理
4. 完整 GC 周期：完整的对整个堆进行收集与清理

在回收过程中，G1 会对停顿时间进行预测，竭尽所能地调整 GC 的策略从而达到用户代码通过系统参数（`-XX:MaxGCPauseMillis`）所配置的对停顿时间的要求。

这四个周期的执行成本逐渐上升，优化得当的程序可以完全避免完整 GC 周期。

### 性能比较

在 Go、Java 和 V8 JavaScript 之间比较 GC 的性能本质上是一个不切实际的问题。如前面所说，垃圾回收器的设计权衡了很多方面的因素，同时还受语言自身设计的影响，因为语言的设计也直接影响了程序员编写代码的形式，也就自然影响了产生垃圾的方式。

但总的来说，他们三者对垃圾回收的实现都需要 STW，并均已达到了用户代码几乎无法感知到的状态（据 Go GC 作者 Austin 宣称STW 小于 100 微秒 [14]）。当然，随着 STW 的减少，垃圾回收器会增加 CPU 的使用率，这也是程序员在编写代码时需要手动进行优化的部分，即充分考虑内存分配的必要性，减少过多申请内存带给垃圾回收器的压力。

### 参考资料

- [Go Questions](https://github.com/golang-design/go-questions/blob/741cb94826279e6879338565f09b3e71650278f6/content/memgc/4-%E5%8E%86%E5%8F%B2%E5%8F%8A%E6%BC%94%E8%BF%9B.md#L92)，来源许可：GPL-3.0。

<a id="kc8f63e90a1c9"></a>

## Is dispatch from useReducer asynchronous and does it update state immediately?

     The `dispatch` function returned by `useReducer` is **not asynchronous** — it is a **synchronous** function call. When you call `dispatch(action)`, React **synchronously** invokes your reducer with the current state and the action, computes the new state, and **schedules a re-render**. However, the **state variable does not update immediately** within the same render cycle. The updated state is only available in the **next render**.

     This behavior is similar to `useState`'s `setState` — React **batches** state updates for performance optimization, meaning the component does not re-render immediately after each `dispatch` call. Instead, React processes all dispatched actions and re-renders once with the final state.

     #### Key Points

     1. **`dispatch` is synchronous:** The reducer runs immediately when `dispatch` is called.
     2. **State update is not immediate in the current render:** The state variable still holds the old value until the next render.
     3. **React batches updates:** Multiple `dispatch` calls within the same event handler result in a single re-render.
     4. **Reducer is a pure function:** It computes the new state without side effects.

     #### Example demonstrating that state does not update immediately

```jsx
     import React, { useReducer } from 'react';

     function reducer(state, action) {
       switch (action.type) {
         case 'increment':
           return { count: state.count + 1 };
         default:
           return state;
       }
     }

     function Counter() {
       const [state, dispatch] = useReducer(reducer, { count: 0 });

       const handleClick = () => {
         dispatch({ type: 'increment' });
         console.log(state.count); // Still logs the OLD value (e.g., 0), not 1
         dispatch({ type: 'increment' });
         console.log(state.count); // Still logs the OLD value (e.g., 0), not 2
       };

       // After re-render, state.count will be 2 (both dispatches are processed)
       return (
         <div>
           <p>Count: {state.count}</p>
           <button onClick={handleClick}>Increment Twice</button>
         </div>
       );
     }
```

     In the above example, even though `dispatch` is called twice, `state.count` still reflects the **previous** value inside the event handler. React batches both dispatches and re-renders the component **once** with `count: 2`.

     #### How to read updated state after dispatch

     If you need the updated value right after dispatching, you have several options:

     1. **Use `useEffect` to react to state changes:**
```jsx
        useEffect(() => {
          console.log('Updated count:', state.count);
        }, [state.count]);
```

     2. **Compute the next state manually:**
```jsx
        const handleClick = () => {
          const nextState = reducer(state, { type: 'increment' });
          console.log('Next state will be:', nextState.count);
          dispatch({ type: 'increment' });
        };
```

     3. **Use `useRef` to track the latest state:**
```jsx
        const stateRef = useRef(state);
        useEffect(() => {
          stateRef.current = state;
        }, [state]);
```

     **Note:** This behavior is by design in React. The `dispatch` function itself has a **stable identity** (it doesn't change between re-renders), which makes it safe to omit from `useEffect` dependency arrays.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L7187)，来源许可：MIT。

<a id="kbcc2bc8df2ff"></a>

## js 中 function.call 和 function.apply 的区别？

```javascript
function.apply(thisObj, [argArray])
function.call(thisObj, arg1, arg2, …, argN);
```

apply：调用一个对象的一个方法，用另一个对象替换当前对象。例如：B.apply(A, arguments);即 A 对象应用 B 函数，即将 B 上下文从初始的上下文改变为 A 的上下文。

call：调用一个对象的一个方法，用另一个对象替换当前对象。例如：B.call(A, args1,args2);即 A 对象调用 B 对象的方法。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/JavaScript/javascript-fundamentals.md#L69)，来源许可：GPL-3.0。

<a id="kc9ec09b09920"></a>

## js 中什么是闭包？

闭包是利用了 js 的作用域特性，使用返回值为函数的函数，使里面的函数能够访问到外面函数的变量。我们调用外面的函数，就可以调用返回值函数，对外面函数的变量进行修改。

闭包可以访问另一个函数作用域中变量的函数。
作用：
1、可以减少全局变量的对象，防止全局变量过去庞大，导致难以维护
2、防止修改常量。
3、读取函数内部的变量，让这些变量的值始终保持在内存中。

例如：

```javascript
const add = function () {
  let counter = 0
  return function () {
    counter++
    return counter
  }
}

const x = add()
console.log(x()) // 计数器为 1
console.log(x()) // 计数器为 2
console.log(x()) // 计数器为 3
```

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/JavaScript/javascript-fundamentals.md#L126)，来源许可：GPL-3.0。

<a id="k1de83099bb18"></a>

## js 中作用域你是如何理解的？

全局作用域：写在最外层的对象，或者写在内层但是没有用 var 声明的变量，作用域为全局，例如：

```javascript
var outerVar = "outer";
function fn() {
  innerVar = “inner”;
  console.log(outerVar);
}
fn(); //result:outer
console.log(innerVar); //result:inner
```

函数作用域：写在函数内层使用 var 声明的变量，例如：

```javascript
function fn() {
  var innerVar = 'inner'
}
console.log(innerVar) // ReferenceError: innerVar is not defined
```

作用域链：内部函数可以链式访问外部函数的变量，例如：

```javascript
name = 'aaa'

function b() {
  var name = 'bbb'

  function c() {
    var name = 'ccc'
    console.log(name) //ccc
  }

  function d() {
    console.log(name) //bbb
  }
  c()
  d()
}
b()
console.log(name) //aaa
```

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/JavaScript/javascript-fundamentals.md#L80)，来源许可：GPL-3.0。

<a id="ka142797fcd64"></a>

## js 中如何判断一个对象是什么类型？

使用 typeof 可以判断一个 javascript 基本对象的类型。

```javascript
typeof 'John' // 返回 string
typeof 3.14 // 返回 number
typeof NaN // 返回 number
typeof false // 返回 boolean
typeof [1, 2, 3, 4] // 返回 object
typeof { name: 'John', age: 34 } // 返回 object
typeof new Date() // 返回 object
typeof function () {} // 返回 function
typeof myCar // 返回 undefined (如果 myCar 没有声明)
typeof null // 返回 object
```

使用 constructor 可以返回一个构造器的类型，可以根据构造器名称来判断类型。

```javascript
"John".constructor // 返回函数 String() {[native code]}
(3.14).constructor // 返回函数 Number() {[native code]}
false.constructor // 返回函数 Boolean() {[native code]}
[1,2,3,4].constructor // 返回函数 Array() {[native code]}
{name:'John', age:34}.constructor // 返回函数 Object() {[native code]}
new Date().constructor // 返回函数 Date() {[native code]}
function () {}.constructor // 返回函数 Function() {[native code]}
```

使用 instanceof 可以检测引用类型，如：

```javascript
console.log(person instanceof Object) // 变量 person 是 Object 吗？
console.log(colors instanceof Array) // 变量 colors 是 Array 吗？
console.log(pattern instanceof RegExp) // 变量 pattern 是 RegExp 吗？
```

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/JavaScript/javascript-fundamentals.md#L23)，来源许可：GPL-3.0。

<a id="kbfcb794b8c0f"></a>

## js 的原型链你是如何理解的？

![原型链](http://www.shadowingszy.top/images/prototype.png)

只要是对象就有原型, 并且原型也是对象, 因此只要定义了一个对象, 那么就可以找到他的原型, 如此反复, 就可以构成一个对象的序列, 这个结构就被成为原型链。

每个对象都会在其内部初始化一个属性，就是 prototype(原型)，当我们访问一个对象的属性时，如果这个对象内部不存在这个属性，那么他就会去 prototype 里找这个属性，这个 prototype 又会有自己的 prototype，于是就这样一直找下去，也就是我们平时所说的原型链的概念。

关系：instance.constructor.prototype = instance.proto

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/JavaScript/javascript-fundamentals.md#L60)，来源许可：GPL-3.0。

<a id="k69e13d8fc423"></a>

## test" 和 new String("test")有什么区别，{}和 new Object()有什么区别？

"test"是一个 string 类型的常量，而 new String()会创建一个字符串对象。

```javascript
const obj1 = new String('abc') // 类型为object
const obj2 = 'abc' // 类型为string

obj1 == obj2 // true
obj1 === obj2 // false
```

而 {} 和 new Object() 本身都是创建对象，并返回这个对象的引用。

```javascript
const obj1 = new Object('abc') // 类型为object
const obj2 = {} // 类型为obejct

obj1 == obj2 // false
obj1 === obj2 // false
```

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/JavaScript/javascript-fundamentals.md#L398)，来源许可：GPL-3.0。

<a id="k9f038edbf360"></a>

## V8 引擎垃圾回收机制是什么样的？

1、如何判断是否可以回收
（1）标记清除
当变量进入环境（例如，在函数中声明一个变量）时，就将这个变量标记为“进入环境”。从逻辑上讲，永远不能释放进入环境的变量所占用的内存，因为只要执行流进入相应的环境，就可能会用到它们。而当变量离开环境时，则将其标记为“离开环境”。

具体做法：
垃圾收集器在运行的时候会给存储在内存中的所有变量都加上标记（当然，可以使用任何标记方式）。
然后，它会去掉运行环境中的变量以及被环境中变量所引用的变量的标记
此后，依然有标记的变量就被视为准备删除的变量，原因是在运行环境中已经无法访问到这些变量了。
最后，垃圾收集器完成内存清除工作，销毁那些带标记的值并回收它们所占用的内存空间。

（2）引用计数
引用计数的含义是跟踪记录每个值被引用的次数。
当声明了一个变量并将一个引用类型值赋给该变量时，则这个值的引用次数就是 1。
如果同一个值又被赋给另一个变量，则该值的引用次数加 1。
相反，如果包含对这个值引用的变量又取得了另外一个值，则这个值的引用次数减 1。
当这个值的引用次数变成 0 时，就可以将其占用的内存空间回收回来，这样，当垃圾收集器下次再运行时，它就会释放那 些引用次数为零的值所占用的内存。
但这样会有循环引用的问题。

2、V8 垃圾回收策略
将内存分为两个生代：新生代（new generation）和老生代（old generation）。
新生代中的对象为存活时间较短的对象，老生代中的对象为存活时间较长或常驻内存的对象，分别对新老生代采用不同的垃圾回收算法来提高效率，对象最开始都会先被分配到新生代（如果新生代内存空间不够，直接分配到老生代），新生代中的对象会在满足某些条件后，晋升到老生代。

新生代主要使用 Scavenge 进行管理，将内存平均分为两块，使用空间叫 From，闲置空间叫 To，新对象都先分配到 From 空间中，在空间快要占满时将存活对象复制到 To 空间中，然后清空 From 的内存空间，此时，调换 From 空间和 To 空间，继续进行内存分配，当满足晋升条件时对象会从新生代晋升到老生代。

对象晋升的条件主要有两个：
如果一个对象是第二次经历从 From 空间复制到 To 空间，那么这个对象会被移动到老生代中。
当要从 From 空间复制一个对象到 To 空间时，如果 To 空间已经使用了超过 25%，则这个对象直接晋升到老生代中。（设置 25%这个阈值的原因是当这次 Scavenge 回收完成后，这个 To 空间会变为 From 空间，接下来的内存分配将在这个空间中进行。如果占比过高，会影响后续的内存分配）

老生代主要采用 Mark-Sweep 和 Mark-Compact 算法，一个是标记清除，一个是标记整理。两者不同的地方是，Mark-Sweep 在垃圾回收后会产生碎片内存，而 Mark-Compact 在清除前会进行一步整理，将存活对象向一侧移动，随后清空边界的另一侧内存，这样空闲的内存都是连续的，但是带来的问题就是速度会慢一些。在 V8 中，老生代是 Mark-Sweep 和 Mark-Compact 两者共同进行管理的。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/JavaScript/NodeJS.md#L17)，来源许可：GPL-3.0。

<a id="kf630adee12fd"></a>

## What does this method do?

```javascript
JSON.parse();
```

- A: Parses JSON to a JavaScript value
- B: Parses a JavaScript object to JSON
- C: Parses any JavaScript value to JSON
- D: Parses JSON to a JavaScript object only

Answer
<p>

### 参考资料

- [lydiahallie/javascript-questions](https://github.com/lydiahallie/javascript-questions/blob/a8b427b9f7f94f1a2965144ba544b475c5f65829/README.md#L3559)，来源许可：MIT。

<a id="kd1cf7b2c4db6"></a>

## What does this return?

```javascript
const firstPromise = new Promise((res, rej) => {
  setTimeout(res, 500, 'one');
});

const secondPromise = new Promise((res, rej) => {
  setTimeout(res, 100, 'two');
});

Promise.race([firstPromise, secondPromise]).then(res => console.log(res));
```

- A: `"one"`
- B: `"two"`
- C: `"two" "one"`
- D: `"one" "two"`

Answer
<p>

### 补充说明

```javascript
[...'Lydia'];
```

- A: `["L", "y", "d", "i", "a"]`
- B: `["Lydia"]`
- C: `[[], "Lydia"]`
- D: `[["L", "y", "d", "i", "a"]]`

### 参考资料

- [lydiahallie/javascript-questions](https://github.com/lydiahallie/javascript-questions/blob/a8b427b9f7f94f1a2965144ba544b475c5f65829/README.md#L1377)，来源许可：MIT。
- [lydiahallie/javascript-questions](https://github.com/lydiahallie/javascript-questions/blob/a8b427b9f7f94f1a2965144ba544b475c5f65829/README.md#L1319)，来源许可：MIT。

<a id="kf897e5b9a02b"></a>

## What happens when we do this?

```javascript
function bark() {
  console.log('Woof!');
}

bark.animal = 'dog';
```

- A: Nothing, this is totally fine!
- B: `SyntaxError`. You cannot add properties to a function this way.
- C: `"Woof"` gets logged.
- D: `ReferenceError`

Answer
<p>

### 参考资料

- [lydiahallie/javascript-questions](https://github.com/lydiahallie/javascript-questions/blob/a8b427b9f7f94f1a2965144ba544b475c5f65829/README.md#L347)，来源许可：MIT。

<a id="k1c05d28f9880"></a>

## What is the difference between async mode and concurrent mode?

     Both refers the same thing. Previously concurrent Mode being referred to as "Async Mode" by React team. The name has been changed to highlight React’s ability to perform work on different priority levels. So it avoids the confusion from other approaches to Async Rendering.

### 参考资料

- [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions/blob/55b7d491cd74c7b37f9352f3b2420d66e7187951/README.md#L5665)，来源许可：MIT。

<a id="k7757df41abd4"></a>

## 介绍 js 的基本数据类型？

基本类型（值类型）：String，Number，Boolean，Null，Undefined，Symbol，BigInt。

数字类型包含整数与浮点数，整数精度为 2^53，浮点数值最高精度为 17 位小数。
另外注意的是，NAN 属于数字类型，代表非数字，即 1/0=NAN，NAN/1=NAN。
Infinity 代表超过了范围的数，有正负号。

undefined：表示变量已声明，但不含有值。
null：表示变量为空。

引用类型：对象，数组，函数（其实都是对象，都是一种引用）。

数据封装类对象：Object、Array、Boolean、Number、String
其他对象：Function、Arguments、Math、Date、RegExp、Error

基本类型被保存在栈内存中，引用类型被保存在堆内存中

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/JavaScript/javascript-fundamentals.md#L5)，来源许可：GPL-3.0。

<a id="k4349ca1fa180"></a>

## 介绍一下 js 中 async 和 await 的用法？与 Promise 的区别？

async 作为一个关键字放到函数前面，用于表示函数是一个异步函数。
因为 async 就是异步的意思，异步函数也就意味着该函数的执行不会阻塞后面代码的执行。
async 会返回一个 Promise 对象，比如我们 console.log(timeout())，会得到一个 Promise 对象，如果 resolve 会返回 hello world，如果 reject 就会抛异常。
但这不是重点，async 的最大优势在于其内部可以使用 await，能够更简洁的处理 Promise 的 then 链。
如果 async 中没有 await，它其实就相当于一个 resolve 返回了 return 值的 Promise 对象罢了。

await 表达式会暂停当前 async function 的执行，等待 Promise 处理完成。若 Promise 正常处理(fulfilled)，其回调的 resolve 函数参数作为 await 表达式的值，继续执行 async function。若 Promise 处理异常(rejected)，await 表达式会把 Promise 的异常原因抛出。另外，如果 await 操作符后的表达式的值不是一个 Promise，则返回该值本身。

async 和 await 结合能够更直观地处理 Promise 的 then 链。

举个例子：
Promise 的写法：

```javascript
doSomething()
  .then(function (res) {
    return doNext(res)
  })
  .then(function (nextRes) {
    return doFinalThing(nextRes)
  })
  .then(function (finalResult) {
    console.log('Got the final result: ' + finalResult)
  })
  .catch(failureCallback)
```

async/await 的写法：

```javascript
try {
  const result = await doSomething()
  const nextRes = await doNext(result)
  const finalResult = await doFinalThing(newResult)
  console.log('Got the final result: ' + finalResult)
} catch (error) {
  failureCallback(error)
}
```

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/JavaScript/javascript-fundamentals.md#L270)，来源许可：GPL-3.0。

<a id="k7608c6565127"></a>

## 介绍一下 js 中 Promise 的用法？

Promise 对象代表一个异步操作，其不受外界影响，有三种状态：
Pending // 进行中、未完成的
Resolved // 已完成，又称 Fulfilled
Rejected // 已失败

Promise 对象提供了如下四种方法：
then // 异步操作完成调用方法
catch // 异步操作失败调用方法
all // 所有函数操作完成后调用方法
race // 第一个完成或失败后调用方法

举个例子：

```javascript
function read(time) {
  console.log('正在阅读')
  let p = new Promise(function (resolve, reject) {
    setTimeout(function () {
      console.log('阅读完毕')
      time = time + 1
      resolve(time)
    }, 2000)
  })
  return p
}

function write(time) {
  console.log('正在写作')
  let p = new Promise(function (resolve, reject) {
    setTimeout(function () {
      console.log('写作完毕')
      time = time + 1
      resolve(time)
    }, 2000)
  })
  return p
}

function rest(time) {
  console.log('正在休息')
  let p = new Promise(function (resolve, reject) {
    setTimeout(function () {
      console.log('休息完毕')
      time = time + 1
      resolve(time) //把promise的状态设置为resolved，成功
    }, 2000)
  })
  return p
}

function badDream(time) {
  console.log('正在做梦')
  let p = new Promise(function (resolve, reject) {
    setTimeout(function () {
      console.log('做了噩梦')
      time = time + 1
      reject(time) //把promise的状态设置为rejected，失败
    }, 2000)
  })
  return p
}

read(0)
  .then(function (data) {
    return write(data)
  })
  .then(function (data) {
    return badDream(data)
  })
  .then(function (data) {
    return rest(data)
  })
  .then(function (data) {
    console.log(data)
  })
  .catch(function (data) {
    //处理失败的方法
    console.log('第' + data + '步出错')
  })

const p1 = new Promise(function (resolve, reject) {
  setTimeout(function () {
    console.log('p1完成')
    resolve(11)
  }, 1000)
})

const p2 = new Promise(function (resolve, reject) {
  setTimeout(function () {
    console.log('p2完成')
    resolve(22)
  }, 2000)
})

const p3 = new Promise(function (resolve, reject) {
  setTimeout(function () {
    console.log('p3完成')
    resolve(33)
  }, 3000)
})

//all，所有函数都执行结束后，回调方法
Promise.all([p1, p2, p3]).then(function (data) {
  console.log('全部完成', data)
})

//race，第一个函数执行结束后，回调方法
Promise.race([write(1), rest(2)]).then(function (results) {
  console.log('准备工作完毕：')
  console.log(results)
})
```

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/JavaScript/javascript-fundamentals.md#L155)，来源许可：GPL-3.0。

<a id="k5fb2076c763a"></a>

## 代码实现一下展平数组？

```javascript
const arr = [1, 3, [3, 4, [5, 6]]]

// 第一种方案：用现成api，不兼容低版本的浏览器
const arr1 = arr.flat(Infinity)

// 第二种方案：原生循环递归实现
function flat2(arr) {
  const result = []
  arr.forEach((item) => {
    if (Array.isArray(item)) {
      result.push(...flat(item))
    } else {
      result.push(item)
    }
  })
  return result
}
const arr2 = flat2(arr)

// 第三种方案：使用解构和递归实现
function flat3(arr) {
  const result = [].concat(...arr.map((x) => (Array.isArray(x) ? flat(x) : x)))
  return result
}
const arr3 = flat3(arr)
```

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/JavaScript/javascript-fundamentals.md#L347)，来源许可：GPL-3.0。

<a id="k504930642a3a"></a>

## 代码实现一下深拷贝对象？

```javascript
// 对象中如果均为基本类型
JSON.parse(JSON.stringify(obj))

// 对象中如果既有基本类型，还有Array和Object
function deepCopy(data) {
  let output
  if (data === null || !(typeof data === 'object')) {
    output = data
  } else {
    output = data.constructor.name === 'Array' ? [] : {}
    for (let key in data) {
      output[key] = deepCopy(data[key])
    }
  }
  return output
}
```

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/JavaScript/javascript-fundamentals.md#L377)，来源许可：GPL-3.0。

<a id="k22673ad9162c"></a>

## 实现一个 EventEmitter？

实现：

```javascript
class EventEmitter {
  constructor() {
    this._events = {}
  }

  subscribe(type, handler) {
    if (this._events.hasOwnProperty(type)) {
      this._events[type].push(handler)
    } else {
      this._events[type] = [handler]
    }
  }

  unsubscribe(type, handler) {
    if (this._events.hasOwnProperty(type)) {
      const index = this._events[type].indexOf(handler)
      if (index > -1) {
        this._events[type].splice(index, 1)
      }
    }
  }

  once(type, handler) {
    let fired = false
    let _this = this
    function magic() {
      _this.unsubscribe(type, magic)

      if (!fired) {
        fired = true
        handler.apply(_this, arguments)
      }
    }
    this.subscribe(type, magic)
  }

  emit(type, args) {
    if (this._events.hasOwnProperty(type)) {
      this._events[type].forEach((fn) => fn(args))
    }
  }
}

module.exports = EventEmitter
```

使用：

```javascript
const EventEmitter = require('./myEventEmitter')

const eventEmitter = new EventEmitter()

const fn = (args) => {
  console.log('good args', args)
}
const fn2 = (args) => {
  console.log('good args 2', args)
}
const fn3 = (args) => {
  console.log('good args 3', args)
}

eventEmitter.subscribe('good', fn)
eventEmitter.subscribe('good2', fn2)

eventEmitter.emit('good', 11111)
eventEmitter.emit('good2', 22222)

eventEmitter.unsubscribe('good', fn)

eventEmitter.emit('good2', 22222)

eventEmitter.once('good3', fn3)
eventEmitter.emit('good3', 33333)

eventEmitter.emit('good3', 33333)
```

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/JavaScript/NodeJS.md#L49)，来源许可：GPL-3.0。

<a id="k48ff4a16349d"></a>

## 说几个常用的 Array 的 api？

**Array 的 API 重点是会用，而不是知道这个 API 是干什么的**

```javascript
push(a)           // 末尾添加，返回数组长度
unshift(a)	      // 首位添加，返回数组长度
shift()	          // 删除第一个元素，并返回删除的元素
pop()	            // 删除最后一个元素，并返回删除的元素
join(a)	          // 把数组中的所有元素放到一个字符串中，分隔符为a
concat(a, b)	    // 将b连接到a后面
sort()	          // 数组排序
reverse()	        // 数组倒序
isArray(a)	      // a是否为数组
slice(a, b)	      // 根据输入的开始点和末尾点，截取出新的数组（包括前不包括后）
splice(a, b, c)	  // 从a位置开始，删除b长度的数组，插入c

indexOf(a)	      // 从前向后寻找值等于a的项，返回index
lastIndexOf(a)	  // 从后向前寻找等于a的项，返回index

every(function(item, index, array))	      // 对数组每一项运行一次某函数，若函数每一项都为true，返回true
some(function(item, index, array))	      // 对数组每一项运行一次某函数，若函数某一项为true，返回true
filter(function(item, index, array))	    // 对数组每一项运行一次某函数，返回返回值为true的项的数组
map(function(item, index, array))	        // 对数组每一项运行一次某函数，返回返回值的数组
forEach(function(item, index, array))	    // 对数组每一项运行一次某函数，无返回值
reduce(function(prev, cur, index, array)) //接收四个参数：前一个值、当前值、项的索引和数组对象，这个函数的任意返回值会作为第一个参数传给下一项。
```

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/JavaScript/javascript-fundamentals.md#L314)，来源许可：GPL-3.0。

<a id="k4dc05dfcdef0"></a>

## 请简述一下 Koa 的洋葱模型？

koa 洋葱模型是指 koa 中每个中间件的执行顺序。
koa 在执行多个中间件中的逻辑时，会先执行第一个中间件的逻辑，执行到 next()函数后会执行第二个中间件的逻辑，以此类推，直到最后一个中间件。当最后一个中间件执行完毕后，会跳回执行倒数第二个中间件 next()函数后面的代码，以此类推，直到第一个中间件 next()函数后面的代码执行完毕。

![洋葱模型](http://www.shadowingszy.top/images/koa.png)

举例来说：

```javascript
const Koa = require('koa')

const app = new Koa()
const PORT = 3000

// #1
app.use(async (ctx, next) => {
  console.log(1)
  await next()
  console.log(1)
})
// #2
app.use(async (ctx, next) => {
  console.log(2)
  await next()
  console.log(2)
})

app.use(async (ctx, next) => {
  console.log(3)
})

app.listen(PORT)
console.log(`http://localhost:${PORT}`)
```

访问 http://localhost:3000，控制台打印：

```
1
2
3
2
1
```

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/02-programming-languages/JavaScript/NodeJS.md#L178)，来源许可：GPL-3.0。
