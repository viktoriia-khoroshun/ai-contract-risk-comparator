from fastapi import FastAPI, File, HTTPException, UploadFile

from app.models import ContractAnalysisResponse
from app.services.ai_service import analyze_clause, ping_model
from app.services.pdf_service import (
    extract_text_from_pdf,
    split_text_into_clauses,
)

app = FastAPI(title="AI Contract Risk Comparator")

# MVP limit: analyze only the first N clauses to keep response time sane
# with a local model. Raise/remove once moved to a bigger model or batching.
MAX_CLAUSES = 10


@app.get("/")
def root():
    return {"message": "AI Contract Risk Comparator API"}


@app.post("/upload-contract/", response_model=ContractAnalysisResponse)
async def upload_contract(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()

    try:
        text = extract_text_from_pdf(content)
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read the PDF file.")

    clauses = split_text_into_clauses(text)
    risks = [analyze_clause(clause) for clause in clauses[:MAX_CLAUSES]]

    return ContractAnalysisResponse(
        filename=file.filename,
        total_clauses=len(clauses),
        analyzed_clauses=len(risks),
        risks=risks,
    )


@app.get("/test-ollama/")
def test_ollama():
    return {"response": ping_model()}
