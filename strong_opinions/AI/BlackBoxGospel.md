The Black Box Gospel: How Opaque Models Created a Culture of Wishful Thinking in Big Tech
=========================================================================================

Opinion
-------

**I believe opaque models created a culture of wishful thinking in Big Tech.** The fact that neural networks are black boxes — systems whose internal reasoning cannot be meaningfully inspected — has, in my view, produced an engineering culture where confident claims about model capability survive far longer than they should. I see smart people, including seasoned engineers and researchers who should know better, saying things about how models work that are simply not how they work. And I think the opacity of the models gives those claims just enough cover to avoid being killed.

I am not talking about hype from marketing departments. That is expected and uninteresting. What I am talking about is technically literate people making claims that conflate *what we cannot inspect* with *what we cannot know*. The black box of the weights has been quietly extended, without justification, into a black box over everything — architecture, training regime, structure, mechanism. The honest epistemic position — "we do not know, how do we validate this?" — gets crowded out by confident assertions in both directions, optimistic and pessimistic alike.

Look at what passes for serious discourse at the highest levels of the field. Sam Altman, CEO of OpenAI, wrote in a widely-read post that his company is "now confident we know how to build AGI as we have traditionally understood it" and has already pivoted its attention to superintelligence. Elon Musk has publicly predicted AGI will arrive "this year or next." These are not idle blog commenters. These are the people allocating hundreds of billions of dollars and setting the public's expectations for what this technology is and will become.

I also want to be clear: the skeptics are not more honest — they are just confident in the opposite direction. Yann LeCun, Meta's former chief AI scientist and Turing Award winner, has declared flatly that "there's absolutely no way" autoregressive LLMs will ever reach human-level intelligence. This is a strong architectural claim, stated with maximum certainty, about a system the field does not fully understand. Maybe he is right. But "absolutely no way" is not the language of someone who has rigorously proven a bound. It is the language of someone who is very sure of their mental model — and I think that distinction matters enormously.

I also believe there is a less discussed but equally important driver of this problem: researcher ego. A meaningful portion of the people making overconfident claims are not doing so out of naivety. They are doing so because they believe they *get it* in a way others do not. Their mental model is the correct one. The black box protects them. And I see that the culture rewards the confident over the careful.

The broken clock is right twice a day. I do not think the fact that some optimistic claims about emergent capability turned out to be directionally correct validates the reasoning that produced them. You do not get credit for a correct conclusion built on a flawed argument. And I observe the field has been far too generous in granting that credit.


Rationale
---------

The mechanism behind this problem has three parts that reinforce each other.

**The first is what model opacity actually means — and what it does not.** I want to be precise here, because I think the common framing of neural networks as pure black boxes is itself an overstatement that feeds the problem. Neural networks are not uniformly opaque. In a convolutional neural network, the early layers are quite interpretable: they learn to detect edges, simple textures, and color gradients — features that can be directly visualized and inspected. Zeiler and Fergus demonstrated this rigorously in 2014, introducing a deconvnet visualization technique that projects intermediate feature activations back into pixel space, revealing what each layer is actually responding to [1]. Early layers show clean, recognizable patterns. I do not find this mysterious.

What happens in later layers is genuinely different, and I argue this is where things get interesting. As depth increases, representations become increasingly abstract and high-dimensional. Networks learn features with no direct human-language equivalent. Bau et al.'s Network Dissection project at MIT (2017) formalized this by matching individual CNN units to human-labeled semantic concepts — and found that networks trained on scene classification spontaneously developed detectors for "tree," "door," "building facade," and dozens of other object concepts that were *never explicitly labeled in the training data* [2]. The network, given only scene-level labels, internally organized itself around object-level representations because they were useful for solving the task. I find this remarkable — and it is genuinely not fully understood.

Here is the distinction I want to draw: the early layers are interpretable. The later layers develop representations that correspond to human concepts but in dimensions and combinations we cannot straightforwardly read. And beyond a certain depth — particularly in large language models, where the input space is language and the feature dimensions number in the thousands — the representations become genuinely unintuitive. Not because inspection is impossible in principle, but because human vocabulary runs out. Bau et al. also found that 193 out of 512 channels in a given late layer simply did not align with any human concept they could label [2]. I believe this is the honest account of what "opacity" actually means — and it is more specific and more interesting than the blanket "black box" framing most people reach for.

My argument is this: this real and specific opacity in later layers gets carelessly generalized into a claim that nothing is knowable — and that claim then gets used as cover for assertions that have nothing to do with weights or representations at all.

**The second part is the alchemy culture I see around this opacity.** Batch normalization is the cleanest example I know of. In 2015, Ioffe and Szegedy introduced it as a solution to *internal covariate shift* — the problem of layer input distributions shifting during training as earlier layers update [3]. The paper was clear on the mechanism: normalize layer inputs across mini-batches, reduce that shift, training stabilizes. That explanation became gospel. Batch norm was adopted everywhere, in virtually every serious architecture, because it worked spectacularly well.

Then in 2018, Santurkar et al. published a paper with a title that doubled as a verdict: *"How Does Batch Normalization Help Optimization? (No, It Is Not About Internal Covariate Shift)"* [4]. They demonstrated that batch norm's benefits persist even when internal covariate shift is *deliberately increased* after normalization — the very thing it was supposed to fix had little to do with why it actually helped. Their finding: batch norm works primarily by smoothing the optimization landscape, making gradients more predictable. The original explanation was wrong. Three years of adoption, thousands of citations, and the mechanism everyone cited was not the real one.

