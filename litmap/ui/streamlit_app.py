from __future__ import annotations

import pandas as pd
import streamlit as st

from litmap.services.crossref import CrossrefClient
from litmap.services.graph_builder import build_citation_graph, compute_graph_metrics
from litmap.services.preprocess import clean_text, combine_title_abstract
from litmap.services.semantic_scholar import SemanticScholarClient
from litmap.services.topic_model import fit_topics

st.set_page_config(page_title="LitMap", layout="wide")
st.title("Literature Review Mapping Tool (MVP)")
st.caption("Seed-based discovery, citation graphing, and topic clustering for sociology literature.")

client = SemanticScholarClient(api_key=st.secrets.get("SEMANTIC_SCHOLAR_API_KEY") if hasattr(st, "secrets") else None)
crossref = CrossrefClient(mailto=st.secrets.get("CROSSREF_MAILTO") if hasattr(st, "secrets") else None)

with st.sidebar:
    st.header("Search")
    mode = st.radio("Seed type", ["Keyword", "DOI"])
    query = st.text_input("Keyword query or DOI", "social capital educational attainment")
    max_papers = st.slider("Max seed papers", 10, 100, 50, 10)
    expand = st.checkbox("Expand to citations/references", value=True)
    run = st.button("Build map", type="primary")


def _to_rows(papers):
    rows = []
    for p in papers:
        rows.append(
            {
                "paperId": p.get("paperId"),
                "title": p.get("title"),
                "year": p.get("year"),
                "venue": p.get("venue"),
                "doi": (p.get("externalIds") or {}).get("DOI"),
                "citationCount": p.get("citationCount", 0),
                "authors": ", ".join(a.get("name", "") for a in p.get("authors", [])),
                "abstract": p.get("abstract"),
                "url": p.get("url"),
            }
        )
    return rows


if run:
    with st.spinner("Fetching papers..."):
        if mode == "DOI":
            paper = client.find_by_doi(query)
            if paper is None:
                crossref_meta = crossref.lookup_doi(query)
                st.warning("DOI not found in Semantic Scholar.")
                if crossref_meta:
                    st.json(crossref_meta)
                st.stop()
            seeds = [paper]
        else:
            seeds = client.search_papers(query, limit=max_papers)

        papers = client.expand_neighborhood(seeds) if expand else seeds

    rows = _to_rows(papers)
    if not rows:
        st.info("No papers found.")
        st.stop()

    df = pd.DataFrame(rows).drop_duplicates(subset=["paperId"])
    text_docs = [clean_text(combine_title_abstract(r["title"], r["abstract"])) for _, r in df.iterrows()]
    topics, labels = fit_topics(text_docs)
    df["topic_id"] = topics

    graph = build_citation_graph(papers)
    metrics = compute_graph_metrics(graph)
    df["in_degree"] = df["paperId"].map(metrics["in_degree"]).fillna(0)
    df["betweenness"] = df["paperId"].map(metrics["betweenness"]).fillna(0.0)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Paper explorer")
        st.dataframe(
            df[["title", "year", "authors", "citationCount", "topic_id", "in_degree", "betweenness"]],
            use_container_width=True,
            hide_index=True,
        )
    with col2:
        st.subheader("Topic labels")
        st.dataframe(pd.DataFrame(labels), use_container_width=True, hide_index=True)

    st.subheader("Graph summary")
    st.write(
        {
            "nodes": graph.number_of_nodes(),
            "edges": graph.number_of_edges(),
            "density": round(float(0 if graph.number_of_nodes() <= 1 else graph.number_of_edges() / (graph.number_of_nodes() * (graph.number_of_nodes() - 1))), 4),
        }
    )

    selected = st.selectbox("Select paper", options=df["paperId"].tolist(), format_func=lambda pid: df[df.paperId == pid]["title"].iloc[0])
    paper = next((p for p in papers if p.get("paperId") == selected), None)
    if paper:
        st.markdown(f"### {paper.get('title', 'Untitled')}")
        st.write(
            {
                "year": paper.get("year"),
                "doi": (paper.get("externalIds") or {}).get("DOI"),
                "citationCount": paper.get("citationCount"),
                "referenceCount": paper.get("referenceCount"),
                "url": paper.get("url"),
            }
        )
        st.write(paper.get("abstract") or "No abstract available.")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Export CSV", data=csv, file_name="litmap_papers.csv", mime="text/csv")
else:
    st.info("Use the sidebar to seed a map with a keyword or DOI.")
