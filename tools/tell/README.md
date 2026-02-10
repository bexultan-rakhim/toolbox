# tell

AI-powered CLI tool that generates concise summaries from local cli tools using LangChain and Ollama.

## Requirements
This tools uses ollama to run llm model locally. It uses llama3.2, which does not use much resources.
* **Ollama**: Install and pull the model (linux):

`curl -fsSL https://ollama.com/install.sh | sh`

`ollama pull llama3.2`
* **uv**: Fast Python package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Initialization
1. Sync UV Project 
```bash
uv sync
```
2. You can add the line to your `.bashrc` or create alias by this
```bash
alias tell="/path/to/this/folder/tell.sh"
```

## Usage
Generate a usage summary for any tool with a local man page:
```bash
tell use tar
```

Force regeneration (bypass cache):
```bash
tell use tar --regenerate
```

You forgot the very specific one liner? For example, you forgot something like this: `find . -name "*.log" -size +100M | xargs rm`
How on earth are you going to remember this? I got you. You can run this:
```bash
tell gen "find all .log files larger than 100MB and delete them instantly?"
``` 
You have some cryptic command line one liner that you have hard time to understand? You can do this to get explanation:j
```bash
tell expl "sudo rm -rf /"
```

## Features
* **Local Execution:** Runs entirely on your machine via Ollama.
* **Caching:** Stores summaries in `~/.cache/tell/` for instant retrieval.
* **Context-Aware:** Uses the actual system man page as the source of truth.
* **Find one liners:** You can instantly generate a oneliner for your linux terminal using `tell gen`
* **Explain one liners:** You can instantly get explanation for one liner `tell expl`

