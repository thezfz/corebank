import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import type { PaginatedResponse } from '../types/api'

// Query keys for admin transactions
export const adminTransactionKeys = {
  all: ['admin-transactions'] as const,
  lists: () => [...adminTransactionKeys.all, 'list'] as const,
  list: (filters: any) => [...adminTransactionKeys.lists(), filters] as const,
  accounts: () => [...adminTransactionKeys.all, 'accounts'] as const,
  statistics: () => [...adminTransactionKeys.all, 'statistics'] as const,
}

// Get all accounts for admin
export function useAdminAccounts() {
  return useQuery({
    queryKey: adminTransactionKeys.accounts(),
    queryFn: () => apiClient.getAllAccounts(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get all transactions for admin with filters
export function useAdminTransactions(
  page: number = 1,
  pageSize: number = 20,
  filters: {
    account_id?: string
    transaction_type?: string
    user_search?: string
  } = {}
) {
  return useQuery({
    queryKey: adminTransactionKeys.list({ page, pageSize, ...filters }),
    queryFn: () => apiClient.getAllTransactions({
      page,
      page_size: pageSize,
      ...filters
    }),
    staleTime: 30 * 1000, // 30 seconds
    retry: (failureCount, error) => {
      // Don't retry on 401/403 errors
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as any
        if ([401, 403].includes(axiosError.response?.status || 0)) {
          return false
        }
      }
      return failureCount < 3
    }
  })
}

// Get transaction statistics for admin
export function useAdminTransactionStatistics() {
  return useQuery({
    queryKey: adminTransactionKeys.statistics(),
    queryFn: () => apiClient.getTransactionStatistics(),
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}
