import { Link, useParams } from 'react-router-dom'
import { useSession } from '../hooks/useSessions'
import CandidateCard from '../components/CandidateCard'
import SkillBadge from '../components/SkillBadge'

export default function SessionDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: session, isLoading, error } = useSession(id ?? '')

  if (isLoading) {
    return <div className="text-center text-slate-400 py-20">Loading session…</div>
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">
        {error.message}
      </div>
    )
  }

  if (!session) return null

  return (
    <div className="max-w-5xl mx-auto">
      <Link
        to="/history"
        className="inline-flex items-center gap-1 text-sm text-indigo-600 hover:underline mb-4 font-medium"
      >
        ← History
      </Link>

      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">{session.job_title}</h1>
        <p className="text-slate-500 text-sm mt-1">
          {session.candidate_count} candidate{session.candidate_count !== 1 ? 's' : ''} · Avg
          score {session.avg_score}% ·{' '}
          {new Date(session.created_at).toLocaleDateString('en-US', {
            month: 'long',
            day: 'numeric',
            year: 'numeric',
          })}
        </p>
      </div>

      {/* JD summary */}
      <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4 mb-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:gap-6">
          <div className="flex-shrink-0">
            <div className="flex flex-wrap gap-3 text-xs text-indigo-700">
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

      {/* Candidates */}
      <div className="space-y-4">
        {session.candidates.map((c, i) => (
          <CandidateCard key={c.candidate_id} candidate={c} rank={i + 1} />
        ))}
      </div>
    </div>
  )
}
