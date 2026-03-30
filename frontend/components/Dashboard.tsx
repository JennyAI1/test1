'use client'

import { useMemo, useState } from 'react'
import { RichTextEditor } from './RichTextEditor'
import { apiFetch } from '../lib/api'

type EmbeddedApp = {
  id: number
  title: string
  url: string
  category: string
  panel_order: number
}

type LinkedNote = {
  id: number
  title: string
  body: string
  tags: string[]
}

type LiteratureReview = {
  id: number
  title: string
  authors: string[]
  publication_year?: number
  methods: string
  findings: string
  limitations: string
  summary: string
  status: 'to-read' | 'reviewed' | 'synthesized'
  tags: string[]
  linked_notes: LinkedNote[]
}

type SourceItem = {
  id: number
  title: string
  authors: string[]
  source_url?: string
  source_type: string
  publication_year?: number
  summary: string
  takeaway: string
}


type LearningCoachRecommendation = {
  next_skill: string
  recommended_embedded_app: string
  weekly_plan: string
  why_it_matters: string
}

type LearningDashboard = {
  total_learning_minutes: number
  streak_days: number
  topic_distribution: Record<string, number>
  milestones_completed: number
  active_goals_progress: Array<{ goal_id: number; title: string; status: string; estimated_progress_percent: number }>
  session_idea_correlations: Array<{ session_id: number; idea_id: number; score: number; reason: string }>
}

const STATUS_OPTIONS: Array<LiteratureReview['status']> = ['to-read', 'reviewed', 'synthesized']
const ALLOWED_EMBED_HOSTS = ['arxiv.org', 'observablehq.com', 'docs.google.com', 'notion.so']

const isSafeEmbedUrl = (url: string) => {
  try {
    const parsed = new URL(url)
    return parsed.protocol === 'https:' && ALLOWED_EMBED_HOSTS.some((host) => parsed.hostname === host || parsed.hostname.endsWith(`.${host}`))
  } catch {
    return false
  }
}

