---
title: Benchmarking Function Calling
summary: How it is done, and what we can understand from it.
---

!!! danger ""

    Note that this page is a work in progress. Not all things mentioned on this page are complete, and some links may be broken.

A benchmark for function calling among various cloud-based and offline models exists in the form of the [Berkeley Function Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html). This project builds on top of this benchmark in the following ways.

### Providing special prompts to the models

Different models require different prompts to bring out the best of their capabilities. The leaderboard, however, provides a [standard system prompt](https://gorilla.cs.berkeley.edu/blogs/8_berkeley_function_calling_leaderboard.html#prompt) to all models. This disadvantages models that do not have a system prompt, and have no prior instructions on how to go about function calling. In addition, this project aims to explore and extend the function calling capabilities of offline models to the fullest extent possible.

Therefore, this benchmark provides to the models a specially crafted prompt that has been observed to give the best results. These prompts are continuously iterated upon to better the function calling capabilities of the models.

### Providing detailed function specifications

The leaderboard test framework provides the models with simple function docs, which include the name of the function, a description of what it does, and the OpenAPI-style schema of the parameters it accepts.

This benchmark provides the models with more detailed function specifications that also include the possible responses and errors that the function may return or raise, as well as examples of its usage.

### Adding more categories/scenarios to the suite

The leaderboard tests [these categories](https://github.com/ShishirPatil/gorilla/blob/main/berkeley-function-call-leaderboard/TEST_CATEGORIES.md#available-individual-test-categories). The tests from the key categories of the leaderboard have been converted to 'scenarios' and stored [here](https://github.com/offline-function-calling/benchmarks/tree/main/scenarios). In addition to the categories tested by the leaderboard, this benchmarks incorporates:

#### Function Generation

Offline models such as Gemma 3 are capable of generating function code and specifications, and then using those functions as and when neeeded. This benchmark adds scenarios that test this capability.

!!! note ""

    [This tutorial](../learn/dynamic-function-generation.md) will teach you how to make use of the dynamic function generation capabilities of the Gemma 3 (27B parameter) model.

#### Error Handling

When a model calls a function, it must be prepared to handle the errors that could occur during the execution of the function. This benchmark tests scenarios that test how well a model can handle and recover from errors and what methods it uses to do so.

#### Constraint Adherence

Sometimes it is necessary to perform a task without access to certain information or a certain function. This benchmark adds scenarios where the model is given various implicit (for example, a function might have a rate limit attached to it) and explicit (a function may not work in so and so situation) constraints, and tests how well it adheres to them.
