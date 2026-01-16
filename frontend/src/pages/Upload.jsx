import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import axios from 'axios'
import { Upload as UploadIcon, ArrowLeft, FileAudio, FileText, File, Loader, CheckCircle } from 'lucide-react'

const Upload = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [uploadType, setUploadType] = useState('audio') // 'audio' or 'text'
  const [selectedFile, setSelectedFile] = useState(null)
  const [title, setTitle] = useState('')
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      setSelectedFile(file)
      setError('')
      // Auto-fill title with filename (without extension)
      if (!title) {
        const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '')
        setTitle(nameWithoutExt)
      }
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file')
      return
    }

    if (!title.trim()) {
      setError('Please enter a title')
      return
    }

    try {
      setUploading(true)
      setError('')
      setProgress(0)

      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('title', title)

      const endpoint = uploadType === 'audio' ? '/api/upload/audio' : '/api/upload/text'

      const response = await axios.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          setProgress(percentCompleted)
        },
      })

      setSuccess(true)
      setProgress(100)

      // Redirect to recording detail after 2 seconds
      setTimeout(() => {
        navigate(`/recording/${response.data.recording_id}`)
      }, 2000)

    } catch (error) {
      console.error('Upload error:', error)
      setError(error.response?.data?.error || 'Failed to upload file')
      setUploading(false)
    }
  }

  const getAcceptedFileTypes = () => {
    if (uploadType === 'audio') {
      return '.wav,.mp3,.ogg,.flac,.m4a,.webm'
    } else {
      return '.pdf,.txt'
    }
  }

  const getFileIcon = () => {
    if (!selectedFile) return <File className="w-16 h-16 text-gray-400" />
    
    const ext = selectedFile.name.split('.').pop().toLowerCase()
    
    if (['wav', 'mp3', 'ogg', 'flac', 'm4a', 'webm'].includes(ext)) {
      return <FileAudio className="w-16 h-16 text-blue-500" />
    } else if (ext === 'pdf') {
      return <File className="w-16 h-16 text-red-500" />
    } else {
      return <FileText className="w-16 h-16 text-green-500" />
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
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
            <h1 className="text-2xl font-bold text-gray-900">Upload File</h1>
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

        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded flex items-center">
            <CheckCircle className="w-5 h-5 mr-2" />
            <span>File uploaded successfully! Redirecting...</span>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Upload Type Selection */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              What would you like to upload?
            </label>
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => {
                  setUploadType('audio')
                  setSelectedFile(null)
                  setError('')
                }}
                className={`p-4 border-2 rounded-lg transition ${
                  uploadType === 'audio'
                    ? 'border-primary-600 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <FileAudio className={`w-8 h-8 mx-auto mb-2 ${
                  uploadType === 'audio' ? 'text-primary-600' : 'text-gray-400'
                }`} />
                <div className="text-center">
                  <div className="font-medium text-gray-900">Audio File</div>
                  <div className="text-xs text-gray-500 mt-1">
                    WAV, MP3, OGG, FLAC, M4A
                  </div>
                </div>
              </button>

              <button
                onClick={() => {
                  setUploadType('text')
                  setSelectedFile(null)
                  setError('')
                }}
                className={`p-4 border-2 rounded-lg transition ${
                  uploadType === 'text'
                    ? 'border-primary-600 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <FileText className={`w-8 h-8 mx-auto mb-2 ${
                  uploadType === 'text' ? 'text-primary-600' : 'text-gray-400'
                }`} />
                <div className="text-center">
                  <div className="font-medium text-gray-900">Text/PDF File</div>
                  <div className="text-xs text-gray-500 mt-1">
                    PDF, TXT
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* Title Input */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter a title for this recording"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              disabled={uploading}
            />
          </div>

          {/* File Upload Area */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {uploadType === 'audio' ? 'Audio File' : 'Text/PDF File'}
            </label>
            
            {!selectedFile ? (
              <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <UploadIcon className="w-12 h-12 text-gray-400 mb-4" />
                  <p className="mb-2 text-sm text-gray-500">
                    <span className="font-semibold">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-xs text-gray-500">
                    {uploadType === 'audio' 
                      ? 'WAV, MP3, OGG, FLAC, M4A, WEBM (Max 500MB)'
                      : 'PDF or TXT files (Max 500MB)'}
                  </p>
                </div>
                <input
                  type="file"
                  className="hidden"
                  accept={getAcceptedFileTypes()}
                  onChange={handleFileSelect}
                  disabled={uploading}
                />
              </label>
            ) : (
              <div className="border-2 border-gray-300 rounded-lg p-6">
                <div className="flex items-center space-x-4">
                  {getFileIcon()}
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
                    <p className="text-xs text-gray-500">{formatFileSize(selectedFile.size)}</p>
                  </div>
                  {!uploading && (
                    <button
                      onClick={() => setSelectedFile(null)}
                      className="text-sm text-red-600 hover:text-red-700"
                    >
                      Remove
                    </button>
                  )}
                </div>

                {uploading && (
                  <div className="mt-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-600">
                        {progress < 100 ? 'Uploading...' : 'Processing...'}
                      </span>
                      <span className="text-sm font-medium text-gray-900">{progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${progress}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Info Box */}
          <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-blue-900 mb-2">
              {uploadType === 'audio' ? 'Audio Processing' : 'Text Processing'}
            </h3>
            <ul className="text-sm text-blue-700 space-y-1">
              {uploadType === 'audio' ? (
                <>
                  <li>• Your audio will be transcribed using offline speech recognition</li>
                  <li>• A summary will be automatically generated</li>
                  <li>• Both transcript and summary PDFs will be created</li>
                  <li>• Processing may take a few minutes depending on file size</li>
                </>
              ) : (
                <>
                  <li>• Text will be extracted from your file</li>
                  <li>• A summary will be automatically generated</li>
                  <li>• Both transcript and summary PDFs will be created</li>
                  <li>• Processing is usually quick</li>
                </>
              )}
            </ul>
          </div>

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={!selectedFile || !title.trim() || uploading}
            className="w-full flex items-center justify-center space-x-2 bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition text-lg font-medium"
          >
            {uploading ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <UploadIcon className="w-5 h-5" />
                <span>Upload and Process</span>
              </>
            )}
          </button>
        </div>
      </main>
    </div>
  )
}

export default Upload
