import { useState, useEffect } from 'react'
import {
  PlusIcon,
  ArrowDownIcon,
  ArrowUpIcon,
  ArrowsRightLeftIcon,
  FunnelIcon
} from '@heroicons/react/24/outline'
import { useAccounts } from '../hooks/useAccounts'
import { useAccountTransactions } from '../hooks/useTransactions'
import { useEnhancedAccountTransactions } from '../hooks/useEnhancedTransactions'
import DepositModal from '../components/transactions/DepositModal'
import WithdrawModal from '../components/transactions/WithdrawModal'
import CrossUserTransferModal from '../components/transactions/CrossUserTransferModal'
import TransactionCard from '../components/transactions/TransactionCard'
import LoadingSpinner from '../components/common/LoadingSpinner'

export default function TransactionsPage() {
  const [isDepositModalOpen, setIsDepositModalOpen] = useState(false)
  const [isWithdrawModalOpen, setIsWithdrawModalOpen] = useState(false)
  const [isCrossUserTransferModalOpen, setIsCrossUserTransferModalOpen] = useState(false)
  const [selectedAccountId, setSelectedAccountId] = useState('')
  const [currentPage, setCurrentPage] = useState(1)

  const { data: accounts, isLoading: accountsLoading } = useAccounts()
  const {
    data: transactionsData,
    isLoading: transactionsLoading,
    error: transactionsError
  } = useEnhancedAccountTransactions(selectedAccountId, currentPage, 20, !!selectedAccountId)

  const hasAccounts = accounts && accounts.length > 0

  // Use first account as default if none selected
  const defaultAccountId = accounts?.[0]?.id || ''
  const activeAccountId = selectedAccountId || defaultAccountId

  // Update selected account when accounts load
  useEffect(() => {
    if (!selectedAccountId && defaultAccountId) {
      setSelectedAccountId(defaultAccountId)
    }
  }, [defaultAccountId, selectedAccountId])

  if (accountsLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      </div>
    )
  }

  if (!hasAccounts) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="text-center py-12">
          <div className="mx-auto h-12 w-12 text-gray-400">
            <ArrowsRightLeftIcon className="h-12 w-12" />
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">暂无账户</h3>
          <p className="mt-1 text-sm text-gray-500">
            您需要先创建账户才能进行交易。
          </p>
          <div className="mt-6">
            <a
              href="/accounts"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              创建账户
            </a>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      {/* Header */}
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-xl font-semibold text-gray-900">交易记录</h1>
          <p className="mt-2 text-sm text-gray-700">
            查看您的交易历史并进行新的交易。
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <div className="flex space-x-2">
            <button
              onClick={() => setIsDepositModalOpen(true)}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              <ArrowDownIcon className="h-4 w-4 mr-1" />
              存款
            </button>
            <button
              onClick={() => setIsWithdrawModalOpen(true)}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              <ArrowUpIcon className="h-4 w-4 mr-1" />
              取款
            </button>
            <button
              onClick={() => setIsCrossUserTransferModalOpen(true)}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <ArrowsRightLeftIcon className="h-4 w-4 mr-1" />
              转账
            </button>
          </div>
        </div>
      </div>

      {/* Account Filter */}
      <div className="mt-6 flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <FunnelIcon className="h-5 w-5 text-gray-400" />
          <label htmlFor="accountFilter" className="text-sm font-medium text-gray-700">
            筛选账户:
          </label>
        </div>
        <select
          id="accountFilter"
          value={selectedAccountId}
          onChange={(e) => {
            setSelectedAccountId(e.target.value)
            setCurrentPage(1) // Reset to first page when changing account
          }}
          className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          {accounts?.map((account) => (
            <option key={account.id} value={account.id}>
              {account.account_type === 'checking' ? '支票账户' : '储蓄账户'} -
              **** {account.account_number.slice(-4)} -
              ¥{parseFloat(account.balance).toLocaleString('zh-CN', { minimumFractionDigits: 2 })}
            </option>
          ))}
        </select>
      </div>

      {/* Transactions List */}
      <div className="mt-8">
        {transactionsLoading ? (
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : transactionsError ? (
          <div className="text-center py-12">
            <p className="text-red-600">加载交易记录失败，请刷新页面重试。</p>
          </div>
        ) : transactionsData?.items && transactionsData.items.length > 0 ? (
          <div className="space-y-4">
            {transactionsData.items.map((transaction) => (
              <TransactionCard
                key={transaction.id}
                transaction={transaction}
                onClick={() => {
                  // TODO: Navigate to transaction detail page
                  console.log('Navigate to transaction:', transaction.id)
                }}
              />
            ))}

            {/* Pagination */}
            {transactionsData.total_pages > 1 && (
              <div className="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 mt-6">
                <div className="flex flex-1 justify-between sm:hidden">
                  <button
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                    className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
                  >
                    上一页
                  </button>
                  <button
                    onClick={() => setCurrentPage(Math.min(transactionsData.total_pages, currentPage + 1))}
                    disabled={currentPage === transactionsData.total_pages}
                    className="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
                  >
                    下一页
                  </button>
                </div>
                <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700">
                      显示第 <span className="font-medium">{(currentPage - 1) * 20 + 1}</span> 到{' '}
                      <span className="font-medium">
                        {Math.min(currentPage * 20, transactionsData.total_count)}
                      </span>{' '}
                      条，共 <span className="font-medium">{transactionsData.total_count}</span> 条记录
                    </p>
                  </div>
                  <div>
                    <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                      <button
                        onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                        disabled={currentPage === 1}
                        className="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:bg-gray-100 disabled:cursor-not-allowed"
                      >
                        上一页
                      </button>

                      {/* Page numbers */}
                      {Array.from({ length: Math.min(5, transactionsData.total_pages) }, (_, i) => {
                        const pageNum = i + 1
                        return (
                          <button
                            key={pageNum}
                            onClick={() => setCurrentPage(pageNum)}
                            className={`relative inline-flex items-center px-4 py-2 text-sm font-semibold ${
                              pageNum === currentPage
                                ? 'z-10 bg-blue-600 text-white focus:z-20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600'
                                : 'text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0'
                            }`}
                          >
                            {pageNum}
                          </button>
                        )
                      })}

                      <button
                        onClick={() => setCurrentPage(Math.min(transactionsData.total_pages, currentPage + 1))}
                        disabled={currentPage === transactionsData.total_pages}
                        className="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:bg-gray-100 disabled:cursor-not-allowed"
                      >
                        下一页
                      </button>
                    </nav>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="mx-auto h-12 w-12 text-gray-400">
              <ArrowsRightLeftIcon className="h-12 w-12" />
            </div>
            <h3 className="mt-2 text-sm font-medium text-gray-900">暂无交易记录</h3>
            <p className="mt-1 text-sm text-gray-500">
              进行您的第一笔交易后将在此显示。
            </p>
            <div className="mt-6 flex justify-center space-x-2">
              <button
                onClick={() => setIsDepositModalOpen(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <ArrowDownIcon className="h-4 w-4 mr-2" />
                存款
              </button>
              <button
                onClick={() => setIsCrossUserTransferModalOpen(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <ArrowsRightLeftIcon className="h-4 w-4 mr-2" />
                转账
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Transaction Modals */}
      <DepositModal
        isOpen={isDepositModalOpen}
        onClose={() => setIsDepositModalOpen(false)}
        preselectedAccountId={activeAccountId}
        onSuccess={() => {
          // Modal will close automatically, transactions will refetch due to query invalidation
        }}
      />

      <WithdrawModal
        isOpen={isWithdrawModalOpen}
        onClose={() => setIsWithdrawModalOpen(false)}
        preselectedAccountId={activeAccountId}
        onSuccess={() => {
          // Modal will close automatically, transactions will refetch due to query invalidation
        }}
      />

      <CrossUserTransferModal
        isOpen={isCrossUserTransferModalOpen}
        onClose={() => setIsCrossUserTransferModalOpen(false)}
        preselectedFromAccountId={activeAccountId}
        onSuccess={() => {
          // Modal will close automatically, transactions will refetch due to query invalidation
        }}
      />
    </div>
  )
}
