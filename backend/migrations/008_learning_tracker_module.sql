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

CREATE INDEX IF NOT EXISTS idx_learning_goals_user_status ON learning_goals (user_id, status);
CREATE INDEX IF NOT EXISTS idx_skill_areas_user_name ON skill_areas (user_id, name);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_user_time ON learning_sessions (user_id, occurred_at DESC);

INSERT INTO schema_migrations(version) VALUES ('008_learning_tracker_module') ON CONFLICT (version) DO NOTHING;
