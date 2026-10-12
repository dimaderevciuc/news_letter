import datetime as dt

import arxiv

from config import ARXIV_MAX_RESULTS, LOOKBACK_HOURS


def fetch_arxiv(query: str):
    search = arxiv.Search(
        query = query,
        max_results = ARXIV_MAX_RESULTS,
        sort_by = arxiv.SortCriterion.SubmittedDate
    )

    # arXiv announces in daily batches (none on weekends), so the window is anchored
    # to the newest paper instead of "now". history.py stops batches repeating.
    cutoff = None

    results = []

    for paper in arxiv.Client(page_size=200).results(search):
        if cutoff is None:
            cutoff = paper.published - dt.timedelta(hours=LOOKBACK_HOURS)
        if paper.published < cutoff:
            break  # results are sorted newest-first, so everything after is older
        results.append(paper)

    return results
