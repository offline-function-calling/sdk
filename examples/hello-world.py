import re
import asyncio

from textwrap import dedent
from aiohttp import ClientSession, ClientTimeout
from microsandbox import PythonSandbox

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

async def main():
    model = "gemma3:27b"

    instruction = "You are a helpful assistant to me, the user. You have access to programmatic functions that you can call to better assist me. You are encouraged to call functions to help the user. You can only use the functions given to you. Do not make up your own functions.\n\nYou can call these functions by producing a python-style function call in plain text only, passing all the parameters as named arguments. For example, to call a function named `do_something`, with the parameter `wait_for_it` set to `true` you must produce the following output:\n\n```python\ndo_something(wait_for_it=True)\n```\n\nThe output of the function will be returned in the next message from the user. You must use the output of the function to generate a helpful natural language response for the user. Your response must satisfy the user's original question."
    discovery = "When I ask for the current weather for a particular place, you can call the `fetch_weather` function and pass the `place` parameter (a string) with the place I mention. The place can be the name of a city or famous landmark, or an airport code. The function will produce a JSON object containing information about the weather condition, temperature and winds for the given place."
    task = "What is the weather in Pune right now?"

    messages = [
        { "role": "user", "content": instruction },
        { "role": "user", "content": discovery },
        { "role": "user", "content": task }
    ]

    timeout = ClientTimeout(total=300)
    session = ClientSession(timeout=timeout)

    response = await chat(session, messages, model)
    print(response)

    find_code_blocks = r"(?:\n+|\A)?(?P<code_all>(?P<code_start>[ ]{0,3}`{3,})[ \t]*(?:(?:(?P<code_class>[\w\-\.]+)(?:[ \t]*\{(?P<code_def_a>[^\}]+)\})?)|(?:[ \t]*\{(?P<code_def_b>[^\}]+)\}))?\n+(?P<code_content>.*?)\n+(?<!`)(?P=code_start)(?!`))(?:\n|\Z)"
    code_block_regex = re.compile(find_code_blocks, re.VERBOSE | re.DOTALL)

    function_calls = []
    for match in code_block_regex.finditer(response):
        if match.group("code_class") == "python":
            function_calls.append(match.group("code_content"))
    print(function_calls)

    function_code = """import requests\ndef fetch_weather(place: str) -> dict:\n    url = f"https://wttr.in/{place}?format=j1"\n    response = requests.get(url)\n    response.raise_for_status()\n    data = response.json()\n    data = data['current_condition'][0]\n    return {\n        "units": "metric",\n        "condition": data['weatherDesc'][0]['value'],\n        "temperature": int(data['temp_C']),\n        "feels_like": int(data['FeelsLikeC']),\n        "wind_speed": int(data['windspeedKmph'])\n    }"""

    sandbox = PythonSandbox(name="function-calling")
    sandbox._session = session

    await sandbox.start()
    await sandbox.run(function_code)

    responses = []
    for call in function_calls:
        runner = await sandbox.run(call)

        output = await runner.output()
        errors = await runner.error()

        responses.append(errors if errors else output)

    outputs = "\n\n".join(responses)
    print(outputs)

    messages.append({ "role": "user", "content": outputs })
    response = await chat(session, messages, model)
    print(response)

    await sandbox.stop()
    await session.close()

asyncio.run(main())
