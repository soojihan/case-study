from forward_context.config.config import SPLIT_PARAGRAPH_FILE
from forward_context.lib.load_data import load_data
from statistics import mean, median
from forward_context.utils.configure_logger import configure_logging


logging = configure_logging()

data_list = load_data(SPLIT_PARAGRAPH_FILE)


def check_chunk_lengths(text_field):
    """
    Calculate and log basic statistics (median, mean, max, min) of the lengths of texts
    from a specified field in the loaded data.
    """
    all_paragraphs = []
    for data_dict in data_list:
        all_paragraphs.append(data_dict[text_field])
    all_paragraphs_lens = [len(text) for text in all_paragraphs]
    logging.info(
        "Paragraph lengths - Median: %s, Mean: %s, Max: %s, Min: %s",
        median(all_paragraphs_lens),
        round(mean(all_paragraphs_lens)),
        max(all_paragraphs_lens),
        min(all_paragraphs_lens),
    )


if __name__ == "__main__":
    check_chunk_lengths("paragraph_clean_text")
