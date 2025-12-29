from langchain_openai.chat_models import AzureChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
import os


load_dotenv()


# 1. Pydantic Model
class ProductServiceDescription(BaseModel):
    description: str = Field("Comprehensive product or service description tailored to the industry and business model"
    )


# 2. Output Parser
parser = PydanticOutputParser(pydantic_object=ProductServiceDescription)


# 3. Prompt Template
system_template = """You are an expert business consultant specializing in product and service development. 
The user will provide an INDUSTRY, BUSINESS MODEL, and LANGUAGE.

Your task:
Generate a comprehensive, compelling product/service description that:
1. Clearly defines what the business offers (products, services, or both)
2. Highlights key features and benefits relevant to the industry
3. Aligns with the specified business model (B2C, B2B, online, retail, premium, budget, etc.)
4. Addresses customer pain points and needs
5. Differentiates from typical offerings in the industry
6. Includes specific examples where applicable
7. Emphasizes value proposition and unique selling points

Consider these factors based on the business model:
   - For retail/restaurant: Product range, quality, customer experience, ambiance
   - For B2B services: Professional expertise, solutions offered, delivery methods
   - For online/delivery: Convenience, speed, technology integration
   - For premium/luxury: Quality, exclusivity, personalized service
   - For budget/value: Affordability, accessibility, essential features

The description should be:
   - Detailed and specific (200-400 words)
   - Professional yet engaging
   - Customer-focused
   - Industry-appropriate
   - Aligned with the business model strategy

IMPORTANT: Your entire response must be in {language}. The JSON structure remains the same, but the description text should be written entirely in {language}.

Respond ONLY in valid JSON matching the format below. No extra text.

{format_instructions}"""

human_template = """INDUSTRY: {industry}
BUSINESS MODEL: {business_model}
LANGUAGE: {language}

Generate a comprehensive product/service description for this business that:
- Reflects the unique characteristics of the {industry} industry
- Aligns with the {business_model} business model approach
- Is written entirely in {language}
- Provides clear value to potential customers
- Differentiates from competitors in the market"""

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template(human_template)
]).partial(format_instructions=parser.get_format_instructions())


# 4. Set up the LLM
llm = AzureChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5,  # Slightly higher for creative descriptions
    api_key=os.getenv("OPENAI_API_KEY")
)


# 5. Create the chain
product_description_chain = prompt | llm | parser

