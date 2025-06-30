---
title: Dynamic Function Generation
summary: Why write functions... when models can do it for you :)
order: 3
---


!!! danger ""

    Note that this page is a work in progress. Not all things mentioned on this page are complete, and some links may be broken.

## What it is

In the [previous](./hello-world.md) [tutorials](./structuring-and-scaling.md), we learnt how to use function calling with offline models like Gemma 3. We:

- **instructed** the model on how to discover and call functions,
- let the model **discover** functions by writing function specifications,
- gave the model a task, and let it **call** the right function with the right parameters,
- **parsed** the function calls from the model's response, and
- **executed** the functions and returned the response to the model.

This process, however, takes a bit of effort. Instructing the model is a one time thing, and we wrote [a program](https://github.com/offline-function-calling/sdk/blob/main/examples/hello-world.py) to take care of the parsing and execution, but we still need to write the code and specifications for the functions in order for the model to use them. Writing this boilerplate for every new function can be tedious. While a shared library of pre-built functions might seem like a solution, individual workflows are often too specific to be covered by a generic toolkit. A more convenient approach is to have the model generate the exact function you need, precisely when you need it. That is what we will be doing in today's tutorial.

## How to do it

Similar to how we instructed the model to discover and call functions, we can instruct it to write function code and specifications as well. Let's try crafting a prompt for the same. First, let us tell it to expect two kinds of instructions - one to write code for a function, and the other to use the code it generated.

!!! note ""

    When you do not have a function that can do something I asked you to, I may ask you to:

    1. generate code to perform a specific action, or
    2. write a function specification for the code you wrote.

Next, let us give it a few guidelines to follow while writing the code for the function.

!!! note ""

    When generating code, please generate the code in Python only. Follow the below guidelines as well:

    - Do not generate examples that use the function.
    - Do not print the result, return it from the function.
    - Do not handle errors by printing or ignoring them, raise a custom exception with a user-friendly name and message instead.
    - Python is sensitive to indentation, so do not generate blank lines with only tabs or whitespaces.

Let's give it some guidelines on how to write a function specification as well.

!!! note ""

    When writing function specifications, make sure the specification is produced in a code block with the language set to `function_spec` instead of `json`. Make sure to follow the below JSON schema while writing the specification:

    <br /><br />

    {schema}

    <br /><br />
    Note that the produced specification must be a valid JSON object. Do NOT re-produce this schema as a function specification.

Now, let's use the [functions from the first tutorial](./hello-world.md#getting-the-model-to-call-functions) to talk to the model.

```python
task = "I want to be able to track my expenses. Could you write a simple expense tracker that lets me record and query my expenses?"
```

!!! note "`output`"

        :::md
        Okay, let's start with the function specifications for the expense tracker.

        ```function_spec
        {
          "name": "record_expense",
          "description": "Records a new expense with a description, amount, and category.",
          "parameters": {
            "type": "object",
            "properties": {
              "description": {
                "type": "string",
                "description": "A description of the expense."
              },
              "amount": {
                "type": "number",
                "description": "The amount of the expense."
              },
              "category": {
                "type": "string",
                "description": "The category of the expense (e.g., food, travel, entertainment)."
              }
            },
            "required": ["description", "amount", "category"]
          },
          "responses": [
            {
              "type": "object",
              "properties": {
                "message": {
                  "type": "string",
                  "description": "Confirmation message"
                }
              }
            }
          ],
          "errors": [
            {
              "name": "InvalidExpenseData",
              "description": "Raised when the expense data is invalid (e.g., amount is negative or zero)."
            },
            {
              "name": "DataStorageError",
              "description": "Raised when there is an error saving the expense data."
            }
          ]
        }
        ```

        ```function_spec
        {
          "name": "query_expenses",
          "description": "Queries expenses based on specified criteria (category and/or date range).",
          "parameters": {
            "type": "object",
            "properties": {
              "category": {
                "type": "string",
                "description": "The category to filter expenses by (optional)."
              },
              "start_date": {
                "type": "string",
                "format": "date",
                "description": "The start date for the date range (optional)."
              },
              "end_date": {
                "type": "string",
                "format": "date",
                "description": "The end date for the date range (optional)."
              }
            },
            "required": []
          },
          "responses": [
            {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "description": {
                    "type": "string"
                  },
                  "amount": {
                    "type": "number"
                  },
                  "category": {
                    "type": "string"
                  },
                  "date": {
                    "type": "string",
                    "format": "date"
                  }
                }
              }
            }
          ],
          "errors": [
            {
              "name": "DataNotFoundError",
              "description": "Raised when no expenses match the specified criteria."
            },
            {
              "name": "DataStorageError",
              "description": "Raised when there is an error reading the expense data."
            }
          ]
        }
        ```

        Now, let's write the Python code for these functions.

        ```python
        import os
        import pickle
        from datetime import datetime

        DATA_FOLDER = os.path.expanduser("~/data")
        EXPENSE_FILE = os.path.join(DATA_FOLDER, "expenses.pkl")

        class InvalidExpenseData(Exception):
            """Raised when the expense data is invalid."""
            pass

        class DataStorageError(Exception):
            """Raised when there is an error saving/loading data."""
            pass

        class DataNotFoundError(Exception):
            """Raised when no data is found for a given query."""
            pass

        def record_expense(description, amount, category):
            """Records a new expense with a description, amount, and category."""
            if amount <= 0:
                raise InvalidExpenseData("Amount must be positive.")

            expense = {
                "description": description,
                "amount": amount,
                "category": category,
                "date": datetime.now().date()
            }

            try:
                if not os.path.exists(DATA_FOLDER):
                    os.makedirs(DATA_FOLDER)

                expenses = []
                if os.path.exists(EXPENSE_FILE):
                    with open(EXPENSE_FILE, "rb") as f:
                        expenses = pickle.load(f)

                expenses.append(expense)

                with open(EXPENSE_FILE, "wb") as f:
                    pickle.dump(expenses, f)

            except Exception as e:
                raise DataStorageError(f"Error saving expense data: {e}")

            return {"message": "Expense recorded successfully."}

        def query_expenses(category=None, start_date=None, end_date=None):
            """Queries expenses based on specified criteria (category and/or date range)."""
            try:
                if not os.path.exists(EXPENSE_FILE):
                    return []

                with open(EXPENSE_FILE, "rb") as f:
                    expenses = pickle.load(f)

                filtered_expenses = expenses

                if category:
                    filtered_expenses = [e for e in filtered_expenses if e["category"] == category]

                if start_date:
                    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                    filtered_expenses = [e for e in filtered_expenses if e["date"] >= start_date]

                if end_date:
                    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                    filtered_expenses = [e for e in filtered_expenses if e["date"] <= end_date]

                if not filtered_expenses:
                    raise DataNotFoundError("No expenses found matching the criteria.")

                return filtered_expenses

            except Exception as e:
                raise DataStorageError(f"Error reading expense data: {e}")
        ```
    
