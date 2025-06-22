import asyncio
import offline_function_calling as sdk

from sdk import Model, Ollama

async def main():
    # the model comes with a few pre-defined functions that allow it to generate and run arbitrary
    # python code in a microsandbox, and prompts that enable its function calling and function code
    # and spec writing capabilities.
    async with Model(
        "gemma3:27b", provider=Ollama(),
        prompts="./prompts/" # additional md files to insert at the beginning of the convo
        functions="./functions/" # each subfolder contains a code.py and spec.json to register
    ) as model:

        # let the user talk to the model forever :)
        while True:
            task = input("Enter your message here: ")

            stream = await model.send_message(task, stream=True)

            # todo: make this more elegant - or is it already pythonic?
            response = ""
            for part in stream:
                print(part)
                response += part

            # keep executing all the functions until there are none left 
            message = model.parse_response(response)
            while message.function_calls.length > 0:
                outputs = await model.execute_calls(message.function_calls)
                response = await model.send_message(outputs, stream=False)
                message = model.parse_response(response)
                print(message.contents)

            # the model's final response
            print(message.contents)

asyncio.run(main())
