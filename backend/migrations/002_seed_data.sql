INSERT INTO users (email, hashed_password)
VALUES ('demo@research.local', '$2b$12$QmO8PfnzL1jXgX72H6y4Jej2U3fHn4mY17CxX8l2oHB94kUqfQ1dq')
ON CONFLICT (email) DO NOTHING;

INSERT INTO topics (name, description)
VALUES
  ('Retrieval-Augmented Generation', 'Techniques for grounding LLM outputs in external corpora.'),
  ('Experiment Design', 'Methods to design and evaluate repeatable ML experiments.')
ON CONFLICT (name) DO NOTHING;

WITH demo_user AS (
  SELECT id FROM users WHERE email='demo@research.local' LIMIT 1
)
INSERT INTO sources (user_id, title, source_url, source_type, publication_year)
SELECT demo_user.id, 'Attention Is All You Need', 'https://arxiv.org/abs/1706.03762', 'paper', 2017 FROM demo_user
UNION ALL
SELECT demo_user.id, 'RAG Survey', 'https://arxiv.org/abs/2312.10997', 'paper', 2023 FROM demo_user
ON CONFLICT DO NOTHING;

WITH demo_user AS (
  SELECT id FROM users WHERE email='demo@research.local' LIMIT 1
), rag_source AS (
  SELECT id FROM sources WHERE title='RAG Survey' LIMIT 1
)
INSERT INTO literature_reviews (user_id, source_id, title, summary, status, tags)
SELECT demo_user.id, rag_source.id,
       'RAG evaluation patterns',
       'Compares retrieval quality metrics and answer faithfulness checks.',
       'reviewed',
       'rag,evaluation,faithfulness'
FROM demo_user, rag_source
ON CONFLICT DO NOTHING;

INSERT INTO review_citations (review_id, citation_text, citation_url)
SELECT lr.id,
       'Lewis et al. 2020 introduced retrieval-augmented generation for knowledge-intensive NLP tasks.',
       'https://arxiv.org/abs/2005.11401'
FROM literature_reviews lr
WHERE lr.title='RAG evaluation patterns'
ON CONFLICT DO NOTHING;

WITH demo_user AS (
  SELECT id FROM users WHERE email='demo@research.local' LIMIT 1
), rag_topic AS (
  SELECT id FROM topics WHERE name='Retrieval-Augmented Generation' LIMIT 1
), rag_source AS (
  SELECT id FROM sources WHERE title='RAG Survey' LIMIT 1
)
INSERT INTO notes (user_id, topic_id, source_id, review_id, title, body, tags)
SELECT demo_user.id, rag_topic.id, rag_source.id, review_row.id,
       'Open questions on retrieval chunking',
       'Need experiments on chunk overlap vs. hallucination rates.',
       'notes,rag,chunking'
FROM demo_user, rag_topic, rag_source, (SELECT id FROM literature_reviews WHERE title='RAG evaluation patterns' LIMIT 1) review_row
ON CONFLICT DO NOTHING;

WITH demo_user AS (
  SELECT id FROM users WHERE email='demo@research.local' LIMIT 1
)
INSERT INTO embedded_apps (user_id, title, url, category, panel_order, is_active, usage_metadata)
SELECT demo_user.id, 'ArXiv', 'https://arxiv.org', 'literature', 0, TRUE, '{"trackable": true, "defaultMinutes": 20}' FROM demo_user
UNION ALL
SELECT demo_user.id, 'Observable', 'https://observablehq.com', 'analysis', 1, TRUE, '{"trackable": true, "defaultMinutes": 30}' FROM demo_user
ON CONFLICT DO NOTHING;

WITH demo_user AS (
  SELECT id FROM users WHERE email='demo@research.local' LIMIT 1
), app_row AS (
  SELECT id FROM embedded_apps WHERE title='ArXiv' LIMIT 1
)
INSERT INTO embedded_app_usage (app_id, user_id, minutes_spent, usage_metadata)
SELECT app_row.id, demo_user.id, 35, '{"session": "seed", "activity": "paper-triage"}'
FROM demo_user, app_row
ON CONFLICT DO NOTHING;

