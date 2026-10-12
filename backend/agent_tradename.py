import re
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

# Matches 2+ consecutive uppercase letters as a standalone word (e.g. ABC, IT, MNS).
# Used for hybrid detection alongside LLM; does not match "A.L." (periods break the pattern).
_ABBREVIATION_RE = re.compile(r'\b[A-Z]{2,}\b')


def detect_abbreviation(name: str) -> bool:
    # An all-caps name ("AL SAQER CONTRACTING") is just shouting, not acronyms; leave it to the LLM.
    return not name.isupper() and bool(_ABBREVIATION_RE.search(name))

class TradeName(BaseModel):
    hasNumber:bool = Field(default=False, description="Indicates if the trade name has a number")
    hasGulf:bool = Field(default=False, description="Indicates if the trade name has a Gulf name")
    hasRegionName:bool = Field(default=False, description="Indicates if the trade name has a region name")
    hasArabizedName:bool = Field(default=False, description="Indicates if the trade name has an Arabized name")
    hasTrademark:bool = Field(default=False, description="Indicates if Part of the Trade Name is a Trade Mark")
    hasAbbreviation:bool = Field(default=False, description="Indicates if the trade name contains an abbreviation or acronym")
    arabicEquivalentName:str = Field(default="", description="The Arabic equivalent of the trade name")
    valid:bool=Field(default=False,description="this will be used tell user if the tradename is valid or not")
    remarks:str=Field(default="",description="return the reject reason by LLM")


# System prompt for trade name analysis.
# The IMPORTANT block below instructs the LLM that hasNumber, hasGulf, hasRegionName,
# hasArabizedName, hasTrademark, and hasAbbreviation are informational only—they must
# never set valid=false or add remarks. Without this, the LLM was incorrectly marking
# names like "A.L. Trading" invalid with "abbreviation not allowed".
system_prompt="""
You are a bot designed to analyze commercial trade names and verify them against specific characteristics.
For the provided trade name, return a JSON object with the following properties:

Analyze the trade name strictly based on these criteria and return only the JSON result , without any additional text or explanation. 
hasNumber: Boolean - whether the trade name contains any numbers.
hasGulf: Boolean - whether the trade name includes the word "Gulf" or the name of a Gulf region/country (e.g., Gulf, Dubai, Abu Dhabi, Sharjah, Doha, Riyadh, Jeddah, Kuwait, Oman, Bahrain, Qatar, UAE, Saudi Arabia, etc.).
hasRegionName: Boolean - whether the trade name includes a generic region name other than Gulf (e.g., Arabia, Middle East, Levant, etc.). Note: "Gulf" is covered by hasGulf.
hasArabizedName: Boolean - whether the trade name is an Arabized version of a foreign name (e.g., "مايكروسوفت" for Microsoft).
hasTrademark: Boolean - whether the trade name resembles a widely recognized global or international brand name (e.g., Coca-Cola, Apple, Samsung).
hasAbbreviation: Boolean - whether the trade name contains abbreviations or acronyms (e.g., "ABC", "IT", "MNS"). These are typically 2 or more consecutive uppercase letters forming a non-standard word. Do not consider legal entity suffixes (LLC, FZE, FZCO) as the input will never include them.

arabicEquivalentName: String - provide the Arabic equivalent name as it is used , Do not translate the name into Arabic; 
valid: Boolean - true if the trade name meets all validation criteria, false otherwise.
remarks: String - the reasons for the invalidity of the trade name if valid is false, or an empty string if valid is true.

- Since this is a trade name name must start with capital letter, for example "al saqer contracting" should be considered as "Al Saqer Contracting".
- If the tradename has or does not have a number, region name, or arabized name, then valid should be true and remarks should be an empty string.
- for the inpur provided consider each word first letter as capital letter, for example "al saqer contracting" should be considered as "Al Saqer Contracting".

##The AI agent must Transliteration names provided in English into Arabic, preserving the original pronunciation and spelling as closely as possible without translating the meaning.

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

IMPORTANT: The flags hasNumber, hasGulf, hasRegionName, hasArabizedName, hasTrademark, and hasAbbreviation are INFORMATIONAL ONLY. They must NEVER cause valid to be false or add any text to remarks. 
Trade names with abbreviations (e.g., "A.L. Trading", "ABC Co"), numbers, Gulf names, region names, Arabized names, or trademarks are valid. 
Do not mention abbreviations in remarks.
Set valid to false and populate remarks ONLY when the name fails one of the validation checks listed below. 

- The name should not include Allaah's name nor "God" or His divine attributes, for example (al wader, al alee, al razzaq, etc ….).
- The name should not include the name of a country or government.
- The name cannot include any restricted names such as global political organisations, religious sectarian organisation etc. (For example, FBI, Mafia.).
- The name should not include any of the punctuation marks, such as (, !?/). Periods used in abbreviations (e.g. "A.L.") are allowed.
"""

llm=AzureChatOpenAI(model="gpt-4o-mini")

agent_prompt=ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "Analyze the following trade name: {name}"),
])

structured_llm=llm.with_structured_output(TradeName)
tradename_agent_chain=agent_prompt | structured_llm

