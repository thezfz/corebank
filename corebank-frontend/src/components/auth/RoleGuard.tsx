import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import LoadingSpinner from '../common/LoadingSpinner'

interface RoleGuardProps {
  children: React.ReactNode
  requiredRoles?: string[]
  requireAuth?: boolean
  fallbackPath?: string
}

/**
 * RoleGuard component for protecting routes based on user roles
 */
export default function RoleGuard({
  children,
  requiredRoles = [],
  requireAuth = true,
  fallbackPath = '/login'
}: RoleGuardProps) {
  const { user, isLoading, isAuthenticated, hasAnyRole } = useAuth()
  const location = useLocation()

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  // Check authentication requirement
  if (requireAuth && !isAuthenticated) {
    return <Navigate to={fallbackPath} state={{ from: location }} replace />
  }

  // Check role requirements
  if (requiredRoles.length > 0 && !hasAnyRole(requiredRoles)) {
    // If user is authenticated but doesn't have required role, redirect to dashboard
    return <Navigate to="/dashboard" replace />
  }

  // All checks passed, render children
  return <>{children}</>
}

/**
 * AdminGuard component for protecting admin-only routes
 */
export function AdminGuard({ children }: { children: React.ReactNode }) {
  return (
    <RoleGuard requiredRoles={['admin']} fallbackPath="/dashboard">
      {children}
    </RoleGuard>
  )
}

/**
 * UserGuard component for protecting user routes (excludes admin)
 */
export function UserGuard({ children }: { children: React.ReactNode }) {
  return (
    <RoleGuard requiredRoles={['user']} fallbackPath="/dashboard">
      {children}
    </RoleGuard>
  )
}

/**
 * AuthGuard component for protecting authenticated routes
 */
export function AuthGuard({ children }: { children: React.ReactNode }) {
  return (
    <RoleGuard requireAuth={true}>
      {children}
    </RoleGuard>
  )
}
