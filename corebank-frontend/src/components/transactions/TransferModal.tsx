import { useState, useEffect } from 'react'
import { XMarkIcon, ArrowRightIcon } from '@heroicons/react/24/outline'
import { useTransactionOperations } from '../../hooks/useTransactions'
import { useAccounts } from '../../hooks/useAccounts'
import type { Account } from '../../types/api'
import LoadingSpinner from '../common/LoadingSpinner'

interface TransferModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
  preselectedFromAccountId?: string
}

export default function TransferModal({ 
  isOpen, 
  onClose, 
  onSuccess, 
  preselectedFromAccountId 
}: TransferModalProps) {
  const [fromAccountId, setFromAccountId] = useState(preselectedFromAccountId || '')
  const [toAccountId, setToAccountId] = useState('')
  const [amount, setAmount] = useState('')
  const [description, setDescription] = useState('')
  
  const { data: accounts } = useAccounts()
  const { transfer, isTransferring, transferErrorMessages } = useTransactionOperations()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!fromAccountId || !toAccountId || !amount) {
      return
    }

    const transferData = {
      from_account_id: fromAccountId,
      to_account_id: toAccountId,
      amount: amount,
      description: description || undefined
    }

    transfer(transferData, {
      onSuccess: () => {
        // Reset form
        setFromAccountId(preselectedFromAccountId || '')
        setToAccountId('')
        setAmount('')
        setDescription('')
        
        // Call success callback
        onSuccess?.()
        
        // Close modal
        onClose()
      }
    })
  }

  const handleClose = () => {
    if (!isTransferring) {
      // Reset form when closing
      setFromAccountId(preselectedFromAccountId || '')
      setToAccountId('')
      setAmount('')
      setDescription('')
      onClose()
    }
  }

  // Update from account when preselected changes
  useEffect(() => {
    if (preselectedFromAccountId) {
      setFromAccountId(preselectedFromAccountId)
    }
  }, [preselectedFromAccountId])

  if (!isOpen) return null

  const fromAccount = accounts?.find(acc => acc.id === fromAccountId)
  const toAccount = accounts?.find(acc => acc.id === toAccountId)
  const availableBalance = fromAccount ? parseFloat(fromAccount.balance) : 0
  
  // Filter out the selected from account from to account options
  const availableToAccounts = accounts?.filter(acc => acc.id !== fromAccountId) || []

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={handleClose}
        />
        
        {/* Modal */}
        <div className="relative w-full max-w-lg transform rounded-lg bg-white p-6 shadow-xl transition-all">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">转账</h3>
            <button
              onClick={handleClose}
              disabled={isTransferring}
              className="text-gray-400 hover:text-gray-600 disabled:cursor-not-allowed"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Error Messages */}
          {transferErrorMessages.length > 0 && (
            <div className="mb-4 rounded-lg bg-red-50 border border-red-200 p-4">
              <div className="flex items-start">
                <svg className="h-5 w-5 text-red-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <div>
                  <h3 className="text-sm font-medium text-red-800">转账失败</h3>
                  <ul className="text-sm text-red-700 mt-1 list-disc list-inside">
                    {transferErrorMessages.map((message, index) => (
                      <li key={index}>{message}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* From Account */}
            <div>
              <label htmlFor="fromAccount" className="block text-sm font-medium text-gray-700 mb-2">
                转出账户
              </label>
              <select
                id="fromAccount"
                value={fromAccountId}
                onChange={(e) => {
                  setFromAccountId(e.target.value)
                  // Clear to account if it's the same as from account
                  if (toAccountId === e.target.value) {
                    setToAccountId('')
                  }
                }}
                disabled={isTransferring || !!preselectedFromAccountId}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                <option value="">请选择转出账户</option>
                {accounts?.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.account_type === 'checking' ? '支票账户' : '储蓄账户'} - 
                    **** {account.account_number.slice(-4)} - 
                    ¥{parseFloat(account.balance).toLocaleString('zh-CN', { minimumFractionDigits: 2 })}
                  </option>
                ))}
              </select>
              {fromAccount && (
                <p className="mt-1 text-xs text-gray-500">
                  可用余额: ¥{availableBalance.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}
                </p>
              )}
            </div>

            {/* Transfer Direction Indicator */}
            {fromAccount && (
              <div className="flex items-center justify-center py-2">
                <ArrowRightIcon className="h-6 w-6 text-blue-500" />
              </div>
            )}

            {/* To Account */}
            <div>
              <label htmlFor="toAccount" className="block text-sm font-medium text-gray-700 mb-2">
                转入账户
              </label>
              <select
                id="toAccount"
                value={toAccountId}
                onChange={(e) => setToAccountId(e.target.value)}
                disabled={isTransferring || !fromAccountId}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                <option value="">请选择转入账户</option>
                {availableToAccounts.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.account_type === 'checking' ? '支票账户' : '储蓄账户'} - 
                    **** {account.account_number.slice(-4)} - 
                    ¥{parseFloat(account.balance).toLocaleString('zh-CN', { minimumFractionDigits: 2 })}
                  </option>
                ))}
              </select>
              {!fromAccountId && (
                <p className="mt-1 text-xs text-gray-500">
                  请先选择转出账户
                </p>
              )}
              {fromAccountId && availableToAccounts.length === 0 && (
                <p className="mt-1 text-xs text-red-500">
                  没有可用的转入账户，请先创建其他账户
                </p>
              )}
            </div>

            {/* Amount */}
            <div>
              <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-2">
                转账金额
              </label>
              <div className="relative">
                <span className="absolute left-3 top-2 text-gray-500">¥</span>
                <input
                  id="amount"
                  type="number"
                  min="0.01"
                  max={availableBalance}
                  step="0.01"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  disabled={isTransferring}
                  required
                  className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                  placeholder="0.00"
                />
              </div>
              <div className="mt-1 flex justify-between text-xs text-gray-500">
                <span>最小转账金额: ¥0.01</span>
                {fromAccount && (
                  <button
                    type="button"
                    onClick={() => setAmount(availableBalance.toString())}
                    disabled={isTransferring || availableBalance <= 0}
                    className="text-blue-600 hover:text-blue-700 disabled:text-gray-400 disabled:cursor-not-allowed"
                  >
                    全部转出
                  </button>
                )}
              </div>
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                备注 (可选)
              </label>
              <input
                id="description"
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={isTransferring}
                maxLength={255}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                placeholder="转账备注"
              />
            </div>

            {/* Transfer Summary */}
            {fromAccount && toAccount && amount && (
              <div className="rounded-lg bg-blue-50 border border-blue-200 p-4">
                <h4 className="text-sm font-medium text-blue-800 mb-2">转账确认</h4>
                <div className="text-sm text-blue-700 space-y-1">
                  <div className="flex justify-between">
                    <span>转出账户:</span>
                    <span>**** {fromAccount.account_number.slice(-4)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>转入账户:</span>
                    <span>**** {toAccount.account_number.slice(-4)}</span>
                  </div>
                  <div className="flex justify-between font-medium">
                    <span>转账金额:</span>
                    <span>¥{parseFloat(amount).toLocaleString('zh-CN', { minimumFractionDigits: 2 })}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Buttons */}
            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={handleClose}
                disabled={isTransferring}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                取消
              </button>
              <button
                type="submit"
                disabled={
                  isTransferring || 
                  !fromAccountId || 
                  !toAccountId || 
                  !amount || 
                  parseFloat(amount) > availableBalance ||
                  availableToAccounts.length === 0
                }
                className="flex-1 px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-400 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isTransferring ? (
                  <>
                    <LoadingSpinner size="sm" className="mr-2" />
                    转账中...
                  </>
                ) : (
                  '确认转账'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
