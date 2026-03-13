from litmap.services.preprocess import clean_text, combine_title_abstract


def test_combine_title_abstract():
    assert combine_title_abstract("Title", "Abstract") == "Title Abstract"


def test_clean_text_non_empty():
    cleaned = clean_text("This is a test for social capital in education.")
    assert isinstance(cleaned, str)
    assert "social" in cleaned
