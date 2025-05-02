import re
from collections import Counter, defaultdict
from urllib.parse import urlparse, unquote
from typing import List, Dict
from forward_context.lib.load_data import load_data
from forward_context.config.config import RAW_DATA_FILE
import pandas as pd

HREF_RE = re.compile(r'href\s*=\s*[\'"]([^\'"]+)[\'"]', re.I)


def inspect_href_roots(records: List[Dict], *, max_examples: int = 3):
    """
    Return the distinct first-path segments that occur in <a href="…">
    links inside each record['description'] as a data frame.
    """
    root_counts = Counter()
    examples = defaultdict(list)

    for rec in records:
        html = rec.get("description", "") or ""
        for raw_href in HREF_RE.findall(html):
            # decode  \/  → /   and %xx escapes
            href = unquote(raw_href.replace(r"\/", "/"))
            path = urlparse(href).path.lstrip("/")
            if not path:
                continue

            root = path.split("/", 1)[0]  # e.g. "statistics", "topics"
            root_counts[root] += 1
            if len(examples[root]) < max_examples:
                examples[root].append(href)

    df = (
        pd.DataFrame(
            {
                "root": list(root_counts.keys()),
                "count": [root_counts[k] for k in root_counts],
                "samples": [examples[k] for k in root_counts],
            }
        )
        .sort_values("count", ascending=False)
        .reset_index(drop=True)
    )
    return df


if __name__ == "__main__":
    data_list = load_data(RAW_DATA_FILE)

    df_roots = inspect_href_roots(data_list)
    df_roots.to_csv("./data/href_roots.csv", index=False)
