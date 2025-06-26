import React from 'react'
import {
  UsersIcon,
  CreditCardIcon,
  ArrowsRightLeftIcon,
  ChartBarIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { useAdminDashboard } from '../../hooks/useAdmin'
import LoadingSpinner from '../../components/common/LoadingSpinner'

export default function AdminDashboard() {
  const {
    statistics,
    isLoading,
    error,
    totalUsers,
    adminCount,
    userCount,
    newUsersThisMonth,
    newUsersThisWeek,
    userGrowthRate
  } = useAdminDashboard()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">加载失败</h3>
          <p className="mt-1 text-sm text-gray-500">{error}</p>
        </div>
      </div>
    )
  }

  const statCards = [
    {
      name: '总用户数',
      value: totalUsers,
      icon: UsersIcon,
      color: 'bg-blue-500',
      description: '系统中的所有用户',
      growth: userGrowthRate ? `+${userGrowthRate}% 本月` : undefined
    },
    {
      name: '管理员',
      value: adminCount,
      icon: CreditCardIcon,
      color: 'bg-purple-500',
      description: '具有管理权限的用户'
    },
    {
      name: '普通用户',
      value: userCount,
      icon: UsersIcon,
      color: 'bg-green-500',
      description: '普通银行用户'
    },
    {
      name: '本月新用户',
      value: newUsersThisMonth,
      icon: ChartBarIcon,
      color: 'bg-orange-500',
      description: '过去30天注册的用户'
    },
    {
      name: '本周新用户',
      value: newUsersThisWeek,
      icon: ArrowsRightLeftIcon,
      color: 'bg-indigo-500',
      description: '过去7天注册的用户'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-5">
        <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          管理员仪表板
        </h1>
        <p className="mt-2 max-w-4xl text-sm text-gray-500">
          系统概览和关键指标监控
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {statCards.map((card) => {
          const Icon = card.icon
          return (
            <div
              key={card.name}
              className="relative bg-white pt-5 px-4 pb-12 sm:pt-6 sm:px-6 shadow rounded-lg overflow-hidden"
            >
              <dt>
                <div className={`absolute ${card.color} rounded-md p-3`}>
                  <Icon className="h-6 w-6 text-white" aria-hidden="true" />
                </div>
                <p className="ml-16 text-sm font-medium text-gray-500 truncate">
                  {card.name}
                </p>
              </dt>
              <dd className="ml-16 pb-6 flex items-baseline sm:pb-7">
                <p className="text-2xl font-semibold text-gray-900">
                  {card.value.toLocaleString()}
                </p>
              </dd>
              <div className="absolute bottom-0 inset-x-0 bg-gray-50 px-4 py-4 sm:px-6">
                <div className="text-sm">
                  <span className="text-gray-600">{card.description}</span>
                  {card.growth && (
                    <span className="ml-2 text-green-600 font-medium">
                      {card.growth}
                    </span>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            快速操作
          </h3>
          <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <button
              onClick={() => window.location.href = '/admin/users'}
              className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500 rounded-lg border border-gray-300 hover:border-gray-400"
            >
              <div>
                <span className="rounded-lg inline-flex p-3 bg-blue-50 text-blue-700 ring-4 ring-white">
                  <UsersIcon className="h-6 w-6" aria-hidden="true" />
                </span>
              </div>
              <div className="mt-8">
                <h3 className="text-lg font-medium">
                  <span className="absolute inset-0" aria-hidden="true" />
                  用户管理
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  查看和管理系统用户
                </p>
              </div>
            </button>

            <button
              onClick={() => window.location.href = '/admin/transactions'}
              className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500 rounded-lg border border-gray-300 hover:border-gray-400"
            >
              <div>
                <span className="rounded-lg inline-flex p-3 bg-green-50 text-green-700 ring-4 ring-white">
                  <ArrowsRightLeftIcon className="h-6 w-6" aria-hidden="true" />
                </span>
              </div>
              <div className="mt-8">
                <h3 className="text-lg font-medium">
                  <span className="absolute inset-0" aria-hidden="true" />
                  交易监控
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  监控系统交易活动
                </p>
              </div>
            </button>

            <button
              onClick={() => window.location.href = '/admin/settings'}
              className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500 rounded-lg border border-gray-300 hover:border-gray-400"
            >
              <div>
                <span className="rounded-lg inline-flex p-3 bg-purple-50 text-purple-700 ring-4 ring-white">
                  <CreditCardIcon className="h-6 w-6" aria-hidden="true" />
                </span>
              </div>
              <div className="mt-8">
                <h3 className="text-lg font-medium">
                  <span className="absolute inset-0" aria-hidden="true" />
                  系统设置
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  配置系统参数
                </p>
              </div>
            </button>

            <button
              onClick={() => window.location.href = '/dashboard'}
              className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500 rounded-lg border border-gray-300 hover:border-gray-400"
            >
              <div>
                <span className="rounded-lg inline-flex p-3 bg-orange-50 text-orange-700 ring-4 ring-white">
                  <ChartBarIcon className="h-6 w-6" aria-hidden="true" />
                </span>
              </div>
              <div className="mt-8">
                <h3 className="text-lg font-medium">
                  <span className="absolute inset-0" aria-hidden="true" />
                  用户视图
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  切换到普通用户界面
                </p>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
