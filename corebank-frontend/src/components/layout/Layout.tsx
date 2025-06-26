import { useState } from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import {
  HomeIcon,
  CreditCardIcon,
  ArrowsRightLeftIcon,
  ChartBarIcon,
  ArrowRightStartOnRectangleIcon,
  UserIcon,
  ChevronDownIcon,
  CogIcon,
  UsersIcon,
  ChartPieIcon
} from '@heroicons/react/24/outline'

export default function Layout() {
  const { user, logout, isAdmin } = useAuth()
  const location = useLocation()
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)

  const handleLogout = async () => {
    setIsLoggingOut(true)
    try {
      console.log('Layout: Starting logout process')
      // 短暂延迟以显示加载状态，然后执行退出
      await new Promise(resolve => setTimeout(resolve, 300))
      logout()
      console.log('Layout: Logout called, state will be handled by useAuth')
      // 不在这里重置 isLoggingOut，让页面跳转处理
    } catch (error) {
      console.error('Logout failed:', error)
      setIsLoggingOut(false)
    }
  }

  const navigation = [
    { name: '仪表板', href: '/dashboard', icon: HomeIcon },
    { name: '账户管理', href: '/accounts', icon: CreditCardIcon },
    { name: '交易记录', href: '/transactions', icon: ArrowsRightLeftIcon },
    { name: '投资理财', href: '/investments', icon: ChartBarIcon },
  ]

  const adminNavigation = [
    { name: '管理仪表板', href: '/admin/dashboard', icon: ChartPieIcon },
    { name: '用户管理', href: '/admin/users', icon: UsersIcon },
    { name: '交易监控', href: '/admin/transactions', icon: ArrowsRightLeftIcon },
    { name: '系统设置', href: '/admin/settings', icon: CogIcon },
  ]

  // Combine navigation based on user role
  const allNavigation = isAdmin ? [...navigation, ...adminNavigation] : navigation

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold text-primary-600">数脉银行</h1>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {allNavigation.map((item) => {
                  const Icon = item.icon
                  const isActive = location.pathname === item.href
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`${
                        isActive
                          ? 'border-primary-500 text-gray-900'
                          : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                      } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {item.name}
                    </Link>
                  )
                })}
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {/* User Menu */}
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center text-sm text-gray-700 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 rounded-md px-2 py-1"
                >
                  <UserIcon className="h-4 w-4 mr-2" />
                  <span>欢迎，{user?.username}</span>
                  <ChevronDownIcon className="h-4 w-4 ml-1" />
                </button>

                {/* Dropdown Menu */}
                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200">
                    <Link
                      to="/profile"
                      onClick={() => setShowUserMenu(false)}
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      <UserIcon className="h-4 w-4 mr-2" />
                      个人信息
                    </Link>
                    <button
                      onClick={() => {
                        setShowUserMenu(false)
                        handleLogout()
                      }}
                      disabled={isLoggingOut}
                      className={`w-full text-left flex items-center px-4 py-2 text-sm ${
                        isLoggingOut
                          ? 'text-gray-400 cursor-not-allowed'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <ArrowRightStartOnRectangleIcon className="h-4 w-4 mr-2" />
                      {isLoggingOut ? '退出中...' : '退出登录'}
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Outlet />
      </main>


    </div>
  )
}
