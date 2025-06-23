---
title: Models
summary: Setup and run models offline on your machine
---

<style> .codehilite { margin-top: 16px; margin-bottom: 16px; } </style>

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

### Usage

To run the model, use the `ollama run` command. For example, the following command runs the Gemma 3 (27B parameter) model:

```bash
ollama run gemma3:27b
```

The first response might take some time while the model is loaded into memory. The model is unloaded when idle or not in use.

See the [official documentation](https://github.com/ollama/ollama/tree/main/docs#readme) for more commands and info.
