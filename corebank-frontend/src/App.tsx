import React from 'react'
import { useLocation, useNavigate, Outlet } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import Layout from './components/layout/Layout'
import AuthDebugger from './components/debug/AuthDebugger'
import LoadingSpinner from './components/common/LoadingSpinner'

function App() {
  const { user, isLoading } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  // Debug: Log user and location changes
  React.useEffect(() => {
    console.log('App: user state changed:', user)
    console.log('App: current location:', location.pathname)
    console.log('App: isLoading:', isLoading)
  }, [user, location, isLoading])

  // Handle authentication-based navigation
  React.useEffect(() => {
    if (isLoading) return // Don't navigate while loading

    const isAuthPage = location.pathname === '/login' || location.pathname === '/register'

    if (user && isAuthPage) {
      // User is logged in but on auth page, redirect to dashboard
      console.log('App: User logged in, redirecting to dashboard')
      navigate('/dashboard', { replace: true })
    } else if (!user && !isAuthPage) {
      // User is not logged in but not on auth page, redirect to login
      console.log('App: User not logged in, redirecting to login')
      navigate('/login', { replace: true })
    }
  }, [user, isLoading, location.pathname, navigate])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  const isAuthPage = location.pathname === '/login' || location.pathname === '/register'

  return (
    <>
      {user && !isAuthPage ? (
        <Layout />
      ) : !user && isAuthPage ? (
        <Outlet />
      ) : (
        // Show loading while navigation is happening
        <div className="min-h-screen flex items-center justify-center">
          <LoadingSpinner size="lg" />
        </div>
      )}
      {/* Debug component - enable by adding ?debug=true to URL */}
      <AuthDebugger enabled={new URLSearchParams(window.location.search).get('debug') === 'true'} />
    </>
  )
}

export default App
