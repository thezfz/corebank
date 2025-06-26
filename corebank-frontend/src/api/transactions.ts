import { PaginatedResponse, EnhancedTransaction } from '../types/api'
import { apiClient } from './client'

export const transactionsApi = {
  // Get enhanced transaction history for an account
  getEnhancedAccountTransactions: async (
    accountId: string,
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedResponse<EnhancedTransaction>> => {
    const response = await apiClient.get<PaginatedResponse<EnhancedTransaction>>(
      `/transactions/accounts/${accountId}/enhanced`,
      {
        params: {
          page,
          page_size: pageSize
        }
      }
    )
    return response.data
  }
}
