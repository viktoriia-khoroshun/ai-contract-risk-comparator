import fitz


def extract_text_from_pdf(content: bytes) -> str:
    with fitz.open(stream=content, filetype="pdf") as pdf:
        return "".join(page.get_text() for page in pdf)


def split_text_into_clauses(text: str) -> list[str]:
    clean_text = text.replace("\n", " ")
    clauses = clean_text.split(".")
    # MVP limitation: naive split on ".", drops empty/whitespace clauses.
    return [clause.strip() for clause in clauses if clause.strip()]
