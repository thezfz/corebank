import React from 'react'
import { 
  CogIcon,
  ShieldCheckIcon,
  DatabaseIcon,
  BellIcon,
  ChartBarIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

export default function SystemSettings() {
  const settingsSections = [
    {
      title: '系统配置',
      description: '基本系统参数和配置',
      icon: CogIcon,
      color: 'bg-blue-500',
      items: [
        { name: '系统名称', value: '数脉银行', editable: true },
        { name: '系统版本', value: 'v1.0.0', editable: false },
        { name: '维护模式', value: '关闭', editable: true },
        { name: '最大并发用户', value: '1000', editable: true },
      ]
    },
    {
      title: '安全设置',
      description: '用户认证和安全策略',
      icon: ShieldCheckIcon,
      color: 'bg-red-500',
      items: [
        { name: '密码最小长度', value: '8', editable: true },
        { name: '登录失败锁定次数', value: '5', editable: true },
        { name: '会话超时时间', value: '30分钟', editable: true },
        { name: '双因子认证', value: '关闭', editable: true },
      ]
    },
    {
      title: '数据库设置',
      description: '数据库连接和性能配置',
      icon: DatabaseIcon,
      color: 'bg-green-500',
      items: [
        { name: '连接池大小', value: '20', editable: true },
        { name: '查询超时时间', value: '30秒', editable: true },
        { name: '备份频率', value: '每日', editable: true },
        { name: '数据保留期', value: '7年', editable: true },
      ]
    },
    {
      title: '通知设置',
      description: '系统通知和警报配置',
      icon: BellIcon,
      color: 'bg-yellow-500',
      items: [
        { name: '邮件通知', value: '启用', editable: true },
        { name: '短信通知', value: '启用', editable: true },
        { name: '系统警报', value: '启用', editable: true },
        { name: '交易通知', value: '启用', editable: true },
      ]
    },
    {
      title: '监控设置',
      description: '系统监控和日志配置',
      icon: ChartBarIcon,
      color: 'bg-purple-500',
      items: [
        { name: '日志级别', value: 'INFO', editable: true },
        { name: '性能监控', value: '启用', editable: true },
        { name: '错误报告', value: '启用', editable: true },
        { name: '审计日志', value: '启用', editable: true },
      ]
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-5">
        <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          系统设置
        </h1>
        <p className="mt-2 max-w-4xl text-sm text-gray-500">
          管理系统配置参数和安全策略
        </p>
      </div>

      {/* Warning Notice */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              注意事项
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>
                修改系统设置可能会影响系统的正常运行。请在修改前确保了解相关配置的作用，
                并建议在维护时间窗口内进行修改。
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Settings Sections */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {settingsSections.map((section) => {
          const Icon = section.icon
          return (
            <div key={section.title} className="bg-white shadow rounded-lg overflow-hidden">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center mb-4">
                  <div className={`flex-shrink-0 ${section.color} rounded-md p-3`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      {section.title}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {section.description}
                    </p>
                  </div>
                </div>

                <div className="space-y-4">
                  {section.items.map((item) => (
                    <div key={item.name} className="flex items-center justify-between">
                      <div className="flex-1">
                        <label className="block text-sm font-medium text-gray-700">
                          {item.name}
                        </label>
                      </div>
                      <div className="flex-1 max-w-xs">
                        {item.editable ? (
                          <input
                            type="text"
                            defaultValue={item.value}
                            className="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                            disabled
                          />
                        ) : (
                          <div className="mt-1 text-sm text-gray-900 bg-gray-50 px-3 py-2 rounded-md">
                            {item.value}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-6 flex justify-end">
                  <button
                    type="button"
                    disabled
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    保存设置
                  </button>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* System Information */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            系统信息
          </h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="bg-gray-50 px-4 py-3 rounded-lg">
              <dt className="text-sm font-medium text-gray-500">服务器时间</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {new Date().toLocaleString('zh-CN')}
              </dd>
            </div>
            <div className="bg-gray-50 px-4 py-3 rounded-lg">
              <dt className="text-sm font-medium text-gray-500">系统运行时间</dt>
              <dd className="mt-1 text-sm text-gray-900">72小时15分钟</dd>
            </div>
            <div className="bg-gray-50 px-4 py-3 rounded-lg">
              <dt className="text-sm font-medium text-gray-500">数据库状态</dt>
              <dd className="mt-1 text-sm text-green-600 font-medium">正常</dd>
            </div>
            <div className="bg-gray-50 px-4 py-3 rounded-lg">
              <dt className="text-sm font-medium text-gray-500">缓存状态</dt>
              <dd className="mt-1 text-sm text-green-600 font-medium">正常</dd>
            </div>
          </div>
        </div>
      </div>

      {/* Development Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <CogIcon className="h-5 w-5 text-blue-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">
              开发说明
            </h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                此页面为系统设置的演示界面。在实际生产环境中，这些设置将连接到后端配置系统，
                支持实时修改和保存配置参数。
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
