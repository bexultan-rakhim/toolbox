# Code Duplication Is Not Bad - It's a Tradeoff

## What
If you take anything from this article, then I want it to be this mantra that you will repeat whenever someone says that code duplication is bad. Repeat after me, out loud:

**Duplication is FAR cheaper than the WRONG abstraction.**

Today's topic of discussion, in essence, is **accidental coupling**. 
## Why
Maybe you have seen or heard this dogma: **DRY** - don't repeat yourself. There is a lot of wisdom in reducing duplication. In many cases, you should strive to reduce duplication, or better to say - do not reinvent the wheel. 

## How

### Rule of Three Repetitions
This is a pragmatic rule of a thumb approach. 
Simply put, when you write something first time, do it as it is.
Second time, you can cringe it, but just duplicate it.
Third time, consider refactoring for DRY. 
