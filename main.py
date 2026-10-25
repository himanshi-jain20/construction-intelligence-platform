import os
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from .schemas import InsightResponse, PlanningRequest, TextRequest, ValuationRequest, WeatherRequest
from .services import insight

app = FastAPI(title="Construction Intelligence API", version="1.0.0")
origins = [s.strip() for s in os.getenv("FRONTEND_ORIGINS","http://localhost:5173").split(",") if s.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
MAX_MB = int(os.getenv("MAX_IMAGE_MB","8"))
ALLOWED = {"image/jpeg","image/png","image/webp"}

@app.get("/health")
def health():
    return {"status":"ok","service":"construction-intelligence-api"}

async def get_image(image: UploadFile):
    if image.content_type not in ALLOWED: raise HTTPException(415,"Upload JPG, PNG, or WEBP.")
    data = await image.read()
    if not data: raise HTTPException(400,"Image is empty.")
    if len(data) > MAX_MB * 1024 * 1024: raise HTTPException(413,f"Image exceeds {MAX_MB} MB.")
    return data, image.content_type

@app.post("/api/safety/analyze", response_model=InsightResponse)
async def safety(image: UploadFile = File(...), context: str = Form(default="")):
    data,mime = await get_image(image)
    return insight("safety","Review visible potential construction hazards: PPE, fall hazards, housekeeping, access, equipment proximity, signage. Do not certify compliance.",context,data,mime)

@app.post("/api/cracks/analyze", response_model=InsightResponse)
async def cracks(image: UploadFile = File(...), context: str = Form(default="")):
    data,mime = await get_image(image)
    return insight("cracks","Describe visible crack-like features and what measurements/professional inspection are needed. Never diagnose structural integrity.",context,data,mime)

@app.post("/api/valuation/estimate", response_model=InsightResponse)
def valuation(r: ValuationRequest):
    cf = {"poor":.75,"fair":.88,"good":1.0,"excellent":1.08}[r.condition]
    af = max(.65,1-r.age_years*.005)
    estimate = r.area_sqft*r.rate_per_sqft*cf*af
    return {"feature":"valuation","summary":f"Illustrative estimate: {r.currency} {estimate:,.0f}. Base area × rate: {r.currency} {r.area_sqft*r.rate_per_sqft:,.0f}.",
      "findings":[f"Location: {r.location}",f"Type: {r.property_type}; area: {r.area_sqft:,.0f} sq ft.",f"Condition factor: {cf}; age factor: {af:.2f}."],
      "recommendations":["Use recent comparable sales in the same locality.","Check legal title, exact area, amenities, and property condition."],
      "risk_level":"unknown","limitations":["Heuristic estimate, not a validated valuation model or formal appraisal.","Local market and legal factors are excluded."],"demo_mode":True}

@app.post("/api/planning/generate", response_model=InsightResponse)
def planning(r: PlanningRequest):
    ctx=f"Project: {r.project_type}; location: {r.site_location}; area: {r.built_up_area_sqft} sq ft; floors: {r.floors}; duration: {r.target_duration_weeks} weeks; budget: {r.budget}; notes: {r.notes}"
    return insight("planning","Create a high-level construction plan including work packages, dependencies, approvals, quality hold points, safety controls, and procurement risks. Do not invent local code requirements.",ctx)

@app.post("/api/site-assistant", response_model=InsightResponse)
def assistant(r: TextRequest):
    return insight("site-assistant","Answer the construction site question practically. Separate assumptions from facts and flag when a professional or local code is needed.",f"Question: {r.question}\nContext: {r.context}")

@app.post("/api/weather/advisory", response_model=InsightResponse)
def weather(r: WeatherRequest):
    return insight("weather","Give cautious weather-aware construction advice using only supplied conditions. Mention stop-work triggers and checking official forecasts; do not claim live weather access.",f"Location: {r.location}; conditions: {r.conditions}; activity: {r.planned_activity}")

@app.post("/api/knowledge/ask", response_model=InsightResponse)
def knowledge(r: TextRequest):
    return insight("knowledge","Answer the construction knowledge question clearly. Do not fabricate building-code clauses; recommend checking official local codes.",f"Question: {r.question}\nContext: {r.context}")
