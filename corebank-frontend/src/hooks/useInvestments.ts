import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { AxiosError } from 'axios'
import apiClient from '../api/client'
import { useTransactionRefresh } from './useTransactionRefresh'
import type { 
  InvestmentProduct, 
  RiskAssessment, 
  RiskAssessmentCreate,
  InvestmentTransaction,
  InvestmentPurchaseRequest,
  InvestmentRedemptionRequest,
  InvestmentHolding,
  PortfolioSummary,
  ProductRecommendation,
  ProductFilters,

} from '../types/investment'
import type { ApiError } from '../types/api'

// Query keys
export const investmentKeys = {
  all: ['investments'] as const,
  products: () => [...investmentKeys.all, 'products'] as const,
  product: (id: string) => [...investmentKeys.products(), id] as const,
  productList: (filters: ProductFilters) => [...investmentKeys.products(), 'list', filters] as const,
  riskAssessment: () => [...investmentKeys.all, 'risk-assessment'] as const,
  holdings: () => [...investmentKeys.all, 'holdings'] as const,
  portfolio: () => [...investmentKeys.all, 'portfolio'] as const,
  transactions: () => [...investmentKeys.all, 'transactions'] as const,
  recommendations: () => [...investmentKeys.all, 'recommendations'] as const,
}

