# AI Contract Risk Comparator (Multi-Document RAG)

A FastAPI backend that analyzes **Terms & Conditions / contract PDFs** with a
local LLM and returns a structured, per-clause risk assessment. It can also
**compare two contracts** from different providers and tell you which one is
riskier.

The user uploads a PDF, the backend extracts the text with PyMuPDF, splits it
into clauses, and sends each clause to a local Llama model running through
Ollama. The model returns a risk level, a risk score, and an explanation for
every clause — all as structured JSON ready for a frontend to consume.

## Features

- **Per-clause risk analysis** — every clause gets a `risk_level`, a numeric
  `risk_score`, and a short `description` of the risk.
- **Multi-document comparison** — upload two contracts and get an average risk
  score for each plus a verdict on which provider is riskier.
- **Structured JSON output** — all responses are typed via Pydantic models and
  documented automatically in the interactive `/docs` (Swagger UI).
- **Local & private** — analysis runs on a local Ollama model, no contract data
  leaves your machine.

## Tech stack

- **Python 3.11+**
- **FastAPI** + **Uvicorn** — web framework and ASGI server
- **PyMuPDF (fitz)** — PDF text extraction
- **Ollama** + **Llama 3.2 (1B)** — local LLM for clause analysis
- **Pydantic** — request/response models and validation
- **flake8** — style checks

## Project structure

```
ai-contract-risk-comparator/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app and API endpoints
│   ├── models.py                # Pydantic response models
│   └── services/
│       ├── __init__.py
│       ├── pdf_service.py       # PDF text extraction + clause splitting
│       ├── ai_service.py        # Ollama-based clause risk analysis
│       └── analysis_service.py  # orchestration + contract comparison
├── requirements.txt
├── README.md
└── .gitignore
```

## Prerequisites

1. **Python 3.11+**
2. **Ollama** installed and running — https://ollama.com
3. The Llama model pulled locally:

   ```bash
   ollama pull llama3.2:1b
   ```

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/viktoriia-khoroshun/ai-contract-risk-comparator.git
cd ai-contract-risk-comparator

# 2. Create and activate a virtual environment
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Running the app

Make sure Ollama is running, then start the server:

```bash
uvicorn app.main:app --reload
```

The API is now available at `http://127.0.0.1:8000`.
Open the interactive docs at `http://127.0.0.1:8000/docs`.

## API endpoints

| Method | Path                  | Description                                  |
|--------|-----------------------|----------------------------------------------|
| GET    | `/`                   | Health check                                 |
| POST   | `/upload-contract/`   | Analyze one contract PDF (per-clause risk)   |
| POST   | `/compare-contracts/` | Compare two contract PDFs                     |
| GET    | `/test-ollama/`       | Check the connection to the local Ollama model |

### `POST /upload-contract/`

Form field: `file` — a single PDF.

```bash
curl -X POST "http://127.0.0.1:8000/upload-contract/" \
  -F "file=@contract.pdf"
```

Example response (trimmed):

```json
{
  "filename": "contract.pdf",
  "total_clauses": 57,
  "analyzed_clauses": 10,
  "risks": [
    {
      "clause": "The user's personal data may be processed ...",
      "risk_level": "high",
      "risk_score": 8,
      "description": "The clause allows broad processing of personal data, which could lead to privacy risks."
    }
  ]
}
```

### `POST /compare-contracts/`

Form fields: `file_a` and `file_b` — two PDFs.

```bash
curl -X POST "http://127.0.0.1:8000/compare-contracts/" \
  -F "file_a=@provider_a.pdf" \
  -F "file_b=@provider_b.pdf"
```

Example response (trimmed):

```json
{
  "contract_a": { "filename": "provider_a.pdf", "risks": [ ... ] },
  "contract_b": { "filename": "provider_b.pdf", "risks": [ ... ] },
  "avg_score_a": 4.4,
  "avg_score_b": 6.3,
  "riskier_contract": "provider_b.pdf",
  "summary": "provider_b.pdf looks riskier (average risk score 6.3 vs 4.4)."
}
```

## Development

Run style checks before pushing:

```bash
flake8 --max-line-length=100 app/
```

## Notes & limitations

- Uses `llama3.2:1b`, a small local model, so risk assessments are
  demonstration-quality, **not legal advice**. Swap `MODEL` in
  `app/services/ai_service.py` for a larger model (e.g. `llama3.2:3b`) for
  better quality.
- Clauses are split on `.` and short fragments are filtered out — this is a
  simple MVP approach, not a full legal-clause parser.
- Only the first `MAX_CLAUSES` (default 10) clauses are analyzed per document to
  keep response times reasonable with a local model.
