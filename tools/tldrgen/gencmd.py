import sys
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

def main():
    if len(sys.argv) < 2:
        print("Usage: gencmd <your question>")
        return

    query = " ".join(sys.argv[1:])

    llm = ChatOllama(model="llama3.2", temperature=0)

    template = """You are a Linux command line expert. 
    Provide only the raw command that solves the user's request. 
    Do not include explanations, markdown code blocks, or any extra text.

    Request: {question}
    Command:"""

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm

    response = chain.invoke({"question": query})
    print(response.content.replace("`", "").strip())

if __name__ == "__main__":
    main()
