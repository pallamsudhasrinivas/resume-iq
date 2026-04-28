import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useDeleteJD, useJDCandidates, useJDDetail, useJDList, useSaveJD } from '../hooks/useJDs'
import type { JDIndex } from '../types'
import CandidateCard from '../components/CandidateCard'
import SkillBadge from '../components/SkillBadge'

export default function JDLibraryPage() {
  const { data, isLoading } = useJDList()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)

  const jds = data?.jds ?? []

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">JD Library</h1>
          <p className="text-slate-500 text-sm mt-1">
            Save job descriptions and view all analyses run against each one.
          </p>
        </div>
        <button
          onClick={() => { setShowForm(true); setSelectedId(null) }}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors"
        >
          + Save New JD
        </button>
      </div>

      {showForm && (
        <SaveJDForm onClose={() => setShowForm(false)} />
      )}

      {isLoading && (
        <div className="text-center text-slate-400 py-16">Loading…</div>
      )}

      {!isLoading && jds.length === 0 && !showForm && (
        <div className="text-center py-20 bg-white rounded-xl border border-slate-200">
          <div className="text-5xl mb-4">📋</div>
          <p className="text-slate-600 font-medium">No saved job descriptions yet.</p>
          <p className="text-slate-400 text-sm mt-1">
            Save a JD to reuse it across multiple analyses.
          </p>
        </div>
      )}

      {jds.length > 0 && (
        <div className="flex gap-6">
          {/* Left: JD list */}
          <div className="w-72 flex-shrink-0 space-y-2">
            {jds.map((jd) => (
              <JDListItem
                key={jd.jd_id}
                jd={jd}
                isSelected={selectedId === jd.jd_id}
                onSelect={() => setSelectedId(jd.jd_id)}
              />
            ))}
          </div>

          {/* Right: Detail panel */}
          <div className="flex-1 min-w-0">
            {selectedId
              ? <JDDetailPanel jdId={selectedId} />
              : (
                <div className="flex items-center justify-center h-64 bg-white rounded-xl border border-dashed border-slate-300 text-slate-400 text-sm">
                  Select a JD to view details and analyses
                </div>
              )
            }
          </div>
        </div>
      )}
    </div>
  )
}

function JDListItem({
  jd, isSelected, onSelect,
}: { jd: JDIndex; isSelected: boolean; onSelect: () => void }) {
  const date = new Date(jd.created_at).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  })
  return (
    <button
      onClick={onSelect}
      className={`w-full text-left px-4 py-3 rounded-xl border transition-colors ${
        isSelected
          ? 'border-indigo-300 bg-indigo-50'
          : 'border-slate-200 bg-white hover:border-indigo-200 hover:bg-slate-50'
      }`}
    >
      <p className={`text-sm font-semibold truncate ${isSelected ? 'text-indigo-800' : 'text-slate-800'}`}>
        {jd.title}
      </p>
      <div className="flex items-center gap-2 mt-1 text-xs text-slate-400">
        <span>{date}</span>
        <span>·</span>
        <span>{jd.session_count} {jd.session_count === 1 ? 'analysis' : 'analyses'}</span>
      </div>
    </button>
  )
}

