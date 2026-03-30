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

CREATE INDEX IF NOT EXISTS idx_ai_eval_user_task_created ON ai_evaluation_logs (user_id, task_type, created_at DESC);

INSERT INTO schema_migrations(version) VALUES ('007_ai_evaluation_logs') ON CONFLICT (version) DO NOTHING;
