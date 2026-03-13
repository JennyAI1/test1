from litmap.services.topic_model import fit_topics


def test_fit_topics_returns_assignments_and_labels():
    docs = [
        "social capital education school attainment",
        "gender family work care",
        "class inequality stratification income",
    ]
    topics, labels = fit_topics(docs)

    assert len(topics) == len(docs)
    assert isinstance(labels, list)
    assert labels
