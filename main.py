from fetch_arxiv import fetch_arxiv


if __name__ == "__main__":

    query = "cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.CV"

    papers = fetch_arxiv(query)
    print(f"Found {len(papers)} papers\n")

    for paper in papers:
        print(f"Title: {paper.title}")
        print(f"Authors: {', '.join([author.name for author in paper.authors])}")
        print(f"Published: {paper.published}")
        print(f"Abstract:  {paper.summary.strip()[:200]}...")
        print(f"URL: {paper.entry_id}\n")