# Nix As Build System
## What
This tutorial is about using [nix](https://nixos.org/learn/) as a build system.

Before going through these examples, I suggest checking out [this tutorial](../nix_as_package_manager/README.md) on using nix as package manager.


## Why
Nix is pure functional language. Nix package manager creates immutable `nix/store`, where every build/packages are unique. And Nix has functionality to describe how to build these packages. This tutorial gives hands on examples how to use nix to build your projects. All examples are inside this folder, so you can clone it and follow along.

In this tutorial, we will go from fundamentals of nix language, to simple builds, and climb the levels of abstraction in this order:
1. Nix language
2. Nix derivations
3. make Derivations
4. Flake Derivations

## How

First, what is a build system? If you want comprehensive answer, check out [this resource](https://j3t.ch/tech/whats-a-build-system/). There you can find nice visual illustration of a build systems. By the definition there, nix is not full fledged build system (but it could be!)

So, let's start with simpler goal. Let's start with building programs. Can we build programs with nix?
### 1. Raw Derivation
Let's say we have a simple build. We want to write nix code that gets inputs and transform it into outputs. As we are interested in builds, and not running the code, we need output files transformed from source code and dependencies:
```
INPUTS                     BUILD SYSTEM                  OUTPUTS
+-------------------+        +--------------------+        +------------------+
| - Source Code     |        |                    |        | - Binaries (.exe)|
| - Dependencies    | ---->  |   Transformation   | ---->  | - Data Files     |
| - Build Tools     |        |      Process       |        | - Packages       |
+-------------------+        +--------------------+        +------------------+
```
Let's get a bit familiar with nix language. You can think of nix as functions (like in functional programming) operating on attribute sets. So simple function in nix looks like this:
```nix
func = a: b: a + b # function that adds two numbers
```
Here is a simple attribute set. You can think of them as "immutable" dictionaries:
```nix
myattrset = {
 field1 = "hello";
 field2 = 123;
};
```
Here is a function that transforms one attribute set to another attribute set:
```nix
attrFunc = {arg1, arg2, ...}:
{
  out1=arg1;
  out2=arg2
};
```
Note, you can use `...` to specify that this function can take other arguments, that are "hidden". This helps to implement polymorphic behavior. So, now you can realize that modules/flakes in nix are just definitions of some specialized functions. Normally, you will have file containing only lambda functions:
```nix
{config, nixpkgs, ...}: {
  imports = [];
  # ...
}
```

For our topic, we also need to introduce one more build-in nix concept. In core of the nix language, there is built-in [derivation](https://nix.dev/manual/nix/2.22/language/derivations) that can help to modify attribute sets to generate derivations. Derivation attribute requires to have specific required sets to fill. Here is a minimal set of required fields:
```nix
derivation {
  name="hello"; # name of a derivation
  syste="aarch64-darwin"; # system type for which, we are trying to build 
  builder="/bin/sh"; # absolute path to executable used to perform the build. Here we are using just shell.
  args= ["-c", "echo 'Hello from Nix' > $out"];  # arguments to builder. Although, this is optional, your derivation MUST produce some file. You can use `$out` to generate a specific outout. It will result in `result` which is either file or folder containing all build results.
}
```
So, you can save this to a nix file, say `raw.nix`. To "build" it, you can use this command:
```bash 
>$ nix-build raw.nix
```
If you check the folder, you should see a new `result` object, that is going to be a symlink to some immutable file in nix store:
```bash
>$ ls .
raw.nix result
>$ readlink result
/nix/store/iaz2wqpzq046s7g8dpxkfpdp7isnm200-hello
```
If you check the content of the `result`, it has our message
```bash
>$ cat result
Hello from Nix
```

#### What is going on here?
You may ask yourself "What just happened?". Let's unveil magic a bit. If you check the [nix architecture](https://nix.dev/manual/nix/2.22/architecture/architecture), You will find this diagram, that explains "build" process in high level:
```

   .----------------.
   | Nix expression |----------.
   '----------------'          |
           |              passed to
           |                   |
+----------|-------------------|--------------------------------+
| Nix      |                   V                                |
|          |      +-------------------------+                   |
|          |      | commmand line interface |------.            |
|          |      +-------------------------+      |            |
|          |                   |                   |            |
|    evaluated by            calls              manages         |
|          |                   |                   |            |
|          |                   V                   |            |
|          |         +--------------------+        |            |
|          '-------->| language evaluator |        |            |
|                    +--------------------+        |            |
|                              |                   |            |
|                           produces               |            |
|                              |                   V            |
| +----------------------------|------------------------------+ |
| | store                      |                              | |
| |            referenced by   V       builds                 | |
| | .-------------.      .------------.      .--------------. | |
| | | build input |----->| build plan |----->| build result | | |
| | '-------------'      '------------'      '--------------' | |
| +-------------------------------------------------|---------+ |
+---------------------------------------------------|-----------+
                                                    |
                                              represented as
                                                    |
                                                    V
                                            .---------------.
                                            |     file      |
                                            '---------------'

```
You can see 3 different things stored in nix store:
1. Inputs: source code (libraries), data files, dependencies, build tools/ executable
2. Build plans: derivations
3. Build results: practically, same as inputs! New source code, new executables, or new dependencies.

Inputs and results are somewhat clear. You are familiar with them. What are derivations?
You can check nix store and you can find many files that end with `.drv` extension.
```bash 
>$ ls /nix/store | grep ".drv"
```

You can generate derivation for the `raw.nix` Using command line tool:
```bash
>$ nix-instantiate raw.nix
/nix/store/gcb5bf47ljdpfrcryrxqf8vdk45j3pzv-hello.drv
```
You can check its content:
```bash
>$ cat /nix/store/gcb5bf47ljdpfrcryrxqf8vdk45j3pzv-hello.drv
Derive([("out","/nix/store/fpihphff4y827j4dwy8hpqjcd2z5jdv4-hello","","")],[],[],"aarch64-darwin","/bin/sh",["-c","ec
ho 'Raw Nix Build' > $out"],[("builder","/bin/sh"),("name","hello"),("out","/nix/store/fpihphff4y827j4dwy8hpqjcd2z5jd
v4-hello"),("system","aarch64-darwin")])%                                                                            
```
All derivations have the same structure - exhaustive list of all requirements to build a nix package.

So, derivations, in a nut-shell, a plan on how to build a certain nix "package". Before nix creates a build, it first generates this file. In essence, derivations have full information how to build certain package. Nix uses these instructions to do two things:
1. To generate "unique" hash for a package.
2. To encapsulate full input list to create unique builds.

If anything changes in inputs, this will result in unique .drv file, which means new build. By storing it in immutable store, nix ensures that before executing a new build, it is clearly captured. Say, if build fails, because you unplugged the cord of your computer during the build process, next time you but up, you can rebuild the same binary using same `.drv` instructions down to a bit.

Another part is, say if you specified some derivation that nix already build before. Because the hash fully depends on the content of the derivation, nix will generate the same hash. Which means, if build is already in the store, instead of rebuilding, you can safely pull that package instead and have full confidence that it is exactly what you wanted. 

Contrary, if anything changes in the argument, instead of pulling some incompatible package, nix can just use `.drv` file to build the package from scratch. Nix will not update store from derivations with incomplete unsuccessful builds. And even if derivation exists in the store, it does not mean that it can result into successful build!

### 2. Up a level of abstraction: make Derfivation

So far so good. But you may have notices a sneaky issue here. We used "/bin/sh" to "build" our first program. But, this relies on a "leaky" build. Question of the day: which version of bash are we using here? What if new version of bash changes something?

Yes, it will not result into a "hermetic", isolated build. We can not ensure that our build is "vacuum" sealed.

>[!NOTE]
> Unfortunately, if you want fully vacuum sealed, completely pure, no side-effect solution, it becomes almost impossible. Ask yourself this: what hardware we are using? Even if several machines have same hardware architecture, actual machine may be different, and same binary may not work same way on same architecture. Similarly, you can find many other parts of the system that are not perfectly isolated. Perfect isolation means a software that probably can not even run in real world. When we speak about hermetic builds, we go for a lower goal: if two machines use same instructions and produce binaries that generate same hash, that is a win. In other words, we seek logical determinism, not physical/metaphysical identity.

So, let's build the same program to be a bit more deterministic.
```nix
let 
  pkgs = import <nixpkgs> {}; # <...> means import searches from path visible in $NIX_PATH variable 
in derivation {
  name="hermetic-hello"; # name of a derivation
  syste=builtins.currentSystem; # use current system architecture to build, instead of hardcoding
  builder="${pkgs.bash}/bin/bash";  
  args= [
    "-c",
    ''
    echo "Building with: $BASH_VERSION"
    echo 'Hello from Nix' > $out
    ''
  ]; 
}
```
`let/in` syntax helps us to define shorthand names for variables. as you can see, we are searching for nixpkgs from `NIX_PATH`. `(import <nixkpkgs>)` means that are we are getting the content of the module. And you can infer that we are calling it on an empty attribute, that this module stores a "function", that transforms empty attribute set, into an attribute set with packages.

Now, we specify that bash version is the same as the one that is currently available of the `nixpkgs` on a current system. As nix store is immutable, this gives a better guarantee on version of the bash. You could technically build any program like this. Here is example how to build C++ program:
```nix
let
  pkgs = import <nixpkgs> {};
  
  # We need these specific packages
  bash = pkgs.bash;
  gcc = pkgs.gcc;
  coreutils = pkgs.coreutils; # for mkdir and cp
  sourceFile = ./main.cpp; # mainfile in same foder as this nix

in derivation {
  name = "raw-cpp-hello";
  system = builtins.currentSystem;

  # Point to the specific bash binary
  builder = "${bash}/bin/bash";

  # Pass arguments to bash to run our script
  args = [
    "-c"
    ''
      # Setub path to gcc, mkdir, cp
      export PATH="${gcc}/bin:${coreutils}/bin"
      
      # Build
      g++ ${sourceFile} -o hello

      # 3. Install (move to $out)
      mkdir -p $out/bin
      cp hello $out/bin/
    ''
  ];
}
```

Try to build it. It works!

Few issues with this code. What happens if we:
1. add more source code.
2. add more dependencies.
3. are building for a different language(s)?
4. want to build for different system?
5. want to use different version of nixpkgs?

You probably end up writing a lot of similar boilerplate derivations. Nix community went ahead with it, and now, you can specify derivations using `mkDerivation` function. This function transforms an attribute set with high level information, and transforms it into a derivation by filling out some things for you. [Here](https://blog.ielliott.io/nix-docs/mkDerivation.html) is the documentation You need to pass an attributes. `?` symbol in documentation means that field is optional.

Here is simple C++ build for hello world:
```nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.stdenv.mkDerivation {
  pname = "hello-cpp";
  version = "1.0";

  src = ./.; 

  # These are native for stdenv
  nativeBuildInputs = [ 
    pkgs.gcc 
  ];
  # Nix expects a 'buildPhase' to compile and an 'installPhase' to move the binary
  buildPhase = ''
    g++ main.cpp -o hello-cpp
  '';

  installPhase = ''
    mkdir -p $out/bin
    cp hello-cpp $out/bin/
  '';
}
```
`stdenv` provides environment with [standard tools](https://github.com/NixOS/nixpkgs/blob/master/doc/stdenv/stdenv.chapter.md#tools-provided-by-stdenv-sec-tools-of-stdenv), like GCC compiler, `coreutils`, etc. You may also notice that now, this module is a function. The idea is to inject `pkgs` from external, and default to importing local packages if it is not provided. When you run nix commands, they can provide some context as input to modules. Or you can use modules in other modules to inject this and change its behavior.
1. We can add any source files using `src`
2. We can easily add dependencies specified in `pkgs`. 
3. We can use `mkDerivation` for any language in a sandboxed standard environment.
4. So, now our "Build" instructions are system independent. 
5. We can inject different version of `nixpkgs`.

Also, install phase and build phases are optional. You can have simple header only library. All you need is just copy it to results.

### 3. Up level of abstraction: Flakes and External Dependencies

It may seem that we achieved everything we wanted for a build. However, there is one more lurking issue - again, it is hermeticity. You see, our fix for hermeticity was manual, and `mkDerivation` makes it optional, instead of making it enforced. You can still getaway with leaky builds using `mkDerivation`. Here is striking example that is possible:
```nix 
with import <nixpkgs> {};

stdenv.mkDerivation {
  name = "impure-bin-reference";

  # 1. This is the "magic" flag that disables the sandbox for this derivation.
  # Note: This only works if your nix.conf has 'sandbox = relaxed' or 'false'.
  __noChroot = true;

  # 2. We skip adding pkgs.coreutils to buildInputs 
  # so we are forced to use the host's /bin.
  buildCommand = ''
    echo "Accessing the host binary directly:" > $out
    /bin/date >> $out
    /bin/ls /bin | head -n 5 >> $out
  '';
}
```
There are two ways this build is leaky. we are intentionally forcing it to do `_noChroot` to force `/bin/date` and `/bin/ls`. Second one is importing local nixpgs. "it works on my machine". Flakes make it harder to make such leaky builds in few ways:
1. **Lockfile** - you will have `flake.lock` file generated that pins down url for all the inputs used for builds.
2. **Git integration** - flakes require git tracked files to be used as source. Rest are not visible to flakes.
3. **Environment Stripping** - flakes scrub the environment getting rid of variables or access to paths outside what is provided.

Another part of the issue with builds is that you may want to also have some development environment where you can write a code. After all, you don't know how to build a project before you even wrote a code!

#### Dev Workflow with Flakes

1\. Create a Flake with Dev Shell

```nix
{
  description = "Minimal C++ dev shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }: 
    let
      # Change this to "aarch64-darwin" if you are on an M1/M2 Mac
      system = "x86_64-linux"; 
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        # Tools (native)
        nativeBuildInputs = [ pkgs.gcc pkgs.cmake ];

        # Libraries (target)
        buildInputs = [ pkgs.fmt ];

        shellHook = ''
          echo "Environment ready. Run 'g++ main.cpp -lfmt' to compile."
        '';
      };
    };
}
```
2\. enable dev sheell and write code
```bash
>$ nix develop
(nix:develop)>$ touch main.cpp
```
You can write creat simple code:
```c++
#include <fmt/core.h> // inside dev shell, you can use language server and it can find references!

int main() {
    fmt::print("Hello from Nix with {} library!\n", "fmt");
    return 0;
}
```
3\. Either compile it inside shell for experimentation, or define nix steps to compile in a flake. Here is final shell you may end up with:
```nix
{
  description = "A simple C++ Hello World flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      # Change this to match your system (e.g., "aarch64-linux" or "x86_64-darwin")
      system = "aarch64-darwin"; 
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      packages.${system}.default = pkgs.stdenv.mkDerivation {
        pname = "hello-cpp";
        version = "1.1";
        src = ./.;
        nativeBuildInputs = [ 
          pkgs.gcc 
          pkgs.pkg-config
        ];

        # external dependency!
        buildInputs = [ pkgs.fmt ];

        # Build
        buildPhase = ''
          g++ main.cpp $(pkg-config --cflags --libs fmt) -o hello-cpp
        '';
        
        # Test : try to append `exit 1` and build this project
        doCheck = true;
        checkPhase = ''
            echo "Running test..."
            ./hello-cpp | grep "Hello" 
        '';
        
        # Install
        installPhase = ''
          mkdir -p $out/bin
          cp hello-cpp $out/bin/
        '';
      };

     devShells.${system}.default = pkgs.mkShell {
       inputsFrom = [self.packages.${system}.default ];
     };
    };
}
```

Flakes can be build with `nix build` command:
```bash
>$ nix build .
```
Of course, above flake only supports only Apple Silicon Macbooks, but you can extend it to support any system with small change (hint: use `nixpkgs.lib.genAttrs`)

You can even have tests! Also, you if you push it to github, you can use it directly and depend on it in your nix configurations!
```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    
    # Private GitHub repo using SSH
    my-private-project.url = "git+ssh://git@github.com/your-user/your-repo.git";
    
    # Or, if using the github: shorthand (requires local git/SSH setup)
    # my-private-project.url = "github:your-user/your-repo";
  };

  outputs = { self, nixpkgs, my-private-project }: {
    # You can now use my-private-project.packages.aarch64-darwin.default
  };
}
```
