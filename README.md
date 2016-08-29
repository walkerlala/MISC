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
利用网络通信传递链接信息。主节点是被动的，如果子节点向主节点发送链接链接，那么主节点就会
向其返回一定量的待爬取链接；如果子节点向主节点发送返回请求，那么主节点就会接收一定数量的已爬取链接。
为了达到这个目的，主节点处需要维护两个链接池：已经"爬取的链接"和"待爬取的链接"。"已经爬取的链接"用
一个布隆过滤器[3]实现，初始时为空，但是随着子节点返回的链接数量不断增加，其大小可能呈指数式增长，所以，
为了能够维持庞大数量的链接池并且能够随机存储，我们布隆过滤器使用Linux系统所提供的内存映射机制(memory mapping)，将文件映射为
内存，这样既能实现链接池容量的扩展，又能随机实现随机储存，而且省去手动管理内存的烦恼。“待爬取的链接”存放
准备爬取的链接，可以像“已爬取的链接”一样，使用内存映射机制扩展容量，也可以限制大小，因为Internet是一张有
回路的网络，不用担心某些链接爬不大。
