import sys
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

def main():
    if len(sys.argv) < 2:
        print("Usage: explain <your question>")
        return

    query = " ".join(sys.argv[1:])

    llm = ChatOllama(model="llama3.2", temperature=0)

    template = """You are a Linux command line expert.\n
    Provide only short text explanations, do not add markdown code blocks, or any extra text.\n
    Provide sort short explanation clear explanation for this comand:\n
    {question}
    """

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm

    response = chain.invoke({"question": query})
    print(response.content.replace("`", "").strip())

if __name__ == "__main__":
    main()

