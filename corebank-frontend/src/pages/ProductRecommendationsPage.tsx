import { Link } from 'react-router-dom'
import { 
  StarIcon,
  ShoppingCartIcon,
  InformationCircleIcon,
  ChartBarIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline'
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid'
import { useProductRecommendations, useRiskAssessment } from '../hooks/useInvestments'
import LoadingSpinner from '../components/common/LoadingSpinner'
import PurchaseModal from '../components/investment/PurchaseModal'
import { useState } from 'react'
import {
  InvestmentProduct,
  ProductRecommendation,
  PRODUCT_TYPE_LABELS,
  RISK_LEVEL_LABELS,
  RISK_LEVEL_COLORS
} from '../types/investment'

export default function ProductRecommendationsPage() {
  const [selectedProduct, setSelectedProduct] = useState<InvestmentProduct | null>(null)
  const [showPurchaseModal, setShowPurchaseModal] = useState(false)

  const { data: recommendations, isLoading, error } = useProductRecommendations()
  const { data: riskAssessment } = useRiskAssessment()

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

  const getRiskLevelBadge = (level: number) => {
    const riskLevel = level as keyof typeof RISK_LEVEL_LABELS
    const color = RISK_LEVEL_COLORS[riskLevel]
    const label = RISK_LEVEL_LABELS[riskLevel]
    
    return (
      <span 
        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
        style={{ 
          backgroundColor: `${color}20`, 
          color: color 
        }}
      >
        {label}
      </span>
    )
  }

  const renderStars = (score: number) => {
    const stars = Math.round(score * 5) // Convert 0-1 score to 0-5 stars
    return (
      <div className="flex items-center">
        {[1, 2, 3, 4, 5].map((star) => (
          star <= stars ? (
            <StarIconSolid key={star} className="h-4 w-4 text-yellow-400" />
          ) : (
            <StarIcon key={star} className="h-4 w-4 text-gray-300" />
          )
        ))}
        <span className="ml-1 text-sm text-gray-600">
          ({(score * 100).toFixed(0)}% 匹配)
        </span>
      </div>
    )
  }

  const handlePurchase = (product: InvestmentProduct) => {
    setSelectedProduct(product)
    setShowPurchaseModal(true)
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
          <h2 className="text-lg font-medium text-gray-900 mb-2">获取推荐产品时出现问题</h2>
          <p className="text-gray-600 mb-4">请稍后重试或联系客服</p>
          <Link 
            to="/investments/products"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            浏览所有产品
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center mb-4">
          <StarIconSolid className="h-8 w-8 text-yellow-500 mr-3" />
          <h1 className="text-2xl font-bold text-gray-900">
            为您推荐的理财产品
          </h1>
        </div>
        <p className="text-gray-600">
          基于您的风险评估结果，我们为您精选了以下理财产品
        </p>
        
        {/* Risk Assessment Summary */}
        {riskAssessment && (
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center">
              <ShieldCheckIcon className="h-5 w-5 text-blue-600 mr-2" />
              <span className="text-sm font-medium text-blue-900">
                您的风险等级：{RISK_LEVEL_LABELS[riskAssessment.risk_tolerance]}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Recommendations */}
      {!recommendations || recommendations.length === 0 ? (
        <div className="text-center py-12">
          <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">暂无推荐产品</h3>
          <p className="mt-1 text-sm text-gray-500">
            请先完成风险评估，或浏览所有产品
          </p>
          <div className="mt-6 space-x-3">
            <Link
              to="/investments/risk-assessment"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              完成风险评估
            </Link>
            <Link
              to="/investments/products"
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              浏览所有产品
            </Link>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {recommendations.map((recommendation: ProductRecommendation, index: number) => (
            <div key={recommendation.product.id} className="bg-white shadow rounded-lg overflow-hidden">
              <div className="p-6">
                {/* Recommendation Badge */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                      #{index + 1} 推荐
                    </span>
                    {recommendation.risk_match && (
                      <span className="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        风险匹配
                      </span>
                    )}
                  </div>
                  {renderStars(recommendation.recommendation_score)}
                </div>

                {/* Product Info */}
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900 mb-1">
                      {recommendation.product.name}
                    </h3>
                    <p className="text-sm text-gray-500 mb-2">
                      {recommendation.product.product_code}
                    </p>
                    <div className="flex items-center space-x-3 mb-3">
                      {getRiskLevelBadge(recommendation.product.risk_level)}
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {PRODUCT_TYPE_LABELS[recommendation.product.product_type]}
                      </span>
                    </div>
                  </div>

                  {/* Expected Return */}
                  {recommendation.product.expected_return_rate && (
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-600">
                        {formatPercentage(recommendation.product.expected_return_rate)}
                      </div>
                      <div className="text-sm text-gray-500">预期年化收益率</div>
                    </div>
                  )}
                </div>

                {/* Recommendation Details */}
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-start">
                    <InformationCircleIcon className="h-5 w-5 text-blue-500 mt-0.5 mr-2 flex-shrink-0" />
                    <div className="flex-1">
                      <p className="text-sm text-gray-700 mb-2">
                        <strong>推荐理由：</strong>{recommendation.recommendation_reason}
                      </p>
                      {recommendation.suggested_allocation && (
                        <p className="text-sm text-gray-700">
                          <strong>建议配置：</strong>投资组合的 {recommendation.suggested_allocation}%
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Investment Details */}
                <div className="mt-4 grid grid-cols-2 gap-4 text-sm text-gray-600">
                  <div>
                    <span className="font-medium">起投金额：</span>
                    {formatCurrency(recommendation.product.min_investment_amount)}
                  </div>
                  {recommendation.product.investment_period_days && (
                    <div>
                      <span className="font-medium">投资期限：</span>
                      {recommendation.product.investment_period_days}天
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="mt-6 flex space-x-3">
                  <button
                    onClick={() => handlePurchase(recommendation.product)}
                    className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <ShoppingCartIcon className="h-4 w-4 inline mr-2" />
                    立即购买
                  </button>
                  <Link
                    to={`/investments/products/${recommendation.product.id}`}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    查看详情
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Purchase Modal */}
      {selectedProduct && (
        <PurchaseModal
          isOpen={showPurchaseModal}
          onClose={() => {
            setShowPurchaseModal(false)
            setSelectedProduct(null)
          }}
          product={selectedProduct}
        />
      )}
    </div>
  )
}
