---
title: Structuring and Scaling
summary: Scaling function calling by adding structure to our processes.
---

<style>
  html.dark .typography details summary::after { filter: invert(100%); }
</style>

## How we did it

In the [previous tutorial](./hello-world.md), we learned that function calling involves five key steps: _instruction_, _discovery_, _calling_, _parsing_, and _execution_. We covered in each step in detail while enabling a Gemma 3 model to call a `fetch_weather` function when we ask it for the current weather in a certain place. Here's a recap of how we did it:

- We wrote two prompts for the model: an instruction prompt that taught the model the general rules for how to call functions, and a discovery prompt that described our specific `fetch_weather` function, including its purpose and parameters.
- We wrote a code that used the [`ollama`](../setup/models.md) REST API to send our prompts and a task ("What's the weather in Pune?") to the model running offline on our machine.
- The model understood the instructions and produced a function call in response to our message.
- We wrote code to parse the function calls from the model's response, and used [`microsandbox`](../setup/tools.md#microsandbox) to execute the function code in a secure sandbox, and return the function's output to the model.
- The model acknowledged and understood the function's output, and returned a natural language response that answered our original question about the weather in Pune.

## What we can do better

Towards the end of the tutorial, we found several things to improve:

- The current function discovery prompt is hard-coded to direct the model on how and when to call the `fetch_weather` function. This is unscalable - imagine having to write similar instructions for hundreds of functions!
- When calling multiple functions, the model needs to be able to keep track of which function call returned what output. The current prompt cannot properly do this.
- With the current prompt, the model cannot perform complex tasks that require it to call functions in parallel (like asking for the weather in multiple cities), and/or chain function calls in a particular sequence (like comparing the weather between two cities and booking a flight to the city with the more pleasant weather).

We'll take a look at how to address these problems in detail over the course of this tutorial.

## How we can do it better

Most of the above problems can be addressed by modifying the instructions (prompts) provided to the model. This section thus focuses on modifying and re-writing portions of the function calling prompt to improve the function discovery and calling capabilities of the model.

### Using function specifications for discovery

