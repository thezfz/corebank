/**
 * Investment-related type definitions for the frontend.
 */

// Enums
export enum ProductType {
  MONEY_FUND = 'money_fund',
  FIXED_TERM = 'fixed_term',
  MUTUAL_FUND = 'mutual_fund',
  INSURANCE = 'insurance'
}

export enum RiskLevel {
  VERY_LOW = 1,
  LOW = 2,
  MEDIUM = 3,
  HIGH = 4,
  VERY_HIGH = 5
}

export enum InvestmentExperience {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced'
}

export enum InvestmentGoal {
  WEALTH_PRESERVATION = 'wealth_preservation',
  STEADY_GROWTH = 'steady_growth',
  AGGRESSIVE_GROWTH = 'aggressive_growth'
}

export enum InvestmentHorizon {
  SHORT_TERM = 'short_term',
  MEDIUM_TERM = 'medium_term',
  LONG_TERM = 'long_term'
}

export enum TransactionType {
  PURCHASE = 'purchase',
  REDEMPTION = 'redemption',
  DIVIDEND = 'dividend',
  INTEREST = 'interest'
}

export enum TransactionStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export enum HoldingStatus {
  ACTIVE = 'active',
  MATURED = 'matured',
  REDEEMED = 'redeemed'
}

// Investment Product interfaces
export interface InvestmentProduct {
  id: string
  product_code: string
  name: string
  product_type: ProductType
  risk_level: RiskLevel
  expected_return_rate?: number
  min_investment_amount: number
  max_investment_amount?: number
  investment_period_days?: number
  is_active: boolean
  description?: string
  features?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface InvestmentProductCreate {
  product_code: string
  name: string
  product_type: ProductType
  risk_level: RiskLevel
  expected_return_rate?: number
  min_investment_amount: number
  max_investment_amount?: number
  investment_period_days?: number
  description?: string
  features?: Record<string, any>
}

// Risk Assessment interfaces
export interface RiskAssessment {
  id: string
  user_id: string
  risk_tolerance: RiskLevel
  investment_experience: InvestmentExperience
  investment_goal: InvestmentGoal
  investment_horizon: InvestmentHorizon
  monthly_income_range?: string
  assessment_score: number
  assessment_data?: Record<string, any>
  expires_at: string
  created_at: string
}

export interface RiskAssessmentCreate {
  risk_tolerance: RiskLevel
  investment_experience: InvestmentExperience
  investment_goal: InvestmentGoal
  investment_horizon: InvestmentHorizon
  monthly_income_range?: string
  assessment_data?: Record<string, any>
}

// Investment Transaction interfaces
export interface InvestmentTransaction {
  id: string
  user_id: string
  account_id: string
  product_id: string
  holding_id?: string
  transaction_type: TransactionType
  shares: number
  unit_price: number
  amount: number
  fee: number
  net_amount: number
  status: TransactionStatus
  settlement_date?: string
  description?: string
  created_at: string
  updated_at: string
}

export interface InvestmentPurchaseRequest {
  account_id: string
  product_id: string
  amount: number
}

export interface InvestmentRedemptionRequest {
  holding_id: string
  shares?: number
}

// Investment Holding interfaces
export interface InvestmentHolding {
  id: string
  user_id: string
  account_id: string
  product_id: string
  product_name: string
  product_type: ProductType
  shares: number
  average_cost: number
  total_invested: number
  current_value: number
  unrealized_gain_loss: number
  realized_gain_loss: number
  return_rate: number
  purchase_date: string
  maturity_date?: string
  status: HoldingStatus
  created_at: string
  updated_at: string
}

// Portfolio interfaces
export interface PortfolioSummary {
  total_assets: number
  total_invested: number
  total_gain_loss: number
  total_return_rate: number
  asset_allocation: Record<ProductType, number>
  holdings_count: number
  active_products_count: number
}

// Product NAV interfaces
export interface ProductNAV {
  id: string
  product_id: string
  nav_date: string
  unit_nav: number
  accumulated_nav?: number
  daily_return_rate?: number
  created_at: string
}

// Product Recommendation interfaces
export interface ProductRecommendation {
  product: InvestmentProduct
  recommendation_score: number
  recommendation_reason: string
  risk_match: boolean
  suggested_allocation?: number
}

// Filter and query interfaces
export interface ProductFilters {
  product_type?: ProductType
  risk_level?: RiskLevel
  is_active?: boolean
  search?: string
}

export interface TransactionFilters {
  product_id?: string
  transaction_type?: TransactionType
  status?: TransactionStatus
  start_date?: string
  end_date?: string
}

// Chart data interfaces
export interface ChartDataPoint {
  date: string
  value: number
  label?: string
}

export interface AssetAllocationData {
  type: ProductType
  value: number
  percentage: number
  color: string
}

export interface PerformanceData {
  period: string
  return_rate: number
  benchmark_return?: number
  volatility?: number
  sharpe_ratio?: number
}

// Form interfaces
export interface RiskAssessmentForm {
  // Personal Information
  age_range: string
  monthly_income_range: string
  investment_experience: InvestmentExperience
  
