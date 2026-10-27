# HTML、CSS与页面布局

<a id="kf950e4c97bf0"></a>

## FC 是什么？BFC 和 IFC 是什么？

FC：格式化模型。

FC 会根据 CSS 盒子模型将文档中的元素转换为一个个的盒子，每个盒子的布局由以下因素决定：
1、盒子的尺寸：精确指定、由约束条件指定或没有指定
2、盒子的类型：行内盒子（inline）、行内级盒子（inline-level）、原子行内级盒子（atomic inline-level）、块盒子（block）
3、定位方案：普通流定位、浮动定位或绝对定位
4、文档树中的其它元素：即当前盒子的子元素或兄弟元素
5、视窗尺寸与位置
6、包含的图片的尺寸
7、其他的某些外部因素

BFC：块级格式化上下文。

1、在 BFC 中，盒子从顶端开始垂直地一个接一个地排列，两个盒子之间的垂直的间隙是由它们的 margin 值所决定的。在一个 BFC 中，两个相邻的块级盒子的垂直外边距会产生折叠。
2、在 BFC 中，每一个盒子的左外边缘会触碰到容器的左边缘。
3、浮动元素、绝对定位元素，以及设置了 overflow 属性（除了 visible）的元素不是块级盒子的块容器，因此会为他们的内容创建新的 BFC。

IFC：行内级格式化上下文。

1、在 IFC 中，盒子一个接着一个地水平放置。这些盒子会通过不同的方式进行对齐，如底部对齐，顶部对齐，文字基线对齐。
2、矩形区域包含着来自一行的盒子叫做盒行盒（line box）。
3、line box 的宽度由浮动情况和它的包含块决定。line box 的高度由 line-height 计算决定（也就是说，由其内部的块撑开）。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/06-development-tech/frontend/css-advanced.md#L56)，来源许可：GPL-3.0。

<a id="k0001e42e2772"></a>

## HTML5 新增了哪些元素？

| 标签        | 说明                                                             |
| ----------- | ---------------------------------------------------------------- |
| `<header>`  | 定义 section �?document 的页眉�?                               |
| `<footer>`  | 定义 section �?document 的页脚�?                               |
| `<nav>`     | 定义导航链接的部分�?                                            |
| `<article>` | 定义文章的内容�?                                                |
| `<section>` | 定义文档中的段落。比如章节、页眉、页脚或文档中的其他部分�?      |
| `<aside>`   | 定义 article 以外的内容。aside 的内容应该与 article 的内容相关�?|
| `<audio>`   | 定义声音�?                                                      |
| `<canvas>`  | 定义图形�?                                                      |
| `<video>`   | 定义视频，比如电影片段或其他视频流�?                            |
| `<source>`  | 为媒介元素（比如 `<video>` �?`<audio>`）定义媒介资源�?         |

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/06-development-tech/frontend/HTML_CSS.md#L52)，来源许可：GPL-3.0。

<a id="k33852f070a1e"></a>

## 如何开启 GPU 加速？其优缺点是什么？

当页面中某个 DOM 元素应用了某些 CSS 规则时就会开启 GPU 加速，如 3D 变换：

```css
.cube {
  -webkit-transform: translate3d(250px, 250px, 250px) rotate3d(250px, 250px, 250px, -120deg) scale3d(0.5, 0.5, 0.5);
}
```

如果不想对元素用 3D 变换但是还想要开 GPU 加速，就可以：

```css
.cube {
  -webkit-transform: translateZ(0);
  -moz-transform: translateZ(0);
  -ms-transform: translateZ(0);
  -o-transform: translateZ(0);
  transform: translateZ(0);
}
```

但是，一定要注意：不要随意使用 GPU 加速，如果的确能够显著提高性能，可以尝试使用 GPU 加速。但是另一方面，使用 GPU 可能会导致严重的性能问题，因为它增加了内存的使用，而且它会减少移动端设备的电池寿命。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/06-development-tech/frontend/css-advanced.md#L107)，来源许可：GPL-3.0。

