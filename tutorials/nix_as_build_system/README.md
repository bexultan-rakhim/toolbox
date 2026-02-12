# Nix As Build System
## What
This tutorial is about using [nix](https://nixos.org/learn/) as a build system.

Before going through these examples, I suggest checking out [this tutorial](../nix_as_package_manager/README.md) on using nix as package manager.


## Why
Nix is pure functional language. Nix package manager creates immutable `nix/store`, where every build/packages are unique. And Nix has functionality to describe how to build these packages. This tutorial gives hands on examples how to use nix to build your projects. All examples are inside this folder, so you can clone it and follow along.


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

