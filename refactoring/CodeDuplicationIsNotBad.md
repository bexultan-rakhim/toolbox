# Code Duplication Is Not Bad - It's a Tradeoff

## What
If you take anything from this article, then I want it to be this mantra that you will repeat whenever someone says that code duplication is bad. Repeat after me, out loud:

**Duplication is FAR cheaper than the WRONG abstraction.**

Today's topic of discussion, in essence, is **accidental coupling**. 
## Why
Maybe you have seen or heard this dogma: **DRY** - don't repeat yourself. There is a lot of wisdom in reducing duplication. In many cases, you should strive to reduce duplication, or better to say - do not reinvent the wheel. 

However, remember the mantra above - **WRONG abstractions are not cheap!**

Let's just simple example here. Look a this simple class:

```python
import requests

class DataClient:
    def get_book(self, book_id):
        # Specific logic for Books
        url = f"https://api.example.com/v1/books/{book_id}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()

    def get_user(self, user_id):
        # Specific logic for Users
        url = f"https://api.example.com/v1/users/{user_id}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
```
This is a simple client for a service that manages Books and Users. Currently, the logic for fetching them is almost identical. Watch this. Here is what happens if you try to DRY.
```python
import requests

class DataClient:
    def _fetch_resource(self, resource_type, resource_id):
        url = f"https://api.example.com/v1/{resource_type}/{resource_id}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()

    def get_book(self, book_id):
        return self._fetch_resource("books", book_id)

    def get_user(self, user_id):
        return self._fetch_resource("users", user_id)
```
This is logical change, if you are in a current time frame.
This is exactly same code, with little duplication. But, the world of programming would have been simple, if not for one small fact - **requirements change**. You see, they also change in a direction where you may not have expected. This change comes with uncertainty on how services evolve in a long run. So, imagine this request for change: The API team decides that `Users` now requires an **OAuth Token**, but `Books` remains **Public**. So, out of necessity to satisfy this requirement now you have to bloat the `_fetch_resources` to have if/else condition to handle user and books differently:
```python
def _fetch_resource(self, resource_type, resource_id, token=None):
    url = f"https://www.google.com/url?sa=E&source=gmail&q=https://api.example.com/v1/{resource_type}/{resource_id}" headers = {"Authorization": f"Bearer {token}"} if token else {}
```
Think why the api has to be in this form for a second.

This is the trap of incorrect abstractions. If you had kept the original duplication, you could be in a better place to evolve the code for users and books separately in much cohesive way. But now, you have complex two sided issue that has to be solved both on server and client side. 

In fact, there was a bigger trap of such form - architecture build for reducing duplicates:
* [Service Oriented Architecture] (https://en.wikipedia.org/wiki/Service-oriented_architecture) - check the wikipedia section on criticisms. It is a good read why we went from this bloatware to microservices.

## How
Question of the day: **How to avoid wrong abstractions?**

Avoiding wrong abstractions is exercise of **restraint**. You have to learn to be pragmatic and [Duct Tape Programmer](https://www.joelonsoftware.com/2009/09/23/the-duct-tape-programmer/). Meaning, form should follow function, form over function. 

### 1. There is so called rule of 3
which serves as a rule of a thumb. This is the gold standard for avoiding premature abstraction.

* 1st time: Just write the code.

* 2nd time: You feel a twinge of guilt, but you duplicate it anyway.

* 3rd time: Now that you have three distinct use cases, the actual pattern becomes visible

### 2. Identify "Similarity" vs "Identity"
Before you unify two functions, ask yourself: "Do these change for the same reason?" (This is the Single Responsibility Principle in disguise).

* **Similarity**: Both a `CancelOrder` button and a `DeleteUser` button are red, have a confirmation popup, and hit a DELETE endpoint.

* **Identity**: They are both "Destructive Action Buttons."

* **The Trap**: If you create a single `RedButton` component, what happens when `CancelOrder` needs to be changed to a "Late Fee" warning? You’ve coupled two unrelated business domains because they happened to "look" the same on Tuesday.

### 3. Design for Deletion, Not Reuse
We often build abstractions as if they are permanent monuments. Instead, build them to be **disposable**.

* Keep your abstractions "shallow." Don't wrap a library (like `requests`) in three layers of your own custom classes.

* If an abstraction is easy to delete, it's a good abstraction. If deleting it requires a 4-hour refactor of the entire codebase, you’ve built a "Wrong Abstraction" cage.
