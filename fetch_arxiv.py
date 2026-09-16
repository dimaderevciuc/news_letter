import datetime as dt
from re import search
import arxiv

lookback_hours = 48

def fetch_arxiv(query: str):
    search = arxiv.Search(
        query = query,
        max_results = 15,
        sort_by = arxiv.SortCriterion.SubmittedDate
    )

    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=lookback_hours)

    results = []

    for paper in arxiv.Client().results(search):
        if paper.published < cutoff:
            continue
    results.append(paper)

    return results
