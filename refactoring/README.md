# Code Refactoring
## What
This folder contains some code refactoring materials, that I found really useful over the years. It is sorted by topic and contains readme files with materials on specific topics.

## Why
Over the years, I have found that on specific languages you face the same type of problems and they have same type of treatment. Oftentimes, they are pretty specific, that you can apply easily. I wanted to have a single repository of such methods that I can share as examples instead of explaining it 100th time.

Before diving in, I want to specify what I look for refactoring. Point of refactoring for me is not some "ideal" code structure that encourages people to take unnecessary [Prima Donna Programmer](https://wiki.c2.com/?PrimaDonna) attitude that snobbishly looks at code and like a grammar nazi critiques your if-statements. Here is how I understand refactoring:

**Refactoring - changing code structure, without changing behavior to make it easier for new members to work on the software or easily trace errors.**

In other words there are three main measurable objectives:
1. No Change in behavior - can be observed in many ways: change in behavior as failing requirements, added bug(s), or failing tests.
2. Ease of Onboarding to Codebase - can be measured by time it takes to contribute
3. Ease of Debugging - can be measured by time spend finding bugs

All the other reasons such as aesthetics, abstraction, coupling etc. are not objective of refactoring. They are **design concerns**. You have to just accept that bad design can not be solved by hours of refactoring in hopes of arriving at good structured code. There is a saying in Russian "No matter how much you knead shit, it won't become a pie". You have to design in advance, and refactoring can help to facilitate this process. So, they are related, but orthogonal concepts.

### Patterns of Bad Code - Code Smells
There is a concept of **Code Smells** in refactoring. In short, this is a way of training your eye and categorize (anti-) patterns of coding. Bad code smells may be indicators of bad code, but not reason. Sometimes, bad code smells are not a problem at all! That said, when I see bad code smells, I find myself struggling to debug or to understand the code. 

## How
You can find all the in each readme file.

### Refactoring Resources
I do not like reinventing wheel. Whenever I can, I just reference some of these resources.

**Online Resources**
* [Refactoring Guru](https://refactoring.guru/) - web page that categorizes refactoring based on code smells.
* [ArjanCodes](https://www.youtube.com/arjancodes) - YouTube channel that demonstrates step-by-step python code refactoring. Good resource for learning.

**Books**
* M. Fowler, K. Beck - [Refactoring: Improving the Design of Existing Code](https://www.amazon.co.jp/-/en/Refactoring-Improving-Existing-Addison-Wesley-Signature/dp/0134757599) - Advice in this book are timeless, and apply to many different languages. 

> [!WARNING]
> The worst possible book to read on this topic, by far, is [Clean Code](http://cleancoder.com/products). 
> Reason: Many advice in the book are ill-formed or outdated. The book has clearly good intention and provides some of the unwisest decisions to achieve those goals. You can read these books with fair bit of skepticism.
> My personal remark is that dogmatic followers of this book tend to be the worst type of "Prima Donna" developers ever.  
