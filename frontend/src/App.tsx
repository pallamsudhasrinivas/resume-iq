import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Sidebar from './components/Sidebar'
import AnalyzePage from './pages/AnalyzePage'
import DashboardPage from './pages/DashboardPage'
import HistoryPage from './pages/HistoryPage'
import JDLibraryPage from './pages/JDLibraryPage'
import LoginPage from './pages/LoginPage'
import SessionDetailPage from './pages/SessionDetailPage'

function AppShell() {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <main className="flex-1 p-8 overflow-auto min-w-0">
        <Routes>
          <Route path="/"             element={<AnalyzePage />} />
          <Route path="/dashboard"    element={<DashboardPage />} />
          <Route path="/history"      element={<HistoryPage />} />
          <Route path="/jd-library"   element={<JDLibraryPage />} />
          <Route path="/sessions/:id" element={<SessionDetailPage />} />
          <Route path="*"             element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <AppShell />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
