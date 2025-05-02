import json
from forward_context.utils.clean_html_text import paragraphs_with_refdict
from forward_context.lib.load_data import load_data
from forward_context.config.config import RAW_DATA_FILE
import uuid
from tqdm import tqdm
from forward_context.utils.configure_logger import configure_logging
from forward_context.utils.extract_linked_sentences import enrich_with_linked_sentences

logging = configure_logging()


def process_data():
    """
    Parse and clean descriptions, extract references, split into paragraphs,
    enrich with linked sentences, and save both merged and split data to files.
    """
    data_list = load_data(RAW_DATA_FILE)
    separate_paragraph_data = []
    merged_paragraph_data = []
    for i, data in tqdm(enumerate(data_list), total=len(data_list)):
        description = data.get("description")
        all_paras = []
        all_refs = {}
        for cleaned_paragraph_text, refs, raw_paragraph_text in paragraphs_with_refdict(
            description
        ):
            all_paras.append(cleaned_paragraph_text)
            all_refs.update(refs)
            paragraph_uuid = str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f"{data.get('id')}_{cleaned_paragraph_text[:100]}",
                )
            )
            paragraph_dict = {
                "paragraph_id": paragraph_uuid,
                "paragraph_clean_text": cleaned_paragraph_text,
                "paragraph_raw_text": raw_paragraph_text,
            }
            separate_para_dict = data | paragraph_dict
            del separate_para_dict["description"]
            separate_paragraph_data.append(separate_para_dict)
        merged_paragraph = " ".join(all_paras)
        merged_para_dict = data.copy()
        merged_para_dict["cleaned_description"] = merged_paragraph
        merged_para_dict["references"] = all_refs
        merged_paragraph_data.append(merged_para_dict)
    enriched_separate_paragraph_data = enrich_with_linked_sentences(
        separate_paragraph_data, "paragraph_raw_text"
    )
    enriched_merged_paragraph_data = enrich_with_linked_sentences(
        merged_paragraph_data, "description"
    )
    with open("../data/statistics_cleaned_description.json", "w") as f:
        json.dump(enriched_merged_paragraph_data, f, indent=4)
    with open("../data/statistics_split_paragraphs.json", "w") as f:
        json.dump(enriched_separate_paragraph_data, f, indent=4)
    logging.info(
        f"{len(enriched_merged_paragraph_data)} descriptions were cleaned. {len(enriched_separate_paragraph_data)} paragraphs extracted."
    )


if __name__ == "__main__":
    process_data()
