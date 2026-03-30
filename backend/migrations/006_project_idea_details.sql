ALTER TABLE project_ideas
  ADD COLUMN IF NOT EXISTS estimated_difficulty VARCHAR(40) NOT NULL DEFAULT 'medium',
  ADD COLUMN IF NOT EXISTS suggested_next_step TEXT NOT NULL DEFAULT '',
  ADD COLUMN IF NOT EXISTS evidence_json TEXT NOT NULL DEFAULT '[]';

INSERT INTO schema_migrations(version) VALUES ('006_project_idea_details') ON CONFLICT (version) DO NOTHING;
