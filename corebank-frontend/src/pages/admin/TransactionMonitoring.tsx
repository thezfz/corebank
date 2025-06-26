import React, { useState, useEffect } from 'react'
import { 
  ArrowsRightLeftIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  FunnelIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline'
import { useEnhancedAccountTransactions } from '../../hooks/useEnhancedTransactions'
import { useAccounts } from '../../hooks/useAccounts'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import TransactionCard from '../../components/transactions/TransactionCard'

export default function TransactionMonitoring() {
  const [selectedAccountId, setSelectedAccountId] = useState<string>('')
  const [currentPage, setCurrentPage] = useState(1)
  const [searchTerm, setSearchTerm] = useState('')
  const [transactionType, setTransactionType] = useState('')

  const { data: accounts, isLoading: accountsLoading } = useAccounts()
  const { 
    data: transactionsData, 
    isLoading: transactionsLoading,
    error: transactionsError 
  } = useEnhancedAccountTransactions(
    selectedAccountId, 
    currentPage, 
    20,
    { enabled: !!selectedAccountId }
  )

  // Auto-select first account if available
  useEffect(() => {
    if (accounts && accounts.length > 0 && !selectedAccountId) {
      setSelectedAccountId(accounts[0].id)
    }
  }, [accounts, selectedAccountId])

  const filteredTransactions = transactionsData?.items?.filter(transaction => {
    const matchesSearch = searchTerm === '' || 
      transaction.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      transaction.related_user_name?.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesType = transactionType === '' || transaction.transaction_type === transactionType
    
    return matchesSearch && matchesType
  }) || []

  if (accountsLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-5">
        <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          交易监控
        </h1>
        <p className="mt-2 max-w-4xl text-sm text-gray-500">
          监控和分析系统中的所有交易活动
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ArrowsRightLeftIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    总交易数
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {transactionsData?.total_count || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-6 w-6 text-green-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    存款交易
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {filteredTransactions.filter(t => t.transaction_type === 'deposit').length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-6 w-6 text-red-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    取款交易
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {filteredTransactions.filter(t => t.transaction_type === 'withdrawal').length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ArrowsRightLeftIcon className="h-6 w-6 text-blue-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    转账交易
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {filteredTransactions.filter(t => t.transaction_type === 'transfer').length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
            {/* Account Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                选择账户
              </label>
              <select
                value={selectedAccountId}
                onChange={(e) => {
                  setSelectedAccountId(e.target.value)
                  setCurrentPage(1)
                }}
                className="focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
              >
                <option value="">选择账户</option>
                {accounts?.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.account_number} ({account.account_type})
                  </option>
                ))}
              </select>
            </div>

            {/* Transaction Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                交易类型
              </label>
              <select
                value={transactionType}
                onChange={(e) => setTransactionType(e.target.value)}
                className="focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
              >
                <option value="">所有类型</option>
                <option value="deposit">存款</option>
                <option value="withdrawal">取款</option>
                <option value="transfer">转账</option>
                <option value="investment_purchase">理财申购</option>
                <option value="investment_redemption">理财赎回</option>
              </select>
            </div>

            {/* Search */}
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                搜索交易
              </label>
              <div className="relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-10 sm:text-sm border-gray-300 rounded-md"
                  placeholder="搜索描述、用户名..."
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Transactions List */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              交易记录
            </h3>
            <div className="text-sm text-gray-500">
              {selectedAccountId ? `显示 ${filteredTransactions.length} 条记录` : '请选择账户'}
            </div>
          </div>

          {!selectedAccountId ? (
            <div className="text-center py-12">
              <ArrowsRightLeftIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">请选择账户</h3>
              <p className="mt-1 text-sm text-gray-500">
                选择一个账户来查看交易记录
              </p>
            </div>
          ) : transactionsLoading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner />
            </div>
          ) : transactionsError ? (
            <div className="text-center py-12">
              <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">加载失败</h3>
              <p className="mt-1 text-sm text-gray-500">
                无法加载交易记录，请稍后重试
              </p>
            </div>
          ) : filteredTransactions.length === 0 ? (
            <div className="text-center py-12">
              <ArrowsRightLeftIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">暂无交易记录</h3>
              <p className="mt-1 text-sm text-gray-500">
                {searchTerm || transactionType ? '没有符合条件的交易记录' : '该账户暂无交易记录'}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredTransactions.map((transaction) => (
                <TransactionCard
                  key={transaction.id}
                  transaction={transaction}
                />
              ))}
            </div>
          )}

          {/* Pagination */}
          {transactionsData && transactionsData.total_pages > 1 && (
            <div className="mt-6 flex items-center justify-between">
              <div className="text-sm text-gray-700">
                显示第 {(currentPage - 1) * 20 + 1} 到{' '}
                {Math.min(currentPage * 20, transactionsData.total_count)} 条，
                共 {transactionsData.total_count} 条记录
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  上一页
                </button>
                <span className="px-3 py-2 text-sm text-gray-700">
                  {currentPage} / {transactionsData.total_pages}
                </span>
                <button
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={currentPage === transactionsData.total_pages}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  下一页
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
