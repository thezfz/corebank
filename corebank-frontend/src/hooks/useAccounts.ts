import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { AxiosError } from 'axios'
import apiClient from '../api/client'
import type { Account, AccountCreate, AccountSummary, ApiError } from '../types/api'

// Query keys
export const accountKeys = {
  all: ['accounts'] as const,
  lists: () => [...accountKeys.all, 'list'] as const,
  list: (filters: string) => [...accountKeys.lists(), { filters }] as const,
  details: () => [...accountKeys.all, 'detail'] as const,
  detail: (id: string) => [...accountKeys.details(), id] as const,
  summary: () => [...accountKeys.all, 'summary'] as const,
}

// Get all accounts for current user
export function useAccounts() {
  return useQuery({
    queryKey: accountKeys.lists(),
    queryFn: () => apiClient.getAccounts(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get account summary
export function useAccountSummary() {
  return useQuery({
    queryKey: accountKeys.summary(),
    queryFn: () => apiClient.getAccountSummary(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get specific account
export function useAccount(accountId: string) {
  return useQuery({
    queryKey: accountKeys.detail(accountId),
    queryFn: () => apiClient.getAccount(accountId),
    enabled: !!accountId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Create account mutation
export function useCreateAccount() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (accountData: AccountCreate) => apiClient.createAccount(accountData),
    onSuccess: (newAccount: Account) => {
      // Invalidate and refetch accounts list
      queryClient.invalidateQueries({ queryKey: accountKeys.lists() })
      queryClient.invalidateQueries({ queryKey: accountKeys.summary() })
      
      // Add the new account to the cache
      queryClient.setQueryData(accountKeys.detail(newAccount.id), newAccount)
      
      console.log('Account created successfully:', newAccount.account_number)
    },
    onError: (error: AxiosError<ApiError>) => {
      console.error('Failed to create account:', error)
    }
  })
}

// Helper function to parse account creation errors
export function parseAccountError(error: unknown): string[] {
  if (!error || typeof error !== 'object') {
    return ['创建账户失败，请重试']
  }

  const axiosError = error as AxiosError<ApiError>

  if (!axiosError.response?.data) {
    return ['网络错误，请检查连接后重试']
  }

  const data = axiosError.response.data

  // Handle validation errors (422 status)
  if (axiosError.response.status === 422 && data.errors) {
    return data.errors.map(err => err.message)
  }

  // Handle other specific errors
  if (typeof data.detail === 'string') {
    return [data.detail]
  }

  return ['创建账户失败，请重试']
}

// Custom hook for account operations
export function useAccountOperations() {
  const createAccountMutation = useCreateAccount()
  
  return {
    createAccount: createAccountMutation.mutate,
    isCreating: createAccountMutation.isPending,
    createError: createAccountMutation.error,
    createErrorMessages: createAccountMutation.error ? parseAccountError(createAccountMutation.error) : [],
  }
}
