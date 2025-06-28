---
title: Multimodal Input
summary: And how you can use it with function calling
order: 3
---

## What it is

The multi-modal input capabilities of a model enable it to understand more than just text - you can use image, video, and audio files in the conversation as well.

The Gemma 3 (27B parameter) model we used in the [previous](./hello-world.md) [tutorials](./structuring-and-scaling.md) supports adding image files to the conversation. This tutorial will go through using this capability together with function calling, with the example of a simple expense tracker.

Here's a peak at the conversation you'll be having by the end of this tutorial:

!!! note "`you`"

    <br />
    <blockquote>
    [[image of bill](media/bill.jpg)]
    </blockquote>

    <br />
    Add this to my expenses, and let me know if I'm going over my food budget of 1000 this month.

!!! info "`model`"

    &nbsp;You've spent a total of 1278.5 on food this month, which exceeds your budget of 1000 by 278.5. It looks like that dinner at TSC put you over the limit!

## How to do it

### Reading and encoding images for models

Making use of a model's multimodal capabilities is easy to do using Ollama. Recall [the function we wrote](./hello-world.md#getting-the-model-to-call-functions) to make requests to the Ollama REST API in the first tutorial:

```python
model = "gemma3:27b"
```

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

Each message in the `messages` array passed to the above function looks like this:

```python
{
    "role": "user" or "assisstant",
    "content": "What is the answer to life, the universe and everything?"
}
```

Ollama supports passing multiple images as an array of base64-encoded strings along with the text content. So our new message object should look like this:

```python
{
    "role": "user",
    "content": "Tell me what is in this image.",
    "images": ["iVBORw0KGgoAAAANSUhEUgAAAe0AAAKACAY..."]
}
```

In this message, the string `"iVBORw0KGgoAAAANSUhEUgAAAe0AAAKACAY..."` is the bytes of an image encoded using base64.

Let us write the code to read an image (given a path on the disk), encode it using base64, and pass it to the API:

```python
from base64 import b64encode

def encode_image(path: str) -> str:
    try:
        with open(path, "rb") as file:
            return b64encode(file.read()).decode("utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find file: {path}")
    except Exception as error:
        raise Exception(f"Failed to encode image {path}: {str(error)}")
```

Now, we can add this to the existing `chat` function:

```{ .python hl_lines="7 8 9 10" }
from aiohttp import ClientSession, ClientTimeout

timeout = ClientTimeout(total=300)
session = ClientSession(timeout=timeout)

async def chat(session, messages, model, server="http://localhost:11434"):
    for message in messages:
        if "images" in message:
            encoded = [encode_image(path) for path in message["images"]]
            message["images"] = encoded

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

We can use this to provide the model with images on disk, like so:

```python
task = "Add this to my expenses, and let me know if I'm going over my food budget of 1000 this month."
messages.append({
    "role": "user",
    "content": task,
    "images": ["~/media/bill.jpg"]
})

response = await chat(session, messages, model)
print(response)
```

### Using the images with function calls
