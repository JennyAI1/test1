from litmap.services.graph_builder import build_citation_graph, compute_graph_metrics


def test_build_citation_graph_and_metrics():
    papers = [
        {"paperId": "A", "title": "A", "references": [{"paperId": "B"}]},
        {"paperId": "B", "title": "B", "references": []},
    ]
    graph = build_citation_graph(papers)

    assert graph.number_of_nodes() == 2
    assert graph.number_of_edges() == 1
    assert graph.has_edge("A", "B")

    metrics = compute_graph_metrics(graph)
    assert metrics["in_degree"]["B"] == 1
    assert metrics["out_degree"]["A"] == 1
