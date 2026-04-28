import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useSessions, useDeleteSession } from '../hooks/useSessions'

const PAGE_SIZE = 20

function scoreColor(score: number) {
  if (score >= 80) return 'text-emerald-600'
  if (score >= 60) return 'text-blue-600'
  if (score >= 40) return 'text-amber-600'
  return 'text-red-600'
}

export default function HistoryPage() {
  const [search, setSearch] = useState('')
  const [offset, setOffset] = useState(0)
  const [deleteId, setDeleteId] = useState<string | null>(null)

  const { data, isLoading, error } = useSessions({
    limit: PAGE_SIZE,
    offset,
    search: search || undefined,
  })
  const { mutate: deleteSession, isPending: isDeleting } = useDeleteSession()

  const confirmDelete = () => {
    if (!deleteId) return
    deleteSession(deleteId, { onSuccess: () => setDeleteId(null) })
  }

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-6 flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">History</h1>
          <p className="text-slate-500 text-sm mt-1">All past screening sessions.</p>
        </div>
        <input
          type="search"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setOffset(0) }}
          placeholder="Search by job title…"
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 w-56"
        />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm mb-4">
          {error.message}
        </div>
      )}

      {isLoading ? (
        <div className="text-center text-slate-400 py-20">Loading…</div>
      ) : !data || data.sessions.length === 0 ? (
        <div className="text-center py-24 text-slate-400">
          <div className="text-5xl mb-3">📭</div>
          <p className="font-medium">
            {search ? 'No sessions match your search.' : 'No sessions yet — start a new analysis!'}
          </p>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Job Title</th>
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Date</th>
                  <th className="text-center px-4 py-3 font-semibold text-slate-600"># Candidates</th>
                  <th className="text-center px-4 py-3 font-semibold text-slate-600">Avg Score</th>
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Top Candidate</th>
                  <th className="text-center px-4 py-3 font-semibold text-slate-600">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.sessions.map((s) => (
                  <tr key={s.session_id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-medium text-slate-800 max-w-[220px]">
                      <span className="block truncate">{s.job_title}</span>
                    </td>
                    <td className="px-4 py-3 text-slate-500 whitespace-nowrap">
                      {new Date(s.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 text-center text-slate-700">{s.candidate_count}</td>
                    <td className="px-4 py-3 text-center">
                      <span className={`font-semibold ${scoreColor(s.avg_score)}`}>
                        {s.avg_score}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-600 max-w-[160px]">
                      <span className="block truncate">{s.top_candidate ?? '—'}</span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <div className="flex items-center justify-center gap-3">
                        <Link
                          to={`/sessions/${s.session_id}`}
                          className="text-indigo-600 hover:underline text-xs font-semibold"
                        >
                          View
                        </Link>
                        <button
                          onClick={() => setDeleteId(s.session_id)}
                          className="text-red-500 hover:underline text-xs font-semibold"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {data.total > PAGE_SIZE && (
            <div className="flex items-center justify-between mt-4 text-sm text-slate-600">
              <span>
                Showing {offset + 1}–{Math.min(offset + PAGE_SIZE, data.total)} of {data.total}
              </span>
              <div className="flex gap-2">
                <button
                  disabled={offset === 0}
                  onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                  className="px-3 py-1.5 border border-slate-300 rounded-lg disabled:opacity-40 hover:bg-slate-50"
                >
                  Previous
                </button>
                <button
                  disabled={offset + PAGE_SIZE >= data.total}
                  onClick={() => setOffset(offset + PAGE_SIZE)}
                  className="px-3 py-1.5 border border-slate-300 rounded-lg disabled:opacity-40 hover:bg-slate-50"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Delete dialog */}
      {deleteId && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 shadow-2xl max-w-sm w-full">
            <h3 className="font-semibold text-slate-800 text-lg mb-2">Delete Session</h3>
            <p className="text-slate-500 text-sm mb-6">
              Are you sure? This action cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeleteId(null)}
                className="px-4 py-2 text-sm border border-slate-300 rounded-lg hover:bg-slate-50 font-medium"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                disabled={isDeleting}
                className="px-4 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 font-medium"
              >
                {isDeleting ? 'Deleting…' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
