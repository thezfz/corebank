import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AxiosError } from 'axios'
import { userProfileApi } from '../api/userProfile'
import type { UserDetailResponse, UserProfileUpdate, ApiError } from '../types/api'

export const useUserProfile = () => {
  const queryClient = useQueryClient()

  // Get current user profile
  const {
    data: userProfile,
    isLoading,
    error,
    refetch
  } = useQuery<UserDetailResponse>({
    queryKey: ['userProfile'],
    queryFn: userProfileApi.getCurrentUserProfile,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Update user profile
  const updateProfileMutation = useMutation({
    mutationFn: (profileData: UserProfileUpdate) => userProfileApi.updateCurrentUserProfile(profileData),
    onSuccess: (data) => {
      // Update the cache with new data
      queryClient.setQueryData(['userProfile'], data)
      // Also update the user cache if it exists
      queryClient.setQueryData(['user'], (oldData: any) => {
        if (oldData) {
          return { ...oldData, ...data }
        }
        return data
      })
      console.log('Profile updated successfully:', data.id)
    },
    onError: (error: AxiosError<ApiError>) => {
      console.error('Failed to update profile:', error)
    }
  })

  return {
    userProfile,
    isLoading,
    error,
    refetch,
    updateProfile: updateProfileMutation.mutateAsync,
    isUpdating: updateProfileMutation.isPending,
    updateError: updateProfileMutation.error?.response?.data?.detail ||
                 updateProfileMutation.error?.message ||
                 (updateProfileMutation.error ? '更新失败，请重试' : null),
    updateSuccess: updateProfileMutation.isSuccess
  }
}

// Check if user has completed KYC (has profile information)
export function useKYCStatus() {
  const { userProfile, isLoading, error } = useUserProfile()

  // Consider KYC completed if user has essential profile information
  const isKYCCompleted = userProfile &&
    userProfile.real_name &&
    userProfile.id_number &&
    userProfile.phone &&
    userProfile.email

  return {
    isKYCCompleted: !!isKYCCompleted,
    userProfile,
    isLoading,
    error
  }
}
