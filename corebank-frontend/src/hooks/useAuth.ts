import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../api/client'
import type { User, UserLogin, UserCreate, Token } from '../types/api'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const queryClient = useQueryClient()

  // Check if user is authenticated on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token')
    if (storedToken) {
      // In a real app, you'd validate the token with the server
      // For now, we'll assume it's valid if it exists
      setIsLoading(false)
    } else {
      setIsLoading(false)
    }
  }, [])

  const loginMutation = useMutation({
    mutationFn: (credentials: UserLogin) => apiClient.login(credentials),
    onSuccess: (_token: Token) => {
      // In a real app, you'd decode the JWT to get user info
      // For now, we'll create a mock user object
      const mockUser: User = {
        id: 'user-id',
        username: 'user',
        created_at: new Date().toISOString()
      }
      setUser(mockUser)
      queryClient.invalidateQueries()
    },
  })

  const registerMutation = useMutation({
    mutationFn: (userData: UserCreate) => apiClient.register(userData),
    onSuccess: (user: User) => {
      // Auto-login after registration would require additional API call
      console.log('User registered:', user)
    },
  })

  const logout = () => {
    apiClient.logout()
    setUser(null)
    queryClient.clear()
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
  }
}
