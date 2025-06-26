import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ChartBarIcon,
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  PlusIcon,
  EyeIcon,
  ArrowPathIcon,
  StarIcon
} from '@heroicons/react/24/outline'
import { useInvestmentSummary, usePortfolioSummary, useRiskAssessment } from '../hooks/useInvestments'
import { useAuth } from '../hooks/useAuth'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { RISK_LEVEL_LABELS, RISK_LEVEL_COLORS, PRODUCT_TYPE_LABELS } from '../types/investment'

export default function InvestmentDashboardPage() {
  const { user } = useAuth()

  try {
    const {
      isLoading,
      hasInvestments,
      hasRiskAssessment,
      productsCount,
      holdingsCount,
      totalAssets,
      totalReturnRate,
      riskLevel
    } = useInvestmentSummary()

    const { data: portfolio } = usePortfolioSummary()
    const { data: riskAssessment } = useRiskAssessment()

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      minimumFractionDigits: 2,
    }).format(amount)
  }

  const formatPercentage = (rate: number | undefined) => {
    if (typeof rate !== 'number' || isNaN(rate)) {
      return '0.00%'
    }
    return `${rate >= 0 ? '+' : ''}${rate.toFixed(2)}%`
  }

  if (isLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          投资理财
        </h1>
        <p className="mt-1 text-sm text-gray-600">
          欢迎使用数脉银行投资理财服务，让您的财富稳健增长
        </p>
      </div>

      {/* Risk Assessment Warning */}
      {!hasRiskAssessment && (
        <div className="mb-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-start">
            <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-lg font-medium text-yellow-800">完成风险评估</h3>
              <p className="mt-2 text-sm text-yellow-700">
                为了为您推荐合适的理财产品，请先完成风险承受能力评估。这将帮助我们了解您的投资偏好和风险承受能力。
              </p>
              <div className="mt-4">
                <Link
                  to="/investments/risk-assessment"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-yellow-600 hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
                >
                  <ShieldCheckIcon className="h-4 w-4 mr-2" />
                  开始风险评估
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Portfolio Summary Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {/* Total Assets */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CurrencyDollarIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">总资产</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {formatCurrency(totalAssets)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Total Return */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ArrowTrendingUpIcon className={`h-6 w-6 ${totalReturnRate >= 0 ? 'text-green-600' : 'text-red-600'}`} />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">总收益率</dt>
                  <dd className={`text-lg font-medium ${totalReturnRate >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatPercentage(totalReturnRate)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Holdings Count */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">持仓产品</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {holdingsCount} 个
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Risk Level */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ShieldCheckIcon 
                  className="h-6 w-6" 
                  style={{ color: riskLevel ? RISK_LEVEL_COLORS[riskLevel] : '#6B7280' }}
                />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">风险等级</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {riskLevel ? RISK_LEVEL_LABELS[riskLevel] : '未评估'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Asset Allocation */}
      {hasInvestments && portfolio?.asset_allocation && (
        <div className="mb-8 bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">资产配置</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {Object.entries(portfolio.asset_allocation).map(([type, percentage]) => (
                <div key={type} className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {typeof percentage === 'number' ? percentage.toFixed(1) : '0.0'}%
                  </div>
                  <div className="text-sm text-gray-500">
                    {PRODUCT_TYPE_LABELS[type as keyof typeof PRODUCT_TYPE_LABELS]}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">快速操作</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            
            {/* Browse Products */}
            <Link
              to="/investments/products"
              className="relative group bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg hover:bg-gray-100 text-center"
            >
              <div className="flex justify-center">
                <span className="rounded-lg inline-flex p-3 bg-blue-50 text-blue-700 ring-4 ring-white">
                  <EyeIcon className="h-6 w-6" />
                </span>
              </div>
              <div className="mt-4">
                <h3 className="text-lg font-medium text-gray-900">浏览产品</h3>
                <p className="mt-2 text-sm text-gray-500">
                  查看所有可投资的理财产品
                </p>
              </div>
            </Link>

            {/* My Holdings */}
            <Link
              to="/investments/holdings"
              className="relative group bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg hover:bg-gray-100 text-center"
            >
              <div className="flex justify-center">
                <span className="rounded-lg inline-flex p-3 bg-green-50 text-green-700 ring-4 ring-white">
                  <ChartBarIcon className="h-6 w-6" />
                </span>
              </div>
              <div className="mt-4">
                <h3 className="text-lg font-medium text-gray-900">我的持仓</h3>
                <p className="mt-2 text-sm text-gray-500">
                  查看和管理您的投资持仓
                </p>
              </div>
            </Link>

            {/* Transaction History */}
            <Link
              to="/investments/transactions"
              className="relative group bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg hover:bg-gray-100 text-center"
            >
              <div className="flex justify-center">
                <span className="rounded-lg inline-flex p-3 bg-purple-50 text-purple-700 ring-4 ring-white">
                  <ArrowPathIcon className="h-6 w-6" />
                </span>
              </div>
              <div className="mt-4">
                <h3 className="text-lg font-medium text-gray-900">交易记录</h3>
                <p className="mt-2 text-sm text-gray-500">
                  查看投资交易历史记录
                </p>
              </div>
            </Link>

            {/* Risk Assessment */}
            <Link
              to="/investments/risk-assessment"
              className="relative group bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg hover:bg-gray-100 text-center"
            >
              <div className="flex justify-center">
                <span className="rounded-lg inline-flex p-3 bg-yellow-50 text-yellow-700 ring-4 ring-white">
                  <ShieldCheckIcon className="h-6 w-6" />
                </span>
              </div>
              <div className="mt-4">
                <h3 className="text-lg font-medium text-gray-900">
                  {hasRiskAssessment ? '更新风险评估' : '风险评估'}
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  {hasRiskAssessment ? '更新您的风险承受能力' : '评估您的风险承受能力'}
                </p>
              </div>
            </Link>
          </div>
        </div>
      </div>

      {/* No Investments State */}
      {!hasInvestments && hasRiskAssessment && (
        <div className="mt-8 text-center py-12">
          <div className="mx-auto h-12 w-12 text-gray-400">
            <ChartBarIcon className="h-12 w-12" />
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">开始您的投资之旅</h3>
          <p className="mt-1 text-sm text-gray-500">
            您已完成风险评估，现在可以开始投资理财产品了。
          </p>
          <div className="mt-6 space-x-3">
            <Link
              to="/investments/recommendations"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <StarIcon className="h-4 w-4 mr-2" />
              查看推荐产品
            </Link>
            <Link
              to="/investments/products"
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              浏览所有产品
            </Link>
          </div>
        </div>
      )}
    </div>
  )
  } catch (error) {
    console.error('Investment dashboard error:', error)
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="text-center py-12">
          <h2 className="text-lg font-medium text-gray-900 mb-2">加载投资数据时出现问题</h2>
          <p className="text-gray-600 mb-4">请稍后重试或联系客服</p>
          <button
            onClick={() => window.location.reload()}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            重新加载
          </button>
        </div>
      </div>
    )
  }
}
