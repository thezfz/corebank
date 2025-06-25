import React from 'react'
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline'

interface PasswordRequirement {
  id: string
  label: string
  test: (password: string) => boolean
  met: boolean
}

interface PasswordStrengthIndicatorProps {
  password: string
  className?: string
}

const PasswordStrengthIndicator: React.FC<PasswordStrengthIndicatorProps> = ({
  password,
  className = ''
}) => {
  const requirements: PasswordRequirement[] = [
    {
      id: 'length',
      label: '至少8个字符',
      test: (pwd) => pwd.length >= 8,
      met: password.length >= 8
    },
    {
      id: 'uppercase',
      label: '包含大写字母 (A-Z)',
      test: (pwd) => /[A-Z]/.test(pwd),
      met: /[A-Z]/.test(password)
    },
    {
      id: 'lowercase',
      label: '包含小写字母 (a-z)',
      test: (pwd) => /[a-z]/.test(pwd),
      met: /[a-z]/.test(password)
    },
    {
      id: 'digit',
      label: '包含数字 (0-9)',
      test: (pwd) => /\d/.test(pwd),
      met: /\d/.test(password)
    },
    {
      id: 'special',
      label: '包含特殊字符 (!@#$%^&*等)',
      test: (pwd) => /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(pwd),
      met: /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)
    }
  ]

  const metRequirements = requirements.filter(req => req.met).length
  const totalRequirements = requirements.length

  const getStrengthLevel = () => {
    if (metRequirements === 0) return 'none'
    if (metRequirements <= 2) return 'weak'
    if (metRequirements <= 3) return 'fair'
    if (metRequirements <= 4) return 'good'
    return 'strong'
  }

  const getStrengthColor = () => {
    const level = getStrengthLevel()
    switch (level) {
      case 'none': return 'bg-gray-200'
      case 'weak': return 'bg-red-500'
      case 'fair': return 'bg-orange-500'
      case 'good': return 'bg-yellow-500'
      case 'strong': return 'bg-green-500'
      default: return 'bg-gray-200'
    }
  }

  const getStrengthText = () => {
    const level = getStrengthLevel()
    switch (level) {
      case 'none': return '请输入密码'
      case 'weak': return '密码强度：弱'
      case 'fair': return '密码强度：一般'
      case 'good': return '密码强度：良好'
      case 'strong': return '密码强度：强'
      default: return ''
    }
  }

  const strengthPercentage = (metRequirements / totalRequirements) * 100

  return (
    <div className={`space-y-3 ${className}`}>
      {/* 密码强度条 */}
      {password && (
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-700">
              {getStrengthText()}
            </span>
            <span className="text-xs text-gray-500">
              {metRequirements}/{totalRequirements} 项要求
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${getStrengthColor()}`}
              style={{ width: `${strengthPercentage}%` }}
            />
          </div>
        </div>
      )}

      {/* 密码要求列表 */}
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-gray-700 mb-2">密码要求：</h4>
        <div className="space-y-1">
          {requirements.map((requirement) => (
            <div
              key={requirement.id}
              className={`flex items-center space-x-2 text-sm transition-colors duration-200 ${
                requirement.met
                  ? 'text-green-600'
                  : password
                  ? 'text-red-500'
                  : 'text-gray-500'
              }`}
            >
              {requirement.met ? (
                <CheckCircleIcon className="h-4 w-4 text-green-500" />
              ) : (
                <XCircleIcon className={`h-4 w-4 ${password ? 'text-red-400' : 'text-gray-400'}`} />
              )}
              <span className={requirement.met ? 'line-through' : ''}>
                {requirement.label}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* 额外提示 */}
      {password && metRequirements === totalRequirements && (
        <div className="flex items-center space-x-2 text-sm text-green-600 bg-green-50 p-2 rounded-md">
          <CheckCircleIcon className="h-4 w-4" />
          <span className="font-medium">密码符合所有安全要求！</span>
        </div>
      )}
    </div>
  )
}

export default PasswordStrengthIndicator
