You Will Not Code in Plain English: On LLMs, Formal Languages, and the Replacement Myth
=======================================================================================

Opinion
-------

**I believe the claim that LLMs will replace programmers is wrong.** Not slightly wrong — categorically wrong. And the related claim, the one I find genuinely embarrassing to hear from technically literate people, is that "you will soon code in plain English." I believe this confuses what LLMs are good at with what programming actually is, and I think the gap between those two things is where most of the hype lives.

I want to be precise about what I am and am not arguing. I am not claiming LLMs cannot produce code. They clearly can. They can produce syntactically valid code, reproduce common patterns, autocomplete boilerplate, and save time on tasks that are essentially text retrieval with mild transformation. And I will go further: I think LLMs are genuinely good at finding bugs — sometimes better than humans, for reasons rooted in how they are trained. That is real and useful, and I will get to it. What I am arguing is that none of that amounts to programming in any meaningful sense, and that the people claiming LLMs will replace programmers or make natural language the new programming interface do not seem to understand what programming actually does.

I should also note that I am not saying anything new here. Edsger Dijkstra said it in 1978, in an essay titled *"On the Foolishness of Natural Language Programming"* [1]. He was writing about a different era's version of the same fantasy, and his argument has not aged in any meaningful way.

I also think there is a specific and underexamined problem driving bad software decisions right now: companies are using LLMs to rewrite and reinvent software that already exists, off the shelf, cheaper and better. They are burning compute and engineering time producing fine-tuned versions of solved problems, because their internal processes are broken and the off-the-shelf solution requires fixing the process rather than the software. I think this is one of the more expensive mistakes the current AI moment is producing, and I do not see it discussed nearly enough.

Rationale
---------

I think the case against the replacement myth rests on five claims, each of which I believe is independently sufficient.

**First: code is a domain-specific formal language, and that formality is the point.** Natural language is ambiguous by design. It works precisely because humans resolve ambiguity through context, shared assumptions, and real-time negotiation of meaning. Code cannot do any of that — and that is not a limitation of code, it is the entire basis of what code does. Code must compile. It must be deterministic. It must map, ultimately, to binary operations on physical hardware. Every layer of abstraction between natural language and machine code exists to make the translation progressively more precise, and the precision is what makes the result operable on a machine at all.

Dijkstra put this more plainly than I can. He described natural language as "wonderful for the purposes it was created for, such as to be rude in, to tell jokes in, to cheat or to make love in" — but "hopelessly inadequate when we have to deal unambiguously with situations of great intricacy, situations which unavoidably arise in such activities as legislation, arbitration, mathematics or programming" [1]. This was a precise technical claim about what formal languages exist to accomplish: they eliminate the ambiguity that natural language not only tolerates but depends on. Proposing to replace code with plain English means proposing to reintroduce that ambiguity into a process that cannot function with it.

Research on the structural difference between natural and programming languages confirms this empirically. Studies comparing code and natural language corpora find that natural language grammars are measurably more non-deterministic and ambiguous than code grammars, and that the entropy differences between them likely arise from the more restrictive formal structure of code, not from any stylistic choice by programmers [2]. The formality is not aesthetic. It is what makes the output meaningful to a machine.

**Second: solving a problem is not the same as writing code, and I do not think LLMs can reliably do the former.** The hard part of programming is not syntax. It is building a mental model of the problem — understanding what it actually requires, what it does not require, what the constraints are, and what the solution space looks like before a single line is written. This conceptualization process is where programming skill actually lives. An LLM prompted to write a solution will write a solution. It will not tell you your problem is underspecified, your data model is wrong, or that you do not need software at all.

I believe what makes this especially hard for current LLMs is something architectural rather than incidental. Human engineers solving novel problems can reorganize their entire mental model mid-solution — recognizing that the original framing was wrong and rebuilding the conceptual structure from scratch in response to what they discover. Research on insight and cognitive restructuring suggests this involves active neural reorganization: new pathways forming in direct response to the problem being worked on [3]. Current LLMs have a static structure during inference and cannot do anything analogous. This is not a claim that LLMs will never be capable of this. It is a claim about how they are trained and structured right now, and I think it is an honest description of the current limitation.

**Third: the compilation contract matters in a way that has no natural language equivalent.** A program either compiles or it does not. A program either produces the correct output for all valid inputs or it does not. These are binary conditions, not matters of interpretation or degree. "Roughly correct," "mostly works," and "handles the common cases" are acceptable ways to describe natural language communication — they are how natural language functions. They are not acceptable descriptions of production software, and they cannot be made acceptable by improving the tool that generates the software. The act of programming is the act of satisfying that contract — taking an imprecise human understanding of a problem and encoding it into something formally correct with respect to a machine. LLMs can produce text that resembles the output of that process, but resemblance is not the same thing as satisfying the contract. There is no free lunch here: you have to validate that it works, so you will be doing exactly what the language model is asked to do beforehand, in the form of a precise specification or tests. Instead, you could have skipped this and just written code. Besides, the most of the cost of the software in its lifetime is maintenance, not initial implementation [7].

**Fourth: not all problems are software problems, and I think this is being systematically ignored.** I am specifically thinking about the wave of LLM-assisted rewrites I see happening right now. Companies are using LLMs to build custom software for problems that have mature, well-supported, off-the-shelf solutions. The reason they are not using the off-the-shelf solution is not that it is inadequate — it is that their internal processes are broken and the off-the-shelf solution requires fixing the process to adopt it. So instead, they build something bespoke that fits the broken process, using LLMs to accelerate the construction, and count it as a productivity win. The LLM did not identify that the real problem was the process. It was not asked to. It was asked to write code, and it wrote code, and now the broken process has a custom software layer on top of it. I may revise my decision when Claude will insist that I just pay for an off-the-shelf solution and it will guide with integration instead of torturing it to reimplement the same.

