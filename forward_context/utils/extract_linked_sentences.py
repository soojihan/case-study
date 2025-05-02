# This script was generated using GPT-o3 and refined manually
from bs4 import BeautifulSoup
import re

STAT_ID_RE = re.compile(r"/statistics/(\d+)/")
SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def enrich_with_linked_sentences(records, text_field):
    """
    Extract anchor phrases and their surrounding sentences from HTML-formatted text fields.
    """
    for rec in records:
        rec.setdefault("linked_sentences", [])

    for src in records:
        soup = BeautifulSoup(src.get(text_field, ""), "html.parser")

        for a in soup.find_all("a", href=True):
            m = STAT_ID_RE.search(a["href"])
            if not m:
                continue

            anchor_text = a.get_text(" ", strip=True)
            parent_text = a.parent.get_text(" ", strip=True)

            for sent in SENT_SPLIT_RE.split(parent_text):
                if anchor_text in sent:
                    payload = {
                        "anchor_sentence": " ".join(sent.split()),
                        "anchor": anchor_text,
                        "target_id": int(m.group(1)),  # keep ID even if doc missing
                    }
                    if payload not in src["linked_sentences"]:
                        src["linked_sentences"].append(payload)
                    break
    return records
