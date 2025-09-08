from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pyotp,smtplib,os
from langchain_core.tools import tool
from backend.schema import Profile
from langchain_community.tools import TavilySearchResults
from dotenv import load_dotenv
from backend.rag.ragchain import retrieval_chain

load_dotenv()

SMTPPWD=os.getenv("SMTP_PWD")
SMTPSERVER=os.getenv("SMTP_SERVER")
SMTPPORT=os.getenv("SMTP_PORT")
SMTPUSER=os.getenv("SMTP_USER")
TAVILYAPIKEY=os.getenv("TAVILY_API_KEY")
OTP_SECRET = pyotp.random_base32()

@tool
def searchdocs(query:str)->dict:
  """
    Search the company’s vector store for documents related to policies, procedures, regulations, roles, 
    responsibilities, performance, or discipline. 
    Use this tool for all queries about company-specific rules or guidelines.
    
    Args:
        query (str): The search query to find relevant documents.
    
    Returns:
        dict: A dictionary containing the answer and retrieved documents.
              Format: {"answer": str, "documents": [{"content": str, "metadata": dict}, ...]}
    """
  
  response=retrieval_chain.invoke({"input": query})
  print(f"response from searchdocs {response}")
    # if len(result)>0:
    #     result=[{"content":doc.page_content,"metadata":doc.metadata} for doc in result]
    # else:
    #     result=[]
  return response["answer"]


@tool
def searchuser(email:str)->dict:
    """
    search user by email or employee number
    Args:
     email (employee email) 
     empno (employee number)
    Returns:
     user profile object
    """
    if (email=="muhcis@gmail.com"):
        return {
            "message":f"profile successfully found {email}",
            "status":"success",
            
           
        }
    return {
        "message":f"no profile was found {email}",
        "status":"not found",
        
    }
@tool 
def TavilySearch(searchquery:str):
    """
    search web for results
    """
    tavily_search=TavilySearchResults(max_results=1)
    
    results=tavily_search.invoke(searchquery)
    return results

@tool 
def sendemail(to:str,subject:str,body:str)-> dict:
    """
   this a tool used to Send Emails to users 

    Args:
     to: receiver email address
     subject: email subject
     body: email body
    """
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = "noreply@inventix.com"
    msg['To'] = to
    msg['Subject'] = subject
    
    # Attach the email body
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP(SMTPSERVER, SMTPPORT)
        print(f"send email is called port is {SMTPPORT} smptserver {SMTPSERVER}")
        # server.starttls()  # Enable TLS 
        server.send_message(msg)
        server.quit()
        return {
            "status": "success",
            "message": f"Email sent successfully to {to} with subject '{subject}'"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to send email: {str(e)}"
        }

def generate_otp() -> str:
    """
    Generating One-Time Password (OTP)

    Returns:
        str: One-Time Password (OTP)
    """
    return pyotp.TOTP(OTP_SECRET, digits=6).now()

def verify_otp(otp_secret: str) -> bool:
    """
    Verifying One-Time Password (OTP)

    Args:
        otp_secret (str): One-Time Password (OTP)

    Returns:
        str: True or False
    """
    return pyotp.TOTP(OTP_SECRET).verify(otp_secret.strip(), valid_window=120)