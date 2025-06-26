import { useState, useEffect } from 'react'
import { useUserProfile } from '../hooks/useUserProfile'
import { UserProfileUpdate } from '../types/api'
import LoadingSpinner from '../components/common/LoadingSpinner'
import {
  UserIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

export default function ProfilePage() {
  const { userProfile, isLoading, error, updateProfile, isUpdating, updateError, updateSuccess } = useUserProfile()
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState<UserProfileUpdate>({})
  const [showSuccessMessage, setShowSuccessMessage] = useState(false)

  // Initialize form data when user profile loads
  useEffect(() => {
    if (userProfile) {
      // Extract profile fields from the flattened user profile
      const profileData = {
        real_name: userProfile.real_name,
        english_name: userProfile.english_name,
        id_type: userProfile.id_type,
        id_number: userProfile.id_number,
        country: userProfile.country,
        ethnicity: userProfile.ethnicity,
        gender: userProfile.gender,
        birth_date: userProfile.birth_date,
        birth_place: userProfile.birth_place,
        phone: userProfile.phone,
        email: userProfile.email,
        address: userProfile.address
      }
      setFormData(profileData)
    }
  }, [userProfile])

  // Show success message when update succeeds
  useEffect(() => {
    if (updateSuccess) {
      setShowSuccessMessage(true)
      setIsEditing(false)
      const timer = setTimeout(() => setShowSuccessMessage(false), 3000)
      return () => clearTimeout(timer)
    }
  }, [updateSuccess])

  const handleInputChange = (field: keyof UserProfileUpdate, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value || undefined
    }))
  }

  const handleSave = () => {
    updateProfile(formData)
  }

  const handleCancel = () => {
    if (userProfile) {
      // Extract profile fields from the flattened user profile
      const profileData = {
        real_name: userProfile.real_name,
        english_name: userProfile.english_name,
        id_type: userProfile.id_type,
        id_number: userProfile.id_number,
        country: userProfile.country,
        ethnicity: userProfile.ethnicity,
        gender: userProfile.gender,
        birth_date: userProfile.birth_date,
        birth_place: userProfile.birth_place,
        phone: userProfile.phone,
        email: userProfile.email,
        address: userProfile.address
      }
      setFormData(profileData)
    }
    setIsEditing(false)
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
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">加载个人信息失败</h3>
              <p className="mt-2 text-sm text-red-700">请稍后重试</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div className="flex items-center">
          <UserIcon className="h-8 w-8 text-gray-400 mr-3" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">个人信息</h1>
            <p className="mt-1 text-sm text-gray-600">管理您的个人资料和银行信息</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          {!isEditing ? (
            <button
              onClick={() => setIsEditing(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <PencilIcon className="h-4 w-4 mr-2" />
              修改
            </button>
          ) : (
            <div className="flex space-x-2">
              <button
                onClick={handleSave}
                disabled={isUpdating}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
              >
                {isUpdating ? (
                  <LoadingSpinner size="sm" className="mr-2" />
                ) : (
                  <CheckIcon className="h-4 w-4 mr-2" />
                )}
                保存
              </button>
              <button
                onClick={handleCancel}
                disabled={isUpdating}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
              >
                <XMarkIcon className="h-4 w-4 mr-2" />
                取消
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Success Message */}
      {showSuccessMessage && (
        <div className="mb-6 rounded-md bg-green-50 p-4">
          <div className="flex">
            <CheckIcon className="h-5 w-5 text-green-400" />
            <div className="ml-3">
              <p className="text-sm font-medium text-green-800">个人信息已成功更新</p>
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {updateError && (
        <div className="mb-6 rounded-md bg-red-50 p-4">
          <div className="flex">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">更新失败</h3>
              <p className="mt-2 text-sm text-red-700">
                {updateError instanceof Error ? updateError.message : '请稍后重试'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Notice */}
      <div className="mb-6 rounded-md bg-orange-50 p-4">
        <div className="flex">
          <ExclamationTriangleIcon className="h-5 w-5 text-orange-400" />
          <div className="ml-3">
            <p className="text-sm text-orange-700">
              为确保操作成功，建议您每日北京时间7:00-21:00期间通过电子银行进行个人信息修改。
            </p>
          </div>
        </div>
      </div>

      {/* Basic Information */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">基本信息</h2>
        </div>
        <div className="px-6 py-4 space-y-6">
          {/* Account Number */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                电子银行客户序号
              </label>
              <div className="text-lg font-semibold text-gray-900">
                {userProfile?.id?.slice(-8) || '280314928'}
              </div>
            </div>
          </div>

          {/* Name Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                姓名
              </label>
              {isEditing ? (
                <input
                  type="text"
                  value={formData.real_name || ''}
                  onChange={(e) => handleInputChange('real_name', e.target.value)}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="请输入真实姓名"
                />
              ) : (
                <div className="text-gray-900">
                  {userProfile?.real_name || '未设置'}
                </div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                英文/拼音姓名
              </label>
              {isEditing ? (
                <input
                  type="text"
                  value={formData.english_name || ''}
                  onChange={(e) => handleInputChange('english_name', e.target.value)}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="请输入英文或拼音姓名"
                />
              ) : (
                <div className="text-gray-900">
                  {userProfile?.english_name || '未设置'}
                </div>
              )}
            </div>
          </div>

          {/* ID Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                证件类型
              </label>
              {isEditing ? (
                <select
                  value={formData.id_type || ''}
                  onChange={(e) => handleInputChange('id_type', e.target.value)}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">请选择证件类型</option>
                  <option value="居民身份证">居民身份证</option>
                  <option value="护照">护照</option>
                  <option value="港澳通行证">港澳通行证</option>
                  <option value="台胞证">台胞证</option>
                  <option value="军官证">军官证</option>
                </select>
              ) : (
                <div className="text-gray-900">
                  {userProfile?.id_type || '未设置'}
                </div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                证件号码
              </label>
              {isEditing ? (
                <input
                  type="text"
                  value={formData.id_number || ''}
                  onChange={(e) => handleInputChange('id_number', e.target.value)}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="请输入证件号码"
                />
              ) : (
                <div className="text-gray-900">
                  {userProfile?.id_number || '未设置'}
                </div>
              )}
            </div>
          </div>

          {/* Location and Personal Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                国家/地区
              </label>
              {isEditing ? (
                <input
                  type="text"
                  value={formData.country || ''}
                  onChange={(e) => handleInputChange('country', e.target.value)}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="请输入国家/地区"
                />
              ) : (
                <div className="text-gray-900">
                  {userProfile?.country || '未设置'}
                </div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                民族
              </label>
              {isEditing ? (
                <input
                  type="text"
                  value={formData.ethnicity || ''}
                  onChange={(e) => handleInputChange('ethnicity', e.target.value)}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="请输入民族"
                />
              ) : (
                <div className="text-gray-900">
                  {userProfile?.ethnicity || '未设置'}
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                性别
              </label>
              {isEditing ? (
                <select
                  value={formData.gender || ''}
                  onChange={(e) => handleInputChange('gender', e.target.value)}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">请选择性别</option>
                  <option value="男">男</option>
                  <option value="女">女</option>
                </select>
              ) : (
                <div className="text-gray-900">
                  {userProfile?.gender || '未设置'}
                </div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                出生日期
              </label>
              {isEditing ? (
                <input
                  type="date"
                  value={formData.birth_date || ''}
                  onChange={(e) => handleInputChange('birth_date', e.target.value)}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                />
              ) : (
                <div className="text-gray-900">
                  {userProfile?.birth_date || '未设置'}
                </div>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              出生地
            </label>
            {isEditing ? (
              <input
                type="text"
                value={formData.birth_place || ''}
                onChange={(e) => handleInputChange('birth_place', e.target.value)}
                className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                placeholder="请输入出生地"
              />
            ) : (
              <div className="text-gray-900">
                {userProfile?.birth_place || '未设置'}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Contact Information */}
      <div className="mt-6 bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">证件 地址信息</h2>
        </div>
        <div className="px-6 py-4 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              联系地址
            </label>
            {isEditing ? (
              <textarea
                value={formData.address || ''}
                onChange={(e) => handleInputChange('address', e.target.value)}
                rows={3}
                className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                placeholder="请输入联系地址"
              />
            ) : (
              <div className="text-gray-900">
                {userProfile?.address || '未设置'}
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                手机号码
              </label>
              {isEditing ? (
                <input
                  type="tel"
                  value={formData.phone || ''}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="请输入手机号码"
                />
              ) : (
                <div className="text-gray-900">
                  {userProfile?.phone || '未设置'}
                </div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                邮箱地址
              </label>
              {isEditing ? (
                <input
                  type="email"
                  value={formData.email || ''}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="请输入邮箱地址"
                />
              ) : (
                <div className="text-gray-900">
                  {userProfile?.email || '未设置'}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
