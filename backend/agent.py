from langchain_openai.chat_models import ChatOpenAI,AzureChatOpenAI
from langgraph.graph import StateGraph,END
from langchain_core.messages import filter_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import Image,display
from backend.state import State
from dotenv import load_dotenv
from backend.schema import Profile
from backend.prompts import sysprompts
from backend.tools import TavilySearch,sendemail,searchuser,generate_otp,verify_otp,searchdocs
import os
import json

# load_dotenv(dotenv_path="../.env")

# AZURE_OPENAI_EMEBDDING_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMEBDDING_DEPLOYMENT")
# print(f"AZURE_OPENAI_EMEBDDING_DEPLOYMENT_NAME is {AZURE_OPENAI_EMEBDDING_DEPLOYMENT_NAME}")

llm=AzureChatOpenAI(model="gpt-4o-mini")

tools=[TavilySearch,sendemail,searchuser,generate_otp,verify_otp,searchdocs]
llmwithtools=llm.bind_tools(tools)

def route_nodes(state:State)->str:
    if state.get('next')=="collect_info":
        return "collect_info"
    elif state.get('next')=="assistant":
        return "assistant"
    else:
        return "checkprofile"

def checkprofile(state:State)->State:
    print(f"checkprofile is called")
    if state.get('profile'):
        if state.get('isverified')==True:
            return{"next":"assistant"}
    return{"next":"collect_info"}


def collect_info(state:State)->State:
    print(f"collect_info is called")
    # #filter messages to fetch user profile from messages
    if not state.get('profile'):
        filterdmessages=filter_messages(state['messages'],include_names =["searchuser"])        
        if len(filterdmessages)>0:
            # fetch profile from the messages if searchuser return success status 
            for msg in filterdmessages:
                data = json.loads(msg.content)
                status = data["status"]
                if status=="success":
                # profile=Profile(**data["profile"])
                 llmwithoutput=llm.with_structured_output(Profile)
                 userprofile= llmwithoutput.invoke(f"Extract the name and email from this user response: '{filterdmessages[0].content}'")
                #  user_profile_chain = llm.with_structured_output(UserProfile) 
                #  user_profile = await user_profile_chain.ainvoke(relevant_messages[0].content)

                 print(f"userprofile {userprofile}")
                 return {
                     "messages":state['messages'],
                     "profile":userprofile        
                     }
        return{
            "messages":state['messages'],
            "next":"assistant"
        }
    else:
        #Prfile is already loaded
        print(f"profile is loaded collect info is {state.get('profile')}:")
        return{
            "messages":state['messages'],
            "next":"assistant"
        }


def should_continue(state: State) -> str:
    messages = state["messages"]
    last_message = messages[-1]    
    print(f"Last message: {last_message}")
    print(f"Tool calls: {last_message.tool_calls}")
    # Check if there are tool calls and they are valid
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print("Routing to tools node")
        return "tools"
    print("No tool calls detected, ending flow")
    return END

def assistant(state: State) -> State:
    response = llmwithtools.invoke([sysprompts] + state['messages'])
    # print(f"response is {response}")
    return {"messages":response}

builder=StateGraph(State)
builder.add_node("checkprofile",checkprofile)
builder.add_node("collect_info",collect_info)
builder.add_node("assistant",assistant)
builder.add_node("tools",ToolNode(tools))

builder.set_entry_point("checkprofile")
builder.add_conditional_edges("checkprofile",route_nodes,["collect_info","assistant"])
builder.add_edge("collect_info","assistant")
builder.add_edge("tools", "assistant")  # After tools, go back to assistant
builder.add_conditional_edges("assistant", should_continue, {"tools": "tools", END: END})

graph=builder.compile(checkpointer=MemorySaver())

#display(Image(graph.get_graph().draw_mermaid_png(output_file_path="agent.png")))


# config={"configurable": {"thread_id":"100"}}

# while True:
#     #get user input
#     user_input=input("User: ")
#     input_state = {"messages": user_input}
#     if user_input=="exit":
#         break
#     #get response
#     response=graph.invoke(input_state,config=config)      
#     print("Agent:",response)