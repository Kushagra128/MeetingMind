import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Recording from './pages/Recording'
import RecordingDetail from './pages/RecordingDetail'
import Upload from './pages/Upload'
import PrivateRoute from './components/PrivateRoute'
import MicTest from './pages/MicTest'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/recording"
            element={
              <PrivateRoute>
                <Recording />
              </PrivateRoute>
            }
          />
          <Route
            path="/upload"
            element={
              <PrivateRoute>
                <Upload />
              </PrivateRoute>
            }
          />
          <Route
            path="/recording/:id"
            element={
              <PrivateRoute>
                <RecordingDetail />
              </PrivateRoute>
            }
          />
          <Route path="/mic-test" element={<MicTest />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App



