# Atomic Changes
## What
This document introduces a refactoring concept called **atomic change**. Simply put, atomic change is a changes to code that changes the source file and code structure, but **does not change the behavior**. 
## Why
If you start reading any book on refactoring, it will suggest that you should be writing tests to protect correct behavior, so that you can easily modify your code without worrying of breaking anything. Indeed, you should be writing tests. 

However, let's be realistic. More than often than not, you end up in a situation where code you want to refactor is beyond salvation, and writing tests in themselves is a struggle. **How to refactor the code, if it is not even organized in a way to be testable in the first place?** If you have been asking this question, this document is exactly about this topic. So lets clearly define objective of this document.

1. We will try to define an atomic changes - small code modifications safe enough to not require writing tests in advance.
2. We will discuss how to use these steps to extract testable code.

If we can do this, then we can get to point, where regular refactoring techniques become useful again.

> [!WARNING]
> But before going there, I want to give you word of wisdom. Before trying to spend resources untangling a mess, ask yourself: "Is this worth the effort?".
> Remember, point of refactoring is not to achieve some aesthetics. It is about being productive.
> The best way to deal with bad code is not waste time on it. If it is a throwaway code in a long run, consider [putting it into quarantine](https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer).

## How
In a nutshell, learning atomic changes boils down to recognize patterns and apply it. These are patterns on code that can be replaced with its equivalent without any change in behavior, so it is bidirectional changes.

Here are Atomic Changes by topic:
1. [Booleans ](Booleans.md)
2. [If Conditions](If_Conditions.md)
