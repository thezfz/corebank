import { 
  ArrowDownIcon, 
  ArrowUpIcon, 
  ArrowsRightLeftIcon,
  CheckCircleIcon,
  ClockIcon,
  XCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import type { Transaction } from '../../types/api'

interface TransactionCardProps {
  transaction: Transaction
  onClick?: () => void
}

export default function TransactionCard({ transaction, onClick }: TransactionCardProps) {
  const formatCurrency = (amount: string) => {
    const num = parseFloat(amount)
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      minimumFractionDigits: 2,
    }).format(num)
  }

  const formatDateTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return {
      date: date.toLocaleDateString('zh-CN'),
      time: date.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    }
  }

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case 'deposit':
        return ArrowDownIcon
      case 'withdrawal':
        return ArrowUpIcon
      case 'transfer':
        return ArrowsRightLeftIcon
      default:
        return ArrowsRightLeftIcon
    }
  }

  const getTransactionLabel = (type: string) => {
    switch (type) {
      case 'deposit':
        return '存款'
      case 'withdrawal':
        return '取款'
      case 'transfer':
        return '转账'
      default:
        return type
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return CheckCircleIcon
      case 'pending':
        return ClockIcon
      case 'failed':
        return XCircleIcon
      case 'cancelled':
        return ExclamationTriangleIcon
      default:
        return ClockIcon
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed':
        return '已完成'
      case 'pending':
        return '处理中'
      case 'failed':
        return '失败'
      case 'cancelled':
        return '已取消'
      default:
        return status
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100'
      case 'pending':
        return 'text-yellow-600 bg-yellow-100'
      case 'failed':
        return 'text-red-600 bg-red-100'
      case 'cancelled':
        return 'text-gray-600 bg-gray-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getAmountColor = (type: string) => {
    switch (type) {
      case 'deposit':
        return 'text-green-600'
      case 'withdrawal':
        return 'text-red-600'
      case 'transfer':
        return 'text-blue-600'
      default:
        return 'text-gray-600'
    }
  }

  const getAmountPrefix = (type: string) => {
    switch (type) {
      case 'deposit':
        return '+'
      case 'withdrawal':
        return '-'
      case 'transfer':
        return ''
      default:
        return ''
    }
  }

  const Icon = getTransactionIcon(transaction.transaction_type)
  const StatusIcon = getStatusIcon(transaction.status)
  const { date, time } = formatDateTime(transaction.timestamp)

  return (
    <div 
      className={`bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow ${
        onClick ? 'cursor-pointer hover:border-blue-300' : ''
      }`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        {/* Left side - Icon and details */}
        <div className="flex items-start space-x-3">
          {/* Transaction Icon */}
          <div className={`p-2 rounded-lg ${
            transaction.transaction_type === 'deposit' ? 'bg-green-100' :
            transaction.transaction_type === 'withdrawal' ? 'bg-red-100' :
            'bg-blue-100'
          }`}>
            <Icon className={`h-5 w-5 ${
              transaction.transaction_type === 'deposit' ? 'text-green-600' :
              transaction.transaction_type === 'withdrawal' ? 'text-red-600' :
              'text-blue-600'
            }`} />
          </div>

          {/* Transaction Details */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-1">
              <h3 className="text-sm font-medium text-gray-900">
                {getTransactionLabel(transaction.transaction_type)}
              </h3>
              
              {/* Status Badge */}
              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(transaction.status)}`}>
                <StatusIcon className="h-3 w-3 mr-1" />
                {getStatusLabel(transaction.status)}
              </span>
            </div>

            {/* Description */}
            {transaction.description && (
              <p className="text-sm text-gray-600 mb-1 truncate">
                {transaction.description}
              </p>
            )}

            {/* Related Account Info for Transfers */}
            {transaction.transaction_type === 'transfer' && transaction.related_account_id && (
              <p className="text-xs text-gray-500">
                相关账户: **** {transaction.related_account_id.slice(-4)}
              </p>
            )}

            {/* Date and Time */}
            <div className="flex items-center space-x-2 text-xs text-gray-500 mt-2">
              <span>{date}</span>
              <span>•</span>
              <span>{time}</span>
            </div>
          </div>
        </div>

        {/* Right side - Amount */}
        <div className="text-right">
          <p className={`text-lg font-semibold ${getAmountColor(transaction.transaction_type)}`}>
            {getAmountPrefix(transaction.transaction_type)}{formatCurrency(transaction.amount)}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            ID: {transaction.id.slice(0, 8)}...
          </p>
        </div>
      </div>
    </div>
  )
}
