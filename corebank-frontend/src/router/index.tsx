import { lazy } from 'react'
import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom'
import App from '../App'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { AdminGuard } from '../components/auth/RoleGuard'

// Lazy load pages
const LoginPage = lazy(() => import('../pages/LoginPage'))
const RegisterPage = lazy(() => import('../pages/RegisterPage'))
const DashboardPage = lazy(() => import('../pages/DashboardPage'))
const AccountsPage = lazy(() => import('../pages/AccountsPage'))
const TransactionsPage = lazy(() => import('../pages/TransactionsPage'))
const InvestmentDashboardPage = lazy(() => import('../pages/InvestmentDashboardPage'))
const InvestmentProductsPage = lazy(() => import('../pages/InvestmentProductsPage'))
const RiskAssessmentPage = lazy(() => import('../pages/RiskAssessmentPage'))
const InvestmentHoldingsPage = lazy(() => import('../pages/InvestmentHoldingsPage'))
const InvestmentTransactionsPage = lazy(() => import('../pages/InvestmentTransactionsPage'))
const ProductRecommendationsPage = lazy(() => import('../pages/ProductRecommendationsPage'))
const ProfilePage = lazy(() => import('../pages/ProfilePage'))

// Admin pages
const AdminDashboard = lazy(() => import('../pages/admin/AdminDashboard'))
const UserManagement = lazy(() => import('../pages/admin/UserManagement'))
const TransactionMonitoring = lazy(() => import('../pages/admin/TransactionMonitoring'))
const SystemSettings = lazy(() => import('../pages/admin/SystemSettings'))

// Router configuration
const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      {
        path: 'accounts',
        element: <AccountsPage />,
      },
      {
        path: 'transactions',
        element: <TransactionsPage />,
      },
      {
        path: 'investments',
        element: <InvestmentDashboardPage />,
      },
      {
        path: 'investments/products',
        element: <InvestmentProductsPage />,
      },
      {
        path: 'investments/risk-assessment',
        element: <RiskAssessmentPage />,
      },
      {
        path: 'investments/holdings',
        element: <InvestmentHoldingsPage />,
      },
      {
        path: 'investments/transactions',
        element: <InvestmentTransactionsPage />,
      },
      {
        path: 'investments/recommendations',
        element: <ProductRecommendationsPage />,
      },
      {
        path: 'profile',
        element: <ProfilePage />,
      },
      // Admin routes
      {
        path: 'admin/dashboard',
        element: (
          <AdminGuard>
            <AdminDashboard />
          </AdminGuard>
        ),
      },
      {
        path: 'admin/users',
        element: (
          <AdminGuard>
            <UserManagement />
          </AdminGuard>
        ),
      },
      {
        path: 'admin/transactions',
        element: (
          <AdminGuard>
            <TransactionMonitoring />
          </AdminGuard>
        ),
      },
      {
        path: 'admin/settings',
        element: (
          <AdminGuard>
            <SystemSettings />
          </AdminGuard>
        ),
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
])

export default router
