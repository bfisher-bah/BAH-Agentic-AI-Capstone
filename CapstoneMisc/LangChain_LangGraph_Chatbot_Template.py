from typing_extensions import TypedDict
from typing import Annotated
from langchain.chat_models import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint import MemorySaver  # For in-memory conversation storage

# --- 1. Define State Structure ---
class MessagesState(TypedDict):
    messages: Annotated[list, add_messages]

# --- 2. Build the State Graph ---
workflow = StateGraph(state_schema=MessagesState)

# Replace with your preferred LLM API/model (e.g. OpenAI, Anthropic, OpenRouter)
llm = ChatOpenAI(model='gpt-3.5-turbo', api_key='your-api-key')

def call_llm(state: MessagesState):
    """Invoke LLM using the current state."""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

workflow.add_node("llm", call_llm)
workflow.add_edge(START, "llm")
workflow.add_edge("llm", END)

# --- 3. Integrate in-memory Memory ---
memory = MemorySaver()  # Keeps conversation context in memory

app = workflow.compile(checkpointer=memory)

# --- 4. Chat Loop (for CLI usage) ---
def run_chat():
    print("Type 'exit' to end the chat.")
    while True:
        user_msg = input("User: ")
        if user_msg.lower() in {"exit", "quit", "q"}:
            print("Goodbye!")
            break
        # Pass user input as a message in state
        for event in app.stream({"messages": [{"role": "user", "content": user_msg}]}):
            for val in event.values():
                print("Bot:", val["messages"][-1].content)
                
run_chat()
-