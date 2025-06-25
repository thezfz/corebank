import React, { useState } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { useAccountOperations } from '../../hooks/useAccounts'
import type { AccountType } from '../../types/api'
import LoadingSpinner from '../common/LoadingSpinner'

interface CreateAccountModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

export default function CreateAccountModal({ isOpen, onClose, onSuccess }: CreateAccountModalProps) {
  const [accountType, setAccountType] = useState<AccountType>('checking')
  const [initialDeposit, setInitialDeposit] = useState('')
  const { createAccount, isCreating, createErrorMessages } = useAccountOperations()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    const accountData = {
      account_type: accountType,
      initial_deposit: initialDeposit || undefined
    }

    createAccount(accountData, {
      onSuccess: () => {
        // Reset form
        setAccountType('checking')
        setInitialDeposit('')
        
        // Call success callback
        onSuccess?.()
        
        // Close modal
        onClose()
      }
    })
  }

  const handleClose = () => {
    if (!isCreating) {
      // Reset form when closing
      setAccountType('checking')
      setInitialDeposit('')
      onClose()
    }
  }

  if (!isOpen) return null

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
            <h3 className="text-lg font-semibold text-gray-900">创建新账户</h3>
            <button
              onClick={handleClose}
              disabled={isCreating}
              className="text-gray-400 hover:text-gray-600 disabled:cursor-not-allowed"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Error Messages */}
          {createErrorMessages.length > 0 && (
            <div className="mb-4 rounded-lg bg-red-50 border border-red-200 p-4">
              <div className="flex items-start">
                <svg className="h-5 w-5 text-red-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <div>
                  <h3 className="text-sm font-medium text-red-800">创建失败</h3>
                  <ul className="text-sm text-red-700 mt-1 list-disc list-inside">
                    {createErrorMessages.map((message, index) => (
                      <li key={index}>{message}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Account Type */}
            <div>
              <label htmlFor="accountType" className="block text-sm font-medium text-gray-700 mb-2">
                账户类型
              </label>
              <select
                id="accountType"
                value={accountType}
                onChange={(e) => setAccountType(e.target.value as AccountType)}
                disabled={isCreating}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                <option value="checking">支票账户</option>
                <option value="savings">储蓄账户</option>
              </select>
              <p className="mt-1 text-xs text-gray-500">
                {accountType === 'checking' ? '用于日常交易和支付' : '用于储蓄和获得利息'}
              </p>
            </div>

            {/* Initial Deposit */}
            <div>
              <label htmlFor="initialDeposit" className="block text-sm font-medium text-gray-700 mb-2">
                初始存款 (可选)
              </label>
              <div className="relative">
                <span className="absolute left-3 top-2 text-gray-500">¥</span>
                <input
                  id="initialDeposit"
                  type="number"
                  min="0"
                  step="0.01"
                  value={initialDeposit}
                  onChange={(e) => setInitialDeposit(e.target.value)}
                  disabled={isCreating}
                  className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                  placeholder="0.00"
                />
              </div>
              <p className="mt-1 text-xs text-gray-500">
                留空则创建零余额账户
              </p>
            </div>

            {/* Buttons */}
            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={handleClose}
                disabled={isCreating}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                取消
              </button>
              <button
                type="submit"
                disabled={isCreating}
                className="flex-1 px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-400 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isCreating ? (
                  <>
                    <LoadingSpinner size="sm" className="mr-2" />
                    创建中...
                  </>
                ) : (
                  '创建账户'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
