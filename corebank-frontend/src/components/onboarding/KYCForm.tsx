import { useState } from 'react'
import { ExclamationCircleIcon } from '@heroicons/react/24/outline'
import { useUserProfile } from '../../hooks/useUserProfile'
import LoadingSpinner from '../common/LoadingSpinner'
import type { UserProfileUpdate } from '../../types/api'

interface KYCFormProps {
  onSuccess: () => void
}

interface FormData {
  real_name: string
  english_name: string
  id_type: string
  id_number: string
  country: string
  ethnicity: string
  gender: string
  birth_date: string
  birth_place: string
  phone: string
  email: string
  address: string
}

interface FormErrors {
  [key: string]: string
}

export default function KYCForm({ onSuccess }: KYCFormProps) {
  const { updateProfile, isUpdating, error } = useUserProfile()
  
  const [formData, setFormData] = useState<FormData>({
    real_name: '',
    english_name: '',
    id_type: '居民身份证',
    id_number: '',
    country: '中国',
    ethnicity: '汉族',
    gender: '',
    birth_date: '',
    birth_place: '',
    phone: '',
    email: '',
    address: ''
  })

  const [formErrors, setFormErrors] = useState<FormErrors>({})

  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when user starts typing
    if (formErrors[field]) {
      setFormErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const validateForm = (): boolean => {
    const errors: FormErrors = {}

    // Required fields validation
    if (!formData.real_name.trim()) {
      errors.real_name = '请输入真实姓名'
    }

    if (!formData.english_name.trim()) {
      errors.english_name = '请输入英文/拼音姓名'
    }

    if (!formData.id_number.trim()) {
      errors.id_number = '请输入证件号码'
    } else if (formData.id_type === '居民身份证') {
      // Chinese ID card validation
      const idPattern = /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/
      if (!idPattern.test(formData.id_number)) {
        errors.id_number = '请输入有效的身份证号码'
      }
    }

    if (!formData.gender) {
      errors.gender = '请选择性别'
    }

    if (!formData.birth_date) {
      errors.birth_date = '请选择出生日期'
    }

    if (!formData.birth_place.trim()) {
      errors.birth_place = '请输入出生地'
    }

    if (!formData.phone.trim()) {
      errors.phone = '请输入手机号码'
    } else {
      // Chinese mobile phone validation
      const phonePattern = /^1[3-9]\d{9}$/
      if (!phonePattern.test(formData.phone)) {
        errors.phone = '请输入有效的手机号码'
      }
    }

    if (!formData.email.trim()) {
      errors.email = '请输入邮箱地址'
    } else {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailPattern.test(formData.email)) {
        errors.email = '请输入有效的邮箱地址'
      }
    }

    if (!formData.address.trim()) {
      errors.address = '请输入联系地址'
    }

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    try {
      const profileData: UserProfileUpdate = {
        ...formData,
        birth_date: formData.birth_date
      }

      await updateProfile(profileData)
      onSuccess()
    } catch (err) {
      console.error('Failed to update profile:', err)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6 text-center">
        <h4 className="text-lg font-semibold text-gray-900 mb-2">
          身份信息验证
        </h4>
        <p className="text-gray-600">
          请填写真实、准确的个人信息，这些信息将用于账户安全验证
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-lg bg-red-50 border border-red-200 p-4">
          <div className="flex items-start">
            <ExclamationCircleIcon className="h-5 w-5 text-red-400 mt-0.5 mr-2 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-medium text-red-800">提交失败</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Basic Information */}
        <div className="bg-gray-50 rounded-lg p-3">
          <h5 className="font-medium text-gray-900 mb-3">基本信息</h5>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                真实姓名 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.real_name}
                onChange={(e) => handleInputChange('real_name', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  formErrors.real_name ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="请输入真实姓名"
              />
              {formErrors.real_name && (
                <p className="mt-1 text-sm text-red-600">{formErrors.real_name}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                英文/拼音姓名 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.english_name}
                onChange={(e) => handleInputChange('english_name', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  formErrors.english_name ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="请输入英文或拼音姓名"
              />
              {formErrors.english_name && (
                <p className="mt-1 text-sm text-red-600">{formErrors.english_name}</p>
              )}
            </div>
          </div>
        </div>

        {/* Identity Information */}
        <div className="bg-gray-50 rounded-lg p-3">
          <h5 className="font-medium text-gray-900 mb-3">证件信息</h5>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                证件类型 <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.id_type}
                onChange={(e) => handleInputChange('id_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="居民身份证">居民身份证</option>
                <option value="护照">护照</option>
                <option value="港澳通行证">港澳通行证</option>
                <option value="台胞证">台胞证</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                证件号码 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.id_number}
                onChange={(e) => handleInputChange('id_number', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  formErrors.id_number ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="请输入证件号码"
              />
              {formErrors.id_number && (
                <p className="mt-1 text-sm text-red-600">{formErrors.id_number}</p>
              )}
            </div>
          </div>
        </div>

        {/* Personal Details */}
        <div className="bg-gray-50 rounded-lg p-3">
          <h5 className="font-medium text-gray-900 mb-3">个人详情</h5>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                国家/地区
              </label>
              <select
                value={formData.country}
                onChange={(e) => handleInputChange('country', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="中国">中国</option>
                <option value="香港">香港</option>
                <option value="澳门">澳门</option>
                <option value="台湾">台湾</option>
                <option value="其他">其他</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                民族
              </label>
              <input
                type="text"
                value={formData.ethnicity}
                onChange={(e) => handleInputChange('ethnicity', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="请输入民族"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                性别 <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.gender}
                onChange={(e) => handleInputChange('gender', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  formErrors.gender ? 'border-red-300' : 'border-gray-300'
                }`}
              >
                <option value="">请选择性别</option>
                <option value="男">男</option>
                <option value="女">女</option>
              </select>
              {formErrors.gender && (
                <p className="mt-1 text-sm text-red-600">{formErrors.gender}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                出生日期 <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.birth_date}
                onChange={(e) => handleInputChange('birth_date', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  formErrors.birth_date ? 'border-red-300' : 'border-gray-300'
                }`}
              />
              {formErrors.birth_date && (
                <p className="mt-1 text-sm text-red-600">{formErrors.birth_date}</p>
              )}
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                出生地 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.birth_place}
                onChange={(e) => handleInputChange('birth_place', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  formErrors.birth_place ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="请输入出生地"
              />
              {formErrors.birth_place && (
                <p className="mt-1 text-sm text-red-600">{formErrors.birth_place}</p>
              )}
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="bg-gray-50 rounded-lg p-3">
          <h5 className="font-medium text-gray-900 mb-3">联系信息</h5>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                手机号码 <span className="text-red-500">*</span>
              </label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => handleInputChange('phone', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  formErrors.phone ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="请输入手机号码"
              />
              {formErrors.phone && (
                <p className="mt-1 text-sm text-red-600">{formErrors.phone}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                邮箱地址 <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  formErrors.email ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="请输入邮箱地址"
              />
              {formErrors.email && (
                <p className="mt-1 text-sm text-red-600">{formErrors.email}</p>
              )}
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                联系地址 <span className="text-red-500">*</span>
              </label>
              <textarea
                value={formData.address}
                onChange={(e) => handleInputChange('address', e.target.value)}
                rows={3}
                className={`w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  formErrors.address ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="请输入详细联系地址"
              />
              {formErrors.address && (
                <p className="mt-1 text-sm text-red-600">{formErrors.address}</p>
              )}
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={isUpdating}
            className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-400 disabled:cursor-not-allowed flex items-center"
          >
            {isUpdating ? (
              <>
                <LoadingSpinner size="sm" className="mr-2" />
                提交中...
              </>
            ) : (
              '提交身份信息'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
