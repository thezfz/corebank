import React, { useState } from 'react'
import { XMarkIcon, ClipboardDocumentIcon, ArrowsRightLeftIcon, PlusIcon, MinusIcon } from '@heroicons/react/24/outline'
import { CreditCardIcon, BanknotesIcon } from '@heroicons/react/24/outline'
import type { Account } from '../../types/api'

interface AccountDetailModalProps {
  isOpen: boolean
  onClose: () => void
  account: Account
  onTransfer?: (accountId: string) => void
  onDeposit?: (accountId: string) => void
  onWithdraw?: (accountId: string) => void
}

export default function AccountDetailModal({
  isOpen,
  onClose,
  account,
  onTransfer,
  onDeposit,
  onWithdraw
}: AccountDetailModalProps) {
  const [copySuccess, setCopySuccess] = useState<string | null>(null)

  if (!isOpen) return null

  const formatCurrency = (amount: string) => {
    const num = parseFloat(amount)
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      minimumFractionDigits: 2,
    }).format(num)
  }

  const formatAccountNumber = (accountNumber: string) => {
    // Format full number with spaces: 1234 5678 9012 3456
    return accountNumber.replace(/(.{4})/g, '$1 ').trim()
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

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopySuccess(type)
      setTimeout(() => setCopySuccess(null), 2000)
    } catch (err) {
      console.error('Failed to copy: ', err)
    }
  }

  const Icon = getAccountIcon(account.account_type)
  const balance = parseFloat(account.balance)
  const isNegative = balance < 0

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={onClose}
        />
        
        {/* Modal */}
        <div className="relative w-full max-w-lg transform rounded-lg bg-white p-6 shadow-xl transition-all">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Icon className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">
                {getAccountTypeLabel(account.account_type)}
              </h3>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Account Details */}
          <div className="space-y-6">
            {/* Account Number */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                账户号码
              </label>
              <div className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg">
                <span className="font-mono text-lg text-gray-900 flex-1">
                  {formatAccountNumber(account.account_number)}
                </span>
                <button
                  onClick={() => copyToClipboard(account.account_number, 'account')}
                  className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                  title={copySuccess === 'account' ? "已复制!" : "复制账户号码"}
                >
                  <ClipboardDocumentIcon className="h-5 w-5" />
                </button>
              </div>
              {copySuccess === 'account' && (
                <p className="text-sm text-green-600 mt-1">账户号码已复制到剪贴板</p>
              )}
            </div>

            {/* Account ID */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                账户ID
              </label>
              <div className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg">
                <span className="font-mono text-sm text-gray-600 flex-1">
                  {account.id}
                </span>
                <button
                  onClick={() => copyToClipboard(account.id, 'id')}
                  className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                  title={copySuccess === 'id' ? "已复制!" : "复制账户ID"}
                >
                  <ClipboardDocumentIcon className="h-5 w-5" />
                </button>
              </div>
              {copySuccess === 'id' && (
                <p className="text-sm text-green-600 mt-1">账户ID已复制到剪贴板</p>
              )}
            </div>

            {/* Balance */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                当前余额
              </label>
              <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg">
                <p className={`text-3xl font-bold ${
                  isNegative ? 'text-red-600' : 'text-green-600'
                }`}>
                  {formatCurrency(account.balance)}
                </p>
              </div>
            </div>

            {/* Account Info */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  账户类型
                </label>
                <p className="text-sm text-gray-900">
                  {getAccountTypeLabel(account.account_type)}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  创建时间
                </label>
                <p className="text-sm text-gray-900">
                  {new Date(account.created_at).toLocaleDateString('zh-CN')}
                </p>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="mt-8 flex flex-col space-y-3">
            <div className="grid grid-cols-3 gap-3">
              {onDeposit && (
                <button
                  onClick={() => {
                    onDeposit(account.id)
                    onClose()
                  }}
                  className="flex items-center justify-center px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
                >
                  <PlusIcon className="h-4 w-4 mr-1" />
                  存款
                </button>
              )}
              
              {onWithdraw && (
                <button
                  onClick={() => {
                    onWithdraw(account.id)
                    onClose()
                  }}
                  className="flex items-center justify-center px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 transition-colors"
                >
                  <MinusIcon className="h-4 w-4 mr-1" />
                  取款
                </button>
              )}
              
              {onTransfer && (
                <button
                  onClick={() => {
                    onTransfer(account.id)
                    onClose()
                  }}
                  className="flex items-center justify-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <ArrowsRightLeftIcon className="h-4 w-4 mr-1" />
                  转账
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
