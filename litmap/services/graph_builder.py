from __future__ import annotations

from typing import Any

try:
    import networkx as nx
except Exception:  # pragma: no cover
    nx = None


class _MiniDiGraph:
    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, Any]] = {}
        self._edges: set[tuple[str, str]] = set()

    def add_node(self, node_id: str, **attrs: Any) -> None:
        self._nodes[node_id] = attrs

    def add_edge(self, source: str, target: str) -> None:
        self._edges.add((source, target))

    def nodes(self):
        return self._nodes.keys()

    def has_edge(self, source: str, target: str) -> bool:
        return (source, target) in self._edges

    def number_of_nodes(self) -> int:
        return len(self._nodes)

    def number_of_edges(self) -> int:
        return len(self._edges)

    def in_degree(self):
        return [(n, sum(1 for _, t in self._edges if t == n)) for n in self._nodes]

    def out_degree(self):
        return [(n, sum(1 for s, _ in self._edges if s == n)) for n in self._nodes]


def _new_graph():
    return nx.DiGraph() if nx else _MiniDiGraph()


def build_citation_graph(papers: list[dict[str, Any]]):
    graph = _new_graph()

    for paper in papers:
        paper_id = paper.get("paperId")
        if not paper_id:
            continue
        graph.add_node(
            paper_id,
            title=paper.get("title"),
            year=paper.get("year"),
            citation_count=paper.get("citationCount", 0),
            url=paper.get("url"),
        )

    node_ids = set(graph.nodes())
    for paper in papers:
        source = paper.get("paperId")
        if not source:
            continue
        for ref in paper.get("references", []):
            target = ref.get("paperId")
            if target and target in node_ids:
                graph.add_edge(source, target)

    return graph


def compute_graph_metrics(graph) -> dict[str, dict[str, float]]:
    if graph.number_of_nodes() == 0:
        return {"in_degree": {}, "out_degree": {}, "betweenness": {}}

    if nx:
        betweenness = nx.betweenness_centrality(graph)
    else:
        betweenness = {node: 0.0 for node in graph.nodes()}

    return {
        "in_degree": dict(graph.in_degree()),
        "out_degree": dict(graph.out_degree()),
        "betweenness": betweenness,
    }
