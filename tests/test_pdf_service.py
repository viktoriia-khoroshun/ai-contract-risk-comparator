from app.services.pdf_service import MIN_CLAUSE_WORDS, split_text_into_clauses


def test_split_basic_sentences():
    text = "This is the first clause here. This is the second clause indeed."
    result = split_text_into_clauses(text)
    assert result == [
        "This is the first clause here",
        "This is the second clause indeed",
    ]


def test_split_filters_short_fragments():
    text = "02. 2023. This clause is long enough to be kept here."
    result = split_text_into_clauses(text)
    assert result == ["This clause is long enough to be kept here"]


def test_split_strips_whitespace():
    text = "   A clause with enough words to keep around   .   "
    result = split_text_into_clauses(text)
    assert result == ["A clause with enough words to keep around"]


def test_newlines_are_replaced_with_spaces():
    text = "alpha beta gamma\ndelta epsilon zeta."
    result = split_text_into_clauses(text)
    assert result == ["alpha beta gamma delta epsilon zeta"]


def test_split_empty_text_returns_empty_list():
    assert split_text_into_clauses("") == []


def test_min_clause_words_is_respected():
    short = " ".join(["word"] * (MIN_CLAUSE_WORDS - 1)) + "."
    assert split_text_into_clauses(short) == []
