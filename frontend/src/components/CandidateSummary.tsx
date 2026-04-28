import type { CandidateSummary } from '../types'

interface Props {
  summary: CandidateSummary
}

export default function CandidateSummaryPanel({ summary }: Props) {
  return (
    <div className="border-t border-slate-100 bg-slate-50 px-5 py-5 space-y-5">

      {/* Overview prose */}
      <div>
        <SectionLabel>Candidate Overview</SectionLabel>
        <p className="text-sm text-slate-700 leading-relaxed mt-1">{summary.overview}</p>
      </div>

      {/* Core Capabilities */}
      {summary.core_capabilities.length > 0 && (
        <div>
          <SectionLabel>Core Capabilities</SectionLabel>
          <div className="flex flex-wrap gap-1.5 mt-1">
            {summary.core_capabilities.map((cap) => (
              <span
                key={cap}
                className="inline-block bg-indigo-100 text-indigo-800 text-xs font-medium px-2.5 py-1 rounded-full"
              >
                {cap}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* 2-column grid: Education | Certifications */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        {/* Education */}
        <div>
          <SectionLabel icon="🎓">Education</SectionLabel>
          {summary.education.length > 0 ? (
            <ul className="mt-1 space-y-1.5">
              {summary.education.map((e, i) => (
                <li key={i} className="text-sm">
                  <span className="font-medium text-slate-800">{e.degree}</span>
                  {e.field && (
                    <span className="text-slate-500"> — {e.field}</span>
                  )}
                  {e.year && (
                    <span className="text-slate-400 text-xs ml-1">({e.year})</span>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-slate-400 mt-1">Not detected</p>
          )}
        </div>

        {/* Certifications */}
        <div>
          <SectionLabel icon="🏅">Certifications</SectionLabel>
          {summary.certifications.length > 0 ? (
            <ul className="mt-1 space-y-1">
              {summary.certifications.map((cert) => (
                <li key={cert} className="text-sm text-slate-700 flex items-start gap-1.5">
                  <span className="text-amber-500 mt-0.5 flex-shrink-0">✦</span>
                  {cert}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-slate-400 mt-1">None detected</p>
          )}
        </div>
      </div>

      {/* Strengths & Gaps */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        {summary.strengths.length > 0 && (
          <div>
            <SectionLabel icon="💪">Strengths</SectionLabel>
            <ul className="mt-1 space-y-1">
              {summary.strengths.map((s) => (
                <li key={s} className="flex items-start gap-2 text-sm text-slate-700">
                  <span className="text-emerald-500 font-bold flex-shrink-0">✓</span>
                  {s}
                </li>
              ))}
            </ul>
          </div>
        )}
        {summary.gaps.length > 0 && (
          <div>
            <SectionLabel icon="⚠️">Skill Gaps</SectionLabel>
            <ul className="mt-1 space-y-1">
              {summary.gaps.map((g) => (
                <li key={g} className="flex items-start gap-2 text-sm text-slate-700">
                  <span className="text-red-400 font-bold flex-shrink-0">✗</span>
                  {g}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

function SectionLabel({ children, icon }: { children: React.ReactNode; icon?: string }) {
  return (
    <h5 className="text-xs font-semibold text-slate-500 uppercase tracking-wide flex items-center gap-1">
      {icon && <span>{icon}</span>}
      {children}
    </h5>
  )
}
