# This script was generated using GPT-o3 and refined manually
import re
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup  # pip install beautifulsoup4
from forward_context.utils.configure_logger import configure_logging

logging = configure_logging()

HREF_RE = re.compile(r'href\s*=\s*[\'"]([^\'"]+)[\'"]', re.I)  # pulls any href="…"


def clean_unicode(txt):
    """Squash whitespace and remove non-breaking spaces."""
    cleaned = " ".join(txt.replace("\u00a0", " ").split())
    # Remove space before common punctuation
    cleaned = re.sub(r"\s+([.,!?;:])", r"\1", cleaned)
    return cleaned.strip()


def extract_refs(tag):
    """
    Collect references in *tag*, grouped by first path segment.
    IDs are unique within each bucket, order preserved.
    """
    refs = {}
    for a in tag.find_all("a", href=True):
        href_raw = a["href"]
        href = unquote(href_raw.replace(r"\/", "/"))
        path = urlparse(href).path.lstrip("/")
        if not path:
            continue  # e.g. "mailto:", "#top"

        root, *rest = path.split("/", 1)
        root = root.lower()

        # Decide what we consider the “ID” (int if digits, otherwise slug)
        if rest:
            first_piece = rest[0].split("/", 1)[0]
            id_part = int(first_piece) if first_piece.isdigit() else first_piece
        else:
            id_part = root

        # De-duplicate *within this bucket list* only
        bucket = refs.setdefault(root, [])
        if id_part not in bucket:
            bucket.append(id_part)

    return refs


def merge_refs(target, source) -> None:
    """
    Merge *source* into *target* in-place, preserving order but
    without extra sets.
    """
    for root, vals in source.items():
        bucket = target.setdefault(root, [])
        for v in vals:
            if v not in bucket:  # de-dup per bucket
                bucket.append(v)


def paragraphs_with_refdict(html):
    """
    Returns a list with tuples:
        (cleaned_text, refs_dict, raw_html)
    """
    soup = BeautifulSoup(html, "html.parser")
    results = []

    # markup with headings + <p>
    if soup.find(["p", "h1", "h2", "h3", "h4", "h5", "h6"]):
        head_txt_buf = []
        head_html_buf = []
        head_refs_buf = {}

        for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p"]):
            # ---------- heading ----------
            if tag.name.startswith("h"):
                head_txt_buf.append(clean_unicode(tag.get_text(" ", strip=True)))
                head_html_buf.append(str(tag))  # keep <h*> tag
                merge_refs(head_refs_buf, extract_refs(tag))
                continue

            # ---------- paragraph ----------
            body_txt = clean_unicode(tag.get_text(" ", strip=True))
            if not body_txt:
                continue
            body_html = str(tag)  # full <p>…</p>

            para_refs = {}
            merge_refs(para_refs, head_refs_buf)  # refs from headings
            merge_refs(para_refs, extract_refs(tag))  # refs from this <p>

            if head_txt_buf:
                prefix_txt = " ".join(head_txt_buf)
                prefix_html = "".join(head_html_buf)
                body_txt = f"{prefix_txt}: {body_txt}"
                body_html = f"{prefix_html}{body_html}"
                head_txt_buf.clear()
                head_html_buf.clear()
                head_refs_buf.clear()

            results.append((body_txt, para_refs, body_html))

        # dangling headings at the very end
        if head_txt_buf:
            results.append(
                (" ".join(head_txt_buf), head_refs_buf, "".join(head_html_buf))
            )

    # plain‑text fallback
    else:
        raw_html = soup.get_text(" ", strip=False)
        cleaned = clean_unicode(raw_html)
        if cleaned:
            results.append((cleaned, extract_refs(soup), raw_html))

    return results


def log_paragraphs(snippet: str, label: str):
    for idx, (cleaned, refs, raw) in enumerate(paragraphs_with_refdict(snippet), 1):
        logging.info(
            "%s – paragraph %d\nCLEANED:\n%s\nRAW:\n%s\nREFERENCES: %s\n",
            label,
            idx,
            cleaned,
            raw,
            refs,
        )


