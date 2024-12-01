from langchain.chat_models import ChatOpenAI
import json
import os
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


def ask_assistant(question):

    """
    Function to interact with the OpenAI API using LangChain.
    :param question: User question as a string.
    :return: AI's response as a string.
    """

    try:
        with open("formatted_projects.json", "r") as f:
            projects = json.load(f)
    except FileNotFoundError:
        return "Data not found. Please ensure 'formatted_projects.json' exists."

    chat = ChatOpenAI(model="gpt-4", temperature=0)

    messages = [
        SystemMessage(content="You are an AI assistant for crypto projects."),
        HumanMessage(content=f"{question}\n\nHere is the data: {json.dumps(projects)}")
    ]

    try:
        response = chat(messages)
        return response.content
    except Exception as e:
        return f"Error during AI response generation: {e}"
