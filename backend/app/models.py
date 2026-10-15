from pydantic import BaseModel, Field, HttpUrl
from typing import Literal

class ICP(BaseModel):
    target_industries: list[str] = Field(default_factory=lambda: ["SaaS", "Financial Services", "Healthcare", "Manufacturing", "Retail", "Technology"])
    target_geographies: list[str] = Field(default_factory=lambda: ["United States", "United Kingdom", "India", "Canada", "Australia"])
    min_employee_count: int = 50
    ideal_employee_count: int = 500
    services: list[str] = Field(default_factory=lambda: ["cloud", "data analytics", "AI automation"])

class LeadRequest(BaseModel):
    companies: list[str] = Field(min_length=1, max_length=25)
    icp: ICP = Field(default_factory=ICP)
    research_live: bool = True

class Evidence(BaseModel):
    title: str
    url: str
    snippet: str = ""
    source_domain: str = ""
    evidence_type: Literal["search_result", "company_site", "sample"] = "search_result"

class LeadResult(BaseModel):
    company: str
    score: int = Field(ge=0, le=100)
    tier: Literal["High fit", "Potential fit", "Low fit", "Needs research"]
    rationale: list[str]
    industry: str = "Unknown"
    geography: str = "Unknown"
    estimated_size: str = "Unknown"
    signals: list[str]
    missing_information: list[str]
    confidence: Literal["High", "Medium", "Low"]
    human_review_required: bool = True
    evidence: list[Evidence]

class QualificationResponse(BaseModel):
    results: list[LeadResult]
    scoring_method: dict
    research_mode: str
    warnings: list[str] = Field(default_factory=list)
