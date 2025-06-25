import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { AxiosError } from 'axios'
import apiClient from '../api/client'
import type { 
  Transaction, 
  DepositRequest, 
  WithdrawalRequest, 
  TransferRequest,
  PaginatedResponse,
  ApiError 
} from '../types/api'

// Query keys
export const transactionKeys = {
  all: ['transactions'] as const,
  lists: () => [...transactionKeys.all, 'list'] as const,
  list: (accountId: string, page: number) => [...transactionKeys.lists(), { accountId, page }] as const,
  details: () => [...transactionKeys.all, 'detail'] as const,
  detail: (id: string) => [...transactionKeys.details(), id] as const,
}

// Get transactions for a specific account
export function useAccountTransactions(accountId: string, page = 1, pageSize = 20) {
  return useQuery({
    queryKey: transactionKeys.list(accountId, page),
    queryFn: () => apiClient.getAccountTransactions(accountId, page, pageSize),
    enabled: !!accountId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

// Get specific transaction
export function useTransaction(transactionId: string) {
  return useQuery({
    queryKey: transactionKeys.detail(transactionId),
    queryFn: () => apiClient.getTransaction(transactionId),
    enabled: !!transactionId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get recent transactions across all accounts
export function useRecentTransactions(limit = 5) {
  return useQuery({
    queryKey: [...transactionKeys.all, 'recent', limit],
    queryFn: () => apiClient.getRecentTransactions(limit),
    staleTime: 1 * 60 * 1000, // 1 minute
  })
}

// Deposit mutation
export function useDeposit() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (depositData: DepositRequest) => apiClient.deposit(depositData),
    onSuccess: (transaction: Transaction) => {
      // Invalidate account transactions
      queryClient.invalidateQueries({ 
        queryKey: transactionKeys.lists() 
      })
      
      // Invalidate account data to update balance
      queryClient.invalidateQueries({ 
        queryKey: ['accounts'] 
      })
      
      console.log('Deposit successful:', transaction.id)
    },
    onError: (error: AxiosError<ApiError>) => {
      console.error('Deposit failed:', error)
    }
  })
}

// Withdrawal mutation
export function useWithdraw() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (withdrawalData: WithdrawalRequest) => apiClient.withdraw(withdrawalData),
    onSuccess: (transaction: Transaction) => {
      // Invalidate account transactions
      queryClient.invalidateQueries({ 
        queryKey: transactionKeys.lists() 
      })
      
      // Invalidate account data to update balance
      queryClient.invalidateQueries({ 
        queryKey: ['accounts'] 
      })
      
      console.log('Withdrawal successful:', transaction.id)
    },
    onError: (error: AxiosError<ApiError>) => {
      console.error('Withdrawal failed:', error)
    }
  })
}

// Transfer mutation
export function useTransfer() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (transferData: TransferRequest) => apiClient.transfer(transferData),
    onSuccess: (transactions: Transaction[]) => {
      // Invalidate account transactions
      queryClient.invalidateQueries({ 
        queryKey: transactionKeys.lists() 
      })
      
      // Invalidate account data to update balances
      queryClient.invalidateQueries({ 
        queryKey: ['accounts'] 
      })
      
      console.log('Transfer successful:', transactions.map(t => t.id))
    },
    onError: (error: AxiosError<ApiError>) => {
      console.error('Transfer failed:', error)
    }
  })
}

// Helper function to parse transaction errors
export function parseTransactionError(error: unknown): string[] {
  if (!error || typeof error !== 'object') {
    return ['交易失败，请重试']
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

  return ['交易失败，请重试']
}

// Custom hook for transaction operations
export function useTransactionOperations() {
  const depositMutation = useDeposit()
  const withdrawMutation = useWithdraw()
  const transferMutation = useTransfer()
  
  return {
    // Deposit
    deposit: depositMutation.mutate,
    isDepositing: depositMutation.isPending,
    depositError: depositMutation.error,
    depositErrorMessages: depositMutation.error ? parseTransactionError(depositMutation.error) : [],
    
    // Withdrawal
    withdraw: withdrawMutation.mutate,
    isWithdrawing: withdrawMutation.isPending,
    withdrawError: withdrawMutation.error,
    withdrawErrorMessages: withdrawMutation.error ? parseTransactionError(withdrawMutation.error) : [],
    
    // Transfer
    transfer: transferMutation.mutate,
    isTransferring: transferMutation.isPending,
    transferError: transferMutation.error,
    transferErrorMessages: transferMutation.error ? parseTransactionError(transferMutation.error) : [],
  }
}
