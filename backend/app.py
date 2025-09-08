from fastapi import FastAPI
from pydantic import BaseModel
from backend.agent import graph
from backend.agent_tradename import agent_chain
from backend.agent_executivesummary import agent_summary_chain
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
class ChatInput(BaseModel):
    messages: list[str]
    thread_id: str

class Tradename(BaseModel):
    trade_name: str
  
@app.post("/")
async def chat():
    
    config = {"configurable": {"thread_id":"1"}}
    response = await graph.ainvoke({"messages": "Hello"}, config=config)
    return response["messages"]

@app.post("/chat")
async def chat(input: ChatInput):
    config = {"configurable": {"thread_id": input.thread_id}}
    response = await graph.ainvoke({"messages": input.messages}, config=config)
    return response["messages"][-1].content

@app.post("/tradename")
async def chat(input: ChatInput):
    config = {"configurable": {"thread_id": input.thread_id}}
    response = await agent_chain.ainvoke({"messages": input.messages}, config=config)
     # Convert the TradeName object to a dictionary for the response
    return {
        "hasNumber": response.hasNumber,
        "hasRegionName": response.hasRegionName,
        "hasArabizedName": response.hasArabizedName,
        "hasGlobalName": response.hasGlobalName,
        "arabicEquivalentName": response.arabicEquivalentName,
        "result": response.result,
        "remarks": response.remarks 
        
        
    }

@app.post("/executivesummary")
async def generate_summary(input: ChatInput):
    config = {"configurable": {"thread_id": input.thread_id}}
    response = await agent_summary_chain.ainvoke({"messages": input.messages}, config=config)
    return {
        "summary": response.summary,
        "vision_analysis": response.vision_analysis,
        "mission_analysis": response.mission_analysis
    }

#use the below command to run the fast api server

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)
# # uvicorn main:app --reload