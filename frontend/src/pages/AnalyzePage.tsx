import { useCallback, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAnalyze } from '../hooks/useAnalyze'
import { useJDList } from '../hooks/useJDs'
import type { Session } from '../types'
import CandidateCard from '../components/CandidateCard'
import SkillBadge from '../components/SkillBadge'

const STEPS = ['Parsing job description', 'Scoring candidates', 'Saving results']

export default function AnalyzePage() {
  const [jdMode, setJdMode] = useState<'paste' | 'library'>('paste')
  const [jd, setJd] = useState('')
  const [selectedJdId, setSelectedJdId] = useState<string | null>(null)
  const [files, setFiles] = useState<File[]>([])
  const [session, setSession] = useState<Session | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [step, setStep] = useState(0)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { mutate, isPending, error } = useAnalyze()
  const { data: jdList } = useJDList()

  const addFiles = useCallback((list: FileList | null) => {
    if (!list) return
    const valid = Array.from(list).filter(
      (f) => /\.(pdf|docx|doc|rtf|txt)$/i.test(f.name),
    )
    setFiles((prev) => {
      const existing = new Set(prev.map((f) => f.name))
      return [...prev, ...valid.filter((f) => !existing.has(f.name))].slice(0, 10)
    })
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)
      addFiles(e.dataTransfer.files)
    },
    [addFiles],
  )

  const removeFile = (name: string) => setFiles((p) => p.filter((f) => f.name !== name))

  const handleAnalyze = () => {
    const jdReady = jdMode === 'paste' ? jd.trim().length > 0 : !!selectedJdId
    if (!jdReady || files.length === 0) return
    setSession(null)
    setStep(0)

    const interval = setInterval(() => {
      setStep((s) => {
        if (s < STEPS.length - 1) return s + 1
        clearInterval(interval)
        return s
      })
    }, 700)

    const args =
      jdMode === 'library' && selectedJdId
        ? { files, jdId: selectedJdId }
        : { files, jobDescription: jd }

    mutate(args, {
      onSuccess: (data) => {
        clearInterval(interval)
        setStep(STEPS.length)
        setSession(data)
      },
      onError: () => {
        clearInterval(interval)
        setStep(0)
      },
    })
  }

  const resetAll = () => {
    setSession(null)
    setFiles([])
    setJd('')
    setSelectedJdId(null)
    setStep(0)
  }

  const jdReady = jdMode === 'paste' ? jd.trim().length > 0 : !!selectedJdId
  const canAnalyze = jdReady && files.length > 0 && !isPending

  const savedJDs = jdList?.jds ?? []

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">New Analysis</h1>
        <p className="text-slate-500 text-sm mt-1">
          Paste a job description or pick one from your library, then upload resumes.
        </p>
      </div>

      {/* ── Input form ── */}
      {!session && (
        <div className="space-y-5">
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-sm font-medium text-slate-700">
                Job Description <span className="text-red-500">*</span>
              </label>
              {/* Mode toggle */}
              <div className="flex rounded-lg border border-slate-200 overflow-hidden text-xs font-medium">
                <button
                  onClick={() => setJdMode('paste')}
                  className={`px-3 py-1.5 transition-colors ${
                    jdMode === 'paste'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white text-slate-500 hover:bg-slate-50'
                  }`}
                >
                  Paste
                </button>
                <button
                  onClick={() => setJdMode('library')}
                  className={`px-3 py-1.5 transition-colors border-l border-slate-200 ${
                    jdMode === 'library'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white text-slate-500 hover:bg-slate-50'
                  }`}
                >
                  From Library {savedJDs.length > 0 && `(${savedJDs.length})`}
                </button>
              </div>
            </div>

            {jdMode === 'paste' ? (
              <textarea
                value={jd}
                onChange={(e) => setJd(e.target.value)}
                rows={8}
                placeholder="Paste the full job description here…"
                className="w-full border border-slate-300 rounded-lg px-4 py-3 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
              />
            ) : savedJDs.length === 0 ? (
              <div className="border border-dashed border-slate-300 rounded-lg px-4 py-8 text-center text-sm text-slate-400">
                No saved JDs yet.{' '}
                <Link to="/jd-library" className="text-indigo-600 hover:underline font-medium">
                  Go to JD Library →
                </Link>
              </div>
            ) : (
              <div className="border border-slate-200 rounded-lg divide-y divide-slate-100 max-h-72 overflow-y-auto">
                {savedJDs.map((jdItem) => (
                  <button
                    key={jdItem.jd_id}
                    onClick={() => setSelectedJdId(jdItem.jd_id)}
                    className={`w-full text-left px-4 py-3 flex items-center justify-between transition-colors ${
                      selectedJdId === jdItem.jd_id
                        ? 'bg-indigo-50 border-l-2 border-indigo-500'
                        : 'hover:bg-slate-50'
                    }`}
                  >
                    <div>
                      <p className={`text-sm font-medium ${selectedJdId === jdItem.jd_id ? 'text-indigo-800' : 'text-slate-800'}`}>
                        {jdItem.title}
                      </p>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {new Date(jdItem.created_at).toLocaleDateString()} · {jdItem.session_count} {jdItem.session_count === 1 ? 'analysis' : 'analyses'}
                      </p>
                    </div>
                    {selectedJdId === jdItem.jd_id && (
                      <span className="text-indigo-500 text-base flex-shrink-0">✓</span>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              Resumes{' '}
              <span className="text-slate-400 font-normal">(PDF, DOCX, DOC, RTF, TXT — up to 10 files)</span>
            </label>

            <div
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
                isDragging
                  ? 'border-indigo-400 bg-indigo-50'
                  : 'border-slate-300 hover:border-indigo-300 bg-slate-50 hover:bg-indigo-50'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.docx,.doc,.rtf,.txt"
                className="hidden"
                onChange={(e) => addFiles(e.target.files)}
              />
              <div className="text-4xl mb-2">📄</div>
              <p className="text-slate-600 font-medium">Drop files here or click to browse</p>
              <p className="text-slate-400 text-xs mt-1">PDF · DOCX · DOC · RTF · TXT · max 10 files</p>
            </div>

            {files.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3">
                {files.map((f) => (
                  <div
                    key={f.name}
                    className="flex items-center gap-1.5 bg-white border border-slate-200 rounded-lg px-3 py-1.5 text-sm text-slate-700 shadow-sm"
                  >
                    <span>
                      {/\.pdf$/i.test(f.name) ? '📕' : /\.txt$/i.test(f.name) ? '📄' : '📘'}
                    </span>
                    <span className="max-w-[160px] truncate">{f.name}</span>
                    <button
                      onClick={(e) => { e.stopPropagation(); removeFile(f.name) }}
                      className="ml-1 text-slate-400 hover:text-red-500 font-bold text-xs"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">
              {error.message}
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={!canAnalyze}
            className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold text-sm hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isPending ? 'Analyzing…' : `Analyze ${files.length > 0 ? `${files.length} Resume${files.length > 1 ? 's' : ''}` : 'Resumes'}`}
          </button>
        </div>
      )}

      {/* ── Loading progress ── */}
      {isPending && (
        <div className="mt-8 bg-white border border-slate-200 rounded-xl p-10 text-center shadow-sm">
          <div className="text-4xl mb-4 inline-block animate-spin">⚙️</div>
          <h3 className="text-lg font-semibold text-slate-700 mb-6">Processing your resumes…</h3>
          <div className="space-y-3 max-w-xs mx-auto text-left">
            {STEPS.map((label, i) => (
              <div key={label} className="flex items-center gap-3">
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                    i < step
                      ? 'bg-emerald-500 text-white'
                      : i === step
                        ? 'bg-indigo-500 text-white animate-pulse'
                        : 'bg-slate-200 text-slate-400'
                  }`}
                >
                  {i < step ? '✓' : i + 1}
                </div>
                <span
                  className={`text-sm ${i <= step ? 'text-slate-800 font-medium' : 'text-slate-400'}`}
                >
                  {label}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Results ── */}
      {session && !isPending && (
        <div>
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-semibold text-slate-700">
              {session.candidate_count} candidate{session.candidate_count !== 1 ? 's' : ''} ranked
            </h2>
            <button onClick={resetAll} className="text-sm text-indigo-600 hover:underline font-medium">
              ← New Analysis
            </button>
          </div>

          {/* JD summary card */}
          <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4 mb-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:gap-6">
              <div className="flex-shrink-0">
                <h3 className="font-semibold text-indigo-900 text-base">{session.job_title}</h3>
                <div className="flex flex-wrap gap-3 mt-1 text-xs text-indigo-700">
                  {session.jd_summary.role_level && (
                    <span>Level: <strong>{session.jd_summary.role_level}</strong></span>
                  )}
                  {session.jd_summary.domain && (
                    <span>Domain: <strong>{session.jd_summary.domain}</strong></span>
                  )}
                  {session.jd_summary.years_required && (
                    <span><strong>{session.jd_summary.years_required}+</strong> yrs required</span>
                  )}
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-indigo-500 uppercase tracking-wide mb-1.5">
                  Required Skills ({session.jd_summary.required_skills.length})
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {session.jd_summary.required_skills.slice(0, 25).map((s) => (
                    <SkillBadge key={s} skill={s} variant="matched" />
                  ))}
                  {session.jd_summary.required_skills.length > 25 && (
                    <span className="text-xs text-indigo-400 self-center">
                      +{session.jd_summary.required_skills.length - 25} more
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Candidate cards */}
          <div className="space-y-4">
            {session.candidates.map((c, i) => (
              <CandidateCard key={c.candidate_id} candidate={c} rank={i + 1} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
