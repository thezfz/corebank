import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { AxiosError } from 'axios'
import apiClient from '../api/client'
import type { User, UserLogin, UserCreate, Token } from '../types/api'

interface PasswordValidationError {
  message: string
  issues: string[]
}

interface ValidationError {
  detail: string | PasswordValidationError
  errors?: Array<{
    type: string
    loc: string[]
    msg: string
    input?: string
  }>
}

// Helper function to parse registration errors
function parseRegistrationError(error: unknown): string[] {
  if (!error || typeof error !== 'object') {
    return ['注册失败，请重试']
  }

  const axiosError = error as AxiosError<ValidationError>

  if (!axiosError.response?.data) {
    return ['网络错误，请检查连接后重试']
  }

  const data = axiosError.response.data

  // Handle password validation errors (400 status)
  if (axiosError.response.status === 400 && typeof data.detail === 'object' && data.detail.issues) {
    return data.detail.issues
  }

  // Handle validation errors (422 status)
  if (axiosError.response.status === 422 && data.errors) {
    return data.errors.map(err => err.msg)
  }

  // Handle other specific errors
  if (typeof data.detail === 'string') {
    return [data.detail]
  }

  return ['注册失败，请重试']
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const queryClient = useQueryClient()

  // Check if user is authenticated on mount
  useEffect(() => {
    let isMounted = true

    const checkAuth = async () => {
      const storedToken = localStorage.getItem('auth_token')
      if (storedToken) {
        try {
          // Validate token by getting user info
          const userInfo = await apiClient.getCurrentUser()
          if (isMounted) {
            setUser(userInfo)
          }
        } catch (error) {
          console.error('Token validation failed:', error)
          if (isMounted) {
            // Clear invalid token
            apiClient.logout()
          }
        }
      }
      if (isMounted) {
        setIsLoading(false)
      }
    }

    checkAuth()

    return () => {
      isMounted = false
    }
  }, [])

  const loginMutation = useMutation({
    mutationFn: (credentials: UserLogin) => apiClient.login(credentials),
    onSuccess: async (_token: Token) => {
      try {
        console.log('Login API success, getting user info...')
        // Get actual user information after successful login
        const userInfo = await apiClient.getCurrentUser()
        console.log('User info received:', userInfo)

        // Set user state
        setUser(userInfo)

        // Invalidate queries after user state is set
        queryClient.invalidateQueries()

        console.log('User state set, forcing navigation to dashboard')
        // Force navigation using window.location to ensure it works
        setTimeout(() => {
          window.location.href = '/dashboard'
        }, 100)

      } catch (error) {
        console.error('Failed to get user info after login:', error)
        // Fallback: create a basic user object
        const basicUser: User = {
          id: 'unknown',
          username: 'user',
          created_at: new Date().toISOString()
        }
        console.log('Setting fallback user:', basicUser)
        setUser(basicUser)

        // Force navigation even with fallback user
        setTimeout(() => {
          window.location.href = '/dashboard'
        }, 100)
      }
    },
    onError: (error) => {
      console.error('Login mutation error:', error)
      // Don't navigate on error - stay on login page to show error message
    }
  })

  const registerMutation = useMutation({
    mutationFn: (userData: UserCreate) => apiClient.register(userData),
    onSuccess: (user: User) => {
      console.log('User registered:', user)
      // Note: We don't auto-login after registration for security reasons
      // User should manually login with their credentials
    },
  })

  const logout = () => {
    try {
      console.log('Logout: starting logout process')

      // 清除 API 客户端状态
      apiClient.logout()
      console.log('Logout: API client cleared')

      // 清除所有查询缓存
      queryClient.clear()
      console.log('Logout: query cache cleared')

      // 清除所有本地存储
      localStorage.clear()
      console.log('Logout: localStorage cleared')

      // 清除用户状态
      setUser(null)
      console.log('Logout: user state set to null')

      console.log('Logout: forcing navigation to login page')
      // Force navigation using window.location to ensure it works immediately
      setTimeout(() => {
        window.location.href = '/login'
      }, 100)

    } catch (error) {
      console.error('Logout error:', error)
      // Force page reload on error as fallback
      setTimeout(() => {
        window.location.href = '/login'
      }, 100)
    }
  }

  return {
    user,
    isLoading,
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout,
    isLoginLoading: loginMutation.isPending,
    isRegisterLoading: registerMutation.isPending,
    loginError: loginMutation.error,
    registerError: registerMutation.error,
    registerErrorMessages: registerMutation.error ? parseRegistrationError(registerMutation.error) : [],
  }
}
