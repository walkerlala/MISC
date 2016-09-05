How to build a gcc cross compiler
====================================


Recently I have to configure some routers to suit my need. Those routers are all of MIPS, with some in little endianness and others in big endianness. All the routers are running OpenWrt, a tiny little Linux distro that is built specifically for router. My job is compiling a 802.1x authentication program so that it can work in the router. Unfortunately, the routers have too little memory(16 M) and flash storage(64 M) to host a gcc compiler(and I have no interest in using other compiler for compatibility issue). So I have to build a cross compiler on my own x86_64 Linux box, cross compile the program, send it over ssh to the routers and then start it internally in routers.

As well-known by any one who himself have build a compiler by hand itself, it is intimidating and time consuming. In this post, I try to explain the procedures needed to achieve that. Hopefully that would be helpful.

what is a cross compiler
-------------------------
Recall the way how you compile a _hello world_ program:
  1.  you run a gcc compiler on **x86_64**
  2.  it compile that source file and output a program that also run on **x86_64**

with a cross compiler, it go this way:
  1.  you run a gcc compiler on **x86_64**
  2.  it compile the source file and output a program that run on **other architecture**(e.g., ARM or MIPS)

When building a cross compiler, it involve an additional point: **the architecture that you build the cross compiler**. To make it clear, imagine that you are using a **x86_64** computer to build the cross compiler. And that compiler will run on an **ARM** platform. And it would compile and produce a program that run on a **MIPS** platform. So in summary, there are three platform invovled:
  * the _build_ platform, which you use to build the compiler,
  * the _host_ platform, which the cross compiler run,
  * the _target_ platform, which the program produced by the cross compiler run
  *
Please remember these three thing as it would be required when we are configure that build.

Preliminary
-------------------
In my way, to build a gcc cross compiler, all you need is a Unix-like operating system, a recent version of gcc and a working networking. I am using arch-linux on a x86_64.

### Get the source

Fir obtain all the packages needed:
```
$ wget http://ftpmirror.gnu.org/binutils/binutils-2.24.tar.gz
$ wget http://ftpmirror.gnu.org/gcc/gcc-4.9.2/gcc-4.9.2.tar.gz
$ wget https://www.kernel.org/pub/linux/kernel/v3.x/linux-3.10.70.tar.xz
$ wget http://ftpmirror.gnu.org/glibc/glibc-2.20.tar.xz
$ wget http://ftpmirror.gnu.org/mpfr/mpfr-3.1.2.tar.xz
$ wget http://ftpmirror.gnu.org/gmp/gmp-6.0.0a.tar.xz
$ wget http://ftpmirror.gnu.org/mpc/mpc-1.0.2.tar.gz
$ wget ftp://gcc.gnu.org/pub/gcc/infrastructure/isl-0.12.2.tar.bz2
$ wget ftp://gcc.gnu.org/pub/gcc/infrastructure/cloog-0.18.1.tar.gz
```
Note that that may not be the newest version of the package, and you may want a specific version of some package to suit your need(for example, I want linux-kernel v3.10.70 because my router is running a kernel of that version). Also, in case that the download may be slow, try to find some other mirror sites.



References:
[1]: [preshing on programming: How to build a gcc cross compiler](http://preshing.com/20141119/how-to-build-a-gcc-cross-compiler/)
