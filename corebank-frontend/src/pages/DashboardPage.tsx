import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  PlusIcon,
  CreditCardIcon,
  BanknotesIcon,
  ArrowsRightLeftIcon,
  ExclamationTriangleIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'
import { useAccounts, useAccountSummary } from '../hooks/useAccounts'
import { useRecentTransactions } from '../hooks/useTransactions'
import { useAuth } from '../hooks/useAuth'
import { useKYCStatus } from '../hooks/useUserProfile'
import CreateAccountModal from '../components/accounts/CreateAccountModal'
import FirstTimeAccountCreationFlow from '../components/onboarding/FirstTimeAccountCreationFlow'
import LoadingSpinner from '../components/common/LoadingSpinner'

export default function DashboardPage() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [isOnboardingFlowOpen, setIsOnboardingFlowOpen] = useState(false)
  const { user } = useAuth()
  const { isKYCCompleted, isLoading: kycLoading } = useKYCStatus()
  const { data: accounts, isLoading: accountsLoading } = useAccounts()
  const { data: summary, isLoading: summaryLoading } = useAccountSummary()
  const { data: recentTransactions, isLoading: transactionsLoading } = useRecentTransactions(5)

  const isLoading = accountsLoading || summaryLoading || transactionsLoading || kycLoading
  const hasAccounts = accounts && accounts.length > 0
  const recentTransactionCount = recentTransactions?.length || 0

  // Handle create account button click from onboarding area (with KYC guidance)
  const handleOnboardingCreateAccountClick = () => {
    if (!isKYCCompleted) {
      // If KYC not completed, start onboarding flow
      setIsOnboardingFlowOpen(true)
    } else {
      // If KYC completed, show regular create account modal
      setIsCreateModalOpen(true)
    }
  }

  // Handle create account button click from quick actions (direct account creation)
  const handleQuickCreateAccountClick = () => {
    // Always show regular create account modal, no KYC guidance
    setIsCreateModalOpen(true)
  }

  const formatCurrency = (amount: string) => {
    const num = parseFloat(amount)
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      minimumFractionDigits: 2,
    }).format(num)
  }

  if (isLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          欢迎回来，{user?.username}！
        </h1>
        <p className="mt-1 text-sm text-gray-600">
          这是您的数脉银行仪表板概览
        </p>
      </div>

      {/* No Accounts Warning */}
      {!hasAccounts && (
        <div className="mb-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-start">
            <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-lg font-medium text-yellow-800">开始使用数脉银行</h3>
              <p className="mt-2 text-sm text-yellow-700">
                您还没有创建任何银行账户。创建您的第一个账户来开始管理您的资金。
              </p>
              <div className="mt-4 flex space-x-3">
                <button
                  onClick={handleOnboardingCreateAccountClick}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-yellow-600 hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
                >
                  <PlusIcon className="h-4 w-4 mr-2" />
                  创建账户
                </button>
                <Link
                  to="/accounts"
                  className="inline-flex items-center px-4 py-2 border border-yellow-300 text-sm font-medium rounded-md text-yellow-700 bg-white hover:bg-yellow-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
                >
                  了解更多
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 mb-8">
        {/* Total Balance */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BanknotesIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">总余额</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {summary ? formatCurrency(summary.total_balance) : '¥0.00'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Total Accounts */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CreditCardIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">账户数量</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {summary ? `${summary.total_accounts} 个` : '0 个'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ArrowsRightLeftIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">近期交易</dt>
                  <dd className="text-lg font-medium text-gray-900">{recentTransactionCount} 笔</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">快速操作</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <button
              onClick={handleQuickCreateAccountClick}
              className="relative group bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg hover:bg-gray-100 text-center"
            >
              <div className="flex justify-center">
                <span className="rounded-lg inline-flex p-3 bg-blue-50 text-blue-700 ring-4 ring-white">
                  <PlusIcon className="h-6 w-6" />
                </span>
              </div>
              <div className="mt-4">
                <h3 className="text-lg font-medium text-gray-900">创建账户</h3>
                <p className="mt-2 text-sm text-gray-500">
                  开设新的支票或储蓄账户
                </p>
              </div>
            </button>

            <Link
              to="/accounts"
              className="relative group bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg hover:bg-gray-100 text-center"
            >
              <div className="flex justify-center">
                <span className="rounded-lg inline-flex p-3 bg-green-50 text-green-700 ring-4 ring-white">
                  <CreditCardIcon className="h-6 w-6" />
                </span>
              </div>
              <div className="mt-4">
                <h3 className="text-lg font-medium text-gray-900">管理账户</h3>
                <p className="mt-2 text-sm text-gray-500">
                  查看和管理您的所有账户
                </p>
              </div>
            </Link>

            <Link
              to="/transactions"
              className="relative group bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg hover:bg-gray-100 text-center"
            >
              <div className="flex justify-center">
                <span className="rounded-lg inline-flex p-3 bg-purple-50 text-purple-700 ring-4 ring-white">
                  <ArrowsRightLeftIcon className="h-6 w-6" />
                </span>
              </div>
              <div className="mt-4">
                <h3 className="text-lg font-medium text-gray-900">交易记录</h3>
                <p className="mt-2 text-sm text-gray-500">
                  查看交易历史和进行转账
                </p>
              </div>
            </Link>

            <Link
              to="/investments"
              className="relative group bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg hover:bg-gray-100 text-center"
            >
              <div className="flex justify-center">
                <span className="rounded-lg inline-flex p-3 bg-orange-50 text-orange-700 ring-4 ring-white">
                  <ChartBarIcon className="h-6 w-6" />
                </span>
              </div>
              <div className="mt-4">
                <h3 className="text-lg font-medium text-gray-900">投资理财</h3>
                <p className="mt-2 text-sm text-gray-500">
                  创建财富，稳健增长
                </p>
              </div>
            </Link>
          </div>
        </div>
      </div>

      {/* Create Account Modal */}
      <CreateAccountModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={() => {
          // Modal will close automatically, data will refetch due to query invalidation
        }}
      />

      {/* First Time Account Creation Flow */}
      <FirstTimeAccountCreationFlow
        isOpen={isOnboardingFlowOpen}
        onClose={() => setIsOnboardingFlowOpen(false)}
        onSuccess={() => {
          // Flow completed, data will refetch due to query invalidation
        }}
      />
    </div>
  )
}