export function Dashboard() {
  const [token, setToken] = useState<string>('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const [appTitle, setAppTitle] = useState('')
  const [appUrl, setAppUrl] = useState('https://arxiv.org')
  const [appCategory, setAppCategory] = useState('literature')
  const [embeddedApps, setEmbeddedApps] = useState<EmbeddedApp[]>([])
  const [failedEmbeds, setFailedEmbeds] = useState<Record<number, boolean>>({})

  const [reviewTitle, setReviewTitle] = useState('')
  const [reviewAuthors, setReviewAuthors] = useState('')
  const [reviewYear, setReviewYear] = useState<number | ''>('')
  const [reviewMethods, setReviewMethods] = useState('')
  const [reviewFindings, setReviewFindings] = useState('<p>Key findings...</p>')
  const [reviewLimitations, setReviewLimitations] = useState('')
  const [reviewSummary, setReviewSummary] = useState('')
  const [reviewTags, setReviewTags] = useState('')
  const [reviewStatus, setReviewStatus] = useState<LiteratureReview['status']>('to-read')

  const [searchQuery, setSearchQuery] = useState('')
  const [searchTag, setSearchTag] = useState('')
  const [searchStatus, setSearchStatus] = useState('')
  const [reviews, setReviews] = useState<LiteratureReview[]>([])

  const [noteReviewId, setNoteReviewId] = useState<number | ''>('')
  const [noteTitle, setNoteTitle] = useState('')
  const [noteBody, setNoteBody] = useState('')
  const [noteTags, setNoteTags] = useState('')

  const [sourceTitle, setSourceTitle] = useState('')
  const [sourceAuthors, setSourceAuthors] = useState('')
  const [sourceUrl, setSourceUrl] = useState('')
  const [sourceYear, setSourceYear] = useState<number | ''>('')
  const [sourceSummary, setSourceSummary] = useState('')
  const [sourceTakeaway, setSourceTakeaway] = useState('')
  const [sources, setSources] = useState<SourceItem[]>([])

  const [pdfFilename, setPdfFilename] = useState('paper.pdf')
  const [pdfMetadataPreview, setPdfMetadataPreview] = useState<{ title: string; authors: string[]; notes: string } | null>(null)

  const [sourceNoteSourceId, setSourceNoteSourceId] = useState<number | ''>('')
  const [sourceNoteTitle, setSourceNoteTitle] = useState('')
  const [sourceNoteBody, setSourceNoteBody] = useState('')
  const [sourceNoteTags, setSourceNoteTags] = useState('')
  const [learningDashboard, setLearningDashboard] = useState<LearningDashboard | null>(null)
  const [learningCoach, setLearningCoach] = useState<LearningCoachRecommendation[]>([])

  const isAuthed = useMemo(() => token.length > 0, [token])

  const authenticate = async (mode: 'register' | 'login') => {
    const data = await apiFetch<{ access_token: string }>(`/auth/${mode}`, {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    setToken(data.access_token)
  }

  const createSource = async () => {
    await apiFetch('/ingestion/sources', {
      method: 'POST',
      body: JSON.stringify({
        title: sourceTitle,
        authors: sourceAuthors.split(',').map((v) => v.trim()).filter(Boolean),
        source_url: sourceUrl || null,
        source_type: 'manual',
        publication_year: sourceYear === '' ? null : sourceYear,
        summary: sourceSummary,
        takeaway: sourceTakeaway,
      }),
    }, token)
    setSourceTitle('')
    setSourceAuthors('')
    setSourceUrl('')
    setSourceYear('')
    setSourceSummary('')
    setSourceTakeaway('')
    await loadSources()
  }

  const loadSources = async () => {
    const data = await apiFetch<SourceItem[]>('/ingestion/sources', {}, token)
    setSources(data)
  }

  const previewPdfMetadata = async () => {
    const data = await apiFetch<{ title: string; authors: string[]; notes: string }>('/ingestion/pdf-metadata-placeholder', {
      method: 'POST',
      body: JSON.stringify({ filename: pdfFilename }),
    }, token)
    setPdfMetadataPreview(data)
  }

  const attachNoteToSource = async () => {
    if (sourceNoteSourceId === '') return
    await apiFetch(`/ingestion/sources/${sourceNoteSourceId}/notes`, {
      method: 'POST',
      body: JSON.stringify({
        title: sourceNoteTitle,
        body: sourceNoteBody,
        tags: sourceNoteTags.split(',').map((v) => v.trim()).filter(Boolean),
      }),
    }, token)
    setSourceNoteTitle('')
    setSourceNoteBody('')
    setSourceNoteTags('')
  }

  const loadLearningDashboard = async () => {
    const data = await apiFetch<LearningDashboard>('/learning-tracker/dashboard', {}, token)
    setLearningDashboard(data)
  }

  const loadLearningCoach = async () => {
    const data = await apiFetch<{ recommendations: LearningCoachRecommendation[] }>('/ai/learning-coach/recommendations', {}, token)
    setLearningCoach(data.recommendations)
  }

  const loadEmbeddedApps = async () => {
    const data = await apiFetch<EmbeddedApp[]>('/embedded-apps', {}, token)
    setEmbeddedApps(data)
  }

  const addEmbeddedApp = async () => {
    await apiFetch('/embedded-apps', {
      method: 'POST',
      body: JSON.stringify({ title: appTitle, url: appUrl, category: appCategory }),
    }, token)
    setAppTitle('')
    await loadEmbeddedApps()
  }

  const removeEmbeddedApp = async (id: number) => {
    await apiFetch(`/embedded-apps/${id}`, { method: 'DELETE' }, token)
    await loadEmbeddedApps()
  }

  const reorderEmbeddedApp = async (id: number, direction: -1 | 1) => {
    const index = embeddedApps.findIndex((app) => app.id === id)
    const targetIndex = index + direction
    if (index < 0 || targetIndex < 0 || targetIndex >= embeddedApps.length) {
      return
    }

    const reordered = [...embeddedApps]
    ;[reordered[index], reordered[targetIndex]] = [reordered[targetIndex], reordered[index]]

    const updated = await apiFetch<EmbeddedApp[]>('/embedded-apps/reorder', {
      method: 'POST',
      body: JSON.stringify({ ordered_ids: reordered.map((app) => app.id) }),
    }, token)
    setEmbeddedApps(updated)
  }

  const saveReview = async () => {
    await apiFetch('/literature-reviews', {
      method: 'POST',
      body: JSON.stringify({
        title: reviewTitle,
        authors: reviewAuthors.split(',').map((v) => v.trim()).filter(Boolean),
        publication_year: reviewYear === '' ? null : reviewYear,
        methods: reviewMethods,
        findings: reviewFindings,
        limitations: reviewLimitations,
        summary: reviewSummary,
        status: reviewStatus,
        tags: reviewTags.split(',').map((v) => v.trim()).filter(Boolean),
      }),
    }, token)
    await searchReviews()
  }

  const searchReviews = async () => {
    const params = new URLSearchParams()
    if (searchQuery) params.set('query', searchQuery)
    if (searchTag) params.set('tag', searchTag)
    if (searchStatus) params.set('status', searchStatus)

    const path = `/literature-reviews${params.toString() ? `?${params.toString()}` : ''}`
    const data = await apiFetch<LiteratureReview[]>(path, {}, token)
    setReviews(data)
  }

  const addLinkedNote = async () => {
    if (noteReviewId === '') return

    await apiFetch(`/literature-reviews/${noteReviewId}/notes`, {
      method: 'POST',
      body: JSON.stringify({
        title: noteTitle,
        body: noteBody,
        tags: noteTags.split(',').map((v) => v.trim()).filter(Boolean),
      }),
    }, token)

    setNoteTitle('')
    setNoteBody('')
    setNoteTags('')
    await searchReviews()
  }

  if (!isAuthed) {
    return (
      <main className="shell">
        <h1>Research Workspace</h1>
        <section className="card">
          <h2>Authentication</h2>
          <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
          <div className="row">
            <button onClick={() => authenticate('register')}>Register</button>
            <button onClick={() => authenticate('login')}>Login</button>
          </div>
        </section>
      </main>
    )
  }

  return (
    <main className="shell">
      <h1>Research Workspace Dashboard</h1>

      <section className="card">
        <h2>Ingestion Flow: Manual Entry</h2>
        <div className="grid2">
          <input value={sourceTitle} onChange={(e) => setSourceTitle(e.target.value)} placeholder="Source title" />
          <input value={sourceAuthors} onChange={(e) => setSourceAuthors(e.target.value)} placeholder="Authors (comma separated)" />
          <input value={sourceUrl} onChange={(e) => setSourceUrl(e.target.value)} placeholder="URL/source field" />
          <input value={sourceYear} type="number" onChange={(e) => setSourceYear(e.target.value ? Number(e.target.value) : '')} placeholder="Year" />
        </div>
        <textarea value={sourceSummary} onChange={(e) => setSourceSummary(e.target.value)} placeholder="Summary" />
        <textarea value={sourceTakeaway} onChange={(e) => setSourceTakeaway(e.target.value)} placeholder="Takeaway" />
        <div className="row">
          <button onClick={createSource}>Create Source</button>
          <button onClick={loadSources}>Refresh Sources</button>
        </div>
      </section>

      <section className="card">
        <h2>PDF Metadata Form (Placeholder)</h2>
        <div className="row">
          <input value={pdfFilename} onChange={(e) => setPdfFilename(e.target.value)} placeholder="paper.pdf" />
          <button onClick={previewPdfMetadata}>Generate Placeholder Metadata</button>
        </div>
        {pdfMetadataPreview && (
          <div className="panelCard">
            <strong>{pdfMetadataPreview.title}</strong>
            <p>Authors: {pdfMetadataPreview.authors.join(', ')}</p>
            <p>{pdfMetadataPreview.notes}</p>
          </div>
        )}
      </section>

      <section className="card">
        <h2>Attach Notes to Source</h2>
        <div className="row">
          <input value={sourceNoteSourceId} onChange={(e) => setSourceNoteSourceId(e.target.value ? Number(e.target.value) : '')} placeholder="Source ID" />
          <input value={sourceNoteTitle} onChange={(e) => setSourceNoteTitle(e.target.value)} placeholder="Note title" />
          <input value={sourceNoteTags} onChange={(e) => setSourceNoteTags(e.target.value)} placeholder="Tags" />
        </div>
        <textarea value={sourceNoteBody} onChange={(e) => setSourceNoteBody(e.target.value)} placeholder="Note body" />
        <button onClick={attachNoteToSource}>Attach Note</button>

        <ul className="reviewList">
          {sources.map((source) => (
            <li key={source.id}>
              <strong>{source.title}</strong> {source.publication_year ? `(${source.publication_year})` : ''}
              <p>{source.source_url}</p>
              <p>Summary: {source.summary}</p>
              <p>Takeaway: {source.takeaway}</p>
            </li>
          ))}
        </ul>
      </section>

      <section className="card">
        <h2>Literature Review Editor</h2>
        <div className="grid2">
          <input value={reviewTitle} onChange={(e) => setReviewTitle(e.target.value)} placeholder="Title" />
          <input value={reviewAuthors} onChange={(e) => setReviewAuthors(e.target.value)} placeholder="Authors (comma separated)" />
          <input value={reviewYear} type="number" onChange={(e) => setReviewYear(e.target.value ? Number(e.target.value) : '')} placeholder="Year" />
          <select value={reviewStatus} onChange={(e) => setReviewStatus(e.target.value as LiteratureReview['status'])}>
            {STATUS_OPTIONS.map((status) => <option key={status} value={status}>{status}</option>)}
          </select>
        </div>
        <textarea value={reviewMethods} onChange={(e) => setReviewMethods(e.target.value)} placeholder="Methods (markdown or plain text)" />
        <RichTextEditor value={reviewFindings} onChange={setReviewFindings} />
        <textarea value={reviewLimitations} onChange={(e) => setReviewLimitations(e.target.value)} placeholder="Limitations" />
        <textarea value={reviewSummary} onChange={(e) => setReviewSummary(e.target.value)} placeholder="Summary" />
        <input value={reviewTags} onChange={(e) => setReviewTags(e.target.value)} placeholder="tags,comma,separated" />
        <button onClick={saveReview}>Save Literature Review</button>
      </section>

      <section className="card">
        <h2>Search & Organize</h2>
        <div className="row">
          <input value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Full-text search" />
          <input value={searchTag} onChange={(e) => setSearchTag(e.target.value)} placeholder="Tag filter" />
          <select value={searchStatus} onChange={(e) => setSearchStatus(e.target.value)}>
            <option value="">All statuses</option>
            {STATUS_OPTIONS.map((status) => <option key={status} value={status}>{status}</option>)}
          </select>
          <button onClick={searchReviews}>Run Search</button>
        </div>

        <ul className="reviewList">
          {reviews.map((review) => (
            <li key={review.id}>
              <div className="row between">
                <strong>{review.title}</strong>
                <span className={`badge badge-${review.status}`}>{review.status}</span>
              </div>
              <p>{review.authors.join(', ')} {review.publication_year ? `(${review.publication_year})` : ''}</p>
              <p>Tags: {review.tags.join(', ') || 'none'}</p>
              <details>
                <summary>Linked notes ({review.linked_notes.length})</summary>
                <ul>{review.linked_notes.map((note) => <li key={note.id}><strong>{note.title}</strong> — {note.tags.join(', ')}</li>)}</ul>
              </details>
            </li>
          ))}
        </ul>
      </section>

      <section className="card">
        <h2>Linked Notes</h2>
        <div className="row">
          <input value={noteReviewId} onChange={(e) => setNoteReviewId(e.target.value ? Number(e.target.value) : '')} placeholder="Review ID" />
          <input value={noteTitle} onChange={(e) => setNoteTitle(e.target.value)} placeholder="Note title" />
          <input value={noteTags} onChange={(e) => setNoteTags(e.target.value)} placeholder="note tags" />
        </div>
        <textarea value={noteBody} onChange={(e) => setNoteBody(e.target.value)} placeholder="Note body" />
        <button onClick={addLinkedNote}>Add Linked Note</button>
      </section>



      <section className="card">
        <h2>AI Learning Coach</h2>
        <button onClick={loadLearningCoach}>Generate Coaching Recommendations</button>
        <ul className="reviewList">
          {learningCoach.map((item, idx) => (
            <li key={`${item.next_skill}-${idx}`}>
              <p><strong>Next skill:</strong> {item.next_skill}</p>
              <p><strong>Use next app:</strong> {item.recommended_embedded_app}</p>
              <p><strong>Weekly plan:</strong> {item.weekly_plan}</p>
              <p><strong>Why it matters:</strong> {item.why_it_matters}</p>
            </li>
          ))}
        </ul>
      </section>

      <section className="card">
        <h2>Progress Dashboard</h2>
        <button onClick={loadLearningDashboard}>Load Progress Dashboard</button>
        {learningDashboard && (
          <div className="panelCard">
            <p><strong>Total learning time:</strong> {learningDashboard.total_learning_minutes} min</p>
            <p><strong>Streak:</strong> {learningDashboard.streak_days} day(s)</p>
            <p><strong>Milestones completed:</strong> {learningDashboard.milestones_completed}</p>
            <p><strong>Topic distribution:</strong></p>
            <pre>{JSON.stringify(learningDashboard.topic_distribution, null, 2)}</pre>
            <p><strong>Progress toward active goals:</strong></p>
            <ul>
              {learningDashboard.active_goals_progress.map((goal) => (
                <li key={goal.goal_id}>{goal.title}: {goal.estimated_progress_percent}%</li>
              ))}
            </ul>
            <p><strong>Session ↔ idea correlations:</strong></p>
            <ul>
              {learningDashboard.session_idea_correlations.map((item) => (
                <li key={`${item.session_id}-${item.idea_id}`}>Session {item.session_id} / Idea {item.idea_id} ({item.score}) - {item.reason}</li>
              ))}
            </ul>
          </div>
        )}
      </section>

      <section className="card">
        <h2>Embedded Apps Dashboard</h2>
        <p className="muted">Allowed domains are enforced by the backend allowlist for safe embedding.</p>
        <div className="row">
          <input value={appTitle} onChange={(e) => setAppTitle(e.target.value)} placeholder="App title" />
          <input value={appUrl} onChange={(e) => setAppUrl(e.target.value)} placeholder="https://..." />
          <input value={appCategory} onChange={(e) => setAppCategory(e.target.value)} placeholder="Category" />
          <button onClick={addEmbeddedApp}>Add app</button>
          <button onClick={loadEmbeddedApps}>Refresh</button>
        </div>

        <div className="panelGrid">
          {embeddedApps.map((app, idx) => (
            <article key={app.id} className="panelCard">
              <header className="row panelHeader">
                <strong>{app.title}</strong>
                <span>{app.category}</span>
              </header>
              {isSafeEmbedUrl(app.url) ? (
                <>
                  <iframe src={app.url} title={app.title} sandbox="allow-scripts allow-same-origin allow-forms" referrerPolicy="no-referrer" onError={() => setFailedEmbeds((prev) => ({ ...prev, [app.id]: true }))} />
                  {failedEmbeds[app.id] && (
                    <div className="embedFallback">
                      <p>This app could not be embedded. It may block framing.</p>
                      <a href={app.url} target="_blank" rel="noreferrer">Open in a new tab</a>
                    </div>
                  )}
                </>
              ) : (
                <div className="embedFallback">
                  <p>Blocked unsafe or unexpected iframe source.</p>
                </div>
              )}
              <div className="row">
                <button disabled={idx === 0} onClick={() => reorderEmbeddedApp(app.id, -1)}>Move up</button>
                <button disabled={idx === embeddedApps.length - 1} onClick={() => reorderEmbeddedApp(app.id, 1)}>Move down</button>
                <button onClick={() => removeEmbeddedApp(app.id)}>Remove</button>
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  )
}
