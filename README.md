# CliniScan v2

CliniScan is a rule-augmented multimodal triage assistant that fuses structured symptom intake and visual evidence.

## What It Is
- A layered triage prioritization workflow with deterministic risk fusion.
- Explainable pipeline output for demo and educational use.

## What It Is Not
- Not a diagnosis tool.
- Not a replacement for licensed medical consultation.
- Not a clinically validated medical device.

Every result includes: `Not a diagnosis. Always consult a licensed medical professional.`

## Architecture
- `backend/`
  - FastAPI orchestration (`/analyze`, `/health`)
  - Layered modules:
    - Layer 0: Safety override
    - Layer 1A: Vision extractor (LLM)
    - Layer 1B: Symptom structurer (LLM)
    - Layer 2: Evidence fusion (deterministic)
    - Layer 3: Quality gate (deterministic)
    - Layer 4: Clinical reasoning (LLM)
  - Demo cache scenarios in `backend/cache/`
- `frontend/`
  - React + Vite SPA with 3-view state machine:
    - Input
    - Processing pipeline
    - Results

## API Contract
`POST /analyze` expects JSON:
- `symptom_text`, `body_location`, `duration_days`, `severity_score`
- optional: `age`, `known_conditions`, `medications`
- optional image: `image_base64`, `image_mime`
- optional demo: `demo_scenario` (`1|2|3`)
- `provider`: `anthropic` or `openai`

Returns:
- `pipeline_stages`, `diagnosis`, `urgency`, `conflict`, `risk_signals`, `quality`, `no_image_mode`, `demo_mode`

## Local Setup
### Backend
```bash
cd backend
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend default URL: `http://localhost:3000`
Backend default URL: `http://localhost:8000`
