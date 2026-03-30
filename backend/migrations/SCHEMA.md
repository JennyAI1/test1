# Schema Notes

## Core
- `users`
- `topics`
- `sources`

## Research Knowledge
- `literature_reviews` -> optional `sources`
- `review_citations` -> `literature_reviews`
- `notes` -> optional `topics`, optional `sources`, optional `literature_reviews`

## Embedded Apps Dashboard
- `embedded_apps` -> `users` (owner), includes `panel_order`, `is_active`, URL/category/metadata
- `embedded_app_usage` -> `embedded_apps`, `users`

## AI Ideas
- `project_ideas` -> `users`
- `project_idea_note_links` -> `project_ideas`, `notes`
- `project_idea_review_links` -> `project_ideas`, `literature_reviews`
- `ai_evaluation_logs` -> `users` (prompt template, snapshots, quality score)

## Learning
- `learning_progress_events` -> `users`
- `learning_goals` -> `users`
- `learning_sessions` -> `users`, optional `embedded_apps`, optional research links (`topics`/`sources`)
- `skill_areas` -> `users`
- `learning_milestones` -> `users`
- `learning_reflections` -> `users`, optional `learning_milestones`
