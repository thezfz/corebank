import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  ShieldCheckIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'
import { useCreateRiskAssessment, useRiskAssessment } from '../hooks/useInvestments'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { 
  RiskLevel, 
  InvestmentExperience, 
  InvestmentGoal, 
  InvestmentHorizon,
  RiskAssessmentForm,
  RISK_LEVEL_LABELS,
  INVESTMENT_EXPERIENCE_LABELS,
  INVESTMENT_GOAL_LABELS,
  INVESTMENT_HORIZON_LABELS
} from '../types/investment'

const ASSESSMENT_QUESTIONS = [
  {
    id: 'personal_info',
    title: '个人信息',
    questions: [
      {
        key: 'age_range',
        label: '您的年龄段',
        type: 'select',
        options: [
          { value: '18-25', label: '18-25岁' },
          { value: '26-35', label: '26-35岁' },
          { value: '36-45', label: '36-45岁' },
          { value: '46-55', label: '46-55岁' },
          { value: '56-65', label: '56-65岁' },
          { value: '65+', label: '65岁以上' }
        ]
      },
      {
        key: 'monthly_income_range',
        label: '您的月收入范围',
        type: 'select',
        options: [
          { value: '5000以下', label: '5,000元以下' },
          { value: '5000-10000', label: '5,000-10,000元' },
          { value: '10000-20000', label: '10,000-20,000元' },
          { value: '20000-50000', label: '20,000-50,000元' },
          { value: '50000以上', label: '50,000元以上' }
        ]
      },
      {
        key: 'investment_experience',
        label: '您的投资经验',
        type: 'select',
        options: Object.entries(INVESTMENT_EXPERIENCE_LABELS).map(([value, label]) => ({
          value,
          label
        }))
      }
    ]
  },
  {
    id: 'investment_goals',
    title: '投资目标',
    questions: [
      {
        key: 'investment_goal',
        label: '您的主要投资目标',
        type: 'select',
        options: Object.entries(INVESTMENT_GOAL_LABELS).map(([value, label]) => ({
          value,
          label
        }))
      },
      {
        key: 'investment_horizon',
        label: '您的投资期限',
        type: 'select',
        options: Object.entries(INVESTMENT_HORIZON_LABELS).map(([value, label]) => ({
          value,
          label
        }))
      },
      {
        key: 'investment_amount_range',
        label: '您计划投资的金额范围',
        type: 'select',
        options: [
          { value: '1万以下', label: '1万元以下' },
          { value: '1-5万', label: '1-5万元' },
          { value: '5-10万', label: '5-10万元' },
          { value: '10-50万', label: '10-50万元' },
          { value: '50万以上', label: '50万元以上' }
        ]
      }
    ]
  },
  {
    id: 'risk_tolerance',
    title: '风险承受能力',
    questions: [
      {
        key: 'market_decline_reaction',
        label: '如果您的投资在短期内下跌20%，您会如何反应？',
        type: 'radio',
        options: [
          { value: '1', label: '立即卖出，避免更大损失' },
          { value: '2', label: '考虑卖出一部分' },
          { value: '3', label: '继续持有，等待回升' },
          { value: '4', label: '趁低买入更多' },
          { value: '5', label: '完全不担心，这是正常波动' }
        ]
      },
      {
        key: 'investment_priority',
        label: '在投资中，您最看重什么？',
        type: 'radio',
        options: [
          { value: '1', label: '本金安全，不能有任何损失' },
          { value: '2', label: '稳定收益，波动要小' },
          { value: '3', label: '平衡收益和风险' },
          { value: '4', label: '追求较高收益，可承受一定风险' },
          { value: '5', label: '追求最高收益，愿意承担高风险' }
        ]
      },
      {
        key: 'risk_vs_return_preference',
        label: '您更倾向于哪种投资方式？',
        type: 'radio',
        options: [
          { value: '1', label: '银行存款，收益低但安全' },
          { value: '2', label: '债券基金，收益稳定' },
          { value: '3', label: '混合基金，收益和风险适中' },
          { value: '4', label: '股票基金，收益较高但波动大' },
          { value: '5', label: '高风险投资，追求最大收益' }
        ]
      }
    ]
  }
]

