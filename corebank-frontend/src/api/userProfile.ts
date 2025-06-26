import { UserDetailResponse, UserProfileUpdate } from '../types/api'
import { apiClient } from './client'

export const userProfileApi = {
  // Get current user with profile
  getCurrentUserProfile: async (): Promise<UserDetailResponse> => {
    const response = await apiClient.get<UserDetailResponse>('/auth/me/profile')
    return response.data
  },

  // Update current user profile
  updateCurrentUserProfile: async (profileData: UserProfileUpdate): Promise<UserDetailResponse> => {
    const response = await apiClient.put<UserDetailResponse>('/auth/me/profile', profileData)
    return response.data
  }
}
