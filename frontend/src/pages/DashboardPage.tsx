import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useDashboard } from '../hooks/useDashboard'
import StatCard from '../components/StatCard'

const PIE_COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
const PIE_LABELS = ['Strong Match', 'Good Match', 'Partial Match', 'Poor Match']

export default function DashboardPage() {
  const { data, isLoading, error } = useDashboard()

  if (isLoading) {
    return <div className="text-center text-slate-400 py-20">Loading dashboard…</div>
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">
        Failed to load dashboard: {error.message}
      </div>
    )
  }

  if (!data) return null

  const pieData = [
    { name: 'Strong Match', value: data.score_distribution.strong },
    { name: 'Good Match',   value: data.score_distribution.good },
    { name: 'Partial Match',value: data.score_distribution.partial },
    { name: 'Poor Match',   value: data.score_distribution.poor },
  ]

  const barData = data.top_missing_skills.map((s) => ({
    skill: s.skill.length > 22 ? s.skill.slice(0, 19) + '…' : s.skill,
    count: s.count,
  }))

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
        <p className="text-slate-500 text-sm mt-1">
          Aggregate statistics across all screening sessions.
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard title="Total Sessions"      value={data.total_sessions}      icon="📁" />
        <StatCard title="Total Candidates"    value={data.total_candidates}    icon="👥" />
        <StatCard title="Avg Score"           value={`${data.avg_score}%`}     icon="📊" />
        <StatCard title="Sessions This Month" value={data.sessions_this_month} icon="📅" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie chart */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Score Distribution</h2>
          {data.total_candidates === 0 ? (
            <div className="text-center text-slate-400 py-16">No candidates yet</div>
          ) : (
            <>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={95}
                    dataKey="value"
                    paddingAngle={2}
                  >
                    {pieData.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v: number) => [v, 'Candidates']} />
                </PieChart>
              </ResponsiveContainer>
              <div className="grid grid-cols-2 gap-2 mt-3">
                {PIE_LABELS.map((label, i) => (
                  <div key={label} className="flex items-center gap-2 text-sm">
                    <div
                      className="w-3 h-3 rounded-full flex-shrink-0"
                      style={{ backgroundColor: PIE_COLORS[i] }}
                    />
                    <span className="text-slate-600 truncate">{label}</span>
                    <span className="font-semibold text-slate-800 ml-auto">{pieData[i].value}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Bar chart */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Top 10 Missing Skills</h2>
          {barData.length === 0 ? (
            <div className="text-center text-slate-400 py-16">No data yet</div>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={barData}
                layout="vertical"
                margin={{ left: 8, right: 24, top: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="skill" tick={{ fontSize: 11 }} width={120} />
                <Tooltip />
                <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  )
}
