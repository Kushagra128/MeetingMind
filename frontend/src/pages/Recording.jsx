import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import axios from 'axios'
import { Mic, Square, ArrowLeft, Loader } from 'lucide-react'

const Recording = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [isRecording, setIsRecording] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [transcript, setTranscript] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const transcriptIntervalRef = useRef(null)

  useEffect(() => {
    return () => {
      if (transcriptIntervalRef.current) {
        clearInterval(transcriptIntervalRef.current)
        transcriptIntervalRef.current = null
      }
    }
  }, [])

  // ⭐ NEW: Ask browser for mic permission BEFORE backend starts recording
  const requestMicPermission = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      console.log("Microphone permission granted")

      // Stop stream because backend will handle actual recording
      stream.getTracks().forEach(track => track.stop())
      return true
    } catch (err) {
      console.error("Mic permission denied:", err)
      alert("Microphone access is required to record audio.")
      return false
    }
  }

  const startRecording = async () => {
    try {
      setLoading(true)
      setError('')

      // ✔ FIRST: Browser permission
      const allowed = await requestMicPermission()
      if (!allowed) {
        setLoading(false)
        return
      }

      // ✔ THEN: Backend starts recording
      const response = await axios.post('/api/recordings/start', {
        title: `Recording ${new Date().toLocaleString()}`
      })

      setSessionId(response.data.session_id)
      setIsRecording(true)
      setLoading(false)

      // Start polling for live transcript
      transcriptIntervalRef.current = setInterval(fetchTranscript, 2000)
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to start recording')
      setLoading(false)
    }
  }

  const stopRecording = async () => {
    if (loading || !sessionId) return

    try {
      if (transcriptIntervalRef.current) {
        clearInterval(transcriptIntervalRef.current)
        transcriptIntervalRef.current = null
      }

      setLoading(true)
      setIsRecording(false)

      const response = await axios.post(`/api/recordings/${sessionId}/stop`)

      if (response.data.recording?.id) {
        navigate(`/recording/${response.data.recording.id}`)
      } else {
        navigate('/dashboard')
      }
    } catch (error) {
      console.error('Stop recording error:', error)
      setError(error.response?.data?.error || 'Failed to stop recording')
      setLoading(false)
      navigate('/dashboard')
    }
  }

  const fetchTranscript = async () => {
    if (!sessionId) return

    try {
      const response = await axios.get(`/api/recordings/${sessionId}/transcript`)
      if (response.data.transcript) {
        const fullText = response.data.transcript.full_text || ''
        setTranscript(fullText)
      }
    } catch (error) {
      console.error('Error fetching transcript:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back to Dashboard</span>
            </button>
            <h1 className="text-2xl font-bold text-gray-900">New Recording</h1>
            <div className="w-32"></div>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <div
              className={`inline-flex items-center justify-center w-32 h-32 rounded-full mb-6 ${
                isRecording ? 'bg-red-100 animate-pulse' : 'bg-gray-100'
              }`}
            >
              {isRecording ? (
                <Mic className="w-16 h-16 text-red-600" />
              ) : (
                <Mic className="w-16 h-16 text-gray-400" />
              )}
            </div>

            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              {isRecording ? 'Recording in Progress...' : 'Ready to Record'}
            </h2>
            <p className="text-gray-600">
              {isRecording
                ? 'Speak clearly into your microphone. Click stop when finished.'
                : 'Click the button below to start recording your meeting'}
            </p>
          </div>

          <div className="flex justify-center space-x-4 mb-8">
            {!isRecording ? (
              <button
                onClick={startRecording}
                disabled={loading}
                className="flex items-center space-x-2 bg-primary-600 text-white px-8 py-4 rounded-lg hover:bg-primary-700 disabled:opacity-50 transition text-lg font-medium"
              >
                {loading ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    <span>Starting...</span>
                  </>
                ) : (
                  <>
                    <Mic className="w-5 h-5" />
                    <span>Start Recording</span>
                  </>
                )}
              </button>
            ) : (
              <button
                onClick={stopRecording}
                disabled={loading}
                className="flex items-center space-x-2 bg-red-600 text-white px-8 py-4 rounded-lg hover:bg-red-700 disabled:opacity-50 transition text-lg font-medium"
              >
                {loading ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    <span>Stopping...</span>
                  </>
                ) : (
                  <>
                    <Square className="w-5 h-5" />
                    <span>Stop Recording</span>
                  </>
                )}
              </button>
            )}
          </div>

          {isRecording && (
            <div className="mt-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Live Transcript
              </h3>
              <div className="bg-gray-50 rounded-lg p-6 min-h-[300px] max-h-[500px] overflow-y-auto">
                {transcript ? (
                  <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">
                    {transcript}
                  </p>
                ) : (
                  <p className="text-gray-400 italic">
                    Waiting for speech... Start speaking to see transcription here.
                  </p>
                )}
              </div>
              <p className="text-sm text-gray-500 mt-2">
                Transcript updates in real-time as you speak
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default Recording
