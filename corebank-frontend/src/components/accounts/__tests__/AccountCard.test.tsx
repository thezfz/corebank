import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import AccountCard from '../AccountCard'
import type { Account } from '../../../types/api'

describe('AccountCard', () => {
  const mockAccount: Account = {
    id: '123e4567-e89b-12d3-a456-426614174000',
    account_number: '1234567890123456',
    user_id: 'user-123',
    account_type: 'checking',
    balance: '1234.56',
    created_at: '2025-01-15T10:30:00Z'
  }

  it('应该显示账户信息', () => {
    render(<AccountCard account={mockAccount} />)
    
    expect(screen.getByText('支票账户')).toBeInTheDocument()
    expect(screen.getByText('**** **** **** 3456')).toBeInTheDocument()
    expect(screen.getByText('¥1,234.56')).toBeInTheDocument()
    expect(screen.getByText('当前余额')).toBeInTheDocument()
  })

  it('应该正确格式化账户号码', () => {
    render(<AccountCard account={mockAccount} />)
    
    // 应该只显示最后4位数字
    expect(screen.getByText('**** **** **** 3456')).toBeInTheDocument()
  })

  it('应该正确显示储蓄账户类型', () => {
    const savingsAccount = { ...mockAccount, account_type: 'savings' as const }
    render(<AccountCard account={savingsAccount} />)
    
    expect(screen.getByText('储蓄账户')).toBeInTheDocument()
  })

  it('应该正确格式化货币', () => {
    render(<AccountCard account={mockAccount} />)
    
    expect(screen.getByText('¥1,234.56')).toBeInTheDocument()
  })

  it('应该显示负余额为红色', () => {
    const negativeAccount = { ...mockAccount, balance: '-500.00' }
    render(<AccountCard account={negativeAccount} />)
    
    const balanceElement = screen.getByText('-¥500.00')
    expect(balanceElement).toHaveClass('text-red-600')
  })

  it('应该显示正余额为绿色', () => {
    render(<AccountCard account={mockAccount} />)
    
    const balanceElement = screen.getByText('¥1,234.56')
    expect(balanceElement).toHaveClass('text-green-600')
  })

  it('应该在点击时调用onClick回调', () => {
    const onClick = vi.fn()
    render(<AccountCard account={mockAccount} onClick={onClick} />)

    // 找到最外层的div元素
    const card = screen.getByText('支票账户').closest('div')?.parentElement?.parentElement?.parentElement
    if (card) {
      fireEvent.click(card)
      expect(onClick).toHaveBeenCalled()
    }
  })

  it('应该在有onClick时显示指针光标', () => {
    const onClick = vi.fn()
    render(<AccountCard account={mockAccount} onClick={onClick} />)

    // 找到最外层的div元素
    const card = screen.getByText('支票账户').closest('div')?.parentElement?.parentElement?.parentElement
    expect(card).toHaveClass('cursor-pointer')
  })

  it('应该在没有onClick时不显示指针光标', () => {
    render(<AccountCard account={mockAccount} />)

    // 找到最外层的div元素
    const card = screen.getByText('支票账户').closest('div')?.parentElement?.parentElement?.parentElement
    expect(card).not.toHaveClass('cursor-pointer')
  })

  it('应该显示账户ID和创建日期', () => {
    render(<AccountCard account={mockAccount} />)
    
    expect(screen.getByText(/账户 ID: 123e4567/)).toBeInTheDocument()
    expect(screen.getByText(/创建于/)).toBeInTheDocument()
  })

  it('应该正确格式化创建日期', () => {
    render(<AccountCard account={mockAccount} />)
    
    // 检查是否包含日期格式
    expect(screen.getByText(/2025/)).toBeInTheDocument()
  })
})
