import { useState } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { Fragment } from 'react'
import { XMarkIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import { useRedeemInvestment } from '../../hooks/useInvestments'
import LoadingSpinner from '../common/LoadingSpinner'
import type { InvestmentHolding } from '../../types/investment'

interface RedemptionModalProps {
  isOpen: boolean
  onClose: () => void
  holding: InvestmentHolding | null
}

export default function RedemptionModal({ isOpen, onClose, holding }: RedemptionModalProps) {
  const [isConfirming, setIsConfirming] = useState(false)
  const redeemMutation = useRedeemInvestment()

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      minimumFractionDigits: 2,
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-CN')
  }

  const handleRedeem = async () => {
    if (!holding) return

    setIsConfirming(true)
    try {
      await redeemMutation.mutateAsync({
        holding_id: holding.id,
        // 全额赎回：不传 shares 字段，后端会自动处理为全额赎回
      })

      // 成功后关闭模态框
      onClose()
    } catch (error) {
      console.error('Redemption failed:', error)
      // 错误处理已在 mutation 中处理
    } finally {
      setIsConfirming(false)
    }
  }

  const handleClose = () => {
    if (isConfirming) return // 防止在处理过程中关闭
    onClose()
  }

  if (!holding) return null

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={handleClose}>
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
                <div className="flex items-center justify-between mb-4">
                  <Dialog.Title as="h3" className="text-lg font-medium leading-6 text-gray-900">
                    确认赎回
                  </Dialog.Title>
                  <button
                    onClick={handleClose}
                    disabled={isConfirming}
                    className="rounded-md text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>

                {/* Warning */}
                <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                  <div className="flex">
                    <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400 mr-2 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-yellow-700">
                      <p className="font-medium">赎回提醒</p>
                      <p className="mt-1">赎回后资金将返回到您的账户，此操作不可撤销。</p>
                    </div>
                  </div>
                </div>

                {/* Holding Details */}
                <div className="mb-6 space-y-3">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-3">{holding.product_name}</h4>
                    
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <span className="text-gray-500">持有份额</span>
                        <p className="font-medium">{(holding.shares || 0).toLocaleString()}</p>
                      </div>
                      <div>
                        <span className="text-gray-500">当前价值</span>
                        <p className="font-medium">{formatCurrency(holding.current_value || 0)}</p>
                      </div>
                      <div>
                        <span className="text-gray-500">总投入</span>
                        <p className="font-medium">{formatCurrency(holding.total_invested || 0)}</p>
                      </div>
                      <div>
                        <span className="text-gray-500">盈亏</span>
                        <p className={`font-medium ${(holding.unrealized_gain_loss || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {(holding.unrealized_gain_loss || 0) >= 0 ? '+' : ''}{formatCurrency(holding.unrealized_gain_loss || 0)}
                        </p>
                      </div>
                      <div className="col-span-2">
                        <span className="text-gray-500">购买日期</span>
                        <p className="font-medium">{formatDate(holding.purchase_date)}</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-blue-50 p-3 rounded-md">
                    <p className="text-sm text-blue-700">
                      <span className="font-medium">预计到账金额：</span>
                      {formatCurrency(holding.current_value || 0)}
                    </p>
                  </div>
                </div>

                {/* Error Message */}
                {redeemMutation.error && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                    <p className="text-sm text-red-700">
                      赎回失败：{redeemMutation.error.message || '请稍后重试'}
                    </p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex space-x-3">
                  <button
                    onClick={handleClose}
                    disabled={isConfirming}
                    className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    取消
                  </button>
                  <button
                    onClick={handleRedeem}
                    disabled={isConfirming}
                    className="flex-1 px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 flex items-center justify-center"
                  >
                    {isConfirming ? (
                      <>
                        <LoadingSpinner size="sm" className="mr-2" />
                        处理中...
                      </>
                    ) : (
                      '确认赎回'
                    )}
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}
