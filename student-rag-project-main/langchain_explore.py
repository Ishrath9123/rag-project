import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = "gemini-2.5-flash"
def basic_flow():
    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.2,
    )

    question = "What is RAG in one sentence?"
    answer = llm.invoke(question)

    print("Part 1")
    print("Question:", question)
    print("Answer:", answer.content)

def template_flow():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Answer clearly and briefly."),
        ("human", "{question}"),
    ])

    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.2,
    )

    chain = prompt | llm
    question = "What is Python used for?"
    result = chain.invoke({"question": question})

    print("\nPart 2")
    print("Question:", question)
    print("Answer:", result.content)
if __name__ == "__main__":
    basic_flow()
    template_flow()