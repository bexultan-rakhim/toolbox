# Software Design 
## What
Please, read this document to the end if you want to learn what software design is.
This folder contains some of my favorite design patterns and architecture styles, as well as software designing techniques. (Work in Progress). 
## Why
Software design is the most engineering and artistic part of the software development. This is part of software development that is not as strict as "Computer Science", in a sense that there are no objective solution. Before diving in to software design, we should define some of the important terms that are used in the language of software desing, and why this process tends to be subjective.

### Crux of the Designg Problems
If you ask what is the optimal algorithm to searh an element in a sorted list, you have an answer - binrary search. This problem has optimal algorithm. We discovered this algorithm, problem is solved, we move on. This is a type of problem that has **well-defined** problem statement. Having well-defined objective guides us a search of an algorithm that solves it in an optimal way. Sometimes, you can have well-defined objective, but search space is so big, that you may not have simple and easy solutions or can not be practically solved. We call such problems **intractable**. However, these problems, have well-defined objective and when you see solution, you can recognize that you do not need to search further. What if your defining an objective itself is part of the problem?

**Design Problems** - type of problems, where you have to juggle both objective and solutions. For example, think about coming up with a form for a cup. Your solution will change based on how you understand the problem. That is why you have cups of so many different forms. At the high level, you can think of cups, for example, as "an object formed to hold liquids". Let's start defning our objecive function. Well, you want it to be "easy to grasp", "hold enough liquid, for few sips, but not too much to become a bowl", so what else? Turns out, you can come up with infinite list of requirements for a cup, that can be sorted by relevance, but still. One of the requirements, unironcically, will be "Do not blow up the Moon, during the process of making a cup". This may sound strange, but how to sort infinite list of requirements based on relevance? How to evalutate relevance in a first place?

Second issue, even if you come up with some shortlist of requirements, finding a solution can pose a problem as well, as you may not immediately recognize that some objectives you put forward may be in direct contradiction to each other. And you may end up discovering this only when you start solving the problem. 

We figured out how to find solutions effectively even for problems like these. I would not have writtent so much text if we did not have. 

**Design Process** - effective way of solving design problems. Unfortunately, design problems nature turn them into intractable problem, but aside from some forms of intractable problems, you can make progress in solution by gradually converging to both solution and problem statement. Design process has a **design interation**:

```mermaid
graph TD
    %% Node Definitions
    Problem(["<b>1. Problem Statement</b><br/>Listing fitness objectives"])
    Solution(["<b>2. Solution</b><br/>Producing a form that fits objectives"])
    Evaluation(["<b>3. Evaluation</b><br/>Checking fit & 'hidden' objectives"])
    Iteration{{"<b>Next Iteration</b>"}}

    %% Flow
    Problem ==> Solution
    Solution ==> Evaluation
    Evaluation ==> Iteration
    Iteration -.->|Refine Objectives| Problem

    %% Styling
    style Problem fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style Solution fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style Evaluation fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    style Iteration fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,stroke-dasharray: 5 5
```

