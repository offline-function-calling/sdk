---
title: Models
summary: Setup and run function calling models offline
order: 2
---

## Ollama

[`ollama`](https://github.com/ollama/ollama) is one of the easiest ways to run open-source large language models offline on your machine. It provides a CLI and REST API to manage and run models.

### Setup

To get started, follow the official [installation instructions](https://ollama.com/download) to download it onto your machine.

Next, run the server by executing the following command in a terminal:

```bash
ollama serve
```

This starts a server that listens on port `11434` by default. The [REST API](https://github.com/ollama/ollama/blob/main/docs/api.md) can be accessed on this port.

Then, open another terminal and pull the model you wish to run. A list of models can be found in [the library](https://ollama.com/library). For example, the following command pulls the Gemma 3 (27B parameter) model.

```bash
ollama pull gemma3:27b
```

Ollama does not support function calling with Gemma 3 officially yet. The [tutorials](../learn/hello-world.md) take that into account and provide code snippets to manually parse the function calls. To use function calling via the Offline Function Calling CLI, or the Ollama API, you can pull the function calling enabled version of the models from [here](https://ollama.com/gamemaker1/gemma3) instead:

```bash
ollama pull gamemaker1/gemma3:27b-fc # or 12b-fc
```

The files used to create these function calling enabled models can be found [here](https://github.com/offline-function calling/cli/tree/main/models).

Note that it is recommended to use the 27b parameter model only if you have 20-24 GB of RAM or more.

### Usage

To run the model, use the `ollama run` command. For example, the following command runs the function calling enabled Gemma 3 (27B parameter) model:

```bash
ollama run gamemaker1/gemma3:27b-fc
```

The first response might take some time while the model is loaded into memory. The model is unloaded when idle or not in use.

See the [official documentation](https://github.com/ollama/ollama/tree/main/docs#readme) for more commands and info.
