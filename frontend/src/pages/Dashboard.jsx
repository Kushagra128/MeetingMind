import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import axios from 'axios'
import { Mic, Plus, LogOut, FileText, Clock, Trash2, Download, Eye, Upload } from 'lucide-react'

const Dashboard = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [recordings, setRecordings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchRecordings()
  }, [])

  const fetchRecordings = async () => {
    try {
      const response = await axios.get('/api/recordings')
      setRecordings(response.data.recordings)
    } catch (error) {
      setError('Failed to load recordings')
      console.error('Error fetching recordings:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this recording?')) {
      return
    }

    try {
      await axios.delete(`/api/recordings/${id}`)
      fetchRecordings()
    } catch (error) {
      alert('Failed to delete recording')
      console.error('Error deleting recording:', error)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A'
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Mic className="w-8 h-8 text-primary-600" />
              <h1 className="text-2xl font-bold text-gray-900">Meeting Transcriber</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Welcome, {user?.username}</span>
              <button
                onClick={logout}
                className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:text-gray-900"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-2xl font-semibold text-gray-900">My Recordings</h2>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => navigate('/upload')}
              className="flex items-center space-x-2 bg-white border border-primary-600 text-primary-600 px-4 py-2 rounded-lg hover:bg-primary-50 transition"
            >
              <Upload className="w-5 h-5" />
              <span>Upload File</span>
            </button>
            <button
              onClick={() => navigate('/recording')}
              className="flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition"
            >
              <Mic className="w-5 h-5" />
              <span>New Recording</span>
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        ) : recordings.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No recordings yet</h3>
            <p className="text-gray-600 mb-6">Start your first recording to get started</p>
            <button
              onClick={() => navigate('/recording')}
              className="inline-flex items-center space-x-2 bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition"
            >
              <Plus className="w-5 h-5" />
              <span>Start Recording</span>
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recordings.map((recording) => (
              <div
                key={recording.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition cursor-pointer"
                onClick={() => navigate(`/recording/${recording.id}`)}
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 truncate">
                      {recording.title}
                    </h3>
                    <span className={`px-2 py-1 text-xs rounded ${
                      recording.status === 'completed' ? 'bg-green-100 text-green-800' :
                      recording.status === 'recording' ? 'bg-blue-100 text-blue-800' :
                      recording.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {recording.status}
                    </span>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center text-sm text-gray-600">
                      <Clock className="w-4 h-4 mr-2" />
                      <span>{formatDate(recording.created_at)}</span>
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <FileText className="w-4 h-4 mr-2" />
                      <span>Duration: {formatDuration(recording.duration)}</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 pt-4 border-t">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        navigate(`/recording/${recording.id}`)
                      }}
                      className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 text-sm text-primary-600 hover:bg-primary-50 rounded transition"
                    >
                      <Eye className="w-4 h-4" />
                      <span>View</span>
                    </button>
                    {recording.transcript_pdf_path && (
                      <a
                        href={`/api/recordings/${recording.id}/pdf/transcript`}
                        onClick={(e) => e.stopPropagation()}
                        download
                        className="flex items-center justify-center px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded transition"
                      >
                        <Download className="w-4 h-4" />
                      </a>
                    )}
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDelete(recording.id)
                      }}
                      className="flex items-center justify-center px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded transition"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

export default Dashboard