The best book that recognizes this process comes from a [Christopher Alexander's](https://en.wikipedia.org/wiki/Christopher_Alexander) [Notes on the Syntesis of Form](https://en.wikipedia.org/wiki/Notes_on_the_Synthesis_of_Form).

### Software Design
Now, we have to turn back into software engineering, and problems for software design. Software, as compared to hardware, have different type of design problems associated. The biggest merit of sofware is that it is "modlable" and **Ease of Change**. You can, in fact, measure the quality of software on this - **Cost of Change** (in a sense of satisfying "new" requirements). **Cost of Maiantenence** is related concept - cost of change, related to preserving the software and maintaining its usability without adding new features. Some software changes are trivial and tractable, as mentioned above, and have rather straightforward solutions. Such changes are not design problems. 

However, sometimes, we meet type of a problem, for example, that can come in a form of a new requriement where you can recognize that if done naively, it will turn your software into unmaintainable mess - that is, change that is hard to rework or maintain later. Anything that sitfles the ease of change of a software strips software of its main merit. At the end of the day, why make life harder by solving a hardware problem with software? If you can easily make it part of a hardware itself? If you can guarantee that you do not need a rework, that is. You merit a little from a cup that can programmatically change its form, right? We know for a fact that if we have a software problem, then by its nature, it is meant to be changed. So, this problem is not trivial, and what are the objectives? Ease of change, but this is still too vague and general to be actionable. Similar to many of the design problems, you can come up with a list of requirements.

**Software Design** - Type of software development problems that juggle ease of change of a sofware with a solution to satisfy requirements.

What makes software easy to change? Lines of code (LOC)? Well, if you have 1000 lines of somewhat repeptitive code, this does not make it harder to maintain or change. Even if it is 1000,000 lines, you could imagine writing simple script to add new stuff, or ask your LLM to do this for you.

**Software Complexity** - is the main culprit that makes software hard to change. Some complex (new) requirements require complex reworks.There are two types of complexity for the softeware:
* **Essential Complexity** - Some complex software exists, because the problem we want to solve with it are as complex. This can not be reduced. 
* **Accidental Complexity** - We may misunderstand requirements, or make shortcuts. Why spend 5 hours to find the best alrogithm that solves this particular problem, that may be 10 lines of code, if you can write 100 lines in 10 minutes that does marginally worse? "Best" is enemy of "better". This is a practical tradeoff. We use this reasoning, modify existing code by adding a bit of worse, and see our codebase rot. This is how all of the accidental complexity is incurred. 

### Software Architecture
As copmlexity of the software grows, we end up with some problems that are really massive. Problems that are in a systems level and require rework of 1000's of LOC in multiple files under multiple directories in your codebase, that can span across multiple services and devices in a distributed network. Architecture problems are indeed design problems of a bigger scale. And in such scales, they have different things that are relevant to them and end up having different set of objectives. You can think of architecture and design problems being on a spectrum of complexity, where less complex problems are design problems and more complex problems are architecture problems. 

Architecture problems are like General theory of relativity to gravity, while design problems are like Newtonian gravity. In the vicinity of earth, Newtonian dynamics simpler to apply even if it is less accurate than general relativity. It gets the job done. But closer to the earth, there are ups and downs. Similarly, design problems have somewhat well scoped objectives. If you require rigor at scale, Newtonian gravity does not cut it, same goes with Architecture problems for design problems at larger scale. There are two laws of software architecture that you should know:

1. In software architecture, **everything is a tradeoff**. This means, you can not really discuss about "better" or "worse". "Good software" or "Bad software". Such will not cut it. Remember, "In space, there is no up and down", similarly, in software architecture, there is no good or bad architecture. Any solutions have merits and demerits. Balancing them with the requirements of the software is what matters. No silver bullets - you can not use miroservices for every system. You can not use pub/subs for every communication.
The issue here is not that it will not work, as indeed you can fit either pub/sub or microservices to any software. The issue here is an oppportunity costs of not using something that balances tradeoff of merits to demerits better.
2. **WHY is more important than HOW**. Primary objective of a software architect is, at the end of the day, convince team of developers to take his words seriously and implement the architecture as architect imagined. People do not want to do what they do not understand or do not buy in. Simple as that. Architects can not solve these problems alone, otherwise, it would not have been architecture problem to begin with! And because everything is tradeoff, any developer can argue that he can come up with better solution! "My solution is the best", "No! My solution is better than yours!". Nobody wants to be in shouting matches like this, fueled by ego. Instead, you should just be honest and acknowledge demerits, and provide reasons why accepting those demerits are okay. "I think, we should implement microservcies, because this is how you implement it" is not convincing. "I think we should implement microservices, because we are planning to expand our services in several ways in the future, and although it is more complex, has higher deployment and development overhead, we will be able to spin up new servers on demand and better satisfy our customer needs". This is tangible, you can argue with it by providing data, and developers can get communicated on what is important for the project. 

## How
Let's be pragmatic. You do not need to reinvent wheel and start from the white canvas. Some common problems, have common solutions. You do not need to come up with a new form for a cup. You can just adopt one of existing solutions. Design problems have such solutions - **Design patterns**. Architecture problems, similarly have such solution - **Architecture Styles**. Design pattern merits and demerits can be practicall and easy to apply, but Architecture styles can only specify their merits and demerits.

### Resources

**Online Resources**
- WIP
**Books**
- WIP
