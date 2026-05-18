import json

import fitz
import ollama
from fastapi import FastAPI, File, UploadFile

app = FastAPI()


@app.get("/")
def root():
    return {"message": "AI Contract Risk Comparator API"}


def extract_text_from_pdf(content: bytes) -> str:
    pdf = fitz.open(stream=content, filetype="pdf")

    text = ""

    for page in pdf:
        text += page.get_text()

    return text


def split_text_into_clauses(text: str) -> list[str]:
    clean_text = text.replace("\n", " ")
    clauses = clean_text.split(".")

    return [clause.strip() for clause in clauses if clause.strip()]


def analyze_clause_with_ollama(clause: str) -> dict:
    prompt = f"""
You are a contract risk analysis API.

Analyze the contract clause.

IMPORTANT RULES:
- Return ONLY pure JSON
- Do NOT use markdown
- Do NOT write explanations outside JSON
- Do NOT use ```json
- Do NOT add extra text

Return this exact JSON format:

{{
    "risk_level": "low",
    "risk_score": 1,
    "description": "Explain the specific risk in 1-2 sentences"
}}

The description must clearly explain:
- what the risk is
- why it may affect the user

Clause:
{clause}
"""

    response = ollama.chat(
        model="llama3.2:1b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    content = response["message"]["content"]
    content = content.replace("```json", "")
    content = content.replace("```", "")
    content = content.strip()

    try:
        parsed_response = json.loads(content)
    except json.JSONDecodeError:
        parsed_response = {
            "risk_level": "unknown",
            "risk_score": 0,
            "description": content,
        }

    return {
        "clause": clause,
        "risk_level": parsed_response.get("risk_level", "unknown"),
        "risk_score": parsed_response.get("risk_score", 0),
        "description": str(parsed_response.get("description", "")).replace("{", "").replace("}", "").replace('"', ""),
    }


@app.post("/upload-contract/")
async def upload_contract(file: UploadFile = File(...)):
    content = await file.read()

    text = extract_text_from_pdf(content)
    clauses = split_text_into_clauses(text)

    analyzed_risks = []

    for clause in clauses[:10]:
        analyzed_clause = analyze_clause_with_ollama(clause)
        analyzed_risks.append(analyzed_clause)

    return {
        "filename": file.filename,
        "total_clauses": len(clauses),
        "analyzed_clauses": len(analyzed_risks),
        "risks": analyzed_risks,
    }


@app.get("/test-ollama/")
def test_ollama():
    response = ollama.chat(
        model="llama3.2:1b",
        messages=[
            {
                "role": "user",
                "content": "Say hello in one short sentence.",
            }
        ],
    )

    return {
        "response": response["message"]["content"],
    }