def test_clean_html():
    # Test
    text1 = """<p>The NYSE U.S. 100 Index tracks the largest U.S. companies traded on the New York Stock Exchange. 
    This statistic shows the leading 20 companies on the NYSE U.S. 100 Index by market capitalization. As of January 28, 2024 the multinational conglomerate company Berkshire Hathaway ranked as the first, with a market capitalization of over 900 billion euros. This was followed by Eli Lilly and JP Morgan Chase, with market capitalizations amounting to 695 billion and 678 billion euros respectively.\u00a0  </p>\n<h2>NYSE U.S. 100 Index vs. Nasdaq 100 Index</h2>\n<p>The New York Stock Exchange and the Nasdaq are<a href=\"/statistics/270126/largest-stock-exchange-operators-by-market-capitalization-of-listed-companies/\" target=\"_blank\" rel=\"noopener\"> the largest two stock exchanges in the world</a>, but they differ in the kinds of companies they list. The NYSE is known to list stable and long-lasting firms, commonly referred to as \u201cblue-chip\u201d companies. In contrast, the Nasdaq is renowned for listing <a href=\"/statistics/263264/top-companies-in-the-world-by-market-capitalization/\" target=\"_blank\" rel=\"noopener\">the world\u2019s biggest companies</a>, mainly from the tech industry. Similar to the NYSE U.S. 100 Index, <a href=\"/statistics/261720/annual-development-of-the-sunds-500-index/\" target=\"_blank\" rel=\"noopener\">the Nasdaq 100 Index</a> tracks the 100 largest non-financial companies listed on the Nasdaq exchange, including both U.S. and non-U.S. companies.   </p>\n<h2>The leader of the NYSE U.S. 100 index: Berkshire Hathaway</h2>\n<p>Berkshire Hathaway, the leader of the NYSE U.S. 100 Index, was also among <a href=\"/statistics/263265/top-companies-in-the-world-by-revenue/\" target=\"_blank\" rel=\"noopener\">the world's largest companies by revenue</a> in 2023. The company is a multinational conglomerate and holding company with insurance as its core business and interests in other sectors such as railroad, utilities and energy, finance. In fact, Berkshire was <a href=\"/statistics/185746/revenue-of-the-leading-global-insurance-companies/\" target=\"_blank\" rel=\"noopener\">the world's biggest insurance company</a> by revenue in 2023. As a holding company, it has significant stakes in some of the world\u2019s largest companies, including Apple, Bank of America and Coca-Cola. With its diverse background in various businesses and industries, Berkshire Hathaway had a<a href=\"/statistics/209570/total-revenue-of-berkshire-hathaway/\" target=\"_blank\" rel=\"noopener\"> total revenue of 365 billion U.S. dollars</a> in 2023.</p>"""

    text2 = '<p>In 2023/24, FC Barcelona generated around 760 million euros in revenue. Overall, the club ranked sixth worldwide in terms of total revenue.\u00a0  </p>\n<h2>Which are the main sources of revenue for FC Barcelona?</h2>\n<p>Bar\u00e7a \u2013 as the club is commonly known \u2013 generated most of its <a href="/statistics/800061/revenue-of-fc-barcelona-united-by-stream/" target="_blank" rel="noopener">revenue from commercial sales</a> during the 2023/24 season. The major sponsors of Barcelona are the American sports brand Nike, the Japanese e-commerce company Rakuten, and the music streaming giant <a href="/topics/2075/spotify/" target="_blank" rel="noopener">Spotify</a> since 2022.\u00a0</p>\n<h2>FC Barcelona is not only about soccer</h2>\n<p>Barcelona is known around the world mostly for its soccer teams. However, the Spanish giant is also engaged in several sports: handball, basketball, and roller hockey. In 2021/22, there were 671\u00a0<a href="/statistics/1273846/fc-barcelona-youth-academy-athletes-sport-types/" target="_blank" rel="noopener">athletes across all sports in Barcelona\u2019s youth academy</a>.</p>'

    log_paragraphs(text1, "Text1")
    log_paragraphs(text2, "Text2")


if __name__ == "__main__":
    test_clean_html()
