import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '../../../test/utils'
import userEvent from '@testing-library/user-event'
import LoginPage from '../LoginPage'
import '@testing-library/jest-dom'

// Mock useAuth hook
const mockLogin = vi.fn()
const mockLogout = vi.fn()
const mockRegister = vi.fn()

// 创建可变的 mock 对象
let mockAuthState = {
  login: mockLogin,
  isLoginLoading: false,
  loginError: null as Error | null,
  user: null,
  logout: mockLogout,
  register: mockRegister,
  isRegisterLoading: false,
  registerError: null as Error | null,
}

// Mock the entire auth hook module
vi.mock('../../../hooks/useAuth', () => ({
  useAuth: () => mockAuthState,
}))

describe('LoginPage 集成测试', () => {
  const user = userEvent.setup()

  beforeEach(() => {
    vi.clearAllMocks()
    // 重置 mock 状态
    mockAuthState = {
      login: mockLogin,
      isLoginLoading: false,
      loginError: null,
      user: null,
      logout: mockLogout,
      register: mockRegister,
      isRegisterLoading: false,
      registerError: null,
    }
  })

  it('应该渲染登录表单的所有元素', () => {
    render(<LoginPage />)
    
    expect(screen.getByText('核心银行')).toBeInTheDocument()
    expect(screen.getByText('欢迎回来')).toBeInTheDocument()
    expect(screen.getByLabelText('用户名')).toBeInTheDocument()
    expect(screen.getByLabelText('密码')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '登录' })).toBeInTheDocument()
    expect(screen.getByText('创建账户')).toBeInTheDocument()
  })

  it('应该能够输入用户名和密码', async () => {
    render(<LoginPage />)
    
    const usernameInput = screen.getByLabelText('用户名')
    const passwordInput = screen.getByLabelText('密码')
    
    await user.type(usernameInput, 'testuser')
    await user.type(passwordInput, 'password123')
    
    expect(usernameInput).toHaveValue('testuser')
    expect(passwordInput).toHaveValue('password123')
  })

  it('应该在提交表单时调用登录函数', async () => {
    render(<LoginPage />)
    
    const usernameInput = screen.getByLabelText('用户名')
    const passwordInput = screen.getByLabelText('密码')
    const submitButton = screen.getByRole('button', { name: '登录' })
    
    await user.type(usernameInput, 'testuser')
    await user.type(passwordInput, 'password123')
    await user.click(submitButton)
    
    expect(mockLogin).toHaveBeenCalledWith({
      username: 'testuser',
      password: 'password123',
    })
  })

  it('应该显示加载状态', () => {
    // 设置加载状态
    mockAuthState.isLoginLoading = true

    render(<LoginPage />)

    expect(screen.getByText('登录中...')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /登录中/ })).toBeDisabled()
  })

  it('应该显示登录错误', () => {
    // 设置错误状态
    mockAuthState.loginError = new Error('登录失败')

    render(<LoginPage />)

    expect(screen.getByText('用户名或密码错误，请重试。')).toBeInTheDocument()
  })

  it('应该能够切换密码可见性', async () => {
    render(<LoginPage />)

    const passwordInput = screen.getByLabelText('密码')
    // 通过查找密码输入框旁边的按钮
    const toggleButton = passwordInput.parentElement?.querySelector('button')

    expect(passwordInput).toHaveAttribute('type', 'password')

    if (toggleButton) {
      await user.click(toggleButton)
      expect(passwordInput).toHaveAttribute('type', 'text')

      await user.click(toggleButton)
      expect(passwordInput).toHaveAttribute('type', 'password')
    }
  })
})
