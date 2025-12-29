from typing import Literal
from langchain_openai.chat_models import ChatOpenAI,AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from backend.state import State
from pydantic import BaseModel,Field
load_dotenv()

class TradeName(BaseModel):
    hasNumber:bool = Field(default=False, description="Indicates if the trade name has a number")
    hasRegionName:bool = Field(default=False, description="Indicates if the trade name has a region name")
    hasArabizedName:bool = Field(default=False, description="Indicates if the trade name has an Arabized name")
    hasGlobalName:bool = Field(default=False, description="Indicates if the trade name has a global name")
    arabicEquivalentName:str = Field(default="", description="The Arabic equivalent of the trade name")
    result:bool=Field(default=False,description="this will be used tell user if the tradename is valid or not")
    remarks:str=Field(default="",description="return the reject reason by LLM")


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

##The AI agent must transliterate names provided in English into Arabic, preserving the original pronunciation and spelling as closely as possible without translating the meaning. Transliteration should follow the ALA-LC Romanization standard for Arabic (or specify another standard if preferred). 

- Input: The user will provide a name in English (e.g., personal names, company names, or mixed names).
- Output: The AI will return the name transliterated into Arabic script.
- Rules:
  1. Do not translate the meaning of the name; only transliterate based on pronunciation.
  2. Preserve the original word order unless Arabic grammar requires adjustment (e.g., for company names like "al Saqer Contracting").
  3. Handle special characters, spaces, or numbers by keeping them intact or transliterating phonetically where applicable (e.g., "Jean-Pierre" should be transliterated as "جان-بيار").
  4. If the input is already in Arabic or contains Arabic characters, return it unchanged with a note explaining why.
  5. Maintain capitalization only if it affects pronunciation; otherwise, follow Arabic script conventions.
  6. For ambiguous pronunciations, use the most common English pronunciation or request clarification from the user.

Examples:
- Input: "al Saqer Contracting" → Output: "الصقر للمقاولات"
- Input: "Mohammed Ali" → Output: "محمد علي"
- Input: "O'Connor" → Output: "أوكونور"
- Input: "123 Tech" → Output: "١٢٣ تك"
- Input: "خالد" → Output: "خالد (Input is already in Arabic, no transliteration needed)"

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
tradename_agent_chain=agent_prompt | structured_llm

