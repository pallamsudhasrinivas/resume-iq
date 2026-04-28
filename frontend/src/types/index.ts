export interface SubScores {
  skills: number
  experience: number
  domain: number
  bonus: number
}

export interface EducationEntry {
  degree: string
  field?: string
  year?: string
}

export interface CandidateSummary {
  overview: string
  core_capabilities: string[]
  education: EducationEntry[]
  certifications: string[]
  strengths: string[]
  gaps: string[]
}

export interface Candidate {
  candidate_id: string
  filename: string
  candidate_name: string
  email: string
  overall_score: number
  sub_scores: SubScores
  matched_skills: string[]
  missing_skills: string[]
  bonus_skills: string[]
  years_experience: number | null
  recommendation: 'Strong Match' | 'Good Match' | 'Partial Match' | 'Poor Match'
  summary: CandidateSummary
}

export interface JDSummary {
  required_skills: string[]
  years_required: number | null
  role_level: string | null
  domain: string | null
}

export interface Session {
  session_id: string
  job_title: string
  created_at: string
  jd_summary: JDSummary
  candidates: Candidate[]
  candidate_count: number
  avg_score: number
  top_candidate: string | null
}

export interface SessionIndex {
  session_id: string
  job_title: string
  created_at: string
  candidate_count: number
  avg_score: number
  top_candidate: string | null
  jd_id?: string
}

export interface JDIndex {
  jd_id: string
  title: string
  created_at: string
  session_count: number
}

export interface JDEntry {
  jd_id: string
  title: string
  text: string
  created_at: string
  jd_summary: JDSummary
  session_count: number
}

export interface JDDetail extends JDEntry {
  sessions: SessionIndex[]
}

export interface JDCandidate extends Candidate {
  session_id: string
  session_date: string
}

export interface JDCandidatesResponse {
  candidates: JDCandidate[]
  total: number
}

export interface JDListResponse {
  jds: JDIndex[]
  total: number
  limit: number
  offset: number
}

export interface SessionListResponse {
  sessions: SessionIndex[]
  total: number
  limit: number
  offset: number
}

export interface ScoreDistribution {
  strong: number
  good: number
  partial: number
  poor: number
}

export interface TopMissingSkill {
  skill: string
  count: number
}

export interface DashboardStats {
  total_sessions: number
  total_candidates: number
  avg_score: number
  sessions_this_month: number
  score_distribution: ScoreDistribution
  top_missing_skills: TopMissingSkill[]
}
