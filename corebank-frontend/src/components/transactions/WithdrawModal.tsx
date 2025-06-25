import { useState, useEffect } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { useTransactionOperations } from '../../hooks/useTransactions'
import { useAccounts } from '../../hooks/useAccounts'
import type { Account } from '../../types/api'
import LoadingSpinner from '../common/LoadingSpinner'

interface WithdrawModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
  preselectedAccountId?: string
}

export default function WithdrawModal({ 
  isOpen, 
  onClose, 
  onSuccess, 
  preselectedAccountId 
}: WithdrawModalProps) {
  const [selectedAccountId, setSelectedAccountId] = useState(preselectedAccountId || '')
  const [amount, setAmount] = useState('')
  const [description, setDescription] = useState('')
  
  const { data: accounts } = useAccounts()
  const { withdraw, isWithdrawing, withdrawErrorMessages } = useTransactionOperations()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!selectedAccountId || !amount) {
      return
    }

    const withdrawData = {
      account_id: selectedAccountId,
      amount: amount,
      description: description || undefined
    }

    withdraw(withdrawData, {
      onSuccess: () => {
        // Reset form
        setSelectedAccountId(preselectedAccountId || '')
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
    if (!isWithdrawing) {
      // Reset form when closing
      setSelectedAccountId(preselectedAccountId || '')
      setAmount('')
      setDescription('')
      onClose()
    }
  }

  // Update selected account when preselected changes
  useEffect(() => {
    if (preselectedAccountId) {
      setSelectedAccountId(preselectedAccountId)
    }
  }, [preselectedAccountId])

  if (!isOpen) return null

  const selectedAccount = accounts?.find(acc => acc.id === selectedAccountId)
  const availableBalance = selectedAccount ? parseFloat(selectedAccount.balance) : 0

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={handleClose}
        />
        
        {/* Modal */}
        <div className="relative w-full max-w-md transform rounded-lg bg-white p-6 shadow-xl transition-all">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">取款</h3>
            <button
              onClick={handleClose}
              disabled={isWithdrawing}
              className="text-gray-400 hover:text-gray-600 disabled:cursor-not-allowed"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Error Messages */}
          {withdrawErrorMessages.length > 0 && (
            <div className="mb-4 rounded-lg bg-red-50 border border-red-200 p-4">
              <div className="flex items-start">
                <svg className="h-5 w-5 text-red-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <div>
                  <h3 className="text-sm font-medium text-red-800">取款失败</h3>
                  <ul className="text-sm text-red-700 mt-1 list-disc list-inside">
                    {withdrawErrorMessages.map((message, index) => (
                      <li key={index}>{message}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Account Selection */}
            <div>
              <label htmlFor="account" className="block text-sm font-medium text-gray-700 mb-2">
                选择账户
              </label>
              <select
                id="account"
                value={selectedAccountId}
                onChange={(e) => setSelectedAccountId(e.target.value)}
                disabled={isWithdrawing || !!preselectedAccountId}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                <option value="">请选择账户</option>
                {accounts?.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.account_type === 'checking' ? '支票账户' : '储蓄账户'} - 
                    **** {account.account_number.slice(-4)} - 
                    ¥{parseFloat(account.balance).toLocaleString('zh-CN', { minimumFractionDigits: 2 })}
                  </option>
                ))}
              </select>
              {selectedAccount && (
                <p className="mt-1 text-xs text-gray-500">
                  可用余额: ¥{availableBalance.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}
                </p>
              )}
            </div>

            {/* Amount */}
            <div>
              <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-2">
                取款金额
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
                  disabled={isWithdrawing}
                  required
                  className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                  placeholder="0.00"
                />
              </div>
              <div className="mt-1 flex justify-between text-xs text-gray-500">
                <span>最小取款金额: ¥0.01</span>
                {selectedAccount && (
                  <button
                    type="button"
                    onClick={() => setAmount(availableBalance.toString())}
                    disabled={isWithdrawing || availableBalance <= 0}
                    className="text-red-600 hover:text-red-700 disabled:text-gray-400 disabled:cursor-not-allowed"
                  >
                    全部取出
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
                disabled={isWithdrawing}
                maxLength={255}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                placeholder="取款备注"
              />
            </div>

            {/* Warning for large amounts */}
            {amount && parseFloat(amount) > 10000 && (
              <div className="rounded-lg bg-yellow-50 border border-yellow-200 p-3">
                <div className="flex items-start">
                  <svg className="h-5 w-5 text-yellow-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <p className="text-sm text-yellow-700">
                    大额取款提醒：您正在取款 ¥{parseFloat(amount).toLocaleString('zh-CN', { minimumFractionDigits: 2 })}，请确认金额无误。
                  </p>
                </div>
              </div>
            )}

            {/* Buttons */}
            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={handleClose}
                disabled={isWithdrawing}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                取消
              </button>
              <button
                type="submit"
                disabled={isWithdrawing || !selectedAccountId || !amount || parseFloat(amount) > availableBalance}
                className="flex-1 px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:bg-red-400 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isWithdrawing ? (
                  <>
                    <LoadingSpinner size="sm" className="mr-2" />
                    取款中...
                  </>
                ) : (
                  '确认取款'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
