from email.mime.text import MIMEText
import os, secrets, smtplib, time
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from tavily import TavilyClient
from dotenv import load_dotenv
from backend.rag.ragchain import answer

load_dotenv()

SMTPPWD=os.getenv("SMTP_PWD")
SMTPSERVER=os.getenv("SMTP_SERVER")
SMTPPORT=os.getenv("SMTP_PORT")
SMTPUSER=os.getenv("SMTP_USER")
OTP_TTL_SECONDS = 300

# ponytail: in-process dicts — lost on restart (user just re-verifies) and not shared
# across workers/replicas. Move to Redis/DB if the API runs more than one process.
_pending_otps: dict[str, tuple[str, str, float]] = {}  # thread_id -> (email, otp, expires_at)
_verified: dict[str, str] = {}  # thread_id -> verified email

NOT_VERIFIED = {"status": "error", "message": "User is not verified. Ask for their email and verify it with an OTP first."}


def _thread_id(config: RunnableConfig) -> str:
    return config["configurable"]["thread_id"]


def _find_user(email: str) -> bool:
    # TODO: replace with the real user directory lookup
    return email.strip().lower() == "muhcis@gmail.com"


def _send(to: str, subject: str, body: str) -> None:
    msg = MIMEText(body, 'plain')
    msg['From'] = "noreply@inventix.com"
    msg['To'] = to
    msg['Subject'] = subject
    with smtplib.SMTP(SMTPSERVER, int(SMTPPORT)) as server:
        if SMTPUSER:  # never send credentials over plaintext
            server.starttls()
            server.login(SMTPUSER, SMTPPWD)
        server.send_message(msg)


@tool
def searchdocs(query: str, config: RunnableConfig):
    """
    Search the company’s vector store for documents related to policies, procedures, regulations, roles, 
    responsibilities, performance, or discipline. 
    Use this tool for all queries about company-specific rules or guidelines.

    Args:
        query (str): The search query to find relevant documents.
    """
    if _thread_id(config) not in _verified:
        return NOT_VERIFIED
    return answer(query)


@tool
def searchuser(email: str) -> dict:
    """
    search user by email
    Args:
     email (employee email)
    """
    if _find_user(email):
        return {"message": f"profile successfully found {email}", "status": "success"}
    return {"message": f"no profile was found {email}", "status": "not found"}


@tool
def TavilySearch(searchquery: str, config: RunnableConfig):
    """
    search web for results
    """
    if _thread_id(config) not in _verified:
        return NOT_VERIFIED
    return TavilyClient().search(searchquery, max_results=1)["results"]


@tool
def send_otp(email: str, config: RunnableConfig) -> dict:
    """
    Generate a one-time password and email it to the user. The code is never returned to you.
    Args:
     email: the user's email address (must be a known user)
    """
    if not _find_user(email):
        return {"status": "not found", "message": f"no profile was found {email}"}
    otp = f"{secrets.randbelow(10**6):06d}"
    try:
        _send(email, "Your verification code", f"Your verification code is {otp}. It expires in 5 minutes.")
    except Exception as e:
        return {"status": "error", "message": f"Failed to send OTP: {e}"}
    _pending_otps[_thread_id(config)] = (email, otp, time.time() + OTP_TTL_SECONDS)
    return {"status": "success", "message": f"OTP sent to {email}"}


@tool
def verify_otp(otp: str, config: RunnableConfig) -> dict:
    """
    Verify the one-time password the user received by email.
    Args:
     otp: the code the user typed
    """
    thread_id = _thread_id(config)
    pending = _pending_otps.get(thread_id)
    if not pending or time.time() > pending[2]:
        return {"status": "error", "message": "No valid OTP pending, send a new one."}
    email, expected, _ = pending
    if not secrets.compare_digest(otp.strip(), expected):
        return {"status": "error", "message": "Incorrect OTP."}
    del _pending_otps[thread_id]
    _verified[thread_id] = email
    return {"status": "success", "message": f"{email} verified"}


@tool
def sendemail(subject: str, body: str, config: RunnableConfig) -> dict:
    """
    Send an email to the verified user of this conversation.

    Args:
     subject: email subject
     body: email body
    """
    to = _verified.get(_thread_id(config))
    if not to:
        return NOT_VERIFIED
    try:
        _send(to, subject, body)
        return {"status": "success", "message": f"Email sent successfully to {to} with subject '{subject}'"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to send email: {e}"}
