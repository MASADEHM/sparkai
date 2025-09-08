from typing import Literal, Optional, TypedDict,Annotated,Any,Dict
from langgraph.graph import StateGraph, MessagesState,END,START,add_messages
from langchain_core.messages import AnyMessage
from backend.schema import Profile
class State(TypedDict):
    messages:Annotated[list[AnyMessage],add_messages]
    profile:Profile=""
    isverified:bool=False
    next:str=""