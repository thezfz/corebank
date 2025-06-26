import { useState } from 'react'
import { 
  ArrowsRightLeftIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  ArrowDownIcon,
  ArrowUpIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline'
import { useInvestmentTransactions } from '../hooks/useInvestments'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { 
  TransactionType,
  TransactionStatus,
  TRANSACTION_TYPE_LABELS,
  TRANSACTION_STATUS_LABELS
} from '../types/investment'

export default function InvestmentTransactionsPage() {
  const [filters, setFilters] = useState<{
    transaction_type?: TransactionType
    status?: TransactionStatus
  }>({})
  const [showFilters, setShowFilters] = useState(false)

  const { data: transactions, isLoading, error } = useInvestmentTransactions(filters)

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      minimumFractionDigits: 2,
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('zh-CN')
  }

  const getTransactionIcon = (type: TransactionType) => {
    switch (type) {
      case TransactionType.PURCHASE:
        return <ArrowDownIcon className="h-5 w-5 text-red-500" />
      case TransactionType.REDEMPTION:
        return <ArrowUpIcon className="h-5 w-5 text-green-500" />
      case TransactionType.DIVIDEND:
      case TransactionType.INTEREST:
        return <ArrowUpIcon className="h-5 w-5 text-blue-500" />
      default:
        return <ArrowsRightLeftIcon className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusBadge = (status: TransactionStatus) => {
    const statusConfig = {
      [TransactionStatus.PENDING]: { label: '处理中', color: 'bg-yellow-100 text-yellow-800' },
      [TransactionStatus.CONFIRMED]: { label: '已确认', color: 'bg-green-100 text-green-800' },
      [TransactionStatus.FAILED]: { label: '失败', color: 'bg-red-100 text-red-800' },
      [TransactionStatus.CANCELLED]: { label: '已取消', color: 'bg-gray-100 text-gray-800' }
    }
    
    const config = statusConfig[status]
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        {config.label}
      </span>
    )
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

  if (error) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="text-center py-12">
          <InformationCircleIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">加载失败</h3>
          <p className="mt-1 text-sm text-gray-500">无法加载交易记录，请稍后重试</p>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">投资交易记录</h1>
        <p className="mt-1 text-sm text-gray-600">
          查看您的投资交易历史记录
        </p>
      </div>

      {/* Filters */}
      <div className="mb-6 space-y-4">
        {/* Filter Toggle */}
        <div className="flex justify-between items-center">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <FunnelIcon className="h-4 w-4 mr-2" />
            筛选条件
          </button>
          <div className="text-sm text-gray-500">
            共 {transactions?.length || 0} 条记录
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="bg-gray-50 p-4 rounded-lg space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              {/* Transaction Type Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  交易类型
                </label>
                <select
                  value={filters.transaction_type || ''}
                  onChange={(e) => setFilters({
                    ...filters,
                    transaction_type: e.target.value as TransactionType || undefined
                  })}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">全部类型</option>
                  {Object.entries(TRANSACTION_TYPE_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </div>

              {/* Status Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  交易状态
                </label>
                <select
                  value={filters.status || ''}
                  onChange={(e) => setFilters({
                    ...filters,
                    status: e.target.value as TransactionStatus || undefined
                  })}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">全部状态</option>
                  {Object.entries(TRANSACTION_STATUS_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </div>

              {/* Clear Filters */}
              <div className="flex items-end">
                <button
                  onClick={() => setFilters({})}
                  className="w-full px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  清除筛选
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Transactions List */}
      {!transactions || transactions.length === 0 ? (
        <div className="text-center py-12">
          <ArrowsRightLeftIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">暂无交易记录</h3>
          <p className="mt-1 text-sm text-gray-500">
            您还没有任何投资交易记录
          </p>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {transactions.map((transaction) => (
              <li key={transaction.id}>
                <div className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        {getTransactionIcon(transaction.transaction_type)}
                      </div>
                      <div className="ml-4">
                        <div className="flex items-center">
                          <p className="text-sm font-medium text-gray-900">
                            {TRANSACTION_TYPE_LABELS[transaction.transaction_type]}
                          </p>
                          <div className="ml-2">
                            {getStatusBadge(transaction.status)}
                          </div>
                        </div>
                        <p className="text-sm text-gray-500">
                          交易ID: {transaction.id.slice(0, 8)}...
                        </p>
                        {transaction.description && (
                          <p className="text-sm text-gray-500">
                            {transaction.description}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`text-lg font-medium ${
                        transaction.transaction_type === TransactionType.PURCHASE 
                          ? 'text-red-600' 
                          : 'text-green-600'
                      }`}>
                        {transaction.transaction_type === TransactionType.PURCHASE ? '-' : '+'}
                        {formatCurrency(transaction.net_amount)}
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatDate(transaction.created_at)}
                      </p>
                    </div>
                  </div>

                  {/* Transaction Details */}
                  <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
                    <div>
                      <dt className="text-sm font-medium text-gray-500">份额</dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        {transaction.shares.toLocaleString('zh-CN', { maximumFractionDigits: 4 })}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">单价</dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        {formatCurrency(transaction.unit_price)}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">手续费</dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        {formatCurrency(transaction.fee)}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">结算日期</dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        {transaction.settlement_date 
                          ? formatDate(transaction.settlement_date)
                          : '待结算'
                        }
                      </dd>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
