---
title: CLI
summary: Install and setup the Offline Function Calling CLI
order: 1
---

The Offline Function Calling CLI helps you interact with a function calling enabled offline LLM using Ollama. It uses the [`@offline-function-calling/sdk`](https://github.com/offline-function-calling/sdk) library.

## Installation

The CLI is still under active development. During this phase, installation has to be done manually by cloning the git repository, installing the dependencies, and running the `main.py` script. Before running the below commands, please follow the instructions [here](./tools.md#python) to install `python` and `uv`.

```bash
git clone https://github.com/offline-function-calling/cli ; cd cli
uv run main.py --model gemma3:12b-fc --tools ./tools
```

The CLI works with the models that support tool calls via the Ollama API, such as the `gemma3:12b-fc` and `gemma3:27b-fc` models. Please refer to the instructions given [here](./models.md) to download and setup these models.

## Usage

To run the CLI, just `cd` into the directory where it was installed and run the following:

```bash
uv run main.py \
  --model gemma3:12b-fc \               # the model to use, must support tool calls using ollama
  --tools ./tools \                     # the path to the directory containing .py files with tool code
  --ollama http://localhost:11434       # the url at which the ollama server is running
```

You type multiline messages to send to the model, and submit it by pressing <kbd>Enter</kbd> and then <kbd>Ctrl</kbd>+<kbd>D</kbd>. Typing `/exit` or pressing <kbd>Ctrl</kbd>+<kbd>C</kbd> twice exits the chat, and typing `/help` prints a small message on how to use the CLI.

You can add more tools by just creating files in the custom tools directory that you mention. Each file must have one or more Python functions with docstrings that contain a description of what the tool does, as well as what the parameters are. The CLI comes with some builtin tools, which can be listed using the `/tools` command. If you add/remove tools mid-conversation, you can run the `/tools reload` command to update the list of available tools.

You can attach files from your computer by specifying the relative/absolute path to the files, or by specifying a `file://` URI. If it is a image/audio file, the CLI will pass it on to the model. If it is a document, the CLI will extract the text contents and append them to the end of the your message.
