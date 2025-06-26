import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { AxiosError } from 'axios'
import apiClient from '../api/client'
import { useTransactionRefresh } from './useTransactionRefresh'
import type {
  Transaction,
  DepositRequest,
  WithdrawalRequest,
  TransferRequest,
  TransferByAccountNumberRequest,
  AccountLookupResponse,
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
  const { refreshAllTransactionData } = useTransactionRefresh()

  return useMutation({
    mutationFn: (depositData: DepositRequest) => apiClient.deposit(depositData),
    onSuccess: (transaction: Transaction) => {
      // Refresh all transaction-related data
      refreshAllTransactionData()

      console.log('Deposit successful:', transaction.id)
    },
    onError: (error: AxiosError<ApiError>) => {
      console.error('Deposit failed:', error)
    }
  })
}

// Withdrawal mutation
export function useWithdraw() {
  const { refreshAllTransactionData } = useTransactionRefresh()

  return useMutation({
    mutationFn: (withdrawalData: WithdrawalRequest) => apiClient.withdraw(withdrawalData),
    onSuccess: (transaction: Transaction) => {
      // Refresh all transaction-related data
      refreshAllTransactionData()

      console.log('Withdrawal successful:', transaction.id)
    },
    onError: (error: AxiosError<ApiError>) => {
      console.error('Withdrawal failed:', error)
    }
  })
}

// Legacy transfer mutation (kept for backward compatibility)
export function useTransfer() {
  const { refreshAllTransactionData } = useTransactionRefresh()

  return useMutation({
    mutationFn: (transferData: TransferRequest) => apiClient.transfer(transferData),
    onSuccess: (transactions: Transaction[]) => {
      // Refresh all transaction-related data
      refreshAllTransactionData()

      console.log('Transfer successful:', transactions.map(t => t.id))
    },
    onError: (error: AxiosError<ApiError>) => {
      console.error('Transfer failed:', error)
    }
  })
}

// Transfer by account number mutation
export function useTransferByAccountNumber() {
  const { refreshAllTransactionData } = useTransactionRefresh()

  return useMutation({
    mutationFn: (transferData: TransferByAccountNumberRequest) => apiClient.transferByAccountNumber(transferData),
    onSuccess: (transactions: Transaction[]) => {
      // Refresh all transaction-related data
      refreshAllTransactionData()

      console.log('Transfer by account number successful:', transactions.map(t => t.id))
    },
    onError: (error: AxiosError<ApiError>) => {
      console.error('Transfer by account number failed:', error)
    }
  })
}

// Account lookup query
export function useAccountLookup(accountNumber: string, enabled: boolean = false) {
  return useQuery({
    queryKey: ['account-lookup', accountNumber],
    queryFn: () => apiClient.lookupAccountByNumber(accountNumber),
    enabled: enabled && !!accountNumber,
    retry: false, // Don't retry on failed lookups
    staleTime: 5 * 60 * 1000, // 5 minutes
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
  const transferByAccountNumberMutation = useTransferByAccountNumber()

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

    // Transfer by account number
    transferByAccountNumber: transferByAccountNumberMutation.mutate,
    isTransferringByAccountNumber: transferByAccountNumberMutation.isPending,
    transferByAccountNumberError: transferByAccountNumberMutation.error,
    transferByAccountNumberErrorMessages: transferByAccountNumberMutation.error ? parseTransactionError(transferByAccountNumberMutation.error) : [],
  }
}
