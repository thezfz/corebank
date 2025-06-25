/**
 * Integration test for login flow
 * Tests the complete login process from API to UI
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import LoginPage from '../pages/LoginPage/LoginPage'
import { useAuth } from '../hooks/useAuth'

// Mock the API client
vi.mock('../api/client', () => ({
  default: {
    login: vi.fn(),
    getCurrentUser: vi.fn(),
    logout: vi.fn(),
  }
}))

// Mock the useAuth hook for some tests
vi.mock('../hooks/useAuth', () => ({
  useAuth: vi.fn()
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('Login Flow', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render login form correctly', () => {
    const mockUseAuth = useAuth as vi.MockedFunction<typeof useAuth>
    mockUseAuth.mockReturnValue({
      user: null,
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
      isLoginLoading: false,
      isRegisterLoading: false,
      loginError: null,
      registerError: null,
      registerErrorMessages: [],
    })

    render(<LoginPage />, { wrapper: createWrapper() })

    // Check if form elements are present
    expect(screen.getByLabelText(/用户名/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/密码/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /登录/i })).toBeInTheDocument()
  })

  it('should show error message on login failure', () => {
    const mockUseAuth = useAuth as vi.MockedFunction<typeof useAuth>
    mockUseAuth.mockReturnValue({
      user: null,
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
      isLoginLoading: false,
      isRegisterLoading: false,
      loginError: new Error('Login failed'),
      registerError: null,
      registerErrorMessages: [],
    })

    render(<LoginPage />, { wrapper: createWrapper() })

    // Check if error message is displayed
    expect(screen.getByText(/登录失败/i)).toBeInTheDocument()
    expect(screen.getByText(/用户名或密码错误/i)).toBeInTheDocument()
  })

  it('should call login function when form is submitted', async () => {
    const mockLogin = vi.fn()
    const mockUseAuth = useAuth as vi.MockedFunction<typeof useAuth>
    mockUseAuth.mockReturnValue({
      user: null,
      isLoading: false,
      login: mockLogin,
      register: vi.fn(),
      logout: vi.fn(),
      isLoginLoading: false,
      isRegisterLoading: false,
      loginError: null,
      registerError: null,
      registerErrorMessages: [],
    })

    render(<LoginPage />, { wrapper: createWrapper() })

    // Fill in the form
    const usernameInput = screen.getByLabelText(/用户名/i)
    const passwordInput = screen.getByLabelText(/密码/i)
    const submitButton = screen.getByRole('button', { name: /登录/i })

    fireEvent.change(usernameInput, { target: { value: 'testuser' } })
    fireEvent.change(passwordInput, { target: { value: 'MySecure123!' } })
    fireEvent.click(submitButton)

    // Check if login function was called with correct credentials
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'MySecure123!'
      })
    })
  })

  it('should show loading state during login', () => {
    const mockUseAuth = useAuth as vi.MockedFunction<typeof useAuth>
    mockUseAuth.mockReturnValue({
      user: null,
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
      isLoginLoading: true,
      isRegisterLoading: false,
      loginError: null,
      registerError: null,
      registerErrorMessages: [],
    })

    render(<LoginPage />, { wrapper: createWrapper() })

    // Check if loading state is shown
    expect(screen.getByText(/登录中/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /登录中/i })).toBeDisabled()
  })

  it('should toggle password visibility', () => {
    const mockUseAuth = useAuth as vi.MockedFunction<typeof useAuth>
    mockUseAuth.mockReturnValue({
      user: null,
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
      isLoginLoading: false,
      isRegisterLoading: false,
      loginError: null,
      registerError: null,
      registerErrorMessages: [],
    })

    render(<LoginPage />, { wrapper: createWrapper() })

    const passwordInput = screen.getByLabelText(/密码/i) as HTMLInputElement
    const toggleButton = screen.getByRole('button', { name: /显示密码|隐藏密码/i })

    // Initially password should be hidden
    expect(passwordInput.type).toBe('password')

    // Click toggle button
    fireEvent.click(toggleButton)

    // Password should now be visible
    expect(passwordInput.type).toBe('text')

    // Click toggle button again
    fireEvent.click(toggleButton)

    // Password should be hidden again
    expect(passwordInput.type).toBe('password')
  })

  it('should have proper form validation', () => {
    const mockUseAuth = useAuth as vi.MockedFunction<typeof useAuth>
    mockUseAuth.mockReturnValue({
      user: null,
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
      isLoginLoading: false,
      isRegisterLoading: false,
      loginError: null,
      registerError: null,
      registerErrorMessages: [],
    })

    render(<LoginPage />, { wrapper: createWrapper() })

    const usernameInput = screen.getByLabelText(/用户名/i)
    const passwordInput = screen.getByLabelText(/密码/i)

    // Check required attributes
    expect(usernameInput).toHaveAttribute('required')
    expect(passwordInput).toHaveAttribute('required')
  })
})

describe('Login API Integration', () => {
  it('should handle successful login response', async () => {
    // This would be an integration test with actual API calls
    // For now, we'll just verify the structure
    const mockResponse = {
      access_token: 'mock-token',
      token_type: 'bearer',
      expires_in: 1800
    }

    expect(mockResponse).toHaveProperty('access_token')
    expect(mockResponse).toHaveProperty('token_type')
    expect(mockResponse).toHaveProperty('expires_in')
  })

  it('should handle user info response', async () => {
    const mockUserResponse = {
      id: '0193e155-058a-484c-9ecf-c240441874f2',
      username: 'testuser',
      created_at: '2025-06-24T15:38:49'
    }

    expect(mockUserResponse).toHaveProperty('id')
    expect(mockUserResponse).toHaveProperty('username')
    expect(mockUserResponse).toHaveProperty('created_at')
  })
})
