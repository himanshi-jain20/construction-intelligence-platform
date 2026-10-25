import base64, json, os
from typing import Any
from openai import OpenAI

KEY = os.getenv("OPENAI_API_KEY", "").strip()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=KEY) if KEY else None

def strings(value: Any) -> list[str]:
    return [str(x) for x in value[:20]] if isinstance(value, list) else []

def demo(feature: str) -> dict:
    content = {
      "safety": ("Demo only: no trained site-safety detector was run.",
        ["Image review may miss PPE issues, edge hazards, poor housekeeping, or equipment conflicts."],
        ["Pause work if immediate danger is suspected.", "Ask the site safety officer to inspect using the approved checklist."]),
      "cracks": ("Demo only: crack depth and structural significance cannot be determined here.",
        ["Record crack width, length, location, and whether it changes over time."],
        ["Get a qualified structural engineer to inspect concerning or widening cracks."]),
      "valuation": ("Indicative arithmetic estimate only; this is not a market appraisal.",
        ["Actual value depends on comparable sales, title, amenities, exact area, and local market."],
        ["Compare recent local transactions and consult a qualified valuer."]),
      "planning": ("Illustrative planning brief only; validate scope, dependencies, permits, and procurement.",
        ["Confirm drawings, ground conditions, approvals, contractor capacity, and lead times."],
        ["Review critical path, quality hold points, and site safety with the project manager."]),
      "weather": ("Advisory based only on weather conditions entered by the user; no live forecast was retrieved.",
        ["Forecasts change. Check an official local weather service before work."],
        ["Follow site-specific lifting, concrete, lightning, and heat-stress procedures."]),
    }
    summary, findings, recommendations = content.get(feature, (
      "Demo response: configure OPENAI_API_KEY for model-backed assistance.",
      ["No construction knowledge base was queried."],
      ["Verify against approved drawings, applicable codes, and qualified professional advice."]))
    return {"feature":feature,"summary":summary,"findings":findings,"recommendations":recommendations,
            "risk_level":"unknown","limitations":["DEMO MODE: model API key is not configured.",
            "Not for emergency decisions, code compliance, or engineering certification."],"demo_mode":True}

def insight(feature: str, task: str, context: str = "", image_bytes: bytes | None = None, mime: str = "image/jpeg") -> dict:
    if client is None:
        return demo(feature)
    system = ("You are a cautious construction decision-support assistant. Return ONLY valid JSON with keys "
      "summary (string), findings (array), recommendations (array), risk_level (low|medium|high|unknown), "
      "limitations (array). Do not certify structural safety or code compliance. State uncertainty and advise "
      "qualified on-site review for safety-critical matters.")
    content = [{"type":"text","text":f"Task: {task}\nContext: {context}"}]
    if image_bytes:
        encoded = base64.b64encode(image_bytes).decode("ascii")
        content.append({"type":"image_url","image_url":{"url":f"data:{mime};base64,{encoded}"}})
    response = client.chat.completions.create(model=MODEL, temperature=0.2,
      response_format={"type":"json_object"},
      messages=[{"role":"system","content":system},{"role":"user","content":content}])
    raw = response.choices[0].message.content or "{}"
    data = json.loads(raw)
    risk = data.get("risk_level","unknown")
    if risk not in {"low","medium","high","unknown"}: risk = "unknown"
    return {"feature":feature,"summary":str(data.get("summary","No summary provided.")),
      "findings":strings(data.get("findings")),"recommendations":strings(data.get("recommendations")),
      "risk_level":risk,"limitations":strings(data.get("limitations")) or
      ["AI output may be incomplete; verify with a qualified professional."],"demo_mode":False}
