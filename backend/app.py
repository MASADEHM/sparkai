from dotenv import load_dotenv

load_dotenv()  # before the backend imports, which read env vars at import time

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from pydantic import BaseModel
from backend.agent import builder
from backend.agent_tradename import tradename_agent_chain, detect_abbreviation
import os
import secrets


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Chat history survives restarts; set CHECKPOINT_DB to a mounted volume in Docker.
    async with AsyncSqliteSaver.from_conn_string(os.getenv("CHECKPOINT_DB", "checkpoints.sqlite")) as saver:
        app.state.graph = builder.compile(checkpointer=saver)
        yield


app = FastAPI(lifespan=lifespan)
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


# Clients must send the Authorization header explicitly; browsers won't attach
# cached/ambient credentials cross-origin. Restrict with CORS_ORIGINS=https://a.com,https://b.com
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatInput(BaseModel):
    messages: list[str]
    thread_id: str


class TradenameInput(BaseModel):
    name: str


@app.get("/health")
async def health():
    return {"status": "ok"}


# Endpoint for the main chat
@app.post("/chat")
async def chat(input: ChatInput, _: str = Depends(verify_credentials)):
    config = {"configurable": {"thread_id": input.thread_id}}
    response = await app.state.graph.ainvoke({"messages": input.messages}, config=config)
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
    response = await tradename_agent_chain.ainvoke({"name": normalized_name})
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
