import { useState } from 'react'
import type { Candidate } from '../types'
import ScoreCircle from './ScoreCircle'
import SkillBadge from './SkillBadge'
import CandidateSummaryPanel from './CandidateSummary'

interface Props {
  candidate: Candidate
  rank: number
}

const REC_CLASSES: Record<string, string> = {
  'Strong Match':  'bg-emerald-50 text-emerald-700 border border-emerald-200',
  'Good Match':    'bg-blue-50 text-blue-700 border border-blue-200',
  'Partial Match': 'bg-amber-50 text-amber-700 border border-amber-200',
  'Poor Match':    'bg-red-50 text-red-700 border border-red-200',
}

const SUB_SCORE_BARS = [
  { key: 'skills',     label: 'Skills',      color: 'bg-indigo-500' },
  { key: 'experience', label: 'Experience',  color: 'bg-sky-500' },
  { key: 'domain',     label: 'Domain',      color: 'bg-violet-500' },
  { key: 'bonus',      label: 'Bonus',       color: 'bg-pink-400' },
] as const

export default function CandidateCard({ candidate, rank }: Props) {
  const [summaryOpen, setSummaryOpen] = useState(rank === 1)
  const recClass = REC_CLASSES[candidate.recommendation] ?? ''

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">

      {/* ── Header ── */}
      <div className="p-5 flex items-start gap-4 border-b border-slate-100">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-sm font-bold text-slate-500">
          #{rank}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 flex-wrap">
            <h3 className="text-lg font-semibold text-slate-800">{candidate.candidate_name}</h3>
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${recClass}`}>
              {candidate.recommendation}
            </span>
          </div>
          <div className="text-sm text-slate-500 mt-0.5 flex flex-wrap gap-x-3 gap-y-0.5">
            {candidate.email && <span>{candidate.email}</span>}
            <span className="text-slate-300">·</span>
            <span className="truncate max-w-[200px]">{candidate.filename}</span>
            {candidate.years_experience !== null && (
              <>
                <span className="text-slate-300">·</span>
                <span>{candidate.years_experience} yrs exp</span>
              </>
            )}
          </div>
          {/* Core capabilities mini-row */}
          {candidate.summary.core_capabilities.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-2">
              {candidate.summary.core_capabilities.slice(0, 6).map((cap) => (
                <span
                  key={cap}
                  className="inline-block bg-slate-100 text-slate-600 text-xs px-2 py-0.5 rounded-full"
                >
                  {cap}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="flex-shrink-0">
          <ScoreCircle score={candidate.overall_score} size="lg" />
        </div>
      </div>

      {/* ── Sub-score bars ── */}
      <div className="px-5 py-4 border-b border-slate-100">
        <div className="grid grid-cols-2 gap-x-6 gap-y-3">
          {SUB_SCORE_BARS.map(({ key, label, color }) => (
            <div key={key}>
              <div className="flex justify-between text-xs text-slate-500 mb-1">
                <span>{label}</span>
                <span className="font-semibold text-slate-700">
                  {Math.round(candidate.sub_scores[key])}%
                </span>
              </div>
              <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className={`h-full ${color} rounded-full`}
                  style={{ width: `${candidate.sub_scores[key]}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Skills columns ── */}
      <div className="p-5 grid grid-cols-3 gap-5 border-b border-slate-100">
        <SkillColumn title="Matched" count={candidate.matched_skills.length} skills={candidate.matched_skills} variant="matched" />
        <SkillColumn title="Missing" count={candidate.missing_skills.length} skills={candidate.missing_skills} variant="missing" />
        <SkillColumn title="Bonus"   count={candidate.bonus_skills.length}   skills={candidate.bonus_skills}   variant="bonus" />
      </div>

      {/* ── Summary toggle ── */}
      <button
        onClick={() => setSummaryOpen((o) => !o)}
        className="w-full flex items-center justify-between px-5 py-3 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors"
      >
        <span className="flex items-center gap-2">
          <span>🧠</span>
          Candidate Profile &amp; Analysis
          {candidate.summary.certifications.length > 0 && (
            <span className="bg-amber-100 text-amber-700 text-xs px-1.5 py-0.5 rounded-full">
              {candidate.summary.certifications.length} cert{candidate.summary.certifications.length > 1 ? 's' : ''}
            </span>
          )}
          {candidate.summary.education.length > 0 && (
            <span className="bg-blue-100 text-blue-700 text-xs px-1.5 py-0.5 rounded-full">
              {candidate.summary.education[0].degree}
            </span>
          )}
        </span>
        <span className="text-slate-400 text-base">{summaryOpen ? '▲' : '▼'}</span>
      </button>

      {/* ── Summary panel ── */}
      {summaryOpen && <CandidateSummaryPanel summary={candidate.summary} />}
    </div>
  )
}

function SkillColumn({
  title, count, skills, variant,
}: {
  title: string
  count: number
  skills: string[]
  variant: 'matched' | 'missing' | 'bonus'
}) {
  return (
    <div>
      <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
        {title} ({count})
      </h4>
      <div className="flex flex-wrap gap-1.5">
        {skills.length > 0
          ? skills.map((s) => <SkillBadge key={s} skill={s} variant={variant} />)
          : <span className="text-xs text-slate-400">None</span>}
      </div>
    </div>
  )
}