export default function RiskAssessmentPage() {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState<Partial<RiskAssessmentForm>>({})
  const [isCompleted, setIsCompleted] = useState(false)

  const { data: existingAssessment } = useRiskAssessment()
  const createAssessmentMutation = useCreateRiskAssessment()

  const currentSection = ASSESSMENT_QUESTIONS[currentStep]
  const isLastStep = currentStep === ASSESSMENT_QUESTIONS.length - 1

  const handleInputChange = (key: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const isCurrentStepValid = () => {
    return currentSection.questions.every(q => formData[q.key as keyof RiskAssessmentForm])
  }

  const calculateRiskLevel = (): RiskLevel => {
    // Simple risk calculation based on answers
    const riskScores = [
      parseInt(formData.market_decline_reaction || '1'),
      parseInt(formData.investment_priority || '1'),
      parseInt(formData.risk_vs_return_preference || '1')
    ]
    
    const avgScore = riskScores.reduce((sum, score) => sum + score, 0) / riskScores.length
    
    if (avgScore <= 1.5) return RiskLevel.VERY_LOW
    if (avgScore <= 2.5) return RiskLevel.LOW
    if (avgScore <= 3.5) return RiskLevel.MEDIUM
    if (avgScore <= 4.5) return RiskLevel.HIGH
    return RiskLevel.VERY_HIGH
  }

  const handleNext = () => {
    if (isLastStep) {
      handleSubmit()
    } else {
      setCurrentStep(prev => prev + 1)
    }
  }

  const handlePrevious = () => {
    setCurrentStep(prev => prev - 1)
  }

  const handleSubmit = async () => {
    try {
      const riskLevel = calculateRiskLevel()
      
      const assessmentData = {
        risk_tolerance: riskLevel,
        investment_experience: formData.investment_experience as InvestmentExperience,
        investment_goal: formData.investment_goal as InvestmentGoal,
        investment_horizon: formData.investment_horizon as InvestmentHorizon,
        monthly_income_range: formData.monthly_income_range,
        assessment_data: formData
      }

      await createAssessmentMutation.mutateAsync(assessmentData)
      setIsCompleted(true)
    } catch (error) {
      console.error('Failed to submit assessment:', error)
    }
  }

  if (isCompleted) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="max-w-2xl mx-auto text-center">
          <CheckCircleIcon className="mx-auto h-16 w-16 text-green-500" />
          <h2 className="mt-4 text-2xl font-bold text-gray-900">评估完成！</h2>
          <p className="mt-2 text-gray-600">
            您的风险承受能力评估已完成，我们将为您推荐合适的理财产品。
          </p>
          <div className="mt-8 space-y-3">
            <button
              onClick={() => navigate('/investments/recommendations')}
              className="w-full bg-blue-600 text-white px-6 py-3 rounded-md font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              查看推荐产品
            </button>
            <button
              onClick={() => navigate('/investments/products')}
              className="w-full bg-gray-100 text-gray-700 px-6 py-3 rounded-md font-medium hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
            >
              浏览所有产品
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-8 text-center">
          <ShieldCheckIcon className="mx-auto h-12 w-12 text-blue-600" />
          <h1 className="mt-4 text-2xl font-bold text-gray-900">风险承受能力评估</h1>
          <p className="mt-2 text-gray-600">
            请如实填写以下信息，我们将为您推荐合适的理财产品
          </p>
          {existingAssessment && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
              <p className="text-sm text-yellow-800">
                您已有风险评估记录，重新评估将更新您的风险等级
              </p>
            </div>
          )}
        </div>

        {/* Progress */}
        <div className="mb-8">
          <div className="flex items-center justify-between text-sm text-gray-500 mb-2">
            <span>第 {currentStep + 1} 步，共 {ASSESSMENT_QUESTIONS.length} 步</span>
            <span>{Math.round(((currentStep + 1) / ASSESSMENT_QUESTIONS.length) * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStep + 1) / ASSESSMENT_QUESTIONS.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Current Section */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            {currentSection.title}
          </h2>

          <div className="space-y-6">
            {currentSection.questions.map((question) => (
              <div key={question.key}>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  {question.label}
                </label>
                
                {question.type === 'select' && (
                  <select
                    value={formData[question.key as keyof RiskAssessmentForm] || ''}
                    onChange={(e) => handleInputChange(question.key, e.target.value)}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">请选择...</option>
                    {question.options.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                )}

                {question.type === 'radio' && (
                  <div className="space-y-3">
                    {question.options.map((option) => (
                      <label key={option.value} className="flex items-start">
                        <input
                          type="radio"
                          name={question.key}
                          value={option.value}
                          checked={formData[question.key as keyof RiskAssessmentForm] === option.value}
                          onChange={(e) => handleInputChange(question.key, e.target.value)}
                          className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                        />
                        <span className="ml-3 text-sm text-gray-700">{option.label}</span>
                      </label>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Navigation */}
        <div className="mt-8 flex justify-between">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 0}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeftIcon className="h-4 w-4 mr-2" />
            上一步
          </button>

          <button
            onClick={handleNext}
            disabled={!isCurrentStepValid() || createAssessmentMutation.isPending}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {createAssessmentMutation.isPending ? (
              <LoadingSpinner size="sm" />
            ) : (
              <>
                {isLastStep ? '完成评估' : '下一步'}
                {!isLastStep && <ChevronRightIcon className="h-4 w-4 ml-2" />}
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