// Product queries
export function useInvestmentProducts(filters: ProductFilters = {}) {
  return useQuery({
    queryKey: investmentKeys.productList(filters),
    queryFn: () => apiClient.getInvestmentProducts({
      product_type: filters.product_type,
      risk_level: filters.risk_level,
      is_active: filters.is_active ?? true,
    }),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export function useInvestmentProduct(productId: string) {
  return useQuery({
    queryKey: investmentKeys.product(productId),
    queryFn: () => apiClient.getInvestmentProduct(productId),
    enabled: !!productId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Risk assessment queries
export function useRiskAssessment() {
  return useQuery({
    queryKey: investmentKeys.riskAssessment(),
    queryFn: () => apiClient.getRiskAssessment(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

export function useCreateRiskAssessment() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (assessmentData: RiskAssessmentCreate) => 
      apiClient.createRiskAssessment(assessmentData),
    onSuccess: () => {
      // Invalidate risk assessment and recommendations
      queryClient.invalidateQueries({ queryKey: investmentKeys.riskAssessment() })
      queryClient.invalidateQueries({ queryKey: investmentKeys.recommendations() })
      console.log('Risk assessment created successfully')
    },
    onError: (error: AxiosError<ApiError>) => {
      console.error('Failed to create risk assessment:', error)
    }
  })
}

// Investment transaction mutations
export function usePurchaseInvestment() {
  const queryClient = useQueryClient()
  const { refreshAllTransactionData } = useTransactionRefresh()

  return useMutation({
    mutationFn: (purchaseData: InvestmentPurchaseRequest) =>
      apiClient.purchaseInvestment(purchaseData),
    onSuccess: () => {
      // Invalidate investment-specific queries
      queryClient.invalidateQueries({ queryKey: investmentKeys.holdings() })
      queryClient.invalidateQueries({ queryKey: investmentKeys.portfolio() })
      queryClient.invalidateQueries({ queryKey: investmentKeys.transactions() })

      // Refresh all transaction-related data
      refreshAllTransactionData()

      console.log('Investment purchase successful')
    },
    onError: (error: AxiosError<ApiError>) => {
      console.error('Failed to purchase investment:', error)
    }
  })
}

export function useRedeemInvestment() {
  const queryClient = useQueryClient()
  const { refreshAllTransactionData } = useTransactionRefresh()

  return useMutation({
    mutationFn: (redemptionData: InvestmentRedemptionRequest) =>
      apiClient.redeemInvestment(redemptionData),
    onSuccess: () => {
      // Invalidate investment-specific queries
      queryClient.invalidateQueries({ queryKey: investmentKeys.holdings() })
      queryClient.invalidateQueries({ queryKey: investmentKeys.portfolio() })
      queryClient.invalidateQueries({ queryKey: investmentKeys.transactions() })

      // Refresh all transaction-related data
      refreshAllTransactionData()

      console.log('Investment redemption successful')
    },
    onError: (error: AxiosError<ApiError>) => {
      console.error('Failed to redeem investment:', error)
    }
  })
}

// Portfolio queries
export function useInvestmentHoldings() {
  return useQuery({
    queryKey: investmentKeys.holdings(),
    queryFn: () => apiClient.getInvestmentHoldings(),
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

export function usePortfolioSummary() {
  return useQuery({
    queryKey: investmentKeys.portfolio(),
    queryFn: () => apiClient.getPortfolioSummary(),
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

// Recommendations
export function useProductRecommendations() {
  return useQuery({
    queryKey: investmentKeys.recommendations(),
    queryFn: () => apiClient.getProductRecommendations(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Investment transactions
export function useInvestmentTransactions(filters: { product_id?: string; transaction_type?: string } = {}) {
  return useQuery({
    queryKey: [...investmentKeys.transactions(), filters],
    queryFn: () => apiClient.getInvestmentTransactions(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

// Helper function to parse investment errors
export function parseInvestmentError(error: unknown): string[] {
  if (!error || typeof error !== 'object') {
    return ['操作失败，请重试']
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

  return ['操作失败，请重试']
}

// Custom hook for investment operations
export function useInvestmentOperations() {
  const purchaseMutation = usePurchaseInvestment()
  const redeemMutation = useRedeemInvestment()
  const riskAssessmentMutation = useCreateRiskAssessment()
  
  return {
    // Purchase
    purchaseInvestment: purchaseMutation.mutate,
    isPurchasing: purchaseMutation.isPending,
    purchaseError: purchaseMutation.error,
    purchaseErrorMessages: purchaseMutation.error ? parseInvestmentError(purchaseMutation.error) : [],
    
    // Redemption
    redeemInvestment: redeemMutation.mutate,
    isRedeeming: redeemMutation.isPending,
    redeemError: redeemMutation.error,
    redeemErrorMessages: redeemMutation.error ? parseInvestmentError(redeemMutation.error) : [],
    
    // Risk Assessment
    createRiskAssessment: riskAssessmentMutation.mutate,
    isCreatingAssessment: riskAssessmentMutation.isPending,
    assessmentError: riskAssessmentMutation.error,
    assessmentErrorMessages: riskAssessmentMutation.error ? parseInvestmentError(riskAssessmentMutation.error) : [],
  }
}

// Utility hooks
export function useInvestmentStats() {
  const { data: portfolio } = usePortfolioSummary()
  const { data: holdings } = useInvestmentHoldings()
  
  return {
    totalAssets: portfolio?.total_assets || 0,
    totalInvested: portfolio?.total_invested || 0,
    totalGainLoss: portfolio?.total_gain_loss || 0,
    totalReturnRate: portfolio?.total_return_rate || 0,
    holdingsCount: holdings?.length || 0,
    assetAllocation: portfolio?.asset_allocation || {},
  }
}

export function useInvestmentSummary() {
  const { data: products, isLoading: productsLoading } = useInvestmentProducts()
  const { data: holdings, isLoading: holdingsLoading } = useInvestmentHoldings()
  const { data: portfolio, isLoading: portfolioLoading } = usePortfolioSummary()
  const { data: riskAssessment } = useRiskAssessment()
  
  const isLoading = productsLoading || holdingsLoading || portfolioLoading
  const hasInvestments = holdings && holdings.length > 0
  const hasRiskAssessment = !!riskAssessment
  
  return {
    isLoading,
    hasInvestments,
    hasRiskAssessment,
    productsCount: products?.length || 0,
    holdingsCount: holdings?.length || 0,
    totalAssets: Number(portfolio?.total_assets) || 0,
    totalReturnRate: Number(portfolio?.total_return_rate) || 0,
    riskLevel: riskAssessment?.risk_tolerance,
  }
}
