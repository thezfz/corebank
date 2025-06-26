import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { AxiosError } from 'axios'
import apiClient from '../api/client'
import type { ApiError } from '../types/api'

// Admin query keys
export const adminKeys = {
  all: ['admin'] as const,
  statistics: () => [...adminKeys.all, 'statistics'] as const,
  users: () => [...adminKeys.all, 'users'] as const,
  usersList: (page: number, role?: string) => [...adminKeys.users(), 'list', { page, role }] as const,
  userDetail: (userId: string) => [...adminKeys.users(), 'detail', userId] as const,
}

// Get system statistics
export function useSystemStatistics() {
  return useQuery({
    queryKey: adminKeys.statistics(),
    queryFn: () => apiClient.getSystemStatistics(),
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

// Get all users with pagination
export function useAllUsers(page: number = 1, pageSize: number = 20, role?: string, status: string = 'active', search?: string) {
  return useQuery({
    queryKey: [...adminKeys.usersList(page, role), status, search],
    queryFn: () => apiClient.getAllUsers(page, pageSize, role, status, search),
    staleTime: 1 * 60 * 1000, // 1 minute
  })
}

// Get user detail
export function useUserDetail(userId: string) {
  return useQuery({
    queryKey: adminKeys.userDetail(userId),
    queryFn: () => apiClient.getUserDetail(userId),
    enabled: !!userId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Update user role mutation
export function useUpdateUserRole() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ userId, newRole }: { userId: string; newRole: string }) =>
      apiClient.updateUserRole(userId, newRole),
    onSuccess: (_, { userId }) => {
      // Invalidate user detail
      queryClient.invalidateQueries({
        queryKey: adminKeys.userDetail(userId)
      })

      // Invalidate users list
      queryClient.invalidateQueries({
        queryKey: adminKeys.users()
      })

      // Invalidate statistics
      queryClient.invalidateQueries({
        queryKey: adminKeys.statistics()
      })

      console.log('User role updated successfully')
    },
    onError: (error: AxiosError<ApiError>) => {
      console.error('Failed to update user role:', error)
    }
  })
}



// Soft delete user mutation
export function useSoftDeleteUser() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ userId, reason }: { userId: string; reason: string }) =>
      apiClient.softDeleteUser(userId, reason),
    onSuccess: () => {
      // Invalidate users list
      queryClient.invalidateQueries({
        queryKey: adminKeys.users()
      })

      // Invalidate statistics
      queryClient.invalidateQueries({
        queryKey: adminKeys.statistics()
      })

      console.log('User deleted successfully')
    },
    onError: (error: AxiosError<ApiError>) => {
      console.error('Failed to delete user:', error)
    }
  })
}

// Restore user mutation
export function useRestoreUser() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ userId, reason }: { userId: string; reason: string }) =>
      apiClient.restoreUser(userId, reason),
    onSuccess: (_, { userId }) => {
      // Invalidate user detail
      queryClient.invalidateQueries({
        queryKey: adminKeys.userDetail(userId)
      })

      // Invalidate users list
      queryClient.invalidateQueries({
        queryKey: adminKeys.users()
      })

      // Invalidate statistics
      queryClient.invalidateQueries({
        queryKey: adminKeys.statistics()
      })

      console.log('User restored successfully')
    },
    onError: (error: AxiosError<ApiError>) => {
      console.error('Failed to restore user:', error)
    }
  })
}

// Admin operations hook
export function useAdminOperations() {
  const updateUserRoleMutation = useUpdateUserRole()
  const softDeleteUserMutation = useSoftDeleteUser()
  const restoreUserMutation = useRestoreUser()

  return {
    // User role management
    updateUserRole: updateUserRoleMutation.mutate,
    isUpdatingUserRole: updateUserRoleMutation.isPending,
    updateUserRoleError: updateUserRoleMutation.error,

    // User deletion
    softDeleteUser: softDeleteUserMutation.mutate,
    isDeletingUser: softDeleteUserMutation.isPending,
    deleteUserError: softDeleteUserMutation.error,

    // User restoration
    restoreUser: restoreUserMutation.mutate,
    isRestoringUser: restoreUserMutation.isPending,
    restoreUserError: restoreUserMutation.error,
    
    // Helper functions
    parseAdminError: (error: unknown): string[] => {
      if (!error || typeof error !== 'object') {
        return ['操作失败，请重试']
      }

      const axiosError = error as AxiosError<ApiError>

      if (!axiosError.response?.data) {
        return ['网络错误，请检查连接后重试']
      }

      const data = axiosError.response.data

      // Handle validation errors (422 status)
      if (axiosError.response.status === 422 && data.errors) {
        return data.errors.map(err => err.message)
      }

      // Handle forbidden errors (403 status)
      if (axiosError.response.status === 403) {
        return ['权限不足，无法执行此操作']
      }

      // Handle other specific errors
      if (typeof data.detail === 'string') {
        return [data.detail]
      }

      return ['操作失败，请重试']
    }
  }
}

// Admin dashboard data hook
export function useAdminDashboard() {
  const { data: statistics, isLoading: statsLoading, error: statsError } = useSystemStatistics()
  const { data: recentUsers, isLoading: usersLoading } = useAllUsers(1, 5)

  return {
    statistics,
    recentUsers: recentUsers?.items || [],
    isLoading: statsLoading || usersLoading,
    error: statsError,
    
    // Computed statistics
    totalUsers: statistics?.total_users || 0,
    adminCount: statistics?.admin_count || 0,
    userCount: statistics?.user_count || 0,
    newUsersThisMonth: statistics?.new_users_30d || 0,
    newUsersThisWeek: statistics?.new_users_7d || 0,
    
    // Growth calculations
    userGrowthRate: statistics?.new_users_30d && statistics?.total_users 
      ? ((statistics.new_users_30d / statistics.total_users) * 100).toFixed(1)
      : '0',
  }
}