**Fifth, and this is where I want to be fair: LLMs are genuinely good at finding bugs, and I think this capability is underappreciated.** Research shows that LLM-based critic models catch substantially more inserted bugs than qualified humans paid for code review, with model-written critiques preferred over human critiques in the majority of cases [4]. I think this makes sense given how these models are trained: they have processed more code than any human will read in a lifetime, across more codebases, more languages, more failure patterns. They can recognize a class of error that a human reviewer would miss simply because the human has never encountered that specific failure mode in that specific context. This is a real and useful capability. Why spend 3 days of debugging when AI models can do the same.

What I think is important to separate is that catching bugs in existing code and generating correct code from scratch are not the same task, even though they come from the same underlying capability. Research on bug patterns in LLM-generated code shows the most common categories are misinterpretation of requirements, missing corner cases, and hallucinated objects — calling functions or referencing attributes that do not exist [5]. These are the mistakes of a system predicting what code looks like rather than reasoning about what it needs to do. The pattern recognition that makes LLMs useful for review is the same pattern recognition that produces these specific failure modes in generation, and I think understanding that distinction is more useful than treating LLM coding capability as a single undifferentiated thing.

This gap is visible in practice. Consider a simple quicksort implementation. Ask an LLM to write one and you will get something like this:

```python
def quicksort(arr):
    """
    Sorts a list using the quicksort algorithm.
    
    Args:
        arr: List of comparable elements
        
    Returns:
        Sorted list
    """
    # Base case: arrays with 0 or 1 element are already sorted
    if len(arr) <= 1:
        return arr
    
    # Choose pivot as the middle element
    pivot = arr[len(arr) // 2]
    
    # Partition into three groups
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    # Recursively sort and combine
    return quicksort(left) + middle + quicksort(right)
```

I find this immediately identifiable as AI-generated. The docstring is the first tell — no working engineer writing a utility function begins with a formatted docstring spelling out argument types and return values for an audience that can read the signature. The inline comments restate what the code already says — "Base case: arrays with 0 or 1 element are already sorted" adds no information to a reader who can read Python. The three list comprehensions each iterate the full list, where a single loop would do it once — a cost that a working engineer factors into how they write the function. There is no type checking anywhere, so the function silently accepts anything and fails unpredictably on non-list inputs.

A competent engineer writing this for actual use would write something closer to:

```python
def quicksort(items: list) -> list:
    if not isinstance(items, list):
        raise TypeError(f"Expected list, got {type(items).__name__}")
    if len(items) <= 1:
        return items[:]

    pivot = items[len(items) // 2]
    less, equal, greater = [], [], []

    for item in items:
        if item < pivot:
            less.append(item)
        elif item == pivot:
            equal.append(item)
        else:
            greater.append(item)

    return quicksort(less) + equal + quicksort(greater)
```

No docstring. Explicit type guard up front. One pass through the list. Returns a copy rather than the original reference — a memory assumption baked into the function's contract rather than left implicit. But even this version reads as too uniform, too evenly finished across every line. Human code is meticulous where the problem demanded it and blunt where it did not. It carries the texture of the specific decisions made to solve the specific problem. What I see in LLM-generated code is a consistent surface polish applied everywhere regardless of what the problem actually required — and I think that uniformity comes directly from training on code written to be read and explained, tutorials and documentation and public repositories, rather than code written under real constraints to solve hard specific problems. Polished look is also a contract on how well you understandor care about particular part of the problem. Remember, training to write code is a process of becoming a native speaker in the domain of computers, LLM's speaking plain English is an invitation of machines to the human spaces. 

*Like most articles written today, this one was developed with the help of an LLM — specifically to refine grammar and sharpen how the argument is expressed in plain English. That is, I think, exactly the kind of task language models are genuinely good at. The argument is mine. The polish is collaborative.*

Updates
-------

*Nothing yet.*

---
**References**

1. Dijkstra, E.W. (1978). *On the Foolishness of "Natural Language Programming."* EWD667. https://www.cs.utexas.edu/~EWD/transcriptions/EWD06xx/EWD667.html — and: Dijkstra, E.W. (1996). Foreword to *Teaching and Learning Formal Methods*, ed. C.N. Dean & M.G. Hinchey, Academic Press.
2. Casalnuovo, C. et al. *Studying the Difference Between Natural and Programming Language Corpora.* UC Davis. https://www.cs.ucdavis.edu/~devanbu/ese_main.pdf
3. Kounios, J. & Beeman, M. (2014). *The Cognitive Neuroscience of Insight.* Annual Review of Psychology. https://www.annualreviews.org/doi/10.1146/annurev-psych-010213-115154
4. McAleese, N. et al. (2024). *LLM Critics Help Catch LLM Bugs.* arXiv:2407.00215. https://arxiv.org/abs/2407.00215
5. Tambon, F. et al. (2024). *Bugs in Large Language Models Generated Code: An Empirical Study.* https://arxiv.org/html/2403.08937v2
6. Zan, D. et al. (2023). *Large Language Models Meet NL2Code: A Survey.* ACM. https://arxiv.org/abs/2212.09420
7. Boehm, B. (2007). Software Architectures: Critical Success Factors and Cost Drivers. IEEE Transactions on Software Engineering. * https://api.semanticscholar.org/CorpusID:2094692
