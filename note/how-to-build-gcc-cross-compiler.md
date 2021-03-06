How to build a gcc cross compiler
====================================


Recently I have to configure some routers to suit my need. Those routers are all of MIPS, with some in little endianness and others in big endianness. All the routers are running OpenWrt, a tiny little Linux distro that is built specifically for router. My job is compiling a 802.1x authentication program so that it can run in the router. Unfortunately, the routers have too little memory(16 M) and flash storage(64 M) to host a gcc compiler(and I have no interest in using other compiler for compatibility issue). So I have to build a cross compiler on my own x86_64 Linux box, cross compile the program, send it over ssh to the routers and then start it internally in routers.

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

Usually the _build_ and _host_ is the same, but you should know about that difference. 

Please remember these three thing as it would be required when we configure the build process afterward.

Getting Start
---------------
In my way, to build a gcc cross compiler, all you need is a Unix-like operating system, a recent version of gcc and a working networking. I am using arch-linux on a x86-64, and I will now show how to build a cross compiler that **run on x86_64**(the _host_), but compile and produce programs that run on **mipseb**(the _target_), a big-endian MIPS architecture.

I assume that we are originally in a directory `/home/walkerlala/cross-compile/` before we start.


#### Get the source

Fir obtain all the packages needed:
```
$ wget http://ftpmirror.gnu.org/binutils/binutils-2.27.tar.gz
$ wget http://ftpmirror.gnu.org/gcc/gcc-6.1.0/gcc-6.1.0.tar.gz
$ wget https://www.kernel.org/pub/linux/kernel/v4.x/linux-4.6.5.tar.xz
$ wget http://ftpmirror.gnu.org/glibc/glibc-2.24.tar.xz
$ wget http://ftpmirror.gnu.org/mpfr/mpfr-3.1.4.tar.xz
$ wget http://ftpmirror.gnu.org/gmp/gmp-6.1.1.tar.xz
$ wget http://ftpmirror.gnu.org/mpc/mpc-1.0.3.tar.gz

$ sudo apt-get install g++ make gawk


```
Note that that may not be the newest version of the package, and you may want a specific version of some package to suit your need(for example, I want linux-kernel v4.6.5 because my router is running a kernel of that version). Also, in case that the download may be slow, try to find some other mirror sites.

#### untar all packages:
```
$ for f in *.tar.*; do tar xvf $f; done
```

#### make a new dir to hold the all the output files:
```
$ mkdir output
```

then add the installation’s `bin` subdirectory to your PATH environment variable. You can remove this directory from your PATH later, but most of the build steps expect to find `mipseb-linux-gnu-gcc` and other host tools via the PATH by default.
```
$ export PATH=/home/walkerlala/cross-compile/output/bin:$PATH
```

#### unset some environment variables:
```
unset LIBRARY_PATH CPATH C_INCLUDE_PATH PKG_CONFIG_PATH CPLUS_INCLUDE_PATH LD_LIBRARY_PATH
```
This is needed to prevent gcc messing up with header files.


### compile binutils
we will first compile the binutils packages, which contains the linkers and other stuff:
```
$ mkdir build-binutils
$ cd build-binutils
$ ../binutils-2.27/configure --prefix=/home/walkerlala/cross-compile/output --target=mipseb-linux-gnu --disable-multilib
$ make -j4
$ make install
$ cd ..
```
`--disable-multilib` means that we only want our Binutils installation to work with programs and libraries using the `mipseb` instruction set, and not any related instruction sets such as `mipsel`.

`--target` is as what explained above

`host` and `build` would usually guessed correctly by the GNU `configure` utility. In this case, They would both be X86.

After this, you should have three folders under the `output` directory:
  * the `bin` directory, which hold all the binary file such as `mipseb-linux-gnu-ld`
  * the `mipseb-linux-gnu` directory
  * the `share` directory

### install the Linux kernel headers
This step install the Linux kernel headers to `output/mipseb-linux-gnu/include`, which allow other program(e.g. glibc) to know which kernel are they running against, so that they can make corresponding system calls.

```
$ cd linux-4.6.5
$ make ARCH=mips INSTALL_HDR_PATH=/home/walkerlala/cross-compile/output/mipseb-linux-gnu headers_install
$ cd ..
```


### build the GCC compiler
In this step, we would build the gcc compiler, with no glibc.

Firts we create symbolic links from the GCC directory to some of the other directories. These five packages are dependencies of GCC, and when the symbolic links are present, GCC’s build script will build them automatically.

```
$ cd gcc-6.1.0
$ ln -s ../mpfr-3.1.4 mpfr
$ ln -s ../gmp-6.1.1 gmp
$ ln -s ../mpc-1.0.3 mpc
$ cd ..
```

And then we can start to build `mipseb-linux-gnu-gcc`:

```
$ mkdir build-gcc
$ cd build-gcc
$ ../gcc-6.1.0/configure --prefix=/home/walkerlala/cross-compile/output --target=mipseb-linux-gnu --enable-languages=c,c++ --disable-multilib
$ make -j4 all-gcc
$ make install-gcc
$ cd ..
```

  * Because we’ve specified `--target=mipseb-linux-gnu`, the build script looks for the Binutils cross-tools we built in previous step with names prefixed by `mipseb-linux-gnu-`. Likewise, the C/C++ compiler names will be prefixed by `mips-linux-gnu-`.
  * `--enable-languages=c,c++` prevents other compilers in the GCC suite, such as Fortran, Go or Java, from being built.



Now you should have a cross gcc/g++ compiler and some other cross-platform tools in **output/bin**. But there is one important thing that is missed: the standard C/C++ library. Without this, you cannot do much thing with your new cross gcc compiler. However, I have not figured out the *correct* way to build the standard C/C++ library. All I know is that glibc is highly dependent on the Linux kernel. If the version of the glibc you have and the version of the Linux kernel header you have don't match, you would definitely not be be able to build glibc. I would try to figure out that in the future.


By the way, there are two quick way to build cross-platform tools: using **buildroot** and **crosstoo-ng**. Using these two things, you can make those cross-platform tools very quickly. And of course, you will have all the standard C/C++ library.



References:
[1]: [preshing on programming: How to build a gcc cross compiler](http://preshing.com/20141119/how-to-build-a-gcc-cross-compiler/)
