import React from 'react'
import { useAuth } from '../../hooks/useAuth'

interface PermissionWrapperProps {
  children: React.ReactNode
  requiredRoles?: string[]
  requireAuth?: boolean
  fallback?: React.ReactNode
  showFallback?: boolean
}

/**
 * PermissionWrapper component for conditionally rendering content based on user permissions
 */
export default function PermissionWrapper({
  children,
  requiredRoles = [],
  requireAuth = true,
  fallback = null,
  showFallback = false
}: PermissionWrapperProps) {
  const { isAuthenticated, hasAnyRole } = useAuth()

  // Check authentication requirement
  if (requireAuth && !isAuthenticated) {
    return showFallback ? <>{fallback}</> : null
  }

  // Check role requirements
  if (requiredRoles.length > 0 && !hasAnyRole(requiredRoles)) {
    return showFallback ? <>{fallback}</> : null
  }

  // All checks passed, render children
  return <>{children}</>
}

/**
 * AdminOnly component for admin-only content
 */
export function AdminOnly({ 
  children, 
  fallback = null 
}: { 
  children: React.ReactNode
  fallback?: React.ReactNode 
}) {
  return (
    <PermissionWrapper 
      requiredRoles={['admin']} 
      fallback={fallback}
      showFallback={!!fallback}
    >
      {children}
    </PermissionWrapper>
  )
}

/**
 * UserOnly component for user-only content (excludes admin)
 */
export function UserOnly({ 
  children, 
  fallback = null 
}: { 
  children: React.ReactNode
  fallback?: React.ReactNode 
}) {
  return (
    <PermissionWrapper 
      requiredRoles={['user']} 
      fallback={fallback}
      showFallback={!!fallback}
    >
      {children}
    </PermissionWrapper>
  )
}

/**
 * AuthenticatedOnly component for authenticated users only
 */
export function AuthenticatedOnly({ 
  children, 
  fallback = null 
}: { 
  children: React.ReactNode
  fallback?: React.ReactNode 
}) {
  return (
    <PermissionWrapper 
      requireAuth={true}
      requiredRoles={[]}
      fallback={fallback}
      showFallback={!!fallback}
    >
      {children}
    </PermissionWrapper>
  )
}
