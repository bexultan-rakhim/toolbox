# Nix as a Build System

## What
This tutorial covers using [Nix](https://nixos.org/learn/) as a build system.

Before exploring these examples, I suggest checking out [this tutorial](../nix_as_package_manager/README.md) on using Nix as a package manager.

## Why
Nix is a purely functional language. The Nix package manager creates an immutable `/nix/store` where every build and package is unique. Furthermore, Nix includes the functionality to describe exactly how to build these packages. This tutorial provides hands-on examples of how to use Nix to build your projects. All examples are located within this folder, so you can clone the repository and follow along.

In this tutorial, we will progress from the fundamentals of the Nix language to simple builds, climbing the levels of abstraction in this order:
1.  **Nix language**
2.  **Nix derivations**
3.  **make Derivations (`mkDerivation`)**
4.  **Flake Derivations**

---

## How

First, what is a build system? For a comprehensive answer, check out [this resource](https://j3t.ch/tech/whats-a-build-system/), which provides an excellent visual illustration of build systems. According to the definitions there, Nix is not a "full-fledged" build system—but it certainly can be!

Let’s start with a simpler goal: building programs. Can we build programs with Nix?

### 1. Nix Language 
First, let's get familiar with the Nix language. You can think of Nix as a set of functions (as in functional programming) operating on attribute sets. A simple function in Nix looks like this:
```nix
func = a: b: a + b; # A function that adds two numbers
```
Here is a simple attribute set. You can think of these as "immutable" dictionaries:
```nix
myattrset = {
  field1 = "hello";
  field2 = 123;
};
```
And here is a function that transforms one attribute set into another:
```nix
attrFunc = { arg1, arg2, ... }:
{
  out1 = arg1;
  out2 = arg2;
};
```
Note the use of `...` to specify that the function can accept other "hidden" arguments. This helps implement polymorphic behavior. You will notice that modules and flakes in Nix are essentially definitions of specialized functions. Typically, you will have a file containing only lambda functions:
```nix
{ config, nixpkgs, ... }: {
  imports = [];
  # ...
}
```

### 2. Raw Derivation
Imagine we have a simple build requirement. We want to write Nix code that takes inputs and transforms them into outputs. Since we are interested in the build process rather than just running code, we need output files transformed from source code and dependencies:

```text
INPUTS                BUILD SYSTEM                OUTPUTS
+-------------------+   +--------------------+   +------------------+
| - Source Code     |   |                    |   | - Binaries (.exe)|
| - Dependencies    | ----> |   Transformation   | ----> | - Data Files     |
| - Build Tools     |   |      Process       |   | - Packages       |
+-------------------+   +--------------------+   +------------------+
```

For our purposes, we must introduce one more built-in Nix concept. At the core of the Nix language is the built-in [derivation](https://nix.dev/manual/nix/2.22/language/derivations) built-in keyword, which modifies attribute sets to generate derivations. A derivation attribute set requires specific fields. Here is a minimal set of required fields:

```nix
derivation {
  name = "hello";              # The name of the derivation
  system = "aarch64-darwin";    # The system architecture for the build
  builder = "/bin/sh";         # The absolute path to the executable used to perform the build
  args = ["-c", "echo 'Hello from Nix' > $out"]; # Arguments to the builder. 
  # Note: Your derivation MUST produce a file. $out represents the build result.
}
```

Save this to a Nix file, such as `raw.nix`. To "build" it, run:
```bash 
$ nix-build raw.nix
```
If you check the folder, you will see a new `result` object. This is a symlink to an immutable file in the Nix store:
```bash
$ ls .
raw.nix result
$ readlink result
/nix/store/iaz2wqpzq046s7g8dpxkfpdp7isnm200-hello
```
If you check the content of `result`, it contains our message:
```bash
$ cat result
Hello from Nix
```

#### What is happening here?
You might ask, "What just happened?" Let's unveil the magic. The [Nix architecture](https://nix.dev/manual/nix/2.22/architecture/architecture) documentation explains the high-level build process where Nix expressions are evaluated by the language evaluator to produce build plans (derivations), which are then built into results in the Nix store.

There are three different types of objects stored in the Nix store:
1.  **Inputs:** Source code, libraries, data files, dependencies, and build tools.
2.  **Build plans:** These are the **derivations**.
3.  **Build results:** These are essentially the same as inputs—new binaries, executables, or dependencies.

Inputs and results are straightforward. But what exactly are **derivations**? You can find many files in the Nix store ending in the `.drv` extension:
```bash 
$ ls /nix/store | grep ".drv"
```

You can generate a derivation for `raw.nix` using the command-line tool:
```bash
$ nix-instantiate raw.nix
/nix/store/gcb5bf47ljdpfrcryrxqf8vdk45j3pzv-hello.drv
```
Inspecting its content reveals:
```bash
$ cat /nix/store/gcb5bf47ljdpfrcryrxqf8vdk45j3pzv-hello.drv
Derive([("out","/nix/store/fpihphff4y827j4dwy8hpqjcd2z5jdv4-hello","","")],[],[],"aarch64-darwin","/bin/sh",["-c","echo 'Raw Nix Build' > $out"],[("builder","/bin/sh"),("name","hello"),("out","/nix/store/fpihphff4y827j4dwy8hpqjcd2z5jdv4-hello"),("system","aarch64-darwin")])
```
All derivations share the same structure: an exhaustive list of all requirements to build a Nix package.

In a nutshell, a derivation is a plan for how to build a specific Nix "package." Before Nix executes a build, it first generates this file. Derivations allow Nix to do two things:
1.  **Generate a unique hash** for a package.
2.  **Encapsulate the full input list** to create reproducible builds.

If any input changes, it results in a unique `.drv` file, which triggers a new build. By storing these in an immutable store, Nix ensures the process is clearly captured. If a build fails (e.g., your computer loses power), you can rebuild the exact same binary later using the same `.drv` instructions.

Furthermore, if you specify a derivation that Nix has already built, Nix will generate the same hash. If that build already exists in the store, Nix pulls the existing package instead of rebuilding it, providing full confidence that it is exactly what you requested. 

Conversely, if an argument changes, Nix won't pull an incompatible package; it will use the new `.drv` file to build from scratch. Nix does not update the store with incomplete or unsuccessful builds.

---

### 3. Up a Level: mkDerivation

So far, so good. However, you may have noticed a "leaky" issue. We used `/bin/sh` to build our first program. This relies on the host system. Which version of `sh` or `bash` are we using? What if a new version changes something?

This is not a "hermetic" or isolated build. We cannot guarantee the build is "vacuum-sealed."

> [!NOTE]
> Achieving a perfectly vacuum-sealed, side-effect-free solution is nearly impossible. Hardware architectures differ, and the same binary may behave differently on different machines. When we speak of hermetic builds, we aim for a practical goal: if two machines use the same instructions and produce binaries with the same hash, that is a win. We seek logical determinism, not metaphysical identity.

Let's make our program more deterministic:
```nix
let 
  pkgs = import <nixpkgs> {}; # <...> searches the $NIX_PATH
in derivation {
  name = "hermetic-hello";
  system = builtins.currentSystem; # Use the current system architecture instead of hardcoding
  builder = "${pkgs.bash}/bin/bash";  
  args = [
    "-c"
    ''
    echo "Building with: $BASH_VERSION"
    echo 'Hello from Nix' > $out
    ''
  ]; 
}
```
The `let/in` syntax defines shorthand names for variables. `import <nixpkgs> {}` imports the package module and calls it with an empty attribute set, which returns an attribute set of packages. Now, we specify that the version of Bash used is the one currently available in `nixpkgs`. Since the Nix store is immutable, this provides a much better guarantee.

Here is an example of building a C++ program:
```nix
let
  pkgs = import <nixpkgs> {};
  
  bash = pkgs.bash;
  gcc = pkgs.gcc;
  coreutils = pkgs.coreutils; # For mkdir and cp
  sourceFile = ./main.cpp;     # A source file in the same folder

in derivation {
  name = "raw-cpp-hello";
  system = builtins.currentSystem;

  builder = "${bash}/bin/bash";

  args = [
    "-c"
    ''
      export PATH="${gcc}/bin:${coreutils}/bin"
      
      # Build
      g++ ${sourceFile} -o hello

      # Install (move to $out)
      mkdir -p $out/bin
      cp hello $out/bin/
    ''
  ];
}
```
This works! However, writing raw derivations for every project leads to significant boilerplate, especially when adding more source code, dependencies, or supporting different languages and systems.

To solve this, the Nix community created `mkDerivation`. This function transforms a high-level attribute set into a full derivation by filling in standard details for you.

Here is a simple C++ "Hello World" build using `mkDerivation`:
```nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.stdenv.mkDerivation {
  pname = "hello-cpp";
  version = "1.0";

  src = ./.; 

  nativeBuildInputs = [ 
    pkgs.gcc 
  ];

  buildPhase = ''
    g++ main.cpp -o hello-cpp
  '';

  installPhase = ''
    mkdir -p $out/bin
    cp hello-cpp $out/bin/
  '';
}
```
The `stdenv` (standard environment) provides tools like the GCC compiler and `coreutils`. By making the module a function, we can inject `pkgs` from the outside or default to local packages. This approach makes our build instructions system-independent and allows us to easily inject different versions of `nixpkgs`.

---

### 5. Up a Level: Flakes and External Dependencies

Even with `mkDerivation`, hermeticity remains a potential issue because it is often optional rather than enforced. It is still possible to create "leaky" builds. **Flakes** make it much harder to create leaky builds by:
1.  **Lockfiles:** `flake.lock` pins the exact URLs and hashes for all inputs.
2.  **Git Integration:** Flakes require files to be tracked by Git; untracked files are invisible to the build.
3.  **Environment Stripping:** Flakes scrub environment variables and restrict access to paths outside the provided inputs.

#### Dev Workflow with Flakes

**1. Create a Flake with a Dev Shell**
```nix
{
  description = "Minimal C++ dev shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }: 
    let
      # Change to "aarch64-darwin" for Apple Silicon
      system = "x86_64-linux"; 
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        nativeBuildInputs = [ pkgs.gcc pkgs.cmake ];
        buildInputs = [ pkgs.fmt ];

        shellHook = ''
          echo "Environment ready. Run 'g++ main.cpp -lfmt' to compile."
        '';
      };
    };
}
```

**2. Enable the Dev Shell and Write Code**
```bash
$ nix develop
(nix:develop)$ touch main.cpp
```
Example code using the `fmt` library:
```cpp
#include <fmt/core.h> 

int main() {
    fmt::print("Hello from Nix with the {} library!\n", "fmt");
    return 0;
}
```

**3. Define Build Steps in the Flake**
Here is a complete flake that handles both development and building:
```nix
{
  description = "A multi-system C++ Hello World flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      # Define the systems you want to support
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];

      # Helper function to generate an attrset '{ x86_64-linux = f "x86_64-linux"; ... }'
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;

      # Standard nixpkgs instantiation for each system
      pkgsFor = system: nixpkgs.legacyPackages.${system};
    in
    {
      packages = forAllSystems (system: {
        default = let pkgs = pkgsFor system; in pkgs.stdenv.mkDerivation {
          pname = "hello-cpp";
          version = "1.1";
          src = ./.;
          
          nativeBuildInputs = [ 
            pkgs.gcc 
            pkgs.pkg-config
          ];

          buildInputs = [ pkgs.fmt ];

          buildPhase = ''
            g++ main.cpp $(pkg-config --cflags --libs fmt) -o hello-cpp
          '';
          
          doCheck = true;
          checkPhase = ''
            echo "Running tests on ${system}..."
            ./hello-cpp | grep "Hello" 
          '';
          
          installPhase = ''
            mkdir -p $out/bin
            cp hello-cpp $out/bin/
          '';
        };
      });

      devShells = forAllSystems (system: {
        default = let pkgs = pkgsFor system; in pkgs.mkShell {
          inputsFrom = [ self.packages.${system}.default ];
        };
      });
    };
}
```

Build the flake using:
```bash
$ nix build .
```
You can even include tests (`checkPhase`) and depend on other private or public Git repositories directly:
```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    my-private-project.url = "git+ssh://git@github.com/your-user/your-repo.git";
  };

  outputs = { self, nixpkgs, my-private-project }: {
    # Access via my-private-project.packages.aarch64-darwin.default
  };
}
```

## Bonus: Flake for Python
How about interpreted language? Say you want to just expose this python file as executable in nix:
```nix
import sys
import requests  # Let's add a dependency to make it interesting


def main():
    print(f"Hello from Python {sys.version}!")
    print(f"Requests version: {requests.__version__}")


if __name__ == "__main__":
    main()
```
To execute it, you would normally do this: `python hello.py`. However, it won't work in a "binary form". We can add shebang `#!/usr/bin/env python` to mark it as python, then you can remove extension `.py`, mark it as executable. But notice that we refer to non-isolated `/usr/bin/env`. Solution to this problem then is two-fold:
1. Create isolated nix-environment `/nix/store/<hash>-python-env`
2. Inject it to this source file!

You can imagine nix flake pseudo-code to have following skeleton:
```nix
let
  buildStep = envBuilder {
    #build isolated env
  };
in
modifiedFile = buildStep readFile ./hello.py; 
```

There are already Nix functions to do exactly this. Here is a flake:
```nix 
{
  description = "A hermetic Python hello world";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "aarch64-darwin";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      packages.${system}.default = pkgs.writers.writePython3Bin "hello-python"
      {
          libraries = [pkgs.python3Packages.requests];
      } (builtins.readFile ./hello.py);


      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [ 
          (pkgs.python3.withPackages (ps: [ ps.requests ])) 
        ];
      };
    };
}
```
