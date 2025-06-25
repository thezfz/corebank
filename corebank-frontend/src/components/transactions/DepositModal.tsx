import { useState, useEffect } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { useTransactionOperations } from '../../hooks/useTransactions'
import { useAccounts } from '../../hooks/useAccounts'
import type { Account } from '../../types/api'
import LoadingSpinner from '../common/LoadingSpinner'

interface DepositModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
  preselectedAccountId?: string
}

export default function DepositModal({ 
  isOpen, 
  onClose, 
  onSuccess, 
  preselectedAccountId 
}: DepositModalProps) {
  const [selectedAccountId, setSelectedAccountId] = useState(preselectedAccountId || '')
  const [amount, setAmount] = useState('')
  const [description, setDescription] = useState('')
  
  const { data: accounts } = useAccounts()
  const { deposit, isDepositing, depositErrorMessages } = useTransactionOperations()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!selectedAccountId || !amount) {
      return
    }

    const depositData = {
      account_id: selectedAccountId,
      amount: amount,
      description: description || undefined
    }

    deposit(depositData, {
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
    if (!isDepositing) {
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
            <h3 className="text-lg font-semibold text-gray-900">存款</h3>
            <button
              onClick={handleClose}
              disabled={isDepositing}
              className="text-gray-400 hover:text-gray-600 disabled:cursor-not-allowed"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Error Messages */}
          {depositErrorMessages.length > 0 && (
            <div className="mb-4 rounded-lg bg-red-50 border border-red-200 p-4">
              <div className="flex items-start">
                <svg className="h-5 w-5 text-red-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <div>
                  <h3 className="text-sm font-medium text-red-800">存款失败</h3>
                  <ul className="text-sm text-red-700 mt-1 list-disc list-inside">
                    {depositErrorMessages.map((message, index) => (
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
                disabled={isDepositing || !!preselectedAccountId}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
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
                  当前余额: ¥{parseFloat(selectedAccount.balance).toLocaleString('zh-CN', { minimumFractionDigits: 2 })}
                </p>
              )}
            </div>

            {/* Amount */}
            <div>
              <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-2">
                存款金额
              </label>
              <div className="relative">
                <span className="absolute left-3 top-2 text-gray-500">¥</span>
                <input
                  id="amount"
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  disabled={isDepositing}
                  required
                  className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                  placeholder="0.00"
                />
              </div>
              <p className="mt-1 text-xs text-gray-500">
                最小存款金额: ¥0.01
              </p>
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
                disabled={isDepositing}
                maxLength={255}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                placeholder="存款备注"
              />
            </div>

            {/* Buttons */}
            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={handleClose}
                disabled={isDepositing}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                取消
              </button>
              <button
                type="submit"
                disabled={isDepositing || !selectedAccountId || !amount}
                className="flex-1 px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:bg-green-400 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isDepositing ? (
                  <>
                    <LoadingSpinner size="sm" className="mr-2" />
                    存款中...
                  </>
                ) : (
                  '确认存款'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