This is the pattern. The field discovers a technique, attributes it to a mechanism, builds lore around that mechanism, and practitioners use the technique without ever revisiting whether the mechanism was correctly identified. Nobody gets fired because the loss curve still goes down. The ritual works even when the theory does not. But I believe a culture built on unvalidated mechanisms is a culture with no immune system against bad claims — and that is exactly what I see.

**The third part is the research culture itself.** The ML field has a well-documented reproducibility crisis that I argue is under-discussed relative to its severity. Systematic reviews have found reproducibility failures across at least 17 different fields that have adopted ML methods, collectively affecting hundreds of papers and producing wildly overoptimistic results in some cases [5]. A significant driver is data leakage — where information from test sets bleeds into training — a flaw subtle enough to survive peer review but severe enough to invalidate findings entirely. Beyond methodology, I believe the culture of "publish or perish" creates systematic incentive toward selective reporting, corner-cutting, and what researchers themselves call "questionable research practices" [6].

Into this environment, ego enters as an accelerant, and I think this is something the field does not talk about honestly enough. Look at the public dispute between LeCun and cognitive scientist Gary Marcus — a years-long argument about who was first to criticize the scaling hypothesis for LLMs, who originated the idea of world models, and who deserves credit for predicting the limitations of deep learning. Marcus has documented how LeCun repeatedly presented ideas as his own that had clear predecessors, calling it a "consistent pattern" of appropriating others' work without attribution. LeCun publicly attacked Marcus's early critiques of LLMs, only to later advance nearly identical positions — without acknowledgment. I do not raise this to take sides. I raise it because it is a perfect exhibit for what happens when professional stakes get tangled with technical claims: two smart people, in the same field, unable to agree on basic facts, because being the person who "got it right" is worth too much to concede.

I believe this is not unique to those two. A researcher who thinks their mental model of a system is superior has little reason to say "we do not know." They have every incentive — career, status, citation count — to publish a confident claim in a format that looks like the other confident claims. Peer review cannot reliably catch this because reviewers are operating under the same opacity. The black box protects the claim. The paper format lends it legitimacy. I believe wrong mental models survive and propagate because the system has no reliable mechanism to kill them.

What gets lost in all of this is a distinction that is not actually that hard to make. There are things you genuinely cannot know about a neural network without dedicated interpretability research. And there are things you *can* know with certainty from the architecture and training regime alone, requiring no inspection of the weights whatsoever.

A classifier trained to distinguish A from B, once training is complete, has fixed weights. It cannot update those weights from its own predictions at inference time. It has never seen class C, so it has no learned representation of C. These are not probabilistic claims. They are architectural facts. Yet I keep seeing the cultural posture of "we cannot really know what these models can do" invoked to muddy even these straightforward claims. I think that is a category error — using opacity over the *weights* as justification for agnosticism about *everything* — and I believe it has become normalized to the field's serious detriment.

I want to be clear about one group I am not targeting: researchers doing genuine interpretability work. They are honestly acknowledging uncertainty and building rigorous methods to reduce it. They are asking "how do we validate this?" rather than asserting an answer. My critique is aimed at everyone else — the engineers, product leads, executives, and ego-driven researchers who borrow the language of that uncertainty without doing any of the work.

The position I am arguing for is not radical. Be precise about what kind of claim you are making. If it concerns the weights, say you are speculating. If it concerns the architecture, reason from the architecture and commit to the conclusion. The black box over the weights is real. The black box over everything else is a choice — and it is a choice the field keeps making, at considerable cost to its credibility.


Updates
-------

*Nothing yet.*

---

**References**

1. Zeiler, M.D. & Fergus, R. (2014). *Visualizing and Understanding Convolutional Networks.* ECCV 2014. https://arxiv.org/abs/1311.2901
2. Bau, D., Zhou, B., Khosla, A., Oliva, A. & Torralba, A. (2017). *Network Dissection: Quantifying Interpretability of Deep Visual Representations.* CVPR 2017. https://netdissect.csail.mit.edu/
3. Ioffe, S. & Szegedy, C. (2015). *Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift.* ICML. https://arxiv.org/abs/1502.03167
4. Santurkar, S., Tsipras, D., Ilyas, A. & Madry, A. (2018). *How Does Batch Normalization Help Optimization? (No, It Is Not About Internal Covariate Shift).* NeurIPS. https://arxiv.org/abs/1805.11604
5. Kapoor, S. & Narayanan, A. (2023). *Leakage and the Reproducibility Crisis in ML-based Science.* Patterns. https://reproducible.cs.princeton.edu/
6. Semmelrock, H. et al. (2025). *Reproducibility in Machine Learning-based Research: Overview, Barriers and Drivers.* AI Magazine. https://arxiv.org/abs/2406.14325
7. Altman, S. (2025). *Reflections.* https://blog.samaltman.com/reflections
8. LeCun, Y. (2025, January). Interview at CES. Via PYMNTS. https://www.pymnts.com/artificial-intelligence-2/2025/meta-large-language-models-will-not-get-to-human-level-intelligence/
9. Marcus, G. (2025). *The False Glorification of Yann LeCun.* Marcus on AI. https://garymarcus.substack.com/p/the-false-glorification-of-yann-lecun
