import { useState } from 'react'
import {
  FunnelIcon,
  MagnifyingGlassIcon,
  ShoppingCartIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline'
import { useInvestmentProducts } from '../hooks/useInvestments'
import LoadingSpinner from '../components/common/LoadingSpinner'
import PurchaseModal from '../components/investment/PurchaseModal'
import {
  ProductType,
  RiskLevel,
  InvestmentProduct,
  PRODUCT_TYPE_LABELS,
  RISK_LEVEL_LABELS,
  RISK_LEVEL_COLORS,
  ProductFilters
} from '../types/investment'

export default function InvestmentProductsPage() {
  const [filters, setFilters] = useState<ProductFilters>({
    is_active: true
  })
  const [searchTerm, setSearchTerm] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [selectedProduct, setSelectedProduct] = useState<InvestmentProduct | null>(null)
  const [showPurchaseModal, setShowPurchaseModal] = useState(false)

  const { data: products, isLoading, error } = useInvestmentProducts(filters)

  // Filter products by search term
  const filteredProducts = products?.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.product_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.description?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      minimumFractionDigits: 0,
    }).format(amount)
  }

  const formatPercentage = (rate: number | undefined) => {
    if (typeof rate !== 'number' || isNaN(rate)) {
      return '0.00%'
    }
    return `${(rate * 100).toFixed(2)}%`
  }

  const getRiskLevelBadge = (level: RiskLevel) => {
    const color = RISK_LEVEL_COLORS[level]
    return (
      <span 
        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
        style={{ 
          backgroundColor: `${color}20`, 
          color: color 
        }}
      >
        {RISK_LEVEL_LABELS[level]}
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

  if (error) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="text-center py-12">
          <InformationCircleIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">加载失败</h3>
          <p className="mt-1 text-sm text-gray-500">无法加载投资产品，请稍后重试</p>
        </div>
      </div>
    )
  }

  const handlePurchaseClick = (product: InvestmentProduct) => {
    setSelectedProduct(product)
    setShowPurchaseModal(true)
  }

  const handleClosePurchaseModal = () => {
    setShowPurchaseModal(false)
    setSelectedProduct(null)
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">理财产品</h1>
        <p className="mt-1 text-sm text-gray-600">
          选择适合您的理财产品，实现财富增值
        </p>
      </div>

      {/* Search and Filters */}
      <div className="mb-6 space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="搜索产品名称、代码或描述..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Filter Toggle */}
        <div className="flex justify-between items-center">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <FunnelIcon className="h-4 w-4 mr-2" />
            筛选条件
          </button>
          <div className="text-sm text-gray-500">
            共 {filteredProducts.length} 个产品
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="bg-gray-50 p-4 rounded-lg space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {/* Product Type Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  产品类型
                </label>
                <select
                  value={filters.product_type || ''}
                  onChange={(e) => setFilters({
                    ...filters,
                    product_type: e.target.value as ProductType || undefined
                  })}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">全部类型</option>
                  {Object.entries(PRODUCT_TYPE_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </div>

              {/* Risk Level Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  风险等级
                </label>
                <select
                  value={filters.risk_level || ''}
                  onChange={(e) => setFilters({
                    ...filters,
                    risk_level: e.target.value ? Number(e.target.value) as RiskLevel : undefined
                  })}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">全部风险等级</option>
                  {Object.entries(RISK_LEVEL_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </div>

              {/* Clear Filters */}
              <div className="flex items-end">
                <button
                  onClick={() => setFilters({ is_active: true })}
                  className="w-full px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  清除筛选
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Products Grid */}
      {filteredProducts.length === 0 ? (
        <div className="text-center py-12">
          <ShoppingCartIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">暂无产品</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm || Object.keys(filters).length > 1 
              ? '没有找到符合条件的产品，请调整搜索条件' 
              : '暂时没有可用的理财产品'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {filteredProducts.map((product) => (
            <div
              key={product.id}
              className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow duration-200"
            >
              <div className="p-6">
                {/* Product Header */}
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900 mb-1">
                      {product.name}
                    </h3>
                    <p className="text-sm text-gray-500 mb-2">
                      {product.product_code}
                    </p>
                    <div className="flex items-center space-x-2 mb-3">
                      {getRiskLevelBadge(product.risk_level)}
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {PRODUCT_TYPE_LABELS[product.product_type]}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Expected Return */}
                {product.expected_return_rate && (
                  <div className="mb-4">
                    <div className="text-2xl font-bold text-green-600">
                      {formatPercentage(product.expected_return_rate)}
                    </div>
                    <div className="text-sm text-gray-500">预期年化收益率</div>
                  </div>
                )}

                {/* Investment Amount */}
                <div className="mb-4 text-sm text-gray-600">
                  <div>起投金额：{formatCurrency(product.min_investment_amount)}</div>
                  {product.max_investment_amount && (
                    <div>最高金额：{formatCurrency(product.max_investment_amount)}</div>
                  )}
                  {product.investment_period_days && (
                    <div>投资期限：{product.investment_period_days}天</div>
                  )}
                </div>

                {/* Description */}
                {product.description && (
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {product.description}
                  </p>
                )}

                {/* Actions */}
                <div className="flex justify-end">
                  <button
                    onClick={() => handlePurchaseClick(product)}
                    className="w-full bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    立即购买
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Purchase Modal */}
      <PurchaseModal
        isOpen={showPurchaseModal}
        onClose={handleClosePurchaseModal}
        product={selectedProduct}
      />
    </div>
  )
}