function JDDetailPanel({ jdId }: { jdId: string }) {
  const { data: jd, isLoading: jdLoading } = useJDDetail(jdId)
  const { data: candidatesData, isLoading: candidatesLoading } = useJDCandidates(jdId)
  const { mutate: deleteJD, isPending: deleting } = useDeleteJD()
  const [expanded, setExpanded] = useState(false)

  if (jdLoading) return <div className="text-slate-400 text-sm p-6">Loading…</div>
  if (!jd) return null

  const date = new Date(jd.created_at).toLocaleDateString('en-US', {
    month: 'long', day: 'numeric', year: 'numeric',
  })
  const candidates = candidatesData?.candidates ?? []

  return (
    <div className="space-y-4">
      {/* Header card */}
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <h2 className="text-lg font-bold text-slate-800 truncate">{jd.title}</h2>
            <div className="flex flex-wrap gap-3 mt-1 text-xs text-slate-500">
              <span>Saved {date}</span>
              <span>· {jd.session_count} {jd.session_count === 1 ? 'analysis' : 'analyses'}</span>
              {jd.jd_summary.role_level && (
                <span>· Level: <strong>{jd.jd_summary.role_level}</strong></span>
              )}
              {jd.jd_summary.years_required && (
                <span>· <strong>{jd.jd_summary.years_required}+</strong> yrs required</span>
              )}
              {jd.jd_summary.domain && (
                <span>· Domain: <strong>{jd.jd_summary.domain}</strong></span>
              )}
            </div>
          </div>
          <button
            onClick={() => deleteJD(jdId)}
            disabled={deleting}
            className="text-xs text-red-400 hover:text-red-600 font-medium flex-shrink-0 disabled:opacity-50"
          >
            Delete
          </button>
        </div>

        {/* Required skills */}
        {jd.jd_summary.required_skills.length > 0 && (
          <div className="mt-4">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
              Required Skills ({jd.jd_summary.required_skills.length})
            </p>
            <div className="flex flex-wrap gap-1.5">
              {jd.jd_summary.required_skills.map((s) => (
                <SkillBadge key={s} skill={s} variant="matched" />
              ))}
            </div>
          </div>
        )}

        {/* JD text toggle */}
        <button
          onClick={() => setExpanded((e) => !e)}
          className="mt-4 text-xs text-indigo-600 hover:underline font-medium"
        >
          {expanded ? 'Hide full JD ▲' : 'Show full JD ▼'}
        </button>
        {expanded && (
          <pre className="mt-2 text-xs text-slate-600 whitespace-pre-wrap bg-slate-50 rounded-lg p-4 max-h-64 overflow-y-auto font-sans leading-relaxed">
            {jd.text}
          </pre>
        )}
      </div>

      {/* All matched resumes */}
      <div>
        <h3 className="text-sm font-semibold text-slate-700 mb-3">
          Matched Resumes {candidates.length > 0 && `(${candidates.length})`}
        </h3>

        {candidatesLoading && (
          <div className="text-slate-400 text-sm py-4">Loading candidates…</div>
        )}

        {!candidatesLoading && candidates.length === 0 && (
          <div className="bg-white rounded-xl border border-dashed border-slate-200 p-10 text-center text-slate-400 text-sm">
            No resumes analysed against this JD yet.{' '}
            <Link to="/" className="text-indigo-600 hover:underline font-medium">
              Run an analysis →
            </Link>
          </div>
        )}

        {candidates.length > 0 && (
          <div className="space-y-4">
            {candidates.map((c, i) => (
              <div key={`${c.candidate_id}-${c.session_id}`} className="relative">
                {/* Session date badge */}
                <div className="absolute -top-2 right-3 z-10">
                  <span className="bg-slate-100 text-slate-500 text-xs px-2 py-0.5 rounded-full border border-slate-200">
                    {new Date(c.session_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                  </span>
                </div>
                <CandidateCard candidate={c} rank={i + 1} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function SaveJDForm({ onClose }: { onClose: () => void }) {
  const [title, setTitle] = useState('')
  const [text, setText] = useState('')
  const { mutate: saveJD, isPending, error } = useSaveJD()

  const handleSave = () => {
    if (!title.trim() || !text.trim()) return
    saveJD({ title: title.trim(), text }, {
      onSuccess: () => onClose(),
    })
  }

  return (
    <div className="bg-white border border-indigo-200 rounded-xl p-5 mb-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-slate-800">Save Job Description</h2>
        <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-lg leading-none">✕</button>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Title</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g. Senior Backend Engineer — Q2 2026"
          className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Job Description</label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={8}
          placeholder="Paste the full job description here…"
          className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
        />
      </div>

      {error && (
        <p className="text-red-600 text-sm">{(error as Error).message}</p>
      )}

      <div className="flex gap-3 justify-end">
        <button onClick={onClose} className="px-4 py-2 text-sm text-slate-600 hover:text-slate-800">
          Cancel
        </button>
        <button
          onClick={handleSave}
          disabled={isPending || !title.trim() || !text.trim()}
          className="px-4 py-2 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isPending ? 'Saving…' : 'Save JD'}
        </button>
      </div>
    </div>
  )
}
