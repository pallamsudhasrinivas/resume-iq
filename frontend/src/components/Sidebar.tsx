import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'New Analysis', icon: '⊕' },
  { to: '/dashboard', label: 'Dashboard', icon: '◉' },
  { to: '/history', label: 'History', icon: '☰' },
  { to: '/jd-library', label: 'JD Library', icon: '📋' },
]

export default function Sidebar() {
  return (
    <aside className="w-[220px] min-h-screen bg-slate-900 text-white flex flex-col flex-shrink-0">
      <div className="p-5 border-b border-slate-700">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🎯</span>
          <span className="text-xl font-bold tracking-tight">Resume IQ</span>
        </div>
        <p className="text-slate-400 text-xs mt-1">Smart candidate screening</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`
            }
          >
            <span className="text-base">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-700">
        <p className="text-slate-500 text-xs">Resume IQ v1.0</p>
      </div>
    </aside>
  )
}
