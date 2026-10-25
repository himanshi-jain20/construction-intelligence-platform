# SiteSense AI — Construction Intelligence Platform

Full-stack MVP: React/Vite frontend + FastAPI backend. Includes site safety image review, crack analysis, indicative property valuation, project planning, daily site assistant, weather advisory, and construction knowledge Q&A.

## Run it
### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Copy .env.example to .env; optionally set OPENAI_API_KEY
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

### Frontend (new terminal)
```bash
cd frontend
npm install
npm run dev
```
Open the localhost URL printed by Vite. Optional model integration uses `OPENAI_API_KEY` and `OPENAI_MODEL` in `backend/.env`. Without a key, clearly labelled demo responses are returned.

## Important
This is an educational decision-support MVP, not an engineering certification tool. Verify safety, crack, weather, and planning results with qualified professionals and official sources. The weather feature uses conditions entered by the user; it does not fetch live forecasts.
