import { useState } from 'react'
import { 
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CurrencyDollarIcon,
  InformationCircleIcon,
  EyeIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'
import { useInvestmentHoldings, usePortfolioSummary } from '../hooks/useInvestments'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { 
  HoldingStatus,
  PRODUCT_TYPE_LABELS,
  RISK_LEVEL_LABELS,
  RISK_LEVEL_COLORS
} from '../types/investment'

export default function InvestmentHoldingsPage() {
  const [selectedTab, setSelectedTab] = useState<'all' | 'active' | 'matured'>('all')
  
  const { data: holdings, isLoading: holdingsLoading, error: holdingsError } = useInvestmentHoldings()
  const { data: portfolio, isLoading: portfolioLoading } = usePortfolioSummary()

  const isLoading = holdingsLoading || portfolioLoading

  // Filter holdings by status
  const filteredHoldings = holdings?.filter(holding => {
    if (selectedTab === 'all') return true
    if (selectedTab === 'active') return holding.status === HoldingStatus.ACTIVE
    if (selectedTab === 'matured') return holding.status === HoldingStatus.MATURED
    return true
  }) || []

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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-CN')
  }

  const getReturnColor = (returnRate: number) => {
    if (returnRate > 0) return 'text-green-600'
    if (returnRate < 0) return 'text-red-600'
    return 'text-gray-600'
  }

  const getReturnIcon = (returnRate: number) => {
    if (returnRate > 0) return <ArrowTrendingUpIcon className="h-4 w-4" />
    if (returnRate < 0) return <ArrowTrendingDownIcon className="h-4 w-4" />
    return null
  }

  const getStatusBadge = (status: HoldingStatus) => {
    const statusConfig = {
      [HoldingStatus.ACTIVE]: { label: '持有中', color: 'bg-green-100 text-green-800' },
      [HoldingStatus.MATURED]: { label: '已到期', color: 'bg-blue-100 text-blue-800' },
      [HoldingStatus.REDEEMED]: { label: '已赎回', color: 'bg-gray-100 text-gray-800' }
    }
    
    const config = statusConfig[status]
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        {config.label}
      </span>
    )
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

  if (holdingsError) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="text-center py-12">
          <InformationCircleIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">加载失败</h3>
          <p className="mt-1 text-sm text-gray-500">无法加载持仓信息，请稍后重试</p>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">我的持仓</h1>
        <p className="mt-1 text-sm text-gray-600">
          查看和管理您的投资持仓
        </p>
      </div>

      {/* Portfolio Summary */}
      {portfolio && (
        <div className="mb-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CurrencyDollarIcon className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">总资产</dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {formatCurrency(portfolio.total_assets)}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CurrencyDollarIcon className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">总投入</dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {formatCurrency(portfolio.total_invested)}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  {getReturnIcon(portfolio.total_gain_loss)}
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">总盈亏</dt>
                    <dd className={`text-lg font-medium ${getReturnColor(portfolio.total_gain_loss)}`}>
                      {formatCurrency(portfolio.total_gain_loss)}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ChartBarIcon className={`h-6 w-6 ${portfolio.total_return_rate >= 0 ? 'text-green-600' : 'text-red-600'}`} />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">总收益率</dt>
                    <dd className={`text-lg font-medium ${getReturnColor(portfolio.total_return_rate)}`}>
                      {formatPercentage(portfolio.total_return_rate)}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { key: 'all', label: '全部持仓', count: holdings?.length || 0 },
              { key: 'active', label: '持有中', count: holdings?.filter(h => h.status === HoldingStatus.ACTIVE).length || 0 },
              { key: 'matured', label: '已到期', count: holdings?.filter(h => h.status === HoldingStatus.MATURED).length || 0 }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setSelectedTab(tab.key as any)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  selectedTab === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label} ({tab.count})
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Holdings List */}
      {filteredHoldings.length === 0 ? (
        <div className="text-center py-12">
          <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">暂无持仓</h3>
          <p className="mt-1 text-sm text-gray-500">
            {selectedTab === 'all' ? '您还没有任何投资持仓' : `没有${selectedTab === 'active' ? '持有中' : '已到期'}的持仓`}
          </p>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {filteredHoldings.map((holding) => (
              <li key={holding.id}>
                <div className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="text-lg font-medium text-gray-900">
                            {holding.product_name}
                          </h3>
                          <div className="mt-1 flex items-center space-x-2">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {PRODUCT_TYPE_LABELS[holding.product_type]}
                            </span>
                            {getStatusBadge(holding.status)}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-medium text-gray-900">
                            {formatCurrency(holding.current_value)}
                          </div>
                          <div className={`text-sm font-medium flex items-center ${getReturnColor(holding.return_rate)}`}>
                            {getReturnIcon(holding.return_rate)}
                            <span className="ml-1">{formatPercentage(holding.return_rate)}</span>
                          </div>
                        </div>
                      </div>

                      <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
                        <div>
                          <dt className="text-sm font-medium text-gray-500">持有份额</dt>
                          <dd className="mt-1 text-sm text-gray-900">
                            {holding.shares.toLocaleString('zh-CN', { maximumFractionDigits: 4 })}
                          </dd>
                        </div>
                        <div>
                          <dt className="text-sm font-medium text-gray-500">平均成本</dt>
                          <dd className="mt-1 text-sm text-gray-900">
                            {formatCurrency(holding.average_cost)}
                          </dd>
                        </div>
                        <div>
                          <dt className="text-sm font-medium text-gray-500">总投入</dt>
                          <dd className="mt-1 text-sm text-gray-900">
                            {formatCurrency(holding.total_invested)}
                          </dd>
                        </div>
                        <div>
                          <dt className="text-sm font-medium text-gray-500">购买日期</dt>
                          <dd className="mt-1 text-sm text-gray-900">
                            {formatDate(holding.purchase_date)}
                          </dd>
                        </div>
                      </div>

                      <div className="mt-4 flex space-x-3">
                        <button className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                          <EyeIcon className="h-4 w-4 mr-1.5" />
                          查看详情
                        </button>
                        {holding.status === HoldingStatus.ACTIVE && (
                          <button className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500">
                            <ArrowPathIcon className="h-4 w-4 mr-1.5" />
                            赎回
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
