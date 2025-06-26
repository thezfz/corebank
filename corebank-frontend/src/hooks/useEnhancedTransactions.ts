import { useQuery, useQueryClient } from '@tanstack/react-query'
import { transactionsApi } from '../api/transactions'
import type { PaginatedResponse, EnhancedTransaction } from '../types/api'

// Query keys for enhanced transactions
export const enhancedTransactionKeys = {
  all: ['enhancedTransactions'] as const,
  account: (accountId: string) => [...enhancedTransactionKeys.all, 'account', accountId] as const,
  accountPage: (accountId: string, page: number, pageSize: number) => 
    [...enhancedTransactionKeys.account(accountId), 'page', page, pageSize] as const,
}

// Get enhanced transactions for an account
export function useEnhancedAccountTransactions(
  accountId: string,
  page: number = 1,
  pageSize: number = 20,
  enabled: boolean = true
) {
  return useQuery({
    queryKey: enhancedTransactionKeys.accountPage(accountId, page, pageSize),
    queryFn: () => transactionsApi.getEnhancedAccountTransactions(accountId, page, pageSize),
    enabled: enabled && !!accountId,
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
