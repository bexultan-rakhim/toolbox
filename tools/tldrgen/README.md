# tldrgen

AI-powered CLI tool that generates concise summaries from local man pages using LangChain and Ollama.

## Requirements
This tools ollama to run llm model locally. It uses llama3.2, which does not use much resources.
* **Ollama**: Install and pull the model: `ollama pull llama3.2`
* **uv**: Fast Python package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Initialization
1. Sync UV Project 
```bash
uv sync
```
2. You can add the line to your `.bashrc` or create alias by this
```bash
alias tldr="/path/to/this/folder/tldrgen.sh"
```

## Usage
Generate a TL;DR for any tool with a local man page:
```bash
tldrgen tar
```

Force regeneration (bypass cache):
```bash
tldrgen tar --regenerate
```

## Features
* **Local Execution:** Runs entirely on your machine via Ollama.
* **Caching:** Stores summaries in `~/.cache/tldrgen/` for instant retrieval.
* **Context-Aware:** Uses the actual system man page as the source of truth.
