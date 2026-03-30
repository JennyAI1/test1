CREATE TABLE IF NOT EXISTS schema_migrations (
  version TEXT PRIMARY KEY,
  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS topics (
  id SERIAL PRIMARY KEY,
  name VARCHAR(120) UNIQUE NOT NULL,
  description TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sources (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  title VARCHAR(255) NOT NULL,
  authors VARCHAR(1024) NOT NULL DEFAULT '',
  source_url VARCHAR(1024),
  source_type VARCHAR(50) NOT NULL DEFAULT 'paper',
  publication_year INTEGER,
  summary TEXT NOT NULL DEFAULT '',
  takeaway TEXT NOT NULL DEFAULT '',
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS literature_reviews (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  source_id INTEGER REFERENCES sources(id),
  title VARCHAR(255) NOT NULL,
  summary TEXT NOT NULL,
  authors VARCHAR(1024) NOT NULL DEFAULT '',
  publication_year INTEGER,
  methods TEXT NOT NULL DEFAULT '',
  findings TEXT NOT NULL DEFAULT '',
  limitations TEXT NOT NULL DEFAULT '',
  status VARCHAR(40) NOT NULL DEFAULT 'to-read',
  tags VARCHAR(1024) NOT NULL DEFAULT '',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS review_citations (
  id SERIAL PRIMARY KEY,
  review_id INTEGER NOT NULL REFERENCES literature_reviews(id) ON DELETE CASCADE,
  citation_text TEXT NOT NULL,
  citation_url VARCHAR(1024),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notes (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  topic_id INTEGER REFERENCES topics(id),
  source_id INTEGER REFERENCES sources(id),
  review_id INTEGER REFERENCES literature_reviews(id),
  title VARCHAR(255) NOT NULL,
  body TEXT NOT NULL,
  tags VARCHAR(1024) NOT NULL DEFAULT '',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS embedded_apps (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  title VARCHAR(255) NOT NULL,
  url VARCHAR(1024) NOT NULL,
  category VARCHAR(80) NOT NULL,
  panel_order INTEGER NOT NULL DEFAULT 0,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  usage_metadata TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS embedded_app_usage (
  id SERIAL PRIMARY KEY,
  app_id INTEGER NOT NULL REFERENCES embedded_apps(id) ON DELETE CASCADE,
  user_id INTEGER NOT NULL REFERENCES users(id),
  session_started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  session_ended_at TIMESTAMP,
  minutes_spent DOUBLE PRECISION NOT NULL DEFAULT 0,
  usage_metadata TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS project_ideas (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  title VARCHAR(255) NOT NULL,
  rationale TEXT NOT NULL,
  estimated_difficulty VARCHAR(40) NOT NULL DEFAULT 'medium',
  suggested_next_step TEXT NOT NULL DEFAULT '',
  evidence_json TEXT NOT NULL DEFAULT '[]',
  generation_model VARCHAR(120) NOT NULL DEFAULT 'heuristic',
  confidence_score DOUBLE PRECISION,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS project_idea_note_links (
  idea_id INTEGER NOT NULL REFERENCES project_ideas(id) ON DELETE CASCADE,
  note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  PRIMARY KEY (idea_id, note_id)
);

CREATE TABLE IF NOT EXISTS project_idea_review_links (
  idea_id INTEGER NOT NULL REFERENCES project_ideas(id) ON DELETE CASCADE,
  review_id INTEGER NOT NULL REFERENCES literature_reviews(id) ON DELETE CASCADE,
  PRIMARY KEY (idea_id, review_id)
);


CREATE TABLE IF NOT EXISTS ai_evaluation_logs (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  task_type VARCHAR(80) NOT NULL,
  prompt_template TEXT NOT NULL,
  input_snapshot TEXT NOT NULL,
  output_snapshot TEXT NOT NULL,
  quality_score DOUBLE PRECISION,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS learning_goals (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  target_date TIMESTAMP,
  status VARCHAR(40) NOT NULL DEFAULT 'active',
  skill_area VARCHAR(120),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skill_areas (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  name VARCHAR(120) NOT NULL,
  proficiency_level VARCHAR(40) NOT NULL DEFAULT 'beginner',
  milestone_text TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learning_sessions (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  embedded_app_id INTEGER REFERENCES embedded_apps(id),
  app_key VARCHAR(80) NOT NULL,
  duration_minutes DOUBLE PRECISION NOT NULL DEFAULT 0,
  topic VARCHAR(255) NOT NULL,
  session_notes TEXT NOT NULL DEFAULT '',
  perceived_difficulty VARCHAR(40) NOT NULL DEFAULT 'medium',
  research_topic_id INTEGER REFERENCES topics(id),
  research_source_id INTEGER REFERENCES sources(id),
  occurred_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learning_milestones (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  target_date TIMESTAMP,
  status VARCHAR(40) NOT NULL DEFAULT 'planned',
  completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learning_reflections (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  milestone_id INTEGER REFERENCES learning_milestones(id),
  reflection_text TEXT NOT NULL,
  sentiment VARCHAR(40),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Legacy compatibility tables used by existing API routes.
CREATE TABLE IF NOT EXISTS research_entries (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  title VARCHAR(255) NOT NULL,
  entry_type VARCHAR(50) NOT NULL DEFAULT 'note',
  tags VARCHAR(1024) NOT NULL DEFAULT '',
  encrypted_content TEXT NOT NULL,
  source_url VARCHAR(1024),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learning_progress_events (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  app_key VARCHAR(80) NOT NULL,
  activity_type VARCHAR(80) NOT NULL,
  minutes_spent DOUBLE PRECISION NOT NULL DEFAULT 0,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_literature_reviews_user_status ON literature_reviews (user_id, status);
CREATE INDEX IF NOT EXISTS idx_literature_reviews_fts
ON literature_reviews
USING GIN (to_tsvector('english', coalesce(title,'') || ' ' || coalesce(authors,'') || ' ' || coalesce(summary,'') || ' ' || coalesce(methods,'') || ' ' || coalesce(findings,'') || ' ' || coalesce(limitations,'')));
CREATE INDEX IF NOT EXISTS idx_notes_user_topic_source ON notes (user_id, topic_id, source_id);
CREATE INDEX IF NOT EXISTS idx_embedded_apps_category ON embedded_apps (category);
CREATE INDEX IF NOT EXISTS idx_embedded_apps_user_order ON embedded_apps (user_id, panel_order);
CREATE INDEX IF NOT EXISTS idx_project_ideas_user_created ON project_ideas (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_learning_progress_user_created ON learning_progress_events (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_learning_goals_user_status ON learning_goals (user_id, status);
CREATE INDEX IF NOT EXISTS idx_skill_areas_user_name ON skill_areas (user_id, name);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_user_time ON learning_sessions (user_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_sources_user_created ON sources (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_eval_user_task_created ON ai_evaluation_logs (user_id, task_type, created_at DESC);

INSERT INTO schema_migrations(version) VALUES ('001_initial_schema') ON CONFLICT (version) DO NOTHING;
