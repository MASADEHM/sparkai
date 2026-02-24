from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from backend.agent import graph
from backend.agent_tradename import tradename_agent_chain, detect_abbreviation
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import secrets

load_dotenv()

app = FastAPI()
security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify HTTP Basic Auth credentials against environment variables."""
    expected_username = os.getenv("API_USERNAME", "").strip()
    expected_password = os.getenv("API_PASSWORD", "").strip()
    if not expected_username or not expected_password:
        raise HTTPException(
            status_code=503,
            detail="API authentication is not configured",
            headers={"WWW-Authenticate": "Basic"},
        )
    correct_username = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        expected_username.encode("utf-8"),
    )
    correct_password = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        expected_password.encode("utf-8"),
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
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


class TradenameInput(BaseModel):
    name: str
  
@app.post("/")
async def chat(_: str = Depends(verify_credentials)):
    
    config = {"configurable": {"thread_id":"1"}}
    response = await graph.ainvoke({"messages": "Hello"}, config=config)
    return response["messages"]
# Endpoint for the main chat
@app.post("/chat")
async def chat(input: ChatInput, _: str = Depends(verify_credentials)):
    config = {"configurable": {"thread_id": input.thread_id}}
    response = await graph.ainvoke({"messages": input.messages}, config=config)
    return response["messages"][-1].content

# Endpoint for the tradename
@app.post("/tradename")
async def tradename(input: TradenameInput, _: str = Depends(verify_credentials)):
    # Normalize whitespace: collapse multiple spaces (e.g. "A.L.  Trading" -> "A.L. Trading")
    # and trim leading/trailing. Prevents inconsistent LLM behavior on messy input.
    normalized_name = " ".join(input.name.split())

    # Hybrid abbreviation detection: regex catches obvious acronyms (ABC, IT, MNS);
    # LLM catches edge cases. Either can flag it.
    regex_has_abbr = detect_abbreviation(normalized_name)
    response = tradename_agent_chain.invoke({"name": normalized_name})
    has_abbreviation = regex_has_abbr or response.hasAbbreviation

    return {
        "hasNumber": response.hasNumber,
        "hasGulf": response.hasGulf,
        "hasRegionName": response.hasRegionName,
        "hasArabizedName": response.hasArabizedName,
        "hasTrademark": response.hasTrademark,
        "hasAbbreviation": has_abbreviation,
        "arabicEquivalentName": response.arabicEquivalentName,
        "valid": response.valid,
        "remarks": response.remarks
    }
#  Endpoint for the executive summary

    

#use the below command to run the fast api server

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)
# # uvicorn main:app --reload