WITH demo_user AS (
  SELECT id FROM users WHERE email='demo@research.local' LIMIT 1
)
INSERT INTO project_ideas (user_id, title, rationale, generation_model, confidence_score)
SELECT demo_user.id,
       'Benchmark retrieval chunking strategies',
       'Notes and review indicate uncertainty about chunk overlap and retrieval precision.',
       'gpt-4.1-mini',
       0.78
FROM demo_user
ON CONFLICT DO NOTHING;

WITH idea AS (
  SELECT id FROM project_ideas WHERE title='Benchmark retrieval chunking strategies' LIMIT 1
), note_row AS (
  SELECT id FROM notes WHERE title='Open questions on retrieval chunking' LIMIT 1
), review_row AS (
  SELECT id FROM literature_reviews WHERE title='RAG evaluation patterns' LIMIT 1
)
INSERT INTO project_idea_note_links (idea_id, note_id)
SELECT idea.id, note_row.id FROM idea, note_row
ON CONFLICT DO NOTHING;

WITH idea AS (
  SELECT id FROM project_ideas WHERE title='Benchmark retrieval chunking strategies' LIMIT 1
), review_row AS (
  SELECT id FROM literature_reviews WHERE title='RAG evaluation patterns' LIMIT 1
)
INSERT INTO project_idea_review_links (idea_id, review_id)
SELECT idea.id, review_row.id FROM idea, review_row
ON CONFLICT DO NOTHING;

WITH demo_user AS (
  SELECT id FROM users WHERE email='demo@research.local' LIMIT 1
)
INSERT INTO learning_milestones (user_id, title, description, status)
SELECT demo_user.id,
       'Complete 10-paper RAG comparison matrix',
       'Summarize architecture, datasets, and evaluation protocols for each paper.',
       'planned'
FROM demo_user
ON CONFLICT DO NOTHING;

WITH demo_user AS (
  SELECT id FROM users WHERE email='demo@research.local' LIMIT 1
), milestone AS (
  SELECT id FROM learning_milestones WHERE title='Complete 10-paper RAG comparison matrix' LIMIT 1
)
INSERT INTO learning_reflections (user_id, milestone_id, reflection_text, sentiment)
SELECT demo_user.id, milestone.id,
       'Strong progress on retrieval metrics understanding, still weak on long-context benchmarks.',
       'positive'
FROM demo_user, milestone
ON CONFLICT DO NOTHING;

INSERT INTO schema_migrations(version) VALUES ('002_seed_data') ON CONFLICT (version) DO NOTHING;

WITH demo_user AS (
  SELECT id FROM users WHERE email='demo@research.local' LIMIT 1
)
INSERT INTO learning_goals (user_id, title, description, status, skill_area)
SELECT demo_user.id, 'Improve experiment design rigor', 'Practice defining hypotheses and controls.', 'active', 'Experiment Design'
FROM demo_user
ON CONFLICT DO NOTHING;

WITH demo_user AS (
  SELECT id FROM users WHERE email='demo@research.local' LIMIT 1
)
INSERT INTO skill_areas (user_id, name, proficiency_level, milestone_text)
SELECT demo_user.id, 'Literature synthesis', 'intermediate', 'Summarize 20 papers with consistent rubric.'
FROM demo_user
ON CONFLICT DO NOTHING;

WITH demo_user AS (
  SELECT id FROM users WHERE email='demo@research.local' LIMIT 1
), app_row AS (
  SELECT id FROM embedded_apps WHERE title='ArXiv' LIMIT 1
), topic_row AS (
  SELECT id FROM topics WHERE name='Retrieval-Augmented Generation' LIMIT 1
), source_row AS (
  SELECT id FROM sources WHERE title='RAG Survey' LIMIT 1
)
INSERT INTO learning_sessions (user_id, embedded_app_id, app_key, duration_minutes, topic, session_notes, perceived_difficulty, research_topic_id, research_source_id)
SELECT demo_user.id, app_row.id, 'arxiv', 40, 'RAG evaluation metrics', 'Compared retriever metrics and identified open questions.', 'medium', topic_row.id, source_row.id
FROM demo_user, app_row, topic_row, source_row
ON CONFLICT DO NOTHING;
