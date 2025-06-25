import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import CreateAccountModal from '../CreateAccountModal'

// Mock the useAccountOperations hook
vi.mock('../../../hooks/useAccounts', () => ({
  useAccountOperations: () => ({
    createAccount: vi.fn(),
    isCreating: false,
    createError: null,
    createErrorMessages: [],
  })
}))

describe('CreateAccountModal', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })
  })

  const renderModal = (props = {}) => {
    const defaultProps = {
      isOpen: true,
      onClose: vi.fn(),
      onSuccess: vi.fn(),
    }

    return render(
      <QueryClientProvider client={queryClient}>
        <CreateAccountModal {...defaultProps} {...props} />
      </QueryClientProvider>
    )
  }

  it('应该在打开时显示模态框', () => {
    renderModal()
    
    expect(screen.getByText('创建新账户')).toBeInTheDocument()
    expect(screen.getByLabelText('账户类型')).toBeInTheDocument()
    expect(screen.getByLabelText('初始存款 (可选)')).toBeInTheDocument()
  })

  it('应该在关闭时隐藏模态框', () => {
    renderModal({ isOpen: false })
    
    expect(screen.queryByText('创建新账户')).not.toBeInTheDocument()
  })

  it('应该有正确的默认值', () => {
    renderModal()
    
    const accountTypeSelect = screen.getByLabelText('账户类型') as HTMLSelectElement
    const initialDepositInput = screen.getByLabelText('初始存款 (可选)') as HTMLInputElement
    
    expect(accountTypeSelect.value).toBe('checking')
    expect(initialDepositInput.value).toBe('')
  })

  it('应该允许更改账户类型', () => {
    renderModal()
    
    const accountTypeSelect = screen.getByLabelText('账户类型') as HTMLSelectElement
    
    fireEvent.change(accountTypeSelect, { target: { value: 'savings' } })
    
    expect(accountTypeSelect.value).toBe('savings')
    expect(screen.getByText('用于储蓄和获得利息')).toBeInTheDocument()
  })

  it('应该允许输入初始存款', () => {
    renderModal()
    
    const initialDepositInput = screen.getByLabelText('初始存款 (可选)') as HTMLInputElement
    
    fireEvent.change(initialDepositInput, { target: { value: '1000.50' } })
    
    expect(initialDepositInput.value).toBe('1000.50')
  })

  it('应该在点击取消时调用onClose', () => {
    const onClose = vi.fn()
    renderModal({ onClose })
    
    const cancelButton = screen.getByText('取消')
    fireEvent.click(cancelButton)
    
    expect(onClose).toHaveBeenCalled()
  })

  it('应该在点击背景时调用onClose', () => {
    const onClose = vi.fn()
    renderModal({ onClose })
    
    const backdrop = document.querySelector('.fixed.inset-0.bg-black')
    if (backdrop) {
      fireEvent.click(backdrop)
      expect(onClose).toHaveBeenCalled()
    }
  })

  it('应该显示正确的账户类型描述', () => {
    renderModal()
    
    const accountTypeSelect = screen.getByLabelText('账户类型')
    
    // 默认是支票账户
    expect(screen.getByText('用于日常交易和支付')).toBeInTheDocument()
    
    // 切换到储蓄账户
    fireEvent.change(accountTypeSelect, { target: { value: 'savings' } })
    expect(screen.getByText('用于储蓄和获得利息')).toBeInTheDocument()
  })
})
