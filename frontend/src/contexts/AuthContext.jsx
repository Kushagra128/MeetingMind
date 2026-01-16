import React, { createContext, useState, useContext, useEffect } from 'react'
import axios from 'axios'

// Configure axios defaults - use Vite proxy, so no baseURL needed
axios.defaults.headers.common['Content-Type'] = 'application/json'

// Add request interceptor to include token in all requests
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      // Ensure token is properly formatted
      const cleanToken = token.trim()
      config.headers.Authorization = `Bearer ${cleanToken}`
      console.log('Adding token to request:', config.url, cleanToken.substring(0, 20) + '...')
    } else {
      console.log('No token found for request:', config.url)
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    // Set up axios interceptor for token
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchUser = async () => {
    try {
      if (!token) {
        setLoading(false)
        return
      }
      
      const response = await axios.get('/api/auth/me')
      setUser(response.data)
    } catch (error) {
      console.error('Error fetching user:', error)
      if (error.response?.status === 401 || error.response?.status === 422) {
        logout()
      }
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    try {
      const response = await axios.post('/api/auth/login', {
        username,
        password
      })
      const { access_token, user } = response.data
      
      if (!access_token) {
        return {
          success: false,
          error: 'No token received from server'
        }
      }
      
      setToken(access_token)
      setUser(user)
      localStorage.setItem('token', access_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      return {
        success: false,
        error: error.response?.data?.error || 'Login failed'
      }
    }
  }

  const register = async (username, email, password) => {
    try {
      const response = await axios.post('/api/auth/register', {
        username,
        email,
        password
      })
      const { access_token, user } = response.data
      
      if (!access_token) {
        return {
          success: false,
          error: 'No token received from server'
        }
      }
      
      setToken(access_token)
      setUser(user)
      localStorage.setItem('token', access_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      return { success: true }
    } catch (error) {
      console.error('Registration error:', error)
      return {
        success: false,
        error: error.response?.data?.error || 'Registration failed'
      }
    }
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
  }

  const value = {
    user,
    login,
    register,
    logout,
    loading
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

