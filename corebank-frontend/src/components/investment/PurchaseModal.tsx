import { useState, useEffect } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { Fragment } from 'react'
import { Link } from 'react-router-dom'
import {
  XMarkIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline'
import { useAccounts } from '../../hooks/useAccounts'
import { usePurchaseInvestment, useRiskAssessment } from '../../hooks/useInvestments'
import LoadingSpinner from '../common/LoadingSpinner'
import { InvestmentProduct, InvestmentPurchaseRequest } from '../../types/investment'

interface PurchaseModalProps {
  isOpen: boolean
  onClose: () => void
  product: InvestmentProduct | null
}

export default function PurchaseModal({ isOpen, onClose, product }: PurchaseModalProps) {
  const [selectedAccountId, setSelectedAccountId] = useState('')
  const [amount, setAmount] = useState('')
  const [errors, setErrors] = useState<string[]>([])

  const { data: accounts } = useAccounts()
  const { data: riskAssessment } = useRiskAssessment()
  const purchaseMutation = usePurchaseInvestment()

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setSelectedAccountId('')
      setAmount('')
      setErrors([])
    }
  }, [isOpen])

  // Auto-select first account if only one available
  useEffect(() => {
    if (accounts && accounts.length === 1 && !selectedAccountId) {
      setSelectedAccountId(accounts[0].id)
    }
  }, [accounts, selectedAccountId])

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      minimumFractionDigits: 0,
    }).format(amount)
  }

  const validateForm = (): boolean => {
    const newErrors: string[] = []

    if (!selectedAccountId) {
      newErrors.push('请选择付款账户')
    }

    if (!amount || isNaN(Number(amount))) {
      newErrors.push('请输入有效的投资金额')
    } else {
      const amountNum = Number(amount)
      
      if (product) {
        if (amountNum < product.min_investment_amount) {
          newErrors.push(`投资金额不能少于${formatCurrency(product.min_investment_amount)}`)
        }
        
        if (product.max_investment_amount && amountNum > product.max_investment_amount) {
          newErrors.push(`投资金额不能超过${formatCurrency(product.max_investment_amount)}`)
        }
      }

      // Check account balance
      const selectedAccount = accounts?.find(acc => acc.id === selectedAccountId)
      if (selectedAccount && amountNum > Number(selectedAccount.balance)) {
        newErrors.push('账户余额不足')
      }
    }

    setErrors(newErrors)
    return newErrors.length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm() || !product) {
      return
    }

    try {
      const purchaseRequest: InvestmentPurchaseRequest = {
        account_id: selectedAccountId,
        product_id: product.id,
        amount: Number(amount)
      }

      await purchaseMutation.mutateAsync(purchaseRequest)
      onClose()
      
      // Show success message (you might want to use a toast notification)
      alert('投资申购成功！')
    } catch (error) {
      console.error('Purchase failed:', error)
      // Extract error message from API response
      let errorMessage = '购买失败，请重试'
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as any
        if (axiosError.response?.data?.detail) {
          errorMessage = axiosError.response.data.detail
        } else if (axiosError.response?.data?.errors) {
          errorMessage = axiosError.response.data.errors.map((e: any) => e.message).join(', ')
        }
      }
      setErrors([errorMessage])
    }
  }

  const selectedAccount = accounts?.find(acc => acc.id === selectedAccountId)

  if (!product) return null

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                  <Dialog.Title as="h3" className="text-lg font-medium leading-6 text-gray-900">
                    购买理财产品
                  </Dialog.Title>
                  <button
                    onClick={onClose}
                    className="rounded-md text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>

                {/* Product Info */}
                <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-medium text-gray-900">{product.name}</h4>
                  <p className="text-sm text-gray-600 mt-1">{product.product_code}</p>
                  {product.expected_return_rate && (
                    <p className="text-sm text-green-600 mt-1">
                      预期年化收益率：{product.expected_return_rate ? (product.expected_return_rate * 100).toFixed(2) : '0.00'}%
                    </p>
                  )}
                </div>

                {/* Risk Assessment Check */}
                {!riskAssessment && (
                  <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <div className="flex items-start">
                      <ShieldCheckIcon className="h-5 w-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
                      <div className="flex-1">
                        <h4 className="text-sm font-medium text-yellow-800">需要完成风险评估</h4>
                        <p className="mt-1 text-sm text-yellow-700">
                          购买理财产品前，您需要先完成风险承受能力评估。
                        </p>
                        <div className="mt-3">
                          <Link
                            to="/investments/risk-assessment"
                            onClick={onClose}
                            className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-yellow-600 hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
                          >
                            立即评估
                          </Link>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Form */}
                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Account Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      付款账户
                    </label>
                    <select
                      value={selectedAccountId}
                      onChange={(e) => setSelectedAccountId(e.target.value)}
                      className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                      disabled={!riskAssessment}
                      required
                    >
                      <option value="">请选择账户</option>
                      {accounts?.map((account) => (
                        <option key={account.id} value={account.id}>
                          {account.account_number} - 余额：{formatCurrency(Number(account.balance))}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Amount Input */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      投资金额
                    </label>
                    <div className="relative">
                      <input
                        type="number"
                        value={amount}
                        onChange={(e) => setAmount(e.target.value)}
                        placeholder={riskAssessment ? "请输入投资金额" : "请先完成风险评估"}
                        min={product.min_investment_amount}
                        max={product.max_investment_amount || undefined}
                        step="0.01"
                        className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                        disabled={!riskAssessment}
                        required
                      />
                      <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <span className="text-gray-500 sm:text-sm">元</span>
                      </div>
                    </div>
                    <div className="mt-1 text-xs text-gray-500">
                      最低投资金额：{formatCurrency(product.min_investment_amount)}
                      {product.max_investment_amount && (
                        <>，最高投资金额：{formatCurrency(product.max_investment_amount)}</>
                      )}
                    </div>
                  </div>

                  {/* Account Balance Info */}
                  {selectedAccount && (
                    <div className="p-3 bg-blue-50 rounded-md">
                      <div className="flex">
                        <InformationCircleIcon className="h-5 w-5 text-blue-400" />
                        <div className="ml-3">
                          <p className="text-sm text-blue-700">
                            账户余额：{formatCurrency(Number(selectedAccount.balance))}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Errors */}
                  {errors.length > 0 && (
                    <div className="p-3 bg-red-50 rounded-md">
                      <div className="flex">
                        <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
                        <div className="ml-3">
                          <ul className="text-sm text-red-700 space-y-1">
                            {errors.map((error, index) => (
                              <li key={index}>{error}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={onClose}
                      className="flex-1 bg-gray-100 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                    >
                      取消
                    </button>
                    <button
                      type="submit"
                      disabled={!riskAssessment || purchaseMutation.isPending}
                      className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {purchaseMutation.isPending ? (
                        <div className="flex items-center justify-center">
                          <LoadingSpinner size="sm" />
                          <span className="ml-2">处理中...</span>
                        </div>
                      ) : !riskAssessment ? (
                        '需要完成风险评估'
                      ) : (
                        '确认购买'
                      )}
                    </button>
                  </div>
                </form>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}
