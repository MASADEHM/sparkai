from langchain_openai.chat_models import ChatOpenAI,AzureChatOpenAI
from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
import os


load_dotenv()


# 1. Pydantic Models for Funding Requirements
class FundingRequirements(BaseModel):
    startup_costs_aed: float = Field(..., ge=0, description="Total startup/initial costs in AED, including setup, licensing, equipment, initial inventory, deposits, and launch costs")
    operational_costs_monthly_aed: float = Field(..., ge=0, description="Monthly operational expenses in AED, including rent, salaries, utilities, marketing, supplies, and recurring costs")
    use_of_funds: str = Field(..., description="Detailed breakdown explaining how the funds will be allocated across different expense categories, with specific line items and justifications based on the business model and market context")

# 2. Output Parser
parser = PydanticOutputParser(pydantic_object=FundingRequirements)

# 3. Prompt Template for Funding Requirements Analysis
system_template = """You are an expert financial analyst and business consultant specializing in the United Arab Emirates (UAE). 
Your task is to provide a comprehensive funding requirements analysis based on the provided market analysis data.

You will receive:
- INDUSTRY: The business industry
- BUSINESS MODEL: The specific business model
- EMIRATE: The target emirate
- AREA: The specific area (or null if emirate-wide)
- TARGET MARKET: Customer profile and demographics
- MARKET SIZE: TAM and SOM estimates
- LANGUAGE: The language for the response

Your task:
1. Calculate realistic STARTUP COSTS in AED, including:
   - Trade license and business setup fees including the license fee and the registration fee for that specific emirate)
   - Physical space costs (rent deposits, fit-out, furniture) - adjust for area/emirate rental rates
   - Equipment and technology (POS systems, kitchen equipment, computers, software)
   - Initial inventory or supplies (3-6 months depending on business model)
   - Marketing and branding (logo, website, signage, launch campaign)
   - Professional fees (legal, accounting, consultants)
   - Working capital buffer (2-3 months operational costs)
   - Insurance and permits
   - Contingency (10-15% of total)

2. Calculate realistic MONTHLY OPERATIONAL COSTS in AED, including:
   - Rent (based on emirate and area - Dubai Marina vs Al Quoz have different rates)
   - Salaries and benefits (consider UAE labor market rates and visa costs)
   - Utilities (DEWA/ADDC/SEWA depending on emirate)
   - Marketing and advertising (digital, traditional, social media)
   - Inventory/supplies replenishment
   - Maintenance and repairs
   - Insurance premiums
   - Professional services (accounting, legal)
   - Technology subscriptions (software, cloud services)
   - Miscellaneous and contingency

3. Provide detailed USE OF FUNDS breakdown explaining:
   - Specific allocation percentages or amounts for each category
   - Justification based on business model and market context
   - UAE-specific considerations (visa costs, trade license types, RAKEZ vs mainland)
   - Industry-specific requirements
   - Area-specific cost variations

Use realistic UAE market rates and costs. Consider:
- Dubai is 20-30% more expensive than other emirates
- Premium areas (Marina, Downtown) are 50-100% more expensive than suburban areas
- Free zone costs differ significantly from mainland
- Labor costs vary by nationality and skill level (typical range: AED 3,000-15,000/month)
- Retail rent: AED 80-300/sqft annually depending on location
- F&B fit-out: AED 800-2,000/sqft depending on concept

IMPORTANT: All monetary values must be in AED (UAE Dirhams). All text fields must be in {language}.

Respond ONLY in valid JSON matching the format below. No extra text.

{format_instructions}"""

human_template = """INDUSTRY: {industry}
BUSINESS MODEL: {business_model}
EMIRATE: {emirate}
AREA: {area}
TARGET MARKET: {target_market}
MARKET SIZE TAM: {tam}
MARKET SIZE SOM: {som}
LANGUAGE: {language}

Provide a detailed, realistic funding requirements analysis for this business in the UAE context.
Consider the specific emirate and area costs, the business model requirements, and the target market characteristics.
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
funding_requirements_chain = prompt | llm | parser

