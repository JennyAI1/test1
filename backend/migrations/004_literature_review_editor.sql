ALTER TABLE literature_reviews
  ADD COLUMN IF NOT EXISTS authors VARCHAR(1024) NOT NULL DEFAULT '',
  ADD COLUMN IF NOT EXISTS publication_year INTEGER,
  ADD COLUMN IF NOT EXISTS methods TEXT NOT NULL DEFAULT '',
  ADD COLUMN IF NOT EXISTS findings TEXT NOT NULL DEFAULT '',
  ADD COLUMN IF NOT EXISTS limitations TEXT NOT NULL DEFAULT '';

ALTER TABLE notes
  ADD COLUMN IF NOT EXISTS review_id INTEGER REFERENCES literature_reviews(id);

CREATE INDEX IF NOT EXISTS idx_notes_review_id ON notes (review_id);

CREATE INDEX IF NOT EXISTS idx_literature_reviews_fts
ON literature_reviews
USING GIN (to_tsvector('english', coalesce(title,'') || ' ' || coalesce(authors,'') || ' ' || coalesce(summary,'') || ' ' || coalesce(methods,'') || ' ' || coalesce(findings,'') || ' ' || coalesce(limitations,'')));

UPDATE literature_reviews
SET status = 'to-read'
WHERE status IS NULL OR status = 'in_progress';

INSERT INTO schema_migrations(version) VALUES ('004_literature_review_editor') ON CONFLICT (version) DO NOTHING;
