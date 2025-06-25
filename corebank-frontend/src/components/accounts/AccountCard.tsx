import React from 'react'
import { CreditCardIcon, BanknotesIcon } from '@heroicons/react/24/outline'
import type { Account } from '../../types/api'

interface AccountCardProps {
  account: Account
  onClick?: () => void
}

export default function AccountCard({ account, onClick }: AccountCardProps) {
  const formatCurrency = (amount: string) => {
    const num = parseFloat(amount)
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      minimumFractionDigits: 2,
    }).format(num)
  }

  const formatAccountNumber = (accountNumber: string) => {
    // Format as: **** **** **** 1234
    if (accountNumber.length >= 4) {
      const lastFour = accountNumber.slice(-4)
      return `**** **** **** ${lastFour}`
    }
    return accountNumber
  }

  const getAccountTypeLabel = (type: string) => {
    switch (type) {
      case 'checking':
        return '支票账户'
      case 'savings':
        return '储蓄账户'
      default:
        return type
    }
  }

  const getAccountIcon = (type: string) => {
    switch (type) {
      case 'checking':
        return CreditCardIcon
      case 'savings':
        return BanknotesIcon
      default:
        return CreditCardIcon
    }
  }

  const Icon = getAccountIcon(account.account_type)
  const balance = parseFloat(account.balance)
  const isNegative = balance < 0

  return (
    <div 
      className={`bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow ${
        onClick ? 'cursor-pointer hover:border-blue-300' : ''
      }`}
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Icon className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {getAccountTypeLabel(account.account_type)}
            </h3>
            <p className="text-sm text-gray-500">
              {formatAccountNumber(account.account_number)}
            </p>
          </div>
        </div>
      </div>

      {/* Balance */}
      <div className="mb-4">
        <p className="text-sm text-gray-500 mb-1">当前余额</p>
        <p className={`text-2xl font-bold ${
          isNegative ? 'text-red-600' : 'text-green-600'
        }`}>
          {formatCurrency(account.balance)}
        </p>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between text-sm text-gray-500">
        <span>账户 ID: {account.id.slice(0, 8)}...</span>
        <span>
          创建于 {new Date(account.created_at).toLocaleDateString('zh-CN')}
        </span>
      </div>
    </div>
  )
}
