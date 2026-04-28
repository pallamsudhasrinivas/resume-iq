import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import AnalyzePage from './pages/AnalyzePage'
import DashboardPage from './pages/DashboardPage'
import HistoryPage from './pages/HistoryPage'
import JDLibraryPage from './pages/JDLibraryPage'
import SessionDetailPage from './pages/SessionDetailPage'

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-slate-50">
        <Sidebar />
        <main className="flex-1 p-8 overflow-auto min-w-0">
          <Routes>
            <Route path="/"              element={<AnalyzePage />} />
            <Route path="/dashboard"     element={<DashboardPage />} />
            <Route path="/history"       element={<HistoryPage />} />
            <Route path="/jd-library"    element={<JDLibraryPage />} />
            <Route path="/sessions/:id"  element={<SessionDetailPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
