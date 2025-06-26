// User types
export type UserRole = 'user' | 'admin'

export interface User {
  id: string
  username: string
  role: UserRole
  created_at: string
}

export interface UserCreate {
  username: string
  password: string
}

export interface UserLogin {
  username: string
  password: string
}

export interface UserProfile {
  real_name?: string
  english_name?: string
  id_type?: string
  id_number?: string
  country?: string
  ethnicity?: string
  gender?: string
  birth_date?: string
  birth_place?: string
  phone?: string
  email?: string
  address?: string
}

export interface UserDetailResponse extends User {
  profile?: UserProfile
}

export interface UserProfileUpdate extends UserProfile {}

// Account types
export type AccountType = 'checking' | 'savings'

export interface Account {
  id: string
  account_number: string
  user_id: string
  account_type: AccountType
  balance: string
  created_at: string
}

export interface AccountCreate {
  account_type: AccountType
  initial_deposit?: string
}

export interface AccountSummary {
  total_accounts: number
  total_balance: string
  accounts_by_type: Record<AccountType, number>
}

export interface AccountLookupResponse {
  account_id: string
  account_number: string
  account_type: AccountType
  owner_name?: string
}

// Transaction types
export type TransactionType = 'deposit' | 'withdrawal' | 'transfer'
export type TransactionStatus = 'pending' | 'completed' | 'failed' | 'cancelled'

export interface Transaction {
  id: string
  account_id: string
  transaction_type: TransactionType
  amount: string
  related_account_id?: string
  description?: string
  status: TransactionStatus
  timestamp: string
}

export interface EnhancedTransaction {
  id: string
  account_id: string
  account_number: string
  transaction_type: TransactionType
  amount: string
  related_account_id?: string
  related_account_number?: string
  related_user_name?: string
  related_user_phone?: string
  description?: string
  status: TransactionStatus
  timestamp: string
  is_outgoing?: boolean
}

export interface DepositRequest {
  account_id: string
  amount: string
  description?: string
}

export interface WithdrawalRequest {
  account_id: string
  amount: string
  description?: string
}

export interface TransferRequest {
  from_account_id: string
  to_account_id: string
  amount: string
  description?: string
}

export interface TransferByAccountNumberRequest {
  from_account_id: string
  to_account_number: string
  amount: string
  description?: string
}

// Auth types
export interface Token {
  access_token: string
  token_type: string
  expires_in: number
}

// Common types
export interface PaginatedResponse<T> {
  items: T[]
  total_count: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_previous: boolean
}

export interface ApiError {
  detail: string
  status_code: number
  path?: string
  errors?: Array<{
    code: string
    message: string
    field?: string
  }>
}
