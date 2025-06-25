import axios, { AxiosInstance, AxiosError } from 'axios'
import type {
  User, UserCreate, UserLogin, Token,
  Account, AccountCreate, AccountSummary,
  Transaction, DepositRequest, WithdrawalRequest, TransferRequest,
  PaginatedResponse, ApiError
} from '../types/api'
import type {
  InvestmentProduct, RiskAssessment, RiskAssessmentCreate,
  InvestmentTransaction, InvestmentPurchaseRequest, InvestmentRedemptionRequest,
  InvestmentHolding, PortfolioSummary, ProductRecommendation
} from '../types/investment'

class ApiClient {
  private client: AxiosInstance
  private token: string | null = null

  constructor() {
    this.client = axios.create({
      baseURL: '/api/v1',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Load token from localStorage
    this.token = localStorage.getItem('auth_token')
    if (this.token) {
      this.setAuthHeader(this.token)
    }

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiError>) => {
        if (error.response?.status === 401) {
          // Only clear auth and redirect if this is NOT a login request
          // Login failures should be handled by the login form, not by auto-redirect
          const isLoginRequest = error.config?.url?.includes('/auth/login')

          if (!isLoginRequest) {
            // This is an authenticated request that failed due to invalid/expired token
            this.clearAuth()
            window.location.href = '/login'
          }
          // For login requests, just let the error propagate to be handled by the form
        }
        return Promise.reject(error)
      }
    )
  }

  private setAuthHeader(token: string) {
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }

  private clearAuth() {
    this.token = null
    localStorage.removeItem('auth_token')
    delete this.client.defaults.headers.common['Authorization']
  }

  // Auth methods
  async register(userData: UserCreate): Promise<User> {
    const response = await this.client.post<User>('/auth/register', userData)
    return response.data
  }

  async login(credentials: UserLogin): Promise<Token> {
    const response = await this.client.post<Token>('/auth/login', credentials)
    const token = response.data
    
    this.token = token.access_token
    localStorage.setItem('auth_token', token.access_token)
    this.setAuthHeader(token.access_token)
    
    return token
  }

  logout() {
    this.clearAuth()
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/auth/me')
    return response.data
  }

  // Account methods
  async getAccounts(): Promise<Account[]> {
    const response = await this.client.get<Account[]>('/accounts')
    return response.data
  }

  async createAccount(accountData: AccountCreate): Promise<Account> {
    const response = await this.client.post<Account>('/accounts', accountData)
    return response.data
  }

  async getAccount(accountId: string): Promise<Account> {
    const response = await this.client.get<Account>(`/accounts/${accountId}`)
    return response.data
  }

  async getAccountSummary(): Promise<AccountSummary> {
    const response = await this.client.get<AccountSummary>('/accounts/summary')
    return response.data
  }

  // Transaction methods
  async deposit(depositData: DepositRequest): Promise<Transaction> {
    const response = await this.client.post<Transaction>('/transactions/deposit', depositData)
    return response.data
  }

  async withdraw(withdrawalData: WithdrawalRequest): Promise<Transaction> {
    const response = await this.client.post<Transaction>('/transactions/withdraw', withdrawalData)
    return response.data
  }

  async transfer(transferData: TransferRequest): Promise<Transaction[]> {
    const response = await this.client.post<Transaction[]>('/transactions/transfer', transferData)
    return response.data
  }

  async getAccountTransactions(
    accountId: string, 
    page = 1, 
    pageSize = 20
  ): Promise<PaginatedResponse<Transaction>> {
    const response = await this.client.get<PaginatedResponse<Transaction>>(
      `/transactions/account/${accountId}`,
      { params: { page, page_size: pageSize } }
    )
    return response.data
  }

  async getTransaction(transactionId: string): Promise<Transaction> {
    const response = await this.client.get<Transaction>(`/transactions/${transactionId}`)
    return response.data
  }

  async getRecentTransactions(limit = 5): Promise<Transaction[]> {
    const response = await this.client.get<PaginatedResponse<Transaction>>(
      '/transactions/recent',
      { params: { page_size: limit } }
    )
    return response.data.items
  }

  // Investment methods
  async getInvestmentProducts(params?: {
    product_type?: string
    risk_level?: number
    is_active?: boolean
    page?: number
    page_size?: number
  }): Promise<InvestmentProduct[]> {
    const response = await this.client.get<InvestmentProduct[]>('/investments/products', { params })
    return response.data
  }

  async getInvestmentProduct(productId: string): Promise<InvestmentProduct> {
    const response = await this.client.get<InvestmentProduct>(`/investments/products/${productId}`)
    return response.data
  }

  async createRiskAssessment(data: RiskAssessmentCreate): Promise<RiskAssessment> {
    const response = await this.client.post<RiskAssessment>('/investments/risk-assessment', data)
    return response.data
  }

  async getRiskAssessment(): Promise<RiskAssessment | null> {
    const response = await this.client.get<RiskAssessment | null>('/investments/risk-assessment')
    return response.data
  }

  async purchaseInvestment(data: InvestmentPurchaseRequest): Promise<InvestmentTransaction> {
    const response = await this.client.post<InvestmentTransaction>('/investments/purchase', data)
    return response.data
  }

  async redeemInvestment(data: InvestmentRedemptionRequest): Promise<InvestmentTransaction> {
    const response = await this.client.post<InvestmentTransaction>('/investments/redeem', data)
    return response.data
  }

  async getInvestmentHoldings(): Promise<InvestmentHolding[]> {
    const response = await this.client.get<InvestmentHolding[]>('/investments/holdings')
    return response.data
  }

  async getPortfolioSummary(): Promise<PortfolioSummary> {
    const response = await this.client.get<PortfolioSummary>('/investments/portfolio-summary')
    return response.data
  }

  async getInvestmentTransactions(params?: {
    product_id?: string
    transaction_type?: string
    page?: number
    page_size?: number
  }): Promise<PaginatedResponse<InvestmentTransaction>> {
    const response = await this.client.get<PaginatedResponse<InvestmentTransaction>>('/investments/transactions', { params })
    return response.data
  }

  async getProductRecommendations(): Promise<ProductRecommendation[]> {
    const response = await this.client.get<ProductRecommendation[]>('/investments/recommendations')
    return response.data
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get<{ status: string }>('/health')
    return response.data
  }
}

export const apiClient = new ApiClient()
export default apiClient
