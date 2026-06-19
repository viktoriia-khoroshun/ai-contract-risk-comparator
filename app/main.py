from fastapi import FastAPI, File, HTTPException, UploadFile

from app.models import ContractAnalysisResponse, ContractComparison
from app.services.ai_service import ping_model
from app.services.analysis_service import analyze_contract, compare_contracts

app = FastAPI(title="AI Contract Risk Comparator")


async def _read_pdf_content(file: UploadFile) -> bytes:
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    return await file.read()


def _run_analysis(filename: str, content: bytes) -> ContractAnalysisResponse:
    try:
        return analyze_contract(filename, content)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"Could not process the PDF: {filename}",
        )


@app.get("/")
def root():
    return {"message": "AI Contract Risk Comparator API"}


@app.post("/upload-contract/", response_model=ContractAnalysisResponse)
async def upload_contract(file: UploadFile = File(...)):
    content = await _read_pdf_content(file)
    return _run_analysis(file.filename, content)


@app.post("/compare-contracts/", response_model=ContractComparison)
async def compare_contracts_endpoint(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
):
    content_a = await _read_pdf_content(file_a)
    content_b = await _read_pdf_content(file_b)

    analysis_a = _run_analysis(file_a.filename, content_a)
    analysis_b = _run_analysis(file_b.filename, content_b)

    return compare_contracts(analysis_a, analysis_b)


@app.get("/test-ollama/")
def test_ollama():
    return {"response": ping_model()}