  // Investment Goals
  investment_goal: InvestmentGoal
  investment_horizon: InvestmentHorizon
  investment_amount_range: string
  
  // Risk Tolerance Questions
  market_decline_reaction: string
  investment_priority: string
  risk_vs_return_preference: string
  liquidity_needs: string
  
  // Additional Information
  other_investments: string[]
  financial_knowledge_level: string
}

// UI State interfaces
export interface InvestmentPageState {
  selectedProduct?: InvestmentProduct
  showPurchaseModal: boolean
  showRedemptionModal: boolean
  showRiskAssessment: boolean
  selectedHolding?: InvestmentHolding
  filters: ProductFilters
  sortBy: string
  sortOrder: 'asc' | 'desc'
}

// API Response interfaces
export interface InvestmentApiResponse<T> {
  data: T
  message?: string
  timestamp: string
}

export interface PaginatedInvestmentResponse<T> {
  items: T[]
  total_count: number
  page: number
  page_size: number
  total_pages: number
}

// Error interfaces
export interface InvestmentError {
  code: string
  message: string
  field?: string
  details?: Record<string, any>
}

// Constants
export const PRODUCT_TYPE_LABELS: Record<ProductType, string> = {
  [ProductType.MONEY_FUND]: '货币基金',
  [ProductType.FIXED_TERM]: '定期理财',
  [ProductType.MUTUAL_FUND]: '基金产品',
  [ProductType.INSURANCE]: '保险理财'
}

export const RISK_LEVEL_LABELS: Record<RiskLevel, string> = {
  [RiskLevel.VERY_LOW]: '极低风险',
  [RiskLevel.LOW]: '低风险',
  [RiskLevel.MEDIUM]: '中等风险',
  [RiskLevel.HIGH]: '高风险',
  [RiskLevel.VERY_HIGH]: '极高风险'
}

export const RISK_LEVEL_COLORS: Record<RiskLevel, string> = {
  [RiskLevel.VERY_LOW]: '#10B981', // green-500
  [RiskLevel.LOW]: '#84CC16',      // lime-500
  [RiskLevel.MEDIUM]: '#F59E0B',   // amber-500
  [RiskLevel.HIGH]: '#EF4444',     // red-500
  [RiskLevel.VERY_HIGH]: '#DC2626' // red-600
}

export const TRANSACTION_TYPE_LABELS: Record<TransactionType, string> = {
  [TransactionType.PURCHASE]: '申购',
  [TransactionType.REDEMPTION]: '赎回',
  [TransactionType.DIVIDEND]: '分红',
  [TransactionType.INTEREST]: '利息'
}

export const TRANSACTION_STATUS_LABELS: Record<TransactionStatus, string> = {
  [TransactionStatus.PENDING]: '处理中',
  [TransactionStatus.CONFIRMED]: '已确认',
  [TransactionStatus.FAILED]: '失败',
  [TransactionStatus.CANCELLED]: '已取消'
}

export const INVESTMENT_EXPERIENCE_LABELS: Record<InvestmentExperience, string> = {
  [InvestmentExperience.BEGINNER]: '初学者',
  [InvestmentExperience.INTERMEDIATE]: '有经验',
  [InvestmentExperience.ADVANCED]: '专业投资者'
}

export const INVESTMENT_GOAL_LABELS: Record<InvestmentGoal, string> = {
  [InvestmentGoal.WEALTH_PRESERVATION]: '财富保值',
  [InvestmentGoal.STEADY_GROWTH]: '稳健增长',
  [InvestmentGoal.AGGRESSIVE_GROWTH]: '积极增长'
}

export const INVESTMENT_HORIZON_LABELS: Record<InvestmentHorizon, string> = {
  [InvestmentHorizon.SHORT_TERM]: '短期（1年以内）',
  [InvestmentHorizon.MEDIUM_TERM]: '中期（1-5年）',
  [InvestmentHorizon.LONG_TERM]: '长期（5年以上）'
}
