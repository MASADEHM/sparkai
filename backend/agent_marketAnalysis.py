from langchain_openai.chat_models import ChatOpenAI,AzureChatOpenAI
from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
import os


load_dotenv()


# 1. Pydantic Models (refined for business model with optional area specificity)
class Competitor(BaseModel):
    name: str = Field(..., description="Name of a real or representative competitor operating in the same area/emirate")
    strengths: List[str] = Field(..., min_length=2, max_length=3, description="Key strengths relevant to the market and business model")
    weaknesses: List[str] = Field(..., min_length=2, max_length=3, description="Key weaknesses that create opportunities")

class MarketSize(BaseModel):
    tam: float = Field(..., ge=0, description="Total Addressable Market in USD (area-specific if area provided, otherwise emirate-wide)")
    som: float = Field(..., ge=0, description="Serviceable Obtainable Market in USD, considering business model and realistic capture rate")

class MarketAnalysis(BaseModel):
    target_market: str = Field(..., description="Detailed profile of target customers, including demographics (expat/Emirati mix, age, income), psychographics (lifestyle, values), behaviors (shopping patterns, spending), and business model fit. Scope: area-specific if area provided, otherwise emirate-wide")
    market_size: MarketSize = Field(..., description="Market size estimates considering business model and realistic penetration. Scope: area-specific if area provided, otherwise emirate-wide")
    competitors: List[Competitor] = Field(..., min_length=3, max_length=5, description="Direct competitors with similar business models. Scope: area-specific if area provided, otherwise key competitors across the emirate")
    competitive_advantage: str = Field(..., description="Differentiated value proposition tailored to the target market demographics, business model strengths, and competitive gaps")

# 2. Output Parser
parser = PydanticOutputParser(pydantic_object=MarketAnalysis)

# 3. Prompt Template (UAE + Emirate-aware + Language support + Business Model + Optional Area)
system_template = """You are an expert market analyst specializing in the United Arab Emirates (UAE). 
The user will provide an INDUSTRY, BUSINESS MODEL, EMIRATE, optionally an AREA (specific location within emirate), and LANGUAGE.

Your task:
1. If AREA is provided: Conduct a market analysis **strictly within that specific AREA** in the emirate.
2. If AREA is NOT provided (null/None): Conduct a market analysis for the **entire EMIRATE**.
3. Focus on the specific BUSINESS MODEL provided to ensure relevance and accuracy.

Consider these factors based on scope (area-specific or emirate-wide):
   - Population size and composition (expats vs. nationals)
   - Economic profile of the emirate (e.g., Dubai = tourism & business hub; Abu Dhabi = government & oil wealth)
   - Local regulations, zoning laws, and licensing requirements
   - Consumer demographics, preferences, and behaviors
   - For area-specific: Foot traffic, accessibility, visibility, and micro-location factors
   - For emirate-wide: Distribution of target customers across different zones
   - Competitive landscape (area-specific or emirate-wide)
   - Realistic market size based on catchment population and spending power
   - Business model viability (e.g., B2C vs B2B, retail vs online, premium vs budget)

Tailor your analysis to the business model:
   - For retail/restaurant: Consider foot traffic, competitors, rent costs, location strategy
   - For B2B services: Consider business density, corporate presence, industry clusters
   - For online/delivery: Consider logistics, coverage zones, digital adoption
   - For premium/luxury: Consider high-income demographics concentration
   - For budget/value: Consider middle-income population density and accessibility

Use USD for all monetary values. If data is unavailable, make reasonable, transparent assumptions.

IMPORTANT: All text fields in your response must be in {language}. The JSON structure remains the same, but all string values should be written in {language}.

Respond ONLY in valid JSON matching the format below. No extra text.

{format_instructions}"""

human_template = """INDUSTRY: {industry}
BUSINESS MODEL: {business_model}
EMIRATE: {emirate}
AREA: {area}
LANGUAGE: {language}

Provide a realistic market analysis for this business model and industry.
- If AREA is specified: Focus deeply on that specific area within {emirate}, considering its unique characteristics and how the {business_model} business model fits the local market dynamics.
- If AREA is null/None: Provide an emirate-wide analysis for {emirate}, covering key commercial zones and overall market potential.
Remember to respond in {language}."""

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template(human_template)
]).partial(format_instructions=parser.get_format_instructions())

# 4. Set up the LLM (example: OpenAI)
llm = AzureChatOpenAI(
    model="gpt-4o-mini",  # or "gpt-4o", "claude-3-haiku", etc.
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY")  # Ensure this is set in your environment
)

# 5. Create the chain
market_analysis_chain = prompt | llm | parser


#llm=ChatOpenAI(model="gpt-4o-mini")


# agent_prompt=ChatPromptTemplate.from_messages([
#     ("system",system_tradename),
#     ("placeholder","{messages}"),
#     # ("human","{user_input}")
# ])

# structured_llm=llm.with_structured_output(MarketAnalysis)
# agent_chain=agent_prompt | structured_llm

