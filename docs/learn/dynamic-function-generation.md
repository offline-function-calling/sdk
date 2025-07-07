---
title: Dynamic Function Generation
summary: Why write functions... when models can do it for you :)
order: 3
---

## What it is

In the [previous](./hello-world.md) [tutorials](./structuring-and-scaling.md), we learnt how to use function calling with offline models like Gemma 3. We:

- **instructed** the model on how to discover and call functions,
- let the model **discover** functions by writing function specifications,
- gave the model a task, and let it **call** the right function with the right parameters,
- **parsed** the function calls from the model's response, and
- **executed** the functions and returned the response to the model.

This process, however, takes a bit of effort. Instructing the model is a one time thing, and we wrote [a program](https://github.com/offline-function-calling/sdk/blob/main/examples/hello-world.py) to take care of the parsing and execution, but we still need to write the code and specifications for the functions in order for the model to use them. Writing this boilerplate for every new function can be tedious. While a shared library of pre-built functions might seem like a solution, individual workflows are often too specific to be covered by a generic toolkit. A more convenient approach is to have the model generate the exact function you need, precisely when you need it. That is what we will be doing in today's tutorial.

## How to do it

Similar to how we instructed the model to discover and call functions, we can instruct it to write function code and specifications as well. We can then parse the function code from its response, and run it in the sandbox when the function is called.

### Instructing the model to write functions

Let's try crafting a prompt for function writing. First, let us tell it to expect two kinds of instructions - one to write code for a function, and the other to use the code it generated.

!!! note ""

    When you do not have a function that can do something I asked you to, I may ask you to:

    1. generate code to perform a specific action, or
    2. write a function specification for the code you wrote.

Next, let us give it a few guidelines to follow while writing the code for the function.

!!! note ""

    When generating code, please generate the code in Python only. Follow the below guidelines as well:

    - Generate functions that can be called, instead of classes or scripts.
    - Use pickle files to store data in the `~/data/` folder.
    - Do not use global variables.
    - Do not generate examples that use the function.
    - Do not print the result, return it from the function.
    - Do not handle errors by printing or ignoring them, raise a custom exception with a user-friendly name and message instead.
    - Blank lines with only tabs or whitespaces cause errors. Leave blank lines completely blank.

Let's give it some guidelines on how to write a function specification as well.

!!! note ""

    When writing function specifications, make sure the specification is produced in a code block with the language set to `function_spec` instead of `json`. Make sure to follow the below JSON schema while writing the specification:

    <br /><br />

    {schema}

    <br /><br />
    Note that the produced specification must be a valid JSON object. Do NOT re-produce this schema as a function specification.

Where `{schema}` must be replaced by [the JSON schema for function specifications](https://github.com/offline-function-calling/sdk/schemas/function.schema.json).

Putting it all together, we get our function calling prompt. Click on the clipboard icon to copy the entire prompt as a string.

    :::python
    "When writing functions for the user to access/interact with external systems on my behalf, I may ask you to:\n\n1. generate code to perform a specific action, or\n2. write a function specification for the code you wrote.\n\nWhen generating code, please generate the code in Python only. Follow the below guidelines as well:\n\n- Generate functions that can be called, instead of classes or scripts.\n- Use pickle files to store data in the `~/data/` folder.\n- Do not use global variables.\n- Do not generate examples that use the function.\n- Do not print the result, return it from the function.\n- Do not handle errors by printing or ignoring them, raise a custom exception with a user-friendly name and message instead.\n- Blank lines with only tabs or whitespaces cause errors. Leave blank lines completely blank.\n\nWhen writing function specifications, make sure the specification is produced in a code block with the language set to `function_spec` instead of `json`. Make sure to follow the below JSON schema while writing the specification:\n\n{schema}\n\nNote that the produced specification must be a valid JSON object. Do NOT re-produce this schema as a function specification."

### Asking the model to write a function

Let's use the Gemma 3 (27B parameter) that we used in the previous tutorials.

```python
model = "gemma3:27b"
```

Let us also create a list to hold our conversation history, and add the prompt from the instruction section above to it:

```python
messages = [{
  "role": "user", "content": "When writing functions for the user..."
}]
```

Next, making use of the [functions from the first tutorial](./hello-world.md#getting-the-model-to-call-functions) to talk to the model.

```python
task = """
    I want to be able to track my expenses. Could you write a simple expense
    tracker that lets me (1) record any expense I make, and (2) query all the
    expenses I've made so far?
"""

messages.append({ "role": "user", "content": task })
response = await chat(session, messages, model)

print(response)
```

!!! note "`output`"

        :::md
        ```python
        import pickle
        import os
        from datetime import datetime

        class InvalidDateError(Exception):
            """Raised when an invalid date format is provided."""
            pass

        def record_expense(category, amount, date, description=""):
            """Records an expense.

            Args:
                category (str): The category of the expense (e.g., "Food", "Travel").
                amount (float): The amount of the expense.
                date (str): The date of the expense in YYYY-MM-DD format.
                description (str, optional): A description of the expense. Defaults to "".

            Returns:
                bool: True if the expense was recorded successfully, False otherwise.

            Raises:
                InvalidDateError: If the date is not in the correct format.
            """
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise InvalidDateError("Invalid date format. Please use YYYY-MM-DD.")

            data_dir = os.path.expanduser("~/data")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)

            filepath = os.path.join(data_dir, "expenses.pkl")
            expenses = []

            try:
                with open(filepath, "rb") as f:
                    expenses = pickle.load(f)
            except FileNotFoundError:
                pass  # File doesn't exist, start with an empty list

            expense = {
                "category": category,
                "amount": amount,
                "date": date,
                "description": description,
            }
            expenses.append(expense)

            with open(filepath, "wb") as f:
                pickle.dump(expenses, f)

            return True

        def list_expenses(category=None, start_date=None, end_date=None):
            """Lists expenses, optionally filtered by category or date range.

            Args:
                category (str, optional): The category to filter by. Defaults to None.
                start_date (str, optional): The start date for the date range (YYYY-MM-DD). Defaults to None.
                end_date (str, optional): The end date for the date range (YYYY-MM-DD). Defaults to None.

            Returns:
                list: A list of expense dictionaries that match the filter criteria.
                      Returns an empty list if no expenses match the criteria or if the file doesn't exist.

            Raises:
                ValueError: If start_date or end_date are not in the correct format.
            """

            data_dir = os.path.expanduser("~/data")
            filepath = os.path.join(data_dir, "expenses.pkl")

            try:
                with open(filepath, "rb") as f:
                    expenses = pickle.load(f)
            except FileNotFoundError:
                return []  # Return empty list if file doesn't exist

            filtered_expenses = []
            for expense in expenses:
                if category and expense["category"] != category:
                    continue

                if start_date and expense["date"] < start_date:
                    continue

                if end_date and expense["date"] > end_date:
                    continue

                filtered_expenses.append(expense)

            return filtered_expenses
        ```

Great! It's generated two python functions that record and query the expenses, just like we asked it to. Let's parse the response and store the python code so we can execute it later.

```python
find_code_blocks = r"(?:\n+|\A)?(?P<code_all...>(?P<code_start>[ ]{0..."
code_block_regex = re.compile(find_code_blocks, re.VERBOSE | re.DOTALL)

function_code = []
for match in code_block_regex.finditer(response):
    if match.group("code_class") == "python":
        function_code.append(match.group("code_content"))
function_code = "\n".join(function_code)
```

Next, let's ask it to write the function specifications.

```python
task = "Generate a function specification for the code you just wrote."
messages.append({ "role": "user", "content": task })

response = await chat(session, messages, model)
print(response)
```

!!! note "`output`"

        :::md
        ```function_spec
        {
          "name": "record_expense",
          "description": "Records a single expense with details like category, amount, date, and an optional description. Expenses are stored persistently for later retrieval.",
          "parameters": {
            "type": "object",
            "properties": {
              "category": {
                "type": "string",
                "description": "The category of the expense (e.g., 'Food', 'Travel')."
              },
              "amount": {
                "type": "number",
                "description": "The amount of the expense."
              },
              "date": {
                "type": "string",
                "format": "date",
                "description": "The date of the expense in YYYY-MM-DD format."
              },
              "description": {
                "type": "string",
                "description": "An optional description of the expense."
              }
            },
            "required": ["category", "amount", "date"]
          },
          "responses": [
            {
              "type": "boolean",
              "description": "True if the expense was recorded successfully, False otherwise."
            }
          ],
          "errors": [
            {
              "name": "InvalidDateError",
              "description": "Raised if the provided date is not in the correct YYYY-MM-DD format."
            }
          ]
        }
        ```

        ```function_spec
        {
          "name": "list_expenses",
          "description": "Lists expenses, with optional filtering by category and/or date range.  Returns a list of expense details.",
          "parameters": {
            "type": "object",
            "properties": {
              "category": {
                "type": "string",
                "description": "The category to filter expenses by. If provided, only expenses in this category will be returned."
              },
              "start_date": {
                "type": "string",
                "format": "date",
                "description": "The start date for the date range (YYYY-MM-DD). Expenses on or after this date will be returned."
              },
              "end_date": {
                "type": "string",
                "format": "date",
                "description": "The end date for the date range (YYYY-MM-DD). Expenses on or before this date will be returned."
              }
            }
          },
          "responses": [
            {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "category": {
                    "type": "string"
                  },
                  "amount": {
                    "type": "number"
                  },
                  "date": {
                    "type": "string"
                  },
                  "description": {
                    "type": "string"
                  }
                }
              },
              "description": "A list of expense dictionaries that match the filter criteria.  Each dictionary contains the expense's category, amount, date, and description."
            }
          ],
          "errors": []
        }
        ```

Since the generated function specifications are now a part of the conversation history, and are labelled `function_spec`, the model will discover it automatically when we continue the conversation. We can now go ahead and try getting the model to call the functions.

### Getting the model to call the functions

Now, let us provide the model with the [function calling prompt (from the second tutorial)](./structuring-and-scaling.md#putting-it-all-together) and then request it to record an expense for us.

```python
prompt = "You are a helpful assistant to me, the user..."
messages.append({ "role": "user", "content": prompt })

task = """
    I just spent 300 rupees on a cab ride back home today (7th July, 2025).
    Log this as a travel expense, please.
"""

messages.append({ "role": "user", "content": task })
response = await chat(session, messages, model)

print(response)
```

!!! note "`output`"

        :::md
        ```function_call
        {
        	"id": "1",
        	"function": "record_expense",
        	"parameters": {
        		"category": "Travel",
        		"amount": 300.0,
        		"date": "2025-07-07",
        		"description": "cab ride home"
        	}
        }
        ```

Yay! With what we've done so far, the model:

- understood our instructions about function writing,
- wrote code and specifications for our expense tracker,
- automatically discovered the functions it generated,
- understood our instructions about function calling, as well as our task,
- decided to call a function to accomplish the task,
- correctly picked the `record_expense` expense function,
- extracted from our message the right parameters and passed them to the function.

### Parsing and executing the function call

Next, let's parse the function call using the same regex we used earlier to find our function code.

```python
import json

function_calls = []
for match in code_block_regex.finditer(response):
    if match.group("code_class") == "function_call":
        function_calls.append(json.loads(match.group("code_content")))
```

Now before executing these function calls, let's create a [`microsandbox`](../setup/tools.md#microsandbox) and execute the function code generated by the model.

```python
from microsandbox import PythonSandbox

sandbox = PythonSandbox(name="execution-sandbox")
sandbox._session = session

await sandbox.start()
await sandbox.run(function_code)
```

Now we can generate python code to call the functions, and execute it in the sandbox.

```python
function_calls = [{ **call, "parameters": ", ".join([
    f"{k}={repr(v)}" for k, v in call["parameters"].items()
])} for call in function_calls]
```

```python
from textwrap import dedent

response = ""
for call in function_calls:
    code = dedent(f"""
        try:
            print(json.dumps({{
                "id": {repr(call["id"])},
                "result": {call["function"]}({call["parameters"]})
            }}, indent=4))
        except Exception as error:
            print(json.dumps({{
                "id": {repr(call["id"])},
                "error": {{
                    "name": type(error).__name__,
                    "message": str(error)
                }}
            }}, indent=4))
    """)

    runner = await sandbox.run(f"{func}({args})")
    output = await runner.output()
    response += f"```function_output\n{output}\n```\n\n"

print(response)
```

!!! note "`output`"

        :::md
        ```function_output
        {
            "id": "1",
            "result": true
        }
        ```

Now, let us convey this output to the model.

```python
messages.append({ "role": "user", "content": response })
response = await chat(session, messages, model)

print(response)
```

!!! note "`output`"

        :::md
        Okay, the expense has been successfully recorded!


Nice! To check if the expense has actually been recorded, we can read the `~/data/expenses.pickle` file.

```python
import os

data_dir = os.path.expanduser("~/data")
filepath = os.path.join(data_dir, "expenses.pkl")

with open(filepath, "rb") as f:
    expenses = pickle.load(f)

print(expenses)
```

!!! note "`output`"

        :::python
        [{'date': '2025-07-07', 'category': 'Travel', 'amount': 300.0, 'description': 'cab ride home'}]

Yay! The function worked as intended, storing the expense in the file. Congratulations! You have completed your first conversation that uses a model-generated function to accomplish a task, and all of it completely offline :)

## What's next

In [the next tutorial](./multimodal-input.md), we'll explore how to use the multimodal capabilities of offline LLMs in conjunction with all that we have learnt about function calling so far.
