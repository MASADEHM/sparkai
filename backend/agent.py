from langchain_openai.chat_models import AzureChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from backend.prompts import sysprompts
from backend.tools import TavilySearch, sendemail, searchuser, send_otp, verify_otp, searchdocs

llm=AzureChatOpenAI(model="gpt-4o-mini")

tools=[TavilySearch,sendemail,searchuser,send_otp,verify_otp,searchdocs]
llmwithtools=llm.bind_tools(tools)


async def assistant(state: MessagesState):
    response = await llmwithtools.ainvoke([("system", sysprompts)] + state['messages'])
    return {"messages": response}


# Compiled with a checkpointer in app.py (it needs an open DB connection).
builder=StateGraph(MessagesState)
builder.add_node("assistant",assistant)
builder.add_node("tools",ToolNode(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")  # After tools, go back to assistant
