# Semantic Review

## What
Semantic review involves assigning a specific tag to each PR comment. Here is a template:

`[Tag] <message body> [optional] Suggestion`

## Why
To have clear expectations and a definition of Done for each comment. It allows a PR submitter to autonomously close review comments and have clear expectations.

## How
Here is a list of tags and their expectations.

| Tag | Expectation | Explanation |
| :--- | :--- | :--- |
| **crucial** | Code change | Mainly for necessary changes: code standards, linting, convention violations, design flaws, bottlenecks, or suboptimal solutions. |
| **bug** | Code change and test | Reserved for bugs, uncovered edge cases, vulnerabilities, or potential issues. |
| **suggestion** | Code change or comment | Non-critical improvements. Accepted with a code change. If rejected, you must explain why. |
| **question** | Comment | Explanations or clarifications. No code change is expected. |
| **remark** | Acknowledgement | Interesting information for the future. No change required. |

## Examples

* **[bug]** The loop condition here might lead to an off-by-one error. It iterates while `i <= length`, but array indices are typically 0-based, so the last element would be at `length - 1`. [Suggestion: Change the condition to `i < length`.]
* **[crucial]** According to our style guide, variable names should be camelCase. `user_name` should be `userName`.
* **[suggestion]** This section of code could be simplified by using the `.map()` function instead of a traditional `for` loop to achieve the same result.

## How semantic review helps
Consider the following comment:
> *This loop could be less efficient. Maybe consider a different data structure here.*

Check out how the tone changes based on the tag:

* **[crucial]** This loop could be less efficient. Maybe consider a different data structure here. [Suggestion: Consider using a hash map for O(n) lookup.]
    * *A code change is expected, and additional suggestions are needed on how to change it.*
* **[suggestion]** This loop could be less efficient. Maybe consider a different data structure here. It's not critical for this PR, but something to consider for future improvements.
    * *Code change is NOT expected per se, but it would be nice. If rejected, just explain why.*
* **[remark]** This loop could be less efficient. Maybe consider a different data structure here.
    * *Interesting note, but no code change is expected—something to be mindful of in the future.*

