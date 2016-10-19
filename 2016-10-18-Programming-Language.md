这是一个坑。未填完。待续。


### Single-Dispatch, Double-Dispatch, Multiple-Dispatch
singlle-Dispath 就是一般 OO 里面的“多态”了。。。
Double-Dispatch 就是...
Multiple-Dispatch 就是 [1]
值得一提的是，这三种都属于 Dynamic-Dispatch

这里讲讲 static-overloading 和 Multiple-Dispatch 的区别。Static-overloading 就是所谓的“重载”。
也就是说，多个重名函数，参数的类型，或者参数的个数不一样。这种是编译时行为，并不属于 Dynamic-Dispatch
的范畴。但是 Multiple-Dispatch 不一样，Multiple-Dispatch是运行时行为。

[1][Report on language support for Multi-Methods and Open-Methods for C++](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2007/n2216.pdf)
