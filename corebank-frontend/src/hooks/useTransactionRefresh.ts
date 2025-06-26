import { useQueryClient } from '@tanstack/react-query'
import { transactionKeys } from './useTransactions'
import { enhancedTransactionKeys } from './useEnhancedTransactions'

/**
 * Hook to handle refreshing all transaction-related queries after a transaction
 */
export function useTransactionRefresh() {
  const queryClient = useQueryClient()

  const refreshAllTransactionData = () => {
    // Invalidate all transaction queries
    queryClient.invalidateQueries({ 
      queryKey: transactionKeys.all 
    })
    
    // Invalidate enhanced transaction queries
    queryClient.invalidateQueries({ 
      queryKey: enhancedTransactionKeys.all 
    })
    
    // Invalidate account data (balances, etc.)
    queryClient.invalidateQueries({ 
      queryKey: ['accounts'] 
    })
    
    // Invalidate account summary
    queryClient.invalidateQueries({ 
      queryKey: ['accountSummary'] 
    })
    
    // Invalidate investment data that might be affected
    queryClient.invalidateQueries({ 
      queryKey: ['investments'] 
    })
    
    console.log('Refreshed all transaction-related data')
  }

  const refreshAccountTransactions = (accountId: string) => {
    // Invalidate specific account transactions
    queryClient.invalidateQueries({ 
      queryKey: transactionKeys.lists() 
    })
    
    // Invalidate enhanced transactions for this account
    queryClient.invalidateQueries({ 
      queryKey: enhancedTransactionKeys.account(accountId) 
    })
    
    // Invalidate recent transactions
    queryClient.invalidateQueries({ 
      queryKey: [...transactionKeys.all, 'recent'] 
    })
    
    // Invalidate account data
    queryClient.invalidateQueries({ 
      queryKey: ['accounts'] 
    })
    
    console.log(`Refreshed transaction data for account ${accountId}`)
  }

  return {
    refreshAllTransactionData,
    refreshAccountTransactions
  }
}
