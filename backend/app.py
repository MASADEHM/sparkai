from fastapi import FastAPI
from pydantic import BaseModel
from backend.agent import graph
from backend.agent_tradename import tradename_agent_chain
from backend.agent_executivesummary import agent_summary_chain
from backend.agent_marketAnalysis import market_analysis_chain
from backend.agent_fundingrequirements import funding_requirements_chain
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

class MarketAnalysisInput(BaseModel):
    industry: str
    business_model: str
    emirate: str
    area: str = None  # Optional: if not provided, analysis covers whole emirate
    language: str = "English"

class FundingRequirementsInput(BaseModel):
    industry: str
    business_model: str
    emirate: str
    area: str = None
    target_market: str
    tam: float
    som: float
    language: str = "English"

  
@app.post("/")
async def chat():
    
    config = {"configurable": {"thread_id":"1"}}
    response = await graph.ainvoke({"messages": "Hello"}, config=config)
    return response["messages"]
# Endpoint for the main chat
@app.post("/chat")
async def chat(input: ChatInput):
    config = {"configurable": {"thread_id": input.thread_id}}
    response = await graph.ainvoke({"messages": input.messages}, config=config)
    return response["messages"][-1].content

# Endpoint for the tradename
@app.post("/tradename")
async def chat(input: ChatInput):
    config = {"configurable": {"thread_id": input.thread_id}}
    response = await tradename_agent_chain.ainvoke({"messages": input.messages}, config=config)
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

#  Endpoint for the executive summary
@app.post("/executivesummary")
async def generate_summary(input: ChatInput):
    config = {"configurable": {"thread_id": input.thread_id}}
    response = await agent_summary_chain.ainvoke({"messages": input.messages}, config=config)
    return {
        "summary": response.summary,
        "vision_analysis": response.vision_analysis,
        "mission_analysis": response.mission_analysis
    }

# Endpoint for the market analysis
@app.post("/marketanalysis")
async def generate_market_analysis(input: MarketAnalysisInput):
    print(input)
    response = market_analysis_chain.invoke({
        "industry": input.industry,
        "business_model": input.business_model,
        "emirate": input.emirate,
        "area": input.area,
        "language": input.language
    })
    return {
        "target_market": response.target_market,
        "market_size": response.market_size.dict(),
        "competitors": [competitor.dict() for competitor in response.competitors],
        "competitive_advantage": response.competitive_advantage
    }

# Endpoint for funding requirements analysis
@app.post("/fundingrequirements")
async def generate_funding_requirements(input: FundingRequirementsInput):
    # Generate funding requirements based on market analysis
    funding_response = funding_requirements_chain.invoke({
        "industry": input.industry,
        "business_model": input.business_model,
        "emirate": input.emirate,
        "area": input.area if input.area else "Not specified",
        "target_market": input.target_market,
        "tam": input.tam,
        "som": input.som,
        "language": input.language
    })
    
    return {
        "startup_costs_aed": funding_response.startup_costs_aed,
        "operational_costs_monthly_aed": funding_response.operational_costs_monthly_aed,
        "use_of_funds": funding_response.use_of_funds
    }

    

#use the below command to run the fast api server

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)
# # uvicorn main:app --reload