一个分布式爬虫的设计与实现
===========================

Abstract
-----------
近年来由于互联网的快速发展，大数据应用变得越来越重要。
而在大数据应用中分布式计算占据一个很重要的地位。我们构建了一个用于获取
网页数据并处理数据的分布式爬虫系统，这个系统的功能与一般搜索引擎所用的
爬虫功能相似，主要用于快速爬取网页、存储网页和进行数据处理；所不同的是，
我们尝试了与一般爬虫不同的架构，使得这个架构更加的简洁和灵活，而且便于
控制，适合于轻量级的爬虫应用。我们将会首先介绍我们所设计的系统的架构，
然后分析系统的优缺点，最后列出我们使用这个系统进行数据获取时所获得的一些运行数据。

With the development of the Internet, the application of big data starts to 
become more and more important. Within application of big data, distributed
computing play an very important role. Recently we build a distributed crawler
system for distributing web page crawling and data processing. It resemble 
the crawling system used in search engine, but use a different structure.
This different but flexible structure make it easy to control, customize and 
thus suitable for lightweight application. We will first examine the design of
the structure fo this system. And then we will analyse the cons and pros of this
structure. Finally we conclude we some real world data that we collect.



系统架构
----------
总体上，我们的爬虫为Client-Server架构。以下是我们的粗略架构图：

  在这个架构中，主节点只有一个，负责整个爬虫系统的调度，但是本身却不负责爬取，
子节点有多个，接受主节点的调度信息（主要是待爬取链接）。主节点和子节点之间
利用TCP网络通信传递链接信息。主节点是被动的，如果子节点向主节点发送“链接请求”，那么主节点就会
向其返回一定量的待爬取链接；如果子节点向主节点发送“返回请求”，那么主节点就会准备接收一定数量的已爬取链接。
为了达到这个目的，主节点处需要维护两个链接池：已经"爬取的链接"和"待爬取的链接"。"已经爬取的链接"用
一个布隆过滤器[3]实现，初始时为空，但是随着子节点返回的链接数量不断增加，其大小可能呈指数式增长，所以，
为了能够维持庞大数量的链接池并且能够随机存储，我们布隆过滤器使用内存映射机制(memory mapping)，将文件映射为
内存，这样既能实现链接池容量的扩展，又能随机实现随机储存，而且省去手动管理内存的烦恼。“待爬取的链接”存放
准备爬取的链接，需要手动在配置文件中给出一些初始链接。它的实现可以像“已爬取的链接”一样，使用内存映射机制扩展容量；
也可以限制它的大小，因为Internet是一张有回路的网络，不用担心某些链接爬不到。

  在启动这个系统的时候，我们会首先在一台服务器上启动主节点，主节点在特定端口不断地监听，等待链接请求或返回请求。
节点之间的请求是通过在TCP协议上实现的一个简单的Request-Response协议：
* 如果子节点向主节点发送'SEND',那么主节点则返回'OK'，然后发送链接，子节点收到'OK',开始准备接收链接；如果收到的链接不为空，则子节点开始爬取，如果为空，则子节点开始循环向主节点请求，如果请求一定次数后主节点还是返回空链接，则子节点认为已经没有新链接可爬，子节点退出。
* 如果字节点向主节点发送'REQUEST'，则主节点返回'OK',字节点接收到'OK'后，开始发送格式为'{已经爬取的链接：处理网页得到的新链接}’。主节点将已经爬取的链接加入布隆过滤器，将新链接对比布隆过滤器中已经爬取的链接，如果已经存在，则丢弃，否则将新链接加入“待爬取的链接”池中。由于过程中使用了布隆过滤器，速度可以大大提高。

 在一个这样的系统中，主节点只有一台，但是子节点可以有1～n台。主节点一直在监听，子节点可以根据需要随时增加或减少，这样，只需要在一些服务器（子节点）上简单地启动和停止一个爬虫程序，就可以实现整个系统的扩张或收缩。我们觉得这种设计可以带来至少两种好处：
 * 便于调度。如何能保证分布在不同机器的爬虫子节点不会爬到相同的链接？如果让爬虫直接进行通信处理的话，那么这个架构将是复杂而且易于出错的。将所有的链接返回给主节点，统一调度，统一发放，那么这个调度设计将会很简洁。
 * 易于监控。这个系统的关键在与主节点，只要我们能够监控好主节点的状态，就可以知道整个系统的大致情况。
 * 易于扩张和收缩。只要保持主节点的稳定，那么子节点的加入或退出并不会对其他子节点造成影响。换句话说，各个子节点之间是透明的
 * 可塑性。如果担心主机之间网络通信不畅，可以简单地将主节点和子节点同时存放于同一台机器上，这样即与传统的爬虫模型[4]相似了
 
 当然，由于是1+n的架构，所以n的大小会收到主节点的配置、网络带宽的影响。但是，1)由于主节点和子节点一般存放与内网，网络通信不会是很大的问题；2)由于 1+n 可以简单地扩展成 k * (1+n)，所以主节点对于n大小的限制可以得到减少。
  