In the previous tutorial, [we gave the model the following instructions](../learn/hello-world.md#letting-the-model-discover-functions) so that it can discover and use the `fetch_weather` function:

!!! note ""

    When I ask for the current weather for a particular place, you can call the `fetch_weather` function and pass the `place` parameter (a string) with the place I mention. The place can be the name of a city or famous landmark, or an airport code. The function will produce a JSON object containing information about the weather condition, temperature and winds for the given place.

Breaking the prompt down, we see that it provides the model with several important pieces of information:

> When I ask for the current weather for a particular place, ...

This gives the model examples of tasks that can be accomplished by calling this function.

> ... you can call the `fetch_weather` function and ...

This gives the model the name of the function.

> ... pass the `place` parameter (a string) with the place I mention. The place can be the name of a city or famous landmark, or an airport code ...

This provides the model with detailed information about the parameters required by the function, and what kind of values the function expects.

> ... The function will produce a JSON object containing information about the weather condition, temperature and winds for the given place.

This tells the model what kind of output it can expect when it calls the function. Notice that this is missing the possible errors that the function can return.

When you want to support tens and even hundreds of functions, it is necessary to find a structured way to provide this information. Structuring this information enables easier maintainability, reduces ambiguity introduced by poor wording, and allows for programmatic generation of function information. Luckily for us, a great way to structure this kind of information already exists - [JSON schemas](https://json-schema.org/docs)!

We use an OpenAPI-inspired JSON schema to provide information on the name of a function, what the function does, what parameters it accepts, the possible outputs it produces, the possible errors it throws, and examples of when to use it. We call these 'function specifications'. For our `fetch_weather` function, the specification would look something like this:

```json
{
  "name": "fetch_weather",
  "description": "Fetches the current weather for a given location using the wttr.in API.",
  "parameters": {
    "type": "object",
    "properties": {
      "place": {
        "type": "string",
        "description": "The location for which to fetch the weather. May be the name of a city, town, country or famous landmark, or an airport code."
      }
    },
    "required": ["place"]
  },
  "responses": [{
    "type": "object",
    "properties": {
      "units": {
        "type": "string",
        "enum": ["metric", "imperial"],
        "description": "The system of units used for measurements (e.g., metric, imperial)."
      },
      "condition": {
        "type": "string",
        "description": "A human-readable text description of the current weather condition."
      },
      "temperature": {
        "type": "number",
        "description": "The current temperature. The unit is specified in the 'units' field (e.g., Celsius for metric)."
      },
      "feels_like": {
        "type": "number",
        "description": "The perceived 'feels like' temperature, accounting for factors like wind and humidity.",
      },
      "wind_speed": {
        "type": "number",
        "minimum": 0,
        "description": "The current wind speed. The unit depends on the 'units' field (e.g., km/h for metric, mph for imperial)."
      }
    }
  }],
  "errors": [{
    "name": "RequestException",
    "description": "Raised if the API request fails or returns an error (e.g., invalid location, network issues)."
  }]
}
```

!!! note ""

    The JSON schema document used to validate function specifications can be found [here](https://github.com/offline-function-calling/schemas/function.schema.json).

Now that we have a structured and scalable way to define functions, we can instruct the model to 'discover' and use any functions that are described by a function specification:

!!! note ""

    You are a helpful assistant to me, the user. You have access to programmatic functions that you can invoke to better assist me. These functions are described via function specifications - essentially, your manual to using them. Each specification contains the name of the function, a detailed description on what it does, the parameters it accepts, the possible responses and errors it produces, and examples of when to use the given function. A function specification is a JSON object, provided by me in a special code block labelled `function_spec`, like so:

        :::md
        ```function_spec
        {
            "name": the name of the function,
            "description": a detailed description of what the function does,
            "parameters": a dictionary of arguments to pass to the function,
            "responses": a list of possible outputs the function can produce,
            "errors": a list of possible errors the function can raise,
            "examples": a list of examples of when to call the function
        }
        ```

With this, we no longer require the function discovery prompt we wrote for the `fetch_weather` function in the previous tutorial. All we need to do is provide the specification for the function in a `function_spec` code block before asking it for the weather! This addresses our first problem.

### Structuring function calls and outputs

In our [initial function calling prompt](./hello-world.md#instructing-the-model), we had instructed the model to produce python-style function calls in markdown code blocks. While this works for simple, single-call scenarios, it can become ambiguous when the model needs to call multiple functions at once. The current method of parsing function calls also means that our code will find and execute all python code in the model's responses, even code that is _not_ a function call.

Consider the following scenario:

!!! note "`you`"

    &nbsp;What's the weather in Pune and Hyderabad right now?

!!! info "`model`"

        :::md
        ```python
        get_weather(location="Pune")
        ```

        ```python
        get_weather(location="Hyderabad")
        ```

!!! warning "`function output`"

        :::json
        {
          "conditions": "Cloudy",
          "temperature": 30,
          "feels_like": 31,
          "wind_speed": 9,
          "units": "metric"
        }

        {
          "conditions": "Patchy rain",
          "temperature": 26,
          "feels_like": 28,
          "wind_speed": 23,
          "units": "metric"
        }

Since we asked the model for the weather at two locations, it produced two function calls in the same message. However, when we write the code to execute these two functions, we might run them in parallel to save time. This means we can't guarantee which one will finish first, and we cannot assume they came back in the same order you called them. In such a case, how do we tell the model which output is for Pune and which is for Hyderabad? One idea is to instruct the model to assign each function call an identifier. This identifier would be returned along with the output of the function call, which lets the model know which call produced what output.

We could instruct the model to produce these new function calls and outputs in JSON wrapped in labelled markdown code blocks. This means our above conversation would instead look like this:

!!! note "`you`"

    &nbsp;What's the weather in Pune and Hyderabad right now?

!!! info "`model`"

        :::md
        ```function_call
        {
          "id": "fetch_weather_pune",
          "function": "fetch_weather"
          "parameters": {
            "place": "Pune"
          }
        }
        ```

        ```function_call
        {
          "id": "fetch_weather_hydb",
          "function": "fetch_weather"
          "parameters": {
            "place": "Hyderabad"
          }
        }
        ```

!!! warning "`function output`"

        :::md
        ```function_output
        {
          "id": "fetch_weather_hydb",
          "result": {
            conditions": "Cloudy",
            "temperature": 30,
            "feels_like": 31,
            "wind_speed": 9,
            "units": "metric"
          }
        }
        ```

        ```function_output
        {
          "id": "fetch_weather_pune",
          "result": {
            "conditions": "Patchy rain",
            "temperature": 26,
            "feels_like": 28,
            "wind_speed": 23,
            "units": "metric"
          }
        }
        ```

With this, the model will now be able to keep track of which function calls have been completed and what output they produce, even if the output is returned a few messages later or out of order. In addition, the `function_call` label on the code blocks makes it easier for us to programmatically extract function calls from the model's responses.

Now that we have decided upon the structured function call and output formats, let us modify the function calling prompt:

!!! note ""

    You can call these functions by including special code blocks labelled function_call in your responses, like so:

        :::md
        ```function_call
        {
        	"id": a string used to pair the function call with its output,
        	"function": the name of the function to call,
        	"parameters": a dictionary of parameter names and values to pass to the function
        }
        ```

    I will execute the function and the result of the function call will be returned in a special code block labelled function_output in their response, like so:

        :::md
        ```function_output
        {
        	"id": the same string provided when calling the function,
        	"result": the output of the function - present only when the function execution succeeds,
        	"error": the error thrown by the function - present only when the function raises an exception or throws an error
        }
        ```

This means we would also need to change the code that deals with parsing function calls and collating function outputs. This is left as an exercise to the reader :)

### Handling ambiguity to prevent guesswork

As the number of functions and parameters grows, the chances of the model making incorrect assumptions or hallucinating answers when it lacks information increase. To remedy this, we can include instructions that ask the model to figure out what information it has, decide what function to call, and then ask for clarification if it does not have sufficient information to proceed.

!!! note ""

    Before responding, briefly consider:

    - what information do you need to fulfill the request?
    - what functions, if any, can help?
    - what are the potential dependencies between functions?

    If you need information that I haven't provided in the conversation uptil now, ask me for it. You must never, ever, guess or make assumptions.

### Exposing the model's thought process

To better understand the reasons behind what the model does, we can ask it to output its thought process at the beginning of its response in a markdown code block labelled `thinking`:

!!! note ""

    Please preface all your responses with a special code block labelled `thinking` that includes your thoughts, observations, and justification for the actions you are taking. Include the considerations you made about the information required, the relevant functions, and any dependencies between functions.

### Enabling parallel function calls

When a model needs to make more than one function call, it can make the calls in sequence (one after the other) or in parallel (all at the same time). Let us take an example to understand when we can call functions in parallel, and when we have to call them in sequence.

Say we have a database of users which stores their favourite fruit, and a function called `run_sql_query` that allows the model to run arbitrary SQL queries on the database. Then, let us assign the model a task that:

/// details | **Forces the model to call functions in a certain sequence**

!!! note "`you`"

    &nbsp;Delete all users who like apples, and tell me the updated number of users in the database.

To accomplish this task, the model needs to make two queries, in the following order: the first to delete the users who like apples, and the second to count the number of users in the database _after the deletion_. Let us go through the checklist and see if these queries are independent:

- no, since the deletion query might acquire a read-write lock on the database, affecting the execution of the count query.
- yes, there is no data dependency between the queries - the result of one is not needed for the other to run.
- no, the count query reads the data that the deletion query will have deleted.

Since these queries fail two of the checks, they are not independent. Thus, the model should call them in sequence, like so:

!!! info "`model`"

        :::md
        ```function_call
        {
          "id": "delete_users_apples",
          "function": "run_sql_query"
          "parameters": {
            "query": "delete from users where fruit = 'apple';"
          }
        }
        ```

!!! warning "`function_output`"

        :::md
        ```function_output
        {
          "id": "delete_users_apples",
          "result": "DELETE 37"
        }
        ```

!!! info "`model`"

        :::md
        ```function_call
        {
          "id": "count_all_users",
          "function": "run_sql_query"
          "parameters": {
            "query": "select count(*) from users;"
          }
        }
        ```

!!! warning "`function_output`"

        :::md
        ```function_output
        {
          "id": "count_all_users",
          "result": 55
        }
        ```

!!! info "`model`"

    &nbsp;After deleting the users whose favorite food is apples, the number of users left is 55.

///

/// details | **Allows the model to call functions in parallel**

!!! note "`you`"

    &nbsp;Count the number of users who like apples and the number of users who like oranges.

To accomplish this task, the model needs to make two queries: the first to count the number of users who like apples, and the second to count the number of users who like oranges. These two queries:

- yes, since queries do not affect each others' execution.
- yes, the result of one is not needed for the other to run.
- yes, the queries do not read data that will be created, updated or deleted by the other query.

Since all three checks have passed, the queries are independent, and can be executed in parallel, like so:

!!! info "`model`"

        :::md
        ```function_call
        {
          "id": "count_apple_lovers",
          "function": "run_sql_query"
          "parameters": {
            "query": "select count(*) from users where fruit = 'apples';"
          }
        }
        ```

        ```function_call
        {
          "id": "count_orange_lovers",
          "function": "run_sql_query"
          "parameters": {
            "query": "select count(*) from users where fruit = 'oranges';"
          }
        }
        ```

!!! warning "`function_output`"

        :::md
        ```function_output
        {
          "id": "count_orange_lovers",
          "result": 13
        }
        ```

!!! warning "`function_output`"

        :::md
        ```function_output
        {
          "id": "count_apple_lovers",
          "result": 37
        }
        ```

!!! info "`model`"

      &nbsp;The number of users that like apples is 37, and oranges is 13.

///

Thus, adding the following to the function calling prompt should enable the model to perform calls in parallel when appropriate:

!!! note ""

    You are encouraged to combine subtasks and call functions in parallel by including multiple `function_call` code blocks in a single response IF AND ONLY IF:

    - the functions do not affect each other's execution,
    - the result of one or more function call(s) is not needed for the others to run, and
    - a function does not need to read the data that another function has just created, updated, or deleted.

    Please note that the order in which functions execute is NOT guaranteed. If all the above conditions are not satisfied, do not call the dependent functions in parallel. It is generally safe to call the same function with different parameters in parallel when you need to fetch, update, create or delete multiple of the same kind of resources.

### Putting it all together

Finally, combining all the additions and modifications we made to the function calling instructions over the course of this tutorial, we get our improved prompt. Click on the clipboard icon to copy the entire prompt as a string.

    :::python  
    "You are a helpful assistant to me, the user.\n\nYou have access to programmatic functions that you can invoke to better assist me. These functions are described via function specifications - essentially, your manual to using them. Each specification contains the name of the function, a detailed description on what it does, the parameters it accepts, the possible responses and errors it produces, and examples of when to use the given function. A function specification is a JSON object, provided by me in a special code block labelled `function_spec`, like so:\n\n```function_spec\n{\n    \"name\": the name of the function,\n    \"description\": a detailed description of what the function does,\n    \"parameters\": a dictionary of arguments to pass to the function,\n    \"responses\": a list of possible outputs the function can produce,\n    \"errors\": a list of possible errors the function can raise,\n    \"examples\": a list of examples of when calling the function is required\n}\n```\n\nYou can call these functions by including special code blocks labelled `function_call` in your responses, like so:\n\n```function_call\n{\n\t\"id\": a string used to pair the function call with its output,\n\t\"function\": the name of the function to call,\n\t\"parameters\": a dictionary of parameter names and values to pass to the function\n}\n```\n\nI will execute the function and the result of the function call will be returned in a special code block labelled `function_output` in their response, like so:\n\n```function_output\n{\n\t\"id\": the same string provided when calling the function,\n\t\"result\": the output of the function - present only when the function execution succeeds,\n\t\"error\": the error thrown by the function - present only when the function raises an exception or throws an error\n}\n```\n\nPlease remember the following guidelines while responding.\n\nIf you need information that I haven't provided in the conversation uptil now, *ask me for it*. You must never, ever, guess or make assumptions. This is a critical safeguard that prevents hallucinations.\n\nBefore responding, briefly consider:\n\n- what information do you need to fulfill the request?\n- what functions, if any, can help?\n- what are the potential dependencies between functions?\n\nYou are encouraged to combine subtasks and call functions in parallel by including multiple `function_call` blocks in a single response IF AND ONLY IF:\n\n- the functions do not affect each other's execution,\n- the result of one or more function call(s) is not needed for the others to run, and\n- a function does not need to read the data that another function has just created, updated, or deleted.\n\nPlease note that the order in which functions execute is NOT guaranteed. If all the above conditions are not satisfied, do not call the dependent functions in parallel. It is generally safe to call the same function with different parameters in parallel when you need to fetch, update, create or delete multiple of the same kind of resources.\n\nEnsure your final response fully addresses my request, and is helpful to me.\n\nPlease preface all your responses with a special code block labelled `thinking` that include your thoughts, observations and justification for actions that you are taking. Include the guidelines you have followed and not followed while producing your response as well.\n"

Providing this prompt to a model enables function calling, and providing function specifications enables it to discover which functions it can call. After that, we can start giving it tasks.

## Using the SDK


