---
title: Hello, Function Calling!
summary: A look at what it is, what it can do, and how to do it.
---

## What it is

As you read on the overview page,

> Function calling is a powerful construct that allows large language models to use tools and interact with external APIs. It empowers LLMs to go beyond just generating text and actually do real world tasks for you, like checking the weather, re-organizing your files and folders, keeping track of your expenses, and much much more!

Function calling leverages the ability of large language models to understand natural language and produce structured output. It involves five steps:

- **instruction**: instructing the model on how to discover and call functions,
- **discovery**: letting the a model discover the functions that it can call,
- **calling**: letting the model select and call a function with parameters,
- **parsing**: extracting function calls from the model's response, and
- **execution**: running the functions and returning the outputs to the model.

!!! note ""

    Notice how only the `discovery` and `calling` steps are performed by the model. The rest are performed by a program that we will write over the course of this tutorial.

## What it can do

Function calling makes LLMs extremely useful for real world tasks, and being able to run everything offline allows you to protect your data. Since this is an introduction to function calling, this tutorial will focus on this minimal example of fetching the current weather:

/// tab | Without Function Calling

!!! note "`you`"

    &nbsp;What's the weather in Pune right now?

!!! info "`model`"

    &nbsp;The weather in Pune, India right now (November 2, 2023) is:

    * **Temperature:** 27°C (81°F)
    * **Condition:** Clear Sky
    * **Humidity:** 58%
    * **Wind:** 8 km/h

    It's generally warm and pleasant! Expect sunny skies for the rest of the day.

Here, the model is not able to fetch the current weather, and instead relies on its outdated training data - at the time of writing this, the date is June 21, 2025.

Now, click on the **With Function Calling** tab and see how differently the model responds.

///

/// tab | With Function Calling

!!! note "`you`"

    &nbsp;What's the weather in Pune right now?

!!! info "`model`"

        get_weather(location="Pune")

!!! warning "`function output`"

        {
          "conditions": "Patchy rain",
          "temperature": 26,
          "feels_like": 28,
          "wind_speed": 23,
          "units": "metric"
        }

!!! info "`model`"

    &nbsp;The weather in Pune is patchy rain and 26°C (feels like 28°C) with winds at 23km/h.

Here, the model has access to a function named `get_weather`, and calls it in response to the user's message. The function call is parsed and executed by a program, and the function output is returned to the model. The model turns the function's JSON output into a natural language response for the user.

///

## How to do it

