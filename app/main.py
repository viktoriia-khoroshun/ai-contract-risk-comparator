from fastapi import FastAPI, UploadFile, File
import fitz

app = FastAPI()


@app.get("/")
def root():
    return {"message": "AI Contract Risk Comparator API"}


@app.post("/upload-contract/")
async def upload_contract(file: UploadFile = File(...)):
    content = await file.read()

    pdf = fitz.open(stream=content, filetype="pdf")

    text = ""

    for page in pdf:
        text += page.get_text()

    return {
        "filename": file.filename,
        "text_preview": text[:1000]
    }
