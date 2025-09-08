from pydantic import BaseModel,Field

class Profile(BaseModel):
    email:str=Field(description="user email address")
    empname:str=Field(description="user name")
    empid:int=Field(description="user employee id")
    
class TradeName(BaseModel):
    hasNumber:bool = Field(default=False, description="Indicates if the trade name has a number")
    hasRegionName:bool = Field(default=False, description="Indicates if the trade name has a region name")
    hasArabizedName:bool = Field(default=False, description="Indicates if the trade name has an Arabized name")
    hasGlobalName:bool = Field(default=False, description="Indicates if the trade name has a global name")
    arabicEquivalentName:str = Field(default="", description="The Arabic equivalent of the trade name")
    result:bool=Field(default=False,description="this will be used tell user if the tradename is valid or not")
    remarks:str=Field(default="",description="return the reject reason by LLM")

class ExecutiveSummary(BaseModel):
    summary: str = Field(description="a brief summary based on vision and mission analysis")
    vision_analysis: str = Field(description="analysis of the vision statement")
    mission_analysis: str = Field(description="analysis of the mission statement")
