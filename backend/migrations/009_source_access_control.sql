ALTER TABLE sources
  ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id);

UPDATE sources
SET user_id = (
  SELECT id FROM users ORDER BY id ASC LIMIT 1
)
WHERE user_id IS NULL;

ALTER TABLE sources
  ALTER COLUMN user_id SET NOT NULL;

CREATE INDEX IF NOT EXISTS idx_sources_user_created ON sources (user_id, created_at DESC);

INSERT INTO schema_migrations(version) VALUES ('009_source_access_control') ON CONFLICT (version) DO NOTHING;