!!! note ""

    Before we start, you will need [`python`](../setup/tools.md#python), [`microsandbox`](../setup/tools.md#microsandbox) and [`ollama`](../setup/models.md) setup on your machine. Please refer to the linked setup guides to get them set up.

To empower models with function calling capabilities, we need to follow [the five steps](#what-it-is): _instruction, discovery, calling, parsing, and execution_. Let us get started with the first step.

### Instructing the model

To enable function calling in models, we need to give it some basic information: what functions it can call, when and how it should call them, and how it should process the function's output. We give this information as instructions in a 'prompt'.

In most models, we can provide a 'system prompt', which models are trained to give more importance to. However, some models (such as Gemma 3) [do not have a system prompt](https://ai.google.dev/gemma/docs/core/prompt-structure#system-instructions). In such cases, we will simply prepend our prompt to the first user message.

Let us start crafting our prompt. First, let us inform the model that it has a new capability, and how it should use it.

!!! note ""

    You are a helpful assistant to me, the user. You have access to programmatic functions that you can call to better assist me. You are encouraged to call functions to help the user. You can only use the functions given to you. Do not make up your own functions.

Then, let us tell it how to call a function. We want the model to print a python-style function call when it needs to call a function, and pass the parameters with their names.

!!! note ""

    You can call these functions by producing a python-style function call in plain text only, passing all the parameters as named arguments. For example, to call a function named `do_something`, with the parameter `wait_for_it` set to `true` you must produce the following output: <br />

        :::md
        ```python
        do_something(wait_for_it=True)
        ```

Then, let us give it an idea of how the output will be returned, and what it should do with the output.

!!! note ""

    The output of the function will be returned in the next message from the user. You must use the output of the function to generate a helpful natural language response for the user. Your response must satisfy the user's original question.

Putting it all together, we get our function calling prompt. Click on the clipboard icon to copy the entire prompt as a string.

    :::python
    "You are a helpful assistant to me, the user. You have access to programmatic functions that you can call to better assist me. You are encouraged to call functions to help the user. You can only use the functions given to you. Do not make up your own functions.\n\nYou can call these functions by producing a python-style function call in plain text only, passing all the parameters as named arguments. For example, to call a function named `do_something`, with the parameter `wait_for_it` set to `true` you must produce the following output:\n\n```python\ndo_something(wait_for_it=True)\n```\n\nThe output of the function will be returned in the next message from the user. You must use the output of the function to generate a helpful natural language response for the user. Your response must satisfy the user's original question."

### Letting the model discover functions

Now that we have a prompt that enables the model to call functions, let us provide it with functions to call. Say we have the following python function that fetches the weather using the [`wttr.in`](https://github.com/chubin/wttr.in) API:

```python
import requests

def fetch_weather(place: str) -> dict:
    url = f"https://wttr.in/{place}?format=j1"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    data = data['current_condition'][0]
    return {
        "units": "metric",
        "condition": data['weatherDesc'][0]['value'],
        "temperature": int(data['temp_C']),
        "feels_like": int(data['FeelsLikeC']),
        "wind_speed": int(data['windspeedKmph'])
    }
```

So whenever the model needs to fetch the current weather for a particular place, say Pune, it can generate the following function call:

    :::md
    ```python
    fetch_weather(place="Pune")
    ```

The function will produce a JSON object containing information about the weather condition, temperature and winds in Pune.

To inform the model of this, we can give it the following instruction:

!!! note ""

    When I ask for the current weather for a particular place, you can call the `fetch_weather` function and pass the `place` parameter (a string) with the place I mention. The place can be the name of a city or famous landmark, or an airport code. The function will produce a JSON object containing information about the weather condition, temperature and winds for the given place.

These instructions make up our function discovery prompt. Click on the clipboard icon to copy the entire prompt as a string.

    :::python
    "When I ask for the current weather for a particular place, you can call the `fetch_weather` function and pass the `place` parameter (a string) with the place I mention. The place can be the name of a city or famous landmark, or an airport code. The function will produce a JSON object containing information about the weather condition, temperature and winds for the given place."

This prompt helps the model 'discover' the `fetch_weather` function.

### Getting the model to call functions

Upto this point in the tutorial, we have not written any code at all! That's because half of function calling is ensuring that the model is provided the right instructions and functions so it can call them as needed.

Let's start by selecting a model and writing code to chat with it via `ollama`.

```python
model = "gemma3:27b"
```

We'll be using the Gemma 3 (27B parameter) model, since it is [good at function calling](../bench/gemma3.md).

To chat with the model, we can use the `ollama` REST API, like so:

```python
from aiohttp import ClientSession, ClientTimeout

timeout = ClientTimeout(total=300)
session = ClientSession(timeout=timeout)

async def chat(session, messages, model, server="http://localhost:11434"):
    endpoint = f"{server}/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "num_ctx": 8192,
            "top_p": 0.95,
        }
    }

    async with session.post(endpoint, json=payload) as response:
        response.raise_for_status()

        response = await response.json()
        content = response["message"]["content"]
        messages.append({
          "role": "assistant", "content": content
        })

        return content
```

Create an list to hold our conversation history, and add the prompts from our instruction and discovery steps to the conversation, like so:

```python
messages = [
  { "role": "user", "content": "You are a helpful assistant to..." },
  { "role": "user", "content": "When I ask for the current weather..."}
]
```

Now that we have added all our prompts to the beginning of the conversation, we can start conversing with the model. Let us ask it for the current weather in Pune:

```python
task = "What is the weather in Pune right now?"
messages.append({ "role": "user", "content": task })

response = await chat(messages)
print(response)
```

!!! note "`output`"

        ```python
        fetch_weather(place="Pune")
        ```

Yay! With what we have done so far, the model:

- understood our instructions about function calling and discovery,
- figured out the place we wanted the weather for,
- decided the right course of action was to call a function,
- picked the correct function to call,
- and produced a function call with `place="Pune"`.

### Parsing the function calls

Once the model starts producing function calls in its responses, we need to start parsing them. Since the model has been instructed to produce function calls in markdown code blocks with the `python` language tag, we can use regular expressions to extract the python-style function call:

```python
import re

find_code_blocks = r"(?:\n+|\A)?(?P<code_all...>(?P<code_start>[ ]{0..."
code_block_regex = re.compile(find_code_blocks, re.VERBOSE | re.DOTALL)

function_calls = []
for match in code_block_regex.finditer(response):
    if match.group("code_class") == "python":
        function_calls.append(match.group("code_content"))
print(function_calls)
```

!!! note "`output`"

        ['fetch_weather(place="Pune")']

### Executing the called function

To execute the called function, we use `microsandbox` to spin up a secure sandbox, define the function, run the function call, and return the output. The sandbox provides safety when running unknown or model-generated code.

```python
from microsandbox import PythonSandbox

function_code = "import requests\ndef fetch_weather(place: str) -> ..."

sandbox = PythonSandbox(name="execution-sandbox")
sandbox._session = session

await sandbox.start()
await sandbox.run(function_code)
```

This snippet creates a sandbox and runs the code that defines the function. So our weather calling function is currently ready to be called in the sandbox. Next, we loop through the function calls and execute them one by one:

```python
responses = []
for call in function_calls:
    runner = await sandbox.run(call)

    output = await runner.output()
    errors = await runner.error()

    responses.append(errors if errors else output)

outputs = "\n\n".join(responses)
print(outputs)
```

!!! note "`output`"

        {'units': 'metric', 'condition': 'Patchy rain nearby', 'temperature': 23, 'feels_like': 25, 'wind_speed': 19}

Nice! The `fetch_weather` function executed successfully and returned the weather conditions, temperature and wind speed for Pune. Now, we can send this information back for the model to use:

```python
messages.append({ "role": "user", "content": outputs })

response = await chat(session, messages, model)
print(response)
```

!!! note "`output`"

        The weather in Pune is currently patchy rain nearby with a temperature of 23°C. It feels like 25°C and the wind speed is 19 km/h.

Yay! The model receives the output of the function and uses it to generate a user-friendly response for our question.

Congratulations! You have completed your first conversation with an offline, function calling enabled model.

## How to try it yourself

The code for this example is available as a [python script](https://github.com/offline-function-calling/sdk/blob/main/examples/hello-world.py). To run this script, execute the following commands:

```bash
git clone https://github.com/offline-function-calling/sdk
cd sdk/
uv run examples/hello-world.py
```

## What's next

A lot of the things we did in this tutorial can be done better:

- The current function discovery prompt is hard-coded to direct the model on how and when to call the `fetch_weather` function. This is unscalable - imagine having to write similar instructions for hundreds of functions!
- When calling multiple functions, the model needs to be able to keep track of which function call returned what output. The current prompt cannot properly do this.
- With the current prompt, the model cannot perform complex tasks that require it to call functions in parallel (like asking for the weather in multiple cities), and/or chain function calls in a particular sequence (like comparing the weather between two cities and booking a flight to the city with the more pleasant weather).

We'll take a look at how to address these problems in the next tutorial.
