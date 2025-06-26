import { useState, useEffect } from 'react'
import { XMarkIcon, ArrowRightIcon, MagnifyingGlassIcon, CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline'
import { useTransactionOperations, useAccountLookup } from '../../hooks/useTransactions'
import { useAccounts } from '../../hooks/useAccounts'
import type { Account, AccountLookupResponse } from '../../types/api'
import LoadingSpinner from '../common/LoadingSpinner'

interface CrossUserTransferModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
  preselectedFromAccountId?: string
}

export default function CrossUserTransferModal({ 
  isOpen, 
  onClose, 
  onSuccess, 
  preselectedFromAccountId 
}: CrossUserTransferModalProps) {
  const [fromAccountId, setFromAccountId] = useState(preselectedFromAccountId || '')
  const [toAccountNumber, setToAccountNumber] = useState('')
  const [amount, setAmount] = useState('')
  const [description, setDescription] = useState('')
  const [lookupAccountNumber, setLookupAccountNumber] = useState('')
  const [shouldLookup, setShouldLookup] = useState(false)
  
  const { data: accounts } = useAccounts()
  const { transferByAccountNumber, isTransferringByAccountNumber, transferByAccountNumberErrorMessages } = useTransactionOperations()
  
  // Account lookup
  const { data: lookupResult, isLoading: isLookingUp, error: lookupError } = useAccountLookup(
    lookupAccountNumber, 
    shouldLookup
  )

  const handleLookup = () => {
    if (toAccountNumber.trim()) {
      setLookupAccountNumber(toAccountNumber.trim())
      setShouldLookup(true)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!fromAccountId || !toAccountNumber || !amount) {
      return
    }

    const transferData = {
      from_account_id: fromAccountId,
      to_account_number: toAccountNumber,
      amount: amount,
      description: description || undefined
    }

    transferByAccountNumber(transferData, {
      onSuccess: () => {
        // Reset form
        setFromAccountId(preselectedFromAccountId || '')
        setToAccountNumber('')
        setAmount('')
        setDescription('')
        setLookupAccountNumber('')
        setShouldLookup(false)
        
        // Call success callback
        onSuccess?.()
        
        // Close modal
        onClose()
      }
    })
  }

  const handleClose = () => {
    if (!isTransferringByAccountNumber) {
      // Reset form when closing
      setFromAccountId(preselectedFromAccountId || '')
      setToAccountNumber('')
      setAmount('')
      setDescription('')
      setLookupAccountNumber('')
      setShouldLookup(false)
      onClose()
    }
  }

  // Reset lookup when account number changes
  useEffect(() => {
    if (toAccountNumber !== lookupAccountNumber) {
      setShouldLookup(false)
      setLookupAccountNumber('')
    }
  }, [toAccountNumber, lookupAccountNumber])

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setFromAccountId(preselectedFromAccountId || '')
    }
  }, [isOpen, preselectedFromAccountId])

  if (!isOpen) return null

  const fromAccount = accounts?.find(acc => acc.id === fromAccountId)
  const availableBalance = fromAccount ? parseFloat(fromAccount.balance) : 0
  const transferAmount = parseFloat(amount) || 0
  const isValidAmount = transferAmount > 0 && transferAmount <= availableBalance

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
            <h3 className="text-lg font-semibold text-gray-900">跨用户转账</h3>
            <button
              onClick={handleClose}
              disabled={isTransferringByAccountNumber}
              className="text-gray-400 hover:text-gray-600 disabled:cursor-not-allowed"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* From Account */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                转出账户
              </label>
              <select
                value={fromAccountId}
                onChange={(e) => setFromAccountId(e.target.value)}
                disabled={isTransferringByAccountNumber || !!preselectedFromAccountId}
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

            {/* To Account Number */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                收款账户号码
              </label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={toAccountNumber}
                  onChange={(e) => setToAccountNumber(e.target.value)}
                  disabled={isTransferringByAccountNumber}
                  required
                  placeholder="请输入收款账户号码"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                />
                <button
                  type="button"
                  onClick={handleLookup}
                  disabled={!toAccountNumber.trim() || isLookingUp || isTransferringByAccountNumber}
                  className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  {isLookingUp ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    <MagnifyingGlassIcon className="h-4 w-4" />
                  )}
                </button>
              </div>
              
              {/* Lookup Result */}
              {shouldLookup && lookupResult && (
                <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <CheckCircleIcon className="h-5 w-5 text-green-600" />
                    <div>
                      <p className="text-sm font-medium text-green-800">
                        找到账户: {lookupResult.account_type === 'checking' ? '支票账户' : '储蓄账户'}
                      </p>
                      {lookupResult.owner_name && (
                        <p className="text-sm text-green-700">
                          账户持有人: {lookupResult.owner_name}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}
              
              {shouldLookup && lookupError && (
                <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <ExclamationCircleIcon className="h-5 w-5 text-red-600" />
                    <p className="text-sm text-red-800">
                      未找到该账户号码，请检查后重试
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Amount */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                转账金额
              </label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">¥</span>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  max={availableBalance}
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  disabled={isTransferringByAccountNumber}
                  required
                  placeholder="0.00"
                  className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                />
              </div>
              {amount && !isValidAmount && (
                <p className="mt-1 text-sm text-red-600">
                  {transferAmount > availableBalance ? '转账金额不能超过可用余额' : '请输入有效金额'}
                </p>
              )}
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                转账说明 (可选)
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={isTransferringByAccountNumber}
                rows={3}
                placeholder="请输入转账说明..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 resize-none"
              />
            </div>

            {/* Error Messages */}
            {transferByAccountNumberErrorMessages.length > 0 && (
              <div className="rounded-lg bg-red-50 border border-red-200 p-4">
                <div className="flex">
                  <ExclamationCircleIcon className="h-5 w-5 text-red-400" />
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">转账失败</h3>
                    <div className="mt-2 text-sm text-red-700">
                      <ul className="list-disc list-inside space-y-1">
                        {transferByAccountNumberErrorMessages.map((message, index) => (
                          <li key={index}>{message}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Transfer Summary */}
            {fromAccount && lookupResult && amount && isValidAmount && (
              <div className="rounded-lg bg-blue-50 border border-blue-200 p-4">
                <h4 className="text-sm font-medium text-blue-800 mb-2">转账确认</h4>
                <div className="text-sm text-blue-700 space-y-1">
                  <div className="flex justify-between">
                    <span>转出账户:</span>
                    <span>**** {fromAccount.account_number.slice(-4)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>收款账户:</span>
                    <span>{lookupResult.account_number}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>转账金额:</span>
                    <span className="font-medium">¥{transferAmount.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}</span>
                  </div>
                  {description && (
                    <div className="flex justify-between">
                      <span>转账说明:</span>
                      <span>{description}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={handleClose}
                disabled={isTransferringByAccountNumber}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                取消
              </button>
              <button
                type="submit"
                disabled={
                  !fromAccountId || 
                  !toAccountNumber || 
                  !amount || 
                  !isValidAmount || 
                  isTransferringByAccountNumber ||
                  (shouldLookup && !lookupResult)
                }
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isTransferringByAccountNumber ? (
                  <>
                    <LoadingSpinner size="sm" className="mr-2" />
                    转账中...
                  </>
                ) : (
                  <>
                    <ArrowRightIcon className="h-4 w-4 mr-2" />
                    确认转账
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
