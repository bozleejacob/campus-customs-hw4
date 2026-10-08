# Campus Customs

A Yale-affiliated apparel shop website with an AI shopping assistant: a React + Vite + TypeScript frontend, a FastAPI backend, and a PydanticAI agent that can search the catalogue, check live stock, and remember logged-in shoppers across visits.

See [`output/harness.md`](output/harness.md) for full documentation: database schema, agent abilities/tools, Pydantic model fields and why they were chosen, safety rules, and specifications (model, loop limits, result caps).

Other docs in [`output/`](output/): [`design.md`](output/design.md) (styling), [`usability.md`](output/usability.md) (usability improvements), [`app_check.html`](output/app_check.html) (live site test report), [`audit_trail.json`](output/audit_trail.json) (agent run log).

The full prompt history for this project is in [`AI_prompts.md`](AI_prompts.md).

## Local data pack

This repo does **not** include the product database or images. Before running the backend, place the data pack at `data/` in the repo root:

```
data/
├── campus_customs.db
└── products/        # product images referenced by the catalogue
```

## Setup

1. Copy `.env.example` to `.env` and fill in your real `PORTKEY_API_KEY`.
2. Install and run the backend:

   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r ../requirements.txt
   uvicorn main:app --reload --port 8000
   ```

3. In a separate terminal, install and run the frontend:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

4. Open `http://localhost:5173`. The frontend expects the backend at `http://localhost:8000`.

## Project layout

```
hw4/
├── AI_prompts.md
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── frontend/              # Vite React TypeScript app
├── backend/
│   ├── main.py            # FastAPI app — run with: uvicorn main:app --reload
│   ├── agent.py
│   ├── models.py
│   ├── tools.py
│   └── prompts/
│       └── prompt.md
└── output/
    ├── harness.md
    ├── design.md
    ├── usability.md
    ├── app_check.html
    ├── app_check_images/
    └── audit_trail.json
```
