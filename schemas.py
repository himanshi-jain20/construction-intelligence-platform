from typing import Literal
from pydantic import BaseModel, Field

class InsightResponse(BaseModel):
    feature: str
    summary: str
    findings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    risk_level: Literal["low", "medium", "high", "unknown"] = "unknown"
    limitations: list[str] = Field(default_factory=list)
    demo_mode: bool = False

class ValuationRequest(BaseModel):
    location: str = Field(min_length=2, max_length=200)
    area_sqft: float = Field(gt=0, le=10_000_000)
    property_type: str = Field(min_length=2, max_length=80)
    age_years: float = Field(ge=0, le=300)
    condition: Literal["poor", "fair", "good", "excellent"]
    rate_per_sqft: float = Field(gt=0, le=10_000_000)
    currency: str = Field(default="INR", min_length=3, max_length=5)

class PlanningRequest(BaseModel):
    project_type: str = Field(min_length=2, max_length=100)
    site_location: str = Field(min_length=2, max_length=200)
    built_up_area_sqft: float = Field(gt=0, le=100_000_000)
    floors: int = Field(ge=1, le=200)
    target_duration_weeks: int = Field(ge=1, le=520)
    budget: float | None = Field(default=None, gt=0)
    notes: str = Field(default="", max_length=4000)

class TextRequest(BaseModel):
    question: str = Field(min_length=2, max_length=6000)
    context: str = Field(default="", max_length=8000)

class WeatherRequest(BaseModel):
    location: str = Field(min_length=2, max_length=200)
    conditions: str = Field(min_length=2, max_length=2000)
    planned_activity: str = Field(min_length=2, max_length=500)
