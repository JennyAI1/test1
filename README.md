# LitMap MVP

A first-version literature review mapping tool focused on metadata + abstracts.

## Features

- Seed by keyword or DOI
- Fetch papers from Semantic Scholar and DOI metadata from Crossref fallback
- Expand to 1-hop references/citations for a literature neighborhood
- Build directed citation graph (`A -> B` means A cites B)
- Compute graph metrics (in-degree, out-degree, betweenness)
- Cluster papers by topic (BERTopic when available, keyword fallback otherwise)
- Explore papers and export CSV from Streamlit UI

## Run

```bash
pip install -r requirements.txt
streamlit run litmap/ui/streamlit_app.py
```

Optional Streamlit secrets:

```toml
SEMANTIC_SCHOLAR_API_KEY="..."
CROSSREF_MAILTO="you@example.edu"
```

## Suggested roadmap

1. Add persistence (SQLite/Postgres via SQLAlchemy)
2. Add BibTeX and PNG export
3. Add pyvis/plotly interactive network rendering
4. Add topic evolution by year
5. Add bridge-paper and review-gap heuristics
