import { useState } from 'react'
import { PlusIcon } from '@heroicons/react/24/outline'
import { useAccounts, useAccountSummary } from '../hooks/useAccounts'
import CreateAccountModal from '../components/accounts/CreateAccountModal'
import AccountDetailModal from '../components/accounts/AccountDetailModal'
import CrossUserTransferModal from '../components/transactions/CrossUserTransferModal'
import AccountCard from '../components/accounts/AccountCard'
import LoadingSpinner from '../components/common/LoadingSpinner'
import type { Account } from '../types/api'

export default function AccountsPage() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null)
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false)
  const [isTransferModalOpen, setIsTransferModalOpen] = useState(false)
  const [transferFromAccountId, setTransferFromAccountId] = useState<string>('')
  const { data: accounts, isLoading: accountsLoading, error: accountsError } = useAccounts()
  const { data: summary, isLoading: summaryLoading } = useAccountSummary()

  const isLoading = accountsLoading || summaryLoading
  const hasAccounts = accounts && accounts.length > 0

  const formatCurrency = (amount: string) => {
    const num = parseFloat(amount)
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      minimumFractionDigits: 2,
    }).format(num)
  }

  const handleAccountClick = (account: Account) => {
    setSelectedAccount(account)
    setIsDetailModalOpen(true)
  }

  const handleCloseDetailModal = () => {
    setIsDetailModalOpen(false)
    setSelectedAccount(null)
  }

  const handleOpenTransferModal = (accountId: string) => {
    setTransferFromAccountId(accountId)
    setIsTransferModalOpen(true)
  }

  const handleCloseTransferModal = () => {
    setIsTransferModalOpen(false)
    setTransferFromAccountId('')
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

  if (accountsError) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="text-center py-12">
          <p className="text-red-600">加载账户信息失败，请刷新页面重试。</p>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      {/* Header */}
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-xl font-semibold text-gray-900">账户管理</h1>
          <p className="mt-2 text-sm text-gray-700">
            管理您的银行账户并查看余额。
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            type="button"
            onClick={() => setIsCreateModalOpen(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            创建账户
          </button>
        </div>
      </div>

      {/* Summary */}
      {summary && hasAccounts && (
        <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-semibold text-sm">{summary.total_accounts}</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">总账户数</dt>
                    <dd className="text-lg font-medium text-gray-900">{summary.total_accounts} 个</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <span className="text-green-600 font-semibold text-sm">¥</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">总余额</dt>
                    <dd className="text-lg font-medium text-gray-900">{formatCurrency(summary.total_balance)}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                    <span className="text-purple-600 font-semibold text-sm">类</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">账户类型</dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {Object.entries(summary.accounts_by_type).map(([type, count]) => (
                        <span key={type} className="text-sm">
                          {type === 'checking' ? '支票' : '储蓄'}: {count}
                          {' '}
                        </span>
                      ))}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Accounts List */}
      <div className="mt-8">
        {hasAccounts ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {accounts.map((account) => (
              <AccountCard
                key={account.id}
                account={account}
                onClick={() => handleAccountClick(account)}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="mx-auto h-12 w-12 text-gray-400">
              <svg fill="none" stroke="currentColor" viewBox="0 0 48 48">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M34 40h10v-4a6 6 0 00-10.712-3.714M34 40H14m20 0v-4a9.971 9.971 0 00-.712-3.714M14 40H4v-4a6 6 0 0110.712-3.714M14 40v-4a9.971 9.971 0 01.712-3.714M28 16a4 4 0 11-8 0 4 4 0 018 0zm-8 8a6 6 0 00-6 6v4h12v-4a6 6 0 00-6-6z" />
              </svg>
            </div>
            <h3 className="mt-2 text-sm font-medium text-gray-900">暂无账户</h3>
            <p className="mt-1 text-sm text-gray-500">创建您的第一个账户开始使用数脉银行。</p>
            <div className="mt-6">
              <button
                type="button"
                onClick={() => setIsCreateModalOpen(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                创建账户
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Create Account Modal */}
      <CreateAccountModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={() => {
          // Modal will close automatically, accounts will refetch due to query invalidation
        }}
      />

      {/* Account Detail Modal */}
      {selectedAccount && (
        <AccountDetailModal
          isOpen={isDetailModalOpen}
          onClose={handleCloseDetailModal}
          account={selectedAccount}
          onTransfer={(accountId) => {
            handleOpenTransferModal(accountId)
          }}
          onDeposit={(accountId) => {
            // TODO: Open deposit modal with preselected account
            console.log('Deposit to account:', accountId)
          }}
          onWithdraw={(accountId) => {
            // TODO: Open withdraw modal with preselected account
            console.log('Withdraw from account:', accountId)
          }}
        />
      )}

      {/* Cross User Transfer Modal */}
      <CrossUserTransferModal
        isOpen={isTransferModalOpen}
        onClose={handleCloseTransferModal}
        preselectedFromAccountId={transferFromAccountId}
        onSuccess={() => {
          // Modal will close automatically, accounts will refetch due to query invalidation
        }}
      />
    </div>
  )
}
