import pytest
from forward_context.utils.clean_html_text import paragraphs_with_refdict, clean_unicode


@pytest.mark.parametrize("input_html, expected_phrase", [
    (
        "<h2>Heading</h2><p>This is a paragraph with a <a href='/statistics/1234/interesting-data/'>link</a>.</p>",
        "Heading: This is a paragraph with a link."
    ),
    (
        "<p>Plain paragraph with &nbsp; whitespace.</p>",
        "Plain paragraph with whitespace."
    ),
    (
        "<h3>Title</h3><p></p>",  # empty paragraph
        "Title"
    )
])
def test_paragraphs_with_refdict_returns_cleaned_text(input_html, expected_phrase):
    results = paragraphs_with_refdict(input_html)
    assert results, "No results returned"
    cleaned_texts = [r[0] for r in results]  # extract cleaned text
    assert any(expected_phrase in text for text in cleaned_texts)


def test_paragraph_refs_extracted():
    html = """
        <h2>Topic</h2>
        <p>Reference to <a href="/statistics/263265/top-companies/">this stat</a>
        and <a href="/topics/2075/spotify/">Spotify</a>.</p>
    """
    results = paragraphs_with_refdict(html)
    assert results
    _, refs, _ = results[0]

    # Should group refs by root paths
    assert "statistics" in refs
    assert "topics" in refs
    assert 263265 in refs["statistics"]
    assert 2075 in refs["topics"]


def test_clean_unicode_removes_nbsp_and_trims():
    raw = "Example\u00a0text   with  spaces"
    expected = "Example text with spaces"
    assert clean_unicode(raw) == expected
