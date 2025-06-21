# Offline Function Calling

Function calling is a powerful construct that allows large language models to use tools and interact with external APIs. It empowers LLMs to go beyond just generating text and actually do real world tasks for you, like checking the weather, re-organizing your files and folders, keeping track of your expenses, and much much more! Combined with the multimodal capabilities and offline nature of recent LLMs, function calling opens up a lot of amazing possibilities.

Most current function calling implementations require cloud-based LLMs or servers. Advances in offline models such as Gemma 3n have brought both multimodal and function calling capabilities to our devices, however, there is a lack of documentation and tooling that enables us to make use of it. This project aims to remedy that by becoming a comprehensive source of knowledge regarding function calling in offline large language models. To date, it consists of:

- [a library](https://github.com/offline-function-calling/sdk) that enables function calling with offline models,
- [tutorials and guides](learn/hello-world.md) that help you get started with function calling, and
- [benchmarks](bench/gemma3.md) that explore different models' function calling capabilities.

Most of the content in this repository is currently centered around Gemma 3. Contributions that explore function calling using other offline models are welcome :)
