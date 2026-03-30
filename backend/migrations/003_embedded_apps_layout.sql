ALTER TABLE embedded_apps
  ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id),
  ADD COLUMN IF NOT EXISTS panel_order INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

UPDATE embedded_apps
SET user_id = (
  SELECT id FROM users ORDER BY id ASC LIMIT 1
)
WHERE user_id IS NULL;

ALTER TABLE embedded_apps
  ALTER COLUMN user_id SET NOT NULL;

CREATE INDEX IF NOT EXISTS idx_embedded_apps_user_order ON embedded_apps (user_id, panel_order);

INSERT INTO schema_migrations(version) VALUES ('003_embedded_apps_layout') ON CONFLICT (version) DO NOTHING;
