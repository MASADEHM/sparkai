from typing import Literal
from langchain_openai.chat_models import ChatOpenAI,AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from backend.state import State
from backend.schema import TradeName

load_dotenv()

#system messages
system_tradename="""
You are a bot designed to analyze commercial trade names and verify them against specific characteristics.
For the provided trade name, return a JSON object with the following properties:

Analyze the trade name strictly based on these criteria and return only the JSON result , without any additional text or explanation. 
hasNumber: Boolean - whether the trade name contains any numbers.
hasRegionName: Boolean - whether the trade name includes the name of a region (e.g., Gulf, Arabia, Middle East).
hasArabizedName: Boolean - whether the trade name is an Arabized version of a foreign name (e.g., "مايكروسوفت" for Microsoft).
hasGlobalName: Boolean - whether the trade name resembles a widely recognized global or international brand name (e.g., Coca-Cola, Apple, Samsung).
arabicEquivalentName: String - provide the Arabic equivalent name as it is used , Do not translate the name into Arabic; 
result:string - a summary of the analysis result that list if the trade name is valid or not based on the criteria below.
remarks:string - the reasons for the invalidity of the trade name if it is not valid, or an empty string if it is valid.

- If the tradename has or don't has a number or region name or arabized name then the result should be "Valid" and remarks should be empty string.
- for the inpur provided consider each word first letter as capital letter, for example "al saqer contracting" should be considered as "Al Saqer Contracting".
Names should be written literally and not translated. (For example, if the Arabic name is (للمقاوالت الصقر (it must be written as "al Saqer contracting".

The result should be one of the following:
- "Valid": if the trade name meets all the criteria.
- "Invalid": if the trade name did not pass the following validation checks:

- If the trade name include widely recognized global or international brand name (e.g., Coca-Cola, Apple, Samsung).
- The name should not include Allaah's name nor "God" or His divine attributes, for example (al wader, al alee, al razzaq, etc ….).
- The name should not include the name of a country or government.
- The name cannot include any restricted names such as global political organisations, religious sectarian organisation etc. (For example, FBI, Mafia.).
- The name should not include any of the punctuation marks, such as (., !?/).
"""

#llm=ChatOpenAI(model="gpt-4o-mini")
llm=AzureChatOpenAI(model="gpt-4o-mini")

agent_prompt=ChatPromptTemplate.from_messages([
    ("system",system_tradename),
    ("placeholder","{messages}"),
    # ("human","{user_input}")
])

structured_llm=llm.with_structured_output(TradeName)
agent_chain=agent_prompt | structured_llm

