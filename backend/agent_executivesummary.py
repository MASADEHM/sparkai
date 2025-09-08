from typing import Literal
from langchain_openai.chat_models import ChatOpenAI,AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from backend.state import State
from backend.schema import ExecutiveSummary

load_dotenv()

#system messages
system_executivesummary = """
You are a bot designed to analyze vision and mission statements and provide an executive summary.

For the provided vision and mission statements, analyze and return a JSON object with the following properties:
- summary: A concise summary combining both vision and mission analysis
- vision_analysis: Analysis of how well the vision statement defines the desired future state
- mission_analysis: Analysis of how well the mission statement defines current purpose and methods

Return only the JSON result, without any additional text or explanation.
"""

#llm=ChatOpenAI(model="gpt-4o-mini")
llm=AzureChatOpenAI(model="gpt-4o-mini")

agent_prompt=ChatPromptTemplate.from_messages([
    ("system",system_executivesummary),
    ("placeholder","{messages}"),
    # ("human","{user_input}")
])

structured_llm=llm.with_structured_output(ExecutiveSummary)
agent_summary_chain=agent_prompt | structured_llm

