import { useState } from 'react'
import { XMarkIcon, CheckCircleIcon, ArrowRightIcon, UserIcon, DocumentTextIcon, BanknotesIcon } from '@heroicons/react/24/outline'
import { useUserProfile } from '../../hooks/useUserProfile'
import KYCForm from './KYCForm'
import CreateAccountModal from '../accounts/CreateAccountModal'
import LoadingSpinner from '../common/LoadingSpinner'

interface FirstTimeAccountCreationFlowProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

type FlowStep = 'welcome' | 'kyc' | 'account-creation' | 'complete'

export default function FirstTimeAccountCreationFlow({ 
  isOpen, 
  onClose, 
  onSuccess 
}: FirstTimeAccountCreationFlowProps) {
  const [currentStep, setCurrentStep] = useState<FlowStep>('welcome')
  const [isKYCCompleted, setIsKYCCompleted] = useState(false)
  const { updateProfile, isUpdating } = useUserProfile()

  const handleClose = () => {
    if (isUpdating) return
    onClose()
    // Reset state when modal closes
    setTimeout(() => {
      setCurrentStep('welcome')
      setIsKYCCompleted(false)
    }, 300)
  }

  const handleKYCSuccess = () => {
    setIsKYCCompleted(true)
    setCurrentStep('account-creation')
  }

  const handleAccountCreationSuccess = () => {
    setCurrentStep('complete')
    // Auto close after 2 seconds and call success callback
    setTimeout(() => {
      handleClose()
      onSuccess?.()
    }, 2000)
  }

  const steps = [
    { id: 'welcome', name: '欢迎', icon: UserIcon },
    { id: 'kyc', name: '身份验证', icon: DocumentTextIcon },
    { id: 'account-creation', name: '创建账户', icon: BanknotesIcon },
  ]

  const currentStepIndex = steps.findIndex(step => step.id === currentStep)

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50 overflow-y-auto">
      <div className="relative w-full max-w-2xl transform rounded-lg bg-white shadow-xl transition-all my-8">
        {/* Header with Progress */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              {currentStep === 'complete' ? '开户完成' : '首次开户引导'}
            </h3>
            <button
              onClick={handleClose}
              disabled={isUpdating}
              className="text-gray-400 hover:text-gray-600 disabled:cursor-not-allowed"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Progress Steps */}
          {currentStep !== 'complete' && (
            <div className="flex items-center space-x-4">
              {steps.map((step, index) => {
                const StepIcon = step.icon
                const isActive = index === currentStepIndex
                const isCompleted = index < currentStepIndex || (index === currentStepIndex && currentStep === 'account-creation' && isKYCCompleted)
                
                return (
                  <div key={step.id} className="flex items-center">
                    <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                      isCompleted 
                        ? 'bg-green-100 border-green-500 text-green-600'
                        : isActive 
                          ? 'bg-blue-100 border-blue-500 text-blue-600'
                          : 'bg-gray-100 border-gray-300 text-gray-400'
                    }`}>
                      {isCompleted ? (
                        <CheckCircleIcon className="h-5 w-5" />
                      ) : (
                        <StepIcon className="h-5 w-5" />
                      )}
                    </div>
                    <span className={`ml-2 text-sm font-medium ${
                      isActive ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-gray-500'
                    }`}>
                      {step.name}
                    </span>
                    {index < steps.length - 1 && (
                      <ArrowRightIcon className="h-4 w-4 text-gray-400 mx-3" />
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Content */}
        <div className="px-6 py-6 max-h-[calc(100vh-8rem)] overflow-y-auto">
          {currentStep === 'welcome' && (
            <WelcomeStep onNext={() => setCurrentStep('kyc')} />
          )}
          
          {currentStep === 'kyc' && (
            <KYCForm onSuccess={handleKYCSuccess} />
          )}
          
          {currentStep === 'account-creation' && (
            <div className="text-center">
              <div className="mb-6">
                <CheckCircleIcon className="h-16 w-16 text-green-500 mx-auto mb-4" />
                <h4 className="text-lg font-semibold text-gray-900 mb-2">
                  身份信息已保存！
                </h4>
                <p className="text-gray-600">
                  现在，让我们来创建您的第一个银行账户吧。
                </p>
              </div>
              <CreateAccountModal
                isOpen={true}
                onClose={() => {}} // Prevent closing during flow
                onSuccess={handleAccountCreationSuccess}
                isInFlow={true}
              />
            </div>
          )}
          
          {currentStep === 'complete' && (
            <div className="text-center py-8">
              <CheckCircleIcon className="h-20 w-20 text-green-500 mx-auto mb-6" />
              <h4 className="text-xl font-semibold text-gray-900 mb-2">
                欢迎加入数脉银行！
              </h4>
              <p className="text-gray-600 mb-4">
                您的账户已成功创建，正在为您跳转到仪表板...
              </p>
              <LoadingSpinner size="sm" />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Welcome Step Component
function WelcomeStep({ onNext }: { onNext: () => void }) {
  return (
    <div className="text-center py-8">
      <div className="mb-8">
        <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <BanknotesIcon className="h-10 w-10 text-blue-600" />
        </div>
        <h4 className="text-xl font-semibold text-gray-900 mb-4">
          欢迎使用数脉银行！
        </h4>
        <div className="max-w-md mx-auto text-gray-600 space-y-3">
          <p>
            根据金融监管要求，开立银行账户需要您提供真实的个人信息以完成身份验证。
          </p>
          <p className="font-medium text-blue-600">
            整个过程仅需2分钟。
          </p>
        </div>
      </div>
      
      <div className="space-y-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h5 className="font-medium text-blue-800 mb-2">您将需要提供：</h5>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• 真实姓名和英文姓名</li>
            <li>• 有效身份证件信息</li>
            <li>• 联系方式（手机号码和邮箱）</li>
            <li>• 基本个人信息</li>
          </ul>
        </div>
        
        <button
          onClick={onNext}
          className="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
        >
          开始身份验证
        </button>
      </div>
    </div>
  )
}
