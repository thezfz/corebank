import React, { useState } from 'react'
import {
  UsersIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  EyeIcon,
  TrashIcon,
  ChevronDownIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'
import { useAllUsers, useAdminOperations } from '../../hooks/useAdmin'
import LoadingSpinner from '../../components/common/LoadingSpinner'

interface User {
  id: string
  username: string
  role: 'user' | 'admin'
  created_at: string
  updated_at?: string
  is_active: boolean
  deleted_at?: string
  last_login_at?: string
  real_name?: string
  phone?: string
  email?: string
  account_count?: number
  total_balance?: string
  investment_count?: number
}

interface PaginatedUsers {
  items: User[]
  total_count: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_previous: boolean
}

export default function UserManagement() {
  const [currentPage, setCurrentPage] = useState(1)
  const [roleFilter, setRoleFilter] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('active')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [showUserDetail, setShowUserDetail] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [showRestoreModal, setShowRestoreModal] = useState(false)
  const [deleteReason, setDeleteReason] = useState('')
  const [restoreReason, setRestoreReason] = useState('')

  const { data: users, isLoading, error, refetch } = useAllUsers(currentPage, 20, roleFilter || undefined, statusFilter, searchTerm.trim() || undefined)
  const { updateUserRole, softDeleteUser, restoreUser, isUpdatingUserRole } = useAdminOperations()

  const handleRoleChange = (userId: string, newRole: string) => {
    updateUserRole({ userId, newRole }).then(() => {
      refetch()
    })
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  const handleViewDetail = (user: User) => {
    setSelectedUser(user)
    setShowUserDetail(true)
  }

  const handleDelete = (user: User) => {
    setSelectedUser(user)
    setShowDeleteModal(true)
  }

  const handleRestore = (user: User) => {
    setSelectedUser(user)
    setShowRestoreModal(true)
  }

  const confirmDelete = async () => {
    if (!selectedUser || !deleteReason.trim()) return

    try {
      await softDeleteUser({
        userId: selectedUser.id,
        reason: deleteReason
      })
      setShowDeleteModal(false)
      setDeleteReason('')
      setSelectedUser(null)
      refetch()
    } catch (error) {
      console.error('Failed to delete user:', error)
    }
  }

  const confirmRestore = async () => {
    if (!selectedUser || !restoreReason.trim()) return

    try {
      await restoreUser({
        userId: selectedUser.id,
        reason: restoreReason
      })
      setShowRestoreModal(false)
      setRestoreReason('')
      setSelectedUser(null)
      refetch()
    } catch (error) {
      console.error('Failed to restore user:', error)
    }
  }

  // 服务器端已经处理了搜索，直接使用返回的数据
  const filteredUsers = users?.items || []

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-5">
        <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          用户管理
        </h1>
        <p className="mt-2 max-w-4xl text-sm text-gray-500">
          管理系统中的所有用户账户和权限
        </p>
      </div>

      {/* Filters and Search */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0 sm:space-x-4">
            {/* Search */}
            <div className="flex-1 min-w-0">
              <div className="relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => {
                    setSearchTerm(e.target.value)
                    setCurrentPage(1) // 搜索时重置到第一页
                  }}
                  className="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-10 sm:text-sm border-gray-300 rounded-md"
                  placeholder="搜索用户名、姓名或邮箱..."
                />
              </div>
            </div>

            {/* Status Filter */}
            <div className="flex items-center space-x-2">
              <FunnelIcon className="h-5 w-5 text-gray-400" />
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value)
                  setCurrentPage(1)
                }}
                className="focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
              >
                <option value="active">活跃用户</option>
                <option value="deleted">已删除用户</option>
                <option value="all">全部用户</option>
              </select>
            </div>

            {/* Role Filter */}
            <div className="flex items-center space-x-2">
              <select
                value={roleFilter}
                onChange={(e) => {
                  setRoleFilter(e.target.value)
                  setCurrentPage(1)
                }}
                className="focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
              >
                <option value="">所有角色</option>
                <option value="user">普通用户</option>
                <option value="admin">管理员</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              用户列表
            </h3>
            <div className="text-sm text-gray-500">
              {searchTerm.trim()
                ? `找到 ${filteredUsers.length} 个匹配用户`
                : `共 ${users?.total_count || 0} 个用户`
              }
            </div>
          </div>

          {error ? (
            <div className="text-center py-12">
              <UsersIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">加载失败</h3>
              <p className="mt-1 text-sm text-gray-500">获取用户列表失败</p>
            </div>
          ) : filteredUsers.length === 0 ? (
            <div className="text-center py-12">
              <UsersIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                {searchTerm.trim() ? '没有找到匹配的用户' : '没有找到用户'}
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                {searchTerm.trim()
                  ? '尝试调整搜索条件或清空搜索框查看所有用户'
                  : '系统中暂无用户'}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      用户信息
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      角色
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      状态
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      账户信息
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      注册时间
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      操作
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredUsers.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                              <UsersIcon className="h-6 w-6 text-gray-600" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {user.real_name || user.username}
                            </div>
                            <div className="text-sm text-gray-500">
                              @{user.username}
                            </div>
                            {user.email && (
                              <div className="text-sm text-gray-500">
                                {user.email}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <select
                          value={user.role}
                          onChange={(e) => handleRoleChange(user.id, e.target.value)}
                          disabled={isUpdatingUserRole}
                          className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border-0 focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed ${
                            user.role === 'admin'
                              ? 'bg-purple-100 text-purple-800'
                              : 'bg-green-100 text-green-800'
                          }`}
                        >
                          <option value="user">普通用户</option>
                          <option value="admin">管理员</option>
                        </select>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            user.is_active
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {user.is_active ? '正常' : '禁用'}
                          </span>
                          {user.last_login_at && (
                            <span className="ml-2 text-xs text-gray-500">
                              最后登录: {new Date(user.last_login_at).toLocaleDateString('zh-CN')}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className="space-y-1">
                          <div>账户: {user.account_count || 0} 个</div>
                          <div>余额: ¥{user.total_balance || '0.00'}</div>
                          <div>投资: {user.investment_count || 0} 个</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(user.created_at).toLocaleDateString('zh-CN')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleViewDetail(user)}
                            className="text-indigo-600 hover:text-indigo-900 flex items-center"
                            title="查看详情"
                          >
                            <EyeIcon className="h-4 w-4" />
                          </button>

                          {user.deleted_at ? (
                            // 已删除用户：显示恢复按钮
                            <button
                              onClick={() => handleRestore(user)}
                              className="text-green-600 hover:text-green-900 flex items-center"
                              title="恢复用户"
                            >
                              <ArrowPathIcon className="h-4 w-4" />
                            </button>
                          ) : (
                            // 活跃用户：显示删除按钮
                            <button
                              onClick={() => handleDelete(user)}
                              className="text-red-600 hover:text-red-900 flex items-center"
                              title="删除用户"
                            >
                              <TrashIcon className="h-4 w-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          {users && users.total_pages > 1 && (
            <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 mt-4">
              <div className="flex-1 flex justify-between sm:hidden">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={!users.has_previous}
                  className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  上一页
                </button>
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={!users.has_next}
                  className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  下一页
                </button>
              </div>
              <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700">
                    显示第 <span className="font-medium">{(currentPage - 1) * 20 + 1}</span> 到{' '}
                    <span className="font-medium">
                      {Math.min(currentPage * 20, users.total_count)}
                    </span>{' '}
                    条，共 <span className="font-medium">{users.total_count}</span> 条记录
                  </p>
                </div>
                <div>
                  <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                    <button
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={!users.has_previous}
                      className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ChevronLeftIcon className="h-5 w-5" />
                    </button>
                    <span className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                      {currentPage} / {users.total_pages}
                    </span>
                    <button
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={!users.has_next}
                      className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ChevronRightIcon className="h-5 w-5" />
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* User Detail Modal */}
      {showUserDetail && selectedUser && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">用户详情</h3>
                <button
                  onClick={() => setShowUserDetail(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="sr-only">关闭</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">用户名</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedUser.username}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">真实姓名</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedUser.real_name || '未设置'}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">角色</label>
                    <p className="mt-1 text-sm text-gray-900">
                      {selectedUser.role === 'admin' ? '管理员' : '普通用户'}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">状态</label>
                    <p className="mt-1 text-sm text-gray-900">
                      {selectedUser.is_active ? '正常' : '禁用'}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">手机号</label>
                    <p className="mt-1 text-sm text-gray-900">
                      {selectedUser.phone ? selectedUser.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : '未设置'}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">邮箱</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedUser.email || '未设置'}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">账户数量</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedUser.account_count || 0} 个</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">总余额</label>
                    <p className="mt-1 text-sm text-gray-900">¥{selectedUser.total_balance || '0.00'}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">投资产品</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedUser.investment_count || 0} 个</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">注册时间</label>
                    <p className="mt-1 text-sm text-gray-900">
                      {new Date(selectedUser.created_at).toLocaleString('zh-CN')}
                    </p>
                  </div>
                  {selectedUser.last_login_at && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">最后登录</label>
                      <p className="mt-1 text-sm text-gray-900">
                        {new Date(selectedUser.last_login_at).toLocaleString('zh-CN')}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}



      {/* Delete Modal */}
      {showDeleteModal && selectedUser && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">删除用户</h3>
              <p className="text-sm text-gray-500 mb-4">
                您确定要删除用户 "{selectedUser.username}" 吗？此操作不可撤销。
              </p>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  删除原因 <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={deleteReason}
                  onChange={(e) => setDeleteReason(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  rows={3}
                  placeholder="请输入删除原因..."
                  required
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowDeleteModal(false)
                    setDeleteReason('')
                  }}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                >
                  取消
                </button>
                <button
                  onClick={confirmDelete}
                  disabled={!deleteReason.trim()}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  确认删除
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Restore Modal */}
      {showRestoreModal && selectedUser && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">恢复用户</h3>
              <p className="text-sm text-gray-500 mb-4">
                您确定要恢复用户 "{selectedUser.username}" 吗？恢复后用户将重新激活。
              </p>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  恢复原因 <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={restoreReason}
                  onChange={(e) => setRestoreReason(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  rows={3}
                  placeholder="请输入恢复原因..."
                  required
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowRestoreModal(false)
                    setRestoreReason('')
                  }}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                >
                  取消
                </button>
                <button
                  onClick={confirmRestore}
                  disabled={!restoreReason.trim()}
                  className="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  确认恢复
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
