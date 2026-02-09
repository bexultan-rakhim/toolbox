import sys
from pathlib import Path
import argparse
import subprocess
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# unly use first 1000 characters in man page
MAN_PAGE_CONTEXT_LENGTH = 1000
# limit output to be short
PREDICTION_LENGTH = 250
CACHE_DIR = Path.home() / ".cache" / "tldrgen"


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[32m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def get_man_page(tool_name: str) -> str | None:
    """Fetches the man page content using the 'man' command."""
    try:
        process = subprocess.Popen(
            ['man', tool_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, _ = process.communicate()

        if process.returncode != 0:
            return None

        clean_man = subprocess.check_output(
            ['col', '-b'],
            input=stdout,
            text=True
        )
        return clean_man
    except FileNotFoundError:
        return None


def save_cache(tool_name: str, tldr_text: str) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = CACHE_DIR / f"{tool_name}.tldr"
        cache_file.write_text(tldr_text, encoding="utf-8")
    except (PermissionError, IOError) as e:
        print(f"{Colors.YELLOW}Warning:"
              f"Could not write to cache: {e}{Colors.END}")


def load_tldr_form_cache(tool_name: str) -> str | None:
    cache_file = CACHE_DIR / f"{tool_name}.tldr"
    if not cache_file.is_file():
        return None
    try:
        return cache_file.read_text(encoding="utf-8")
    except (PermissionError, IOError, UnicodeDecodeError):
        return None


def generate_tldr(tool_name: str, man_page: str) -> str:
    llm = ChatOllama(
        model="llama3.2",
        temperature=0,
        num_predict=PREDICTION_LENGTH
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a minimalist technical writer. Create a TL;DR for a command-line tool.\n"
            "STRICT RULES:\n"
            "1. Provide a maximum of 5 most common examples.\n"
            "2. Each example description must be a single line.\n"
            "3. Do not explain the history or technical architecture.\n"
            "4. Format: Short Description -> Link -> Examples.\n"
            "5. Output only the TL;DR content, no introductory chatter like 'Here is the summary'."
        )),
        ("human", "Tool: {tool}\nContext: {context}")
    ])

    chain = prompt | llm | StrOutputParser()

    return chain.invoke(
        {"tool": tool_name, "context": man_page[:MAN_PAGE_CONTEXT_LENGTH]})


def main():
    parser = argparse.ArgumentParser(
        description="Generate a TL;DR for any installed man page.")
    parser.add_argument(
        "tool",
        help="The name of the command-line tool (e.g., tar, ls, grep)")
    parser.add_argument(
        "-r", "--regenerate",
        action="store_true",
        help="Force LLM to regenerate even if cache exists")
    args = parser.parse_args()
    tool = args.tool

    from_cache = load_tldr_form_cache(tool)
    if from_cache and not args.regenerate:
        print(f"{Colors.GREEN}{from_cache}\n{Colors.END}")
        return

    man_page = get_man_page(tool)

    if not man_page:
        print(f"{Colors.RED}{Colors.BOLD}Error{Colors.END}: {Colors.RED}"
              f"No man page found for '{tool}'. Maybe a typo?{Colors.END}")
        sys.exit(1)

    print(f"Generating TL;DR for {tool}...\n")
    try:
        result = generate_tldr(tool, man_page)
    except Exception as e:
        print(f"{Colors.RED}An error occurred:{Colors.END} {e}")
        sys.exit(1)

    print(f"{Colors.GREEN}{result}\n{Colors.END}")
    save_cache(tool, result)


if __name__ == "__main__":
    main()
