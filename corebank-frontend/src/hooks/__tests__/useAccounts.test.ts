import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useAccounts, useAccountSummary, useCreateAccount, parseAccountError } from '../useAccounts'
import apiClient from '../../api/client'
import type { Account, AccountSummary } from '../../types/api'

// Mock API client
vi.mock('../../api/client', () => ({
  default: {
    getAccounts: vi.fn(),
    getAccountSummary: vi.fn(),
    createAccount: vi.fn(),
  }
}))

describe('useAccounts hooks', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })
    vi.clearAllMocks()
  })

  const wrapper = ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children)

  describe('useAccounts', () => {
    it('应该获取账户列表', async () => {
      const mockAccounts: Account[] = [
        {
          id: '1',
          account_number: '1234567890',
          user_id: 'user-1',
          account_type: 'checking',
          balance: '1000.00',
          created_at: '2025-01-15T10:30:00Z'
        }
      ]

      vi.mocked(apiClient.getAccounts).mockResolvedValue(mockAccounts)

      const { result } = renderHook(() => useAccounts(), { wrapper })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(mockAccounts)
      expect(apiClient.getAccounts).toHaveBeenCalledOnce()
    })

    it('应该处理获取账户失败', async () => {
      const error = new Error('Failed to fetch accounts')
      vi.mocked(apiClient.getAccounts).mockRejectedValue(error)

      const { result } = renderHook(() => useAccounts(), { wrapper })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })

      expect(result.current.error).toEqual(error)
    })
  })

  describe('useAccountSummary', () => {
    it('应该获取账户摘要', async () => {
      const mockSummary: AccountSummary = {
        total_accounts: 2,
        total_balance: '2500.00',
        accounts_by_type: {
          checking: 1,
          savings: 1
        }
      }

      vi.mocked(apiClient.getAccountSummary).mockResolvedValue(mockSummary)

      const { result } = renderHook(() => useAccountSummary(), { wrapper })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(mockSummary)
      expect(apiClient.getAccountSummary).toHaveBeenCalledOnce()
    })
  })

  describe('useCreateAccount', () => {
    it('应该创建账户', async () => {
      const newAccount: Account = {
        id: '2',
        account_number: '9876543210',
        user_id: 'user-1',
        account_type: 'savings',
        balance: '500.00',
        created_at: '2025-01-15T11:00:00Z'
      }

      vi.mocked(apiClient.createAccount).mockResolvedValue(newAccount)

      const { result } = renderHook(() => useCreateAccount(), { wrapper })

      const accountData = {
        account_type: 'savings' as const,
        initial_deposit: '500.00'
      }

      result.current.mutate(accountData)

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(newAccount)
      expect(apiClient.createAccount).toHaveBeenCalledWith(accountData)
    })

    it('应该处理创建账户失败', async () => {
      const error = new Error('Failed to create account')
      vi.mocked(apiClient.createAccount).mockRejectedValue(error)

      const { result } = renderHook(() => useCreateAccount(), { wrapper })

      const accountData = {
        account_type: 'checking' as const,
        initial_deposit: '100.00'
      }

      result.current.mutate(accountData)

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })

      expect(result.current.error).toEqual(error)
    })
  })

  describe('parseAccountError', () => {
    it('应该解析验证错误', () => {
      const error = {
        response: {
          status: 422,
          data: {
            detail: 'Validation failed',
            errors: [
              { message: 'Initial deposit must be positive' },
              { message: 'Account type is required' }
            ]
          }
        }
      }

      const result = parseAccountError(error)
      expect(result).toEqual([
        'Initial deposit must be positive',
        'Account type is required'
      ])
    })

    it('应该解析字符串错误', () => {
      const error = {
        response: {
          status: 400,
          data: {
            detail: 'Account creation failed'
          }
        }
      }

      const result = parseAccountError(error)
      expect(result).toEqual(['Account creation failed'])
    })

    it('应该处理网络错误', () => {
      const error = {
        response: undefined
      }

      const result = parseAccountError(error)
      expect(result).toEqual(['网络错误，请检查连接后重试'])
    })

    it('应该处理未知错误', () => {
      const result = parseAccountError(null)
      expect(result).toEqual(['创建账户失败，请重试'])
    })
  })
})
