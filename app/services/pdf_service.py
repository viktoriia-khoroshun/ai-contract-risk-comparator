import fitz

# Skip fragments like "02", "2023", "ggf." that come from the naive "." split.
MIN_CLAUSE_WORDS = 6


def extract_text_from_pdf(content: bytes) -> str:
    with fitz.open(stream=content, filetype="pdf") as pdf:
        return "".join(page.get_text() for page in pdf)


def split_text_into_clauses(text: str) -> list[str]:
    clean_text = text.replace("\n", " ")
    parts = (part.strip() for part in clean_text.split("."))
    return [part for part in parts if len(part.split()) >= MIN_CLAUSE_WORDS]