<a id="k4820ee9b97b4"></a>

## 如何清除浮动？

浮动可以理解为让某个 div 元素脱离标准流，漂浮在标准流之上。
一个浮动元素会尽量向左或向右移动，直到它的外边缘碰到包含框或另一个浮动框的边框为止。

清除浮动可以理解为打破横向排列。清除浮动的关键字是 clear，其取值有以下几种：
1、none，默认值。允许两边都可以有浮动对象
2、left，不允许左边有浮动对象
3、right，不允许右边有浮动对象
4、both，不允许有浮动对象
对于 CSS 的清除浮动(clear)，一定要牢记：这个规则只能影响使用清除的元素本身，不能影响其他元素。

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/06-development-tech/frontend/css-advanced.md#L81)，来源许可：GPL-3.0。

<a id="ka1e864225a4d"></a>

## 描述一�?HTML 的事件模型？事件捕获/事件冒泡指的是？

![事件模型](http://www.shadowingszy.top/images/event.png)

当页面触发一个事件的时候，浏览器主要做了三个阶段的事情，分别是�?
1、捕获事件阶�?
2、目标处理阶�?
3、后续事件处理阶�?

当事件被触发，从根节点传递事件对象到目标节点的过程，就是事件捕获�?
当处理完成事件后，从目标节点反向的传递到根节点的过程，就是事件冒泡�?

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/06-development-tech/frontend/HTML_CSS.md#L69)，来源许可：GPL-3.0。

<a id="k67b00105ad84"></a>

## 简单介绍下常用�?HTML 元素�?

块状标签：元素独占一行，可指定宽、高�?
常用的块状元素有�?

```
<div>�?p>�?h1>-<h6>�?ol>�?ul>�?dl>�?table>�?form>
```

内联元素：元素在一行内，宽度与高度由内容决定，只有在内容超�?HTML 的宽度时，才会换行�?
常用的内联元素有�?

```
<a>�?span>�?i>�?em>�?strong>�?label>
```

内联块状元素同时具备内联元素、块状元素的特点，它和其他元素都在一行，但元素的高度、宽度、行高以及顶和底边距都可设置。常用的内联块状元素有：

```
<img>�?input>
```

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/06-development-tech/frontend/HTML_CSS.md#L5)，来源许可：GPL-3.0。

<a id="kd3dda4a6c58d"></a>

## 请简述一下 CSS 盒模型？

![盒模型](http://www.shadowingszy.top/images//www.shadowingszy.top/images/flex.png)

flex 的各种属性：

```
1、flex-direction
属性决定主轴的方向（即项目的排列方向）。

row（默认值）：主轴为水平方向，起点在左端。
row-reverse：主轴为水平方向，起点在右端。
column：主轴为垂直方向，起点在上沿。
column-reverse：主轴为垂直方向，起点在下沿。
```

```
2、flex-wrap
默认情况下，项目都排在”轴线”上。本属性定义如果一条轴线排不下，如何换行。

nowrap（默认值）：不换行。
wrap：换行，第一行在上方。
wrap-reverse：换行，第一行在下方。
```

```

3、align-items
定义弹性盒子在交叉轴上如何对齐。

flex-start：交叉轴的起点对齐。
flex-end：交叉轴的终点对齐。
center：交叉轴的中点对齐。
baseline: 项目的第一行文字的基线对齐。
stretch（默认值）：如果项目未设置高度或设为 auto，将占满整个容器的高度。

```

```

4、justify-content
定义弹性盒子在主轴方向上的对齐方式。

flex-start：容器开头对齐。
flex-end：容器终点对齐。
center：容器中点对齐。

```

### 参考资料

- [Datawhale](https://github.com/datawhalechina/daily-interview/blob/f35e8d555f8ff07d568eae569c3641bd76d0eac9/docs/06-development-tech/frontend/css-advanced.md#L5)，来源许可：GPL-3.0。
